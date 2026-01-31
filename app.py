import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# -------------------------------
# 🌐 Language
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
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้",
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน"],
}

# -------------------------------
# 🎭 3D Model (Premium)
# -------------------------------
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width:100%;height:400px;
        background:radial-gradient(circle,#334155 0%,#0f172a 100%);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        position:relative;cursor:grab;border:2px solid #6366f1;">
            <div id="character" style="font-size:150px;transition:transform 0.1s linear;">🧥</div>
            <div style="position:absolute;bottom:15px;color:#94a3b8;font-size:12px;">
                [ ลากเพื่อหมุนดูชุด 360° ]
            </div>
        </div>
        <script>
            const el=document.getElementById('viewer-3d');
            const char=document.getElementById('character');
            let drag=false,rot=0,startX=0;
            el.onmousedown=e=>{drag=true;startX=e.pageX;};
            window.onmouseup=()=>drag=false;
            window.onmousemove=e=>{
                if(!drag)return;
                const d=e.pageX-startX;
                rot+=d*0.5;
                char.style.transform=`rotateY(${rot}deg)`;
                startX=e.pageX;
            };
        </script>
    """, height=420)

# -------------------------------
# ⚙️ Analysis Logic
# -------------------------------
def process_analysis(api_key, city, country, activity, free_mode, image, start, end):
    days = (end - start).days + 1
    if api_key and not free_mode and image:
        client = OpenAI(api_key=api_key)
        b64 = base64.b64encode(image.getvalue()).decode()
        prompt = f"""
        วิเคราะห์การแต่งกายสำหรับ {city} ประเทศ{country}
        อุณหภูมิประมาณ 2°C
        กิจกรรม: {activity}
        ระยะเวลา {days} วัน
        ตอบเป็นภาษาไทย
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
# 🎨 Dashboard
# -------------------------------
def main_dashboard():
    t = LANG_DATA["Thai"]

    # Sidebar (ใช้จาก code ที่ให้มา)
    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai"], horizontal=True)
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        free_mode = st.toggle(t["free_mode"], value=not api_key)
        dark = st.toggle(t["theme_label"], value=False)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

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
                api_key, city, country, activity, free_mode, img, start, end
            )

            # Weather
            st.metric(t["temp_label"], "2°C")
            st.warning(f"❄️ อากาศหนาวใน {city}")
            st.divider()

            # 🔍 Analysis FIRST
            st.subheader(t["analysis_title"])
            st.markdown(f"<div class='analysis-box'>{result}</div>", unsafe_allow_html=True)

            # 🎭 3D ต่อจากผลวิเคราะห์
            st.divider()
            if is_premium:
                render_3d_model()
            else:
                st.image(
                    "https://images.unsplash.com/photo-1517495306684-21523df7d62c",
                    caption="Reference Outfit (Free Mode)"
                )

            # 🛍️ Shopping
            st.divider()
            st.subheader(t["shop_title"])
            for item in ["เสื้อโค้ทกันหนาว","ถุงมือกันหนาว","รองเท้าบูทกันหนาว"]:
                st.markdown(f"""
                <div class="shop-card">
                    🔹 {item}<br>
                    <a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank">
                        คลิกเพื่อค้นหาสินค้า
                    </a>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("👈 กรอกข้อมูลแล้วกดเริ่มวิเคราะห์")

# -------------------------------
# 🔑 Login Page (ใช้จาก code ที่ให้มา)
# -------------------------------
def login_page():
    t = LANG_DATA["Thai"]
    st.markdown(f"""
    <div style="text-align:center;padding:40px">
        <h1 style="font-size:3rem">Tripnify</h1>
        <p>{t['login_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1,1.5,1])
    with c:
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True
            st.rerun()
        if st.button(t["guest_btn"], use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()

# -------------------------------
# 🚀 Main
# -------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
