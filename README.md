# 🐟 Majcha Pla Jum — Facebook Bot

## วิธี Deploy บน Railway (ฟรี)

### ขั้นตอนที่ 1 — อัปโหลดไฟล์ขึ้น GitHub
1. ไปที่ github.com → New repository → ชื่อ "majcha-bot"
2. อัปโหลดไฟล์ main.py, requirements.txt, railway.toml

### ขั้นตอนที่ 2 — Deploy บน Railway
1. ไปที่ railway.app → Login ด้วย GitHub
2. กด "New Project" → "Deploy from GitHub repo"
3. เลือก repo "majcha-bot"
4. Railway จะ deploy อัตโนมัติ

### ขั้นตอนที่ 3 — ตั้งค่า Environment Variables
ใน Railway → Settings → Variables → เพิ่ม:
```
ANTHROPIC_API_KEY   = sk-ant-xxxx (Claude API key ของคุณ)
PAGE_ACCESS_TOKEN   = EAAxxxx (Facebook Page Access Token)
VERIFY_TOKEN        = majcha2024 (ตั้งเองได้ คำอะไรก็ได้)
```

### ขั้นตอนที่ 4 — เอา URL จาก Railway
หลัง deploy เสร็จ Railway จะให้ URL เช่น:
`https://majcha-bot-production.up.railway.app`

Webhook URL คือ:
`https://majcha-bot-production.up.railway.app/webhook`

### ขั้นตอนที่ 5 — ตั้งค่า Facebook Webhook
1. ไปที่ developers.facebook.com → App ของคุณ
2. Messenger → Settings → Webhooks
3. กด "Add Callback URL"
   - Callback URL: `https://your-url.railway.app/webhook`
   - Verify Token: `majcha2024` (ต้องตรงกับที่ตั้งใน Railway)
4. กด Verify and Save
5. Subscribe to events: messages, messaging_postbacks

### เสร็จแล้ว! 🎉
Bot จะตอบลูกค้าอัตโนมัติทันที
