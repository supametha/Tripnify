import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ระบบจัดการภาษาและข้อมูลพื้นฐาน ---
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา",
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
        "run_btn": "✨ เริ่มวิเคราะห์ชุดแต่งกาย",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำตามผลวิเคราะห์",
        "login_sub": "ระบบวิเคราะห์การแต่งกายอัจฉริยะ",
        "login_btn": "🔑 เข้าสู่ระบบ"
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

# --- ⚙️ 2. ระบบวิเคราะห์ AI (ดึงข้อมูลสินค้าแยกส่วน) ---
def process_analysis(api_key, country, city, activity, use_free_mode, lang):
    if api_key and not use_free_mode:
        try:
            # ในระบบจริงจะเรียก OpenAI API ตรงนี้
            # ตัวอย่างการส่งโครงสร้างข้อมูลกลับมาเพื่อให้ระบบประมวลผลต่อได้
            analysis_text = f"สำหรับการเดินทางไป {city} เพื่อ {', '.join(activity)} แนะนำให้เน้นเสื้อผ้าที่กันลมและเก็บความร้อนได้ดี"
            items = [
                {"name": "Heattech Ultra Warm", "reason": "เป็นเลเยอร์แรกที่สำคัญที่สุดในการกักเก็บความร้อนในร่างกาย"},
                {"name": "เสื้อขนเป็ดกันลม", "reason": "เหมาะกับอุณหภูมิติดลบและป้องกันลมหนาวในตัวเมือง"},
                {"name": "กางเกงบุขนกันหนาว", "reason": "ช่วยให้ช่วงล่างอบอุ่นขณะเดินท่องเที่ยวเป็นเวลานาน"}
            ]
            return {"text": analysis_text, "items": items}, True
        except Exception as e:
            return {"text": f"Error: {e}", "items": []}, False
    else:
        # ข้อมูลสำหรับโหมดฟรี
        v_free = "แนะนำชุดกันหนาว 3 ชั้นพื้นฐาน: Heattech, ไหมพรม, และโค้ทกันหนาว"
        items_free = [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "เสื้อตัวนอกที่จำเป็นสำหรับกันอากาศเย็น"},
            {"name": "แผ่นแปะความร้อน", "reason": "ตัวช่วยเสริมความอบอุ่นที่พกพาสะดวก"}
        ]
        return {"text": v_free, "items": items_free}, False

# --- 🎨 3. หน้า Dashboard ---
def main_dashboard():
    t = LANG_DATA["Thai"]
    
    with st.sidebar:
        st.subheader(t["settings"])
        api_key = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        if st.button(t["logout"]):
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
            gender = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            # ประมวลผล
            data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, "Thai")
            
            # [1] ส่วนผลวิเคราะห์การแต่งกาย (ขึ้นก่อนตามสั่ง)
            st.subheader(t["analysis_title"])
            st.info(data["text"])
            
            st.divider()

            # [2] ส่วน 3D Model (Premium) หรือ ภาพนิ่ง (Free)
            if is_premium:
                render_3d_model()
            else:
                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Outfit (Free Mode)")

            st.divider()

            # [3] ส่วนแหล่งช้อปปิ้งแนะนำ (ดึงข้อมูลจาก AI มาสร้าง)
            st.subheader(t["shop_title"])
            
            # CSS สำหรับปุ่มแบรนด์
            st.markdown("""
                <style>
                .shop-card { border: 1px solid #e6e9ef; padding: 20px; border-radius: 15px; margin-bottom: 15px; background-color: rgba(255,255,255,0.05); }
                .btn-shopee { background-color: #EE4D2D !important; color: white !important; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-uniqlo { background-color: #FF0000 !important; color: white !important; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-lazada { background-color: #101566 !important; color: white !important; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .reason-text { font-size: 0.9rem; color: #888; margin-top: 5px; margin-bottom: 15px; }
                </style>
            """, unsafe_allow_html=True)

            for item in data["items"]:
                kw = quote_plus(item['name'])
                st.markdown(f"""
                    <div class="shop-card">
                        <h4 style="margin:0;">🧥 {item['name']}</h4>
                        <div class="reason-text"><strong>💡 ทำไมถึงแนะนำ:</strong> {item['reason']}</div>
                        <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🛍️ Shopee</a>
                        <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">🔴 Uniqlo</a>
                        <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">💙 Lazada</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลการเดินทางและกดปุ่มเพื่อเริ่มวิเคราะห์")

# --- 🔑 4. หน้า Login ---
def login_page():
    t = LANG_DATA["Thai"]
    st.markdown("<h1 style='text-align: center;'>Tripnify</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>{t['login_sub']}</p>", unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.text_input("Username")
        st.text_input("Password", type="password")
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True
            st.rerun()

# --- 🚀 5. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
