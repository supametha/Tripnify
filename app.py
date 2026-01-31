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



# --- 🎮 1. ฟังก์ชันแสดงผล 3D Model (Premium) ---

def render_3d_model():

    st.markdown("### 🎭 3D Outfit Character Preview")

    components.html("""

        <div id="viewer-3d" style="width: 100%; height: 400px; background: radial-gradient(circle, #334155 0%, #0f172a 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; position: relative; cursor: grab; border: 2px solid #6366f1;">

            <div id="character" style="font-size: 150px; transition: transform 0.1s linear; user-select: none;">🧥</div>

            <div style="position: absolute; bottom: 20px; color: #94a3b8; font-family: sans-serif; font-size: 12px; pointer-events: none;">

                [ ลากเพื่อหมุนดูชุดรอบตัว 360° ]

            </div>

        </div>

        <script>

            const el = document.getElementById('viewer-3d');

            const char = document.getElementById('character');

            let isDragging = false; let rotation = 0; let startX;

            el.onmousedown = (e) => { isDragging = true; startX = e.pageX; el.style.cursor = 'grabbing'; };

            window.onmouseup = () => { isDragging = false; el.style.cursor = 'grab'; };

            window.onmousemove = (e) => {

                if (!isDragging) return;

                const delta = e.pageX - startX;

                rotation += delta * 0.5;

                char.style.transform = `rotateY(${rotation}deg)`;

                startX = e.pageX;

            };

        </script>

    """, height=420)



# --- ⚙️ 2. ระบบวิเคราะห์ Logic (Premium vs Free) ---

# --- แก้ไขบรรทัดที่ 100 เป็นต้นไป ในฟังก์ชัน process_analysis ---

# แก้ไขบรรทัดที่ 90 เป็นต้นไป

def process_analysis(api_key, country, city, activity, use_free_mode, uploaded_file, lang, start_date, end_date):

    if api_key and not use_free_mode:

        try:

            client = OpenAI(api_key=api_key)

            # ปรับ Prompt สั่ง AI ให้ตอบแยกส่วน

            prompt = f"Analyze outfit for {city}, {country}. Activity: {activity}. Respond in {lang}. Then, list 3 specific essential items for this trip with a reason for each."

            

            # (ส่วนส่ง API ปกติของคุณ...)

            # จุดสำคัญ: คืนค่าเป็น Dictionary เพื่อเอาไปวนลูปสร้างปุ่มช้อปปิ้ง

            # ตัวอย่างการคืนค่า: return {"analysis": "ข้อความวิเคราะห์", "items": [{"name": "ชื่อสินค้า", "reason": "เหตุผล"}]}, True

            items = [

                {"name": "Ultra Warm Heattech", "reason": "ช่วยรักษาอุณหภูมิร่างกายชั้นในสุดได้ดีเยี่ยม"},

                {"name": "Seamless Down Parka", "reason": "กันลมและละอองน้ำได้ดี เหมาะกับกิจกรรมกลางแจ้ง"},

                {"name": "Heattech Gloves", "reason": "ป้องกันปลายนิ้วชาขณะถ่ายรูปหรือใช้งานมือถือ"}

            ]

            return {"text": analysis_text, "items": items}, True

        except Exception as e:

            return {"text": f"Error: {e}", "items": []}, False

    else:

        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน"

        items_free = [{"name": "เสื้อโค้ทกันหนาว", "reason": "พื้นฐานสำคัญสำหรับกันความหนาว"}]

        return {"text": v_free, "items": items_free}, False



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



    # แก้ไขบรรทัดที่ 200 เป็นต้นไป (ในส่วน if run_btn:)

            result_data, is_premium = process_analysis(...) # ดึงข้อมูลจากจุดที่ 1



            # 1. ผลวิเคราะห์การแต่งกาย (ย้ายมาไว้บนสุด)

            st.subheader(t["analysis_title"])

            st.info(result_data["analysis"]) # แสดงบทวิเคราะห์



            st.divider()



            # 2. 3D Model (อยู่ลำดับที่สอง)

            if is_premium:

                render_3d_model()

            else:

                st.image("...", caption="Reference Outfit")

            

            st.divider()



            # [ลำดับที่ 2] 3D Model หรือ Reference Image

            if is_premium:

                render_3d_model()

            else:

                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Image (Free Mode)")



            st.divider()



            # [ลำดับที่ 3] แหล่งช้อปปิ้งแนะนำ (ปรับสีปุ่มและ Logo ตามแบรนด์)

            st.subheader(t["shop_title"])

            st.markdown("""

                <style>

                .btn-shopee { background-color: #EE4D2D !important; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-right: 5px; display: inline-block; }

                .btn-uniqlo { background-color: #FF0000 !important; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-right: 5px; display: inline-block; }

                .btn-lazada { background-color: #101566 !important; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; }

                .item-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; }

                </style>

            """, unsafe_allow_html=True)



            for item in data["items"]:

                kw = quote_plus(item['name'])

                st.markdown(f"""

                <div class="item-card">

                    <strong>🔹 {item['name']}</strong><br>

                    <small style="color: gray;">เหตุผล: {item['reason']}</small><br><br>

                    <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🧡 Shopee</a>

                    <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">❤️ Uniqlo</a>

                    <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">💙 Lazada</a>

                </div>

                """, unsafe_allow_html=True)

        else:

            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์และตัวละคร 3D")



# --- 🔑 4. หน้า Login ---

def login_page():

    current_lang = st.session_state.get('lang_choice', 'Thai')

    t = LANG_DATA[current_lang]



    # แก้ไขบรรทัดที่ 230 เป็นต้นไป

            st.subheader(t["shop_title"])

            

            # CSS สำหรับตกแต่งปุ่มและโลโก้

            st.markdown("""<style>

                .shop-box { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; margin-bottom: 15px; background: #f8fafc; }

                .btn-shopee { background: #EE4D2D; color: white !important; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; }

                .btn-uniqlo { background: #FF0000; color: white !important; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; }

                .btn-lazada { background: #00008B; color: white !important; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; }

            </style>""", unsafe_allow_html=True)



            for item in result_data["items"]: # ดึงสินค้าที่ AI แนะนำทีละตัว

                kw = quote_plus(item["name"])

                st.markdown(f"""

                <div class="shop-box">

                    <strong>🧥 {item['name']}</strong>

                    <p style='font-size: 0.9rem; color: #64748b;'>{item['reason']}</p>

                    <div style='display: flex; gap: 10px;'>

                        <a href="https://shopee.co.th/search?keyword={kw}" class="btn-shopee">🟠 Shopee</a>

                        <a href="https://www.uniqlo.com/th/th/search/?q={kw}" class="btn-uniqlo">🔴 Uniqlo</a>

                        <a href="https://www.lazada.co.th/catalog/?q={kw}" class="btn-lazada">🔵 Lazada</a>

                    </div>

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
