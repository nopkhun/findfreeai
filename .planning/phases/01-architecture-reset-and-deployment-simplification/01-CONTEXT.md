# Phase 1: Architecture Reset and Deployment Simplification - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase covers end-to-end improvement of the existing SML AI Router project to make deployment and operation straightforward across Local, Docker, and Coolify. It includes architecture cleanup, deployment path unification, configuration hardening, dashboard operational UX improvements, and compatibility verification for OpenClaw.

The phase may refactor or replace parts of the current structure if needed, as long as OpenAI-compatible proxy behavior and Thai-first operator communication are preserved.

</domain>

<decisions>
## Implementation Decisions

### Locked decisions
- Keep support for three deployment modes: Local, Docker Compose, Coolify.
- Keep OpenAI-compatible API surface required by OpenClaw (`/v1/chat/completions`, `/v1/models`).
- Keep Thai language as primary for operator-facing UI/log output.
- No secrets committed in repository (`.env`, `api_keys.json`, credentials files).
- Prioritize deploy simplicity and operability over feature expansion.

### the agent's Discretion
- Exact internal module boundaries and file moves.
- Whether to keep one frontend stack or define one as canonical and deprecate the other.
- How much of the dashboard should be refactored now versus deferred.
- Test/checklist implementation approach (automated tests vs scripted validation).

</decisions>

<canonical_refs>
## Canonical References

### Runtime and deploy
- `README.md` - current architecture and deployment narrative
- `docker-compose.yml` - current Docker and Coolify service topology
- `Dockerfile` - proxy container runtime contract
- `nginx.conf` - OpenClaw reverse-proxy behavior

### Core services
- `proxy.py` - OpenAI-compatible gateway behavior and provider routing
- `app.py` - host dashboard/scanner backend
- `dashboard.py` - embedded HTML dashboard server
- `run_all.py` - local multi-process launcher

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` - phase requirements and IDs
- `.planning/ROADMAP.md` - phase goal and success criteria
- `.planning/STATE.md` - project risks and decisions

</canonical_refs>

<specifics>
## Specific Ideas

- Consolidate startup paths to reduce user confusion (single canonical commands per mode).
- Standardize environment validation and clear error messages during startup.
- Add quick health/report endpoints and operational scripts for troubleshooting.
- Ensure dashboard highlights provider health, missing key state, and recommended fixes.

</specifics>

<deferred>
## Deferred Ideas

- Full modern dashboard rewrite and design system rebuild can be deferred if not required for phase success.
- Advanced metrics/alerting backends are deferred to later phase.

</deferred>

---

*Phase: 01-architecture-reset-and-deployment-simplification*
