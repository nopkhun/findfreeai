#!/usr/bin/env python3
"""Endpoint-level health checks for proxy contract."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def fail(msg: str) -> None:
    print(f"ข้อผิดพลาด: {msg}")


def request(url: str, method: str = "GET", body: dict | None = None) -> tuple[int, str]:
    payload = None
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "smlairouter-healthcheck",
    }
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return exc.code, text
    except urllib.error.URLError as exc:
        return 0, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ตรวจ endpoint / /v1/models /v1/chat/completions"
    )
    parser.add_argument(
        "--base-url", default="http://127.0.0.1:8900", help="Proxy base URL"
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    checks = [
        ("/", "GET", None, {200}),
        ("/v1/models", "GET", None, {200}),
        (
            "/v1/chat/completions",
            "POST",
            {
                "model": "auto",
                "messages": [{"role": "user", "content": "ตอบว่า ok"}],
                "max_tokens": 5,
            },
            {200, 401, 403, 422, 502, 503},
        ),
    ]

    bad = False
    for path, method, body, accepted in checks:
        status, resp = request(f"{base}{path}", method=method, body=body)
        if status in accepted:
            ok(f"HEALTHCHECK {path}: HTTP {status}")
        else:
            bad = True
            fail(
                f"HEALTHCHECK {path}: HTTP {status}, response={resp[:180].replace(chr(10), ' ')}"
            )

    if bad:
        return 1
    ok("HEALTHCHECK ผ่าน endpoint contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
