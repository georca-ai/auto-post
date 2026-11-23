# Media Distribution

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md)

## 面向设计作品的多语言发布

准备图文与视频内容，发布到社交平台或向设计媒体投稿。支持文案本地化、逐渠道预览和投放结果记录。

将 SKILL.md、scripts/、references/ 和 examples/ 一起复制到你的代理技能目录下的 media-distribution 文件夹。需要 Linux/macOS 和 Python 3.12+。素材准备及邮件投稿仅依赖标准库；YouTube 需要可选 Google 客户端和 OAuth 授权文件，详见[安装说明](references/setup.md)。

YouTube 视频上传与 SMTP 投稿提供执行适配器。Instagram、小红书、Bilibili 及媒体投稿表单依赖代理提供的浏览器工具和登录会话。缺少条件时返回 blocked，不会虚报成功。尚未进行真实账号测试或当前平台界面核验。

先将示例占位图片换成你的素材。在 localizations 中添加各语言标题和正文，并为每个渠道指定语言。自动授权按内容 ID、账号与渠道限定，跨修订有效，用后撤销。重试时保留同一产物和状态目录；不确定是否送达时先核查外部记录。submitted 仅表示已提交，不代表媒体录用。不支持字幕侧文件上传或定时发布。

```bash
python3 scripts/media_distribution.py validate examples/image-package.json
python3 scripts/media_distribution.py prepare examples/image-package.json --output prepared
# Use the artifact path returned above.
python3 scripts/media_distribution.py --state-dir .distribution-state preview prepared/package-REPLACE/artifact.json
# Only after explicit approval:
python3 scripts/media_distribution.py --state-dir .distribution-state approve prepared/package-REPLACE/artifact.json
python3 scripts/media_distribution.py --state-dir .distribution-state execute prepared/package-REPLACE/artifact.json --send
python3 scripts/media_distribution.py --state-dir .distribution-state status
```

[Skill](SKILL.md) · [Content format](references/content-format.md) · [Authorization and recovery](references/authorization.md) · [Channels](references/channels.md)

```bash
python3 -m unittest discover -s tests -v
```
