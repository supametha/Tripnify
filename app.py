import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล ---
def process_logic(api_key, country, activity, gender, travel_days, use_free_mode, uploaded_file, lang):
    # กำหนด Prompt ตามภาษาที่เลือก
    prompt_critique = "Analyze this outfit for 1.8°C in South Korea. Give a professional critique and suggestions in Thai language."
    if lang == "English":
        prompt_critique = "Analyze this outfit for 1.8°C in South Korea. Give a professional critique and suggestions in English."

    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            analysis_feedback = "ไม่พบรูปภาพ" if lang == "Thai" else "No image found"
            
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                v_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt_critique},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}]
                )
                analysis_feedback = v_resp.choices[0].message.content
            
            # ตัดข้อมูลวันที่ออก ให้เหลือแค่เนื้อหาการแต่งกาย
            r_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"แนะนำการแต่งกายไป {country} กิจกรรม {activity} ไม่ต้องบอกวันจันทร์-อาทิตย์ เอาแค่ประเภทชุดที่ต้องเตรียม"}]
            )
            recommendation = r_resp.choices[0].message.content
            
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter outfit", n=1)
            return analysis_feedback, recommendation, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "Please check Key", None
    else:
        # โหมดฟรี
        res = "แนะนำให้เตรียมเสื้อโค้ทและลองจอน" if lang == "Thai" else "Suggest preparing coat and heattech."
        sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        return "โหมดพื้นฐาน", res, sample_img

# --- 🎨 หน้า Login ---
def login_page():
    st.markdown("""<style>.stApp { background-color: #ffffff; } .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; } .google-btn { display: flex; align-items: center; justify-content: center; width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 10px; cursor: pointer; margin-bottom: 20px; color: #475569; } .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 10px !important; }</style>""", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="login-box"><h2>Tripnify Login</h2><div class="google-btn"><img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="18" style="margin-right:10px;"> Continue with Google</div>', unsafe_allow_html=True)
    st.text_input("อีเมล")
    st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"): st.session_state['logged_in'] = True; st.rerun()
    st.markdown('<div style="margin-top:20px; font-size:13px;"><a style="color:#6366f1;">สมัครสมาชิกใหม่</a> | <a style="color:#64748b;">ทดลองใช้งาน (Guest)</a></div></div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>.metric-card { background: #f8fafc; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; } .analysis-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; color: #92400e; line-height: 1.6; } .shop-item { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า (Settings)")
        # --- ปุ่มปรับ 2 ภาษา ---
        lang = st.radio("เลือกภาษา (Select Language)", ["Thai", "English"])
        st.divider()
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี", value=not api_key)
        if st.button("ออกจากระบบ"): st.session_state['logged_in'] = False; st.rerun()

    title = "🌍 Tripnify Dashboard" if lang == "English" else "🌍 แผงควบคุม Tripnify"
    st.title(title)
    
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ Travel Info" if lang == "English" else "🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("Destination", ["South Korea", "Japan", "Thailand"])
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input("Start", datetime.now())
            end_date = d_col2.date_input("End", datetime.now() + timedelta(days=5))
            activity = st.selectbox("Activity", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("Gender", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 Upload Outfit", type=['jpg', 'png'])
            run_btn = st.button("✨ Analyze" if lang == "English" else "✨ เริ่มวิเคราะห์")

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, (end_date-start_date).days, use_free_mode, img_file, lang)
            
            # Section 1: Metrics
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metric-card"><small>Destination</small><br><b>{country}</b></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><small>Temp</small><br><b>1.8°C</b></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card"><small>Mode</small><br><b>{"Premium" if api_key else "Free"}</b></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Section 2: AI Critique (ภาษาไทย)
            st.markdown("### 🔍 AI Critique & Analysis")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            # Section 3: Recommendation (ตัดวันออก)
            st.markdown("### 🎭 Outfit Plan")
            if img_url: st.image(img_url, use_container_width=True)
            st.info(r_out)
            
            st.divider()

            # Section 4: Shopping (ชื่อสินค้าเพรียวๆ)
            st.markdown("### 🛍️ Shopping Links")
            # ดึงเฉพาะชื่อสินค้าหลักจากคำแนะนำ
            shop_list = ["เสื้อโค้ทกันหนาว", "ชุดลองจอน", "รองเท้าบูท", "ถุงมือและหมวกไหมพรม", "แผ่นแปะความร้อน"]
            if lang == "English":
                shop_list = ["Winter Coat", "Heattech", "Winter Boots", "Gloves & Beanie", "Hot Packs"]

            for item in shop_list:
                st.markdown(f"""
                    <div class="shop-item">
                        <strong>🔹 {item}</strong><br>
                        <a href='https://shopee.co.th/search?keyword={quote_plus(item)}' target='_blank' style='text-decoration:none; color:#4f46e5;'>Shopee</a> | 
                        <a href='https://www.lazada.co.th/catalog/?q={quote_plus(item)}' target='_blank' style='text-decoration:none; color:#4f46e5; margin-left:10px;'>Lazada</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 Please fill in the info to start." if lang == "English" else "👈 กรุณากรอกข้อมูลเพื่อเริ่มวิเคราะห์")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
