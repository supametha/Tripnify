import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล ---
def process_logic(api_key, country, activity, gender, travel_days, use_free_mode, uploaded_file, lang):
    # Prompt วิเคราะห์รูปภาพ (AI Critique) ตามภาพต้นฉบับที่คุณต้องการ
    prompt_critique = """
    วิเคราะห์รูปภาพการแต่งกายสำหรับอุณหภูมิ 1.8°C ในเกาหลีใต้ โดยให้ผลลัพธ์เป็นภาษาไทยในรูปแบบดังนี้:
    1. เสื้อผ้าชั้นนอก: ...
    2. กางเกง: ...
    3. หมวก: ...
    4. รองเท้า: ...
    5. อุปกรณ์เสริม: ...
    สรุปปิดท้ายสั้นๆ
    """
    if lang == "English":
        prompt_critique = "Analyze this outfit for 1.8°C in South Korea. Provide critique in 5 points: Outerwear, Pants, Headwear, Footwear, and Accessories in English."

    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            analysis_feedback = "ไม่พบรูปภาพสำหรับวิเคราะห์"
            
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
            
            # คำแนะนำการแต่งกาย (Outfit Plan) ตัดการระบุวันจันทร์-อาทิตย์ออก
            r_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"แนะนำประเภทเสื้อผ้าที่ต้องเตรียมสำหรับไป {country} กิจกรรม {activity} อากาศ 1.8C โดยไม่ต้องระบุชื่อวันจันทร์ถึงอาทิตย์ ให้สรุปเป็นหมวดหมู่เสื้อผ้าเท่านั้น"}]
            )
            recommendation = r_resp.choices[0].message.content
            
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter outfit style", n=1)
            return analysis_feedback, recommendation, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "โปรดตรวจสอบ API Key ของคุณ", None
    else:
        # โหมดฟรี (Guest Mode)
        res = "แนะนำ: เสื้อกันหนาวหนา, ลองจอน, และรองเท้าที่เดินสะดวก"
        sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        return "ระบบกำลังจำลองการวิเคราะห์ (โหมดฟรี)", res, sample_img

# --- 🎨 หน้า Login ---
def login_page():
    st.markdown("""<style>.login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; } .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 10px !important; }</style>""", unsafe_allow_html=True)
    st.markdown('<div class="login-box"><h2>Tripnify Login</h2>', unsafe_allow_html=True)
    # เพิ่ม Google Login ตามรูปที่ 1
    st.markdown('<div style="border:1px solid #e2e8f0; padding:10px; border-radius:10px; cursor:pointer; margin-bottom:20px;"><img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="18" style="margin-right:10px;"> ดำเนินการต่อด้วย Google</div>', unsafe_allow_html=True)
    st.text_input("อีเมล")
    st.text_input("รหัสผ่าน", type="password")
    st.markdown('<div style="text-align:right; font-size:12px; color:#6366f1; margin-bottom:15px;">ลืมรหัสผ่าน?</div>', unsafe_allow_html=True)
    if st.button("เข้าสู่ระบบ"): st.session_state['logged_in'] = True; st.rerun()
    st.markdown('<div style="margin-top:20px; font-size:13px; color:#64748b;"><a style="color:#6366f1;">สมัครสมาชิกใหม่</a> | ทดลองใช้งาน (Guest)</div></div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .metric-card { background: #f8fafc; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; }
        .analysis-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; color: #92400e; line-height: 1.8; }
        .shop-item { background: white; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 15px; }
        .tag { background: #eef2ff; color: #4f46e5; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        lang = st.radio("เลือกภาษา / Select Language", ["Thai", "English"])
        st.divider()
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดทดลองใช้งานฟรี", value=not api_key)
        if st.button("ออกจากระบบ"): st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Thailand"])
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input("วันเดินทางไป", datetime.now())
            end_date = d_col2.date_input("วันเดินทางกลับ", datetime.now() + timedelta(days=5))
            activity = st.selectbox("ประเภทกิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 อัปโหลดรูปชุดของคุณ", type=['jpg', 'png'])
            run_btn = st.button("✨ เริ่มการวิเคราะห์")

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, (end_date-start_date).days, use_free_mode, img_file, lang)
            
            # --- 1. สรุปข้อมูล (Metric Card) ---
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metric-card"><small>จุดหมาย</small><br><b>{country}</b></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><small>อากาศ</small><br><b>1.8°C</b></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card"><small>สถานะ</small><br><b>{"Premium" if api_key else "Guest"}</b></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # --- 2. AI Critique & Analysis (ภาษาไทยตามรูปที่ 10) ---
            st.markdown("### 🔍 AI Critique & Analysis")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            # --- 3. Outfit Plan (รูป 3D และข้อมูลแบบไม่มีชื่อวัน) ---
            st.markdown("### 🎭 Outfit Plan")
            if img_url: st.image(img_url, use_container_width=True)
            st.info(r_out)
            
            st.divider()

            # --- 4. แหล่งช้อปปิ้ง (เชื่อมโยง 5 ข้อจากการวิเคราะห์) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งและไอเทมแนะนำ")
            
            # ปรับหัวข้อสินค้าให้สอดคล้องกับ 5 ข้อของการวิเคราะห์ (รูปที่ 1)
            shop_categories = [
                {"item": "เสื้อผ้าชั้นนอก (เสื้อโค้ท/แจ็คเก็ต)", "id": "1"},
                {"item": "กางเกง (กางเกงขายาวหนา/เลกกิ้ง)", "id": "2"},
                {"item": "หมวก (หมวกไหมพรม/ผ้าพันคอ)", "id": "3"},
                {"item": "รองเท้า (รองเท้าบูท/ถุงเท้าหนา)", "id": "4"},
                {"item": "อุปกรณ์เสริม (ถุงมือ/แผ่นแปะความร้อน)", "id": "5"}
            ]

            for s in shop_categories:
                st.markdown(f"""
                    <div class="shop-item">
                        <span class="tag">แนะนำสำหรับการช้อป ข้อที่ {s['id']}</span>
                        <div style="margin-top:8px;"><strong>🔹 {s['item']}</strong></div>
                        <div style="margin-top:10px;">
                            <a href='https://shopee.co.th/search?keyword={quote_plus(s['item'])}' target='_blank' style='text-decoration:none; color:#4f46e5; font-size:14px;'>🛒 Shopee</a> | 
                            <a href='https://www.lazada.co.th/catalog/?q={quote_plus(s['item'])}' target='_blank' style='text-decoration:none; color:#4f46e5; font-size:14px; margin-left:10px;'>🛒 Lazada</a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและอัปโหลดรูปภาพเพื่อเริ่มต้นวิเคราะห์")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
