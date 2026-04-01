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


def test_models_endpoint_returns_openai_list_shape():
    status, data = _request_json("/v1/models")
    assert status == 200
    assert "data" in data
    assert isinstance(data["data"], list)


def test_chat_nonstream_returns_openai_completion_shape():
    status, data = _request_json(
        "/v1/chat/completions",
        method="POST",
        payload={"model": "auto", "messages": [{"role": "user", "content": "ทดสอบ"}]},
    )
    assert status == 200
    for key in ["id", "object", "choices", "model"]:
        assert key in data


def test_chat_stream_emits_sse_data_events():
    req = urllib.request.Request(
        f"{BASE}/v1/chat/completions",
        data=json.dumps(
            {
                "model": "auto",
                "stream": True,
                "messages": [{"role": "user", "content": "ทดสอบสตรีม"}],
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        text = resp.read().decode("utf-8", errors="replace")

    assert "data:" in text
    assert "data: [DONE]" in text
