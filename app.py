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
        "theme_label": "โหมดแอป",
        "light": "สว่าง",
        "dark": "มืด",
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
        "camera": "🤳 หรือเปิดกล้องถ่ายภาพชุด",
        "run": "✨ เริ่มวิเคราะห์",
        "temp": "🌡️ อุณหภูมิเฉลี่ย",
        "warn": "⚠️ **สถานะอากาศ: หนาวจัด** | โปรดเตรียมเครื่องกันหนาวให้พร้อม",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "ai_img": "🎭 ภาพจำลองแนะนำ",
        "essential_title": "📋 สิ่งที่ควรเตรียมเพิ่มเติม",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ",
        "info_click": "💡 คลิกเพื่อดูรายละเอียด",
        "essentials": [
            "เสื้อโค้ทกันหนาวหนาพิเศษ", "กางเกงบุขนกันหนาว", "หมวกไหมพรมและผ้าพันคอ", "รองเท้าบูทกันหนาว", "แผ่นแปะความร้อนและถุงมือ"
        ]
    },
    "English": {
        "settings": "⚙️ Settings",
        "lang_label": "Language",
        "free_mode": "Free Mode",
        "theme_label": "App Mode",
        "light": "Light",
        "dark": "Dark",
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
        "camera": "🤳 or Use Camera",
        "run": "✨ Run Analysis",
        "temp": "🌡️ Avg Temp",
        "warn": "⚠️ **Weather: Extreme Cold** | Please prepare winter gear",
        "analysis_title": "🔍 Outfit Analysis",
        "ai_img": "🎭 AI Generated Image",
        "essential_title": "📋 Additional Essentials",
        "shop_title": "🛍️ Recommended Shopping",
        "info_click": "💡 Click for details",
        "essentials": [
            "Heavy Winter Down Jacket", "Fleece Lined Pants", "Beanie & Scarf", "Winter Boots", "Heat Packs & Gloves"
        ]
    }
}

# --- ⚙️ 1. ฟังก์ชันประมวลผล Logic ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang, start_date, end_date):
    days = (end_date - start_date).days + 1
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            p_critique = f"Analyze for 1.8°C in {country} ({days} days). Response in {lang}."
            v_out = "No image"
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                v_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": p_critique}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                )
                v_out = v_resp.choices[0].message.content
            img_url = "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"
            return v_out, img_url
        except Exception as e:
            return f"Error: {e}", None
    else:
        v_free = "1. Outer: Down Jacket\n2. Bottom: Fleece Lined" if lang=="English" else "1. เสื้อนอก: Padding Jacket\n2. กางเกง: บุขน"
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
        theme_mode = st.toggle(t["theme_label"], value=False)
        
        if theme_mode:
            st.markdown("""<style>
                .stApp { background-color: #1E293B; color: #F8FAFC; }
                .analysis-box { background: #334155 !important; color: #F1F5F9 !important; border: 1px solid #475569 !important; padding:20px; border-radius:12px; }
                .shop-card { background: #334155 !important; color: white !important; border: 1px solid #475569 !important; border-left: 5px solid #6366F1 !important; padding:15px; border-radius:10px; margin-bottom:10px; }
            </style>""", unsafe_allow_html=True)
        else:
            st.markdown("""<style>
                .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
                .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
            </style>""", unsafe_allow_html=True)

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
            w_col1, w_col2 = st.columns([1, 2])
            with w_col1: st.metric(label=t["temp"], value="1.8°C")
            with w_col2: st.warning(t["warn"])
            
            st.divider()
            st.markdown(f"### {t['analysis_title']}")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            if img_url: st.image(img_url, use_container_width=True)
            st.markdown(f"### {t['shop_title']}")
            for it in t["essentials"]:
                st.markdown(f'<div class="shop-card"><strong>🔹 {it}</strong><br><a href="https://shopee.co.th/search?keyword={quote_plus(it)}" target="_blank">🛒 Shopee</a></div>', unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดเริ่มวิเคราะห์")

# --- 🔑 3. หน้า Login ---
def login_page():
    st.markdown("""<style>
        .stButton > button { border-radius: 8px; height: 3.5em; font-weight: 500; }
        .social-container { display: flex; align-items: center; justify-content: center; background-color: white; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -48px; pointer-events: none; position: relative; z-index: 10; }
        .social-text { color: #3c4043; font-family: sans-serif; font-weight: 500; font-size: 14px; }
    </style>""", unsafe_allow_html=True)

    # --- ส่วนที่แก้ให้ Logo อยู่กึ่งกลาง ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<center>", unsafe_allow_html=True)
    # ใส่ Link รูปโลโก้ของคุณที่นี่ (ตอนนี้เป็นรูปตัวอย่าง)
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=120)
    st.markdown("<h1 style='margin-bottom: 0;'>Tripnify</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: gray;'>จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ</p>", unsafe_allow_html=True)
    st.markdown("</center>", unsafe_allow_html=True)
    st.markdown("---")
    
    google_logo = "https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"
    facebook_logo = "https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg"

    st.markdown(f'<div class="social-container"><img src="{google_logo}" width="18px" style="margin-right: 12px;"><span class="social-text">เข้าสู่ระบบด้วยบัญชี Google</span></div>', unsafe_allow_html=True)
    if st.button("", use_container_width=True, key="google_login"):
        st.session_state['logged_in'] = True
        st.rerun()

    st.write("") 
    st.markdown(f'<div class="social-container"><img src="{facebook_logo}" width="20px" style="margin-right: 12px;"><span class="social-text">เข้าสู่ระบบด้วยบัญชี Facebook</span></div>', unsafe_allow_html=True)
    if st.button("", use_container_width=True, key="fb_login"):
        st.session_state['logged_in'] = True
        st.rerun()
    
    st.markdown("<p style='text-align: center; color: gray; margin: 20px 0;'>หรือ</p>", unsafe_allow_html=True)
    user = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="กรอกชื่อผู้ใช้งาน")
    password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน")
    
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("🔑 เข้าสู่ระบบ", use_container_width=True):
            if user: st.session_state['logged_in'] = True; st.rerun()
    with col_r:
        if st.button("👤 ทดลองใช้ (Guest)", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("<center>Tripnify - Travel Smart, Dress Right</center>", unsafe_allow_html=True)

# --- 🚀 4. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
