# 图片与流程图

## 最终运行界面

![最终运行截图](images/hmi-final.png)

作者提供的历史运行原图。与下面的赛题要求插图分开标明：赛题插图不是本工程推理结果。

## 总体结构

![总体结构](images/system-overview.svg)

## 原平台流程缩略图

![原工程流程图](images/original-flow.png)

原工程自带缩略图，保留原分辨率，不用插值重画冒充更高清的原图。

## 极片焊点检测

![极片焊点检测流程](images/electrode-pipeline.svg)

| 极片：漏焊 | 极片：多焊 | 极片：焊偏 |
| --- | --- | --- |
| ![极片：漏焊](../docs/images/brief/electrode-less.png) | ![极片：多焊](../docs/images/brief/electrode-more.png) | ![极片：焊偏](../docs/images/brief/electrode-skew.png) |

| 极片：焊穿 | 极片：偏移 | 极片：合格 |
| --- | --- | --- |
| ![极片：焊穿](../docs/images/brief/electrode-break.png) | ![极片：偏移](../docs/images/brief/electrode-offset.png) | ![极片：合格](../docs/images/brief/electrode-ok.png) |

来源：赛题 PDF 第 4 页；裁切只提取说明图，保留原图中的缺陷标记。

## 线缆姿态调整

![线缆姿态调整流程](images/cable-pipeline.svg)

| 线缆：标准姿态 | 线缆：待旋转 | 线缆：角度示意 |
| --- | --- | --- |
| ![线缆：标准姿态](../docs/images/brief/cable-standard.png) | ![线缆：待旋转](../docs/images/brief/cable-test.png) | ![线缆：角度示意](../docs/images/brief/cable-angle.png) |

来源：赛题 PDF 第 5 页；裁切只提取说明图，保留原图中的缺陷标记。

## CPE 手套质检

![CPE 手套质检流程](images/glove-pipeline.svg)

| 手套：空模 | 手套：破损 | 手套：合格 |
| --- | --- | --- |
| ![手套：空模](../docs/images/brief/glove-empty.png) | ![手套：破损](../docs/images/brief/glove-damage.png) | ![手套：合格](../docs/images/brief/glove-ok.png) |

来源：赛题 PDF 第 5 页；裁切只提取说明图，保留原图中的缺陷标记。

## 芯片缺陷与位置度

![芯片缺陷与位置度流程](images/chip-pipeline.svg)

| 芯片：卷线 | 芯片：连线 | 芯片：漏焊 |
| --- | --- | --- |
| ![芯片：卷线](../docs/images/brief/chip-coil.png) | ![芯片：连线](../docs/images/brief/chip-link.png) | ![芯片：漏焊](../docs/images/brief/chip-missing.png) |

| 芯片：偏线 | 芯片：弯线 | 芯片：合格 |
| --- | --- | --- |
| ![芯片：偏线](../docs/images/brief/chip-offset.png) | ![芯片：弯线](../docs/images/brief/chip-bent.png) | ![芯片：合格](../docs/images/brief/chip-ok.png) |

| 芯片位置：X 基准 | 芯片位置：Y 基准 | 芯片位置：基准总览 |
| --- | --- | --- |
| ![芯片位置：X 基准](../docs/images/brief/datum-x.png) | ![芯片位置：Y 基准](../docs/images/brief/datum-y.png) | ![芯片位置：基准总览](../docs/images/brief/datum-overview.png) |

| 芯片位置：位置度 |
| --- |
| ![芯片位置：位置度](../docs/images/brief/chip-position.png) |

来源：赛题 PDF 第 6 页；裁切只提取说明图，保留原图中的缺陷标记。

## 来源与区分

22 张赛题插图由本地 PDF 渲染裁切，原页码、区域和哈希记录于 `manifests/figures.json`。5 张 SVG 是依据工程重新绘制的结构/流程说明；实际运行截图未作编辑。详见[第三方说明](../THIRD_PARTY_NOTICES.md)。
