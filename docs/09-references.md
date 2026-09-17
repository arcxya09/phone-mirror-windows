# 09 官方资料与版本核验

核验日期：2026-09-17。以下链接用于追溯技术事实，规格中的尺寸、超时、默认行为和测试门槛为本项目设计选择。文档及发布说明核验不等于下载校验、编译或真机验证。

## 资料索引

| 编号 | 官方资料 | 本设计引用范围 |
| --- | --- | --- |
| R1 | [scrcpy v4.1 README](https://github.com/Genymobile/scrcpy/blob/v4.1/README.md)；[v4.1 发布说明](https://github.com/Genymobile/scrcpy/releases/tag/v4.1) | 桌面显示、控制、平台及 OEM 权限边界 |
| R2 | [Android Debug Bridge](https://developer.android.com/tools/adb) | Android 11+ 无线配对、手动端点、授权删除、Android 17 的能力差异 |
| R3 | [Keyboard](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/keyboard.md) | SDK 字符限制、UHID 实体键盘、AOA 传输条件 |
| R4 | [scrcpy for developers](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/develop.md) | 手机端临时组件、媒体与控制通道、内部协议版本匹配 |
| R5 | [Control](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/control.md)；[Shortcuts](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/shortcuts.md) | 剪贴板、只读、拖放安装与传输、默认快捷键 |
| R6 | [Video](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/video.md)；[Audio](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/audio.md)；[Window](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/window.md)；[Device](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/device.md) | 分辨率/码率/帧率、音频限制、全屏与显示屏控制 |
| R7 | [Architecture of ADB Wifi](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/adb_wifi.md) | TLS 配对与连接服务、mDNS、调试信任 |
| R8 | [SDK Platform-Tools release notes](https://developer.android.com/tools/releases/platform-tools) | 37.0.1 版本与 mDNS 后端变化；依赖分发条款入口 |
| R9 | [ADB man page](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/user/adb.1.md) | 本机服务端口、地址、密钥环境变量和命令语义 |
| R10 | [Windows App SDK](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/) | WinUI 3 技术栈；产品实际支持范围仍需本项目验证 |
| R11 | [Android environment variables](https://developer.android.com/tools/variables) | 用户配置目录；不能单凭通用变量文档认定所有 ADB 路径已隔离 |
| R12 | [Mouse](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/mouse.md)；[Shortcuts](https://github.com/Genymobile/scrcpy/blob/v4.1/doc/shortcuts.md) | SDK 坐标鼠标、UHID/AOA 区别、手势映射 |
| R13 | [WindowManager.LayoutParams: FLAG_SECURE](https://developer.android.com/reference/android/view/WindowManager.LayoutParams#FLAG_SECURE) | 敏感窗口的捕获与显示保护 |
| R14 | [scrcpy LICENSE](https://github.com/Genymobile/scrcpy/blob/v4.1/LICENSE) | scrcpy 的 Apache-2.0 许可，不代表其所有依赖使用同一许可 |
| R15 | [scrcpy app/meson.build](https://github.com/Genymobile/scrcpy/blob/v4.1/app/meson.build)；[客户端源码](https://github.com/Genymobile/scrcpy/tree/v4.1/app/src) | SDL3/FFmpeg 构建依赖；实现时审查输入和 ADB 子调用 |
| R16 | [ADB client/auth.cpp](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/client/auth.cpp) | 默认用户密钥与附加密钥加载；专用目录必须实测 |
| R17 | [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) | 公开可见与许可证授权的区别 |

## 本次核验产生的工程约束

scrcpy 发布候选为 v4.1；发布页列出 SDL 3.4.12、FFmpeg 8.1.2 等更新。版本号只用于首轮验证，不能据此跳过依赖兼容及分发核查。[R1][R15]

Platform-Tools 发布页列出的 37.0.1 已移除 openscreen。ADB 使用指南与旧 man page 可能保留较旧的修复步骤；实施时以锁定版本的命令能力、实际输出和对应源码为准。[R2][R8][R9]

Android 17 的 Wi-Fi 2.0 机制作为新能力分支；Android 11 手机仍需独立测试配对与重新连接。[R2]

即便固定到 v4.1，开发文档中的部分命令示例仍写有 4.0。不能照抄旧服务端版本参数；应由实际打包版本生成参数，并执行匹配校验。[R4]

原生 scrcpy 具有拖放文件和安装 APK 的入口。产品要求关闭这些入口，必须审查实际事件处理链，不能只删菜单。[R5]

所有指向 HEAD 的 AOSP 链接是设计依据，不是不可变的构建锁。M0 需将实际使用的源码修订、下载摘要和构建版本固定下来。

## 尚未执行的验证

未下载并审核 Windows 二进制依赖，未在 Windows 上编译，未连接手机，未验证无线网卡/路由器、OEM 权限或中文输入法。候选版本不构成兼容承诺，所有实测状态见[测试计划](06-test-plan.md)。
