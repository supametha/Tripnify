import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus

# --- ⚙️ ฟังก์ชันประมวลผล AI ---
def process_ai_logic(api_key, country, activity, gender, uploaded_file):
    try:
        client = OpenAI(api_key=api_key)
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
        
        r_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"แนะนำชุดไป {country} อุณหภูมิ 1.8 องศา กิจกรรม {activity}"}]
        )
        recommendation = r_resp.choices[0].message.content

        img_resp = client.images.generate(
            model="dall-e-3",
            prompt=f"A 3D character, {gender}, wearing: {recommendation}. White background.",
            n=1, size="1024x1024"
        )
        return analysis_res, recommendation, img_resp.data[0].url
    except Exception as e:
        return str(e), None, None

# --- 🎨 หน้า Login ฉบับทางการ (White Minimalist) ---
def login_page():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
        
        /* พื้นหลังสีขาวสะอาดตา */
        .stApp {
            background-color: #ffffff;
        }

        .login-box {
            background: #ffffff;
            padding: 40px 30px;
            border-radius: 20px;
            border: 1px solid #f1f5f9;
            box-shadow: 0 10px 25px rgba(0,0,0,0.03);
            text-align: center;
            max-width: 450px;
            margin: auto;
        }

        .google-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            margin-bottom: 20px;
            font-size: 16px;
            color: #475569;
        }

        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            color: #cbd5e1;
            margin: 20px 0;
        }
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #f1f5f9;
        }
        .divider span { padding: 0 10px; font-size: 13px; }

        /* ปุ่มสีน้ำเงิน/ม่วงเข้มแบบทางการ */
        .stButton>button {
            width: 100%;
            background-color: #4f46e5 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px !important;
            font-size: 18px !important;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background-color: #4338ca !important;
        }

        .footer-links {
            margin-top: 25px;
            font-size: 14px;
            color: #64748b;
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    e1, col_login, e2 = st.columns([0.1, 1, 0.1])
    
    with col_login:
        st.write("") # เว้นระยะบน
        st.write("")
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("""
            <h2 style='color:#1e293b; margin-bottom:30px; font-weight:500;'>เข้าสู่ระบบ Tripnify</h2>
            <div class="google-btn">
                <img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="20" style="margin-right:10px;">
                Continue with Google
            </div>
            <div class="divider"><span>หรือใช้อีเมลของคุณ</span></div>
        """, unsafe_allow_html=True)

        user = st.text_input("อีเมล", placeholder="email@example.com", label_visibility="collapsed")
        pwd = st.text_input("รหัสผ่าน", type="password", placeholder="Password", label_visibility="collapsed")
        
        st.markdown('<div style="text-align:right; font-size:12px; color:#6366f1; margin-bottom:20px; cursor:pointer;">ลืมรหัสผ่าน?</div>', unsafe_allow_html=True)

        if st.button("เข้าสู่ระบบ"):
            st.session_state['logged_in'] = True
            st.rerun()

        st.markdown("""
            <div class="footer-links">
                <span style="color:#6366f1; cursor:pointer;">สร้างบัญชีใหม่</span>
                <span style="color:#e2e8f0;">|</span>
                <span style="cursor:pointer;">ทดลองใช้งาน (Guest)</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard (คงเดิม) ---
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
            with st.spinner("AI กำลังประมวลผล..."):
                v_out, r_out, img_url = process_ai_logic(api_key, country, activity, gender, img_file)
                with col2:
                    st.info(f"วิเคราะห์ภาพ: {v_out}")
                    if img_url: st.image(img_url, caption="AI Preview")
                    st.write(r_out)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
