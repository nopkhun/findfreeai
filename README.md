# 🦞 SML AI Router — Free AI Gateway + Smart Routing

OpenAI-compatible AI proxy ที่ route requests ไปหลาย free providers อัตโนมัติ
สร้างมาเพื่อให้ OpenClaw และแอปอื่นๆ ใช้ AI ฟรีตลอดไป

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-Provider Failover** | 9 providers (Groq, Cerebras, SambaNova, OpenRouter, ...) สลับอัตโนมัติ |
| **Smart Routing** | เรียนรู้ว่า query แบบไหนเหมาะกับ provider ไหน (code→Groq, chat→OpenRouter) |
| **Vector RAG Memory** | จำบทสนทนาด้วย ChromaDB + Google Gemini Embedding |
| **SSE Streaming** | Stream response ทีละคำ (OpenAI-compatible) |
| **Vision Routing** | ตรวจจับรูปภาพ → route ไป vision model อัตโนมัติ |
| **Tool Calling** | Forward tools ไป provider ที่รองรับ (Groq, OpenRouter) |
| **Cost Tracking** | Track token usage + hypothetical cost per request |
| **Virtual API Keys** | แจก key ย่อยให้ user กำหนด quota + rate limit |
| **System Prompt** | Inject persona ให้ AI ทุก request (แก้ไขได้จาก Dashboard) |
| **Auto-Disable** | ตัด provider ที่ช้า/fail เยอะออกอัตโนมัติ |
| **OpenClaw Integration** | ใช้เป็น LLM provider สำหรับ OpenClaw ได้เลย |

## 🏗️ Architecture

ดูรายละเอียดเต็ม: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

```
┌─ Docker / Coolify VPS ─────────────────────────────────┐
│                                                         │
│  smlairouter (:8900)     — AI Gateway Proxy            │
│  ├── proxy.py            — OpenAI-compatible API       │
│  ├── rag_memory.py       — ChromaDB vector search      │
│  ├── skill_engine.py     — Learn + smart routing       │
│  ├── cost_tracker.py     — Token/cost tracking         │
│  └── virtual_keys.py     — API key management          │
│            ↑ http://smlairouter:8900/v1                 │
│  openclaw (:18789)       — OpenClaw AI Agent           │
│            ↑ nginx proxy                                │
│  openclaw-proxy (:80)    — Nginx → Traefik → Internet  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 วิธีใช้งาน

### 1) Local (เครื่องตัวเอง)

```bash
# เตรียมค่า config
cp .env.example .env
# แก้ .env ใส่ API key อย่างน้อย 1 ตัว (เช่น GROQ_API_KEY)

# ตรวจสอบ preflight
python3 scripts/run_local.py --preflight-only

# เริ่มระบบทั้งหมด (proxy + dashboard)
python3 scripts/run_local.py
```

เปิดใช้งาน:
- Proxy API: `http://127.0.0.1:8900/v1/models`
- Dashboard: `http://127.0.0.1:8899`

### 2) Docker Compose

```bash
# ตั้งค่า env
cp .env.example .env
# แก้ .env ใส่ API keys และ domain (ถ้ามี)

# เริ่มระบบ
docker compose up -d

# ตรวจสอบสถานะ
docker compose ps
```

ทดสอบ:
```bash
curl -s http://127.0.0.1:8900/v1/models
```

### 3) Coolify VPS

ดูรายละเอียดเพิ่มเติม: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

1. Coolify UI → **New Resource** → **Docker Compose** → เลือก repo นี้
2. ตั้งค่า **Environment Variables**:

```env
# Domains
DOMAIN_OPENCLAW=openclaw.yourdomain.com
DOMAIN_PROXY=proxy.yourdomain.com

# API Keys (ใส่อย่างน้อย 1 ตัว)
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...
```

3. คลิก **Deploy**
4. ตรวจสอบ:

```bash
bash scripts/coolify_verify.sh https://proxy.yourdomain.com
```

> สมัคร API Key ฟรีได้จาก [Providers](#-providers-free-tier) ด้านล่าง

---

## 🦞 ใช้งาน OpenClaw บน VPS

OpenClaw จะ **connect ไป smlairouter อัตโนมัติ** ผ่าน env vars ใน docker-compose

เข้าใช้งาน OpenClaw ที่: `https://openclaw.yourdomain.com`

### ตั้ง LLM Provider ใน OpenClaw UI

ไปที่ **Settings → LLM Provider → Custom/OpenAI Compatible** แล้วใส่:

| Field | ค่า |
|-------|-----|
| API Base URL | `https://proxy.yourdomain.com/v1` |
| API Key | `any` |
| Model | `auto` |

---

## 🔌 ใช้กับแอปอื่น

```env
OPENAI_API_BASE=http://127.0.0.1:8900/v1   # local
# หรือ
OPENAI_API_BASE=https://proxy.yourdomain.com/v1   # VPS

OPENAI_API_KEY=any
MODEL_NAME=auto
```

### Model Format

```
auto                              → ให้ smlairouter เลือก provider อัตโนมัติ
groq/llama-3.3-70b-versatile     → เจาะจง provider + model
llama-3.3-70b-versatile          → หา provider ที่มี model นี้
openrouter/nvidia/nemotron-3-super-120b-a12b:free  → OpenRouter free model
```

---

## 🔧 คำสั่งดูแลระบบ (Ops)

```bash
# ดูสถานะ
python3 scripts/ops.py health --mode local
python3 scripts/ops.py health --mode docker

# รีสตาร์ท
python3 scripts/ops.py restart --mode local
python3 scripts/ops.py restart --mode docker

# ดู log
python3 scripts/ops.py logs --mode local --lines 50
python3 scripts/ops.py logs --mode docker --lines 50
```

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/chat/completions` | Chat (OpenAI-compatible) |
| GET | `/v1/models` | List available models |
| GET | `/v1/providers` | Provider status + stats |
| GET | `/v1/stats` | Detailed statistics |
| GET | `/v1/config` | Current config |
| POST | `/v1/config` | Update config (system prompt, mode) |
| POST | `/v1/keys` | Update API keys |
| GET | `/v1/costs` | Cost tracking summary |
| GET | `/v1/virtual-keys` | Virtual API keys |
| POST | `/v1/virtual-keys` | Create/delete/toggle keys |
| GET | `/v1/logs` | Request logs (last 100) |
| GET | `/v1/reload` | Reload providers + reset stats |

### OpenAI Compatibility Examples

#### List models

```bash
curl -s http://127.0.0.1:8900/v1/models
```

#### Chat (non-stream)

```bash
curl -s -X POST http://127.0.0.1:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"สวัสดี"}]}'
```

#### Chat (stream)

```bash
curl -N -s -X POST http://127.0.0.1:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","stream":true,"messages":[{"role":"user","content":"สวัสดี"}]}'
```

---

## ✅ ตรวจสอบระบบ (Verification)

```bash
# รัน verification ทั้งหมด (release gate)
python3 scripts/verify_phase1.py --mode local

# รัน smoke tests
python3 -m pytest tests/smoke/ -q

# ตรวจความปลอดภัยก่อน commit
python3 scripts/secret_guard.py --staged
```

---

## 🤖 Providers (Free Tier)

| Provider | Priority | Models | Free Tier | Sign Up |
|----------|----------|--------|-----------|---------|
| Groq | 100 | Llama 3.3 70B, Mixtral | 30 RPM / 14,400/day | [console.groq.com](https://console.groq.com/keys) |
| Cerebras | 95 | Llama 3.1 70B | 30 RPM | [cloud.cerebras.ai](https://cloud.cerebras.ai/) |
| SambaNova | 90 | Llama 3.1 | Unlimited (rate limited) | [cloud.sambanova.ai](https://cloud.sambanova.ai/apis) |
| OpenRouter | 85 | Free models (:free) | Free models available | [openrouter.ai](https://openrouter.ai/settings/keys) |
| Together AI | 80 | Llama 3 70B | $5 free credit | [api.together.ai](https://api.together.ai/settings/api-keys) |
| NVIDIA NIM | 75 | Llama models | 1,000 free requests | [build.nvidia.com](https://build.nvidia.com/explore/discover) |
| Mistral | 70 | Mistral Small | Free for experiments | [console.mistral.ai](https://console.mistral.ai/api-keys/) |
| DeepInfra | 65 | Llama 3 8B | Free rate-limited | [deepinfra.com](https://deepinfra.com/dash/api_keys) |
| Cohere | 60 | Command R | Trial 5 RPM | [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) |

---

## 🧠 Smart Features

**Vector RAG Memory** — ทุกข้อความถูก embed ด้วย Google Gemini Embedding, ค้นหาด้วย semantic similarity (ChromaDB), จำชื่อ อาชีพ บริบทข้ามข้อความได้

**Skill Engine** — เรียนรู้จากทุก request ว่า provider ไหนเร็ว/ดีสำหรับ query แบบไหน, auto-reorder providers ตาม learned performance, ตัด provider fail >80% หรือ avg >8s ออกอัตโนมัติ

**Vision Routing** — ตรวจจับ `image_url` ใน messages แล้ว route ไป OpenRouter vision model (Qwen VL) อัตโนมัติ

---

## 🛡️ Security

- API keys เก็บใน `api_keys.json` (git-ignored) หรือ env vars
- Virtual keys ใช้ SHA256 hash
- OpenClaw gateway ป้องกันด้วย auth token
- ไม่ hardcode secrets ในโค้ด
- ห้าม commit `.env`, `api_keys.json`, `credentials*`, `*.secret`
- ตรวจก่อน commit: `python3 scripts/secret_guard.py --staged`

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, http.server |
| Vector DB | ChromaDB |
| Embeddings | Google Gemini + SambaNova |
| Container | Docker + Docker Compose |
| Reverse Proxy | Nginx + Traefik (Coolify) |
| AI Providers | 9+ free-tier APIs |

## 📝 License

MIT
