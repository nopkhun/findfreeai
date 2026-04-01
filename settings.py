"""
สัญญา config กลางของ SML AI Router

- รวม schema env เดียวสำหรับทุก runtime
- ตรวจสอบค่าจำเป็นตามโหมด (local/docker/coolify)
- แสดงข้อความผิดพลาดเป็นภาษาไทยและออกทันทีเมื่อ config ไม่ถูกต้อง
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Dict, List


SUPPORTED_MODES = {"local", "docker", "coolify"}
PROVIDER_KEY_VARS = [
    "GROQ_API_KEY",
    "CEREBRAS_API_KEY",
    "SAMBANOVA_API_KEY",
    "OPENROUTER_API_KEY",
    "NVIDIA_API_KEY",
    "TOGETHER_API_KEY",
    "MISTRAL_API_KEY",
    "DEEPINFRA_API_KEY",
    "COHERE_API_KEY",
]


@dataclass
class RuntimeSettings:
    mode: str
    proxy_host: str
    proxy_port: int
    dashboard_host: str
    dashboard_port: int
    keys_file: str
    domain_openclaw: str
    domain_proxy: str


class SettingsValidationError(Exception):
    def __init__(self, messages: List[str]):
        super().__init__("; ".join(messages))
        self.messages = messages


def _get_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _get_int(name: str, default: int, errors: List[str]) -> int:
    raw = os.environ.get(name, "").strip()
    if raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        errors.append(f"ตัวแปร {name} ต้องเป็นตัวเลข แต่ได้รับ '{raw}'")
        return default


def load_settings() -> RuntimeSettings:
    mode = _get_str("DEPLOY_MODE", "local").lower()
    return RuntimeSettings(
        mode=mode,
        proxy_host=_get_str("PROXY_HOST", "0.0.0.0"),
        proxy_port=int(_get_str("PROXY_PORT", "8900") or "8900"),
        dashboard_host=_get_str("DASHBOARD_HOST", "0.0.0.0"),
        dashboard_port=int(_get_str("DASHBOARD_PORT", "8898") or "8898"),
        keys_file=_get_str("KEYS_FILE", "api_keys.json"),
        domain_openclaw=_get_str("DOMAIN_OPENCLAW", ""),
        domain_proxy=_get_str("DOMAIN_PROXY", ""),
    )


def validate_settings(runtime: str) -> RuntimeSettings:
    errors: List[str] = []
    mode = _get_str("DEPLOY_MODE", "local").lower()

    if mode not in SUPPORTED_MODES:
        errors.append(
            f"DEPLOY_MODE ไม่ถูกต้อง: '{mode}' (ค่าที่รองรับ: local, docker, coolify)"
        )

    proxy_port = _get_int("PROXY_PORT", 8900, errors)
    dashboard_port = _get_int("DASHBOARD_PORT", 8898, errors)

    if not (1 <= proxy_port <= 65535):
        errors.append("PROXY_PORT ต้องอยู่ระหว่าง 1-65535")
    if not (1 <= dashboard_port <= 65535):
        errors.append("DASHBOARD_PORT ต้องอยู่ระหว่าง 1-65535")

    provider_key_count = sum(1 for key in PROVIDER_KEY_VARS if _get_str(key))
    if provider_key_count == 0:
        errors.append(
            "ต้องกำหนด API key อย่างน้อย 1 ตัว (เช่น GROQ_API_KEY หรือ OPENROUTER_API_KEY)"
        )

    if mode == "coolify":
        if not _get_str("DOMAIN_OPENCLAW"):
            errors.append("โหมด coolify ต้องกำหนด DOMAIN_OPENCLAW")
        if not _get_str("DOMAIN_PROXY"):
            errors.append("โหมด coolify ต้องกำหนด DOMAIN_PROXY")

    if errors:
        raise SettingsValidationError(errors)

    return RuntimeSettings(
        mode=mode,
        proxy_host=_get_str("PROXY_HOST", "0.0.0.0"),
        proxy_port=proxy_port,
        dashboard_host=_get_str("DASHBOARD_HOST", "0.0.0.0"),
        dashboard_port=dashboard_port,
        keys_file=_get_str("KEYS_FILE", "api_keys.json"),
        domain_openclaw=_get_str("DOMAIN_OPENCLAW", ""),
        domain_proxy=_get_str("DOMAIN_PROXY", ""),
    )


def validate_or_exit(runtime: str) -> RuntimeSettings:
    try:
        settings = validate_settings(runtime)
        print(f"✅ ตรวจสอบ config ผ่านแล้ว ({runtime}, mode={settings.mode})")
        return settings
    except SettingsValidationError as exc:
        print("❌ เริ่มระบบไม่ได้: พบ config ไม่ถูกต้อง")
        for idx, message in enumerate(exc.messages, start=1):
            print(f"  {idx}. {message}")
        sys.exit(2)
