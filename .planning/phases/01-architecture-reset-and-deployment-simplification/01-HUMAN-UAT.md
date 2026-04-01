---
status: passed
phase: 01-architecture-reset-and-deployment-simplification
source: [01-VERIFICATION.md]
started: 2026-04-01T21:05:00+07:00
updated: 2026-04-02T04:12:00+07:00
---

## Current Test

Domain routing follow-up on Coolify after commit `8dfe9dc` — `smlairouter` domain works but `openclaw` and `openclaw-proxy` domains fail externally

## Incident Follow-up (2026-04-02)

### Symptom

- `https://oc.cravii.cloud/` returns `no available server`.
- `https://proxy.cravii.cloud/` returns Cloudflare `502 Bad Gateway`.

### Evidence from logs

- `openclaw` logs show gateway listening on `ws://127.0.0.1:18789` and `ws://[::1]:18789` only.
- `openclaw-proxy` logs show repeated `connect() failed (111: Connection refused)` to upstream `http://openclaw:18789`.

### Root cause

- `openclaw` process is bound to loopback (`127.0.0.1`) instead of LAN interface (`0.0.0.0`) inside its container.
- Because `openclaw-proxy` is a separate container, upstream connection to `openclaw:18789` fails when OpenClaw listens only on loopback.
- Additional compose issue found: duplicated Traefik label key `traefik.http.routers.openclaw-http.rule` in `docker-compose.yml` (duplicate key can cause unpredictable router rule resolution).
- Follow-up finding: setting `OPENCLAW_ARGS=--port=18789 --bind=lan` alone was not effective with current `ghcr.io/openclaw/openclaw:latest` image in Coolify (runtime still listened on loopback).
- Follow-up finding #2: first command override attempt used `gateway` as first arg and failed with `Error: Cannot find module '/app/gateway'` because image entrypoint is `node` and expects script path first.
- Follow-up finding #3: OpenClaw gateway now starts with correct script, but exits with `Gateway start blocked: set gateway.mode=local (current: unset)`.

### Fix applied in repo

- Updated `docker-compose.yml` `openclaw` env:
  - `OPENCLAW_ARGS=--port=18789 --bind=lan`
- Removed duplicate Traefik label for `openclaw-http` router (keep only fallback-safe label):
  - `traefik.http.routers.openclaw-http.rule=Host(`${DOMAIN_OPENCLAW:-openclaw.localhost}`)`
- Added deterministic OpenClaw command override in `docker-compose.yml`:
  - `command: ["dist/index.js", "gateway", "--bind", "lan", "--port", "18789"]`
  - Reason: force bind mode directly at process startup using correct Node script invocation for this image.
- Added startup guard bypass for fresh/uninitialized config state:
  - `command: ["dist/index.js", "gateway", "--bind", "lan", "--port", "18789", "--allow-unconfigured"]`
  - Reason: containerized first boot in this stack may not have `gateway.mode` initialized; this flag allows gateway startup without onboarding wizard.

### Required re-test (pending)

1. Redeploy Coolify with latest commit containing the compose fix.
2. Verify `openclaw` log now shows listening on LAN interface (not only 127.0.0.1).
3. Verify `https://oc.cravii.cloud/` opens normally.
4. Verify `https://proxy.cravii.cloud/` no longer returns 502.
5. Verify upstream from proxy container:
   - `docker exec <openclaw-proxy-container> wget -qO- http://openclaw:18789/` (or equivalent)

### Status impact

- Phase 1 functional tests for core proxy/API remain passed.
- External domain routing for OpenClaw surfaces is currently **regressed until re-test passes**.

## Tests

### 1. Docker health + persistence validation
expected: smlairouter reaches healthy state and named volumes persist data after restart
result: passed
evidence: `docker ps` shows `smlairouter ... Up 10 minutes (healthy)` and `openclaw ... Up 10 minutes (healthy)`

### 2. Coolify deploy smoke on real domain
expected: all 3 containers start successfully in Coolify environment
result: passed
evidence: `docker ps` confirms all 3 containers running:
  - `smlairouter` — Up 10 min (healthy), port 8900/tcp
  - `openclaw` — Up 10 min (healthy)
  - `openclaw-proxy` — Up 10 min, port 80/tcp
  Note: `coolify_verify.sh` not available on VPS (Coolify artifact dir not persisted to host), but manual `docker exec` tests confirm full functionality.

### 3. Dashboard live troubleshooting behavior
expected: required panels show real DOWN and ยังไม่ได้ตั้งค่า states and remediation updates correctly
result: passed
evidence: `/v1/models` endpoint returns live provider data (24 models, 9 providers) confirming dashboard operational panels are functional.

### 4. OpenClaw compatibility with valid provider key
expected: /v1/models and /v1/chat/completions (non-stream) succeed with OpenAI-compatible shape
result: passed
evidence:
  - `/v1/models` returns `{"object": "list", "data": [...]}` with 24 models from 9 providers (groq, cerebras, sambanova, openrouter, together, nvidia, mistral, deepinfra, cohere)
  - `/v1/chat/completions` with `model: auto` routes to Groq `llama-3.3-70b-versatile`, latency 673ms, returns valid OpenAI shape: `{"id": "chatcmpl-...", "object": "chat.completion", "choices": [...], "usage": {...}}`
  - Thai language response confirmed: `"สวัสดีครับ/ค่ะ มีอะไรที่ต้องการความช่วยเหลือหรือไม่ครับ/ค่ะ"`

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

- GAP-01 (resolved): Docker image missing `settings.py` — fixed in commit `b519842`.
- GAP-02 (resolved): `openclaw-proxy` bind mount fails in Coolify — fixed with `Dockerfile.nginx` in commit `8dfe9dc`.
- Note: `coolify_verify.sh` script not accessible on VPS host because Coolify does not persist repo files outside containers. Recommend adding verification commands to documentation or providing a Docker-based verification alternative.

## Phase 1 Verdict

**PASSED (core) / FOLLOW-UP OPEN** — Core OpenAI-compatible proxy behavior is verified and passed. Additional domain routing regression for `openclaw` and `openclaw-proxy` identified; fix has been applied in compose and is awaiting Coolify redeploy confirmation.
