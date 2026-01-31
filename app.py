import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- 🌐 0. ระบบจัดการภาษา ---
LANG_DICT = {
    "Thai": {
        "settings": "⚙️ ตั้งค่า",
        "lang_label": "เลือกภาษา",
        "free_mode": "โหมดใช้งานฟรี",
        "theme_label": "โหมดแอป (มืด/สว่าง)",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "จุดหมาย",
        "dest_list": ["ญี่ปุ่น", "เกาหลีใต้", "เวียดนาม", "ไต้หวัน", "จีน"],
        "start": "วันที่เริ่ม",
        "end": "วันที่สิ้นสุด",
        "activity": "กิจกรรม",
        "act_list": ["ท่องเที่ยวถ่ายรูป", "เล่นสกี/กิจกรรมหิมะ", "ติดต่อธุรกิจ", "ผจญภัย/เดินป่า", "ช้อปปิ้งในเมือง"],
        "gender": "เพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload": "📸 อัปโหลดรูปชุด",
        "run": "✨ เริ่มวิเคราะห์",
        "temp": "🌡️ อุณหภูมิเฉลี่ย",
        "warn": "⚠️ **สถานะอากาศ: หนาวจัด** | โปรดเตรียมเครื่องกันหนาวให้พร้อม",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "essentials": ["เสื้อโค้ทกันหนาวหนาพิเศษ", "กางเกงบุขนกันหนาว", "หมวกไหมพรมและผ้าพันคอ", "รองเท้าบูทกันหนาว", "แผ่นแปะความร้อนและถุงมือ"]
    },
    "English": {
        "settings": "⚙️ Settings",
        "lang_label": "Language",
        "free_mode": "Free Mode",
        "theme_label": "App Mode (Dark/Light)",
        "logout": "Logout",
        "travel_info": "🗓️ Travel Info",
        "dest": "Destination",
        "dest_list": ["Japan", "Korea", "Vietnam", "Taiwan", "China"],
        "start": "Start Date",
        "end": "End Date",
        "activity": "Activity",
        "act_list": ["Photography", "Ski/Snow", "Business", "Hiking", "Shopping"],
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "upload": "📸 Upload Outfit",
        "run": "✨ Run Analysis",
        "temp": "🌡️ Avg Temp",
        "warn": "⚠️ **Weather: Extreme Cold** | Please prepare winter gear",
        "analysis_title": "🔍 Outfit Analysis",
        "essentials": ["Heavy Winter Down Jacket", "Fleece Lined Pants", "Beanie & Scarf", "Winter Boots", "Heat Packs & Gloves"]
    }
}

# --- ⚙️ 1. ฟังก์ชันประมวลผล Logic ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang, start_date, end_date):
    days = (end_date - start_date).days + 1
    if api_key and not use_free_mode:
        return "วิเคราะห์โดย AI: ชุดของคุณเหมาะสมกับอุณหภูมิ 1.8°C", "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"
    else:
        v_free = "แนะนำ: เสื้อนอก Padding Jacket และกางเกงบุขน" if lang == "Thai" else "Suggest: Padding Jacket and Fleece Lined Pants"
        return v_free, "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DICT[lang]

    with st.sidebar:
        st.title(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice')
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        
        # ระบบควบคุม Theme ทั่วทั้งระบบ
        theme_mode = st.toggle(t["theme_label"], value=False)
        if theme_mode:
            st.markdown("""
                <style>
                .stApp { background-color: #0E1117; color: #FFFFFF; }
                [data-testid="stSidebar"] { background-color: #1A1C24; }
                .stMarkdown, p, h1, h2, h3, label { color: #FFFFFF !important; }
                .analysis-box { background: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #334155; color: #E2E8F0; }
                .shop-card { background: #334155; padding: 15px; border-radius: 10px; border-left: 5px solid #6366F1; margin-bottom: 10px; color: white; }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                .analysis-box { background: #F8FAFC; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; color: #1E293B; }
                .shop-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #4f46e5; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
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
            country = st.selectbox(t["dest"], t["dest_list"])
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input(t["start"], datetime.now())
            end_date = d_col2.date_input(t["end"], datetime.now() + timedelta(days=5))
            activity = st.selectbox(t["activity"], t["act_list"])
            gender = st.radio(t["gender"], [t["male"], t["female"]])
            img_file = st.file_uploader(t["upload"], type=['jpg', 'png', 'jpeg'])
            run_btn = st.button(t["run"], use_container_width=True)

    with col2:
        if run_btn:
            v_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang, start_date, end_date)
            # แก้ไข Indentation บรรทัดนี้ให้ตรงกัน
            w_col1, w_col2 = st.columns([1, 2])
            with w_col1:
                st.metric(label=t["temp"], value="1.8°C")
            with w_col2:
                st.warning(t["warn"])
            
            st.divider()
            st.markdown(f"### {t['analysis_title']}")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            if img_url: st.image(img_url, use_container_width=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดเริ่มวิเคราะห์")

# --- 🔑 3. หน้า Login ---
def login_page():
    # CSS สำหรับจัดปุ่ม Social และปรับแต่งพื้นผิวหน้า Login
    st.markdown("""<style>
        .stButton > button { border-radius: 8px; height: 3.5em; font-weight: 500; }
        .social-container { display: flex; align-items: center; justify-content: center; background-color: white; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -49px; pointer-events: none; position: relative; z-index: 10; }
        .social-text { color: #3c4043; font-family: sans-serif; font-weight: 500; font-size: 14px; }
        /* บังคับกึ่งกลางหน้าจอ */
        .login-header { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; margin-bottom: 2rem; }
    </style>""", unsafe_allow_html=True)

    # แก้ไข Logo กึ่งกลางแบบสมบูรณ์
    st.markdown("""
        <div class="login-header">
            <img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="120" style="margin-bottom: 10px;">
            <h1 style='margin: 0; padding: 0;'>Tripnify</h1>
            <p style='color: gray; font-size: 1.1rem;'>จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # ปุ่ม Social Login (คงเดิม)
    google_logo = "https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"
    st.markdown(f'<div class="social-container"><img src="{google_logo}" width="18px" style="margin-right: 12px;"><span class="social-text">เข้าสู่ระบบด้วยบัญชี Google</span></div>', unsafe_allow_html=True)
    if st.button("", use_container_width=True, key="google_login"):
        st.session_state['logged_in'] = True
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    user = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="กรอกชื่อผู้ใช้งาน")
    password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน")
    
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("🔑 เข้าสู่ระบบ", use_container_width=True):
            if user: st.session_state['logged_in'] = True; st.rerun()
    with col_r:
        if st.button("👤 ทดลองใช้ (Guest)", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 4. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
