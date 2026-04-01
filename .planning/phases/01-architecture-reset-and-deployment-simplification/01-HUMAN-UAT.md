---
status: partial
phase: 01-architecture-reset-and-deployment-simplification
source: [01-VERIFICATION.md]
started: 2026-04-01T21:05:00+07:00
updated: 2026-04-01T22:40:00+07:00
---

## Current Test

Coolify deployment regression after commit `7d3bc48` (proxy container unhealthy)

## Tests

### 1. Docker health + persistence validation
expected: smlairouter reaches healthy state and named volumes persist data after restart
result: blocked
evidence: Coolify deploy failed before health stabilized because proxy crashed at import stage (`ModuleNotFoundError: No module named 'settings'`)

### 2. Coolify deploy smoke on real domain
expected: bash scripts/coolify_verify.sh https://$DOMAIN_PROXY passes all checks in real Coolify/TLS setup
result: failed
evidence: Coolify `docker compose up -d` exited code 1; dependency failed because `smlairouter` container stayed unhealthy

### 3. Dashboard live troubleshooting behavior
expected: required panels show real DOWN and ยังไม่ได้ตั้งค่า states and remediation updates correctly
result: blocked
evidence: Dashboard chain not testable because upstream `smlairouter` failed to boot in deployment

### 4. OpenClaw compatibility with valid provider key
expected: /v1/models and /v1/chat/completions (stream + non-stream) succeed with OpenAI-compatible shape
result: blocked
evidence: OpenClaw dependency chain blocked by unhealthy `smlairouter` service

## Summary

total: 4
passed: 0
issues: 1
pending: 0
skipped: 0
blocked: 3

## Gaps

- GAP-01 (critical): Docker image missing `settings.py` while `proxy.py` imports `from settings import validate_or_exit`, causing startup crash and unhealthy container.
- Fix applied in repo: updated `Dockerfile` COPY line to include `settings.py`.
- Required re-test:
  1. Redeploy on Coolify with latest commit.
  2. Confirm `smlairouter` healthy.
  3. Re-run `bash scripts/coolify_verify.sh https://$DOMAIN_PROXY`.
  4. Re-run OpenClaw compatibility smoke tests (`/v1/models`, `/v1/chat/completions` stream/non-stream).
