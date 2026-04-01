# Deployment Runbook

คู่มือ deploy/operate แบบ canonical สำหรับ SML AI Router

## Local

ใช้คำสั่งเดียวต่อไปนี้เป็น local entrypoint:

```bash
python scripts/run_local.py
```

ตรวจ preflight อย่างเดียว:

```bash
python scripts/run_local.py --preflight-only
```

Expected healthy output:
- `PRECHECK: python`
- `PRECHECK: env`
- `PRECHECK: ports`
- `✅ PRECHECK ผ่านทั้งหมด`

## Docker

รันแบบ Docker Compose พร้อม health check และ persistent volumes:

```bash
docker compose up -d
docker compose ps
```

สิ่งที่ต้องเห็น:
- service `smlairouter` เป็น `healthy`
- volume `smlairouter-data`, `smlairouter-logs`, `openclaw-data` ถูกสร้างและคงอยู่หลัง restart

ทดสอบว่า restart แล้วข้อมูลยังอยู่:

```bash
docker compose restart smlairouter
docker compose ps
```

## Coolify

### Prerequisites (ต้องตั้งค่าก่อน Deploy)

1. Domain
   - `DOMAIN_OPENCLAW` = โดเมน OpenClaw
   - `DOMAIN_PROXY` = โดเมน proxy
2. API key อย่างน้อย 1 ตัว (เช่น `GROQ_API_KEY` หรือ `OPENROUTER_API_KEY`)
3. Coolify external network `coolify` พร้อมใช้งาน

Deploy ด้วย Docker Compose resource แล้วตรวจ smoke test:

```bash
bash scripts/coolify_verify.sh https://$DOMAIN_PROXY
```

Expected healthy output:
- `CHECK / -> HTTP 200`
- `CHECK /v1/models -> HTTP 200`
- `CHECK /v1/chat/completions -> HTTP ...` (ยอมรับ 200/401/403/422/502/503)

## Ops Commands

```bash
python scripts/ops.py restart --mode local
python scripts/ops.py health --mode docker
python scripts/ops.py logs --mode docker --lines 50
```
