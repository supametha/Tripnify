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
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ (แนะนำสำหรับคุณ)",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะเพื่อการเดินทาง",
        "login_btn": "🔑 เข้าสู่ระบบ",
        "reg_btn": "📝 ลงทะเบียน",
        "guest_btn": "👤 ทดลองใช้",
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
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width: 100%; height: 400px; background: radial-gradient(circle, #334155 0%, #0f172a 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; position: relative; cursor: grab; border: 2px solid #6366f1;">
            <div id="character" style="font-size: 150px; transition: transform 0.1s linear; user-select: none;">🧥</div>
            <div style="position: absolute; bottom: 20px; color: #94a3b8; font-family: sans-serif; font-size: 12px; pointer-events: none;">[ ลากเพื่อหมุนดูชุดรอบตัว 360° ]</div>
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
            prompt = (f"Analyze outfit for {city}, {country}. Activity: {activity}. Respond in {lang}. "
                      f"Finally, list 3 essential items to buy, each starting with 'ITEM: '")
            
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                )
                full_text = response.choices[0].message.content
                analysis_part = full_text.split("ITEM:")[0].strip()
                items_part = [i.strip() for i in full_text.split("ITEM:") if i.strip()][1:]
                
                if not items_part:
                    items_part = ["เสื้อโค้ทกันหนาว", "ถุงมือ", "ลองจอห์น"]
                
                return {"analysis": analysis_part, "items": items_part}, True
            return {"analysis": "กรุณาอัปโหลดรูปภาพ", "items": []}, False
        except Exception as e:
            return {"analysis": f"Error: {e}", "items": []}, False
    else:
        v_free = "แนะนำการแต่งกาย: เน้นการใส่เสื้อผ้า 3 ชั้น (Layering) เพื่อปรับตามอุณหภูมิได้ง่าย"
        items_free = ["เสื้อกันหนาว Uniqlo", "กางเกงบุขน", "แผ่นแปะความร้อน"]
        return {"analysis": v_free, "items": items_free}, False

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
            st.markdown("<style>.stApp { background-color: #0f172a; color: #f8fafc; } .analysis-box { background: #1e293b !important; padding:20px; border-radius:12px; }</style>", unsafe_allow_html=True)
        else:
            st.markdown("<style>.analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; color: #657b83; }</style>", unsafe_allow_html=True)

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
            start = st.date_input(t["start_date"], datetime.now())
            end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            st.session_state['gender_val'] = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("คลังภาพ", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            result_data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, img_file, current_lang, start, end)
            
            # 1. แสดงผลวิเคราะห์ก่อน
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{result_data["analysis"]}</div>', unsafe_allow_html=True)
            st.divider()

            # 2. แสดง 3D Model
            if is_premium:
                render_3d_model()
            else:
                st.info("โหมดฟรี: แสดงภาพตัวอย่างชุดทั่วไป")
                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?w=500")

            # 3. แหล่งช้อปปิ้งแนะนำ (ดึงจาก AI/ระบบฟรี)
            st.divider()
            st.subheader(t["shop_title"])
            for item in result_data["items"]:
                with st.expander(f"🔹 {item}"):
                    st.write(f"ไอเทมนี้คัดเลือกมาให้เหมาะสมกับกิจกรรม {', '.join(activity)} ที่ {city}")
                    st.markdown(f"[🛒 คลิกเพื่อค้นหาบน Shopee](https://shopee.co.th/search?keyword={quote_plus(item)})")
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์")

# --- 🔑 4. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]
    st.markdown("<h1 style='text-align: center;'>Tripnify</h1>", unsafe_allow_html=True)
    
    _, c2, _ = st.columns([1, 1.6, 1])
    with c2:
        st.text_input("Username")
        st.text_input("Password", type="password")
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True
            st.rerun()
        if st.button(t["guest_btn"], use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()

# --- 🚀 5. Main Controller ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
