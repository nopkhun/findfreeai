from __future__ import annotations

import json
import urllib.request


BASE = "http://127.0.0.1:8900"


def _request_json(path: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}", data=data, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def test_providers_endpoint_exposes_health_and_key_state():
    status, data = _request_json("/v1/providers")
    assert status == 200
    assert "providers" in data
    assert isinstance(data["providers"], list)
    if data["providers"]:
        sample = data["providers"][0]
        assert "id" in sample
        assert "has_key" in sample
        assert "stats" in sample


def test_stats_endpoint_contains_request_log_for_operational_debug():
    status, data = _request_json("/v1/stats")
    assert status == 200
    assert "request_log" in data
    assert isinstance(data["request_log"], list)


def test_auto_routing_response_contains_proxy_metadata_on_success():
    status, data = _request_json(
        "/v1/chat/completions",
        method="POST",
        payload={
            "model": "auto",
            "messages": [{"role": "user", "content": "ทดสอบ fallback"}],
        },
    )
    assert status == 200
    assert "_proxy" in data
    proxy = data["_proxy"]
    assert "provider" in proxy
    assert "attempt" in proxy
    assert proxy["attempt"] >= 1
