---
status: partial
phase: 01-architecture-reset-and-deployment-simplification
source: [01-VERIFICATION.md]
started: 2026-04-01T21:05:00+07:00
updated: 2026-04-01T23:10:00+07:00
---

## Current Test

Coolify deployment retest after commit `b519842` (proxy fixed, nginx sidecar mount failure)

## Tests

### 1. Docker health + persistence validation
expected: smlairouter reaches healthy state and named volumes persist data after restart
result: passed
evidence: deployment log shows `smlairouter ... Healthy` after startup

### 2. Coolify deploy smoke on real domain
expected: bash scripts/coolify_verify.sh https://$DOMAIN_PROXY passes all checks in real Coolify/TLS setup
result: failed
evidence: `docker compose up -d` exited code 1 due to `openclaw-proxy` mount error: `error mounting ... nginx.conf ... not a directory`

### 3. Dashboard live troubleshooting behavior
expected: required panels show real DOWN and ยังไม่ได้ตั้งค่า states and remediation updates correctly
result: blocked
evidence: stack deployment halted at `openclaw-proxy` start failure, preventing full end-to-end dashboard validation

### 4. OpenClaw compatibility with valid provider key
expected: /v1/models and /v1/chat/completions (stream + non-stream) succeed with OpenAI-compatible shape
result: blocked
evidence: deployment chain interrupted by `openclaw-proxy` container init failure (bind mount type mismatch)

## Summary

total: 4
passed: 1
issues: 2
pending: 0
skipped: 0
blocked: 2

## Gaps

- GAP-01 (resolved): Docker image missing `settings.py` while `proxy.py` imports `from settings import validate_or_exit`, causing startup crash and unhealthy container.
- Resolution evidence: retest shows `smlairouter` starts and reaches `Healthy`.
- GAP-02 (critical): `openclaw-proxy` fails to start in Coolify because bind mount `./nginx.conf:/etc/nginx/nginx.conf:ro` resolves to wrong host path type in artifact workspace (`not a directory`).
- Fix applied in repo: remove bind mount dependency by building dedicated nginx image from `Dockerfile.nginx` that embeds `nginx.conf`.
- Required re-test:
  1. Redeploy on Coolify with latest commit (includes `Dockerfile.nginx` + compose change).
  2. Confirm `openclaw-proxy` container starts successfully.
  3. Re-run `bash scripts/coolify_verify.sh https://$DOMAIN_PROXY`.
  4. Re-run OpenClaw compatibility smoke tests (`/v1/models`, `/v1/chat/completions` stream/non-stream).
