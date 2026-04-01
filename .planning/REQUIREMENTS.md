# SML AI Router - Requirements

## v1 Requirements

### Architecture & Scope
- [x] **ARCH-01**: Maintainer can identify the canonical runtime architecture (services, entrypoints, data paths) from project docs and repository structure without conflicting guidance.
- [x] **ARCH-02**: System components (proxy, dashboard, memory/routing, frontend) have explicit ownership boundaries and startup contracts.

### Configuration & Security
- [x] **CONF-01**: Operator can configure required environment variables for each deployment mode with mode-specific examples and validation feedback.
- [x] **CONF-02**: Startup fails fast with readable diagnostics when required configuration is missing or invalid.
- [x] **SEC-01**: Project enforces safe secrets handling with no hardcoded credentials and clear excluded secret files.

### Deployment & Operations
- [x] **DEP-01**: Operator can run the system locally via a documented, repeatable command path and verify readiness.
- [x] **DEP-02**: Operator can run the system in Docker Compose with health checks and persistent data paths that survive restarts.
- [x] **DEP-03**: Operator can deploy on Coolify with explicit env/domain configuration and post-deploy verification steps.
- [x] **OPS-01**: Project provides operational scripts or commands for restart, health check, and log inspection across deployment modes.

### Dashboard & UX
- [ ] **DASH-01**: Dashboard presents provider health, key configuration status, and critical warnings in a way that supports quick troubleshooting.
- [ ] **DASH-02**: Dashboard and logs preserve Thai-first messaging policy for operator-facing text.

### API Compatibility & Quality
- [ ] **API-01**: Proxy preserves OpenAI-compatible chat completion behavior for OpenClaw integration (`/v1/chat/completions`, `/v1/models`).
- [ ] **QUAL-01**: Project includes an executable verification checklist (or automated tests) that validates routing, provider fallback, and deployment readiness.

## v2 Requirements (Deferred)

- [ ] **DASH-03**: Unified modern web dashboard replacing legacy UI duplication.
- [ ] **OBS-01**: Long-term metrics backend and alerting integration.

## Out of Scope

- Multi-tenant billing and account management.
- Enterprise IAM/SSO.

## Traceability

| REQ-ID | Planned Phase |
|--------|---------------|
| ARCH-01 | Phase 1 |
| ARCH-02 | Phase 1 |
| CONF-01 | Phase 1 |
| CONF-02 | Phase 1 |
| SEC-01 | Phase 1 |
| DEP-01 | Phase 1 |
| DEP-02 | Phase 1 |
| DEP-03 | Phase 1 |
| OPS-01 | Phase 1 |
| DASH-01 | Phase 1 |
| DASH-02 | Phase 1 |
| API-01 | Phase 1 |
| QUAL-01 | Phase 1 |
