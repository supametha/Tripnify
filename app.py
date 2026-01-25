import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ 1. Logic การดึงข้อมูลและวิเคราะห์ ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang):
    # Prompt วิเคราะห์ภาพ (ข้อ 8) - ปรับการเรียงลำดับตามรูปภาพต้นฉบับ
    if lang == "Thai":
        p_critique = "วิเคราะห์รูปชุดนี้สำหรับอากาศ 1.8°C ในเกาหลีใต้ ประเมินตามหัวข้อ: 1.เสื้อผ้าชั้นนอก 2.กางเกง 3.หมวก 4.รองเท้า 5.อุปกรณ์เสริม"
    else:
        p_critique = "Critique this outfit for 1.8°C weather based on: 1.Outerwear 2.Pants 3.Headwear 4.Footwear 5.Accessories."

    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            v_out = "ไม่พบรูปภาพ" if lang == "Thai" else "No image"
            
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
            
            # สร้างภาพจำลอง 3D (ข้อ 9)
            img_prompt = f"3D Pixar style character {gender} in {country} winter clothes, 1.8C professional gear, high quality."
            img_resp = client.images.generate(model="dall-e-3", prompt=img_prompt, n=1)
            return v_out, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", None
    else:
        # โหมดฟรี: ใช้ข้อมูลคงที่ตามภาพต้นฉบับ
        v_free = """ในอุณหภูมิ 1.8°C การแต่งกายนี้อาจไม่เหมาะสมนัก เนื่องจากชุดที่เลือกบางเกินไป:
        1. เสื้อชั้นใน: ควรเพิ่มเสื้อแขนยาวหรือคาร์ดิแกน
        2. กางเกง: ควรเลือกกางเกงผ้าหนาหรือใส่เลกกิ้งด้านใน
        3. รองเท้า: ควรเลือกบูทเพื่อป้องกันเท้าเย็น
        4. อุปกรณ์เสริม: เพิ่มหมวกหรือผ้าพันคอ"""
        sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        return v_free, sample_img

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    # CSS ปรับแต่งกล่องข้อมูล
    st.markdown("""<style>
        .critique-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; color: #92400e; margin-bottom: 20px; }
        .must-buy-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .shop-link { color: #4f46e5; text-decoration: none; font-weight: bold; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        lang = st.radio("Language", ["Thai", "English"], key='lang_choice')
        st.divider()
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี" if lang == "Thai" else "Free Mode", value=not api_key)
        if st.button("ออกจากระบบ"): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.5])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("Destination", ["South Korea", "Japan", "Vietnam"])
            activity = st.selectbox("Activity", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("Gender", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png'])
            run_btn = st.button("✨ เริ่มวิเคราะห์")

    with col2:
        if run_btn:
            v_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang)
            
            # ส่วนที่ 1: ผลวิเคราะห์การแต่งกาย (อ้างอิงจากรูป AI Critique)
            st.markdown("### 🔍 AI Critique & Analysis")
            st.markdown(f'<div class="critique-box">{v_out}</div>', unsafe_allow_html=True)

            # ส่วนที่ 2: ภาพจำลองแนะนำ (ข้อ 9)
            st.markdown("### 🎭 ภาพจำลองแนะนำ (3D Visual)")
            if img_url: st.image(img_url, use_container_width=True)
            st.divider()

            # ส่วนที่ 3 & 4: สิ่งที่ควรเตรียม (5 ข้อหลัก) + แหล่งช้อปปิ้งที่สอดคล้องกัน
            st.markdown("### 🛍️ 5 ไอเทมสำคัญที่ควรเตรียมเพิ่ม")
            
            # ดึงข้อมูลจากส่วนวิเคราะห์มาสร้างรายการซื้อ (สอดคล้องกับข้อความวิเคราะห์)
            must_buy_items = [
                ("เสื้อโค้ทกันหนาว (Down Jacket)", "เน้นแบบกันลมและกันน้ำเพื่อรักษาความอบอุ่น"),
                ("ชุดลองจอน (Heattech)", "ชั้นในสำคัญมากสำหรับอุณหภูมิใกล้ 0°C"),
                ("รองเท้าบูทบุขน", "ป้องกันความหนาวเย็นจากพื้นดิน"),
                ("หมวกและผ้าพันคอ", "ช่วยเก็บความร้อนในส่วนหัวและลำคอ"),
                ("แผ่นแปะความร้อน (Hot Pack)", "ตัวช่วยสำหรับกิจกรรมกลางแจ้งนานๆ")
            ]

            for title, desc in must_buy_items:
                st.markdown(f"""
                <div class="must-buy-card">
                    <strong>🔹 {title}</strong><br>
                    <small>{desc}</small><br>
                    <a class="shop-link" href="https://shopee.co.th/search?keyword={quote_plus(title)}">🛒 Shopee</a> | 
                    <a class="shop-link" href="https://www.lazada.co.th/catalog/?q={quote_plus(title)}">🛒 Lazada</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณาอัปโหลดรูปชุดของคุณเพื่อเริ่มการวิเคราะห์")

# --- ระบบ Login ---
def login_page():
    st.markdown('<div style="text-align:center"><h1>Tripnify Login</h1></div>', unsafe_allow_html=True)
    if st.button("เข้าสู่ระบบ (Demo)"): 
        st.session_state['logged_in'] = True
        st.rerun()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
