#!/usr/bin/env python3
"""Ops commands: restart, health, logs (local/docker/coolify)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(command: str) -> int:
    return subprocess.run(command, shell=True, cwd=ROOT).returncode


def restart(mode: str) -> int:
    print(f"ℹ️ restart โหมด {mode}")
    if mode == "local":
        return run(f'"{sys.executable}" scripts/run_local.py --restart')
    return run("docker-compose restart")


def health(mode: str, base_url: str | None) -> int:
    print(f"ℹ️ health check โหมด {mode}")
    if mode in {"docker", "coolify"}:
        ps_code = run("docker-compose ps")
        if ps_code != 0:
            print("⚠️ docker daemon ไม่พร้อมใช้งาน - ข้าม compose ps แล้วตรวจ endpoint แทน")
    url = base_url or "http://127.0.0.1:8900"
    code = run(f'"{sys.executable}" scripts/healthcheck.py --base-url "{url}"')
    if code != 0 and mode == "local":
        print("ข้อผิดพลาด: local runtime ยังไม่พร้อม (ให้รัน python scripts/run_local.py ก่อน)")
    return code


def logs(mode: str, lines: int) -> int:
    print(f"ℹ️ logs โหมด {mode} ({lines} lines)")
    if mode == "local":
        log_file = ROOT / ".runtime" / "logs" / "local-runner.log"
        if not log_file.exists():
            print("ข้อผิดพลาด: ยังไม่มีไฟล์ .runtime/logs/local-runner.log")
            return 1
        return run(f'tail -n {lines} "{log_file}"')
    return run(f"docker-compose logs --tail {lines}")


def main() -> int:
    parser = argparse.ArgumentParser(description="รวมคำสั่ง ops สำหรับทุก deployment mode")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_restart = sub.add_parser("restart", help="restart services")
    p_restart.add_argument(
        "--mode", choices=["local", "docker", "coolify"], required=True
    )

    p_health = sub.add_parser("health", help="run health checks")
    p_health.add_argument(
        "--mode", choices=["local", "docker", "coolify"], required=True
    )
    p_health.add_argument("--base-url", default=None)

    p_logs = sub.add_parser("logs", help="view logs")
    p_logs.add_argument("--mode", choices=["local", "docker", "coolify"], required=True)
    p_logs.add_argument("--lines", type=int, default=100)

    args = parser.parse_args()
    if args.cmd == "restart":
        return restart(args.mode)
    if args.cmd == "health":
        return health(args.mode, args.base_url)
    if args.cmd == "logs":
        return logs(args.mode, args.lines)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
