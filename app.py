import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# -------------------------------
# 🌐 0. Language System
# -------------------------------
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา",
        "theme_label": "โหมดแสดงผล",
        "api_label": "OpenAI API Key",
        "free_mode": "โหมดใช้งานฟรี",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "ประเทศ",
        "city": "เมือง",
        "start_date": "วันที่ไป",
        "end_date": "วันที่กลับ",
        "activity_label": "กิจกรรม",
        "activities": ["ท่องเที่ยวถ่ายรูป", "ติดต่อธุรกิจ", "กิจกรรมหิมะ/สกี", "ผจญภัย/เดินป่า", "ช้อปปิ้ง"],
        "gender": "เพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload_section": "📸 รูปภาพ",
        "run_btn": "✨ เริ่มวิเคราะห์",
        "temp_label": "🌡️ อุณหภูมิ",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน"],
}

# -------------------------------
# 🎭 1. 3D Model (Premium)
# -------------------------------
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
    <div style="width:100%;height:380px;background:#0f172a;
    border-radius:20px;display:flex;align-items:center;justify-content:center;">
        <div style="font-size:140px;">🧥</div>
    </div>
    """, height=400)

# -------------------------------
# ⚙️ 2. AI Analysis
# -------------------------------
def process_analysis(api_key, city, country, activity, use_free, image, lang, start, end):
    days = (end - start).days + 1
    if api_key and not use_free and image:
        client = OpenAI(api_key=api_key)
        b64 = base64.b64encode(image.getvalue()).decode()
        prompt = f"""
        วิเคราะห์การแต่งกายสำหรับ {city} ประเทศ{country}
        อุณหภูมิประมาณ 2°C
        กิจกรรม: {activity}
        ระยะเวลา {days} วัน
        ตอบเป็นภาษาไทย
        แนะนำรายการเสื้อผ้าเป็น bullet
        """
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }]
        )
        return res.choices[0].message.content, True

    return "แนะนำแต่งกายแบบ Layering: Heattech + เสื้อไหมพรม + เสื้อโค้ทกันหนาว", False

# -------------------------------
# 🧾 3. Extract Items from Analysis
# -------------------------------
def extract_items(text):
    return [
        {"name": "เสื้อโค้ทกันหนาว", "reason": "ป้องกันลมและอุณหภูมิต่ำ"},
        {"name": "เสื้อ Heattech", "reason": "ช่วยเก็บความร้อนใกล้ลำตัว"},
        {"name": "ถุงมือกันหนาว", "reason": "ลดการสูญเสียความร้อนที่มือ"},
        {"name": "รองเท้าบูทกันหนาว", "reason": "เดินบนหิมะได้ปลอดภัย"}
    ]

# -------------------------------
# 🎨 4. Dashboard
# -------------------------------
def main_dashboard():
    t = LANG_DATA["Thai"]

    with st.sidebar:
        st.subheader(t["settings"])
        api_key = st.text_input(t["api_label"], type="password")
        free_mode = st.toggle(t["free_mode"], value=not api_key)

    st.title("🌍 Tripnify Dashboard")

    col1, col2 = st.columns([1, 1.4])

    with col1:
        country = st.selectbox(t["dest"], CITY_DATA.keys())
        city = st.selectbox(t["city"], CITY_DATA[country])
        start = st.date_input(t["start_date"], datetime.now())
        end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
        activity = st.multiselect(t["activity_label"], t["activities"])
        img = st.file_uploader("อัปโหลดรูป", type=["jpg","png","jpeg"])
        run = st.button(t["run_btn"], type="primary")

    with col2:
        if run:
            result, is_premium = process_analysis(
                api_key, city, country, activity, free_mode, img, "Thai", start, end
            )

            # 🔍 Analysis FIRST
            st.subheader(t["analysis_title"])
            st.markdown(f"<div style='padding:15px;border-radius:12px;background:#f8fafc'>{result}</div>",
                        unsafe_allow_html=True)

            st.divider()

            # 🎭 3D / Image
            if is_premium:
                render_3d_model()
            else:
                st.image(
                    "https://images.unsplash.com/photo-1517495306684-21523df7d62c",
                    caption="Reference Outfit (Free Mode)"
                )

            # 🧾 Item Recommendation
            st.divider()
            st.subheader("🧾 สินค้าที่ควรซื้อจากผลวิเคราะห์")

            items = extract_items(result)
            for item in items:
                with st.expander(f"🧥 {item['name']}"):
                    st.write(item["reason"])

            # 🛍️ Shopping Sources
            st.divider()
            st.subheader("🛍️ แหล่งช้อปปิ้งแนะนำ")

            shops = [
                ("Shopee", "https://upload.wikimedia.org/wikipedia/commons/f/fe/Shopee.svg",
                 "https://shopee.co.th/search?keyword="),
                ("Uniqlo", "https://upload.wikimedia.org/wikipedia/commons/9/92/UNIQLO_logo.svg",
                 "https://www.uniqlo.com/th/th/search?q="),
                ("Lazada", "https://upload.wikimedia.org/wikipedia/commons/4/45/Lazada_logo.svg",
                 "https://www.lazada.co.th/catalog/?q=")
            ]

            for item in items:
                st.markdown(f"### 🔹 {item['name']}")
                cols = st.columns(3)
                for col, shop in zip(cols, shops):
                    with col:
                        st.markdown(f"""
                        <a href="{shop[2]}{quote_plus(item['name'])}" target="_blank">
                            <img src="{shop[1]}" width="80"><br>
                            {shop[0]}
                        </a>
                        """, unsafe_allow_html=True)

# -------------------------------
# 🚀 5. Main
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

main_dashboard()
