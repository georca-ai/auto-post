# Media Distribution

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md)

## Multilingual publishing for design work

Prepare image posts and videos for social platforms and submit work to editorial publications. Localize copy, preview each destination, and retain delivery evidence.

Copy SKILL.md, scripts/, references/ and examples/ together into a media-distribution directory in your agent’s skill location. Python 3.12+ on Linux/macOS is required. Preparation and SMTP use the standard library. YouTube requires optional Google client packages and authorized OAuth credentials; see [setup](references/setup.md).

YouTube video and SMTP submissions have executable adapters. Instagram, Xiaohongshu, Bilibili and publication forms use host browser workflows with an authenticated session. Missing prerequisites produce blocked results. No live-account testing or current platform-interface verification is claimed.

Replace the example placeholder image with your own media. Add title/body translations under localizations and select a locale for every destination. Grants explicitly scope content ID, account and channel and persist across revisions; revoke them after use. Use the same artifact and state directory for retries. Unknown delivery outcomes require external evidence before retry; submitted is not editorial acceptance. Sidecar subtitle uploading and scheduling are not implemented.

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
