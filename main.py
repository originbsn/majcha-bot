import os
import math
import requests
from flask import Flask, request
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "majcha2024")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8793240457:AAF1Zr0Aws7tdzM-H1VRHB5q3E9ufZBKaxU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5146262487")

KNOWLEDGE_BASE = """
ร้านมัจฉา ปลาจุ่ม:
เวลาเปิด: 11:00-22:00 น. | หยุด: วันจันทร์
ที่ตั้ง: ระหว่างกาดมีโชค-เซ็นทรัลเฟสติวัล เชียงใหม่ แถวรวมโชค ติดถนนใหญ่
โทร: 052-005-581 หรือ 081-751-4044
บริการ: ทานที่ร้าน Takeout Delivery จองโต๊ะล่วงหน้า คนละครึ่ง
ไม่มีบริการส่งถึงบ้าน ถ้าต้องการส่งให้เรียก Grab Food หรือ Grab Delivery มารับเอง
Google Maps: https://maps.app.goo.gl/ZY884ugFrGCJXmoD6
รีวิว: https://www.google.com/maps/place/มัจฉา+ปลาจุ่ม

ชุดเซ็ต (ราคาพิเศษ ไม่ใช่โปรโมชัน):
- ชุดสุขใจ 419 บาท (1-2 ท่าน): ปลาจุ่มปลาช่อน + ยำหัวปลีไข่เค็ม + ข้าวสวย
- ชุดอิ่มสุข 909 บาท ★ขายดี (2-3 ท่าน): ปลาจุ่มปลากะพง + ไข่เจียวปูก้อน + ผัดพริกแกงปลาหมึก + ข้าวสวย
- ชุดเลี้ยงครอบครัว 1,469 บาท (4-6 ท่าน): ปลาจุ่มปลากะพง + กุ้งแม่น้ำทอดราดซอสมะขาม + ต้มยำกุ้งหม้อใหญ่ + ปูก้อนผัดใบโหระพา + ยำวุ้นเส้น + ข้าวสวย 2 โถ

เมนูแนะนำ ★: ปลาจุ่มปลาช่อน 279 | ปลาจุ่มปลากะพง 399 | ไก่ผัดมะม่วงหิมพานต์ 169 | ปลาหมึกผัดไข่เค็ม 189 | ปลากะพงทอดน้ำปลา 399 | ผัดผักโขมห่อไข่เค็มเบรกแตก 129
เมนูลิงก์: https://www.canva.com/design/DAGv3CnDsgM/view
"""

GENERAL_PROMPT = f"""คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" ตอบแชท Facebook แบบคนพิมจริงๆ

กฎ:
- ตอบสั้น 1-2 ประโยคเท่านั้น
- ห้ามใช้ ** bullet numbered list ทุกรูปแบบ ถ้าจะแสดงรายการให้คั่นด้วย |
- emoji แค่ 1 ตัว ลงท้าย ค่ะ หรือ นะคะ
- ถ้าขอดูเมนู: ส่ง link เมนู
- ถ้าถามที่อยู่: บอกสั้นๆ + Maps link
- ถ้าถามโปร/ส่วนลด: ตอบว่าไม่มีโปร แต่มีชุดเซ็ตราคาพิเศษ
- ถ้าถามส่งบ้าน: ทางร้านไม่มีบริการส่ง แนะนำ Grab Food มารับได้เลยค่ะ
- ถ้าลูกค้าบอกว่าจะมากิน/อยากมาทาน: ถามว่าจะจองโต๊ะไว้ก่อนมั้ยคะ
- ถ้าไม่รู้: ไม่แน่ใจค่ะ ลองถามทาง chat ได้เลยนะคะ (ห้ามให้เบอร์โทร)
- ห้ามให้เบอร์โทรร้านโดยเด็ดขาด ยกเว้นลูกค้าถามเองว่าโทรได้มั้ย

ข้อมูลร้าน:
{KNOWLEDGE_BASE}
"""

BOOKING_PROMPT = """คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" รับสั่งอาหารล่วงหน้าและจองโต๊ะผ่าน Facebook

ข้อมูลสำคัญ:
- ไม่มีบริการส่งถึงบ้าน ถ้าลูกค้าอยากส่งให้แนะนำ Grab Food มารับได้เลย
- มัดจำเฉพาะสั่งล่วงหน้าและยอดเกิน 1,000 บาทเท่านั้น

ราคาเมนู:
ชุดสุขใจ 419 | ชุดอิ่มสุข 909 | ชุดเลี้ยงครอบครัว 1469
ปลาจุ่มปลาช่อน 279 | ปลาจุ่มปลากะพง 399 | ไก่ผัดมะม่วงหิมพานต์ 169 | ปลาหมึกผัดไข่เค็ม 189 | ปลากะพงทอดน้ำปลา 399 | ผัดผักโขมห่อไข่เค็มเบรกแตก 129 | ผัดพริกแกงปลาหมึก 189 | ปลาเก๋าผัดฉ่า 299 | หน่อไม้ฝรั่งผัดกุ้ง 169 | หมี่ผัดกระเฉด 169 | ปูก้อนผัดใบโหระพา 289 | ปลากะพงนึ่งซีอิ๊ว 399 | แป๊ะซะปลากะพง 399 | ปีกไก่ทอดน้ำปลา 189 | ปลากะพงราดพริก 399 | ปลาช่อนราดพริก 299 | ปีกไก่ยัดไส้สมุนไพร 159 | ไข่เจียวปูก้อน 349 | ไข่เจียวปู 189 | หมูสามชั้นทอดงาขาว 169 | กุ้งแม่น้ำทอดราดซอสมะขาม 259 | ซี่โครงหมูทอด 169 | ต้มยำกุ้งน้ำข้น 299 | ต้มยำกุ้งน้ำข้นหม้อใหญ่ 399 | โป๊ะแตก 299 | แกงเขียวหวานเนื้อ 259 | หมึกน้ำดำ 399 | ทอดมันปลา+ปูทอด 169 | กุ้งชุปแป้งทอด 159 | เกี๊ยวปลาโบราณ 169 | จ๊อปู 169 | ทอดมันกุ้งโดนัท 169 | ถุงทองกุ้ง 169 | ยำวุ้นเส้น 149 | ยำหัวปลีไข่เค็ม 129

กฎการเขียน:
- ห้ามใช้ numbered list หรือ bullet ทุกกรณี คั่นด้วย | เท่านั้น
- พิมสั้น เป็นกันเอง emoji 1 ตัว ห้ามใช้ **bold**
- ห้ามบอกให้โทรยืนยัน ห้ามบอกเบอร์โทรร้าน
- ถ้าไม่บอกวัน = วันนี้ ห้ามถามวันซ้ำ

== กรณีสั่งอาหารล่วงหน้า ==
ขั้น 1: รับรายการเมนู
ขั้น 2: คำนวณราคารวมในใจทันที
ขั้น 3: ถามเวลา (ถ้าบอกแล้ว ข้าม ถ้าไม่บอกวัน = วันนี้)
ขั้น 4 (ห้ามข้าม): เช็กยอดรวม
  - ยอด > 1,000: ถาม "มัดจำก่อนครึ่งนึงได้เลยนะคะ ถ้าใกล้ถึงเวลาจะทำให้ก่อนเลยค่ะ" รอคำตอบ
    * ตกลง: คำนวณครึ่งแล้วปัดขึ้นเป็นจำนวนเต็ม บอก "ครึ่งนึงคือ X บาทนะคะ เดี๋ยวส่ง QR ให้ทาง chat นะคะ" ปิดด้วย [BOOKING_COMPLETE_DEPOSIT]
    * ไม่มัดจำ: ปิดด้วย [BOOKING_COMPLETE]
  - ยอด ≤ 1,000: ถามชื่อ ปิดด้วย [BOOKING_COMPLETE]
ขั้น 5: ปิดด้วย tag เสมอ ห้ามปิดโดยไม่ผ่านขั้น 4

== กรณีจองโต๊ะ ==
ขั้น 1: กี่โมง (ถ้าบอกแล้ว ข้าม ไม่บอกวัน = วันนี้)
ขั้น 2: กี่ท่าน (ถ้าบอกแล้ว ข้าม)
ขั้น 3: ขอชื่อและเบอร์ ปิดด้วย [BOOKING_COMPLETE]
"""

# เก็บประวัติแชทและ booking mode ต่อ user
user_sessions = {}

BOOKING_KEYWORDS = [
    'จอง','จองโต๊ะ','จองที่','book','reserve','ขอจอง','อยากจอง',
    'สั่งล่วงหน้า','สั่งอาหารล่วงหน้า','preorder','pre-order','ล่วงหน้า',
    'อยากมากิน','อยากเข้าไปกิน','จะมากิน','จะไปกิน','อยากไปกิน',
    'มาทาน','ไปทาน','อยากมาทาน','จะมาทาน',
    'สั่งชุด','ชุดสุขใจ','ชุดอิ่มสุข','ชุดเลี้ยงครอบครัว','ชุดเซ็ต',
    'สั่ง','ขอสั่ง','อยากสั่ง'
]

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
    name = phone = time_val = pax = items = total = deposit = ''
    for i, m in enumerate(history):
        t = m['content']
        import re
        # เวลา
        tm = re.search(r'(\d{1,2})\s*(?:โมง|นาฬิกา|:[0-5]\d)', t)
        if tm and not time_val: time_val = tm.group(0).strip()
        # เบอร์ (จาก user)
        if m['role'] == 'user':
            ph = re.search(r'0\d[\d\s\-]{8,10}', t)
            if ph and not phone: phone = re.sub(r'[\s\-]','',ph.group(0))[:10]
        # จำนวนคน
        px = re.search(r'(\d+)\s*(?:ท่าน|คน)', t)
        if px and not pax: pax = px.group(1) + ' ท่าน'
        # ยอดรวม
        tot = re.search(r'(?:รวม|ยอด)\D{0,5}([\d,]+)\s*บาท', t)
        if tot and not total: total = tot.group(1).replace(',','') + ' บาท'
        # มัดจำ
        dep = re.search(r'ครึ่งนึงคือ\s*([\d,.]+)\s*บาท', t)
        if dep and not deposit:
            d = math.ceil(float(dep.group(1).replace(',','')))
            deposit = str(d) + ' บาท'
        # ชื่อ
        if m['role'] == 'assistant' and ('ขอชื่อ' in t or ('ชื่อ' in t and 'เบอร์' in t)):
            if i+1 < len(history) and history[i+1]['role'] == 'user':
                ans = history[i+1]['content'].strip()
                parts = ans.split()
                for p in parts:
                    if len(p) >= 2 and not re.match(r'^\d+$', p) and not name:
                        name = p
                ph2 = re.search(r'0\d[\d\s\-]{8,}', ans)
                if ph2 and not phone: phone = re.sub(r'[\s\-]','',ph2.group(0))[:10]
        # เมนู (จาก bot message ที่มี |)
        if m['role'] == 'assistant' and not items:
            pipe = re.search(r'[\u0E00-\u0E7Fa-zA-Z][\u0E00-\u0E7Fa-zA-Z\s]+\d+(?:\s*\|\s*[\u0E00-\u0E7Fa-zA-Z][\u0E00-\u0E7Fa-zA-Z\s]+\d+){1,}', t)
            if pipe: items = pipe.group(0)[:200]

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
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    })

def get_ai_reply(user_id, user_text):
    if user_id not in user_sessions:
        user_sessions[user_id] = {"history": [], "booking_mode": False}
    session = user_sessions[user_id]

    if not session["booking_mode"] and is_booking_intent(user_text):
        session["booking_mode"] = True

    session["history"].append({"role": "user", "content": user_text})
    system_prompt = BOOKING_PROMPT if session["booking_mode"] else GENERAL_PROMPT

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=system_prompt,
        messages=session["history"][-20:]
    )
    reply = response.content[0].text
    session["history"].append({"role": "assistant", "content": reply})

    # ตรวจ booking complete
    is_deposit = '[BOOKING_COMPLETE_DEPOSIT]' in reply
    is_complete = '[BOOKING_COMPLETE]' in reply or is_deposit

    if is_complete and session["booking_mode"]:
        clean_reply = reply.replace('[BOOKING_COMPLETE_DEPOSIT]','').replace('[BOOKING_COMPLETE]','').strip()
        summary = build_telegram_summary(session["history"], is_deposit)
        send_telegram(summary)
        session["booking_mode"] = False
        return clean_reply

    return reply

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
    data = request.json
    for entry in data.get('entry', []):
        for event in entry.get('messaging', []):
            sender_id = event['sender']['id']
            if 'message' in event and 'text' in event['message']:
                user_text = event['message']['text']
                reply = get_ai_reply(sender_id, user_text)
                send_message_fb(sender_id, reply)
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
