import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ 1. ฟังก์ชันประมวลผล Logic ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang, start_date, end_date):
    days = (end_date - start_date).days + 1
    
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            p_critique = f"วิเคราะห์ภาพชุดนี้สำหรับอากาศ 1.8°C ที่ {country} (เดินทาง {days} วัน) สรุป 5 ข้อ: 1.เสื้อนอก 2.กางเกง 3.หัว/คอ 4.เท้า 5.อุปกรณ์เสริม"
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
            
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter gear Pixar style", n=1)
            return v_out, r_out, img_resp.data[0].url
        except Exception as e:
            return f"Error: {e}", "ตรวจสอบ API Key", None
    else:
        v_free = "1. **เสื้อชั้นนอก**: ควรใช้ Padding Jacket หรือ Down Coat ที่หนาขึ้น\n2. **กางเกง**: แนะนำกางเกงบุขน (Fleece Lined) หรือ Heattech ชั้นใน\n3. **ส่วนศีรษะ**: ควรเพิ่มหมวกไหมพรมเพื่อป้องกันการสูญเสียความร้อน\n4. **เท้า**: รองเท้าผ้าใบปกติอาจไม่อุ่นพอ ควรใช้ถุงเท้าขนแกะ\n5. **เสริม**: ควรเตรียมถุงมือและแผ่นแปะความร้อน (Hot Pack)"
        r_free = f"คำแนะนำเบื้องต้น: สำหรับ {days} วัน ควรเตรียมชุดลองจอนสำรองไว้อย่างน้อย {max(1, days//2)} ชุด"
        sample_img = "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"
        return v_free, r_free, sample_img

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
        .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
        .stButton > button { border-radius: 8px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        lang = st.radio("Language", ["Thai", "English"], key='lang_choice')
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี", value=not api_key)
        if st.button("ออกจากระบบ", use_container_width=True): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("จุดหมาย", ["ญี่ปุ่น", "เกาหลีใต้", "เวียดนาม", "ไต้หวัน", "จีน"])
            
            d_col1, d_col2 = st.columns(2)
            start_date = d_col1.date_input("วันที่เริ่ม", datetime.now())
            end_date = d_col2.date_input("วันที่สิ้นสุด", datetime.now() + timedelta(days=5))
            
            activity = st.selectbox("กิจกรรม", ["ท่องเที่ยวถ่ายรูป", "เล่นสกี/กิจกรรมหิมะ", "ติดต่อธุรกิจ", "ผจญภัย/เดินป่า", "ช้อปปิ้งในเมือง"])
            gender = st.radio("เพศ", ["ชาย", "หญิง"])
            
            img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png', 'jpeg'])
            camera_file = st.camera_input("🤳 หรือเปิดกล้องถ่ายภาพชุด")

            if camera_file:
                img_file = camera_file
                
            run_btn = st.button("✨ เริ่มวิเคราะห์", use_container_width=True)

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang, start_date, end_date)
            
            st.markdown(f"### 📍 จุดหมาย: {country}")
            
            w_col1, w_col2 = st.columns([1, 2])
            with w_col1:
                st.metric(label="🌡️ อุณหภูมิเฉลี่ย", value="1.8°C")
            
            with w_col2:
                st.warning("⚠️ **สถานะอากาศ: หนาวจัด** | โปรดเตรียมเครื่องกันหนาวให้พร้อม")
            
            st.divider()

            st.markdown("### 🔍 ผลวิเคราะห์การแต่งกาย")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            if img_url: 
                st.markdown("### 🎭 ภาพจำลองแนะนำ")
                st.image(img_url, use_container_width=True)
            
            st.markdown("### 📋 สิ่งที่ควรเตรียมเพิ่มเติม")
            essentials = [
                "เสื้อโค้ทกันหนาวหนาพิเศษ (Padding/Down Jacket)",
                "กางเกงบุขนกันหนาว (Fleece Lined Pants)",
                "หมวกไหมพรมและผ้าพันคอ (Winter Accessories)",
                "รองเท้าบูทกันหนาว (Winter Boots)",
                "แผ่นแปะความร้อนและถุงมือ (Hot Packs & Gloves)"
            ]
            
            for i, item in enumerate(essentials, 1):
                st.write(f"{i}. **{item}**")
            
            with st.expander("💡 คลิกเพื่อดูรายละเอียดและประโยชน์ของแต่ละไอเทม"):
                st.markdown("""
                1. **เสื้อโค้ทกันหนาว**: ช่วยกักเก็บความร้อนและกันลมหนาว 1.8°C ได้อย่างมีประสิทธิภาพ
                2. **กางเกงบุขน**: ชั้นขนด้านในเป็นฉนวนกันความเย็น ป้องกันผิวอักเสบจากความเย็นจัด
                3. **หมวกและผ้าพันคอ**: รักษาอุณหภูมิศีรษะและลำคอ ไม่ให้ลมหนาวเข้าสู่ร่างกาย
                4. **รองเท้าบูท**: ป้องกันความเย็นจากพื้นและกันความชื้นจากหิมะหรือฝน
                5. **แผ่นแปะความร้อน**: ช่วยเพิ่มความอุ่นในจุดที่เลือดหมุนเวียนไปไม่ถึง เช่น ปลายนิ้ว
                """)

            st.markdown("### 🛍️ แหล่งช้อปปิ้งแนะนำ")
            for it in essentials:
                search_term = it.split('(')[0].strip()
                st.markdown(f"""
                <div class="shop-card">
                    <strong>🔹 จัดเตรียมเพิ่ม: {search_term}</strong><br>
                    <a href='https://shopee.co.th/search?keyword={quote_plus(search_term)}' target='_blank'>🛒 Shopee</a> | 
                    <a href='https://www.lazada.co.th/catalog/?q={quote_plus(search_term)}' target='_blank'>🛒 Lazada</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลการเดินทางและกดปุ่มเริ่มวิเคราะห์")

# --- 🔑 3. หน้า Login ---
def login_page():
    st.markdown("""
        <style>
        .stButton > button { border-radius: 8px; height: 3.5em; font-weight: 500; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🌍 Tripnify Login")
    st.subheader("จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ")
    st.markdown("---")
    
    google_logo_url = "https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"

    # สร้างปุ่ม Google อันเดียว และใช้ CSS จัดตำแหน่งโลโก้ให้ตรงกับตัวอักษร
    if st.button("ลงชื่อเข้าใช้ด้วย Google", use_container_width=True, key="google_login_main"):
        st.session_state['logged_in'] = True
        st.rerun()

   # --- เริ่มต้นส่วนปุ่ม Google ที่ล็อคตำแหน่งโลโก้ (แทนที่บรรทัด 155-175) ---
    google_logo_url = "https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"

    # ใช้ HTML/CSS สร้างปุ่มที่โลโก้และข้อความอยู่บรรทัดเดียวกันเป๊ะ
    st.markdown(f"""
        <style>
            .google-btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                cursor: pointer;
                width: 100%;
                margin-bottom: 10px;
                transition: background-color 0.2s;
            }}
            .google-btn:hover {{
                background-color: #f8f9fa;
            }}
            .google-btn img {{
                width: 20px;
                margin-right: 12px;
            }}
            .google-btn span {{
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                color: #444;
            }}
        </style>
        <div class="google-btn" onclick="document.getElementById('hidden_google_btn').click();">
            <img src="{google_logo_url}">
            <span>ลงชื่อเข้าใช้ด้วย Google</span>
        </div>
    """, unsafe_allow_html=True)

    # ปุ่มจริงที่ถูกซ่อนไว้เพื่อใช้รับคำสั่งจากปุ่ม HTML ด้านบน
    if st.button("Google Login Hidden", key="hidden_google_btn", use_container_width=True):
        st.session_state['logged_in'] = True
        st.rerun()
    
    # ซ่อนปุ่มจริงที่หน้าตาไม่สวยด้วย CSS
    st.markdown("<style>#hidden_google_btn { display: none; }</style>", unsafe_allow_html=True)
    # --- สิ้นสุดส่วนปุ่ม Google ---
