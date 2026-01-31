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
# 🎭 3D Model (Premium)
# -------------------------------
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width:100%;height:400px;
        background:radial-gradient(circle,#334155 0%,#0f172a 100%);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        position:relative;cursor:grab;border:2px solid #6366f1;">
            <div id="character" style="font-size:150px;transition:transform 0.1s linear;">🧥</div>
            <div style="position:absolute;bottom:15px;color:#94a3b8;font-size:12px;">
                [ ลากเพื่อหมุนดูชุด 360° ]
            </div>
        </div>
        <script>
            const el=document.getElementById('viewer-3d');
            const char=document.getElementById('character');
            let drag=false,rot=0,startX=0;
            el.onmousedown=e=>{drag=true;startX=e.pageX;};
            window.onmouseup=()=>drag=false;
            window.onmousemove=e=>{
                if(!drag)return;
                const d=e.pageX-startX;
                rot+=d*0.5;
                char.style.transform=`rotateY(${rot}deg)`;
                startX=e.pageX;
            };
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

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            
            d_col1, d_col2 = st.columns(2)
            start = d_col1.date_input(t["start_date"], datetime.now())
            end = d_col2.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            st.session_state['gender_val'] = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            
            st.divider()
            st.subheader(t["upload_section"])
            tabs = st.tabs(["📁 คลังภาพ", "📸 ถ่ายภาพ"])
            with tabs[0]: img_file = st.file_uploader("", type=['jpg','png','jpeg'], key="up_main")
            with tabs[1]: cam_file = st.camera_input("")
            
            active_img = img_file if img_file else cam_file
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            result, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, active_img, current_lang, start, end)
            
            # Weather Widget
            w_col1, w_col2 = st.columns([1, 2])
            w_col1.metric(t["temp_label"], "2°C")
            w_col2.warning(f"❄️ สภาพอากาศหนาวจัดใน {city}")

            st.divider()

            # 🔍 Analysis FIRST
            st.subheader(t["analysis_title"])
            st.markdown(f"<div class='analysis-box'>{result}</div>", unsafe_allow_html=True)

            # 🎭 3D ต่อจากผลวิเคราะห์
            st.divider()
            if is_premium:
                render_3d_model()
            else:
                st.image(
                    "https://images.unsplash.com/photo-1517495306684-21523df7d62c",
                    caption="Reference Outfit (Free Mode)"
                )

            # 🛍️ Shopping
            st.divider()
            st.subheader(t["shop_title"])
            for item in ["เสื้อโค้ทกันหนาว","ถุงมือกันหนาว","รองเท้าบูทกันหนาว"]:
                st.markdown(f"""
                <div class="shop-card">
                    🔹 {item}<br>
                    <a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank">
                        คลิกเพื่อค้นหาสินค้า
                    </a>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("👈 กรอกข้อมูลแล้วกดเริ่มวิเคราะห์")

# -------------------------------
# --- 🔑 4. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    st.markdown("""<style>
        .header-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; padding: 30px 0; }
        .social-btn-custom { display: flex; align-items: center; justify-content: center; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -45px; background: white; position: relative; z-index: 1; pointer-events: none; width: 100%; }
        .social-icon { width: 20px; margin-right: 12px; }
        .social-text { font-weight: 500; font-size: 14px; color: #3c4043; }
    </style>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="header-container">
            <img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="130">
            <h1 style='margin-top: 15px; font-size: 3.5rem; font-weight: bold;'>Tripnify</h1>
            <p style='color: gray; font-size: 1.2rem; margin-top: -15px;'>{t['login_sub']}</p>
        </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png">
            <span class="social-text">เข้าสู่ระบบด้วย Google</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="g_login", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown(f"""<div class="social-btn-custom">
            <img class="social-icon" src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg">
            <span class="social-text" style="color: #1877F2;">เข้าสู่ระบบด้วย Facebook</span>
        </div>""", unsafe_allow_html=True)
        if st.button("", key="f_login", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

        st.markdown("<hr style='margin: 25px 0; opacity: 0.3;'>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="Username")
        pwd = st.text_input("Password", type="password", placeholder="Password")
        
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True; st.rerun()

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1: st.button(t["reg_btn"], use_container_width=True)
        with col_sub2:
            if st.button(t["guest_btn"], use_container_width=True):
                st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 5. Main Controller ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state:
    st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# -------------------------------
# 🌐 Language
# -------------------------------
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา",
        "theme_label": "โหมดแสดงผล",
        "api_label": "OpenAI API Key",
        "free_mode": "โหมดใช้งานฟรี",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "ประเทศ",
        "city": "เมือง",
        "start_date": "วันที่ไป",
        "end_date": "วันที่กลับ",
        "activity_label": "กิจกรรม",
        "activities": ["ท่องเที่ยวถ่ายรูป", "ติดต่อธุรกิจ", "กิจกรรมหิมะ/สกี", "ผจญภัย/เดินป่า", "ช้อปปิ้ง"],
        "gender": "เพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload_section": "📸 รูปภาพ",
        "run_btn": "✨ เริ่มวิเคราะห์",
        "temp_label": "🌡️ อุณหภูมิ",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้",
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน"],
}

# -------------------------------
# 🎭 3D Model (Premium)
# -------------------------------
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width:100%;height:400px;
        background:radial-gradient(circle,#334155 0%,#0f172a 100%);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        position:relative;cursor:grab;border:2px solid #6366f1;">
            <div id="character" style="font-size:150px;transition:transform 0.1s linear;">🧥</div>
            <div style="position:absolute;bottom:15px;color:#94a3b8;font-size:12px;">
                [ ลากเพื่อหมุนดูชุด 360° ]
            </div>
        </div>
        <script>
            const el=document.getElementById('viewer-3d');
            const char=document.getElementById('character');
            let drag=false,rot=0,startX=0;
            el.onmousedown=e=>{drag=true;startX=e.pageX;};
            window.onmouseup=()=>drag=false;
            window.onmousemove=e=>{
                if(!drag)return;
                const d=e.pageX-startX;
                rot+=d*0.5;
                char.style.transform=`rotateY(${rot}deg)`;
                startX=e.pageX;
            };
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
# 🎨 Dashboard
# -------------------------------
def main_dashboard():
    t = LANG_DATA["Thai"]

    # Sidebar (ใช้จาก code ที่ให้มา)
    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai"], horizontal=True)
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        free_mode = st.toggle(t["free_mode"], value=not api_key)
        dark = st.toggle(t["theme_label"], value=False)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")

    col1, col2 = st.columns([1, 1.4])

    with col1:
        country = st.selectbox(t["dest"], CITY_DATA.keys())
        city = st.selectbox(t["city"], CITY_DATA[country])
        start = st.date_input(t["start_date"], datetime.now())
        end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
        activity = st.multiselect(t["activity_label"], t["activities"])
        img = st.file_uploader("อัปโหลดรูป", type=["jpg","png","jpeg"])
        run = st.button(t["run_btn"], type="primary")

    with col2:
        if run:
            result, is_premium = process_analysis(
                api_key, city, country, activity, free_mode, img, start, end
            )

            # Weather
            st.metric(t["temp_label"], "2°C")
            st.warning(f"❄️ อากาศหนาวใน {city}")
            st.divider()

            # 🔍 Analysis FIRST
            st.subheader(t["analysis_title"])
            st.markdown(f"<div class='analysis-box'>{result}</div>", unsafe_allow_html=True)

            # 🎭 3D ต่อจากผลวิเคราะห์
            st.divider()
            if is_premium:
                render_3d_model()
            else:
                st.image(
                    "https://images.unsplash.com/photo-1517495306684-21523df7d62c",
                    caption="Reference Outfit (Free Mode)"
                )

            # 🛍️ Shopping
            st.divider()
            st.subheader(t["shop_title"])
            for item in ["เสื้อโค้ทกันหนาว","ถุงมือกันหนาว","รองเท้าบูทกันหนาว"]:
                st.markdown(f"""
                <div class="shop-card">
                    🔹 {item}<br>
                    <a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank">
                        คลิกเพื่อค้นหาสินค้า
                    </a>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("👈 กรอกข้อมูลแล้วกดเริ่มวิเคราะห์")

# -------------------------------
# 🔑 Login Page (ใช้จาก code ที่ให้มา)
# -------------------------------
def login_page():
    t = LANG_DATA["Thai"]
    st.markdown(f"""
    <div style="text-align:center;padding:40px">
        <h1 style="font-size:3rem">Tripnify</h1>
        <p>{t['login_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1,1.5,1])
    with c:
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True
            st.rerun()
        if st.button(t["guest_btn"], use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()

# -------------------------------
# 🚀 Main
# -------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
