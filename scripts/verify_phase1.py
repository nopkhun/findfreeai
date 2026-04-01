#!/usr/bin/env python3
"""
Phase 1 verification script

รันเช็กลิสต์การพร้อมปล่อยของ Phase 1:
- string audit (Thai-first operator text)
- OpenAI compatibility (/v1/models, /v1/chat/completions)
- fallback/readiness checks

Exit code:
- 0 = ผ่านทั้งหมด
- 1 = มีข้อใดข้อหนึ่งไม่ผ่าน
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROXY_BASE = "http://127.0.0.1:8900"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fetch_json(url: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body, json.loads(body)


def fetch_text(url: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def assert_true(
    name: str, cond: bool, detail: str, results: list[tuple[str, bool, str]]
):
    results.append((name, cond, detail))


def run_string_audit(results: list[tuple[str, bool, str]]):
    files = [ROOT / "app.py", ROOT / "dashboard.py", ROOT / "proxy.py"]
    english_operator_tokens = [
        "Loading...",
        "Waiting for data...",
        "Updated:",
        "✅ Alive",
        "❌ Down",
        "not found",
        "Invalid JSON",
        "unknown action",
        "Toggle Dark/Light",
    ]

    found = []
    string_literal_re = re.compile(r"(['\"])(?:(?=(\\?))\2.)*?\1")
    for path in files:
        txt = read_text(path)
        literals = [m.group(0) for m in string_literal_re.finditer(txt)]
        for token in english_operator_tokens:
            for lit in literals:
                if token in lit:
                    found.append((path.name, token))
                    break

    assert_true(
        "DASH-02 Thai-first string audit",
        len(found) == 0,
        "zero English-only operator labels" if not found else f"found={found}",
        results,
    )


def run_models_compat(results: list[tuple[str, bool, str]]):
    try:
        status, _, data = fetch_json(f"{PROXY_BASE}/v1/models")
        ok = status == 200 and isinstance(data.get("data"), list)
        assert_true(
            "API-01 /v1/models shape",
            ok,
            "top-level key data is array" if ok else f"status={status} body={data}",
            results,
        )
    except Exception as exc:
        assert_true("API-01 /v1/models shape", False, f"error={exc}", results)


def run_chat_nonstream(results: list[tuple[str, bool, str]]):
    payload = {"model": "auto", "messages": [{"role": "user", "content": "ทดสอบ"}]}
    try:
        status, _, data = fetch_json(
            f"{PROXY_BASE}/v1/chat/completions", method="POST", payload=payload
        )
        required = ["id", "object", "choices", "model"]
        ok = status == 200 and all(k in data for k in required)
        assert_true(
            "API-01 /v1/chat/completions non-stream shape",
            ok,
            "contains id/object/choices/model"
            if ok
            else f"status={status} body={data}",
            results,
        )
    except Exception as exc:
        assert_true(
            "API-01 /v1/chat/completions non-stream shape",
            False,
            f"error={exc}",
            results,
        )


def run_chat_stream(results: list[tuple[str, bool, str]]):
    payload = {
        "model": "auto",
        "stream": True,
        "messages": [{"role": "user", "content": "ทดสอบสตรีม"}],
    }
    try:
        status, text = fetch_text(
            f"{PROXY_BASE}/v1/chat/completions", method="POST", payload=payload
        )
        has_data_event = bool(re.search(r"^data:\s", text, flags=re.MULTILINE))
        has_done = "data: [DONE]" in text
        ok = status == 200 and has_data_event and has_done
        assert_true(
            "API-01 /v1/chat/completions stream format",
            ok,
            "emits data: events and [DONE]" if ok else "missing data events or DONE",
            results,
        )
    except Exception as exc:
        assert_true(
            "API-01 /v1/chat/completions stream format", False, f"error={exc}", results
        )


def run_fallback_readiness(results: list[tuple[str, bool, str]]):
    try:
        _, _, providers = fetch_json(f"{PROXY_BASE}/v1/providers")
        items = providers.get("providers", []) if isinstance(providers, dict) else []
        has_any_key = any(bool(p.get("has_key")) for p in items)
        assert_true(
            "QUAL-01 provider readiness",
            has_any_key,
            "at least one provider has key" if has_any_key else "no providers with key",
            results,
        )
    except Exception as exc:
        assert_true("QUAL-01 provider readiness", False, f"error={exc}", results)


def run_mode_local(results: list[tuple[str, bool, str]]):
    run_models_compat(results)
    run_chat_nonstream(results)
    run_chat_stream(results)
    run_fallback_readiness(results)


def print_summary(results: list[tuple[str, bool, str]]):
    print("\n=== Phase 1 Verification Summary ===")
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name} :: {detail}")
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\nResult: {passed}/{total} passed")
    return passed == total


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["local"], default="local")
    parser.add_argument("--string-audit-only", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    results: list[tuple[str, bool, str]] = []

    run_string_audit(results)
    if not args.string_audit_only:
        run_mode_local(results)

    ok = print_summary(results)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
