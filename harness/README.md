# Long-running harness

Externalize progress so agents don't re-litigate finished work.

## When to use

- GCP staging deploy across sessions
- White paper + share pack refresh
- New domain adapter (Regulations.gov, etc.)

## Quick start

```bash
cp harness/templates/features.json ./features.json
cp harness/templates/claude-progress.txt ./claude-progress.txt
chmod +x harness/e2e.sh
```

## Gate policy

**Default verify:** `./harness/e2e.sh`

Agents must not set `"passes": true` without a green e2e run.

## Templates

| File | Role |
|---|---|
| `templates/features.json` | Backlog schema |
| `templates/claude-progress.txt` | Session log stub |
| `templates/e2e.sh` | Wrapper pointing to harness/e2e.sh |
