import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ข้อมูลเมืองตามประเทศ ---
CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด", "ฟุกุโอกะ"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "อินชอน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์", "ดานัง"],
    "ไต้หวัน": ["ไทเป", "เกาสง", "ไถจง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้", "กวางโจว"]
}

LANG_DICT = {
    "Thai": {
        "settings": "⚙️ ตั้งค่า",
        "lang_label": "เลือกภาษา",
        "free_mode": "โหมดใช้งานฟรี",
        "theme_label": "โหมดแอป (มืด/สว่าง)",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "ประเทศจุดหมาย",
        "city": "เลือกเมือง",
        "start": "วันที่เริ่ม",
        "end": "วันที่สิ้นสุด",
        "activity": "กิจกรรม",
        "act_list": ["ท่องเที่ยวถ่ายรูป", "เล่นสกี", "ติดต่อธุรกิจ", "ผจญภัย", "ช้อปปิ้ง"],
        "gender": "เพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload": "📸 เลือกรูปชุดจากเครื่อง",
        "camera": "🤳 ถ่ายรูปจากกล้อง",
        "run": "✨ เริ่มวิเคราะห์และสร้าง 3D",
        "temp": "🌡️ อุณหภูมิเฉลี่ย",
        "warn": "⚠️ **สถานะอากาศ: หนาวจัด**",
        "analysis_title": "🔍 ผลวิเคราะห์และตัวละคร 3D",
    }
}

# --- ⚙️ 1. Logic & AI ---
def process_logic(api_key, country, city, activity, gender, use_free_mode, img_file, lang):
    # จำลองการทำงาน AI
    v_out = f"วิเคราะห์ชุดสำหรับ {city}, {country} เรียบร้อยแล้ว"
    return v_out

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DICT["Thai"] # ยึดภาษาไทยตามที่ตั้งค่าไว้

    with st.sidebar:
        st.title(t["settings"])
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        theme_mode = st.toggle(t["theme_label"], value=False)
        
        # ปรับแก้โหมดมืดให้เสถียรและมองเห็นชัดเจน
        if theme_mode:
            st.markdown("""
                <style>
                .stApp { background-color: #0F172A; color: #F8FAFC; }
                [data-testid="stSidebar"] { background-color: #1E293B; }
                .stMarkdown, p, h1, h2, h3, label, .stMetric { color: #F1F5F9 !important; }
                .stSelectbox div, .stTextInput div { background-color: #334155 !important; color: white !important; }
                .analysis-box { background: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #475569; }
                </style>
            """, unsafe_allow_html=True)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country]) # เชื่อมต่อเมืองตามประเทศ
            
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input(t["start"], datetime.now())
            end_date = d_col2.date_input(t["end"], datetime.now() + timedelta(days=5))
            
            activity = st.selectbox(t["activity"], t["act_list"])
            gender = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            
            # ส่วนอัปโหลดและกล้อง
            tab1, tab2 = st.tabs([t["upload"], t["camera"]])
            with tab1: img_file = st.file_uploader("", type=['jpg', 'png'], key="file_up")
            with tab2: cam_file = st.camera_input("")
            
            active_img = img_file if img_file else cam_file
            run_btn = st.button(t["run"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            v_out = process_logic(api_key, country, city, activity, gender, use_free_mode, active_img, "Thai")
            
            st.metric(label=t["temp"], value="1.8°C")
            st.warning(t["warn"])
            
            st.markdown(f"### {t['analysis_title']}")
            
            # ส่วนจำลองโมเดล 3D หมุนได้ 360 องศา (ใช้ Placeholder สำหรับโหมด AI)
            st.info("📦 กำลังประมวลผลโมเดล 3D แบบหมุนได้ 360 องศา...")
            
            # ตัวอย่างการฝัง 3D Viewer (HTML/JS)
            components.html("""
                <div style="width:100%; height:300px; background:#334155; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; border: 2px dashed #6366F1;">
                    <div style="text-align:center;">
                        <p>3D Character Preview</p>
                        <small>(โหมด OpenAI: ตัวละครสามารถใช้เมาส์หมุนดูได้รอบตัว)</small>
                    </div>
                </div>
            """, height=320)
            
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
        else:
            st.info("👈 กรุณาเลือกข้อมูลการเดินทางและอัปโหลดรูปชุดเพื่อเริ่มระบบ")

# --- 🔑 3. หน้า Login ---
def login_page():
    st.markdown("""<style>
        .login-header { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; margin-bottom: 2rem; }
        .social-btn { display: flex; align-items: center; justify-content: center; width: 100%; padding: 10px; border: 1px solid #dadce0; border-radius: 8px; background: white; margin-bottom: 10px; cursor: pointer; color: #3c4043; font-weight: 500; }
    </style>""", unsafe_allow_html=True)

    st.markdown("""
        <div class="login-header">
            <img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="120">
            <h1>Tripnify</h1>
            <p>จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ</p>
        </div>
    """, unsafe_allow_html=True)

    # ปุ่ม Login Google & Facebook กลับมาครบและกึ่งกลาง
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔵 เข้าสู่ระบบด้วย Facebook", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()
        if st.button("🔴 เข้าสู่ระบบด้วย Google", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

    st.markdown("<p style='text-align: center; color: gray;'>หรือ</p>", unsafe_allow_html=True)
    
    with c2:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("🔑 เข้าสู่ระบบ", use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 4. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
