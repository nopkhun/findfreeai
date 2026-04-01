#!/usr/bin/env python3
"""
Local launcher แบบ canonical สำหรับ SML AI Router

คุณสมบัติ:
- ตรวจ preflight ก่อนรันจริง (python/env/path/port)
- รัน proxy + dashboard ผ่าน entrypoint เดียว
- รองรับ restart/stop แบบมี pid file สำหรับ ops.py
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from settings import validate_settings, SettingsValidationError


RUNTIME_DIR = ROOT / ".runtime"
PID_FILE = RUNTIME_DIR / "local-runner.pid"
STATE_FILE = RUNTIME_DIR / "local-runner.json"
LOG_DIR = RUNTIME_DIR / "logs"


def _print_ok(message: str) -> None:
    print(message)


def _print_error(message: str) -> None:
    print(f"ข้อผิดพลาด: {message}")


def _load_dotenv() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _is_port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _ensure_writable(path: Path) -> Tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def run_preflight() -> int:
    _load_dotenv()
    errors: List[str] = []

    _print_ok(f"PRECHECK: python -> {sys.executable}")
    if not Path(sys.executable).exists():
        errors.append("ไม่พบ Python interpreter")

    try:
        os.environ.setdefault("DEPLOY_MODE", "local")
        settings = validate_settings("run_local")
        _print_ok(
            f"PRECHECK: env -> mode={settings.mode}, proxy_port={settings.proxy_port}, dashboard_port={settings.dashboard_port}"
        )
    except SettingsValidationError as exc:
        settings = None
        _print_ok("PRECHECK: env -> failed")
        errors.extend(exc.messages)

    data_dir_ok, data_dir_err = _ensure_writable(ROOT / "data")
    runtime_dir_ok, runtime_dir_err = _ensure_writable(RUNTIME_DIR)
    log_dir_ok, log_dir_err = _ensure_writable(LOG_DIR)
    _print_ok(
        f"PRECHECK: paths -> data={'ok' if data_dir_ok else 'fail'}, runtime={'ok' if runtime_dir_ok else 'fail'}, logs={'ok' if log_dir_ok else 'fail'}"
    )
    if not data_dir_ok:
        errors.append(f"เขียน data/ ไม่ได้: {data_dir_err}")
    if not runtime_dir_ok:
        errors.append(f"เขียน .runtime/ ไม่ได้: {runtime_dir_err}")
    if not log_dir_ok:
        errors.append(f"เขียน .runtime/logs ไม่ได้: {log_dir_err}")

    if settings:
        proxy_free = _is_port_free(settings.proxy_host, settings.proxy_port)
        dashboard_free = _is_port_free(settings.dashboard_host, settings.dashboard_port)
        _print_ok(
            f"PRECHECK: ports -> proxy:{settings.proxy_port}={'free' if proxy_free else 'busy'}, dashboard:{settings.dashboard_port}={'free' if dashboard_free else 'busy'}"
        )
        if not proxy_free:
            errors.append(f"พอร์ต proxy {settings.proxy_port} ถูกใช้งานอยู่")
        if not dashboard_free:
            errors.append(f"พอร์ต dashboard {settings.dashboard_port} ถูกใช้งานอยู่")
    else:
        _print_ok("PRECHECK: ports -> skipped")

    if errors:
        for err in errors:
            _print_error(err)
        return 1

    print("✅ PRECHECK ผ่านทั้งหมด")
    return 0


def _read_state() -> Dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_state(state: Dict) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _cleanup_state() -> None:
    PID_FILE.unlink(missing_ok=True)
    STATE_FILE.unlink(missing_ok=True)


def _process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_runner() -> int:
    state = _read_state()
    pid = state.get("runner_pid")
    if not pid:
        print("ℹ️ ไม่มี local runner ที่กำลังทำงาน")
        _cleanup_state()
        return 0

    if not _process_alive(pid):
        print("ℹ️ local runner เดิมไม่ทำงานแล้ว")
        _cleanup_state()
        return 0

    print(f"🛑 กำลังหยุด local runner (PID={pid})")
    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not _process_alive(pid):
            _cleanup_state()
            print("✅ หยุด local runner แล้ว")
            return 0
        time.sleep(0.2)

    os.kill(pid, signal.SIGKILL)
    _cleanup_state()
    print("⚠️ force kill local runner")
    return 0


def _launch_children() -> List[Tuple[str, subprocess.Popen]]:
    proxy_log = open(LOG_DIR / "proxy-local.log", "a", encoding="utf-8")
    app_log = open(LOG_DIR / "app-local.log", "a", encoding="utf-8")
    children = [
        (
            "proxy",
            subprocess.Popen(
                [sys.executable, str(ROOT / "proxy.py")],
                cwd=str(ROOT),
                stdout=proxy_log,
                stderr=proxy_log,
            ),
        ),
        (
            "dashboard",
            subprocess.Popen(
                [sys.executable, str(ROOT / "app.py")],
                cwd=str(ROOT),
                stdout=app_log,
                stderr=app_log,
            ),
        ),
    ]
    return children


def start_runner() -> int:
    preflight_code = run_preflight()
    if preflight_code != 0:
        return preflight_code

    children = _launch_children()
    state = {
        "runner_pid": os.getpid(),
        "children": {name: proc.pid for name, proc in children},
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _write_state(state)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    print("🚀 เริ่ม local services แล้ว")
    print("📡 Proxy: http://127.0.0.1:8900")
    print("🖥️ Dashboard API: http://127.0.0.1:8898")
    print("📄 Log: .runtime/logs/proxy-local.log, .runtime/logs/app-local.log")
    print("⏹️ กด Ctrl+C เพื่อหยุด")

    def _shutdown(*_args):
        print("\n🛑 กำลังปิด local services...")
        for name, proc in children:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"  ✅ หยุด {name} แล้ว")
            except Exception:
                proc.kill()
                print(f"  ⚠️ force kill {name}")
        _cleanup_state()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    while True:
        for name, proc in children:
            code = proc.poll()
            if code is not None:
                _print_error(f"service {name} หยุดทำงาน (exit={code})")
                _shutdown()
        time.sleep(1)


def start_daemon() -> int:
    if _read_state().get("runner_pid"):
        print("ℹ️ local runner ทำงานอยู่แล้ว")
        return 0
    log_file = open(LOG_DIR / "local-runner.log", "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve())],
        cwd=str(ROOT),
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
    )
    print(f"✅ เริ่ม local runner แบบ background แล้ว (PID={proc.pid})")
    print("📄 ดู log ได้ที่ .runtime/logs/local-runner.log")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical local launcher ของ SML AI Router"
    )
    parser.add_argument(
        "--preflight-only", action="store_true", help="ตรวจ preflight แล้วออก"
    )
    parser.add_argument("--daemon", action="store_true", help="เริ่มแบบ background")
    parser.add_argument("--stop", action="store_true", help="หยุด local runner")
    parser.add_argument("--restart", action="store_true", help="restart local runner")
    args = parser.parse_args()

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if args.preflight_only:
        return run_preflight()
    if args.stop:
        return stop_runner()
    if args.restart:
        stop_runner()
        return start_daemon()
    if args.daemon:
        return start_daemon()
    return start_runner()


if __name__ == "__main__":
    raise SystemExit(main())
