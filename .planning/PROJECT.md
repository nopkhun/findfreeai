# SML AI Router - Project Context

## What This Is

SML AI Router is an OpenAI-compatible proxy and operations dashboard for routing requests to free-tier AI providers and serving OpenClaw through a stable internal endpoint. It currently mixes a Python backend, a Python dashboard, and two separate frontend codebases, and it supports local run plus containerized deployment.

## Core Value

Keep OpenClaw continuously usable with free AI providers through automatic provider selection, failover, and a deploy flow that is simple enough to run on local machines and VPS targets (Coolify or Docker).

## Current State

- Runtime services exist for proxy (`proxy.py`), memory/routing (`rag_memory.py`, `skill_engine.py`, `summarizer.py`), and dashboard/scanning (`app.py`).
- Deployment artifacts exist for Docker and Coolify (`Dockerfile`, `docker-compose.yml`, `nginx.conf`), but project layout and startup paths are fragmented.
- There are two web apps (`web/` SvelteKit and `web-next/` Next.js) that create ambiguity around the canonical dashboard/frontend direction.
- Secrets handling guidance exists (`api_keys.json` ignored), but operational hardening and runbook consistency need consolidation.
- Phase 01 complete: architecture contract, centralized config validation, deployment/ops scripts, dashboard operational panels, and verification suite are in place; remaining validation debt is tracked in `01-HUMAN-UAT.md`.

## Constraints

- Must support three operation modes: local run, plain Docker deployment, and Coolify-managed VPS deployment.
- Must remain OpenAI-compatible for OpenClaw integration.
- Must not commit secrets (`.env`, `api_keys.json`, tokens, credentials).
- Thai language should remain the default for UI/log messaging where applicable.

## Success Definition

- New users can deploy and verify the system in one predictable path per target environment (Local, Docker, Coolify) without guesswork.
- Runtime components have clear boundaries, health checks, and startup scripts.
- Dashboard and API configuration flows are coherent and documented.
- Security and operational safeguards are explicit and validated.

## Requirements

### Validated

- Existing proxy endpoints and provider routing are already implemented.
- Existing deployment manifests and dashboard runtime are already present.
- Canonical runtime architecture and service boundaries are documented in `docs/ARCHITECTURE.md` (Validated in Phase 01).
- Centralized env validation and fail-fast Thai diagnostics are implemented through `settings.py` and startup hooks (Validated in Phase 01).
- Local/Docker/Coolify deployment runbooks and unified ops command surface are implemented (`scripts/run_local.py`, `scripts/ops.py`, `docs/DEPLOYMENT.md`) (Validated in Phase 01).
- Dashboard operational visibility panels and Phase 1 verification scripts/smoke tests are implemented (`app.py`, `scripts/verify_phase1.py`, `tests/smoke/`) (Validated in Phase 01).

### Active

- [ ] Decide canonical long-term frontend direction between `web/` and `web-next/` and complete consolidation.
- [ ] Close human UAT verification debt in real Docker/Coolify/OpenClaw runtime environments.

### Out of Scope

- Migrating to paid-only providers as default behavior.
- Replacing OpenClaw itself.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat this as brownfield stabilization + possible partial rewrite | Current code works but has fragmented structure and unclear canonical paths | Locked |
| Prioritize deploy simplicity before feature expansion | Primary user goal is easy deployment and stable usage | Locked |
| Keep multi-mode deployment (Local, Docker, Coolify) as first-class | Explicit user requirement | Locked |

---
*Last updated: 2026-04-01 after Phase 01 completion*
