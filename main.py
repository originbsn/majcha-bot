import os
import re
import math
import time
import requests
import threading
from flask import Flask, request, jsonify
from anthropic import Anthropic

import content

app = Flask(__name__)

def self_ping():
    import time as t
    t.sleep(60)
    while True:
        try:
            requests.get('https://majcha-bot-1.onrender.com/health', timeout=10)
        except:
            pass
        t.sleep(270)

threading.Thread(target=self_ping, daemon=True).start()
import httpx
http_client = httpx.Client(timeout=httpx.Timeout(60.0, connect=30.0))
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], base_url="https://restless-snow-9839.iiceeciibg.workers.dev", http_client=http_client)

MODEL = "claude-sonnet-5-5"
GRAPH_API = os.environ.get("GRAPH_API_VERSION", "v23.0")

PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")

# กฎหลักของบอท — เนื้อหาร้าน/เมนู/โปร/วิธีตอบ มาจาก Google Sheet (ดู content.py)
BASE_RULES = """คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" ตอบแชท Facebook แบบคนพิมจริงๆ รับคำถามทั่วไป จองโต๊ะ และสั่งอาหารล่วงหน้า

กฎการเขียน:
- ตอบสั้น 1-2 ประโยค (ยกเว้นตอนแสดงรายการเมนู/เมนูในเซ็ต)
- ถ้าแสดงรายการเมนู: ใช้ • นำหน้าแต่ละรายการ ขึ้นบรรทัดใหม่ทีละเมนู ลงท้ายด้วย link เมนู
- เมนูในเซ็ต: แยกหัวข้อแต่ละ STEP เป็นบรรทัดของตัวเอง เมนูละบรรทัดขึ้นต้นด้วย • เว้น 1 บรรทัดว่างระหว่าง STEP ห้ามเขียนรายชื่อเมนูต่อกันในวงเล็บหรือคั่นด้วยจุลภาค
- ลงท้าย ค่ะ หรือ นะคะ ห้ามใช้ **bold**
- emoji ไม่ต้องมีทุกข้อความ ใส่บางข้อความพอ ครั้งละไม่เกิน 1 ตัว และห้ามใช้ตัวเดิมซ้ำกับข้อความก่อนหน้า
- การชวนจองโต๊ะ: ทำตาม "คำสั่งเรื่องชวนจอง" ท้าย prompt ว่าข้อความนี้ชวนได้หรือไม่ (ใช้กับประโยคชวนจองใน "วิธีตอบ" ด้วย)
- ตอบภาษาเดียวกับที่ลูกค้าใช้ ถ้าลูกค้าพิมไทยตอบไทย ถ้าพิมอังกฤษตอบอังกฤษ
- ห้ามให้เบอร์โทรร้าน ห้ามบอกให้โทรยืนยัน ยกเว้นลูกค้าถามเองว่าโทรได้มั้ย หรือไม่รู้คำตอบจริงๆ หรือถามรายละเอียดโปรเพิ่มเติม
- ถ้าไม่รู้/ไม่มีข้อมูล: บอกว่าไม่แน่ใจค่ะ แล้วให้โทรถามที่เบอร์ร้าน
- โปรโมชั่น: พูดถึงได้เฉพาะโปรใน "โปรโมชั่นที่ใช้ได้ตอนนี้" เท่านั้น ถ้าไม่มี บอกว่าช่วงนี้ยังไม่มีโปรพิเศษค่ะ
- ถ้าลูกค้าเข้าเงื่อนไขโปรที่เป็นส่วนลด ให้หักส่วนลดก่อนคำนวณยอดรวมเสมอ
- เมนูที่ "หมด" ห้ามรับออเดอร์ บอกลูกค้าว่าวันนี้หมดแล้วและแนะนำเมนูอื่น
- ถ้าลูกค้าไม่บอกวัน = วันนี้ ห้ามถามวันซ้ำ ถ้าวันที่ลูกค้าจะมาเป็นวันหยุดร้าน ให้แจ้งลูกค้า

== กรณีสั่งอาหารล่วงหน้า ==
ขั้น 1: รับรายการเมนู
ขั้น 2: คำนวณราคารวมในใจทันที
ขั้น 3: ถามเวลา (ถ้าบอกแล้ว ข้าม ถ้าไม่บอกวัน = วันนี้)
ขั้น 4 (ห้ามข้าม): เช็กยอดรวม
  - ยอด > {deposit_min}: ถาม "มัดจำก่อนครึ่งนึงได้เลยนะคะ ถ้าใกล้ถึงเวลาจะทำให้ก่อนเลยค่ะ" รอคำตอบ
    * ตกลง: คำนวณ ยอดรวม ÷ 2 ปัดขึ้น (เช่น 1326÷2=663, 1469÷2=735) บอก "ครึ่งนึงคือ X บาทนะคะ เดี๋ยวส่ง QR ให้ทาง chat นะคะ" ปิดด้วย [BOOKING_COMPLETE_DEPOSIT]
    * ไม่มัดจำ: ถามชื่อและเบอร์ → ปิดด้วย [BOOKING_COMPLETE]
  - ยอด ≤ {deposit_min}: ถามชื่อและเบอร์ → ปิดด้วย [BOOKING_COMPLETE]
  (ห้ามพูดถึงมัดจำเลยถ้ายอดไม่ถึง {deposit_min})
ขั้น 5: ปิดด้วย tag เสมอ ห้ามปิดโดยไม่ผ่านขั้น 4

== กรณีจองโต๊ะ ==
ขั้น 1: กี่โมง (ถ้าบอกแล้ว ข้าม ไม่บอกวัน = วันนี้)
ขั้น 2: กี่ท่าน (ถ้าบอกแล้ว ข้าม)
ขั้น 3: ขอชื่อและเบอร์ ปิดด้วย [BOOKING_COMPLETE]

ใช้ tag [BOOKING_COMPLETE] / [BOOKING_COMPLETE_DEPOSIT] เฉพาะตอนได้ข้อมูลจองหรือออเดอร์ครบแล้วเท่านั้น
"""

THAI_DAYS = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
THAI_MONTHS = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
               'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']

def build_system_prompt(invite_booking=True):
    """สร้าง system prompt จากข้อมูลในชีต — ส่วนที่ไม่เปลี่ยนบ่อยอยู่ก่อน (cache ได้) วันเวลาอยู่ท้ายสุด"""
    data = content.get()
    now = content.now_bkk()
    today = now.date()

    info_lines = [f"{r['หัวข้อ']}: {r.get('รายละเอียด', '')}" for r in data["info"] if r.get("หัวข้อ")]

    menu_lines, last_cat = [], None
    for m in data["menu"]:
        name = m.get("ชื่อเมนู")
        if not name:
            continue
        cat = m.get("หมวด", "")
        if cat and cat != last_cat:
            menu_lines.append(f"[{cat}]")
            last_cat = cat
        line = f"{name} {m.get('ราคา', '')}"
        if content.is_true(m.get("แนะนำ")):
            line += " ★แนะนำ"
        if not content.is_true(m.get("มีขาย"), blank=True):
            line += " (หมด)"
        if m.get("หมายเหตุ"):
            line += f" — {m['หมายเหตุ']}"
        menu_lines.append(line)

    faq_lines = [f"- ถ้า{r['เมื่อลูกค้าถาม']}: {r.get('ให้ตอบ', '')}"
                 for r in data["faq"] if r.get("เมื่อลูกค้าถาม")]

    deposit_min = content.info_value(data, "มัดจำเมื่อยอดเกิน", "1000").replace(",", "")
    stable = BASE_RULES.replace("{deposit_min}", f"{int(deposit_min):,}" if deposit_min.isdigit() else deposit_min)
    stable += "\nวิธีตอบเมื่อลูกค้าถามเรื่องต่างๆ:\n" + "\n".join(faq_lines)
    stable += "\n\nข้อมูลร้าน:\n" + "\n".join(info_lines)
    stable += "\n\nเมนูและราคา (บาท):\n" + "\n".join(menu_lines)

    promo_lines = []
    for p in data["promos"]:
        if content.promo_status(p, today) != "active":
            continue
        line = f"- {p.get('ชื่อโปร', '')}: {p.get('รายละเอียด', '')}"
        start, end = content.parse_date(p.get("วันเริ่ม")), content.parse_date(p.get("วันสิ้นสุด"))
        if start or end:
            line += f" (ใช้ได้ {start.strftime('%d/%m/%Y') if start else ''} ถึง {end.strftime('%d/%m/%Y') if end else 'ไม่มีกำหนด'})"
        promo_lines.append(line)

    dynamic = (
        f"วันนี้: วัน{THAI_DAYS[today.weekday()]}ที่ {today.day} {THAI_MONTHS[today.month - 1]} {today.year} "
        f"เวลา {now.strftime('%H:%M')} น. (เวลาไทย)\n\n"
        "โปรโมชั่นที่ใช้ได้ตอนนี้:\n" + ("\n".join(promo_lines) if promo_lines else "(ไม่มี)") + "\n\n"
        "คำสั่งเรื่องชวนจอง: " + (
            "ข้อความนี้ชวนจองโต๊ะได้ (ถ้าลูกค้ากำลังจองอยู่ ให้ทำขั้นตอนจองต่อแทน)" if invite_booking else
            "ข้อความนี้ห้ามชวนจองโต๊ะ ตอบแค่คำถาม (ถ้าลูกค้ากำลังจองอยู่ ให้ทำขั้นตอนจองต่อตามปกติ)")
    )

    return [
        {"type": "text", "text": stable, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": dynamic},
    ]

# Session storage พร้อม TTL 24 ชม. — ป้องกัน memory leak
SESSION_TTL = 24 * 60 * 60  # 24 hours in seconds
user_sessions = {}
sessions_lock = threading.Lock()

def get_session(user_id):
    """ดึง session และ clean up sessions เก่าที่หมดอายุ"""
    now = time.time()

    with sessions_lock:
        # Clean up expired sessions ทุกครั้งที่มี request
        expired = [uid for uid, s in user_sessions.items() if now - s.get("last_active", 0) > SESSION_TTL]
        for uid in expired:
            del user_sessions[uid]

        if user_id not in user_sessions:
            user_sessions[user_id] = {
                "history": [],
                "last_active": now,
                "lock": threading.Lock(),  # กันข้อความของลูกค้าคนเดียวกันตอบสลับกัน
            }
        else:
            user_sessions[user_id]["last_active"] = now

        return user_sessions[user_id]

def send_telegram(message, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if not resp.ok:
            print(f"Telegram error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Telegram exception: {e}")

def build_telegram_summary(history, is_deposit):
    name = phone = time_val = pax = items = total = deposit = ''
    for i, m in enumerate(history):
        t = m['content']

        # เวลา
        tm = re.search(r'(\d{1,2})\s*(?:โมง|นาฬิกา|:[0-5]\d)', t)
        if tm and not time_val:
            time_val = tm.group(0).strip()

        # เบอร์ (จาก user)
        if m['role'] == 'user':
            ph = re.search(r'0\d[\d\s\-]{8,10}', t)
            if ph and not phone:
                phone = re.sub(r'[\s\-]', '', ph.group(0))[:10]

        # จำนวนคน
        px = re.search(r'(\d+)\s*(?:ท่าน|คน)', t)
        if px and not pax:
            pax = px.group(1) + ' ท่าน'

        # ยอดรวม — จับหลาย pattern
        tot = re.search(r'(?:รวม|ยอด|ทั้งหมด|คิดเป็น)\D{0,8}([1-9][\d,]{2,})\s*บาท', t)
        if not tot:
            tot = re.search(r'([1-9][\d,]{3,})\s*บาท', t)  # ตัวเลข 4+ หลัก
        if tot and not total:
            total = tot.group(1).replace(',', '') + ' บาท'

        # มัดจำ
        dep = re.search(r'ครึ่งนึงคือ\s*([\d,.]+)\s*บาท', t)
        if dep and not deposit:
            d = math.ceil(float(dep.group(1).replace(',', '')))
            deposit = str(d) + ' บาท'

        # ชื่อ — ดูจาก user ที่ตอบหลัง bot ถามชื่อ/เบอร์
        if m['role'] == 'assistant' and any(w in t for w in ['ขอชื่อ','ชื่อและเบอร์','ชื่อ-เบอร์','แจ้งชื่อ']):
            if i + 1 < len(history) and history[i + 1]['role'] == 'user':
                ans = history[i + 1]['content'].strip()
                parts = ans.split()
                for p in parts:
                    if len(p) >= 2 and not re.match(r'^[\d\s]+$', p) and not name:
                        name = p
                ph2 = re.search(r'0\d[\d\s\-]{8,}', ans)
                if ph2 and not phone:
                    phone = re.sub(r'[\s\-]', '', ph2.group(0))[:10]

        # เมนู (จาก bot message ที่มี |)
        if m['role'] == 'assistant' and not items:
            pipe = re.search(
                r'[฀-๿a-zA-Z][฀-๿a-zA-Z\s]+\d+(?:\s*\|\s*[฀-๿a-zA-Z][฀-๿a-zA-Z\s]+\d+){1,}',
                t
            )
            if pipe:
                items = pipe.group(0)[:200]

    lines = ['🔔 <b>แจ้งเตือนออเดอร์ใหม่ — มัจฉา ปลาจุ่ม</b>']
    lines.append('💰 ต้องมัดจำ 50%' if is_deposit else '✅ จองปกติ')
    lines.append('')
    if time_val: lines.append(f'🕐 เวลา: {time_val} น. (วันนี้)')
    if pax:      lines.append(f'👥 จำนวน: {pax}')
    if name:     lines.append(f'👤 ชื่อ: {name}')
    if phone:    lines.append(f'📞 เบอร์: {phone}')
    if items:    lines.append(f'🍽 เมนู: {items}')
    if total:    lines.append(f'💵 ยอดรวม: {total}')
    if is_deposit and deposit: lines.append(f'💰 มัดจำ 50%: {deposit}')
    if is_deposit: lines.append('⚠️ รอส่ง QR ให้ลูกค้าทาง chat')
    if not any([time_val, pax, name, phone]):
        lines.append('(ข้อมูลไม่ครบ — ตรวจสอบแชทอีกครั้ง)')

    return '\n'.join(lines)

def send_message_fb(recipient_id, text):
    url = f"https://graph.facebook.com/{GRAPH_API}/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    try:
        resp = requests.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }, timeout=5)
        if not resp.ok:
            print(f"FB send error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"FB send exception: {e}")

# ถ้าลูกค้าถามเรื่องโปร ส่งรูปโปรทาง DM ก่อนข้อความ (คอมเมนต์ส่งรูปไม่ได้)
PROMO_IMAGE_URL = "https://i.ibb.co/MkLtBJ6g/Screenshot-2026-05-15-at-11-40-05-AM.png"
PROMO_KEYWORDS = [
    'โปร', 'โปรโมชั่น', 'promotion', 'set', 'เซ็ต', 'ชุด', 'premium', 'พรีเมียม',
    'ส่วนลด', 'discount', 'ราคาพิเศษ', '999', '1199', '1990', 'คนละครึ่ง', 'ไทยช่วยไทย'
]

def send_image_fb(recipient_id, image_url):
    url = f"https://graph.facebook.com/{GRAPH_API}/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    try:
        resp = requests.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"attachment": {"type": "image", "payload": {"url": image_url, "is_reusable": True}}}
        }, timeout=5)
        if not resp.ok:
            print(f"FB image send error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"FB image send exception: {e}")

ERROR_REPLY ="ขออภัยค่ะ ตอนนี้ร้านยุ่งมาก ไม่สะดวกตอบแชทจริงๆ รบกวนโทร 081-751-4044 นะคะ 🙏"

def get_ai_reply(user_id, user_text):
    session = get_session(user_id)

    with session["lock"]:
        history = session["history"] + [{"role": "user", "content": user_text}]

        # ชวนจองในคำตอบที่ 1, 4, 7, ... และเลิกชวนเมื่อจองเสร็จแล้ว
        past_replies = [m["content"] for m in session["history"] if m["role"] == "assistant"]
        booked = any("[BOOKING_COMPLETE" in r for r in past_replies)
        invite = not booked and len(past_replies) % 3 == 0

        try:
            response = client.beta.messages.create(
                model=MODEL,
                max_tokens=4000,
                system=build_system_prompt(invite),
                messages=history[-20:],
                output_config={"effort": "low"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except Exception as e:
            print(f"Claude API error: {e}")
            return ERROR_REPLY

        reply = "".join(b.text for b in response.content if b.type == "text").strip()
        if response.stop_reason == "refusal" or not reply:
            print(f"Claude no reply: stop_reason={response.stop_reason}")
            return ERROR_REPLY

        # เก็บ history หลังได้คำตอบแล้วเท่านั้น — ไม่ให้ user ต่อกัน 2 ข้อความถ้า API ล่ม
        history.append({"role": "assistant", "content": reply})
        session["history"] = history

    # ตรวจ booking complete
    is_deposit = '[BOOKING_COMPLETE_DEPOSIT]' in reply
    is_complete = '[BOOKING_COMPLETE]' in reply or is_deposit

    if is_complete:
        send_telegram(build_telegram_summary(history, is_deposit))

    return reply.replace('[BOOKING_COMPLETE_DEPOSIT]', '').replace('[BOOKING_COMPLETE]', '').strip()

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Forbidden', 403

def reply_to_comment(comment_id, message):
    url = f"https://graph.facebook.com/{GRAPH_API}/{comment_id}/comments"
    try:
        resp = requests.post(url, json={
            "message": message,
            "access_token": PAGE_ACCESS_TOKEN
        }, timeout=5)
        if not resp.ok:
            print(f"Comment reply error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Comment reply exception: {e}")

def handle_dm(sender_id, user_text):
    try:
        reply = get_ai_reply(sender_id, user_text)
        if reply != ERROR_REPLY and any(k in user_text.lower() for k in PROMO_KEYWORDS):
            send_image_fb(sender_id, PROMO_IMAGE_URL)
        send_message_fb(sender_id, reply)
    except Exception as e:
        print(f"Event processing error: {e}")

def handle_comment(commenter_id, comment_id, comment_text):
    try:
        reply = get_ai_reply(f"comment_{commenter_id}", comment_text)
        reply_to_comment(comment_id, reply)
    except Exception as e:
        print(f"Comment processing error: {e}")

def run_in_background(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()

@app.route('/webhook', methods=['POST'])
def webhook():
    # ตอบ Facebook 200 ทันที แล้วค่อยให้ AI ตอบใน background — ถ้าช้า Facebook จะส่งข้อความซ้ำ
    try:
        data = request.json
        if not data:
            return 'OK', 200

        for entry in data.get('entry', []):
            # handle DM
            for event in entry.get('messaging', []):
                sender_id = event.get('sender', {}).get('id')
                if not sender_id:
                    continue
                msg = event.get('message', {})
                if not msg or msg.get('is_echo'):
                    continue
                user_text = msg.get('text', '').strip()
                if not user_text:
                    continue
                run_in_background(handle_dm, sender_id, user_text)

            # handle comments
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if change.get('field') != 'feed':
                    continue
                if value.get('item') != 'comment':
                    continue
                if value.get('verb') != 'add':
                    continue
                # ข้าม comment ของเพจเอง
                if value.get('from', {}).get('id') == entry.get('id'):
                    continue
                comment_id = value.get('comment_id')
                comment_text = value.get('message', '').strip()
                commenter_id = value.get('from', {}).get('id', 'unknown')
                if not comment_id or not comment_text:
                    continue
                run_in_background(handle_comment, commenter_id, comment_id, comment_text)

    except Exception as e:
        print(f"Webhook error: {e}")

    return 'OK', 200

TELEGRAM_HELP = (
    "คำสั่งบอทมัจฉา:\n"
    "/reload — ดึงข้อมูลจาก Google Sheet ใหม่ทันที\n"
    "/status — ดูว่าตอนนี้บอทเห็นโปร/เมนูอะไรบ้าง"
)

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    if TELEGRAM_WEBHOOK_SECRET and \
            request.headers.get('X-Telegram-Bot-Api-Secret-Token') != TELEGRAM_WEBHOOK_SECRET:
        return 'Forbidden', 403
    try:
        msg = (request.json or {}).get('message') or {}
        # รับคำสั่งเฉพาะจากแชทของร้านเท่านั้น
        if str(msg.get('chat', {}).get('id')) != str(TELEGRAM_CHAT_ID):
            return 'OK', 200
        command = (msg.get('text') or '').strip().split()[0:1]
        command = command[0].split('@')[0].lower() if command else ''

        if command == '/reload':
            ok, note = content.reload(force=True)
            # ถ้าไม่สำเร็จ status_text() แสดงสาเหตุให้แล้ว
            send_telegram((f"✅ {note}\n\n" if ok else "") + content.status_text(), parse_mode=None)
        elif command == '/status':
            send_telegram(content.status_text(), parse_mode=None)
        elif command in ('/help', '/start'):
            send_telegram(TELEGRAM_HELP, parse_mode=None)
    except Exception as e:
        print(f"Telegram webhook error: {e}")
    return 'OK', 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "sessions": len(user_sessions)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
