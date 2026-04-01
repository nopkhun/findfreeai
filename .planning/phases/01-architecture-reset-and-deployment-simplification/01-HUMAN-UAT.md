---
status: partial
phase: 01-architecture-reset-and-deployment-simplification
source: [01-VERIFICATION.md]
started: 2026-04-01T21:05:00+07:00
updated: 2026-04-01T21:05:00+07:00
---

## Current Test

awaiting human testing

## Tests

### 1. Docker health + persistence validation
expected: smlairouter reaches healthy state and named volumes persist data after restart
result: pending

### 2. Coolify deploy smoke on real domain
expected: bash scripts/coolify_verify.sh https://$DOMAIN_PROXY passes all checks in real Coolify/TLS setup
result: pending

### 3. Dashboard live troubleshooting behavior
expected: required panels show real DOWN and ยังไม่ได้ตั้งค่า states and remediation updates correctly
result: pending

### 4. OpenClaw compatibility with valid provider key
expected: /v1/models and /v1/chat/completions (stream + non-stream) succeed with OpenAI-compatible shape
result: pending

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
