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
                5. **แผ่นแปะความร้อน**: ช่วยเพิ่มความอุ่นในจุดที่เลือดหมวนเวียนไปไม่ถึง เช่น ปลายนิ้ว
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
    # --- CSS ปรับแต่งให้ปุ่มเนียนไปกับกล่อง ---
    st.markdown("""
        <style>
        /* ซ่อนตัวหนังสือเดิมของปุ่ม Streamlit */
        div.stButton > button {
            color: transparent;
            background-color: transparent;
            border: 1px solid #dadce0;
            height: 50px;
            width: 100%;
            border-radius: 8px;
            position: relative;
            z-index: 1;
        }
        
        /* เมื่อเอาเมาส์วางให้มีสีพื้นหลังอ่อนๆ */
        div.stButton > button:hover {
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            color: transparent;
        }

        /* กล่อง Social ที่เราสร้างขึ้นมาซ้อน */
        .custom-social-btn {
            position: absolute;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 50px;
            top: 0;
            pointer-events: none; /* ให้คลิกทะลุไปที่ปุ่มข้างล่าง */
            z-index: 2;
        }
        
        .fb-style {
            background-color: #3b5998; /* สีน้ำเงิน Facebook */
            border-radius: 8px;
        }
        
        .fb-text { color: white !important; }
        .social-text {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 500;
            font-size: 16px;
            color: #3c4043;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🌍 Tripnify Login")
    st.subheader("จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ")
    st.markdown("---")
    
    google_logo = "https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"
    facebook_logo = "https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg"

    # --- ปุ่ม Google ---
    # ใช้ container เพื่อคุมตำแหน่งปุ่ม
    c1 = st.container()
    with c1:
        st.markdown(f'''
            <div class="custom-social-btn">
                <img src="{google_logo}" width="20px" style="margin-right: 12px;">
                <span class="social-text">เข้าสู่ระบบด้วยบัญชี Google</span>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("google_hidden_btn", key="google_login", use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()

    st.write("") # เว้นระยะห่าง

    # --- ปุ่ม Facebook ---
    c2 = st.container()
    with c2:
        st.markdown(f'''
            <div class="custom-social-btn fb-style">
                <img src="{facebook_logo}" width="22px" style="margin-right: 12px; filter: brightness(0) invert(1);">
                <span class="social-text fb-text">เข้าสู่ระบบด้วยบัญชี Facebook</span>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("fb_hidden_btn", key="fb_login", use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()
    
    st.markdown("<p style='text-align: center; color: gray; margin: 25px 0;'>หรือ</p>", unsafe_allow_html=True)
    
    # --- ส่วน Login ปกติ ---
    user = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="กรอกชื่อผู้ใช้งาน")
    password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน")
    
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("🔑 เข้าสู่ระบบ", use_container_width=True):
            if user: 
                st.session_state['logged_in'] = True
                st.rerun()
    with col_r:
        if st.button("👤 ทดลองใช้ (Guest)", use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("<center>Tripnify - Travel Smart, Dress Right</center>", unsafe_allow_html=True)

# --- 🚀 4. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
