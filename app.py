import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ 1. ฟังก์ชันหลักในการประมวลผล ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang):
    # ข้อ 8: กำหนด Prompt ตามภาษา
    if lang == "Thai":
        p_critique = "วิเคราะห์รูปชุดนี้สำหรับอากาศ 1.8°C ในเกาหลีใต้ ประเมินความเหมาะสมและแนะนำการปรับปรุง 5 ส่วนหลัก: เสื้อนอก, กางเกง, หมวก/พันคอ, รองเท้า, และอุปกรณ์เสริม"
        p_outfit = f"แนะนำประเภทเสื้อผ้าที่ต้องเตรียมสำหรับไป {country} กิจกรรม {activity} โดยสรุปเป็นหมวดหมู่ (ไม่ต้องมีชื่อวัน)"
    else:
        p_critique = "Critique this outfit for 1.8°C. Evaluate suitability and suggest improvements in 5 areas: Outerwear, Pants, Headwear, Footwear, and Accessories."
        p_outfit = f"Recommend clothing types for {country} for {activity} activities as categories (No daily names)."

    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            v_out = "ไม่พบรูปภาพ" if lang == "Thai" else "No image uploaded"
            
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                v_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": p_critique},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}]
                )
                v_out = v_resp.choices[0].message.content
            
            r_resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": p_outfit}])
            r_out = r_resp.choices[0].message.content
            
            # ข้อ 9: สร้างภาพ 3D ที่สอดคล้องกับผลวิเคราะห์
            img_prompt = f"3D Pixar style character {gender} in {country} wearing professional winter gear for 1.8C weather, high detail."
            img_resp = client.images.generate(model="dall-e-3", prompt=img_prompt, n=1)
            return v_out, r_out, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "Please check your API Key", None
    else:
        # ข้อ 5, 6: โหมดทดลองใช้ฟรี
        v_free = "วิเคราะห์เบื้องต้น (โหมดฟรี): ชุดของคุณอาจบางไปสำหรับ 1.8°C ควรเพิ่มเลเยอร์ชั้นในและเสื้อโค้ทกันลม" if lang == "Thai" else "Basic Analysis (Free): Outfit might be too thin for 1.8°C. Suggest adding thermal layers."
        r_free = "แนะนำให้เตรียม: เสื้อกันหนาวหนา, กางเกงบุขน, และถุงมือ" if lang == "Thai" else "Suggest: Heavy coat, Thermal pants, and Gloves."
        sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        return v_free, r_free, sample_img

# --- 🎨 2. หน้า Dashboard (จัดการภาษาและลำดับการแสดงผล) ---
def main_dashboard():
    # สไตล์ CSS
    st.markdown("""<style>
        .analysis-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; color: #92400e; }
        .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        # ข้อ 2: ส่วนตั้งค่าภาษา
        st.title("⚙️ " + ("ตั้งค่า" if st.session_state.get('lang_choice') == "Thai" else "Settings"))
        lang = st.radio("เลือกภาษา (Select Language)", ["Thai", "English"], key='lang_choice')
        st.divider()
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี" if lang == "Thai" else "Free Mode", value=not api_key)
        if st.button("ออกจากระบบ" if lang == "Thai" else "Logout"): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            # ข้อ 3: ปรับ Label ตามภาษา
            st.subheader("🗓️ " + ("ข้อมูลการเดินทาง" if lang == "Thai" else "Travel Info"))
            country = st.selectbox("จุดหมาย (Destination)", ["South Korea", "Japan", "Vietnam"])
            start_date = st.date_input("วันที่เริ่ม (Start Date)", datetime.now())
            end_date = st.date_input("วันที่สิ้นสุด (End Date)", datetime.now() + timedelta(days=5))
            activity = st.selectbox("กิจกรรม (Activity)", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ (Gender)", ["ชาย", "หญิง"] if lang == "Thai" else ["Male", "Female"])
            img_file = st.file_uploader("📸 " + ("อัปโหลดรูปชุด" if lang == "Thai" else "Upload Outfit"), type=['jpg', 'png'])
            run_btn = st.button("✨ " + ("เริ่มวิเคราะห์" if lang == "Thai" else "Analyze"))

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang)
            
            # ลำดับที่ 1: ผลวิเคราะห์ (ข้อ 8)
            st.markdown("### 🔍 " + ("ผลวิเคราะห์การแต่งกาย" if lang == "Thai" else "Outfit Analysis"))
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            st.divider()

            # ลำดับที่ 2: ภาพ 3D (ข้อ 9, 10)
            st.markdown("### 🎭 " + ("ภาพจำลองแนะนำ" if lang == "Thai" else "3D Visual Guide"))
            if img_url: st.image(img_url, use_container_width=True)
            
            # ลำดับที่ 3: รายการชุด (ไม่มีชื่อวัน)
            st.markdown("### 📋 " + ("สิ่งที่ควรเตรียมเพิ่มเติม" if lang == "Thai" else "Preparation List"))
            st.info(r_out)
            st.divider()

            # ลำดับที่ 4: แหล่งช้อปปิ้ง (ข้อ 11)
            st.markdown("### 🛍️ " + ("แหล่งช้อปปิ้งแนะนำ" if lang == "Thai" else "Shopping Links"))
            items = ["เสื้อโค้ทกันหนาว", "ชุดลองจอน", "หมวกและถุงมือ", "รองเท้าบูท"] if lang == "Thai" else ["Winter Coat", "Heattech", "Gloves & Beanie", "Winter Boots"]
            for item in items:
                st.markdown(f"""<div class="shop-card"><strong>🔹 {item}</strong><br>
                <a href='https://shopee.co.th/search?keyword={quote_plus(item)}' target='_blank'>🛒 Shopee</a> | 
                <a href='https://www.lazada.co.th/catalog/?q={quote_plus(item)}' target='_blank'>🛒 Lazada</a></div>""", unsafe_allow_html=True)
        else:
            st.info("👈 " + ("กรุณาอัปโหลดรูปเพื่อเริ่มวิเคราะห์" if lang == "Thai" else "Please upload an image to start."))

# --- 🔐 3. ระบบ Login ---
def login_page():
    st.markdown("""<style>.login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; }</style>""", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="login-box"><h2>Tripnify Login</h2>', unsafe_allow_html=True)
    st.text_input("อีเมล")
    st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"): 
        st.session_state['logged_in'] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 🚀 4. ส่วนควบคุมการทำงาน ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: 
    main_dashboard()
else: 
    login_page()
