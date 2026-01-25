import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus

# --- ⚙️ ฟังก์ชันประมวลผล AI ---
def process_ai_logic(api_key, country, activity, gender, uploaded_file):
    try:
        client = OpenAI(api_key=api_key)
        # Vision Analysis
        analysis_res = "ยังไม่ได้อัปโหลดรูปภาพ"
        if uploaded_file:
            b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
            v_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "Analyze these clothes and give 3 English keywords."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]}]
            )
            analysis_res = v_resp.choices[0].message.content
        
        # Recommendation
        r_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"แนะนำชุดไป {country} อุณหภูมิ 1.8 องศา กิจกรรม {activity}"}]
        )
        recommendation = r_resp.choices[0].message.content

        # DALL-E Image
        img_resp = client.images.generate(
            model="dall-e-3",
            prompt=f"A 3D character, {gender}, wearing: {recommendation}. White background.",
            n=1, size="1024x1024"
        )
        return analysis_res, recommendation, img_resp.data[0].url
    except Exception as e:
        return str(e), None, None

# --- 🎨 หน้า Login ---
def login_page():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit&display=swap');
        * { font-family: 'Kanit', sans-serif; }
        .login-box { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 400px; margin: auto; }
        .stButton>button { width: 100%; background-color: #5e5ce6 !important; color: white !important; border-radius: 12px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png", width=50)
        st.subheader("เข้าสู่ระบบ Tripnify")
        user = st.text_input("อีเมล", placeholder="example@email.com")
        pwd = st.text_input("รหัสผ่าน", type="password")
        if st.button("เข้าสู่ระบบ"):
            st.session_state['logged_in'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        api_key = st.text_input("OpenAI API Key", type="password")
        if st.button("ออกจากระบบ"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("📍 สวัสดี นักเดินทาง")
    c1, c2, c3 = st.columns(3)
    c1.metric("จุดหมาย", "Seoul, SK")
    c2.metric("อากาศ", "1.8°C")
    c3.metric("คำเตือน", "หนาวจัด")

    col1, col2 = st.columns([1, 1.5])
    with col1:
        country = st.selectbox("ประเทศ", ["South Korea", "Japan", "Thailand"])
        activity = st.selectbox("กิจกรรม", ["ท่องเที่ยว", "ทำงาน", "เดินป่า"])
        gender = st.radio("เพศ", ["ชาย", "หญิง"])
        img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png'])
        run = st.button("✨ เริ่มวางแผน")

    if run:
        if not api_key: st.error("กรุณาใส่ API Key")
        else:
            v_out, r_out, img_url = process_ai_logic(api_key, country, activity, gender, img_file)
            with col2:
                st.info(f"วิเคราะห์ภาพ: {v_out}")
                if img_url: st.image(img_url, caption="AI Preview")
                st.write(r_out)

# --- ควบคุมหน้าจอ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
