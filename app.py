import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล Logic ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang):
    # กำหนด Prompt วิเคราะห์ 5 ข้อหลัก (อ้างอิง image_533a73)
    prompt_critique = """
    วิเคราะห์รูปภาพการแต่งกายสำหรับอุณหภูมิ 1.8°C ในเกาหลีใต้ โดยให้ผลลัพธ์เป็นภาษาไทยใน 5 หัวข้อหลักดังนี้:
    1. เสื้อผ้าชั้นนอก: แนะนำประเภทที่กันลมและหนาขึ้น
    2. กางเกง: แนะนำกางเกงที่หนาหรือเลกกิ้งกันหนาว
    3. หมวก: แนะนำหมวกไหมพรมหรือผ้าพันคอเพิ่มเติม
    4. รองเท้า: แนะนำรองเท้าบูทหรือรองเท้าที่บุขนด้านใน
    5. อุปกรณ์เสริม: แนะนำถุงมือหรือแผ่นแปะความร้อน
    """
    
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
            
            # คำแนะนำชุดที่ควรเตรียม (ไม่มีชื่อวัน อ้างอิง image_52e75b)
            r_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"แนะนำประเภทเสื้อผ้าที่ต้องเตรียมสำหรับไป {country} กิจกรรม {activity} อากาศ 1.8C โดยสรุปเป็นหมวดหมู่ และไม่ต้องระบุชื่อวันจันทร์ถึงอาทิตย์"}]
            )
            recommendation = r_resp.choices[0].message.content
            
            # สร้างภาพ 3D
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D Pixar style character {gender} in {country} winter outfit with heavy coat and boots", n=1)
            return analysis_feedback, recommendation, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "โปรดตรวจสอบ API Key ของคุณ", None
    else:
        # โหมดฟรี (จำลองข้อมูลตาม image_533a73)
        return "วิเคราะห์เบื้องต้น: ควรเพิ่มเสื้อโค้ทหนาและถุงมือ", "เตรียมชุดกันหนาวที่เหมาะสมกับอุณหภูมิติดลบ", "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"

# --- 🎨 หน้า Login (อ้างอิง image_53cc78) ---
def login_page():
    st.markdown("""<style>.login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; } .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; }</style>""", unsafe_allow_html=True)
    st.markdown('<div class="login-box"><h1>Tripnify Login</h1>', unsafe_allow_html=True)
    st.text_input("อีเมล")
    st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        st.session_state['logged_in'] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>.analysis-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; line-height: 1.6; } .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        lang = st.radio("Language", ["Thai", "English"])
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("ใช้งานโหมดฟรี", value=not api_key)
        if st.button("ออกจากระบบ"): st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.5])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Vietnam"])
            activity = st.selectbox("กิจกรรม", ["ท่องเที่ยว", "ธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png'])
            run_btn = st.button("✨ เริ่มวิเคราะห์")

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang)
            
            # --- ลำดับที่ 1: ผลวิเคราะห์ (AI Critique) ---
            st.markdown("### 🔍 AI Critique & Analysis")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            st.divider()

            # --- ลำดับที่ 2: รูป 3D ---
            st.markdown("### 🎭 Outfit Visual (3D)")
            if img_url: st.image(img_url, use_container_width=True)
            
            # --- ลำดับที่ 3: ชุดที่ควรเตรียม (ไม่มีชื่อวัน) ---
            st.markdown("### 📋 ประเภทชุดที่ควรเตรียม")
            st.info(r_out)
            st.divider()

            # --- ลำดับที่ 4: แหล่งช้อปปิ้ง (อ้างอิง image_53cd37) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งไอเทมแนะนำ")
            items = [
                {"n": "เสื้อโค้ทกันหนาว (Down Jacket)", "ref": "1"},
                {"name": "ชุดลองจอน (Heattech)", "ref": "2"},
                {"name": "รองเท้าบูทบุขน", "ref": "4"},
                {"name": "ถุงมือและผ้าพันคอ", "ref": "3,5"},
                {"name": "แผ่นแปะความร้อน (Hot Pack)", "ref": "5"}
            ]
            for i in items:
                name = i.get('n') or i.get('name')
                st.markdown(f"""<div class="shop-card"><strong>🔹 {name}</strong> (อ้างอิงข้อ {i['ref']})<br>
                <a href='https://shopee.co.th/search?keyword={quote_plus(name)}' target='_blank'>🛒 Shopee</a> | 
                <a href='https://www.lazada.co.th/catalog/?q={quote_plus(name)}' target='_blank'>🛒 Lazada</a></div>""", unsafe_allow_html=True)
        else:
            st.info("👈 กรุณาอัปโหลดรูปและกดเริ่มวิเคราะห์")

# --- ระบบจัดการหน้า ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
