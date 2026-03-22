# FindFreeAI — Claude Code CLI Skill

## โปรเจคนี้คืออะไร
ระบบค้นหา ทดสอบ และจัดการ AI API ฟรี พร้อม Proxy สำหรับ OpenClaw
Claude Code CLI เป็นแกนหลักในการพัฒนาและดูแลระบบนี้

## ไฟล์หลัก
| ไฟล์ | หน้าที่ |
|------|---------|
| `app.py` | Dashboard + Scanner + Tester (:8899) |
| `proxy.py` | AI Proxy แบบ OpenRouter (:8900) |
| `.env` | API Keys (ห้าม commit) |
| `free_ai_apis.json` | ข้อมูลผลสแกน |
| `proxy_config.json` | Config ของ proxy |

## วิธีรัน
```bash
python app.py     # Dashboard http://127.0.0.1:8899
python proxy.py   # Proxy http://127.0.0.1:8900/v1
```

## สิ่งที่ Claude Code CLI ทำได้
1. **ค้นหา API ฟรีใหม่** — สแกน GitHub, Reddit, HN, Dev.to
2. **ทดสอบ API** — ส่ง chat request จริง ให้คะแนน 0-100
3. **ทดสอบ API Key** — เช็คว่า key ใช้ได้จริงหรือไม่
4. **เพิ่ม provider ใหม่** — เพิ่มใน PROVIDERS dict ใน proxy.py
5. **ปรับ proxy config** — เปลี่ยน mode (auto/manual/round-robin)
6. **ตรวจสอบความปลอดภัย** — เช็ค URL น่าสงสัย

## Rules
- ใช้ภาษาไทยใน UI และ log เสมอ
- ห้าม hardcode API key ในโค้ด ใช้ .env เท่านั้น
- ทดสอบก่อน deploy เสมอ (รัน python app.py แล้วเช็ค)
- Windows ต้อง reconfigure stdout เป็น utf-8
- เตือน user เรื่อง malware / API น่าสงสัยเสมอ

## Proxy Model Format
```
auto                              → เลือก provider ดีที่สุดอัตโนมัติ
groq/llama-3.3-70b-versatile     → เจาะจง provider + model
llama-3.3-70b-versatile          → หา provider ที่มี model นี้
```
