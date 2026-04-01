# SML AI Router Architecture Contract

Canonical architecture: docs/ARCHITECTURE.md

## Canonical Runtime

SML AI Router has one canonical runtime contract with explicit boundaries:

- **Proxy runtime (`proxy.py`)**: OpenAI-compatible gateway (`/v1/*`) and provider routing.
- **Dashboard runtime (`app.py`)**: Operator dashboard and key/provider operations UI API.
- **Memory/Routing modules (`rag_memory.py`, `skill_engine.py`, `summarizer.py`)**: internal intelligence used by proxy runtime.
- **Frontend runtime**:
  - Canonical operator UI path for this phase: Python dashboard served by `app.py`.
  - `web/` and `web-next/` are **non-canonical/optional** until a later phase selects one frontend direction.

## Service Boundaries

1. **Proxy service**
   - Ownership: API compatibility and provider failover behavior.
   - Entrypoint: `proxy.py` (container-first, can run local for testing).
   - Ports: `8900`.
   - Inputs: env vars, optional keys file (`KEYS_FILE`).
   - Outputs: `/v1/chat/completions`, `/v1/models`, operational endpoints.

2. **Dashboard service**
   - Ownership: operator actions (scan/test keys, status, controls).
   - Entrypoint: `app.py` (host runtime).
   - Ports: `8899` (local dashboard).
   - Inputs: env vars + key storage.
   - Outputs: web UI and operational API endpoints.

3. **OpenClaw service (Docker mode/Coolify mode)**
   - Ownership: AI agent client.
   - Entrypoint: container image `ghcr.io/openclaw/openclaw:latest`.
   - Upstream dependency: `http://smlairouter:8900/v1`.

4. **Reverse proxy service (Coolify mode)**
   - Ownership: domain/TLS ingress for OpenClaw and proxy.
   - Entrypoint: Traefik labels and nginx container (`openclaw-proxy`).

## Data Paths

- Proxy persistent data: Docker volume `smlairouter-data` mounted at `/app/data`.
- Keys persistence in containerized runtime: `KEYS_FILE=/app/data/api_keys.json`.
- OpenClaw persistent data: Docker volume `openclaw-data` mounted at `/home/node/.openclaw`.
- Local mode data and logs: project root runtime files (`api_keys.json`, logs) managed by host process.

## Local Mode

Canonical startup sequence:

1. Copy env template: `cp .env.example .env`.
2. Set at least one provider key.
3. Start proxy container: `docker compose up -d smlairouter`.
4. Start dashboard on host: `python app.py`.
5. Verify:
   - Proxy: `http://127.0.0.1:8900/v1/models`
   - Dashboard: `http://127.0.0.1:8899`

Startup contract:

- Proxy and dashboard must pass centralized settings validation before binding network ports.
- Missing/invalid required config must fail fast with Thai-readable diagnostics.

## Docker Mode

Canonical startup sequence:

1. Configure env (`.env` or platform env vars).
2. Start services: `docker compose up -d`.
3. Wait for `smlairouter` health check to become healthy.
4. Verify proxy endpoint and provider list.

Startup contract:

- `smlairouter` health check is mandatory readiness signal.
- OpenClaw depends on healthy proxy service.

## Coolify Mode

Canonical startup sequence:

1. Import repo as Docker Compose resource.
2. Set domains: `DOMAIN_OPENCLAW`, `DOMAIN_PROXY`.
3. Set provider env keys (at least one valid key).
4. Deploy via Coolify.
5. Verify public endpoints:
   - `https://{DOMAIN_PROXY}/v1/models`
   - `https://{DOMAIN_OPENCLAW}`

Startup contract:

- Traefik labels route traffic to `smlairouter` and `openclaw-proxy`.
- Service-to-service API path remains internal Docker network (`smlairouter:8900`).

## Legacy / Optional Paths

- `run_all.py`, `find_free_ai.py`, `test_ai_apis.py`, and `dashboard.py` represent older workflow utilities and are **not canonical runtime startup paths** for this phase.
- `web/` and `web-next/` remain optional/non-canonical until frontend direction is finalized.
