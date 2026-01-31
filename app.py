import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ระบบจัดการภาษาแบบสมบูรณ์ ---
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ การตั้งค่าระบบ",
        "lang_label": "ภาษาที่ใช้งาน (Language)",
        "api_label": "OpenAI API Key (สำหรับโหมดพรีเมียม)",
        "free_mode": "เปิดใช้งานโหมดฟรี (จำกัดฟีเจอร์)",
        "theme_label": "โหมดแสดงผล (มืด/สว่าง)",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ รายละเอียดการเดินทาง",
        "dest": "ประเทศปลายทาง",
        "city": "เมืองที่ต้องการไป",
        "start": "วันที่เริ่มต้น",
        "end": "วันที่สิ้นสุด",
        "activity": "ประเภทกิจกรรม",
        "gender": "ระบุเพศ",
        "upload_tab": "📸 อัปโหลดรูปภาพ",
        "camera_tab": "🤳 ถ่ายภาพชุด",
        "run_btn": "✨ เริ่มขั้นตอนวิเคราะห์และสร้าง 3D",
        "login_title": "เข้าสู่ระบบ Tripnify",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "guest_btn": "👤 ทดลองใช้งานฟรี",
        "reg_btn": "📝 ลงทะเบียนบัญชีใหม่",
        "login_btn": "🔑 เข้าสู่ระบบ"
    },
    "English": {
        "settings": "⚙️ System Settings",
        "lang_label": "Language",
        "api_label": "OpenAI API Key (Premium Mode)",
        "free_mode": "Use Free Mode (Limited Features)",
        "theme_label": "Display Mode (Dark/Light)",
        "logout": "Sign Out",
        "travel_info": "🗓️ Travel Details",
        "dest": "Destination Country",
        "city": "Select City",
        "start": "Start Date",
        "end": "End Date",
        "activity": "Activity Type",
        "gender": "Gender",
        "upload_tab": "📸 Upload Image",
        "camera_tab": "🤳 Take Photo",
        "run_btn": "✨ Start Analysis & 3D Render",
        "login_title": "Sign in to Tripnify",
        "login_sub": "Smart Outfit Analysis System for Travelers",
        "guest_btn": "👤 Try Guest Mode",
        "reg_btn": "📝 Register New Account",
        "login_btn": "🔑 Sign In"
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
    # ตรวจสอบภาษาปัจจุบัน
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        # ส่วนปรับภาษาที่รองรับทั้ง 2 โหมด
        st.radio("Select Language / เลือกภาษา", ["Thai", "English"], key='lang_choice', horizontal=True)
        
        st.divider()
        # ปรับปรุงส่วน OpenAI API Key
        api_key = st.text_input(t["api_label"], type="password", help="กรอก API Key จาก OpenAI เพื่อใช้งานระบบวิเคราะห์ขั้นสูงและ 3D")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        
        theme_mode = st.toggle(t["theme_label"], value=False)
        if theme_mode:
            st.markdown("""<style>
                .stApp { background-color: #0F172A; color: #FFFFFF; }
                .stMarkdown, p, h1, h2, h3, label { color: #F1F5F9 !important; }
                [data-testid="stSidebar"] { background-color: #1E293B; }
            </style>""", unsafe_allow_html=True)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title(f"🌍 Tripnify Dashboard")
    
    col1, col2 = st.columns([1, 1.4])
    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input(t["start"], datetime.now())
            end_date = d_col2.date_input(t["end"], datetime.now() + timedelta(days=5))
            
            gender = st.radio(t["gender"], ["Male/ชาย", "Female/หญิง"], horizontal=True)
            
            tabs = st.tabs([t["upload_tab"], t["camera_tab"]])
            with tabs[0]: img_file = st.file_uploader("", type=['jpg', 'png'])
            with tabs[1]: cam_file = st.camera_input("")
            
            st.button(t["run_btn"], use_container_width=True, type="primary")

# --- 🔑 2. หน้า Login ---
def login_page():
    # ใช้ภาษาจาก session state (ค่าเริ่มต้นคือไทย)
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # แก้ไขบรรทัดที่ 105-110 (โดยประมาณ)
st.markdown("<br>", unsafe_allow_html=True)
col_logo, col_mid, col_logo2 = st.columns([1, 1, 1])
with col_mid:
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=120)

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.markdown(f"<h1>{t['login_title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: gray;'>{t['login_sub']}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=100)
    st.markdown(f"<h1>{t['login_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: gray;'>{t['login_sub']}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
       with c2:
    # ปุ่ม Facebook ภาษาไทย
    st.markdown(f"""<div class="social-btn">
        <img class="social-icon" src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg">
        <span style="color: #1877F2; font-weight: bold;">เข้าสู่ระบบด้วย Facebook</span>
    </div>""", unsafe_allow_html=True)
    if st.button("Facebook Login", key="fb_hidden", label_visibility="collapsed", use_container_width=True): 
        st.session_state['logged_in'] = True; st.rerun()

    # ปุ่ม Google ภาษาไทย
    st.markdown(f"""<div class="social-btn">
        <img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png">
        <span style="color: #5F6368; font-weight: bold;">เข้าสู่ระบบด้วย Google</span>
    </div>""", unsafe_allow_html=True)
    if st.button("Google Login", key="google_hidden", label_visibility="collapsed", use_container_width=True): 
        st.session_state['logged_in'] = True; st.rerun()
        # Google Login Button
        st.markdown(f"""<div class="social-btn">
            <img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png">
            <span style="color: #5F6368; font-weight: bold;">Continue with Google</span>
        </div>""", unsafe_allow_html=True)
        if st.button("Google Login", key="google_hidden", help="เข้าสู่ระบบผ่าน Google", use_container_width=True): 
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        
        user = st.text_input("Username / ชื่อผู้ใช้งาน")
        pwd = st.text_input("Password / รหัสผ่าน", type="password")
        
        st.button(t["login_btn"], use_container_width=True, type="primary")
        
        # ส่วนที่เพิ่ม: ลงทะเบียน และ ทดลองใช้ฟรี
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            if st.button(t["reg_btn"], use_container_width=True): st.info("ระบบลงทะเบียนจะเปิดให้ใช้งานเร็วๆ นี้")
        with col_sub2:
            if st.button(t["guest_btn"], use_container_width=True):
                st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 3. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state:
    st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
