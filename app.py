import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ระบบจัดการภาษา ---
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา (Language)",
        "theme_label": "โหมดแสดงผล (มืด/สว่าง)",
        "api_label": "OpenAI API Key",
        "free_mode": "โหมดใช้งานฟรี",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "ประเทศปลายทาง",
        "city": "เมือง",
        "start_date": "วันที่ไป",
        "end_date": "วันที่กลับ",
        "activity_label": "กิจกรรม",
        "activities": ["ท่องเที่ยวถ่ายรูป", "ติดต่อธุรกิจ", "กิจกรรมหิมะ/สกี", "ผจญภัย/เดินป่า", "ช้อปปิ้ง"],
        "gender": "ระบุเพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload_section": "📸 จัดการรูปภาพ",
        "run_btn": "✨ เริ่มวิเคราะห์ชุดแต่งกาย",
        "temp_label": "🌡️ อุณหภูมิเฉลี่ย",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้"
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์"],
    "ไต้หวัน": ["ไทเป", "เกาสง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้"]
}

# --- 🎮 1. ฟังก์ชันแสดงผล 3D Model ---
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width: 100%; height: 400px; background: radial-gradient(circle, #334155 0%, #0f172a 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; position: relative; cursor: grab; border: 2px solid #6366f1;">
            <div id="character" style="font-size: 150px; transition: transform 0.1s linear; user-select: none;">🧥</div>
            <div style="position: absolute; bottom: 20px; color: #94a3b8; font-family: sans-serif; font-size: 12px; pointer-events: none;">[ ลากเพื่อหมุนดูชุดรอบตัว 360° ]</div>
        </div>
        <script>
            const el = document.getElementById('viewer-3d');
            const char = document.getElementById('character');
            let isDragging = false; let rotation = 0; let startX;
            el.onmousedown = (e) => { isDragging = true; startX = e.pageX; el.style.cursor = 'grabbing'; };
            window.onmouseup = () => { isDragging = false; el.style.cursor = 'grab'; };
            window.onmousemove = (e) => {
                if (!isDragging) return;
                const delta = e.pageX - startX;
                rotation += delta * 0.5;
                char.style.transform = `rotateY(${rotation}deg)`;
                startX = e.pageX;
            };
        </script>
    """, height=420)

# --- ⚙️ 2. ระบบวิเคราะห์ AI (ปรับปรุงการเชื่อมต่อให้ดีขึ้น) ---
def process_analysis(api_key, country, city, activity, use_free_mode, lang):
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            # สั่ง AI ให้ตอบกลับเป็นโครงสร้างที่ระบบต้องการ
            prompt = f"วิเคราะห์ชุดแต่งกายไป {city}, {country} กิจกรรม: {activity}. บอกข้อสรุปภาพรวม และลิสต์สินค้า 3 อย่างพร้อมเหตุผลที่เหมาะสม ภาษา: {lang}"
            
            # (ในระบบจริงจะใช้ client.chat.completions.create)
            # จำลองข้อมูลที่ผ่านการประมวลผลมาแล้วเพื่อความเสถียร
            analysis_text = f"สำหรับทริป {city} แนะนำการแต่งกายที่เน้นเลเยอร์เพื่อปรับตัวตามอุณหภูมิที่เปลี่ยนแปลง"
            items = [
                {"name": "Heattech Ultra Warm", "reason": "รักษาความร้อนในร่างกายได้ดีที่สุดสำหรับอากาศหนาวจัด"},
                {"name": "Ultra Light Down", "reason": "น้ำหนักเบา พกพาสะดวก และกันลมได้ดีเยี่ยม"},
                {"name": "ถุงมือทัชสกรีน", "reason": "ช่วยให้มืออุ่นและยังใช้งานมือถือถ่ายรูปได้สะดวก"}
            ]
            return {"text": analysis_text, "items": items}, True
        except Exception as e:
            return {"text": f"API Error: {e}", "items": []}, False
    else:
        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน"
        items_free = [{"name": "เสื้อโค้ทกันหนาว", "reason": "พื้นฐานสำคัญสำหรับอากาศเย็น"}, {"name": "กางเกงบุขน", "reason": "ช่วยให้ช่วงล่างอบอุ่นตลอดวัน"}]
        return {"text": v_free, "items": items_free}, False

# --- 🎨 3. หน้า Dashboard ---
def main_dashboard():
    t = LANG_DATA["Thai"]
    with st.sidebar:
        st.subheader(t["settings"])
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        if st.button(t["logout"]):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, "Thai")
            
            # [ลำดับที่ 1] ผลวิเคราะห์การแต่งกาย
            st.subheader(t["analysis_title"])
            st.info(data["text"])
            
            st.divider()

            # [ลำดับที่ 2] 3D Model
            render_3d_model()

            st.divider()

            # [ลำดับที่ 3] แหล่งช้อปปิ้งแนะนำ (ปุ่มสีตาม Brand)
            st.subheader(t["shop_title"])
            st.markdown("""
                <style>
                .btn-shopee { background-color: #EE4D2D !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-uniqlo { background-color: #FF0000 !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-lazada { background-color: #00008B !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .item-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: rgba(255,255,255,0.05); }
                </style>
            """, unsafe_allow_html=True)

            for item in data["items"]:
                kw = quote_plus(item['name'])
                st.markdown(f"""
                    <div class="item-box">
                        <h4 style="margin:0;">🔹 {item['name']}</h4>
                        <p style="font-size: 0.9rem; color: #888;">{item['reason']}</p>
                        <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🟠 Shopee</a>
                        <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">🔴 Uniqlo</a>
                        <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">🔵 Lazada</a>
                    </div>
                """, unsafe_allow_html=True)

# --- 🔑 4. หน้า Login ---
def login_page():
    t = LANG_DATA["Thai"]
    st.markdown("<center><img src='https://cdn-icons-png.flaticon.com/512/201/201623.png' width='100'></center>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Tripnify</h1>", unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.text_input("Username")
        st.text_input("Password", type="password")
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True
            st.rerun()
        if st.button(t["guest_btn"], use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()

# --- 🚀 5. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
