"""Validate publishable files without executing vendor tools or loading models."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
import zipfile
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def load(name):
    return json.loads((ROOT / 'manifests' / name).read_text(encoding='utf-8'))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets', type=Path)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    checks = []
    def check(ok, name):
        if not ok:
            raise AssertionError(name)
        checks.append(name)
    excluded = {'AccountAuthority', 'MPA', 'TempModel', 'Backup', 'Logs', 'Temp'}
    files = [f for f in ROOT.rglob('*') if f.is_file() and not any(x.startswith('runtime') or x in {'.git','__pycache__','bin','obj'} for x in f.relative_to(ROOT).parts)]
    check(not any(excluded.intersection(f.relative_to(ROOT).parts) or f.suffix in {'.db','.mpass','.exe'} for f in files), 'sensitive and generated platform directories excluded')
    check(all(f.stat().st_size < 100 * 1024**2 for f in files), 'all repository files below 100 MiB')
    parser = ET.XMLParser(huge_tree=True, resolve_entities=False, no_network=True)
    roots = {}
    for path in (ROOT / 'project' / 'Config').rglob('*'):
        if not path.is_file():
            continue
        roots[path.relative_to(ROOT / 'project').as_posix()] = ET.fromstring(path.read_bytes(), parser=parser)
    check(bool(roots), 'all staged platform XML configurations parse')
    for row in load('image-bindings.json'):
        items = [x for x in roots[row['file']].iter() if x.get('Id') == row['ref_id']]
        check(len(items) == 1 and items[0].get('CustomValue') == row['folder'], 'portable input: ' + row['folder'])
        check((ROOT / 'project' / Path(row['folder'].replace('\\','/'))).is_dir(), 'demo input directory exists: ' + row['folder'])
    original_code = []
    model_refs = []
    for root in roots.values():
        for item in root.iter():
            for value in item.attrib.values():
                if len(value) < 8192:
                    check(not re.search(r'[A-Za-z]:\\Users\\|[A-Za-z]:\\1\.5\\', value), 'no private absolute path in config attribute') if re.search(r'[A-Za-z]:\\Users\\|[A-Za-z]:\\1\.5\\', value) else None
                if 'public class ScriptClass' in value:
                    original_code.append(value.replace('\r\n','\n').replace('\r','\n'))
            ref = item.get('CustomValue','')
            if ref.lower().endswith('.bin'):
                active = all(a.get('IsEnabled','true') != 'false' for a in [item,*item.iterancestors()] if a.get('Id','').startswith('ATOM'))
                model_refs.append((ref, active))
    check(len(original_code) == 1 and original_code[0] == (ROOT/'src/cable_rotation.cs').read_text(encoding='utf-8'), 'extracted C# is identical to embedded code after newline normalization')
    listed = load('model-references.json')
    check(sorted(model_refs) == sorted((x['reference'],x['effective_enabled']) for x in listed), 'model reference list matches current XML and ancestor enable flags')
    check(sum(x['effective_enabled'] for x in listed) == 5 and sum(not x['exists'] for x in listed) == 1, 'five active model dependencies; one documented disabled missing legacy reference')
    model_list = load('models.json')
    model_paths = {x['file'] for x in model_list}
    check(all('project/'+x['reference'].replace('\\','/') in model_paths for x in listed if x['effective_enabled']), 'all active references have matching exported model manifest entries')
    for row in load('demo-images.json') + load('figures.json'):
        check(digest(ROOT / row['file']) == row['sha256'], 'image hash: ' + row['file'])
    evidence = load('evidence.json')
    for k in ['hmi','brief','project_header']:
        check(digest(ROOT / evidence[k]['file']) == evidence[k]['sha256'], 'source evidence hash: ' + k)
    check(len(load('training-projects.json')) == 17, '17 training projects listed')
    for f in files:
        if f.suffix in {'.json','.dls'}:
            obj=json.loads(f.read_text(encoding='utf-8-sig'))
            def walk(x):
                if isinstance(x,str):
                    if re.search(r'[A-Za-z]:\\Users\\|[A-Za-z]:\\1\.5\\',x):
                        raise AssertionError('Private path in '+str(f.relative_to(ROOT)))
                elif isinstance(x,dict):
                    for v in x.values():walk(v)
                elif isinstance(x,list):
                    for v in x:walk(v)
            walk(obj)
        if f.suffix not in {'.md','.html'}:
            continue
        text=f.read_text(encoding='utf-8')
        links=re.findall(r'\]\(([^)]+)\)',text) if f.suffix=='.md' else re.findall(r'(?:src|href)="([^"]+)"',text)
        for link in links:
            if re.match(r'https?://|mailto:|#',link):
                continue
            local=unquote(link.split('#')[0])
            check((f.parent/local).exists(), 'local document reference: '+local)
    if args.assets:
        def check_bundle(bundle):
            path=args.assets/bundle['file']
            assert path.is_file() and path.stat().st_size==bundle['bytes'], bundle['file']
            assert digest(path)==bundle['sha256'], 'ZIP SHA-256 '+bundle['file']
            assert path.stat().st_size<2*1024**3, 'Release asset too large'
            model_hashes={x['file']:x['sha256'] for x in model_list}
            with zipfile.ZipFile(path) as z:
                for info in z.infolist():
                    h=hashlib.sha256()
                    with z.open(info) as stream:
                        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
                    expected=info.filename.removeprefix('pool/') if bundle['kind']=='dataset' else model_hashes[info.filename]
                    assert h.hexdigest()==expected, 'Object hash '+info.filename
            return bundle['file']
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            for name in ex.map(check_bundle,load('resource-bundles.json')):
                check(True,'ZIP and every internal object hash: '+name)
    report={'status':'passed','checks':len(checks),'file_count':len(files),'scope':'static file validation; optional archive object validation; no vendor runtime inference','details':checks}
    if args.report:
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS:',len(checks),'file / dependency / document checks;',len(files),'files. No vision inference performed.')

if __name__=='__main__':
    main()
