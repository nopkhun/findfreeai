"""
Skill Engine — เรียนรู้จากการใช้งานจริง ปรับ routing อัตโนมัติ
บันทึก latency, error rate, query type performance
ทุก 50 requests จะคำนวณ routing ใหม่
"""

import json
import os
import threading
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SKILL_DB = os.path.join(DATA_DIR, "skill_db.json")
ROUTING_DB = os.path.join(DATA_DIR, "routing_patterns.json")
MAX_LATENCY_SAMPLES = 100
RECOMPUTE_EVERY = 50

_lock = threading.Lock()


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_skill_db():
    _ensure_dirs()
    if os.path.exists(SKILL_DB):
        try:
            with open(SKILL_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "version": 1,
        "total_requests": 0,
        "providers": {},
        "query_type_performance": {},
        "hourly_patterns": {},
        "error_patterns": {},
        "last_updated": "",
    }


def save_skill_db(db):
    _ensure_dirs()
    db["last_updated"] = datetime.now().isoformat()
    with _lock:
        with open(SKILL_DB, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)


def load_routing():
    if os.path.exists(ROUTING_DB):
        try:
            with open(ROUTING_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_routing(data):
    _ensure_dirs()
    with open(ROUTING_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_call(provider_id, query_type, latency_ms, success, error_type=None):
    """บันทึกผลการเรียก API"""
    db = load_skill_db()
    db["total_requests"] += 1

    # Provider stats
    if provider_id not in db["providers"]:
        db["providers"][provider_id] = {
            "total_ok": 0, "total_fail": 0,
            "latency_samples": [], "avg_latency_ms": 0,
            "fail_streak": 0, "learned_priority": 0,
        }
    p = db["providers"][provider_id]

    if success:
        p["total_ok"] += 1
        p["fail_streak"] = 0
        p["latency_samples"].append(latency_ms)
        if len(p["latency_samples"]) > MAX_LATENCY_SAMPLES:
            p["latency_samples"] = p["latency_samples"][-MAX_LATENCY_SAMPLES:]
        p["avg_latency_ms"] = round(sum(p["latency_samples"]) / len(p["latency_samples"]))
    else:
        p["total_fail"] += 1
        p["fail_streak"] += 1
        p["last_fail_reason"] = error_type or "unknown"

    # Query type performance
    if query_type not in db["query_type_performance"]:
        db["query_type_performance"][query_type] = {}
    qtp = db["query_type_performance"][query_type]
    if provider_id not in qtp:
        qtp[provider_id] = {"ok": 0, "fail": 0, "avg_latency": 0, "total_latency": 0}
    qt = qtp[provider_id]
    if success:
        qt["ok"] += 1
        qt["total_latency"] += latency_ms
        qt["avg_latency"] = round(qt["total_latency"] / qt["ok"])
    else:
        qt["fail"] += 1

    # Hourly patterns
    hour = datetime.now().strftime("%H")
    if provider_id not in db["hourly_patterns"]:
        db["hourly_patterns"][provider_id] = {}
    hp = db["hourly_patterns"][provider_id]
    if hour not in hp:
        hp[hour] = {"ok": 0, "fail": 0}
    hp[hour]["ok" if success else "fail"] += 1

    # Error patterns
    if not success and error_type:
        if provider_id not in db["error_patterns"]:
            db["error_patterns"][provider_id] = {}
        ep = db["error_patterns"][provider_id]
        ep[error_type] = ep.get(error_type, 0) + 1

    save_skill_db(db)

    # Recompute routing ทุก N requests
    if db["total_requests"] % RECOMPUTE_EVERY == 0:
        recompute_routing(db)


def classify_error(http_status, error_str=""):
    """จำแนกประเภท error"""
    err = error_str.lower()
    if http_status == 429 or "rate" in err or "limit" in err:
        return "rate_limit"
    if http_status in (401, 403) or "auth" in err or "key" in err:
        return "auth"
    if "timeout" in err or "timed out" in err:
        return "timeout"
    if http_status >= 500:
        return "server_error"
    if "connect" in err or "network" in err:
        return "network"
    return "unknown"


def recompute_routing(db=None):
    """คำนวณ routing ใหม่จากข้อมูลที่เรียนรู้"""
    if db is None:
        db = load_skill_db()

    routing = {"generated_at": datetime.now().isoformat(), "confidence": {}}

    for query_type, providers in db.get("query_type_performance", {}).items():
        scores = []
        total_samples = 0
        for pid, perf in providers.items():
            total = perf["ok"] + perf["fail"]
            total_samples += total
            if total == 0:
                continue
            ok_rate = perf["ok"] / total
            speed_score = max(0, 1 - (perf["avg_latency"] / 5000))
            score = (ok_rate * 0.6) + (speed_score * 0.4)

            # ลด score ถ้า fail streak สูง
            p_stats = db["providers"].get(pid, {})
            if p_stats.get("fail_streak", 0) > 3:
                score *= 0.5

            scores.append((pid, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        routing[query_type] = [pid for pid, _ in scores]
        routing["confidence"][query_type] = min(total_samples / 100, 1.0)

    save_routing(routing)
    return routing


def get_best_providers_for_type(query_type):
    """หา providers ที่ดีที่สุดสำหรับ query type นี้"""
    routing = load_routing()
    if query_type not in routing:
        return []
    confidence = routing.get("confidence", {}).get(query_type, 0)
    if confidence < 0.3:
        return []  # ยังไม่มั่นใจพอ ให้ใช้ default
    return routing[query_type]


def get_skill_summary():
    """สรุปสิ่งที่เรียนรู้มา"""
    db = load_skill_db()
    routing = load_routing()

    summary = {
        "total_requests": db.get("total_requests", 0),
        "last_updated": db.get("last_updated", ""),
        "providers": {},
        "best_per_type": {},
        "routing_confidence": routing.get("confidence", {}),
    }

    for pid, p in db.get("providers", {}).items():
        total = p["total_ok"] + p["total_fail"]
        summary["providers"][pid] = {
            "total": total,
            "success_rate": round(p["total_ok"] / total * 100, 1) if total > 0 else 0,
            "avg_latency_ms": p["avg_latency_ms"],
            "fail_streak": p.get("fail_streak", 0),
        }

    for qt in routing:
        if qt in ("generated_at", "confidence"):
            continue
        providers = routing[qt]
        if providers:
            summary["best_per_type"][qt] = providers[0]

    return summary
