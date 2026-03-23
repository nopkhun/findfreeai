---
name: findfreeai-ops
description: |
  FindFreeAI project operations — deploy, architecture, API key management, proxy management.
  Use when: deploying to production, managing API keys, debugging proxy/chat issues,
  restarting services, working with DigitalOcean server, or any operational task.
  Triggers: deploy, push, restart, proxy, key, chat, production, server, DO, digitalocean
---

# FindFreeAI Operations

## Architecture

```
Production: https://airouter.satistang.com
Server: 165.232.168.183 (DigitalOcean, ssh root@)
Path: /opt/smlairouter/

Caddy (443/80) → reverse proxy
├── Next.js (port 8899) — Frontend UI (standalone build)
├── app.py (port 8898) — Dashboard backend (Python, runs on host)
└── Docker
    ├── proxy.py (port 8900) — AI Proxy gateway
    └── OpenClaw (port 18790) — Chat client
```

## Deploy Flow (MANDATORY after every git push)

```bash
# 1. Push
git push origin main

# 2. SSH + Pull
ssh root@165.232.168.183 "cd /opt/smlairouter && git pull origin main"

# 3a. If app.py changed → restart dashboard
ssh root@165.232.168.183 "pkill -f 'python.*app.py'; sleep 1; cd /opt/smlairouter && nohup python3 app.py > /var/log/smlairouter-dashboard.log 2>&1 &"

# 3b. If proxy.py changed → rebuild Docker
ssh root@165.232.168.183 "cd /opt/smlairouter && docker compose up -d --build"

# 3c. If web-next/ changed → rebuild + restart Next.js
ssh root@165.232.168.183 "cd /opt/smlairouter/web-next && npm run build && cp -r .next/static .next/standalone/.next/static && cp -r public .next/standalone/public 2>/dev/null; kill \$(pgrep -f 'next-server') 2>/dev/null; sleep 2; PORT=8899 nohup node .next/standalone/server.js > /var/log/smlairouter-next.log 2>&1 &"
```

### Critical: Next.js Standalone Build

After `npm run build`, MUST copy static files:
```bash
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public 2>/dev/null
```
Without this, CSS/JS will 404.

### Critical: Process Management

Always check for duplicate processes before starting:
```bash
# Kill ALL before restart — prevent duplicates
pkill -f 'python.*app.py'     # dashboard
kill $(pgrep -f 'next-server') # Next.js
```

## API Key Management

- Keys stored in `api_keys.json` (gitignored)
- Frontend shows ONLY masked keys (`gsk_********xw`)
- **NO auto-save** — keys save ONLY when test passes
- Flow: user types key → clicks test → backend tests → passes → backend saves
- Backend endpoint: `POST /api/test-one-key` accepts `{env_name, key?}`
- If `key` provided: test that key, save on pass
- If no `key`: test existing key from `api_keys.json`
- Masked values (containing `*`) NEVER overwrite real keys

## Providers (KNOWN_SOURCES in app.py)

| Provider | API Base | env_name |
|----------|----------|----------|
| Groq | api.groq.com/openai/v1 | GROQ_API_KEY |
| Google Gemini | generativelanguage.googleapis.com/v1beta | GOOGLE_API_KEY |
| OpenRouter | openrouter.ai/api/v1 | OPENROUTER_API_KEY |
| Cerebras | api.cerebras.ai/v1 | CEREBRAS_API_KEY |
| SambaNova | api.sambanova.ai/v1 | SAMBANOVA_API_KEY |
| NVIDIA NIM | integrate.api.nvidia.com/v1 | NVIDIA_API_KEY |

## Common Issues

### Chat returns "all providers failed"
1. Check proxy: `curl -s http://127.0.0.1:8900/v1/providers`
2. Test key: `curl -s -X POST http://127.0.0.1:8900/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"auto","messages":[{"role":"user","content":"Hi"}],"max_tokens":5}'`
3. If 401 → keys expired, get new ones
4. If Python error → check proxy.py for bugs, rebuild Docker

### CSS missing on production
Next.js static files not copied. Run:
```bash
cp -r .next/static .next/standalone/.next/static
```

### Duplicate processes
Kill all then restart ONE:
```bash
pkill -f 'python.*app.py'
kill $(pgrep -f 'next-server')
```

## DigitalOcean API
Key: See memory `reference_digitalocean.md`
```bash
curl -s -H "Authorization: Bearer $DO_API_KEY" "https://api.digitalocean.com/v2/droplets"
```

## Files Overview

| File | Port | Role |
|------|------|------|
| `app.py` | 8898 | Dashboard + Scanner + Key tester |
| `proxy.py` | 8900 | AI Proxy (Docker) |
| `web-next/` | 8899 | Next.js frontend (standalone) |
| `api_keys.json` | — | API keys (gitignored!) |
| `docker-compose.yml` | — | Proxy + OpenClaw containers |

## Security Rules
- NEVER commit `api_keys.json`, `.env`, secrets
- Always check: `git diff --cached | grep -iE 'api_key|secret|token|gsk_|AIza|sk-or|csk-'`
- Use Thai in UI and logs
