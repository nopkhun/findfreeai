# Phase 1 Research: Architecture Reset and Deployment Simplification

## Objective

Identify the minimum-change and high-leverage technical approach to make this brownfield router deployable and maintainable across Local, Docker, and Coolify without breaking OpenClaw compatibility.

## Current-State Findings

1. **Runtime split is unclear**
   - `proxy.py` is container-first runtime.
   - `app.py` and `dashboard.py` overlap in dashboard intent.
   - `run_all.py` uses legacy finder/tester flow that does not reflect current proxy-centered deploy story.

2. **Deployment story is strong but fragmented**
   - `docker-compose.yml` already contains good health checks and Coolify labels.
   - README instructions are broad, but startup contracts are not normalized into explicit mode-specific runbooks.

3. **Frontend direction is ambiguous**
   - Both `web/` (SvelteKit) and `web-next/` (Next.js) exist.
   - No clear canonical frontend for operations dashboard, increasing maintenance load.

4. **Security baseline exists but should be systematized**
   - Secret files are already expected to stay out of git.
   - Needs enforceable checks in scripts/docs and startup diagnostics.

## Recommended Technical Strategy

### A. Define canonical runtime contract first
- Make proxy service (`proxy.py`) the core runtime authority.
- Explicitly define whether dashboard is:
  1) embedded in Python runtime, or
  2) separate web app consuming proxy endpoints.
- Keep one default path and mark alternatives as optional/legacy.

### B. Standardize deployment entrypoints
- Provide one command set per mode:
  - Local: single launcher with preflight checks
  - Docker: `docker compose up` with health-check verification command
  - Coolify: env/domain checklist + post-deploy smoke test commands
- Add preflight validation for required env keys and writable data paths.

### C. Preserve compatibility while refactoring
- Lock behavior for `/v1/chat/completions` and `/v1/models`.
- Add smoke tests that run against local proxy and container proxy.

### D. Upgrade operator experience with targeted dashboard improvements
- Show provider health summary, key availability status (masked), and actionable warnings.
- Keep Thai-first language for operator-facing text.
- Do not overinvest in full UI rewrite in this phase unless blockers appear.

## Risk Mitigation

- **Risk:** refactor breaks OpenClaw
  - **Mitigation:** compatibility smoke tests and staged migration
- **Risk:** duplicated frontend effort
  - **Mitigation:** choose canonical dashboard path and explicitly deprecate/park non-canonical path
- **Risk:** deploy docs diverge from actual scripts
  - **Mitigation:** generate docs from executable scripts/checklists where possible

## Validation Architecture

Validation must prove three dimensions:

1. **API compatibility:** OpenAI-compatible endpoints return expected schema/status.
2. **Deployment readiness:** Local, Docker, Coolify runbooks are executable and complete.
3. **Operational visibility:** Dashboard and logs expose provider and configuration health state for troubleshooting.

## Output Guidance for Planning

Plans should be split into waves:
- Wave 1: architecture and runtime contract cleanup
- Wave 2: deploy/runbook/script unification
- Wave 3: dashboard and observability UX improvements
- Wave 4: verification suite and release readiness

Each plan should map explicit REQ-IDs and produce verifiable acceptance criteria.
