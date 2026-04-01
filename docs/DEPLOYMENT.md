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
