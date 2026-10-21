# 工程结构与数据流

![系统总览](images/system-overview.svg)

主流程位于 `project/Config/FlowAndTool/Flow/MainFlow/Main.page`。下表是现有平台流程节点的对应关系；它说明连接关系，不据此推断具体线程数、响应时间或硬件控制能力。

| 节点 | 功能 | 算法配置 |
|---|---|---|
| ATOM_1 | 内部触发 | 主流程中的触发入口 |
| ATOM_2 | 极片焊点检测 | `ToolBox/Algo_ATOM_2/AlgoFlowTree_ATOM_2#0.xml` |
| ATOM_3 | 线序姿态调整 | `ToolBox/Algo_ATOM_3/AlgoFlowTree_ATOM_3#0.xml` |
| ATOM_4 | CPE 手套质量检测 | `ToolBox/Algo_ATOM_4/AlgoFlowTree_ATOM_4#0.xml` |
| ATOM_5 | 鼠标芯片缺陷检测与位置度 | `ToolBox/Algo_ATOM_5/AlgoFlowTree_ATOM_5#0.xml` |
| ATOM_6 | 结果数据分析 | 主流程分析节点与 `project/FAIs/` 数据定义 |

四项流程均先以文件夹采图。极片和手套默认走分类组；线缆走目标检测与原始 C# 脚本；芯片包含标定、模板定位、坐标转换、几何工具、位置度目标检测和缺陷分类。

HMI 位于 `project/Config/HMIWindows/HMIWindow.window`，配置画布为 1920 × 1080。运行截图包含四个图像窗口、结果标签、拍照触发、运行/停止控件和测量表。截图像素尺寸来自屏幕导出，与配置画布尺寸不同。

芯片结果进入 ATOM_6，结合标准值与公差显示 X/Y 表格。原标定文件、FAI 表及完整绑定保留，不以新绘制图示替代平台配置。

历史检测组仍留在算法 XML 中。检查依赖时必须同时检查节点及全部父节点的启用状态；不能把停用组内标记为启用的子节点误算为默认依赖。具体 17 处引用与启用状态见 `manifests/model-references.json`。

各任务图解及赛题样例见[图片集](gallery.md)。默认工程没有机械执行器代码、跨平台推理服务或手机端；线缆模块输出旋转建议文字。
