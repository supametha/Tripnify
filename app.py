import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ข้อมูลระบบ ---
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา",
        "theme_label": "โหมดแสดงผล",
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
    },
    "English": {
        "settings": "⚙️ System Settings",
        "lang_label": "Language",
        "theme_label": "Theme",
        "api_label": "OpenAI API Key",
        "free_mode": "Free Mode",
        "logout": "Log Out",
        "travel_info": "🗓️ Travel Info",
        "dest": "Destination",
        "city": "City",
        "start_date": "Departure",
        "end_date": "Return",
        "activity_label": "Activities",
        "activities": ["Photography", "Business", "Ski/Snow", "Hiking/Adventure", "Shopping"],
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "upload_section": "📸 Image Management",
        "run_btn": "✨ Start Analysis",
        "temp_label": "🌡️ Avg Temp",
        "analysis_title": "🔍 Outfit Analysis",
        "shop_title": "🛍️ Recommended Shopping",
        "login_sub": "Smart Outfit Analysis for Your Trip",
        "login_btn": "🔑 Login",
        "reg_btn": "Register",
        "guest_btn": "Guest"
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์"],
    "ไต้หวัน": ["ไทเป", "เกาสง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้"]
}

# --- 🎮 1. 3D Model Render ---
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

# --- ⚙️ 2. AI Logic ---
def process_analysis(api_key, country, city, activity, use_free_mode, lang):
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"Analyze winter outfit for {city}, {country}. Activity: {activity}. Return analysis and 3 specific items with reasons in {lang}."
            # หมายเหตุ: ในโค้ดจริงจะมีการเรียก ChatCompletion ที่นี่
            # นี่คือตัวอย่างผลลัพธ์ที่สกัดออกมา
            analysis_text = f"สภาพอากาศที่ {city} มีความหนาวเย็นและลมแรง แนะนำการแต่งกายแบบ 3 ชั้น (Layering) เพื่อรักษาอุณหภูมิ"
            items = [
                {"name": "Ultra Warm Heattech", "reason": "ช่วยเก็บกักความร้อนจากร่างกายเป็นชั้นแรก (Base Layer) ได้ดีเยี่ยม"},
                {"name": "Seamless Down Parka", "reason": "กันลมและกันละอองน้ำได้ดี เหมาะกับกิจกรรมกลางแจ้ง"},
                {"name": "Heattech Gloves", "reason": "ช่วยให้ปลายนิ้วอุ่นตลอดเวลาขณะเดินเที่ยวหรือถ่ายรูป"}
            ]
            return {"text": analysis_text, "items": items}, True
        except Exception as e:
            return {"text": f"Error: {e}", "items": []}, False
    else:
        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน"
        items_free = [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "พื้นฐานสำคัญสำหรับกันความหนาว"},
            {"name": "ถุงมือบุขน", "reason": "ป้องกันภาวะนิ้วแข็งจากอากาศเย็น"}
        ]
        return {"text": v_free, "items": items_free}, False

# --- 🎨 3. Dashboard ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            start = st.date_input(t["start_date"], datetime.now())
            end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            st.session_state['gender_val'] = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            active_img = st.camera_input("")
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, current_lang)
            
            # --- จัดลำดับใหม่ตามสั่ง ---
            # 1. ผลวิเคราะห์
            st.subheader(t["analysis_title"])
            st.info(data["text"])
            
            st.divider()

            # 2. 3D Model
            render_3d_model()

            st.divider()

            # 3. แหล่งช้อปปิ้ง (ปุ่มสีตามแบรนด์)
            st.subheader(t["shop_title"])
            st.markdown("""
                <style>
                .btn-shopee { background-color: #EE4D2D !important; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-right: 5px; display: inline-block; }
                .btn-uniqlo { background-color: #FF0000 !important; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-right: 5px; display: inline-block; }
                .btn-lazada { background-color: #101566 !important; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; }
                .shop-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
                </style>
            """, unsafe_allow_html=True)

            for item in data["items"]:
                kw = quote_plus(item['name'])
                st.markdown(f"""
                <div class="shop-card">
                    <strong>🔹 {item['name']}</strong><br>
                    <small style="color: gray;">เหตุผล: {item['reason']}</small><br><br>
                    <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🧡 Shopee</a>
                    <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">❤️ Uniqlo</a>
                    <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">💙 Lazada</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์")

# --- 🔑 4. Login Page ---
def login_page():
    t = LANG_DATA[st.session_state.get('lang_choice', 'Thai')]
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

# --- 🚀 5. Main Control ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
