# Channel capabilities

| Channel | Media | Execution | Verification |
|---|---|---|---|
| YouTube | One video | Optional official Python client | Local tests only |
| Publication email | Images, video, documents | SMTP over TLS | Local tests only |
| Xiaohongshu | Images or video | Host browser workflow | No live-account verification |
| Bilibili | One video | Host browser workflow | No live-account verification |
| Instagram | Images or video | Host browser workflow | No live-account verification |
| Publication web form | Per publication rules | Host browser workflow | No live-account verification |

No claim of exhaustive platform support. Limits and available features vary by account and may change. Inspect the live interface and official guidance before committing content. If no browser tool or session is available, return blocked with prepared artifacts.

New scripted transports implement execute(artifact, destination) returning a state and receipt; register them in scripts/media_distribution.py and add channel capability validation. Exceptions become unknown to prevent duplicate writes. Adapters must not conceal partial sends as safely retryable failures.
