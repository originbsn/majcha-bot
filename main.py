import os
import math
import requests
from flask import Flask, request
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    timeout=30.0
)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = "majcha2024"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8793240457:AAF1Zr0Aws7tdzM-H1VRHB5q3E9ufZBKaxU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5146262487")

KNOWLEDGE_BASE = """
ร้านมัจฉา ปลาจุ่ม:
เวลาเปิด: 11:00-22:00 น. | หยุด: วันจันทร์
ที่ตั้ง: ระหว่างกาดมีโชค-เซ็นทรัลเฟสติวัล เชียงใหม่ แถวรวมโชค ติดถนนใหญ่
โทร: 052-005-581 หรือ 081-751-4044
ไม่มีบริการส่งถึงบ้าน ถ้าต้องการส่งให้เรียก Grab Food หรือ Grab Delivery มารับเอง
Google Maps: https://maps.app.goo.gl/ZY884ugFrGCJXmoD6

ชุดเซ็ต (ราคาพิเศษ ไม่ใช่โปรโมชัน):
- ชุดสุขใจ 419 บาท (1-2 ท่าน): ปลาจุ่มปลาช่อน + ยำหัวปลีไข่เค็ม + ข้าวสวย
- ชุดอิ่มสุข 909 บาท ★ขายดี (2-3 ท่าน): ปลาจุ่มปลากะพง + ไข่เจียวปูก้อน + ผัดพริกแกงปลาหมึก + ข้าวสวย
- ชุดเลี้ยงครอบครัว 1,469 บาท (4-6 ท่าน): ปลาจุ่มปลากะพง + กุ้งแม่น้ำทอดราดซอสมะขาม + ต้มยำกุ้งหม้อใหญ่ + ปูก้อนผัดใบโหระพา + ยำวุ้นเส้น + ข้าวสวย 2 โถ

เมนูแนะนำ ★: ปลาจุ่มปลาช่อน 279 | ปลาจุ่มปลากะพง 399 | ไก่ผัดมะม่วงหิมพานต์ 169 | ปลาหมึกผัดไข่เค็ม 189
เมนูลิงก์: https://www.canva.com/design/DAGv3CnDsgM/view
"""

GENERAL_PROMPT = f"""คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" ตอบแชท Facebook แบบคนพิมจริงๆ

กฎ:
- ตอบสั้น 1-2 ประโยคเท่านั้น
- ห้ามใช้ ** bullet numbered list ถ้าจะแสดงรายการให้คั่นด้วย |
- emoji แค่ 1 ตัว
- ถ้าถามส่งบ้าน: ทางร้านไม่มีบริการส่ง แนะนำ Grab Food
- ถ้าลูกค้าบอกว่าจะมากิน: ถามว่าจะจองโต๊ะไว้ก่อนมั้ยคะ
- ถ้าไม่รู้: ไม่แน่ใจค่ะ ลองถามทาง chat ได้เลยนะคะ (ห้ามให้เบอร์โทร)

ข้อมูลร้าน:
{KNOWLEDGE_BASE}
"""

BOOKING_PROMPT = """คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" รับสั่งอาหารล่วงหน้าและจองโต๊ะผ่าน Facebook

ราคาเมนู:
ชุดสุขใจ 419 | ชุดอิ่มสุข 909 | ชุดเลี้ยงครอบครัว 1469
ปลาจุ่มปลาช่อน 279 | ปลาจุ่มปลากะพง 399 | ไก่ผัดมะม่วงหิมพานต์ 169 | ปลาหมึกผัดไข่เค็ม 189 | ปลากะพงทอดน้ำปลา 399 | ไข่เจียวปูก้อน 349 | ไข่เจียวปู 189 | กุ้งแม่น้ำทอดราดซอสมะขาม 259 | ต้มยำกุ้งน้ำข้น 299 | ต้มยำกุ้งน้ำข้นหม้อใหญ่ 399 | ยำวุ้นเส้น 149 | ยำหัวปลีไข่เค็ม 129

กฎ: พิมสั้น เป็นกันเอง emoji 1 ตัว ห้าม ** bullet list ห้ามให้โทร ถ้าไม่บอกวัน=วันนี้

== สั่งล่วงหน้า ==
1. รับเมนู → คำนวณยอด
2. ถามเวลา (ถ้าบอกแล้วข้าม ไม่บอกวัน=วันนี้)
3. ตรวจยอด: >1000 → ถามมัดจำ ตกลง→บอกยอดครึ่ง(ปัดขึ้น)+[BOOKING_COMPLETE_DEPOSIT] ไม่มัดจำ→[BOOKING_COMPLETE] / ≤1000 → ถามชื่อ→[BOOKING_COMPLETE]

== จองโต๊ะ ==
ถามเวลา → กี่ท่าน → ชื่อ+เบอร์ → [BOOKING_COMPLETE]
"""

BOOKING_KEYWORDS = [
    'จอง','จองโต๊ะ','book','reserve','ขอจอง','อยากจอง',
    'สั่งล่วงหน้า','สั่งอาหารล่วงหน้า','preorder','ล่วงหน้า',
    'อยากมากิน','อยากเข้าไปกิน','จะมากิน','จะไปกิน','อยากไปกิน',
    'มาทาน','ไปทาน','อยากมาทาน','จะมาทาน',
    'สั่งชุด','ชุดสุขใจ','ชุดอิ่มสุข','ชุดเลี้ยงครอบครัว','ชุดเซ็ต',
    'สั่ง','ขอสั่ง','อยากสั่ง'
]

user_sessions = {}

def is_booking_intent(text):
    return any(k in text for k in BOOKING_KEYWORDS)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=5)
    except Exception as e:
        print(f"Telegram error: {e}")

def build_telegram_summary(history, is_deposit):
    import re
    name = phone = time_val = pax = items = total = deposit = ''
    for i, m in enumerate(history):
        t = m['content']
        tm = re.search(r'(\d{1,2})\s*(?:โมง|นาฬิกา)', t)
        if tm and not time_val: time_val = tm.group(0).strip()
        if m['role'] == 'user':
            ph = re.search(r'0\d[\d\s\-]{8,10}', t)
            if ph and not phone: phone = re.sub(r'[\s\-]','',ph.group(0))[:10]
        px = re.search(r'(\d+)\s*(?:ท่าน|คน)', t)
        if px and not pax: pax = px.group(1) + ' ท่าน'
        tot = re.search(r'(?:รวม|ยอด)\D{0,5}([\d,]+)\s*บาท', t)
        if tot and not total: total = tot.group(1).replace(',','') + ' บาท'
        dep = re.search(r'ครึ่งนึงคือ\s*([\d,.]+)\s*บาท', t)
        if dep and not deposit:
            d = math.ceil(float(dep.group(1).replace(',','')))
            deposit = str(d) + ' บาท'
        if m['role'] == 'assistant' and ('ขอชื่อ' in t or ('ชื่อ' in t and 'เบอร์' in t)):
            if i+1 < len(history) and history[i+1]['role'] == 'user':
                ans = history[i+1]['content'].strip()
                for p in ans.split():
                    if len(p) >= 2 and not re.match(r'^\d+$', p) and not name:
                        name = p
                ph2 = re.search(r'0\d[\d\s\-]{8,}', ans)
                if ph2 and not phone: phone = re.sub(r'[\s\-]','',ph2.group(0))[:10]

    lines = ['🔔 <b>แจ้งเตือนออเดอร์ใหม่ — มัจฉา ปลาจุ่ม</b>']
    lines.append('💰 ต้องมัดจำ 50%' if is_deposit else '✅ จองปกติ')
    lines.append('')
    if time_val: lines.append(f'🕐 เวลา: {time_val} น. (วันนี้)')
    if pax:      lines.append(f'👥 จำนวน: {pax}')
    if name:     lines.append(f'👤 ชื่อ: {name}')
    if phone:    lines.append(f'📞 เบอร์: {phone}')
    if total:    lines.append(f'💵 ยอดรวม: {total}')
    if is_deposit and deposit: lines.append(f'💰 มัดจำ 50%: {deposit}')
    if is_deposit: lines.append('⚠️ รอส่ง QR ให้ลูกค้าทาง chat')
    return '\n'.join(lines)

def send_message_fb(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    try:
        r = requests.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }, timeout=10)
        print(f"FB send: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"FB send error: {e}")

def get_ai_reply(user_id, user_text):
    if user_id not in user_sessions:
        user_sessions[user_id] = {"history": [], "booking_mode": False}
    session = user_sessions[user_id]

    if not session["booking_mode"] and is_booking_intent(user_text):
        session["booking_mode"] = True

    session["history"].append({"role": "user", "content": user_text})
    system_prompt = BOOKING_PROMPT if session["booking_mode"] else GENERAL_PROMPT

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=system_prompt,
            messages=session["history"][-20:]
        )
        reply = response.content[0].text
    except Exception as e:
        print(f"Anthropic error: {e}")
        return "ขออภัยค่ะ ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้งนะคะ 🙏"

    session["history"].append({"role": "assistant", "content": reply})

    is_deposit = '[BOOKING_COMPLETE_DEPOSIT]' in reply
    is_complete = '[BOOKING_COMPLETE]' in reply or is_deposit

    if is_complete and session["booking_mode"]:
        clean_reply = reply.replace('[BOOKING_COMPLETE_DEPOSIT]','').replace('[BOOKING_COMPLETE]','').strip()
        summary = build_telegram_summary(session["history"], is_deposit)
        send_telegram(summary)
        session["booking_mode"] = False
        return clean_reply

    return reply

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                sender_id = event['sender']['id']
                if 'message' in event and 'text' in event['message']:
                    user_text = event['message']['text']
                    reply = get_ai_reply(sender_id, user_text)
                    send_message_fb(sender_id, reply)
    except Exception as e:
        print(f"Webhook error: {e}")
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
