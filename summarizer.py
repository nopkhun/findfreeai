"""
Summarizer — จำแนกประเภทคำถาม + สรุปบทสนทนา
Pure Python, ไม่ต้องลง library เพิ่ม
"""

import re
from collections import Counter

STOPWORDS = set("a an the is are was were be been being have has had do does did will would shall should "
    "can could may might must need to of in on at by for with from as into through during before after "
    "above below between under over about up down out off then than so if or and but not no nor "
    "i me my we our you your he him his she her it its they them their this that these those "
    "what which who whom how when where why all each every both few more most other some such "
    "am very just also back only even still again further once here there".split())


def estimate_tokens(text):
    """ประมาณจำนวน tokens (1 token ~ 4 chars)"""
    return max(1, len(text) // 4)


def keyword_extract(texts, top_n=10):
    """ดึง keywords จาก texts"""
    words = []
    for t in texts:
        for w in re.findall(r'[a-zA-Z\u0e00-\u0e7f]{3,}', t.lower()):
            if w not in STOPWORDS and len(w) > 2:
                words.append(w)
    return [w for w, _ in Counter(words).most_common(top_n)]


def detect_query_type(message):
    """จำแนกประเภทคำถาม"""
    msg = message.lower()
    if any(k in msg for k in ["def ", "class ", "function", "import ", "```", "code", "error", "bug", "fix"]):
        return "code"
    if any(k in msg for k in ["calculate", "formula", "equation", "math", "sum", "average", "percent"]):
        return "math"
    if any(k in msg for k in ["write", "story", "poem", "create", "imagine", "generate", "compose"]):
        return "creative"
    if any(k in msg for k in ["what is", "who is", "explain", "describe", "define", "how does", "why"]):
        return "factual"
    return "chat"


def summarize_messages(messages):
    """สรุปบทสนทนาเป็นข้อความสั้น (ไม่เรียก AI)"""
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    if not user_msgs:
        return ""

    keywords = keyword_extract(user_msgs, 8)
    first = user_msgs[0][:100]
    last = user_msgs[-1][:80] if len(user_msgs) > 1 else ""
    query_types = [detect_query_type(m) for m in user_msgs]
    types = list(set(query_types))

    parts = [f"บทสนทนา {len(messages)} ข้อความ"]
    if keywords:
        parts.append(f"หัวข้อ: {', '.join(keywords[:5])}")
    if types:
        parts.append(f"ประเภท: {', '.join(types)}")
    parts.append(f"เริ่มจาก: {first}")
    if last:
        parts.append(f"ล่าสุด: {last}")

    return ". ".join(parts)[:500]
