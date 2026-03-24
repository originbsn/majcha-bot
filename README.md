# 🐟 Majcha Pla Jum — Facebook Bot

## วิธี Deploy บน Railway

### ขั้นตอนที่ 1 — อัปโหลดไฟล์ขึ้น GitHub
1. ไปที่ github.com → New repository → ชื่อ "majcha-bot"
2. อัปโหลดไฟล์: `main.py`, `requirements.txt`, `railway.toml`
3. ⚠️ **ห้ามใส่ API key หรือ token ใดๆ ในโค้ด**

### ขั้นตอนที่ 2 — Deploy บน Railway
1. ไปที่ railway.app → Login ด้วย GitHub
2. กด "New Project" → "Deploy from GitHub repo"
3. เลือก repo "majcha-bot"
4. Railway จะ deploy อัตโนมัติ

### ขั้นตอนที่ 3 — ตั้งค่า Environment Variables
ใน Railway → Settings → Variables → เพิ่มทั้ง 5 ตัวนี้:

```
ANTHROPIC_API_KEY     = sk-ant-xxxx
PAGE_ACCESS_TOKEN     = EAAxxxx
VERIFY_TOKEN          = majcha2024
TELEGRAM_BOT_TOKEN    = xxxxxx:xxxx (Token จาก @BotFather)
TELEGRAM_CHAT_ID      = xxxxxxxxx (Chat ID ของแก)
```

### ขั้นตอนที่ 4 — เอา URL จาก Railway
หลัง deploy เสร็จ Railway จะให้ URL เช่น:
`https://majcha-bot-production.up.railway.app`

Webhook URL คือ:
`https://majcha-bot-production.up.railway.app/webhook`

Health check URL (ใช้เช็คว่า bot ยังรันอยู่):
`https://majcha-bot-production.up.railway.app/health`

### ขั้นตอนที่ 5 — ตั้งค่า Facebook Webhook
1. ไปที่ developers.facebook.com → App ของคุณ
2. Messenger → Settings → Webhooks
3. กด "Add Callback URL"
   - Callback URL: `https://your-url.railway.app/webhook`
   - Verify Token: `majcha2024`
4. กด Verify and Save
5. Subscribe to events: `messages`, `messaging_postbacks`

### เสร็จแล้ว! 🎉

---

## สิ่งที่แก้ในเวอร์ชันนี้

| ปัญหาเดิม | แก้แล้ว |
|---|---|
| Telegram token hardcode ใน code | ย้ายเป็น env variable ทั้งหมด |
| Memory leak — sessions ไม่มีวันหมด | เพิ่ม TTL 24 ชม. auto-cleanup |
| Webhook crash ถ้า Facebook ส่ง payload แปลก | ครอบ try/except ทุกชั้น |
| ไม่เช็ค response จาก Facebook API | เพิ่ม error logging |
| `import re` อยู่ในลูป | ย้ายขึ้น top-level |
| Bot ตอบ echo message ของตัวเอง | เช็ค `is_echo` แล้ว skip |
| ไม่มี health check endpoint | เพิ่ม `/health` |
