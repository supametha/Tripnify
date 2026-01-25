import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล ---
def process_logic(api_key, country, activity, gender, travel_days, use_free_mode, uploaded_file, lang):
    # Prompt วิเคราะห์รูปชุด 5 ข้อหลัก (อ้างอิงจาก image_533a73.png)
    prompt_critique = """
    วิเคราะห์รูปภาพการแต่งกายสำหรับอุณหภูมิ 1.8°C ในเกาหลีใต้ โดยให้ผลลัพธ์เป็นภาษาไทยใน 5 หัวข้อหลักดังนี้:
    1. เสื้อผ้าชั้นนอก
    2. กางเกง
    3. หมวก
    4. รองเท้า
    5. อุปกรณ์เสริม
    ให้คำแนะนำที่ชัดเจนว่าควรปรับปรุงหรือเพิ่มชิ้นไหนเพื่อให้กันหนาวได้จริง
    """
    if lang == "English":
        prompt_critique = "Analyze this outfit for 1.8°C. Provide critique in 5 points: Outerwear, Pants, Headwear, Footwear, and Accessories in English."

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
            
            # คำแนะนำการเตรียมชุด (ตัดวันออก) ตาม image_52e75b.png
            r_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"แนะนำประเภทเสื้อผ้าที่ต้องเตรียมสำหรับไป {country} กิจกรรม {activity} อากาศ 1.8C โดยสรุปเป็นประเภทชุด และไม่ต้องระบุชื่อวันจันทร์ถึงอาทิตย์"}]
            )
            recommendation = r_resp.choices[0].message.content
            
            # สร้างภาพ 3D ที่สอดคล้องกับการวิเคราะห์
            img_resp = client.images.generate(model="dall-e-3", prompt=f"A 3D Pixar style character {gender} wearing a complete professional winter outfit for 1.8°C in {country}, including heavy coat, scarf, and boots, high quality", n=1)
            return analysis_feedback, recommendation, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "โปรดลองใหม่อีกครั้ง", None
    else:
        return "โหมดพื้นฐาน: แนะนำเสื้อโค้ทหนาและลองจอน", "เตรียมชุดกันหนาวที่เหมาะสม", "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"

# --- 🎨 หน้า Login ปรับปรุงตาม image_55934c.png ---
def login_page():
    st.markdown("""
        <style>
        .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; }
        .google-btn { display: flex; align-items: center; justify-content: center; width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 12px; cursor: pointer; margin-bottom: 25px; color: #475569; font-weight: 500; }
        .divider { display: flex; align-items: center; margin: 20px 0; color: #cbd5e1; font-size: 12px; }
        .divider::before, .divider::after { content: ''; flex: 1; border-bottom: 1px solid #f1f5f9; }
        .divider span { padding: 0 10px; }
        .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 12px !important; height: 45px; }
        .footer-link { font-size: 14px; color: #6366f1; text-decoration: none; }
        </style>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="google-btn"><img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="18" style="margin-right:10px;"> ดำเนินการต่อด้วย Google</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"><span>หรือเข้าสู่ระบบด้วยอีเมล</span></div>', unsafe_allow_html=True)
    st.text_input("อีเมล")
    st.text_input("รหัสผ่าน", type="password")
    st.markdown('<div style="text-align: right; margin-bottom: 20px;"><a class="footer-link">ลืมรหัสผ่าน?</a></div>', unsafe_allow_html=True)
    if st.button("เข้าสู่ระบบ"): st.session_state['logged_in'] = True; st.rerun()
    st.markdown('<div style="margin-top: 25px; display: flex; justify-content: center; gap: 15px;"><a class="footer-link">สมัครสมาชิกใหม่</a><span style="color: #e2e8f0;">|</span><a class="footer-link" style="color: #64748b;">ทดลองใช้งาน (Guest)</a></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .metric-card { background: #f8fafc; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; }
        .analysis-box { background: #fffbeb; padding: 25px; border-radius: 15px; border: 1px solid #fef3c7; color: #92400e; line-height: 1.8; }
        .shop-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; border-left: 6px solid #4f46e5; margin-bottom: 15px; }
        .tag-buy { background: #eef2ff; color: #4f46e5; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        lang = st.radio("เลือกภาษา / Language", ["Thai", "English"])
        st.divider()
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("ใช้งานโหมดทดลองฟรี", value=not api_key)
        if st.button("ออกจากระบบ"): st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Vietnam"])
            activity = st.selectbox("กิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 อัปโหลดรูปชุดเพื่อวิเคราะห์", type=['jpg', 'png'])
            run_btn = st.button("✨ เริ่มวิเคราะห์แผนการแต่งกาย")

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, 5, use_free_mode, img_file, lang)
            
            # --- ลำดับที่ 1: AI Critique & Analysis (อ้างอิง image_533a73.png) ---
            st.markdown("### 🔍 AI Critique & Analysis")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            st.divider()

            # --- ลำดับที่ 2: ภาพ 3D และคำแนะนำ (Outfit Plan อ้างอิง image_52e75b.png) ---
            st.markdown("### 🎭 แผนภาพและประเภทชุดที่ควรเตรียม")
            if img_url: st.image(img_url, caption="ภาพจำลองชุดที่เหมาะสม", use_container_width=True)
            st.info(r_out)
            
            st.divider()

            # --- ลำดับที่ 3: แหล่งช้อปปิ้ง (Sync ตาม 5 ข้อวิเคราะห์ อ้างอิง image_53cd37.png) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งไอเทมที่ต้องเพิ่ม (ตามการวิเคราะห์)")
            
            # รายการช้อปปิ้งที่สอดคล้องกับ 5 ข้อของการวิเคราะห์
            shopping_list = [
                {"item": "เสื้อโค้ทกันหนาว (Down Jacket / Parka)", "id": "1", "desc": "สำหรับชั้นนอกที่ต้องเพิ่มความอุ่น"},
                {"item": "กางเกงขายาวหนา / เลกกิ้งกันหนาว", "id": "2", "desc": "ป้องกันความหนาวเย็นบริเวณขา"},
                {"item": "หมวกไหมพรม / ผ้าพันคอ", "id": "3", "desc": "เก็บความอบอุ่นส่วนศีรษะและคอ"},
                {"item": "รองเท้าบูทบุขน / กันลื่น", "id": "4", "desc": "สำหรับการเดินในอุณหภูมิต่ำ"},
                {"item": "ถุงมือ / แผ่นแปะความร้อน", "id": "5", "desc": "อุปกรณ์เสริมช่วยกักเก็บความร้อน"}
            ]

            for s in shopping_list:
                st.markdown(f"""
                    <div class="shop-card">
                        <span class="tag-buy">แนะนำสำหรับข้อวิเคราะห์ที่ {s['id']}</span>
                        <div style="margin-top:10px;"><strong>🔹 {s['item']}</strong></div>
                        <div style="font-size:13px; color:#64748b; margin-bottom:10px;">{s['desc']}</div>
                        <a href='https://shopee.co.th/search?keyword={quote_plus(s["item"])}' target='_blank' style='text-decoration:none; color:#4f46e5;'>🛒 Shopee</a> | 
                        <a href='https://www.lazada.co.th/catalog/?q={quote_plus(s["item"])}' target='_blank' style='text-decoration:none; color:#4f46e5; margin-left:15px;'>🛒 Lazada</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
