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
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ (อ้างอิงจาก AI)",
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
def process_analysis(api_key, country, city, activity, use_free_mode, lang):
    # จำลองการดึงข้อมูลจาก AI (ในระบบจริงจะใช้ openai.ChatCompletion)
    if api_key and not use_free_mode:
        analysis_text = f"สำหรับการเดินทางไป {city}, {country} เพื่อทำกิจกรรม {', '.join(activity)} แนะนำให้สวมใส่เสื้อผ้าที่เน้นการเก็บความร้อนและกันลม"
        items = [
            {"name": "Ultra Warm Heattech", "reason": "รักษาอุณหภูมิร่างกายชั้นในสุดได้ดีเยี่ยมในสภาพอากาศเลขตัวเดียว"},
            {"name": "Seamless Down Parka", "reason": "กันลมและละอองน้ำได้ดี เหมาะกับกิจกรรม {activity[0] if activity else ''}"},
            {"name": "Heattech Gloves", "reason": "ป้องกันปลายนิ้วชาขณะถ่ายรูปหรือใช้งานมือถือ"}
        ]
        return {"analysis": analysis_text, "items": items}, True
    else:
        # โหมดทดลองใช้
        analysis_text = "คำแนะนำเบื้องต้น: ควรแต่งกายแบบเลเยอร์ 3 ชั้น (Base, Mid, Outer) เพื่อปรับเปลี่ยนตามอุณหภูมิได้ง่าย"
        items = [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "เป็นไอเทมพื้นฐานที่ช่วยกันหนาวและเพิ่มความดูดีในการถ่ายรูป"},
            {"name": "แผ่นแปะความร้อน (Kairo)", "reason": "พกพาสะดวก ช่วยให้ความอบอุ่นเฉพาะจุดได้ทันที"}
        ]
        return {"analysis": analysis_text, "items": items}, False

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
                </style>""", unsafe_allow_html=True)
        else:
            st.markdown("""<style>
                .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
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
            st.radio(t["gender"], [t["male"], t["female"]], key="gender_val", horizontal=True)
            
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("อัปโหลดรูปภาพเสื้อผ้าที่มี", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            # ดึงข้อมูลการวิเคราะห์
            result_data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, current_lang)

            # [ลำดับที่ 1] ผลวิเคราะห์การแต่งกาย
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{result_data["analysis"]}</div>', unsafe_allow_html=True)
            
            st.divider()

            # [ลำดับที่ 2] 3D Model
            if is_premium:
                render_3d_model()
            else:
                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Style (Free Mode)")

            st.divider()

            # [ลำดับที่ 3] แหล่งช้อปปิ้งแนะนำ (ดึงข้อมูลจาก AI)
            st.subheader(t["shop_title"])
            st.markdown("""
                <style>
                .shop-card { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; margin-bottom: 15px; background: white; color: #1e293b; }
                .btn-shopee { background: #EE4D2D; color: white !important; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; margin-right: 5px; display: inline-block; }
                .btn-uniqlo { background: #FF0000; color: white !important; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; margin-right: 5px; display: inline-block; }
                .btn-lazada { background: #00008B; color: white !important; padding: 5px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; display: inline-block; }
                </style>
            """, unsafe_allow_html=True)

            for item in result_data["items"]:
                kw = quote_plus(item["name"])
                st.markdown(f"""
                <div class="shop-card">
                    <strong>🧥 {item['name']}</strong>
                    <p style='font-size: 0.85rem; color: #64748b; margin: 5px 0;'><strong>เหตุผลที่แนะนำ:</strong> {item['reason']}</p>
                    <div style='margin-top: 10px;'>
                        <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🟠 Shopee</a>
                        <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">🔴 Uniqlo</a>
                        <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">🔵 Lazada</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์")

# --- 🔑 4. หน้า Login ---
def login_page():
    t = LANG_DATA[st.session_state.get('lang_choice', 'Thai')]
    st.markdown("<h1 style='text-align: center;'>Tripnify</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t['login_sub']}</p>", unsafe_allow_html=True)
    
    _, c2, _ = st.columns([1, 1.5, 1])
    with c2:
        st.text_input("Username", placeholder="กรอกชื่อผู้ใช้")
        st.text_input("Password", type="password", placeholder="กรอกรหัสผ่าน")
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
