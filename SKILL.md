---
name: media-distribution
description: Use when publishing design images or videos across social platforms, localizing campaign content, or submitting design work to publications by email or web form.
---

# Media Distribution

Prepare one localized content package, preview each destination, execute within explicit authorization, and preserve delivery evidence.

## Start with the task

Identify source assets, target accounts/publications, requested locales and whether the user authorized delivery or only preparation. Use [channel capabilities](references/channels.md) to distinguish executable transports from browser-dependent workflows. Read only the relevant channel references. Do not promise all-platform unattended automation.

Read [content format](references/content-format.md) and use [the example](examples/image-package.json). Prepare idiomatic localized titles and copy, preserving facts, credits and links. Each destination selects its locale explicitly. Request missing publication recipients or requirements rather than inventing them. Supplied video may contain burned-in captions; sidecar caption uploading is not implemented.

## Prepare and preview

Run commands through Python, using absolute script paths when outside the installed skill folder:

```bash
python3 scripts/media_distribution.py validate examples/image-package.json
python3 scripts/media_distribution.py prepare examples/image-package.json --output prepared
python3 scripts/media_distribution.py --state-dir .distribution-state preview prepared/package-REPLACE/artifact.json
```

Replace the artifact path with the value returned by prepare. Preview, approve and execute consume that artifact, not the original package. Show the final localized copy, destination account, media order, attachments and visibility. Verify that the authenticated account actually matches its label. Check the platform's current restrictions before seeking approval.

## Authorize and deliver

Read [authorization and recovery](references/authorization.md). Default to preview. After explicit user approval of that artifact:

```bash
python3 scripts/media_distribution.py --state-dir .distribution-state approve prepared/package-REPLACE/artifact.json
python3 scripts/media_distribution.py --state-dir .distribution-state execute prepared/package-REPLACE/artifact.json --send
python3 scripts/media_distribution.py --state-dir .distribution-state status
```

Do not approve on the user's behalf just because scripts are available. Full automatic execution requires explicit task/account/channel authorization; use grant only for that scope and revoke afterward. Grants require --artifact and bind exact destination configuration and locale while allowing content revisions of that task; disclose this scope. Host tool permissions remain binding, especially for email.

For executable channels read [setup](references/setup.md). For browser channels use [Instagram](references/channels/instagram.md), [Xiaohongshu](references/channels/xiaohongshu.md), [Bilibili](references/channels/bilibili.md), or [publication forms](references/channels/publications.md). A blocked CLI browser result is a handoff, never success. Before opening a manual publishing flow, run claim ARTIFACT --key KEY using the same --state-dir. This atomically reserves the browser destination and marks it unknown until a receipt is recorded. A second claim fails. Inspect existing status to avoid repeating a published or unknown attempt. Capture a receipt and use record-receipt with the execution key, state and evidence.

## Recovery and reporting

Keep the same artifact and state directory for retries. Do not re-prepare merely to retry: new artifacts can represent a new delivery. Never resend an unknown result without checking external account/server history. Reconcile to failed only with evidence that no delivery occurred. Preserve partial successes.

Report each destination as prepared, blocked, unknown, published or submitted, with evidence and next action. Editorial accepted/rejected requires explicit evidence following submission. Upload success does not guarantee video processing or public visibility. Missing tools, sessions or credentials produce a blocked outcome and a usable prepared package.
