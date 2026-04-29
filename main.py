import os
import re
import math
import time
import requests
import threading
from flask import Flask, request, jsonify
from anthropic import Anthropic

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

PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KNOWLEDGE_BASE = """
ร้านมัจฉา ปลาจุ่ม:
เวลาเปิด: 11:00-22:00 น. | หยุด: วันจันทร์
ที่ตั้ง: ระหว่างกาดมีโชค-เซ็นทรัลเฟสติวัล เชียงใหม่ แถวรวมโชค ติดถนนใหญ่
โทร: 052-005-581 หรือ 081-751-4044
บริการ: ทานที่ร้าน Takeout Delivery จองโต๊ะล่วงหน้า
ไม่มีบริการส่งถึงบ้าน ถ้าต้องการส่งให้เรียก Grab Food หรือ Grab Delivery มารับเอง
Google Maps: https://maps.app.goo.gl/ZY884ugFrGCJXmoD6
ที่จอดรถ: จอดข้างทางหน้าร้านได้เลย หรือจอดด้านหลังแล้วเดินทะลุตรง 7-11 ข้างร้าน
รีวิว: https://www.google.com/maps/place/มัจฉา+ปลาจุ่ม

โปรโมชั่นพิเศษ:
- โปรวันเกิด: ลด 10% (ต้องแจ้งล่วงหน้าและแสดงหลักฐานวันเกิด)

เมนูแนะนำ ★: ปลาจุ่มปลาช่อน 279 | ปลาจุ่มปลากะพง 399 | ไก่ผัดมะม่วงหิมพานต์ 169 | ปลาหมึกผัดไข่เค็ม 189 | ปลากะพงทอดน้ำปลา 399 | ผัดผักโขมห่อไข่เค็มเบรกแตก 129
เมนูลิงก์: https://canva.link/8vshw4aq9lahpgk
"""

MENU_FULL = """
**เมนูแนะนำ**
- ปลาจุ่มซิกเนเจอร์-ปลาช่อน — 279
- ปลาจุ่มพรีเมียม-ปลากะพง — 399
- ไก่ผัดมะม่วงหิมพานต์ — 169
- ปลาหมึกผัดไข่เค็ม — 189
- ปลากะพงทอดน้ำปลา — 399
- ผัดผักโขมห่อไข่เค็มเบรกแตก — 129

**เมนูผัด**
- ผัดพริกแกงปลาหมึก — 189
- ผัดพริกแกงกุ้ง — 189
- ปลาเกาผัดฉ่า — 299
- เห็ดสามอย่างกระเทียมโทนในน้ำมันงาไทย — 149
- ปลากะพงผัดฉ่า — 399
- ปลาช่อนผัดฉ่า — 299
- ยอดมะระผัดไข่ทรงเครื่อง — 149
- หน่อไม้ฝรั่งผัดกุ้ง — 169
- หมี่ผัดกระเฉดแบบโบราณ — 169
- หมูผัดพริกไทยดำ — 159
- เนื้อผัดพริกไทยดำ — 189
- ปูก้อนผัดใบโหระพา — 289
- ถั่วลันเตาผัดกุ้ง — 169
- กุ้งคั่วพริกเกลือ — 259
- เขียวหวานคั่วกลิ้งกุ้ง — 259

**เมนูนึ่ง**
- ปลากะพงนึ่งซีอิ๊ว — 399
- แป๊ะซะปลาช่อน — 299
- แป๊ะซะปลากะพง — 399

**เมนูทอด**
- ปีกไก่ทอดน้ำปลา — 189
- หมูทอดกระเทียม — 169
- ปลากะพงราดพริก — 399
- ปลากะพงทอดกระเทียม — 399
- ปลาช่อนราดพริก — 299
- ปลาช่อนทอดกระเทียม — 299
- ปีกไก่ยัดไส้สมุนไพรทอดกรอบ — 159
- ไข่เจียวปูก้อน — 349
- ไข่เจียว — 89
- ไข่เจียวหมูสับ — 109
- ไข่เจียวปู — 189
- หมูสามชั้นทอดงาขาวราดซอสมะขาม — 169
- กุ้งแม่น้ำทอดราดซอสมะขาม — 259
- ซี่โครงหมูทอดเคลือบน้ำปลากวนผักชีทอดกรอบ — 169
- หมูทอดนมสด — 139

**เมนูต้ม-แกง**
- ต้มยำกุ้งแม่น้ำน้ำใส — 299
- ต้มยำกุ้งแม่น้ำน้ำใสหม้อใหญ่ — 399
- ต้มยำกุ้งแม่น้ำน้ำข้น — 299
- ต้มยำกุ้งแม่น้ำน้ำข้นหม้อใหญ่ — 399
- ต้มยำรวมมิตรทะเล — 299
- โป๊ะแตก — 299
- แกงเขียวหวานลูกชิ้นปลากรายใบมะกรูด — 189
- แกงเขียวหวานเนื้อน่องลาย — 259
- ต้มข่าหัวปลีมะพร้าวอ่อน — 149
- ต้มจืดไข่เจียวหมูสับ — 159
- ต้มจืดสาหร่ายลูกชิ้นปลา — 139
- แกงส้มชะอมทอดใส่กุ้ง — 259
- หมึกน้ำดำ — 399

**อาหารทานเล่น**
- กุ้งแช่น้ำปลา — 189
- เต้าหู้ปลาไส้กุ้งทอด — 169
- ทอดมันปลา + ปูทอด — 169
- ทอดมันปลา + กุ้งทอด — 169
- ทอดมันปลาอินทรีย์ล้วน — 169
- ทอดมันปลาหมึก — 169
- กุ้งชุปแป้งทอด — 159
- เกี๊ยวปลาโบราณ — 169
- หมึกไข่แดดเดียว — 189
- เต้าหู้ไส้ปลาหมึกทอด — 139
- ปอเปี๊ยะเห็ดหอม — 149
- จ๊อปู — 169
- เฟรนช์ฟรายส์ทอด — 89
- ทอดมันกุ้งโดนัท — 169
- ถุงทองกุ้ง — 169
- ปอเปี๊ยะกุ้ง — 189

**เมนูยำ**
- ยำตะไคร้สองกุ้งน้ำพริก — 169
- ยำตะไคร้กุ้งแห้งมะพร้าวคั่ว — 129
- ยำทะเลแตก — 189
- ยำวุ้นเส้นสูตรโบราณ — 149
- ยำหัวปลีไข่เค็ม — 129
- ยำส้มโอโบราณ — 129
- ยำปลาทูใส่ถั่วพลู — 129

**อาหารจานเดียว**
- ข้าวผัดโบราณหมู/ไก่ — 89
- ข้าวผัดเขียวหวานหมู/ไก่ — 89
- ข้าวผัดเขียวหวานเนื้อ — 129
- ข้าวผัดเขียวหวานกุ้ง — 139
- ข้าวผัดกุ้ง/ปู — 129
- ข้าวผัดพริกแกงไก่ — 98
- ข้าวราดกะเพราหมู — 89
- ข้าวราดกระเพราปลาหมึก — 119
- ข้าวราดกะเพรากุ้ง — 129
- ข้าวหมูกระเทียม — 89
- ก๋วยเตี๋ยวคั่วไก่ — 89
- ผัดไทยกุ้งสด — 99
- วุ้นเส้นผัดไทยกุ้งสด — 99
- ราดหน้าเส้นใหญ่หมูหมัก — 99
- ราดหน้าหมี่ขาวหมูหมัก — 99
- ผัดซีอิ๋วหมูหมักเส้นใหญ่ — 89
- ข้าวผัดพริกแกงทะเล — 139
- ข้าวราดพริกแกงหมู/ไก่ — 98

**ของหวาน**
- กล้วยไข่บวชชี — 79
- บัวลอยสามสี — 69
- ทับทิมกรอบมะพร้าวอ่อน — 79
- เต้าทึงร้อน — 69
- บัวลอยน้ำขิง — 79
- บัวลอยเผือก — 69
- สาคูถั่วดำมะพร้าวอ่อน — 79

**เครื่องดื่ม**
- น้ำเก๊กฮวย — 59
- น้ำตะไคร้หอม — 59
- น้ำอัญชันมะนาว — 59
- น้ำมะตูม — 59
- น้ำลำไย — 59
- น้ำกระเจี๊ยบ — 59
- น้ำเสาวรส — 59
- น้ำมะนาวน้ำผึ้ง — 59
- น้ำมะขาม — 59
- โค้ก/โค้กซีโร่ — 20
- รีเจนซี่ — 490
- เบียร์ไฮเนเก้น — 110
- เบียร์สิงห์ — 100
- เบียร์ช้าง — 85
- เบียร์ลีโอ — 90
- โซดา — 20
- น้ำเปล่า — 15
- น้ำแข็งเล็ก — 20
- น้ำแข็งใหญ่ — 30
"""

# ========== PROMPTS ==========
# สำคัญ: ทั้ง 2 prompt มี KNOWLEDGE_BASE ครบ เพื่อป้องกัน hallucinate ข้อมูลพื้นฐาน

GENERAL_PROMPT = f"""คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" ตอบแชท Facebook แบบคนพิมจริงๆ

กฎ:
- ตอบสั้น 1-2 ประโยคเท่านั้น
- ถ้าแสดงรายการเมนู: ใช้ • นำหน้าแต่ละรายการ ขึ้นบรรทัดใหม่ทีละเมนู ลงท้ายด้วย link เมนู
- ถ้าลูกค้าถามเมนู ให้นำเมนูอย่างละ 2-3 อย่างในแต่ละหมวดหมู่โดยไม่ต้องให้เมนูของหวานและน้ำ และปิดท้ายด้วย https://canva.link/8vshw4aq9lahpgk ดูเมนูทั้งหมด
- emoji แค่ 1 ตัว ลงท้าย ค่ะ หรือ นะคะ
- ถ้าขอดูเมนู: ส่ง link เมนู แล้วถามว่า "สนใจจองเลยมั้ยคะ ช่วงเย็นคนจะแน่นนิดนึงค่ะ?"
- ถ้าถามที่อยู่/เส้นทาง/จอดรถ: บอกสั้นๆ + Maps link แล้วถามว่า "จะจองโต๊ะไว้ก่อนได้เลยนะคะเดี๋ยวมาถึงที่เต็มก่อน มากี่ท่านคะ?"
- ถ้าถามราคา/เมนูใดเมนูหนึ่ง: ตอบราคาแล้วถามต่อว่า "จองโต๊ะไว้ก่อนได้เลยนะคะ 😊"
- ถ้าถามเวลาเปิด/ปิด/วันหยุด: ตอบแล้วถามว่า "จะมาช่วงไหนคะ? จองไว้ก่อนได้เลยนะคะ"
- ถ้าถามโปร/ส่วนลด: มีโปรวันเกิดลด 10%
- ถ้าลูกค้าบอกว่าจะมากิน/อยากมาทาน: ถามว่าจะจองโต๊ะไว้ก่อนมั้ยคะ
- ถ้าถามส่งบ้าน: ทางร้านไม่มีบริการส่ง แนะนำ Grab Food หรือให้มารับได้เลยค่ะ
- ถ้าไม่รู้/ไม่มีข้อมูล: บอกว่าไม่แน่ใจค่ะ แล้วให้โทรถามได้เลยที่ 052-005-581 หรือ 081-751-4044 นะคะ
- ห้ามให้เบอร์โทรร้านโดยเด็ดขาด ยกเว้นลูกค้าถามเองว่าโทรได้มั้ย หรือเข้ากรณีไม่รู้จริงๆ
- ตอบภาษาเดียวกับที่ลูกค้าใช้ ถ้าลูกค้าพิมไทยตอบไทย ถ้าพิมอังกฤษตอบอังกฤษ

ข้อมูลร้าน:
{KNOWLEDGE_BASE}
"""

BOOKING_PROMPT = f"""คุณคือแอดมินร้าน "มัจฉา ปลาจุ่ม" รับสั่งอาหารล่วงหน้าและจองโต๊ะผ่าน Facebook

ข้อมูลที่ต้องแม่นยำ 100%:
- เวลาเปิด: 11:00-22:00 น. ทุกวัน (ยกเว้นวันจันทร์หยุด)
- ห้ามตอบเวลาอื่นโดยเด็ดขาด ไม่ว่ากรณีใดๆ

ข้อมูลสำคัญ:
- ไม่มีบริการส่งถึงบ้าน ถ้าลูกค้าอยากให้ส่งแนะนำ Grab Food มารับได้เลย หรือสั่งแล้วเข้ามารับเองก็ได้ค่ะ
- มัดจำเฉพาะสั่งล่วงหน้าและยอดเกิน 1,000 บาทเท่านั้น
- โปรวันเกิด: ลด 10% ต้องแจ้งล่วงหน้าและแสดงหลักฐานวันเกิด
- ถ้ามีโปร ให้หัก 10% ก่อนคำนวณยอดรวมเสมอ
- ลูกค้าสามารถนำเครื่องดื่นแอลกอฮอเข้ามาได้ เบียร์ ไวน์ เหล้า นำเข้ามาได้ไม่เสียค่าเปิดขวด ฟรี

กฎการเขียน:
- ถ้าแสดงรายการเมนู: ใช้ • นำหน้าแต่ละรายการ ขึ้นบรรทัดใหม่ทีละเมนู
- พิมสั้น เป็นกันเอง emoji 1 ตัว ห้ามใช้ **bold**
- ห้ามบอกให้โทรยืนยัน ห้ามบอกเบอร์โทรร้าน
- ถ้าไม่บอกวัน = วันนี้ ห้ามถามวันซ้ำ
- ตอบภาษาเดียวกับที่ลูกค้าใช้ ถ้าลูกค้าพิมไทยตอบไทย ถ้าพิมอังกฤษตอบอังกฤษ

== กรณีสั่งอาหารล่วงหน้า ==
ขั้น 1: รับรายการเมนู
ขั้น 2: คำนวณราคารวมในใจทันที
ขั้น 3: ถามเวลา (ถ้าบอกแล้ว ข้าม ถ้าไม่บอกวัน = วันนี้)
ขั้น 4 (ห้ามข้าม): เช็กยอดรวม
  - ยอด > 1,000: ถาม "มัดจำก่อนครึ่งนึงได้เลยนะคะ ถ้าใกล้ถึงเวลาจะทำให้ก่อนเลยค่ะ" รอคำตอบ
    * ตกลง: คำนวณ ยอดรวม ÷ 2 ปัดขึ้น (เช่น 1326÷2=663, 1469÷2=735) บอก "ครึ่งนึงคือ X บาทนะคะ เดี๋ยวส่ง QR ให้ทาง chat นะคะ" ปิดด้วย [BOOKING_COMPLETE_DEPOSIT]
    * ไม่มัดจำ: ถามชื่อและเบอร์ → ปิดด้วย [BOOKING_COMPLETE]
  - ยอด ≤ 1,000: ถามชื่อและเบอร์ → ปิดด้วย [BOOKING_COMPLETE]
  (ห้ามพูดถึงมัดจำเลยถ้ายอดไม่ถึง 1,000)
ขั้น 5: ปิดด้วย tag เสมอ ห้ามปิดโดยไม่ผ่านขั้น 4

== กรณีจองโต๊ะ ==
ขั้น 1: กี่โมง (ถ้าบอกแล้ว ข้าม ไม่บอกวัน = วันนี้)
ขั้น 2: กี่ท่าน (ถ้าบอกแล้ว ข้าม)
ขั้น 3: ขอชื่อและเบอร์ ปิดด้วย [BOOKING_COMPLETE]

ราคาเมนูทั้งหมด:
{MENU_FULL}

ข้อมูลร้าน:
{KNOWLEDGE_BASE}
"""

# Session storage พร้อม TTL 24 ชม.
SESSION_TTL = 2 * 60 * 60 
user_sessions = {}

# Booking keywords — เฉพาะ intent จองจริงๆ เอา trigger ที่ false positive ออก
BOOKING_KEYWORDS = [
    'จอง','จองโต๊ะ','จองที่','book','reserve','ขอจอง','อยากจอง',
    'สั่งล่วงหน้า','สั่งอาหารล่วงหน้า','preorder','pre-order','ล่วงหน้า',
    'อยากมากิน','อยากเข้าไปกิน','จะมากิน','จะไปกิน','อยากไปกิน',
    'มาทาน','ไปทาน','อยากมาทาน','จะมาทาน',
    'สั่งชุด','สั่ง','ขอสั่ง','อยากสั่ง',
]

def is_booking_intent(text):
    return any(k in text for k in BOOKING_KEYWORDS)

def get_session(user_id):
    now = time.time()
    expired = [uid for uid, s in user_sessions.items() if now - s.get("last_active", 0) > SESSION_TTL]
    for uid in expired:
        del user_sessions[uid]
    if user_id not in user_sessions:
        user_sessions[user_id] = {"history": [], "booking_mode": False, "last_active": now}
    else:
        user_sessions[user_id]["last_active"] = now
    return user_sessions[user_id]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=5)
        if not resp.ok:
            print(f"Telegram error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Telegram exception: {e}")

def build_telegram_summary(history, is_deposit):
    name = phone = time_val = pax = items = total = deposit = ''
    for i, m in enumerate(history):
        t = m['content']

        tm = re.search(r'(\d{1,2})\s*(?:โมง|นาฬิกา|:[0-5]\d)', t)
        if tm and not time_val:
            time_val = tm.group(0).strip()

        if m['role'] == 'user':
            ph = re.search(r'0\d[\d\s\-]{8,10}', t)
            if ph and not phone:
                phone = re.sub(r'[\s\-]', '', ph.group(0))[:10]

        px = re.search(r'(\d+)\s*(?:ท่าน|คน)', t)
        if px and not pax:
            pax = px.group(1) + ' ท่าน'

        tot = re.search(r'(?:รวม|ยอด|ทั้งหมด|คิดเป็น)\D{0,8}([1-9][\d,]{2,})\s*บาท', t)
        if not tot:
            tot = re.search(r'([1-9][\d,]{3,})\s*บาท', t)
        if tot and not total:
            total = tot.group(1).replace(',', '') + ' บาท'

        dep = re.search(r'ครึ่งนึงคือ\s*([\d,.]+)\s*บาท', t)
        if dep and not deposit:
            d = math.ceil(float(dep.group(1).replace(',', '')))
            deposit = str(d) + ' บาท'

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

        if m['role'] == 'assistant' and not items:
            pipe = re.search(
                r'[\u0E00-\u0E7Fa-zA-Z][\u0E00-\u0E7Fa-zA-Z\s]+\d+(?:\s*\|\s*[\u0E00-\u0E7Fa-zA-Z][\u0E00-\u0E7Fa-zA-Z\s]+\d+){1,}',
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
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    try:
        resp = requests.post(url, json={
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }, timeout=5)
        if not resp.ok:
            print(f"FB send error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"FB send exception: {e}")

def get_ai_reply(user_id, user_text):
    session = get_session(user_id)

    if not session["booking_mode"] and is_booking_intent(user_text):
        session["booking_mode"] = True

    session["history"].append({"role": "user", "content": user_text})
    system_prompt = BOOKING_PROMPT if session["booking_mode"] else GENERAL_PROMPT

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            system=system_prompt,
            messages=session["history"][-20:]
        )
        reply = response.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        return "ขอโทษนะคะ ตอนนี้ระบบขัดข้องชั่วคราว ลองใหม่อีกครั้งได้เลยค่ะ 🙏"

    session["history"].append({"role": "assistant", "content": reply})

    is_deposit = '[BOOKING_COMPLETE_DEPOSIT]' in reply
    is_complete = '[BOOKING_COMPLETE]' in reply or is_deposit

    if is_complete and session["booking_mode"]:
        clean_reply = reply.replace('[BOOKING_COMPLETE_DEPOSIT]', '').replace('[BOOKING_COMPLETE]', '').strip()
        summary = build_telegram_summary(session["history"], is_deposit)
        send_telegram(summary)
        session["booking_mode"] = False
        return clean_reply

    return reply

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Forbidden', 403

def reply_to_comment(comment_id, message):
    url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    try:
        resp = requests.post(url, json={
            "message": message,
            "access_token": PAGE_ACCESS_TOKEN
        }, timeout=5)
        if not resp.ok:
            print(f"Comment reply error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Comment reply exception: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            return 'OK', 200

        for entry in data.get('entry', []):
            # handle DM
            for event in entry.get('messaging', []):
                try:
                    sender_id = event.get('sender', {}).get('id')
                    if not sender_id:
                        continue
                    msg = event.get('message', {})
                    if not msg or msg.get('is_echo'):
                        continue
                    user_text = msg.get('text', '').strip()
                    if not user_text:
                        continue
                    reply = get_ai_reply(sender_id, user_text)
                    send_message_fb(sender_id, reply)
                except Exception as e:
                    print(f"Event processing error: {e}")
                    continue

            # handle comments
            for change in entry.get('changes', []):
                try:
                    value = change.get('value', {})
                    if change.get('field') != 'feed':
                        continue
                    if value.get('item') != 'comment':
                        continue
                    if value.get('verb') != 'add':
                        continue
                    if value.get('from', {}).get('id') == entry.get('id'):
                        continue
                    comment_id = value.get('comment_id')
                    comment_text = value.get('message', '').strip()
                    commenter_id = value.get('from', {}).get('id', 'unknown')
                    if not comment_id or not comment_text:
                        continue
                    reply = get_ai_reply(f"comment_{commenter_id}", comment_text)
                    reply_to_comment(comment_id, reply)
                except Exception as e:
                    print(f"Comment processing error: {e}")
                    continue

    except Exception as e:
        print(f"Webhook error: {e}")

    return 'OK', 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "sessions": len(user_sessions)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
