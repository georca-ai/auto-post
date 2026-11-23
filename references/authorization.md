# Authorization and recovery

Preparation and preview do not send. Obtain explicit authorization for the exact preview before invoking approve. `execute --send` requires a stored approval or grant. A grant must be explicitly requested by the user, scoped to content ID, account and channel; a configuration file is not consent. Host permissions still apply. Revoke grants when the task ends.

Use a separate state directory per operator; do not delete it between runs. State is local, advisory-lock protected and atomically replaced. It is not a security boundary against someone who can edit its files. Supported runtime: Linux/macOS with fcntl.

A changed prepared asset blocks execution. Changed artifact fields require renewed approval unless explicitly covered by a task grant. Successful and unknown results are not resent. Failed or blocked destinations may retry after prerequisites are corrected. No automatic retries are performed inside transports.

An interrupted executing record becomes unknown on the next attempt. Inspect account history, server logs or the actual post. Record a confirmed receipt with record-receipt. Use reconcile --state failed ONLY with evidence that nothing was delivered; this enables retry. Never infer failure from a timeout.

Email acceptance means submitted, not editorial acceptance. accepted/rejected requires a submitted record and evidence. Browser publishing requires the host to carry out the approved workflow and record a receipt; a blocked CLI result is not a post.

## Browser reservation and recovery examples

First run execute --send with approval; a browser destination is blocked and returns its key. Reserve it before opening the form:

```bash
python3 scripts/media_distribution.py --state-dir .distribution-state claim ARTIFACT --key KEY
python3 scripts/media_distribution.py --state-dir .distribution-state record-receipt --key KEY --state published --evidence 'Confirmed post URL'
# Only if external history proves no delivery:
python3 scripts/media_distribution.py --state-dir .distribution-state reconcile --key KEY --state failed --evidence 'Account history checked; no submission'
```

claim persists unknown before any browser interaction and refuses a second claim. Unknown is also accepted by record-receipt. Completed posts cannot be reopened; submitted records only advance to accepted or rejected. Receipts preserve prior evidence.

Grant creation requires --artifact ARTIFACT and binds its exact destination options and locale, not merely an account label. Changing recipients, hosts, credential references or locale requires a new grant. Content revisions remain covered. Credential ownership must be verified by the operator; changing the account behind an environment variable is outside this local consent mechanism.

Example grant: `python3 scripts/media_distribution.py --state-dir .distribution-state grant --content-id studio-launch-001 --channel instagram --account studio-example --artifact ARTIFACT`. Revoke with the same scope and the revoke command, omitting --artifact.
