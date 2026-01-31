import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import json

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
        "3d_title": "🎭 3D Outfit Character Preview",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำตามคำแนะนำ",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้"
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
        "3d_title": "🎭 3D Outfit Character Preview",
        "shop_title": "🛍️ Recommended Shopping",
        "login_sub": "Smart Outfit Analysis for Your Trip",
        "login_btn": "🔑 Login",
        "reg_btn": "📝 Register",
        "guest_btn": "👤 Guest"
    }
}

CITY_DATA = {
    "ญี่ปุ่น": ["โตเกียว", "โอซาก้า", "ฮอกไกโด"],
    "เกาหลีใต้": ["โซล", "ปูซาน", "เชจู"],
    "เวียดนาม": ["ฮานอย", "โฮจิมินห์"],
    "ไต้หวัน": ["ไทเป", "เกาสง"],
    "จีน": ["ปักกิ่ง", "เซี่ยงไฮ้"]
}

# --- 🎮 1. ฟังก์ชันแสดงผล 3D Model ---
def render_3d_model(title):
    st.markdown(f"### {title}")
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

# --- ⚙️ 2. ระบบวิเคราะห์ Logic ---
def process_analysis(api_key, country, city, activity, use_free_mode, uploaded_file, lang, start_date, end_date):
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            # สั่งให้ AI ตอบกลับเป็น JSON เพื่อนำไปใช้ในส่วน Shopping
            prompt = f"Analyze outfit for {city}, {country}. Weather approx 2°C. Activity: {activity}. Response in {lang}. Provide a text analysis and a list of 3 essential items with reasons in JSON format: {{'analysis': '...', 'items': [{{'name': '...', 'reason': '...'}}]}}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            return data, True
        except:
            pass

    # Free Mode / Fallback Data
    fallback = {
        "analysis": "แนะนำการแต่งกายแบบ 3 ชั้น (Layering) เนื่องจากอุณหภูมิประมาณ 2°C ควรเน้นการเก็บความร้อน" if lang == "Thai" else "Recommended 3-layer outfit for 2°C weather.",
        "items": [
            {"name": "Ultra Light Down Jacket", "reason": "น้ำหนักเบา กันลม และเก็บอุณหภูมิได้ดีเยี่ยม"},
            {"name": "Heattech Ultra Warm", "reason": "เลเยอร์ด้านในที่ช่วยรักษาความร้อนของร่างกาย"},
            {"name": "ถุงมือกันหนาว", "reason": "ป้องกันปลายนิ้วชาจากอากาศเย็นจัด"}
        ]
    }
    return fallback, False

# --- 🎨 3. หน้า Dashboard ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        dark_mode = st.toggle(t["theme_label"], value=False)
        
        # Style injection
        if dark_mode:
            st.markdown("""<style>.stApp { background-color: #0f172a; color: #f8fafc; } .analysis-box { background: #1e293b; padding:20px; border-radius:12px; border: 1px solid #334155; } .shop-card { background:#334155; padding: 15px; border-radius: 10px; border-left: 5px solid #6366f1; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)
        else:
            st.markdown("""<style>.analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; } .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
            city = st.selectbox(t["city"], CITY_DATA[country])
            start = st.date_input(t["start_date"], datetime.now())
            end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            st.session_state['gender_val'] = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, img_file, current_lang, start, end)
            
            # 1. ผลวิเคราะห์การแต่งกาย (แสดงก่อน)
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{data["analysis"]}</div>', unsafe_allow_html=True)
            
            # 2. ตัวละคร 3D
            st.divider()
            render_3d_model(t["3d_title"])
            
            # 3. แหล่งช้อปปิ้งแนะนำ (ดึงจาก AI Keyword)
            st.divider()
            st.subheader(t["shop_title"])
            
            for item in data["items"]:
                with st.expander(f"🔹 {item['name']}"):
                    st.write(f"**เหตุผลที่เหมาะสม:** {item['reason']}")
                    st.write("**เลือกซื้อได้ที่:**")
                    
                    kw = quote_plus(item['name'])
                    s_col1, s_col2, s_col3 = st.columns(3)
                    
                    # Shopee
                    with s_col1:
                        st.markdown(f'[![Shopee](https://img.icons8.com/color/48/shopee.png)](https://shopee.co.th/search?keyword={kw})  \n[Shopee](https://shopee.co.th/search?keyword={kw})', unsafe_allow_html=True)
                    # Uniqlo
                    with s_col2:
                        st.markdown(f'[![Uniqlo](https://img.icons8.com/color/48/u.png)](https://www.uniqlo.com/th/th/search/?q={kw})  \n[Uniqlo](https://www.uniqlo.com/th/th/search/?q={kw})', unsafe_allow_html=True)
                    # Lazada
                    with s_col3:
                        st.markdown(f'[![Lazada](https://img.icons8.com/color/48/lazada.png)](https://www.lazada.co.th/catalog/?q={kw})  \n[Lazada](https://www.lazada.co.th/catalog/?q={kw})', unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์")

# --- 🔑 4. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]
    st.markdown("""<style>.header-container { text-align: center; padding: 30px 0; }</style>""", unsafe_allow_html=True)
    st.markdown(f'<div class="header-container"><img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="130"><h1>Tripnify</h1><p>{t["login_sub"]}</p></div>', unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        if st.button(t["login_btn"], use_container_width=True, type="primary"): st.session_state['logged_in'] = True; st.rerun()
        if st.button(t["guest_btn"], use_container_width=True): st.session_state['logged_in'] = True; st.rerun()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'lang_choice' not in st.session_state: st.session_state['lang_choice'] = 'Thai'

if st.session_state['logged_in']: main_dashboard()
else: login_page()
