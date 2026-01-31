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
import streamlit as st
from datetime import datetime, timedelta

# --- 🌐 1. ปรับปรุงพจนานุกรมภาษา (Language Control) ---
LANG_DATA = {
    "Thai": {
        "travel_info": "🗓️ รายละเอียดการเดินทาง",
        "start_date": "วันที่เริ่มต้น",
        "end_date": "วันที่สิ้นสุด",
        "activity_label": "กิจกรรมที่วางแผนไว้",
        "activities": ["ท่องเที่ยวทั่วไป", "ติดต่อธุรกิจ", "กิจกรรมกลางแจ้ง/เดินป่า", "งานเลี้ยง/ดินเนอร์", "ไปทะเล"],
        "upload_section": "📸 จัดการรูปภาพชุดแต่งกาย",
        "theme_label": "โหมดแสดงผล (มืด/สว่าง)",
        "lang_label": "เลือกภาษา (Language)",
        "run_btn": "✨ เริ่มวิเคราะห์การแต่งกาย",
        "settings": "⚙️ ตั้งค่าระบบ"
    },
    "English": {
        "travel_info": "🗓️ Travel Itinerary",
        "start_date": "Start Date",
        "end_date": "End Date",
        "activity_label": "Planned Activities",
        "activities": ["General Sightseeing", "Business Trip", "Outdoor/Hiking", "Dinner/Party", "Beach Trip"],
        "upload_section": "📸 Outfit Management",
        "theme_label": "Display Mode (Dark/Light)",
        "lang_label": "Language Selection",
        "run_btn": "✨ Start Analysis",
        "settings": "⚙️ System Settings"
    }
}

def main_dashboard():
    # ดึงค่าภาษาปัจจุบัน
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # --- 🌓 2. ปรับโหมดมืดให้สมดุล (Soft Dark Mode) ---
    with st.sidebar:
        st.subheader(t["settings"])
        # ส่วนควบคุมภาษา
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        
        st.divider()
        dark_mode = st.toggle(t["theme_label"], value=False)
        
        if dark_mode:
            # ใช้สีโทน Slate/Navy แทนสีดำสนิท เพื่อให้มองเห็นองค์ประกอบชัดเจน
            st.markdown("""
                <style>
                .stApp { background-color: #0f172a; color: #f8fafc; }
                [data-testid="stSidebar"] { background-color: #1e293b; }
                .stSelectbox label, .stDateInput label, .stRadio label, p { color: #e2e8f0 !important; }
                .stButton button { background-color: #334155; border: 1px solid #475569; }
                div[data-testid="stExpander"] { background-color: #1e293b; border: 1px solid #334155; }
                </style>
            """, unsafe_allow_html=True)

    # --- 🗓️ 3. ปรับส่วนรายละเอียดการเดินทาง (เพิ่มวันไป-กลับ และ กิจกรรม) ---
    st.title("🌍 Tripnify Dashboard")
    
    col1, col2 = st.columns([1, 1.4])
    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            
            # วันเริ่มต้น - วันสิ้นสุด
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                start = st.date_input(t["start_date"], datetime.now())
            with d_col2:
                end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            
            # เพิ่มส่วนกิจกรรม
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            
            st.divider()
            
            # ส่วนจัดการรูปภาพ (อัพโหลด/ถ่ายรูป เหมือนเดิม)
            st.subheader(t["upload_section"])
            tabs = st.tabs(["📁 คลังภาพ", "📸 ถ่ายภาพ"])
            with tabs[0]:
                img = st.file_uploader("", type=['jpg','png','jpeg'], key="dash_upload")
            with tabs[1]:
                cam = st.camera_input("")
            
            st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        st.info("ส่วนแสดงผล 3D และผลการวิเคราะห์จะปรากฏในส่วนนี้")
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            
            # ส่วนการจัดการรูปภาพ (อัพโหลด + ถ่ายรูป)
            st.write(f"**{t['upload_tab']}**")
            input_tab1, input_tab2 = st.tabs(["📁 คลังภาพ", "📸 กล้องถ่ายรูป"])
            
            with input_tab1:
                img_file = st.file_uploader("เลือกไฟล์ภาพจากเครื่อง", type=['jpg', 'png', 'jpeg'])
            with input_tab2:
                cam_file = st.camera_input("ถ่ายรูปชุดของคุณ")
            
            # รวมไฟล์ภาพจากทั้ง 2 ช่องทาง
            active_img = img_file if img_file else cam_file
            
            if st.button(t["run_btn"], use_container_width=True, type="primary"):
                if active_img:
                    st.success("รับข้อมูลภาพเรียบร้อย กำลังเริ่มวิเคราะห์...")
                else:
                    st.warning("กรุณาอัพโหลดรูปหรือถ่ายภาพก่อนเริ่มวิเคราะห์")

# --- 🔑 2. หน้า Login (ปรับโลโก้กึ่งกลางสมดุล) ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    st.markdown("""<style>
        .header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            width: 100%;
            padding: 30px 0;
        }
        .social-btn-custom {
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: -45px;
            background: white;
            position: relative;
            z-index: 1;
            pointer-events: none;
            width: 100%;
        }
        .social-icon { width: 20px; margin-right: 12px; }
        .social-text { font-weight: 500; font-size: 14px; }
    </style>""", unsafe_allow_html=True)

    # จัดโลโก้และชื่อแบรนด์กึ่งกลาง (ตัดคำว่าเข้าสู่ระบบออก)
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
        st.markdown("""<div class="social-btn-custom">
            <img class="social-icon" src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg">
            <span class="social-text" style="color: #1877F2;">เข้าสู่ระบบด้วย Facebook</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="fb_btn", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        # Google
        st.markdown("""<div class="social-btn-custom">
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

# --- 🚀 3. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state:
    st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
