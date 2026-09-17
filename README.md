# 手机同屏 Windows 版

基于 scrcpy 与 Android 无线调试的极简手机投屏、鼠标控制和键盘输入工具。

**当前状态：设计阶段。** 本仓库包包含产品规格、技术设计、接口草案、测试计划和文档校验工具，尚无应用程序、安装包或真机测试结果。所有性能数值均为验收目标，不代表已测性能。公开仓库：[`arcxya09/phone-mirror-windows`](https://github.com/arcxya09/phone-mirror-windows)。

## 使用目标

首次在 Android 手机上开启无线调试并配对；之后在电脑上选择手机，一键查看和操作手机。手机无需安装用户可见的 App，不需要 Root。scrcpy 会通过获授权的 ADB 会话临时运行手机端组件，不能将此表述为“手机端完全不运行程序”。技术依据见[官方资料](docs/09-references.md)。

接收端规划为 Windows 10 22H2 / Windows 11 x64；手机最低目标为提供系统无线调试功能的 Android 11。电脑可采用有线局域网，前提是两端能够互通。具体手机、输入法和 Windows 构建号以实测兼容性清单为准。

## 第一版范围

无线配对与设备发现；单设备投屏；鼠标点击、拖动和滚动；UHID 键盘输入；电脑输入法文字面板；设备声音播放；全屏、置顶、仅观看；受限自动重连；脱敏诊断导出。

第一版不实现 iPhone、Miracast/AirPlay 接收、手机原生“无线投屏”入口、互联网远程控制、录屏、文件传输、APK 安装、多设备同屏、账户、云服务和自动更新。配对后的连接入口在电脑端。

## 阅读顺序

| 文档 | 内容 |
| --- | --- |
| [设计总览](DESIGN.md) | 技术路线、默认值、关键边界与阅读导航 |
| [产品与交互](docs/01-product-and-ux.md) | 用户流程、界面规格、焦点和窗口行为 |
| [系统架构](docs/02-architecture.md) | 组件、进程、引擎改造、IPC、数据模型 |
| [无线连接](docs/03-wireless-connection.md) | 配对、端口、身份、状态机、重连和 ADB 隔离 |
| [控制与中文输入](docs/04-control-and-text-input.md) | 鼠标、UHID、剪贴板、文本事务与防重复 |
| [安全与数据](docs/05-security-and-data.md) | 授权边界、隐私、日志、凭据和错误分类 |
| [测试与验收](docs/06-test-plan.md) | 兼容性矩阵、测试用例、性能方法和发布门槛 |
| [开发与交付](docs/07-delivery-plan.md) | 阶段任务、依赖、交付证据、打包和许可证 |
| [架构决策](docs/08-architecture-decisions.md) | 各项选择的理由、代价和验证条件 |
| [参考资料](docs/09-references.md) | 2026-09-17 核验的上游资料及版本差异 |

配置与通信样例位于 [schemas](schemas/application-settings.schema.json) 和 [examples](examples/application-settings.json)。这些是设计契约，未接入实际程序。

## 仓库发布

[提交与发布说明](PUBLISHING.md)说明设计文档维护、校验和后续软件发布的边界。当前不包含仓库创建脚本或应用构建脚本。

文档校验：

```text
python -m pip install -r requirements-dev.txt
python tools/verify_docs.py
python -m unittest discover -s tests -v
```

## 许可证状态

公开可见与授予开源许可证是两件事。本项目原创内容尚未选定分发许可证，此包不擅自套用 MIT、Apache 或其他授权条款。第三方组件保留各自许可证。见 [LICENSE-STATUS.md](LICENSE-STATUS.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
