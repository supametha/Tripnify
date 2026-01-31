import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ข้อมูลพื้นฐาน ---
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
        "upload_section": "📸 จัดการรูปภาพ",
        "run_btn": "✨ เริ่มวิเคราะห์ชุดแต่งกาย",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "3d_title": "🎭 3D Outfit Character Preview",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำตามคำแนะนำ",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้"
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
        "upload_section": "📸 Image Management",
        "run_btn": "✨ Start Analysis",
        "analysis_title": "🔍 Outfit Analysis",
        "3d_title": "🎭 3D Outfit Character Preview",
        "shop_title": "🛍️ Recommended Shopping",
        "login_sub": "Smart Outfit Analysis for Your Trip",
        "login_btn": "🔑 Login",
        "reg_btn": "📝 Register",
        "guest_btn": "👤 Guest"
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
def render_3d_model(title):
    st.subheader(title)
    components.html("""
        <div id="viewer-3d" style="width: 100%; height: 350px; background: radial-gradient(circle, #334155 0%, #0f172a 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; position: relative; cursor: grab; border: 2px solid #6366f1;">
            <div id="character" style="font-size: 120px; transition: transform 0.1s linear; user-select: none;">🧥</div>
            <div style="position: absolute; bottom: 20px; color: #94a3b8; font-family: sans-serif; font-size: 12px; pointer-events: none;">
                [ ลากเพื่อหมุนตัวละคร 360° ]
            </div>
        </div>
        <script>
            const el = document.getElementById('viewer-3d');
            const char = document.getElementById('character');
            let isDragging = false; let rotation = 0; let startX;
            el.onmousedown = (e) => { isDragging = true; startX = e.pageX; };
            window.onmouseup = () => { isDragging = false; };
            window.onmousemove = (e) => {
                if (!isDragging) return;
                const delta = e.pageX - startX;
                rotation += delta * 0.5;
                char.style.transform = `rotateY(${rotation}deg)`;
                startX = e.pageX;
            };
        </script>
    """, height=380)

# --- ⚙️ 2. ระบบวิเคราะห์ Logic ---
def get_analysis_data(api_key, city, activity, use_free_mode, lang):
    # จำลองข้อมูลที่ AI จะส่งมา (ในใช้งานจริงจะ parse จาก OpenAI Response)
    if not use_free_mode and api_key:
        return {
            "text": f"สำหรับเมือง {city} และกิจกรรม {activity} แนะนำให้สวมใส่เสื้อโค้ทกันลมหนาพิเศษ เนื่องจากอุณหภูมิต่ำ และควรมีเลเยอร์ด้านในเป็น Heattech เพื่อรักษาความอบอุ่น",
            "items": [
                {"name": "Ultra Light Down Jacket", "reason": "น้ำหนักเบาแต่กันหนาวได้ดีเยี่ยม เหมาะกับการเดินทางที่ต้องเคลื่อนที่บ่อย"},
                {"name": "Heattech Ultra Warm", "reason": "ช่วยเก็บกักความร้อนจากร่างกายได้ดีที่สุดในสภาพอากาศเลขตัวเดียว"},
                {"name": "ถุงมือกันลม Touchscreen", "reason": "จำเป็นสำหรับการใช้งานมือถือถ่ายรูปท่ามกลางอากาศเย็น"}
            ]
        }
    else:
        return {
            "text": "แนะนำการแต่งกายแบบ Layering (3 ชั้น) เพื่อปรับตัวตามสภาพอากาศที่เปลี่ยนแปลงได้ง่าย",
            "items": [
                {"name": "เสื้อกันหนาวมีฮู้ด", "reason": "พื้นฐานสำหรับการกันลมและเพิ่มความอบอุ่นส่วนหัว"},
                {"name": "กางเกงขายาวผ้าหนา", "reason": "ป้องกันความเย็นเข้าสู่ร่างกายส่วนล่าง"}
            ]
        }

# --- 🎨 3. หน้า Dashboard ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        dark_mode = st.toggle(t["theme_label"], value=False)
        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            d_col1, d_col2 = st.columns(2)
            start = d_col1.date_input(t["start_date"], datetime.now())
            end = d_col2.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            data = get_analysis_data(api_key, city, activity, use_free_mode, current_lang)
            
            # A. ผลวิเคราะห์การแต่งกาย (ขึ้นก่อน)
            st.subheader(t["analysis_title"])
            st.info(data["text"])

            # B. 3D Outfit Preview
            render_3d_model(t["3d_title"])

            # C. แหล่งช้อปปิ้งแนะนำ (ดึงจากคำแนะนำ AI)
            st.divider()
            st.subheader(t["shop_title"])
            
            for item in data["items"]:
                with st.expander(f"🔹 {item['name']}"):
                    st.write(f"**ทำไมถึงแนะนำ:** {item['reason']}")
                    st.write("**เลือกซื้อได้ที่:**")
                    
                    # Store Icons & Links
                    s_col1, s_col2, s_col3 = st.columns(3)
                    kw = quote_plus(item['name'])
                    
                    with s_col1:
                        st.markdown(f'[![Shopee](https://img.icons8.com/color/48/shopee.png)](https://shopee.co.th/search?keyword={kw})  \n[Shopee](https://shopee.co.th/search?keyword={kw})', unsafe_allow_html=True)
                    with s_col2:
                        # Uniqlo ใช้โลโก้แทน
                        st.markdown(f'[![Uniqlo](https://img.icons8.com/color/48/u.png)](https://www.uniqlo.com/th/th/search/?q={kw})  \n[Uniqlo](https://www.uniqlo.com/th/th/search/?q={kw})', unsafe_allow_html=True)
                    with s_col3:
                        st.markdown(f'[![Lazada](https://img.icons8.com/color/48/lazada.png)](https://www.lazada.co.th/catalog/?q={kw})  \n[Lazada](https://www.lazada.co.th/catalog/?q={kw})', unsafe_allow_html=True)
        else:
            st.info("👈 กรอกข้อมูลการเดินทางและรูปภาพเพื่อเริ่มการวิเคราะห์")

# --- 🔑 4. หน้า Login (คงเดิม) ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]
    st.markdown("""<style>.header-container { text-align: center; padding: 30px 0; }</style>""", unsafe_allow_html=True)
    st.markdown(f'<div class="header-container"><img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="100"><h1>Tripnify</h1><p>{t["login_sub"]}</p></div>', unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        if st.button(t["login_btn"], use_container_width=True, type="primary"): st.session_state['logged_in'] = True; st.rerun()
        if st.button(t["guest_btn"], use_container_width=True): st.session_state['logged_in'] = True; st.rerun()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state: st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']: main_dashboard()
else: login_page()
