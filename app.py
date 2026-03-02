import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ระบบจัดการภาษา ---
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา (Language)",
        "theme_label": "โหมดแสดงผล (มืด/สว่าง)",
        "api_label": "OpenAI API Key",
        "free_mode": "โหมดใช้งานฟรี",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "ประเทศปลายทาง",
        "city": "เมือง",
        "start_date": "วันที่ไป",
        "end_date": "วันที่กลับ",
        "activity_label": "กิจกรรม",
        "activities": ["ท่องเที่ยวถ่ายรูป", "ติดต่อธุรกิจ", "กิจกรรมหิมะ/สกี", "ผจญภัย/เดินป่า", "ช้อปปิ้ง"],
        "gender": "ระบุเพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload_section": "📸 จัดการรูปภาพ",
        "run_btn": "✨ เริ่มวิเคราะห์ชุดแต่งกาย",
        "temp_label": "🌡️ อุณหภูมิเฉลี่ย",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้",
        "essentials": ["เสื้อโค้ทกันหนาว", "กางเกงบุขน", "ถุงมือกันหนาว", "แผ่นแปะความร้อน"]
    },
    "English": {
        "settings": "⚙️ System Settings",
        "lang_label": "Language",
        "theme_label": "Display Mode (Dark/Light)",
        "api_label": "OpenAI API Key",
        "free_mode": "Free Mode",
        "logout": "Log Out",
        "travel_info": "🗓️ Travel Info",
        "dest": "Destination",
        "city": "City",
        "start_date": "Departure",
        "end_date": "Return",
        "activity_label": "Activities",
        "activities": ["Photography", "Business", "Ski/Snow", "Hiking/Adventure", "Shopping"],
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "upload_section": "📸 Image Management",
        "run_btn": "✨ Start Analysis",
        "temp_label": "🌡️ Avg Temp",
        "analysis_title": "🔍 Outfit Analysis",
        "shop_title": "🛍️ Recommended Shopping",
        "login_sub": "Smart Outfit Analysis for Your Trip",
        "login_btn": "🔑 Login",
        "reg_btn": "📝 Register",
        "guest_btn": "👤 Guest",
        "essentials": ["Winter Coat", "Fleece Pants", "Winter Gloves", "Heat Packs"]
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์"],
    "ไต้หวัน": ["ไทเป", "เกาสง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้"]
}


# -------------------------------
# 🎭 3D Model Preview (Premium Version)
# -------------------------------
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    
    # ตรวจสอบเพศที่เลือก เพื่อดึงรูปตัวละครที่เหมาะสม
    gender = st.session_state.get('gender_val', 'ชาย')
    
    # คุณสามารถเปลี่ยน URL รูปภาพเหล่านี้เป็นรูปตัวละคร 3D ของคุณเองได้
    # แนะนำใช้ไฟล์ PNG ที่มีพื้นหลังโปร่งใส
    if gender == 'ชาย' or gender == 'Male':
        char_img = "https://img.freepik.com/free-psd/3d-illustration-person-with-sunglasses_23-2149436188.jpg" # ตัวอย่างรูปชาย
    else:
        char_img = "https://img.freepik.com/free-psd/3d-rendering-character-with-winter-clothes_23-2149436192.jpg" # ตัวอย่างรูปหญิง

    # ส่วนของ HTML และ CSS เพื่อสร้าง Preview ที่สวยงาม
    components.html(f"""
        <style>
            .viewer-container {{
                width: 100%;
                height: 400px;
                background: radial-gradient(circle, #1e293b 0%, #020617 100%);
                border-radius: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                border: 2px solid #6366f1;
                box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
                cursor: grab;
            }}
            .viewer-container:active {{ cursor: grabbing; }}
            
            #character-sprite {{
                height: 80%;
                filter: drop-shadow(0 10px 15px rgba(0,0,0,0.5));
                transition: transform 0.1s ease-out;
                user-select: none;
                -webkit-user-drag: none;
            }}
            
            .overlay-hint {{
                position: absolute;
                bottom: 20px;
                background: rgba(0,0,0,0.4);
                color: #e2e8f0;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                backdrop-filter: blur(4px);
                pointer-events: none;
            }}
        </style>

        <div class="viewer-container" id="viewer">
            <img id="character-sprite" src="{char_img}" alt="3D Character">
            <div class="overlay-hint">[ ลากเมาส์เพื่อหมุนดูชุด 360° ]</div>
        </div>

        <script>
            const viewer = document.getElementById('viewer');
            const sprite = document.getElementById('character-sprite');
            let isDragging = false;
            let startX = 0;
            let currentRotation = 0;

            viewer.addEventListener('mousedown', (e) => {{
                isDragging = true;
                startX = e.pageX;
            }});

            window.addEventListener('mouseup', () => isDragging = false);

            window.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;
                const deltaX = e.pageX - startX;
                currentRotation += deltaX * 0.5;
                
                // การจำลองการหมุน 3D แบบนุ่มนวล
                sprite.style.transform = `perspective(1000px) rotateY(${{currentRotation}}deg)`;
                startX = e.pageX;
            }});
        </script>
    """, height=420)
# -------------------------------
# ⚙️ Analysis Logic
# -------------------------------
def process_analysis(api_key, city, country, activity, free_mode, image, start, end):
    days = (end - start).days + 1
    if api_key and not free_mode and image:
        client = OpenAI(api_key=api_key)
        b64 = base64.b64encode(image.getvalue()).decode()
        prompt = f"""
        วิเคราะห์การแต่งกายสำหรับ {city} ประเทศ{country}
        อุณหภูมิประมาณ 2°C
        กิจกรรม: {activity}
        ระยะเวลา {days} วัน
        ตอบเป็นภาษาไทย
        """
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }]
        )
        return res.choices[0].message.content, True

    return "แนะนำแต่งกายแบบ Layering: Heattech + เสื้อไหมพรม + เสื้อโค้ทกันหนาว", False

# -------------------------------
# --- 🎨 3. หน้า Dashboard ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)

        dark_mode = st.toggle(t["theme_label"], value=False)
        if dark_mode:
            st.markdown("""<style>
                .stApp { background-color: #0f172a; color: #f8fafc; }
                [data-testid="stSidebar"] { background-color: #1e293b; }
                .analysis-box { background: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #334155; padding:20px; border-radius:12px; }
                .shop-card { background: #334155; padding: 15px; border-radius: 10px; border-left: 5px solid #6366f1; margin-bottom: 10px; }
            </style>""", unsafe_allow_html=True)
        else:
            st.markdown("""<style>
                .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
                .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
            </style>""", unsafe_allow_html=True)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    # ---------- LEFT ----------
    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])

            d_col1, d_col2 = st.columns(2)
            start = d_col1.date_input(t["start_date"], datetime.now())
            end = d_col2.date_input(t["end_date"], datetime.now() + timedelta(days=3))

            activity = st.multiselect(
                t["activity_label"],
                t["activities"],
                default=[t["activities"][0]]
            )

            st.session_state['gender_val'] = st.radio(
                t["gender"], [t["male"], t["female"]], horizontal=True
            )

            st.divider()
            st.subheader(t["upload_section"])
            tabs = st.tabs(["📁 คลังภาพ", "📸 ถ่ายภาพ"])
            with tabs[0]:
                img_file = st.file_uploader("", type=['jpg','png','jpeg'])
            with tabs[1]:
                cam_file = st.camera_input("")

            active_img = img_file if img_file else cam_file
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    # ---------- RIGHT ----------
    with col2:
        if run_btn:
            result, is_premium = process_analysis(
                api_key,
                city,
                country,
                activity,
                use_free_mode,
                active_img,
                start,
                end
            )

            # Weather
            w_col1, w_col2 = st.columns([1, 2])
            w_col1.metric(t["temp_label"], "2°C")
            w_col2.warning(f"❄️ สภาพอากาศหนาวจัดใน {city}")

            st.divider()

          # Analysis Text
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{result}</div>', unsafe_allow_html=True)


            # 3D Model (Premium)
            if is_premium:
                render_3d_model()

            # Shopping
            st.divider()
            st.subheader(t["shop_title"])
            for item in t["essentials"]:
                st.markdown(f"""
                    <div class="shop-card">
                        <strong>🔹 {item}</strong><br>
                        <a href="https://shopee.co.th/search?keyword={quote_plus(item)}"
                           target="_blank"
                           style="text-decoration:none;color:#4f46e5;">
                           🛒 คลิกเพื่อช้อปสินค้าที่เกี่ยวข้อง
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์")


# -------------------------------
# --- 🔑 4. หน้า Login (Modern UI) ---
# -------------------------------
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # --- ✨ Enhanced CSS for Modern UX/UI ---
    st.markdown("""
        <style>
        /* จัดการพื้นหลังหน้า Login */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        }
        
        /* Container หลักของ Login Card */
        .login-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            border: 1px solid rgba(255,255,255,0.3);
            margin-top: 20px;
        }

        .header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 30px;
        }

        /* ปรับแต่งโลโก้ */
        .brand-logo {
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
            margin-bottom: 10px;
        }

        /* ปุ่ม Social Login แบบทางการ */
        .social-container {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        div[data-testid="stVerticalBlock"] > div:has(.social-btn-custom) {
            padding: 0px;
        }

        .social-btn-custom {
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px;
            background: white;
            transition: all 0.3s ease;
            cursor: pointer;
            width: 100%;
            margin-bottom: -48px; /* Overlay on Streamlit Button */
            position: relative;
            z-index: 1;
            pointer-events: none;
        }
        
        .social-btn-custom:hover {
            border-color: #6366f1;
            background: #f8fafc;
        }

        .social-icon { width: 18px; margin-right: 10px; }
        .social-text { font-weight: 500; font-size: 14px; color: #475569; }

        /* ปรับแต่ง Input Fields */
        div[data-baseweb="input"] {
            border-radius: 10px !important;
            background-color: white !important;
        }
        
        /* ปรับแต่ง Divider */
        .divider-text {
            display: flex;
            align-items: center;
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            margin: 20px 0;
        }
        .divider-text::before, .divider-text::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #e2e8f0;
        }
        .divider-text span { padding: 0 10px; }

        </style>
    """, unsafe_allow_html=True)

    # --- 🏗️ Layout Structure ---
    _, col_main, _ = st.columns([1, 1.8, 1])

    with col_main:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Header Section
        st.markdown(f"""
            <div class="header-container">
                <img class="brand-logo" src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="90">
                <h1 style='color: #1e293b; font-size: 2.5rem; font-weight: 800; margin-bottom: 0;'>Tripnify</h1>
                <p style='color: #64748b; font-size: 1rem; margin-top: 5px;'>{t['login_sub']}</p>
            </div>
        """, unsafe_allow_html=True)

        # Social Login Buttons
        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png">
            <span class="social-text">Continue with Google</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="g_login", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg">
            <span class="social-text">Continue with Facebook</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="f_login", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        # Divider
        st.markdown('<div class="divider-text"><span>หรือเข้าสู่ระบบด้วยอีเมล</span></div>', unsafe_allow_html=True)

        # Traditional Login Form
        user = st.text_input("ชื่อผู้ใช้งาน", placeholder="example@email.com")
        pwd = st.text_input("รหัสผ่าน", type="password", placeholder="••••••••")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            if user and pwd: # เพิ่ม Validation เบื้องต้น
                st.session_state['logged_in'] = True; st.rerun()
            else:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")

        # Secondary Actions
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_reg, col_gst = st.columns(2)
        with col_reg:
            st.button(f"➕ {t['reg_btn']}", use_container_width=True)
        with col_gst:
            if st.button(f"👤 {t['guest_btn']}", use_container_width=True):
                st.session_state['logged_in'] = True; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer Note
        st.markdown("""
            <p style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 30px;'>
                © 2024 Tripnify - Smart Travel Companion. All rights reserved.
            </p>
        """, unsafe_allow_html=True)
# --- 🚀 5. Main Controller ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state:
    st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
