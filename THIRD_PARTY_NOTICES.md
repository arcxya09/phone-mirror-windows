# 第三方组件与分发审查

本次提交未包含 scrcpy、ADB、SDL、FFmpeg 或 Windows 运行时的源码副本和二进制。下面是计划使用的组件清单，不是已经完成的二进制分发声明。

| 组件 | 计划用途 | 发布前的核查 |
| --- | --- | --- |
| scrcpy | Android 屏幕、音频和输入引擎 | 保留 Apache-2.0、版权与必要声明，注明修改和固定标签 |
| ADB / Platform-Tools | 无线配对与调试连接 | 对实际取得的包、构建方式及组件逐项核查；不把整个 SDK 包统称同一许可 |
| SDL、FFmpeg 与其构建依赖 | 显示、输入、解码和播放 | 按实际编译选项和链接方式生成组件及许可清单 |
| Windows App SDK / .NET | 管理界面和运行时 | 固定版本，核查实际随包内容和再分发条款 |
| Python jsonschema | 仅文档开发校验 | 通过 requirements-dev 安装；不作为用户投屏程序依赖，不随本仓库打包 |

来源：[scrcpy LICENSE](https://github.com/Genymobile/scrcpy/blob/v4.1/LICENSE)、[scrcpy 构建文件](https://github.com/Genymobile/scrcpy/blob/v4.1/app/meson.build)、[Platform-Tools 发布及条款](https://developer.android.com/tools/releases/platform-tools)。

正式软件包必须增加每个实际分发组件的版本、来源、许可证正文、必要归属与源码提供方式，并核查构建配置对应的义务。本文件不宣称已经完成法律审核。
