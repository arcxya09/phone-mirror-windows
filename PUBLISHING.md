# 文档维护与发布边界

目标仓库为 `arcxya09/phone-mirror-windows`，公开可见，默认分支 `main`。本次为设计基线，未创建软件 Release，不包含应用二进制。

## 文档维护

修改需求时同步更新 `DESIGN.md`、相应详细章节及验收编号。涉及接口时同步更新 Schema 和例子；涉及路径时检查所有相对链接。

在仓库根目录运行（Python 3.10 或更新版本）：

```text
python -m pip install -r requirements-dev.txt
python tools/verify_docs.py
python -m unittest discover -s tests -v
```

本次仓库不附带预生成的 SHA256 清单。默认校验 UTF-8、文件链接、配置和协议样例、验收编号及资料引用；若目录中存在 `MANIFEST.sha256`，同时校验摘要。不存在时明确报告跳过摘要，不宣称已验证摘要。

需要对已审查的本地快照生成清单时运行：

```text
python tools/verify_docs.py --refresh-manifest
python tools/verify_docs.py --require-manifest
```

`--refresh-manifest` 会更新本地 `MANIFEST.sha256`，只用于已审查的文档变更。该摘要文件用于一致性检查，不是数字签名；同时替换正文和摘要仍需代码审查发现。`--require-manifest` 在清单缺失时也会报错。检查器不访问手机，不连接网络，不上传内容。

只提交本项目文件；禁止提交 ADB 密钥、个人日志、手机截图、配对码、令牌或其他项目材料。常规更新采用新提交或 Pull Request，不强制覆盖分支。

## 软件发布

应用实现须先完成 M0–M4 和真机验收；公开文档或校验通过均不表示软件已经可用。发布前固定二进制依赖、原创许可证、第三方声明、安装包与兼容性报告。详细门槛见 [开发与交付](docs/07-delivery-plan.md)。
