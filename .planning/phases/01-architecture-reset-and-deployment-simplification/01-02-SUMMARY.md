---
phase: 01-architecture-reset-and-deployment-simplification
plan: 02
subsystem: infra
tags: [deployment, docker, coolify, ops, healthcheck, runbook]
requires:
  - phase: 01-01
    provides: centralized settings validation contract and security guardrails
provides:
  - canonical local launcher with deterministic preflight checks
  - docker and coolify deployment runbooks with smoke verification steps
  - unified restart/health/logs operator command surface
affects: [deployment, operations, onboarding]
tech-stack:
  added: [python operational scripts, shell smoke verification]
  patterns: [single local entrypoint, endpoint-contract health checks, documented ops command family]
key-files:
  created:
    - scripts/run_local.py
    - scripts/ops.py
    - scripts/healthcheck.py
    - scripts/coolify_verify.sh
    - docs/DEPLOYMENT.md
  modified:
    - docker-compose.yml
    - README.md
key-decisions:
  - "ใช้ scripts/run_local.py เป็น canonical local entrypoint พร้อม preflight เดียวกันทุกเครื่อง"
  - "ใช้ endpoint contract (/ /v1/models /v1/chat/completions dry smoke) เป็นมาตรฐาน health verification ทุกโหมด"
patterns-established:
  - "Pattern: เอกสาร deploy ต้องชี้ไป script ที่รันได้จริง ไม่ใช้คำสั่ง ad-hoc"
  - "Pattern: งาน ops ใช้คำสั่ง family เดียวผ่าน scripts/ops.py"
requirements-completed: [DEP-01, DEP-02, DEP-03, OPS-01]
duration: 7 min
completed: 2026-04-01
---

# Phase 1 Plan 2: Deployment Script and Runbook Unification Summary

**ส่งมอบเส้นทาง deploy/operate ที่ชัดเจนด้วย local launcher + preflight, Docker/Coolify smoke runbook, และ ops command family เดียว**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-01T13:27:05Z
- **Completed:** 2026-04-01T13:34:37Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- เพิ่ม `scripts/run_local.py` ให้เป็นจุดเริ่ม local แบบ canonical พร้อม preflight (`PRECHECK: python/env/ports`) และ Thai error diagnostics
- ปรับสัญญา deploy สำหรับ Docker/Coolify ให้มี health check ชัดเจน พร้อม smoke script `scripts/coolify_verify.sh`
- เพิ่มคำสั่งปฏิบัติการแบบรวมศูนย์ `scripts/ops.py` + `scripts/healthcheck.py` สำหรับ restart/health/logs ข้ามโหมด

## Task Commits

Each task was committed atomically:

1. **Task 1: Create canonical local run path with preflight checks** - `64ef29a` (feat)
2. **Task 2: Standardize Docker and Coolify deployment contracts** - `6fab188` (feat)
3. **Task 3: Provide unified operations command surface** - `a2355e7` (feat)

## Files Created/Modified
- `scripts/run_local.py` - canonical local launcher, preflight checks, pid/state lifecycle
- `docker-compose.yml` - health check target `/v1/models`, persistent logs volume, stable domain defaults
- `scripts/coolify_verify.sh` - domain smoke checks for Coolify deployment
- `scripts/healthcheck.py` - endpoint-level contract checks
- `scripts/ops.py` - unified restart/health/logs commands
- `docs/DEPLOYMENT.md` - local/docker/coolify runbooks and ops examples
- `README.md` - canonical local command path and ops command examples

## Decisions Made
- ยึด `scripts/run_local.py` เป็น local command เดียวเพื่อกำจัดความกำกวมจาก launcher เดิม
- ใช้ health contract ชุดเดียวกันทั้ง local/docker/coolify เพื่อลดช่องว่างระหว่างเอกสารกับ runtime จริง

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] แก้ command/runtime mismatch ในสภาพแวดล้อม executor**
- **Found during:** Task 1-3 verification
- **Issue:** คำสั่ง `python` และ `docker compose` ใช้ไม่ได้ตรงในเครื่อง executor (ต้องใช้ `python3` และ `docker-compose`)
- **Fix:** ปรับ script/document verification ให้รองรับ runtime ที่มีจริง, เพิ่ม fallback behavior ใน ops health
- **Files modified:** scripts/ops.py
- **Verification:** `python3 scripts/ops.py --help`, `python3 scripts/ops.py health --mode local`, `python3 scripts/ops.py health --mode docker`
- **Committed in:** a2355e7

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** ปรับเพื่อให้ execution ทำได้จริงใน environment ปัจจุบัน โดยไม่เปลี่ยนเป้าหมายสถาปัตยกรรมของแผน

## Authentication Gates
None.

## Issues Encountered
- Docker daemon ไม่พร้อมใน executor จึงไม่สามารถยืนยัน `docker compose up -d` และการ healthy transition ของ container จริงในเครื่องนี้ได้
- Coolify smoke against placeholder domain (`https://proxy.localhost`) ล้มเหลวตามคาด เพราะไม่มี endpoint จริงใน environment นี้

## User Setup Required
None - no external service configuration required beyond existing deployment env values.

## Next Phase Readiness
- พร้อมต่อ `01-03` สำหรับ dashboard/observability improvements และ verification hardening
- มี runbook/script ครบทั้ง Local, Docker, Coolify ให้ operator ใช้เส้นทางเดียวกันได้

---
*Phase: 01-architecture-reset-and-deployment-simplification*
*Completed: 2026-04-01*

## Self-Check: PASSED
