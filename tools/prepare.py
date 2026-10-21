"""Prepare a separate runnable copy. Python 3.10+, standard library only."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT / 'manifests' / name).read_text(encoding='utf-8'))

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()

def inside(base, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts or '\\' in relative or ':' in relative:
        raise ValueError('Unsafe archive path: ' + relative)
    path = base.joinpath(*name.parts).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError('Path escapes destination')
    return path

def unpack(archive, destination, prefix=''):
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            if prefix and not member.filename.startswith(prefix):
                raise ValueError('Unexpected archive member: ' + member.filename)
            relative = member.filename[len(prefix):]
            target = inside(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(member) as src, target.open('wb') as out:
                shutil.copyfileobj(src, out)

def bind_inputs(project):
    for binding in load('image-bindings.json'):
        path = project / binding['file']
        data = path.read_text(encoding='utf-8-sig')
        pattern = r'<RefItem\b[^>]{0,4096}\bId="' + re.escape(binding['ref_id']) + r'"[^>]{0,4096}>'
        folder = str(project / Path(binding['folder'].replace('\\', '/'))) + os.sep
        if not Path(folder).is_dir():
            raise FileNotFoundError(folder)
        hits = [0]
        def replace(match):
            hits[0] += 1
            return re.sub(r'CustomValue="[^"]*"', lambda _: 'CustomValue="' + html.escape(folder, quote=True) + '"', match[0])
        data = re.sub(pattern, replace, data)
        if hits[0] != 1:
            raise ValueError('Input binding is not unique: ' + binding['ref_id'])
        path.write_text(data, encoding='utf-8-sig', newline='')

def bind_paths(project, vision_dir):
    paths = [x['reference'] for x in load('model-references.json') if x['exists']]
    paths += [r'Config\FlowAndTool\Calibration\005-A0-004_棋盘格标定.calck', r'Icons\DCCK_logo.png']
    for path in (project / 'Config').rglob('*'):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding='utf-8-sig')
        except UnicodeError:
            continue
        for relative in set(paths):
            text = text.replace('"' + relative + '"', '"' + html.escape(str(project / Path(relative.replace('\\', '/'))), quote=True) + '"')
        if vision_dir:
            text = text.replace('D:\\VisionPlus\\bin\\', html.escape(str(Path(vision_dir).resolve() / 'bin') + os.sep, quote=True))
        path.write_text(text, encoding='utf-8-sig', newline='')
    def resolve(v):
        if isinstance(v, str) and v.startswith('Model\\'):
            return str(project / Path(v.replace('\\', '/')))
        if isinstance(v, dict):
            return {k: resolve(x) for k, x in v.items()}
        if isinstance(v, list):
            return [resolve(x) for x in v]
        return v
    for path in (project / 'Model').rglob('Project.dls'):
        obj = resolve(json.loads(path.read_text(encoding='utf-8')))
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets', type=Path, help='Directory containing checked release ZIP assets')
    p.add_argument('--destination', type=Path, default=ROOT / 'runtime', help='New directory; never overwrite an existing copy')
    p.add_argument('--vision-plus-dir', type=Path, help='Installed VisionPlus folder if different from D:\\VisionPlus')
    p.add_argument('--with-dataset', action='store_true', help='Restore primary dataset and all training image layouts')
    p.add_argument('--copy-data', action='store_true', help='Use independent copies instead of hard links for image layouts')
    p.add_argument('--demo-only', action='store_true', help='Prepare only UI/config inspection copy without models; cannot perform inference')
    args = p.parse_args()
    if args.demo_only and args.with_dataset:
        p.error('--demo-only cannot be combined with --with-dataset')
    if not args.demo_only and not args.assets:
        p.error('--assets is required for inference preparation')
    dest = args.destination.resolve()
    if dest.exists():
        p.error('Destination exists. Choose a new folder to preserve existing work.')
    bundles = [b for b in load('resource-bundles.json') if b['kind'] == 'models' or args.with_dataset]
    if not args.demo_only:
        for b in bundles:
            archive = args.assets / b['file']
            if not archive.is_file() or archive.stat().st_size != b['bytes'] or digest(archive) != b['sha256']:
                raise ValueError('Missing or mismatched asset: ' + b['file'])
            print('Verified', b['file'])
    project = dest / 'project'
    shutil.copytree(ROOT / 'project', project)
    if not args.demo_only:
        for b in bundles:
            archive = args.assets / b['file']
            if b['kind'] == 'models':
                unpack(archive, project, 'project/')
            else:
                unpack(archive, dest / '.resources')
        for model in load('models.json'):
            path = dest / model['file']
            if digest(path) != model['sha256']:
                raise ValueError('Model hash mismatch: ' + model['file'])
        if args.with_dataset:
            rows = load('dataset-files.json')
            for key in sorted({row['sha256'] for row in rows}):
                if digest(dest / '.resources' / 'pool' / key) != key:
                    raise ValueError('Dataset object hash mismatch: ' + key)
            for row in rows:
                source = dest / '.resources' / 'pool' / row['sha256']
                target = inside(dest, row['target'])
                target.parent.mkdir(parents=True, exist_ok=True)
                if args.copy_data:
                    shutil.copy2(source, target)
                else:
                    try:
                        os.link(source, target)
                    except OSError:
                        shutil.copy2(source, target)
    bind_inputs(project)
    bind_paths(project, args.vision_plus_dir)
    missing = [x['reference'] for x in load('model-references.json') if x['effective_enabled'] and not (project / Path(x['reference'].replace('\\', '/'))).is_file()]
    if missing and not args.demo_only:
        raise FileNotFoundError('Active model missing: ' + str(missing))
    report = {'mode': 'inspection-only' if args.demo_only else 'inference-assets-prepared', 'dataset_restored': args.with_dataset,
              'active_models_available': 5 - len(missing), 'platform_execution': 'not performed by this tool',
              'legacy_missing_disabled_model': 'Model/legacy/missing-posun.bin'}
    (dest / 'preparation-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Prepared:', project / 'program1.5.vpsx')
    print('Open this file in licensed VisionPlus. Review docs/reproduction.md before running.')

if __name__ == '__main__':
    main()
