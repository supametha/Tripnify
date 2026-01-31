import streamlit as st
import base64
from datetime import datetime, timedelta

# --- 🌐 0. ระบบจัดการภาษา (Unified Language Control) ---
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

# --- 🎨 1. หน้า Dashboard ---
def main_dashboard():
    # ควบคุมภาษา
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # --- 🌓 Sidebar & Theme Control ---
    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        
        dark_mode = st.toggle(t["theme_label"], value=False)
        if dark_mode:
            # Soft Dark Mode (Slate Blue Theme)
            st.markdown("""
                <style>
                .stApp { background-color: #0f172a; color: #f8fafc; }
                [data-testid="stSidebar"] { background-color: #1e293b; }
                .stSelectbox label, .stDateInput label, .stRadio label, .stMultiSelect label, p, h1, h2, h3 { color: #e2e8f0 !important; }
                .stButton button { background-color: #334155 !important; border: 1px solid #475569 !important; color: white !important; }
                div[data-testid="stExpander"] { background-color: #1e293b; border: 1px solid #334155; }
                /* ปรับสี Metric และ Warning ให้เห็นชัดในโหมดมืด */
                [data-testid="stMetricValue"] { color: #38bdf8 !important; }
                .stAlert { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; }
                </style>
            """, unsafe_allow_html=True)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- 🗓️ Main Content ---
    st.title("🌍 Tripnify Dashboard")
    
    col1, col2 = st.columns([1, 1.4])
    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            
            # 1. ปรับเพิ่มวันไป-กลับ
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                start = st.date_input(t["start_date"], datetime.now())
            with d_col2:
                end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            
            # 2. ปรับเพิ่มกิจกรรม (เลือกได้หลายอย่าง)
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            
            st.divider()
            
            # 3. ส่วนจัดการรูปภาพ (Tabs อัพโหลด/ถ่ายรูป)
            st.subheader(t["upload_section"])
            tabs = st.tabs(["📁 คลังภาพ", "📸 ถ่ายภาพ"])
            with tabs[0]:
                img_file = st.file_uploader("", type=['jpg','png','jpeg'], key="dash_up")
            with tabs[1]:
                cam_file = st.camera_input("")
            
            active_img = img_file if img_file else cam_file
            
            if st.button(t["run_btn"], use_container_width=True, type="primary"):
                if active_img:
                    st.success("รับข้อมูลสำเร็จ กำลังวิเคราะห์ชุดแต่งกายของคุณ...")
                else:
                    st.warning("กรุณาเลือกรูปภาพหรือถ่ายภาพก่อนเริ่ม")

    with col2:
        st.info("💡 ส่วนนี้จะแสดงผลการวิเคราะห์ AI และโมเดลตัวละคร 3D ของคุณ")

# --- 🔑 2. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    st.markdown("""<style>
        .header-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; padding: 30px 0; }
        .social-btn-custom { display: flex; align-items: center; justify-content: center; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -45px; background: white; position: relative; z-index: 1; pointer-events: none; width: 100%; }
        .social-icon { width: 20px; margin-right: 12px; }
        .social-text { font-weight: 500; font-size: 14px; }
    </style>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="header-container">
            <img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="140">
            <h1 style='margin-top: 15px; font-size: 3.5rem; font-weight: bold;'>Tripnify</h1>
            <p style='color: gray; font-size: 1.2rem; margin-top: -15px;'>{t['login_sub']}</p>
        </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        # Facebook
        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg">
            <span class="social-text" style="color: #1877F2;">เข้าสู่ระบบด้วย Facebook</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="fb_btn", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        # Google
        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png">
            <span class="social-text" style="color: #5F6368;">เข้าสู่ระบบด้วย Google</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="google_btn", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown("<hr style='margin-top: 25px; opacity: 0.3;'>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Username")
        pwd = st.text_input("Password", type="password", placeholder="Password")
        
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True; st.rerun()

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1: st.button(t["reg_btn"], use_container_width=True)
        with col_sub2:
            if st.button(t["guest_btn"], use_container_width=True):
                st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 3. Main Controller ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state:
    st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
