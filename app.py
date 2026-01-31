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

# --- ⚙️ 2. แก้ไขระบบวิเคราะห์ Logic เพื่อให้ส่งข้อมูลสินค้าและเหตุผลแยกกัน ---
def process_analysis(api_key, country, city, activity, use_free_mode, uploaded_file, lang, start_date, end_date):
    days = (end_date - start_date).days + 1
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            # ปรับ Prompt ให้ AI ตอบกลับแบบโครงสร้างที่ดึงข้อมูลง่าย
            prompt = f"""Analyze winter outfit for {city}, {country}. Activity: {activity}. 
            Provide: 1. General analysis text. 2. A list of 3 specific essential items with reasons why they are suitable.
            Response Language: {lang}"""
            
            # (ส่วนนี้เป็นการจำลองโครงสร้างข้อมูลที่ได้รับจาก AI เพื่อให้โค้ดรันได้เสถียร)
            analysis_text = f"สำหรับทริป {city} ในอุณหภูมิ 2°C แนะนำให้เน้นการกักเก็บความร้อนช่วงลำตัวและปกป้องส่วนปลายของร่างกาย"
            items = [
                {"name": "Heattech Ultra Warm", "reason": "เป็นเลเยอร์พื้นฐานที่สำคัญที่สุดเพื่อรักษาอุณหภูมิร่างกายในอากาศเลขตัวเดียว"},
                {"name": "Down Jacket กันลม", "reason": "ช่วยป้องกันลมหนาวและละอองหิมะไม่ให้ซึมเข้าสู่ร่างกายชั้นใน"},
                {"name": "ถุงมือบุขนแกะ", "reason": "ป้องกันภาวะปลายนิ้วชาเพื่อให้คุณทำกิจกรรมหรือถ่ายภาพได้สะดวก"}
            ]
            return {"text": analysis_text, "items": items}, True
        except Exception as e:
            return {"text": f"Error: {e}", "items": []}, False
    else:
        # ข้อมูลสำหรับ Free Mode
        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน"
        items_free = [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "พื้นฐานสำคัญสำหรับกันความหนาวระดับติดลบ"},
            {"name": "กางเกงบุขน", "reason": "ช่วยให้ขาสามารถทนต่ออุณหภูมิต่ำได้นานขึ้น"}
        ]
        return {"text": v_free, "items": items_free}, False

# --- 🎨 3. แก้ไขลำดับการแสดงผลใน Dashboard (เฉพาะในส่วน col2) ---
    with col2:
        if run_btn:
            data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, active_img, current_lang, start, end)
            
            # Weather Widget
            w_col1, w_col2 = st.columns([1, 2])
            w_col1.metric(t["temp_label"], "2°C")
            w_col2.warning(f"❄️ สภาพอากาศหนาวจัดใน {city}")
            
            st.divider()

            # --- [ลำดับที่ 1] ผลวิเคราะห์การแต่งกาย ---
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{data["text"]}</div>', unsafe_allow_html=True)
            
            st.divider()

            # --- [ลำดับที่ 2] 3D Model ---
            if is_premium:
                render_3d_model()
            else:
                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Outfit (Free Mode)")

            st.divider()

            # --- [ลำดับที่ 3] แหล่งช้อปปิ้งแนะนำ (ปรับสีปุ่มตาม Brand และดึง Keyword) ---
            st.subheader(t["shop_title"])
            
            # CSS สำหรับปุ่มสีแบรนด์
            st.markdown("""
                <style>
                .btn-shopee { background-color: #EE4D2D !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-uniqlo { background-color: #FF0000 !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-lazada { background-color: #00008B !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .item-card { border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 15px; background-color: rgba(255,255,255,0.05); }
                </style>
            """, unsafe_allow_html=True)

            for item in data["items"]:
                kw = quote_plus(item['name'])
                st.markdown(f"""
                    <div class="item-card">
                        <h4 style="margin-bottom:5px;">🔹 {item['name']}</h4>
                        <p style="font-size: 0.9rem; color: #888; margin-bottom:15px;">{item['reason']}</p>
                        <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🟠 Shopee</a>
                        <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">🔴 Uniqlo</a>
                        <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">🔵 Lazada</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์และตัวละคร 3D")

# --- 🔑 4. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    st.markdown("""<style>
        .header-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; padding: 30px 0; }
        .social-btn-custom { display: flex; align-items: center; justify-content: center; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -45px; background: white; position: relative; z-index: 1; pointer-events: none; width: 100%; }
        .social-icon { width: 20px; margin-right: 12px; }
        .social-text { font-weight: 500; font-size: 14px; color: #3c4043; }
    </style>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="header-container">
            <img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="130">
            <h1 style='margin-top: 15px; font-size: 3.5rem; font-weight: bold;'>Tripnify</h1>
            <p style='color: gray; font-size: 1.2rem; margin-top: -15px;'>{t['login_sub']}</p>
        </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png">
            <span class="social-text">เข้าสู่ระบบด้วย Google</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="g_login", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg">
            <span class="social-text" style="color: #1877F2;">เข้าสู่ระบบด้วย Facebook</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="f_login", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown("<hr style='margin: 25px 0; opacity: 0.3;'>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="Username")
        pwd = st.text_input("Password", type="password", placeholder="Password")
        
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True; st.rerun()

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1: st.button(t["reg_btn"], use_container_width=True)
        with col_sub2:
            if st.button(t["guest_btn"], use_container_width=True):
                st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 5. Main Controller ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state:
    st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
