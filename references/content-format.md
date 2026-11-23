# Content packages

JSON is UTF-8. Paths resolve relative to the source JSON. `prepare` copies assets into a new folder, hashes their bytes and writes artifact.json. Keep that folder intact. Never edit prepared artifacts; prepare and approve a new version instead.

Required fields: content_id (stable task identifier), source_locale (language tag), localizations (map of language tags to title/body), assets (path/type), destinations (channel/account/locale/transport/options). Optional credits are retained; include visible credits in the localized body. No automatic translation fallback. Every destination chooses exactly one locale.

Asset types: image, video, document (publication only). Bilibili and YouTube require exactly one video. Sidecar subtitle uploads are unsupported: supply a captioned video, or attach subtitle documents to a publication package as document assets. No rendering or translation API is bundled; the host prepares translations and checks names, claims, credits and links.

See [example](../examples/image-package.json). Replace its local image before real publication. Example images are tiny placeholders for dry runs, not finished creative assets.

SMTP options: host, port (465 default, implicit TLS), sender, recipient, username_env, password_env. Environment fields name variables; never contain passwords. YouTube options: credentials_env (variable holding authorized-user JSON path), privacy (private default). Browser options: url, plus any publication-specific instructions and account context. Runtime account labels identify consent scope; independently verify that credentials/session belong to the intended account before approval.

For a combined English social post and Japanese editorial submission, see [campaign example](../examples/campaign-package.json). For video, copy [the video template](../examples/video-package.template.json) and replace its nonexistent media path with your actual video before validation.
