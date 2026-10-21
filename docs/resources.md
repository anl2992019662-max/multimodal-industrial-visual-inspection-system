# 模型、数据与训练资料

主项目与大型资源分开保存。[v1.0.0 Release](https://github.com/anl2992019662-max/industrial-vision-prelim/releases/tag/v1.0.0) 提供完整资源下载与 SHA-256 清单。下载后使用 `tools/prepare.py` 校验和恢复，不需要手工改写大型算法 XML。

## 资源统计

- 原始数据集：729 张图像。
- 17 个训练项目与原始数据集合计 2084 个逻辑图片路径；去重后 729 个独立图像，原始字节共 12.880 GB。
- 24 个导出模型版本，默认启用 5 个，默认模型字节共 331.116 MB。
- 资源共 19 个 ZIP，每个均小于 2 GiB；所有包及内部模型、图片均有 SHA-256。

图片去重依据完整文件哈希，不按文件名猜测。恢复映射保留每个训练项目的原逻辑路径，没有用一张同名图片覆盖另一张。主项目中的 12 张演示图转换为无损 PNG，尺寸和像素内容不缩放、不裁切。

## 默认模型

| 模型文件 | 大小 MB |
|---|---:|
| `project/Model/01jipian/01_jipianfenlei/model/ExportModel/ClsModel_20260706100808639.bin` | 94.483 |
| `project/Model/02xianlan/02_xianlan/model/ExportModel/DetModel_20260707000012260.bin` | 23.850 |
| `project/Model/03shoutao/03_shoutaofenlei/model/ExportModel/ClsModel_20260706123312343.bin` | 94.458 |
| `project/Model/04xinpian/04_xinpianfenlei/model/ExportModel/ClsModel_20260706143049292.bin` | 94.483 |
| `project/Model/04xinpian/04_xinpianweizhidu/model/ExportModel/xinpianweizhidu.bin` | 23.842 |

## 配套 ZIP

`model-library.zip` 保留全部可找到的原始导出 `.bin`，没有重训或改权重。`dataset-pool-XX.zip` 保存按哈希去重的完整图像；使用 `tools/prepare.py --with-dataset` 根据映射恢复，不能只把哈希文件名直接作为平台数据目录。

| 资源包 | 大小 MB | 内容 |
|---|---:|---|
| `dataset-pool-01.zip` | 405.6 | 46 图像对象 |
| `dataset-pool-02.zip` | 403.1 | 35 图像对象 |
| `dataset-pool-03.zip` | 401.4 | 31 图像对象 |
| `dataset-pool-04.zip` | 416.8 | 36 图像对象 |
| `dataset-pool-05.zip` | 401.7 | 50 图像对象 |
| `dataset-pool-06.zip` | 386.4 | 44 图像对象 |
| `dataset-pool-07.zip` | 396.5 | 36 图像对象 |
| `dataset-pool-08.zip` | 385.9 | 37 图像对象 |
| `dataset-pool-09.zip` | 387.0 | 36 图像对象 |
| `dataset-pool-10.zip` | 402.4 | 50 图像对象 |
| `dataset-pool-11.zip` | 401.2 | 47 图像对象 |
| `dataset-pool-12.zip` | 407.3 | 45 图像对象 |
| `dataset-pool-13.zip` | 401.9 | 41 图像对象 |
| `dataset-pool-14.zip` | 414.7 | 39 图像对象 |
| `dataset-pool-15.zip` | 419.6 | 49 图像对象 |
| `dataset-pool-16.zip` | 400.0 | 40 图像对象 |
| `dataset-pool-17.zip` | 394.1 | 51 图像对象 |
| `dataset-pool-18.zip` | 251.1 | 16 图像对象 |
| `model-library.zip` | 759.9 | 24 模型文件 |

默认推理只需模型包；完整训练复现还需所有图像包。清单见 `manifests/resource-bundles.json`。资源包在 GitHub Release 分发，避免将大模型和重复图像直接塞入 Git 历史。[GitHub 大文件说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[Release 资源说明](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)。

## 训练项目

| 项目 | 原始图片数 | 标注/划分文件数 |
|---|---:|---:|
| `01_1_louhan(less)` | 20 | 14 |
| `01_2_duohan(more)` | 18 | 20 |
| `01_3_hanpian(skew)` | 92 | 68 |
| `01_4_hanchuan(break)` | 36 | 40 |
| `01_5_pianyi(jipian)` | 20 | 21 |
| `01_jipianfenlei` | 220 | 5 |
| `02_xianlan` | 20 | 15 |
| `03_1_kongmo` | 68 | 5 |
| `03_2_posun` | 136 | 5 |
| `03_shoutaofenlei` | 159 | 5 |
| `04_1_juanxian` | 50 | 54 |
| `04_2_lianxian` | 33 | 36 |
| `04_3_louhan` | 50 | 52 |
| `04_4_pianxian` | 50 | 51 |
| `04_5_wanxian` | 50 | 54 |
| `04_xinpianfenlei` | 283 | 5 |
| `04_xinpianweizhidu` | 50 | 54 |

## 历史引用与排除项

共 17 处模型引用：5 处默认启用，12 处受停用父分支控制。停用的“检测 → 手套空模”引用了缺失历史模型，发布引用记为 `Model/legacy/missing-posun.bin`，该路径无真实文件。所有现有导出模型均保留，但不凭名称为缺失引用指定替代模型。

原始目录中的嵌套旧工程、Backup、Logs、Temp、账户数据库、保护配置和 TempModel 中的训练优化器断点未发布。主工程选用外层 `program1.5`，保留其完整 Config/FAIs/Icons 与项目头。详细路径调整见 `manifests/packaging-changes.json`。

标签与训练元数据保留原内容，绝对个人目录转换为可恢复路径。软件格式可能依赖特定版本，重新打开原训练工程与评价仍需实际平台确认。
