# app.py
# -------------------------------
# Tripnify – Integrated Shopping System (Fixed & Clean)
# -------------------------------

import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# -------------------------------
# 🌐 Language System
# -------------------------------
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
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์"],
    "ไต้หวัน": ["ไทเป", "เกาสง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้"],
}

SHOP_PLATFORMS = {
    "Shopee": "https://shopee.co.th/search?keyword=",
    "Uniqlo": "https://www.uniqlo.com/th/th/search?q=",
    "Lazada": "https://www.lazada.co.th/catalog/?q=",
}

# -------------------------------
# 🎭 3D Model (Premium Only)
# -------------------------------

def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html(
        """
        <div style='width:100%;height:380px;background:#0f172a;border-radius:18px;
        display:flex;align-items:center;justify-content:center;border:2px solid #6366f1;'>
            <div style='font-size:140px;'>🧥</div>
        </div>
        """,
        height=400,
    )

# -------------------------------
# ⚙️ Analysis Logic (Stable)
# -------------------------------

def process_analysis(api_key, city, country, activity, free_mode, image, start, end):
    days = (end - start).days + 1

    if api_key and not free_mode and image:
        try:
            client = OpenAI(api_key=api_key)
            b64 = base64.b64encode(image.getvalue()).decode()
            prompt = f"วิเคราะห์ชุดสำหรับ {city} ประเทศ{country} กิจกรรม {activity} {days} วัน"
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                }],
            )
            return res.choices[0].message.content, True
        except Exception:
            pass

    return "แนะนำแต่งกายแบบ Layering: Heattech + เสื้อไหมพรม + เสื้อโค้ทกันหนาว", False

# -------------------------------
# 🛍️ Shopping System (Keyword-based)
# -------------------------------

def extract_shopping_items(text):
    keywords = ["เสื้อโค้ท", "เสื้อไหมพรม", "Heattech", "รองเท้าบูท", "ถุงมือ"]
    return [k for k in keywords if k in text]


def render_shopping(items):
    for item in items:
        st.markdown(f"#### 🔹 {item}")
        for shop, base_url in SHOP_PLATFORMS.items():
            st.link_button(
                f"ซื้อที่ {shop}",
                base_url + quote_plus(item),
                use_container_width=True,
            )
        st.divider()

# -------------------------------
# 🎨 Dashboard
# -------------------------------

def main_dashboard():
    t = LANG_DATA["Thai"]

    with st.sidebar:
        st.subheader(t["settings"])
        api_key = st.text_input(t["api_label"], type="password")
        free_mode = st.toggle(t["free_mode"], value=not bool(api_key))
        if st.button(t["logout"], use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")

    col1, col2 = st.columns([1, 1.4])

    with col1:
        country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
        city = st.selectbox(t["city"], CITY_DATA[country])
        start = st.date_input(t["start_date"], datetime.now())
        end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
        activity = st.multiselect(t["activity_label"], t["activities"])
        image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        run = st.button(t["run_btn"], type="primary", use_container_width=True)

    with col2:
        if run:
            result, premium = process_analysis(api_key, city, country, activity, free_mode, image, start, end)
            st.subheader(t["analysis_title"])
            st.info(result)

            if premium:
                render_3d_model()

            st.subheader(t["shop_title"])
            items = extract_shopping_items(result)
            render_shopping(items)
        else:
            st.info("👈 กรุณากรอกข้อมูลแล้วกดเริ่มวิเคราะห์")

# -------------------------------
# 🔑 Login
# -------------------------------

def login_page():
    st.title("Tripnify")
    if st.button("เข้าสู่ระบบ / Guest", use_container_width=True):
        st.session_state.logged_in = True
        st.rerun()

# -------------------------------
# 🚀 App Controller
# -------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_dashboard()
else:
    login_page()
