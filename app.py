import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ 1. ฟังก์ชันประมวลผล Logic ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang, start_date, end_date):
    # คำนวณจำนวนวันเดินทาง
    days = (end_date - start_date).days + 1
    
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            # ข้อ 8: Prompt วิเคราะห์ภาพ (Critique)
            p_critique = f"วิเคราะห์ภาพชุดนี้สำหรับอากาศ 1.8°C ที่ {country} (เดินทาง {days} วัน) สรุป 5 ข้อ: 1.เสื้อนอก 2.กางเกง 3.หัว/คอ 4.เท้า 5.อุปกรณ์เสริม"
            # ข้อ 10: Prompt รายละเอียดเพิ่มเติม (ดึงข้อมูลวันเดินทางไปคำนวณ)
            p_detail = f"แนะนำการเตรียมกระเป๋าและชุดเพิ่มเติมสำหรับไป {country} จำนวน {days} วัน กิจกรรม {activity} ให้ละเอียดที่สุด"

            v_out = "ไม่พบรูปภาพ"
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
            
            r_resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": p_detail}])
            r_out = r_resp.choices[0].message.content
            
            # เจนภาพ 3D
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter gear Pixar style", n=1)
            return v_out, r_out, img_resp.data[0].url
        except Exception as e:
            return f"Error: {e}", "ตรวจสอบ API Key", None
    else:
        # --- ข้อ 1: โหมดฟรี จัดเรียงตามภาพต้นฉบับ ---
        v_free = """
        1. **เสื้อชั้นนอก:** ควรเปลี่ยนเป็น Padding Jacket หรือโค้ทหนา
        2. **กางเกง:** ควรเพิ่มลองจอนหรือเลกกิ้งกันหนาวชั้นใน
        3. **ส่วนศีรษะ:** แนะนำให้เพิ่มหมวกไหมพรมและผ้าพันคอ
        4. **เท้า:** ควรใช้ถุงเท้าหนาและรองเท้าที่กันลมได้ดี
        5. **เสริม:** เตรียมถุงมือและแผ่นแปะความร้อนเพิ่มเติม
        """
        r_free = f"คำแนะนำเบื้องต้น: สำหรับการเดินทาง {days} วัน ควรเตรียมชุดลองจอนสำรองไว้อย่างน้อย {max(1, days//2)} ชุด"
        sample_img = "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"
        return v_free, r_free, sample_img

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    # CSS ป้องกันหน้าขาวและจัด Style
    st.markdown("""<style>
        .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
        .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        lang = st.radio("Language", ["Thai", "English"], key='lang_choice')
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี", value=not api_key)
        if st.button("ออกจากระบบ"): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Vietnam"])
            
            # --- ข้อ 2: เพิ่มวันที่ไป-กลับ ทั้ง 2 โหมด ---
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input("วันที่เริ่ม", datetime.now())
            end_date = d_col2.date_input("วันที่สิ้นสุด", datetime.now() + timedelta(days=5))
            
            activity = st.selectbox("กิจกรรม", ["ท่องเที่ยว", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png'])
            run_btn = st.button("✨ เริ่มวิเคราะห์")

    with col2:
      with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang, start_date, end_date)
            
            # 1. แสดงผลวิเคราะห์การแต่งกาย (โหมดฟรีจะเรียง 1-5 ตามภาพ)
            st.markdown("### 🔍 ผลวิเคราะห์การแต่งกาย")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            # 2. แสดงภาพจำลอง
            st.markdown("### 🎭 ภาพจำลองแนะนำ")
            if img_url: st.image(img_url, use_container_width=True)
            
            # --- 3. ส่วนที่ปรับปรุง: ดึงข้อมูล 5 ข้อมาเรียบเรียงใหม่ ---
            st.markdown("### 📋 สิ่งที่ควรเตรียมเพิ่มเติม (สรุปจากผลวิเคราะห์)")
            
            # รายการ 5 ข้อหลักที่ดึงมาจากหัวข้อวิเคราะห์
            essentials = [
                "เสื้อผ้าชั้นนอก (เสื้อโค้ท/Padding Jacket)",
                "กางเกง (บุขน/Fleece Lined)",
                "ส่วนศีรษะ (หมวกไหมพรม/ผ้าพันคอ)",
                "รองเท้า (รองเท้าบูท/ถุงเท้าหนา)",
                "อุปกรณ์เสริม (ถุงมือ/แผ่นแปะความร้อน)"
            ]
            
            for i, item in enumerate(essentials, 1):
                st.write(f"{i}. **{item}**")
            
            # รายละเอียดเชิงลึกที่ได้จาก OpenAI (ถ้ามี)
            with st.expander("คลิกเพื่อดูคำแนะนำการจัดกระเป๋าโดยละเอียด"):
                st.info(r_out)

            # --- 4. ส่วนแหล่งช้อปปิ้งแนะนำ (เชื่อมโยงข้อมูลข้างบน) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งแนะนำ")
            for it in essentials:
                # ตัดคำในวงเล็บออกเพื่อใช้ค้นหา
                search_term = it.split('(')[0].strip()
                st.markdown(f"""
                <div class="shop-card">
                    <strong>🔹 จัดเตรียม: {it}</strong><br>
                    <a href='https://shopee.co.th/search?keyword={quote_plus(search_term)}' target='_blank'>🛒 Shopee</a> | 
                    <a href='https://www.lazada.co.th/catalog/?q={quote_plus(search_term)}' target='_blank'>🛒 Lazada</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลการเดินทางและกดปุ่มเริ่มวิเคราะห์")
def login_page():
    st.title("Tripnify Login")
    user = st.text_input("Username")
    if st.button("Login"):
        st.session_state['logged_in'] = True
        st.rerun()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
