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
        "guest_btn": "👤 ทดลองใช้",
        "essentials": ["เสื้อโค้ทกันหนาว", "กางเกงบุขน", "ถุงมือกันหนาว", "แผ่นแปะความร้อน"]
    },
    "English": {
        "settings": "⚙️ System Settings",
        "lang_label": "Language",
        "theme_label": "Display Mode (Dark/Light)",
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
        "reg_btn": "📝 Register",
        "guest_btn": "👤 Guest",
        "essentials": ["Winter Coat", "Fleece Pants", "Winter Gloves", "Heat Packs"]
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์"],
    "ไต้หวัน": ["ไทเป", "เกาสง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้"]
}

# --- 🎮 1. ฟังก์ชันแสดงผล 3D Model (Premium) ---
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width: 100%; height: 400px; background: radial-gradient(circle, #334155 0%, #0f172a 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; position: relative; cursor: grab; border: 2px solid #6366f1;">
            <div id="character" style="font-size: 150px; transition: transform 0.1s linear; user-select: none;">🧥</div>
            <div style="position: absolute; bottom: 20px; color: #94a3b8; font-family: sans-serif; font-size: 12px; pointer-events: none;">
                [ ลากเพื่อหมุนดูชุดรอบตัว 360° ]
            </div>
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

# --- ⚙️ 2. ระบบวิเคราะห์ Logic ---
def process_analysis(api_key, country, city, activity, use_free_mode, uploaded_file, lang, start_date, end_date):
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"Analyze outfit for {city}, {country}. Activity: {activity}. Response in {lang}."
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                )
                return response.choices[0].message.content, True
            return "กรุณาอัปโหลดรูปภาพ", False
        except Exception as e:
            return f"Error: {e}", False
    else:
        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน" if lang == "Thai" else "Layering recommended: Heattech, Sweater, and Down Jacket."
        return v_free, False

# --- 🔑 3. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]
    st.markdown("""<style>
        .header-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; padding: 20px 0; }
        .social-btn-custom { display: flex; align-items: center; justify-content: center; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -45px; background: white; position: relative; z-index: 1; pointer-events: none; width: 100%; }
        .social-icon { width: 20px; margin-right: 12px; }
    </style>""", unsafe_allow_html=True)
    st.markdown(f'<div class="header-container"><img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="100"><h1>Tripnify</h1><p>{t["login_sub"]}</p></div>', unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        st.markdown(f'<div class="social-btn-custom"><img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"><span style="color:#5F6368;">Continue with Google</span></div>', unsafe_allow_html=True)
        if st.button("", key="g_btn", use_container_width=True): st.session_state['logged_in'] = True; st.rerun()
        st.write("")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button(t["login_btn"], use_container_width=True, type="primary"): st.session_state['logged_in'] = True; st.rerun()
        if st.button(t["guest_btn"], use_container_width=True): st.session_state['logged_in'] = True; st.rerun()

# --- 🎨 4. หน้า Dashboard ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]
    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        if st.button(t["logout"], use_container_width=True): st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])
    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            st.divider()
            img_file = st.file_uploader(t["upload_section"], type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            result, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, img_file, current_lang, None, None)
            if is_premium: render_3d_model()
            else: st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Outfit")
            st.markdown(f"### {t['analysis_title']}")
            st.info(result)
            st.subheader(t["shop_title"])
            for item in t["essentials"]:
                st.markdown(f"🔹 {item} | [🛒 Shopee](https://shopee.co.th/search?keyword={quote_plus(item)})")
        else:
            st.info("👈 กรอกข้อมูลแล้วกดเริ่มวิเคราะห์")

# --- 🚀 5. Main Controller ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
