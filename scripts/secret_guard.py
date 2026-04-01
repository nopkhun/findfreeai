#!/usr/bin/env python3
"""ตรวจ secret จาก staged diff ก่อน commit"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys


SECRET_PATTERNS = [
    (
        "Generic API key",
        re.compile(
            r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"
        ),
    ),
    ("Groq key", re.compile(r"gsk_[A-Za-z0-9]{16,}")),
    ("Google key", re.compile(r"AIza[0-9A-Za-z\-_]{20,}")),
    ("OpenRouter key", re.compile(r"sk-or-[A-Za-z0-9\-_]{16,}")),
    ("Cerebras key", re.compile(r"csk-[A-Za-z0-9\-_]{16,}")),
    ("NVIDIA key", re.compile(r"nvapi-[A-Za-z0-9\-_]{16,}")),
]


def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--no-color"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print("❌ อ่าน staged diff ไม่ได้", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(2)
    return result.stdout


def scan_diff(diff: str) -> list[str]:
    findings: list[str] = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(f"{label}: {line[:200]}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Secret guard for staged changes")
    parser.add_argument("--staged", action="store_true", help="scan staged changes")
    args = parser.parse_args()

    if not args.staged:
        print("ℹ️ ใช้งานด้วย --staged เท่านั้น")
        return 0

    diff = get_staged_diff()
    findings = scan_diff(diff)

    if findings:
        print("❌ พบความเสี่ยง secret ใน staged diff:")
        for idx, finding in enumerate(findings, start=1):
            print(f"  {idx}. {finding}")
        print("\nโปรดลบ secret ออกจาก commit แล้วลองใหม่")
        return 1

    print("✅ ไม่พบ secret ชัดเจนใน staged diff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
