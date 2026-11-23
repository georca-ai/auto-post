# Setup

Copy this entire repository's SKILL.md, scripts/, references/ and examples/ into a skill directory named media-distribution in your agent's supported skill location. Keep relative paths intact. README files are human documentation and need not be installed.

Requires Python 3.12+ on Linux/macOS. No dependencies for preparation or SMTP. For YouTube install google-api-python-client, google-auth and google-auth-httplib2 into your virtual environment (constraints in pyproject.toml). Obtain authorized-user OAuth credentials through your own Google project and consent flow with youtube.upload scope, store outside this repository, and export a variable holding the credentials file path. Interactive OAuth onboarding is not bundled. Verify project audit, upload visibility restrictions and account quotas before use.

Official references (live verification blocked by network availability during development):
- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol
- https://developers.google.com/identity/protocols/oauth2/native-app

SMTP requires an authenticated TLS mail service with permission to send from the chosen address. Configure environment variables before execution. Never include secrets in examples, shell history or receipts.

YouTube upload receipts indicate resource creation, not completed processing or public availability. Check resulting visibility and playback separately. No real posts or emails were sent during development.
