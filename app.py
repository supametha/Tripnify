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
                    {"type": "text", "text": "Analyze these clothes and give 3 short English keywords for fashion items."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]}]
            )
            analysis_res = v_resp.choices[0].message.content
        
        r_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"แนะนำการแต่งกายไป {country} สำหรับกิจกรรม {activity} โดยเน้นสไตล์ที่เหมาะสมกับเพศ {gender} ขอคำแนะนำสั้นๆ 3-4 บรรทัด"}]
        )
        recommendation = r_resp.choices[0].message.content

        img_resp = client.images.generate(
            model="dall-e-3",
            prompt=f"A 3D high-quality fashion character, {gender}, wearing: {recommendation}. White studio background, professional lighting.",
            n=1, size="1024x1024"
        )
        return analysis_res, recommendation, img_resp.data[0].url
    except Exception as e:
        return str(e), None, None

# --- 🎨 หน้า Login (White Minimalist) ---
def login_page():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
        .stApp { background-color: #ffffff; }
        .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; max-width: 450px; margin: auto; }
        .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 10px !important; border: none !important; padding: 12px !important; }
        </style>
    """, unsafe_allow_html=True)
    e1, col_login, e2 = st.columns([0.1, 1, 0.1])
    with col_login:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='color:#1e293b; margin-bottom:30px;'>Tripnify Login</h2>", unsafe_allow_html=True)
        user = st.text_input("อีเมล", placeholder="email@example.com", label_visibility="collapsed")
        pwd = st.text_input("รหัสผ่าน", type="password", placeholder="Password", label_visibility="collapsed")
        if st.button("เข้าสู่ระบบ"):
            st.session_state['logged_in'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard (ปรับปรุงตามเงื่อนไขใหม่) ---
def main_dashboard():
    # CSS สำหรับ Dashboard โทนขาว
    st.markdown("""
        <style>
        .main-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #f1f5f9; margin-bottom: 20px; }
        .shop-card { background: #f8fafc; padding: 15px; border-radius: 12px; border-left: 4px solid #4f46e5; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ การตั้งค่า")
        api_key = st.text_input("OpenAI API Key", type="password")
        st.divider()
        if st.button("ออกจากระบบ"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("👗 Tripnify Dashboard")
    
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        country = st.selectbox("📍 เลือกประเทศปลายทาง", ["South Korea", "Japan", "Thailand", "Vietnam", "Taiwan"])
        activity = st.selectbox("🏃 ประเภทกิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย/เดินป่า", "ถ่ายรูป/Fashion", "ช้อปปิ้งในเมือง"])
        gender = st.radio("👤 เพศ", ["ชาย", "หญิง", "ไม่ระบุ"])
        img_file = st.file_uploader("📸 อัปโหลดรูปชุดที่มี (AI จะช่วยวิเคราะห์)", type=['jpg', 'png'])
        run_btn = st.button("✨ เริ่มวิเคราะห์แผนการแต่งกาย")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if run_btn:
            if not api_key:
                st.warning("⚠️ กรุณาใส่ OpenAI API Key ในแถบด้านข้าง")
            else:
                with st.spinner("🚀 AI กำลังประมวลผลข้อมูล..."):
                    v_out, r_out, img_url = process_ai_logic(api_key, country, activity, gender, img_file)
                    
                    if r_out:
                        # 1. แสดงส่วนอากาศและคำเตือน (เฉพาะหลังกดปุ่ม)
                        st.markdown("### 📋 ข้อมูลการเดินทาง")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("ประเทศ", country)
                        m2.metric("อากาศโดยประมาณ", "1.8°C")
                        m3.metric("คำแนะนำ", "เตรียมชุดกันหนาว")
                        
                        st.divider()
                        
                        # 2. แสดงผลลัพธ์ AI
                        st.image(img_url, caption="ภาพจำลองชุดที่แนะนำโดย AI")
                        st.success(f"**คำแนะนำจาก AI:**\n\n{r_out}")
                        
                        # 3. จอแสดงผลเชื่อมโยงสินค้า E-commerce
                        st.markdown("### 🛍️ รายการสินค้าที่แนะนำ (ช้อปปิ้ง)")
                        # ดึงคำสำคัญจาก AI มาสร้างลิงก์ (ตัวอย่าง: Jacket, Scarf, Boots)
                        items_to_buy = re.findall(r'\b[A-Z][a-z]+\b', r_out)[:3]
                        if not items_to_buy: items_to_buy = ["Fashion", "Travel Gear"]
                        
                        for item in items_to_buy:
                            enc_item = quote_plus(item)
                            st.markdown(f"""
                                <div class="shop-card">
                                    <span style='font-weight:500; color:#1e293b;'>🔍 ค้นหา {item}:</span><br>
                                    <a href='https://shopee.co.th/search?keyword={enc_item}' target='_blank' style='color:#4f46e5; text-decoration:none;'>ดูบน Shopee</a> | 
                                    <a href='https://www.lazada.co.th/catalog/?q={enc_item}' target='_blank' style='color:#4f46e5; text-decoration:none;'>ดูบน Lazada</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("👋 ยินดีต้อนรับ! เลือกประเทศและกิจกรรมทางซ้ายเพื่อเริ่มการวิเคราะห์")

# --- ส่วนควบคุมหน้าจอ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
