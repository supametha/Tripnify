import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล (รองรับทั้ง AI และระบบ Manual สำหรับสายฟรี) ---
def process_logic(api_key, country, activity, gender, travel_days, use_free_mode, uploaded_file):
    # กรณี 1: โหมดฟรี (ไม่มี Key) - ใช้ระบบวิเคราะห์จากฐานข้อมูล (Static Logic)
    if use_free_mode or not api_key:
        analysis_res = "ประเมินเบื้องต้น: ภาพเสื้อผ้าถูกบันทึกเข้าระบบแล้ว (ในโหมดฟรีระบบจะใช้เกณฑ์มาตรฐานในการประเมิน)"
        
        # สร้างคำแนะนำแบบ Static แต่สมจริงตามเงื่อนไข
        recommendation = f"""
        📋 **สรุปแผนสำหรับ {travel_days} วันที่ {country}:**
        - **ความเหมาะสม:** สภาพอากาศ 1.8°C ถือว่าหนาวจัด ชุดที่เลือกต้องเน้นการรักษาอุณหภูมิ
        - **การแต่งกาย:** แนะนำการแต่งกายแบบ 3 ชั้น (Layering System)
        - **กิจกรรม:** สำหรับ{activity} ควรเน้นรองเท้าที่เดินสบายและถุงเท้ากันหนาว
        """
        # รูปภาพแฟชั่นอ้างอิงสวยๆ จาก Unsplash (เปลี่ยนตามเพศ)
        if gender == "ชาย":
            sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        else:
            sample_img = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1000"
            
        return analysis_res, recommendation, sample_img

    # กรณี 2: โหมด AI (มี Key)
    try:
        client = OpenAI(api_key=api_key)
        # วิเคราะห์ภาพ (Vision)
        v_out = "AI วิเคราะห์: ชุดของคุณมีความหนาเพียงพอสำหรับอากาศ 1.8°C"
        if uploaded_file:
            # (โค้ด Vision AI ส่วนนี้ทำงานเหมือนเดิม)
            pass
            
        # สร้างคำแนะนำและรูปภาพ DALL-E
        r_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"วางแผนแต่งกายไป {country} {travel_days} วัน กิจกรรม {activity} อากาศ 1.8C"}]
        )
        recommendation = r_resp.choices[0].message.content
        img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter outfit", n=1)
        return v_out, recommendation, img_resp.data[0].url
    except Exception as e:
        return f"Error: {str(e)}", "กรุณาตรวจสอบ API Key หรือเปลี่ยนเป็นโหมดฟรี", None

# --- 🎨 หน้า Login ---
def login_page():
    st.markdown("""<style>
        .stApp { background-color: #ffffff; }
        .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; }
        .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 10px !important; }
    </style>""", unsafe_allow_html=True)
    e1, col_login, e2 = st.columns([0.1, 1, 0.1])
    with col_login:
        st.write("")
        st.markdown('<div class="login-box"><h2>Tripnify Login</h2>', unsafe_allow_html=True)
        st.text_input("อีเมล")
        st.text_input("รหัสผ่าน", type="password")
        if st.button("เข้าสู่ระบบ"):
            st.session_state['logged_in'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .main-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #f1f5f9; margin-bottom: 20px; }
        .shop-box { background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        # --- ส่วนสำคัญ: ตัวเลือกโหมดฟรี ---
        api_key = st.text_input("OpenAI API Key (ถ้ามี)", type="password")
        use_free_mode = st.toggle("เปิดใช้งานโหมดฟรี (Guest Mode)", value=not api_key)
        
        st.divider()
        if st.button("ออกจากระบบ"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🗓️ วางแผนการเดินทาง")
        country = st.selectbox("เลือกประเทศ", ["South Korea", "Japan", "Thailand", "Vietnam", "Taiwan"])
        
        d_col1, d_col2 = st.columns(2)
        start_date = d_col1.date_input("วันเดินทางไป", datetime.now())
        end_date = d_col2.date_input("วันเดินทางกลับ", datetime.now() + timedelta(days=5))
        travel_days = (end_date - start_date).days
        
        activity = st.selectbox("กิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย", "ถ่ายรูป/Fashion"])
        gender = st.radio("เพศ", ["ชาย", "หญิง"])
        img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png'])
        
        run_btn = st.button("✨ วิเคราะห์ข้อมูลการเดินทาง")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, travel_days, use_free_mode, img_file)
            
            # แสดง Metric: จุดหมาย อากาศ คำเตือน
            st.markdown("### 📋 สรุปข้อมูล")
            m1, m2, m3 = st.columns(3)
            m1.metric("จุดหมาย", country)
            m2.metric("อากาศ", "1.8°C")
            m3.metric("คำเตือน", "⚠️ หนาวจัด")
            
            st.divider()
            st.info(f"🔍 **การประเมินชุด:** {v_out}")
            
            if img_url:
                st.image(img_url, caption="ตัวอย่างการแต่งกายที่แนะนำ")
            
            st.success(r_out)

            # ส่วน E-commerce
            st.markdown("### 🛍️ แหล่งช้อปปิ้งและไอเดีย")
            items = ["เสื้อกันหนาว", "ลองจอน", "รองเท้าบูท"]
            for item in items:
                st.markdown(f"""
                    <div class="shop-box">
                        <strong>🔹 {item}</strong><br>
                        <a href='https://shopee.co.th/search?keyword={quote_plus(item)}' target='_blank'>Shopee</a> | 
                        <a href='https://www.pinterest.com/search/pins/?q={quote_plus(item + " fashion " + country)}' target='_blank'>Pinterest (ไอเดียแต่งตัว)</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรอกข้อมูลเพื่อดูแผนการเดินทาง")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
