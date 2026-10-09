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

## แก้โปร / เมนู / ข้อมูลร้าน ผ่าน Google Sheet (ไม่ต้องแก้โค้ด)

### ตั้งค่าครั้งแรก
1. สร้าง Google Sheet ใหม่ มี 4 แท็บ ชื่อตรงตามนี้: `ข้อมูลร้าน`, `เมนู`, `โปรโมชั่น`, `วิธีตอบ`
2. นำเข้าข้อมูลตั้งต้นจากโฟลเดอร์ `sheet_template/` (File → Import → Upload → เลือก "Replace current sheet" ทีละแท็บ)
3. กด Share → General access → **Anyone with the link → Viewer**
4. ก๊อป Sheet ID จาก URL (`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`) ไปใส่ env `SHEET_ID`
5. (ถ้าจะใช้คำสั่งใน Telegram) ตั้ง env `TELEGRAM_WEBHOOK_SECRET` เป็นคำลับอะไรก็ได้ แล้วเปิด URL นี้ในเบราว์เซอร์ 1 ครั้ง:
   `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<โดเมนบอท>/telegram&secret_token=<TELEGRAM_WEBHOOK_SECRET>`

ถ้ายังไม่ตั้ง `SHEET_ID` บอทจะใช้ข้อมูลตั้งต้นในโค้ด (`content.py`) ทำงานได้ปกติ

### ใช้งานประจำวัน
- **เพิ่มโปร**: เพิ่มแถวในแท็บ `โปรโมชั่น` ใส่วันเริ่ม/วันสิ้นสุดเป็น `2026-10-31` หรือ `31/10/2026` (เว้นว่าง = ไม่มีกำหนด) หมดวันแล้วบอทเลิกพูดถึงเอง
- **ปิดโปรชั่วคราว**: ตั้ง `เปิดใช้` = FALSE
- **เมนูหมด**: ตั้ง `มีขาย` = FALSE บอทจะบอกลูกค้าว่าหมดและไม่รับออเดอร์
- **ข้อมูลร้าน**: เพิ่มแถวหัวข้อใหม่ได้เลย บอทอ่านทุกแถว
- **วิธีตอบพิเศษ**: เพิ่มแถว "เมื่อลูกค้าถาม…" / "ให้ตอบ…"
- บอทดึงชีตใหม่เองทุก 5 นาที ถ้าอยากให้เห็นทันทีพิมพ์ `/reload` ใน Telegram, พิมพ์ `/status` เพื่อดูว่าบอทเห็นโปรอะไรอยู่
- ถ้าดึงชีตไม่ได้ บอทใช้ข้อมูลล่าสุดที่ดึงได้ต่อ (ไม่ล่ม) และ `/status` จะแจ้งสาเหตุ

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
