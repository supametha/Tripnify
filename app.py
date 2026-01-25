import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล AI ---
def process_ai_logic(api_key, country, activity, gender, uploaded_file, travel_days):
    try:
        client = OpenAI(api_key=api_key)
        
        # 1. วิเคราะห์ภาพเสื้อผ้า
        analysis_res = "ไม่พบข้อมูลภาพ"
        if uploaded_file:
            b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
            v_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "Analyze these clothes and assess if they are suitable for 1.8°C weather and the activity. Give 3 keywords."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]}]
            )
            analysis_res = v_resp.choices[0].message.content
        
        # 2. แนะนำการแต่งกาย (แบ่งเป็นส่วนๆ เพื่อเชื่อมโยง Shopping)
        r_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"วางแผนแต่งกายไป {country} {travel_days} วัน กิจกรรม {activity} เพศ {gender} อากาศ 1.8C บอกสิ่งที่ต้องมีแยกเป็น: 1.Outerwear 2.Tops/Bottoms 3.Accessories/Shoes"}]
        )
        recommendation = r_resp.choices[0].message.content

        # 3. สร้างภาพจำลอง 3D
        img_resp = client.images.generate(
            model="dall-e-3",
            prompt=f"A 3D Pixar-style character, {gender}, traveling in {country}, wearing professional winter outfit based on: {recommendation}. High quality, white background.",
            n=1, size="1024x1024"
        )
        return analysis_res, recommendation, img_resp.data[0].url
    except Exception as e:
        return str(e), None, None

# --- 🎨 หน้า Login ---
def login_page():
    st.markdown("""<style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
        .stApp { background-color: #ffffff; }
        .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; max-width: 450px; margin: auto; }
        .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 10px !important; border: none !important; padding: 12px !important; }
    </style>""", unsafe_allow_html=True)
    st.write("")
    st.write("")
    with st.container():
        st.markdown('<div class="login-box"><h2>Tripnify Login</h2>', unsafe_allow_html=True)
        st.text_input("อีเมล", placeholder="email@example.com")
        st.text_input("รหัสผ่าน", type="password")
        if st.button("เข้าสู่ระบบ"):
            st.session_state['logged_in'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .main-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #f1f5f9; margin-bottom: 20px; }
        .info-header { font-size: 1.2rem; font-weight: 500; color: #1e293b; margin-bottom: 10px; }
        .shop-box { background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        api_key = st.text_input("OpenAI API Key", type="password")
        st.divider()
        if st.button("ออกจากระบบ"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🗓️ วางแผนการเดินทาง")
        country = st.selectbox("เลือกประเทศ", ["South Korea", "Japan", "Thailand", "Vietnam", "Taiwan"])
        
        # 3. เพิ่มส่วนเลือกวันไปและกลับ
        d_col1, d_col2 = st.columns(2)
        start_date = d_col1.date_input("วันเดินทางไป", datetime.now())
        end_date = d_col2.date_input("วันเดินทางกลับ", datetime.now() + timedelta(days=5))
        travel_days = (end_date - start_date).days
        
        activity = st.selectbox("ประเภทกิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย/เดินป่า", "ถ่ายรูป/Fashion", "ช้อปปิ้งในเมือง"])
        gender = st.radio("เพศ", ["ชาย", "หญิง", "ไม่ระบุ"])
        img_file = st.file_uploader("📸 อัปโหลดรูปภาพเสื้อผ้าของคุณ", type=['jpg', 'png'])
        
        run_btn = st.button("✨ เริ่มสรุปแผนการเดินทาง")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if run_btn:
            if not api_key:
                st.warning("⚠️ กรุณาใส่ OpenAI API Key")
            else:
                with st.spinner("⏳ กำลังประมวลผลข้อมูลการเดินทาง..."):
                    v_out, r_out, img_url = process_ai_logic(api_key, country, activity, gender, img_file, travel_days)
                    
                    if r_out:
                        # 1. ส่วนจุดหมาย อากาศ คำเตือน
                        st.markdown('<p class="info-header">📋 ข้อมูลสรุปการเดินทาง</p>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("จุดหมาย", country)
                        m2.metric("อากาศ", "1.8°C")
                        m3.metric("คำเตือน", "⚠️ หนาวจัด")
                        
                        st.divider()

                        # 2. ส่วนสรุปข้อมูลการนำเข้าภาพและการประเมิน
                        with st.expander("🔍 ผลการประเมินความเหมาะสมของชุด", expanded=True):
                            st.write(f"**สรุปการนำเข้าภาพ:** {'สำเร็จ' if img_file else 'ไม่มีการอัปโหลด'}")
                            st.info(f"**การประเมินตามสภาพอากาศและกิจกรรม:**\n\n{v_out}")
                        
                        # 4. แสดงภาพ 3D และคำแนะนำ Shopping แยกส่วน
                        st.markdown("### 🎭 ภาพจำลองการแต่งกาย 3 มิติ")
                        st.image(img_url, use_container_width=True)
                        
                        st.markdown("### 🛍️ คำแนะนำสินค้าเพื่อเชื่อมโยง E-commerce")
                        
                        # แยกคำแนะนำเป็นส่วนๆ (จำลองการตัดคำจาก AI)
                        sections = ["เสื้อกันหนาว & Heattech", "กางเก游 & กระโปรง", "รองเท้า & อุปกรณ์เสริม"]
                        items = re.findall(r'\b[A-Z][a-z]+\b', r_out)[:3] # ดึง Keyword จาก AI
                        
                        for idx, sec in enumerate(sections):
                            item_name = items[idx] if idx < len(items) else "Fashion item"
                            st.markdown(f"""
                                <div class="shop-box">
                                    <strong>🔹 {sec}</strong><br>
                                    <small>แนะนำ: {item_name}</small><br>
                                    <a href='https://shopee.co.th/search?keyword={quote_plus(item_name)}' target='_blank'>🛒 ช้อปบน Shopee</a> | 
                                    <a href='https://www.lazada.co.th/catalog/?q={quote_plus(item_name)}' target='_blank'>🛒 ช้อปบน Lazada</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและเลือกวันที่เดินทางเพื่อเริ่มใช้งาน")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
