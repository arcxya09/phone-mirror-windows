# 02 系统架构与接口设计

## 1. 组件边界

```text
Windows 当前用户会话
  WinUI 3 管理进程
    ├─ 设备页 / 配对向导 / 设置 / 文字面板
    ├─ SessionCoordinator：串行化设备会话、状态和取消
    ├─ AdbSupervisor：自有 ADB 的启动、端口和凭据目录
    ├─ DeviceDiscovery：发现事件、超时和缓存
    ├─ DeviceRepository / SettingsStore：本地元数据
    └─ DiagnosticService：白名单诊断和脱敏导出
          │ 版本化本地命名管道，不承载视频帧
          ▼
  定制 scrcpy 原生子进程
    ├─ 受控 IPC 适配器 / 输入策略
    ├─ SDL 原生视频窗口 / FFmpeg 解码及声音
    └─ scrcpy 控制消息、设备端启动及隧道
          │ 本机回环上的 ADB 控制/隧道端点
          ▼
  本应用自有 ADB server
          │ Android 无线调试的认证连接
          ▼
  Android adbd → scrcpy 临时服务组件
    ├─ 屏幕采集与编码
    ├─ 输出音频采集
    └─ 经授权的鼠标、键盘与剪贴板控制
```

scrcpy 本身使用客户端/手机端组件和分离的媒体、控制连接；其内部协议要求版本匹配。以上是在上游能力之上的产品分层，不表示现成 scrcpy 已提供本地管理 API。[R4] 见[参考资料](09-references.md)。

## 2. 技术选型

管理界面选择 C# + WinUI 3。开发启动时锁定稳定版 Windows App SDK、仍在支持期的 .NET LTS、Windows SDK、C++ 构建链和依赖版本。Windows 10 22H2 与 Windows 11 x64 是产品验证目标，框架宣称的较低系统要求不自动扩大产品支持范围。[R10]

原生引擎以 scrcpy v4.1 为首轮验证候选；依据该标签保留 SDL/FFmpeg 架构。v4.1 源码已使用 SDL3，不能沿用旧版本 SDL2 专用代码和构建假设。[R15]

ADB 以 Platform-Tools 37.0.1 为首轮验证候选；版本锁应包括完整构建版本及包校验值，`adb version` 的协议号 `1.0.41` 不能代替 Platform-Tools 版本。[R8]

本设计不添加 Electron、WebView、云 API 或数据库服务。元数据使用版本化 JSON；大量二进制和临时文件不进入 Git。

## 3. 窗口承载方案

采用独立原生投屏窗口。WinUI 3 不接收视频帧，不通过 XAML 每帧转换图片，不用跨进程 `SetParent` 拼接窗口。

M0：原生窗口 + 键盘快捷键，用于验证链路。

M2：在原生窗口周边增加受控工具区。可选实现为原生轻量操作区，或由管理进程持有、关联到视频 HWND 的工具窗口；首选须由 M0 的混合 DPI 与焦点验证决定并补充 ADR。两者均须满足只有视频内容区域能够向手机传递鼠标事件。

工具窗口不得在后台常驻置顶，也不得通过透明区域穿透点击手机。Alt+Tab、最小化、移动显示器、全屏和屏幕阅读器都需要整体测试。文字面板使用 WinUI 编辑控件，获得焦点时必须暂停引擎键盘转发。

该决策只允许更换工具区实现，不允许用不完整的双窗口拼接替代焦点和输入保护。

## 4. 各模块责任

| 模块 | 输入 | 输出 | 禁止事项 |
| --- | --- | --- | --- |
| AppShell | 用户操作、状态快照 | 展示和命令 | 不同步等待 ADB，不解析原始日志 |
| SessionCoordinator | 用户命令、设备事件 | 唯一会话状态 | 不并行启动重复会话 |
| AdbSupervisor | 固定工具路径、用户配置 | 受控 ADB 端点 | 不杀全局 ADB，不导入其他工具的密钥 |
| DeviceDiscovery | ADB 发现和状态流 | 候选列表 | 不主动扫描整个局域网 |
| EngineHost | 绑定设备、参数 | 引擎进程和本地管道 | 不接受任意命令行覆盖 |
| InputPolicy | 焦点、控制模式 | 允许或拒绝输入 | 不缓存断线期间的用户按键 |
| TextComposer | 用户确认后的文本 | 一次文字请求 | 不自动发送回车，不自动重放 |
| SettingsStore | 已验证设置 | 原子持久化 | 不保存剪贴板正文或配对码 |
| DiagnosticService | 白名单事件 | 轮转日志和导出包 | 不收集全量手机日志或画面 |

## 5. 必需的引擎定制

仅传递命令行参数不能完成整个产品。首版至少包含以下定制点：

1. 命名管道控制入口与结构化事件出口；禁止可执行任意 shell 的通用方法。
2. 首帧、视频尺寸、音频可用性、输入模式、异常退出的明确事件。
3. 桌面失焦、打开文字面板、切换只读时释放按下键、鼠标和虚拟手指。
4. 接受内存中的 UTF-8 文字，走 scrcpy 控制通道；不经 Windows 剪贴板临时中转。
5. 禁止文件拖入触发 push 或 APK 安装。上游默认存在该行为，必须在事件和功能层拦截。[R5]
6. 关闭自动剪贴板同步后的显式粘贴、序号回执及本地去重。
7. 控制失败可降为仅观看，不能让音频或单个输入通道失败带走画面。
8. 统一关闭、清理和会话归属；不通过窗口标题模糊匹配其他 scrcpy 进程。

改造以小范围可审查补丁维护。不得使用窗口消息模拟“按某快捷键”作为 IPC 主方案；不凭 stdout 的一段成功文字判定用户文字已经进入手机应用。

## 6. 进程生命周期

应用按 Windows 用户单实例。第二次启动激活既有设备页或视频窗口，不建立第二套 ADB 凭据。

SessionCoordinator 是会话状态唯一写入者；每次连接拥有 `sessionId` 和单调递增的 `generation`。所有回调必须携带两者。取消或重连后，旧代回调直接丢弃。

进程启动顺序：校验引擎与依赖 → 创建私有数据目录 → 启动受控 ADB → 解析设备 → 创建管道 → 启动匹配版本引擎 → 能力握手 → 观察首帧 → 进入活动会话。

Windows Job Object 用于约束自有子进程，正常停止优先发送 Stop 并等待退出；超过 3 秒才终止对应进程树。不得按进程名称批量结束 adb.exe/scrcpy.exe。ADB 是否以前台模式运行、句柄继承和进程归属在 M0 用进程跟踪实测。

正常退出只清理本会话的端口映射和临时组件。意外断网时不能保证手机端瞬时清理；依赖连接关闭后的上游清理机制，后续连接核验，不做远端无差别 kill。

## 7. 本地 IPC

### 7.1 传输与身份

采用命名管道，按当前 Windows 用户 SID 设置 ACL，拒绝远程管道客户端。随机会话名称和握手随机值经继承句柄/标准输入传递，不放入日志、URL 或公开监听端口。检查客户端 PID 与实际启动的子进程，防止其他应用误接管；同用户恶意进程与管理员不在完全隔离保证范围内。

格式：4 字节无符号小端长度 + UTF-8 JSON。单消息上限 65,536 字节，正文文本另设 16,384 字节上限。发送与接收必须按帧循环，处理拆包、粘包、非法长度、非法 UTF-8 和 EOF。请求队列设上限并支持背压，不无限增长。

### 7.2 消息信封

```json
{
  "protocolVersion": 1,
  "kind": "command",
  "sessionId": "00000000-0000-4000-8000-000000000001",
  "generation": 1,
  "requestId": "00000000-0000-4000-8000-000000000002",
  "method": "InsertText",
  "inputSequence": "1",
  "payload": {"text":"示例文字","appendEnter":false}
}
```

样例均为虚构数据。详见 [IPC Schema](../schemas/local-ipc.schema.json) 和[示例](../examples/ipc-insert-text.json)。该 Schema 是首版核心命令契约；实现新增方法必须先更新契约和测试。

### 7.3 方法与事件

| 方法 | 语义 | 重试 |
| --- | --- | --- |
| Hello | 主/子进程版本和能力握手 | 可在建链时重试 |
| Stop | 停止指定会话 | 幂等 |
| SetControlMode | 控制或仅观看；先释放输入 | 可使用同 requestId 查询结果，勿并发切换 |
| InsertText | 当前手机输入框插入文本，不带 Enter | 禁止自动重试 |
| SetAudioMuted | 仅改变电脑播放端静音 | 设定值幂等 |
| SetDisplayPower | 用户明确请求关闭/恢复手机显示屏 | 必须受控制模式限制 |
| SetWindowMode | 全屏、置顶等桌面窗口状态 | 设定值幂等 |

事件包括 Ready、FirstFrame、VideoSizeChanged、CapabilitiesChanged、InputReleased、TextRequestStatus、AudioUnavailable、StateChanged、Error、Stopped。媒体帧和输入正文不进入事件日志。

Hello 返回协议号、引擎版本、上游标签、实际键盘模式和支持的方法。未知主版本直接拒绝；缺失可选能力关闭对应入口；缺失禁止拖放或输入释放能力时不允许作为正式产品启动。

命令接受回执、手机端剪贴板回执、目标 App 内文字是否成功三个层次必须分离。回执不能升级成“消息已发送”。

## 8. 数据模型

`DeviceRecord`：本地 UUID、用户别名、经过认证后读取的型号、候选稳定标识、上次连接时间、上次成功参数和本地允许连接状态。IP、端口及广播实例名是可过期位置，不是唯一身份凭据。

`SessionSnapshot`：sessionId、generation、状态、当前设备、控制能力、音频能力、帧尺寸、开始时间、最近错误。纯内存，不保留帧或输入内容。

`AppSettings`：schemaVersion、主题、画质档、声音、自动连接偏好、窗口 DIP 边界等。示例与[配置 Schema](../schemas/application-settings.schema.json)对应。

`TextRequest`：随机 requestId、当前会话、UTF-8 字节数、内存文本和执行阶段；结束/取消后清理正文。去重缓存只保留短期 requestId 与状态，不保存文本副本，不跨会话重放。

配置文件采用临时文件写入后原子替换；保留一份不含敏感内容的上次可读备份。未知高版本配置以只读模式提示，不用旧程序覆盖新文件。

## 9. 参数与版本管理

默认候选命令如下，仅说明原始引擎参数，不代表完整产品已实现：

```text
scrcpy --serial=<authenticated-transport> --video-codec=h264 --max-size=1920 --max-fps=60 --video-bit-rate=8M --keyboard=uhid --mouse=sdk --no-clipboard-autosync --audio-source=output --audio-codec=opus --window-title=<device-alias>
```

进程使用绝对路径和参数数组启动；`<...>` 是设计占位符，不供用户直接执行。设备名、地址和文本不进入 shell 拼接。设置 `ADB` 到受控二进制，并验证 scrcpy 全部子调用继承正确的 ADB 服务端点及凭据目录。[R4][R15]

流畅：1280 / 30 fps / 4 Mbps；均衡：1920 / 60 fps / 8 Mbps；清晰：2560 / 60 fps / 16 Mbps。均为上限/请求值，显示实际协商尺寸。修改画质默认重启本次引擎并保留窗口位置，不伪称无缝动态码率。[R6]

锁文件记录 scrcpy 客户端、手机端、补丁版本、ADB、SDL、FFmpeg、运行时和逐文件摘要。候选信息在[候选清单](../upstream-candidates.json)，其状态明确为未测试；正式构建必须另生成经过验证的版本锁。
