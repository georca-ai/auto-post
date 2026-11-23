# Media Distribution

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md)

## デザイン作品の多言語配信

画像付き投稿や動画を準備し、ソーシャルプラットフォームへの公開やデザイン媒体への投稿を進めます。言語ごとの文章、送信先別プレビュー、配信記録に対応します。

SKILL.md、scripts/、references/、examples/ をまとめて、エージェントのスキル保存先の media-distribution フォルダーへコピーします。Linux/macOS と Python 3.12 以降が必要です。準備と SMTP は標準ライブラリを使用します。YouTube には Google クライアントと OAuth 認証情報が必要です。[設定](references/setup.md)を参照してください。

YouTube 動画と SMTP 投稿には実行アダプターがあります。Instagram、小紅書、Bilibili、媒体の投稿フォームには、ログイン済みのブラウザーツールが必要です。前提条件が不足すると blocked になります。実アカウントや現在の画面での検証は行っていません。

サンプル画像を自分の素材に置き換え、localizations に各言語のタイトルと本文を追加します。送信先ごとに言語を指定してください。自動実行の許可はコンテンツ ID、アカウント、チャネル単位で、修正後も有効です。使用後に取り消してください。再試行では同じ成果物と状態ディレクトリを使用し、不明な結果は外部記録で確認します。submitted は採用を意味しません。字幕ファイルのアップロードと予約配信には対応していません。

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
