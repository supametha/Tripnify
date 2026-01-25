import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ 1. ฟังก์ชันหลักในการประมวลผล ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang):
    # ข้อ 8: ปรับ Prompt ให้วิเคราะห์แบบแยก 5 ส่วนหลักเพื่อนำไปใช้ต่อ
    if lang == "Thai":
        p_critique = "วิเคราะห์รูปชุดนี้สำหรับอากาศ 1.8°C ในเกาหลีใต้ โดยสรุปผลแยกเป็น 5 ข้อหลัก: 1.เสื้อผ้าชั้นนอก 2.กางเกง 3.หมวกและผ้าพันคอ 4.รองเท้า 5.อุปกรณ์เสริมอื่นๆ ประเมินว่าที่ใส่มาเหมาะสมไหมและควรเปลี่ยนเป็นอะไร"
        p_outfit = f"แนะนำการแต่งกายไป {country} กิจกรรม {activity} สรุปสั้นๆ เป็นประเภทชุดที่ต้องเตรียม (ไม่ระบุวัน)"
    else:
        p_critique = "Critique this outfit for 1.8°C in 5 points: 1.Outerwear 2.Pants 3.Headwear 4.Footwear 5.Accessories. Evaluate suitability and suggested changes."
        p_outfit = f"Recommend clothing for {country} activity {activity} as categories (No daily names)."

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
            img_prompt = f"3D Pixar style character {gender} in {country} wearing professional winter gear for 1.8C weather, based on expert suggestions, high detail."
            img_resp = client.images.generate(model="dall-e-3", prompt=img_prompt, n=1)
            return v_out, r_out, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "Please check your API Key", None
    else:
        # --- โหมดทดลองใช้ฟรี (ปรับตามข้อกำหนดใหม่) ---
        v_free = """
        **วิเคราะห์ภาพถ่ายเบื้องต้น:**
        1. **เสื้อชั้นนอก:** ควรใช้ Padding Jacket หรือ Down Coat ที่หนาขึ้น
        2. **กางเกง:** แนะนำกางเกงบุขน (Fleece Lined) หรือ Heattech ชั้นใน
        3. **ส่วนศีรษะ:** ควรเพิ่มหมวกไหมพรมเพื่อป้องกันการสูญเสียความร้อน
        4. **เท้า:** รองเท้าผ้าใบปกติอาจไม่อุ่นพอ ควรใช้ถุงเท้าขนแกะ
        5. **เสริม:** ควรเตรียมถุงมือและแผ่นแปะความร้อน (Hot Pack)
        """ if lang == "Thai" else "Basic Critique: Outfit too thin for 1.8°C. Need thicker layers, thermal pants, and winter accessories."
        
        r_free = "ข้อมูลเพิ่มเติม: สำหรับอุณหภูมิติดลบหรือใกล้ 0 องศา การแต่งกายแบบ 3 เลเยอร์ (Base, Middle, Outer) คือหัวใจสำคัญ"
        # ภาพประกอบโหมดฟรี
        sample_img = "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000" 
        return v_free, r_free, sample_img

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; line-height: 1.6; }
        .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
        .buy-header { color: #d33682; font-weight: bold; margin-top: 15px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
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
            st.subheader("🗓️ " + ("ข้อมูลการเดินทาง" if lang == "Thai" else "Travel Info"))
            country = st.selectbox("จุดหมาย (Destination)", ["South Korea", "Japan", "Vietnam"])
            activity = st.selectbox("กิจกรรม (Activity)", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ (Gender)", ["ชาย", "หญิง"] if lang == "Thai" else ["Male", "Female"])
            img_file = st.file_uploader("📸 " + ("อัปโหลดรูปชุด" if lang == "Thai" else "Upload Outfit"), type=['jpg', 'png'])
            run_btn = st.button("✨ " + ("เริ่มวิเคราะห์" if lang == "Thai" else "Analyze"))

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang)
            
            # 1. ผลวิเคราะห์การแต่งกาย (AI Critique)
            st.markdown("### 🔍 " + ("ผลวิเคราะห์การแต่งกาย" if lang == "Thai" else "Outfit Analysis"))
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            st.divider()

            # 2. ภาพจำลองแนะนำ (3D Visual)
            st.markdown("### 🎭 " + ("ภาพจำลองแนะนำ" if lang == "Thai" else "3D Visual Guide"))
            if img_url: st.image(img_url, use_container_width=True)
            
            # 3. คำแนะนำประเภทชุด (แยกส่วน)
            st.markdown("### 📋 " + ("คำแนะนำการจัดชุด" if lang == "Thai" else "Outfit Suggestions"))
            st.info(r_out)
            st.divider()

            # 4. สิ่งที่ควรเตรียมเพิ่มเติม (ดึง 5 อย่างหลัก) + แหล่งช้อปปิ้ง
            st.markdown("### 🛒 " + ("รายการที่ควรเลือกซื้อเพิ่ม (5 อย่างหลัก)" if lang == "Thai" else "Must-Buy Items"))
            
            # กำหนดรายการสินค้าที่สอดคล้องกับหัวข้อวิเคราะห์ 5 ส่วน
            items = [
                {"name": "เสื้อโค้ทกันหนาวหนาพิเศษ", "en": "Heavy Winter Coat"},
                {"name": "กางเกงบุขน / ลองจอน", "en": "Thermal Pants / Heattech"},
                {"name": "หมวกไหมพรม / ผ้าพันคอ", "en": "Beanie / Scarf"},
                {"name": "รองเท้าลุยหิมะ / บูท", "en": "Winter Boots"},
                {"name": "ถุงมือ / แผ่นแปะความร้อน", "en": "Gloves / Hot Packs"}
            ]

            for item in items:
                label = item['name'] if lang == "Thai" else item['en']
                st.markdown(f"""<div class="shop-card">
                    <strong>🔹 {label}</strong><br>
                    <a href='https://shopee.co.th/search?keyword={quote_plus(label)}' target='_blank'>🛒 Shopee</a> | 
                    <a href='https://www.lazada.co.th/catalog/?q={quote_plus(label)}' target='_blank'>🛒 Lazada</a>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("👈 " + ("กรุณาอัปโหลดรูปเพื่อเริ่มวิเคราะห์" if lang == "Thai" else "Please upload an image to start."))

# --- 🔐 3. ระบบ Login (ไม่แก้) ---
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

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: 
    main_dashboard()
else: 
    login_page()
