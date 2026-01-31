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
    days = (end_date - start_date).days + 1
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            # ปรับ Prompt ให้ AI ส่งข้อมูลสินค้าและเหตุผลแยกมาให้ชัดเจน
            prompt = (f"Analyze outfit for {city}, {country}. Activity: {activity}. Respond in {lang}. "
                      f"At the end, list 3-4 specific essential items. Format each item as 'ITEM: [Name] | REASON: [Why it is suitable]'.")
            
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                )
                full_text = response.choices[0].message.content
                analysis_part = full_text.split("ITEM:")[0].strip()
                # ดึงรายการสินค้าและเหตุผลมาเก็บเป็น List of Dict
                items_raw = [i.strip() for i in full_text.split("ITEM:") if "|" in i]
                items_data = []
                for entry in items_raw:
                    parts = entry.split("|")
                    items_data.append({"name": parts[0].replace("ITEM:", "").strip(), "reason": parts[1].replace("REASON:", "").strip()})
                
                return {"analysis": analysis_part, "items": items_data}, True
            return "กรุณาอัปโหลดรูปภาพ", False
        except Exception as e:
            return f"Error: {e}", False
    else:
        # โหมดฟรี: ใช้ข้อมูลจำลองที่มีเหตุผลประกอบ
        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน" if lang == "Thai" else "Layering recommended: Heattech, Sweater, and Down Jacket."
        items_free = [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "ช่วยกันลมและรักษาความร้อนในร่างกายได้ดีที่สุดในอุณหภูมิเลขตัวเดียว"},
            {"name": "ลองจอห์น / Heattech", "reason": "เป็นชั้นในที่ช่วยระบายอากาศแต่เก็บกักความร้อนแนบผิวหนัง"},
            {"name": "แผ่นแปะความร้อน", "reason": "ช่วยเพิ่มความอบอุ่นเฉพาะจุด เช่น กระเป๋าเสื้อหรือแผ่นหลัง เมื่อต้องอยู่กลางแจ้งนานๆ"}
        ]
        return {"analysis": v_free, "items": items_free}, False
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
            result_data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, active_img, current_lang, start, end)
            
            # --- [ปรับที่ 1] แสดงบทวิเคราะห์ก่อน ---
            st.subheader(t["analysis_title"])
            analysis_text = result_data["analysis"] if isinstance(result_data, dict) else result_data
            st.markdown(f'<div class="analysis-box">{analysis_text}</div>', unsafe_allow_html=True)
            st.divider()

            # --- [ปรับที่ 2] แสดง 3D (Premium) หรือรูปภาพ (Free) ---
            if is_premium:
                render_3d_model()
            else:
                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Outfit (Free Mode)")
            
            # --- [ปรับที่ 3] แหล่งช้อปปิ้งแนะนำ พร้อมคำอธิบายและโลโก้ ---
            st.divider()
            st.subheader(t["shop_title"])
            
            items_to_show = result_data["items"] if isinstance(result_data, dict) else []
            
            for item in items_to_show:
                with st.expander(f"🛒 แนะนำสินค้า: {item['name']}"):
                    st.write(f"**เหตุผลความเหมาะสม:** {item['reason']}")
                    st.write("เลือกซื้อได้ที่:")
                    
                    # สร้างปุ่มพร้อม Icon สำหรับ Shopee, Uniqlo, Lazada
                    shop_cols = st.columns(3)
                    
                    # Shopee
                    with shop_cols[0]:
                        st.markdown(f'[![Shopee](https://img.icons8.com/color/48/shopee.png)](https://shopee.co.th/search?keyword={quote_plus(item["name"])})')
                        st.caption("Shopee")
                    
                    # Uniqlo
                    with shop_cols[1]:
                        st.markdown(f'[![Uniqlo](https://img.icons8.com/color/48/uniqlo.png)](https://www.uniqlo.com/th/en/search/?q={quote_plus(item["name"])})')
                        st.caption("Uniqlo")
                        
                    # Lazada
                    with shop_cols[2]:
                        st.markdown(f'[![Lazada](https://img.icons8.com/color/48/lazada.png)](https://www.lazada.co.th/catalog/?q={quote_plus(item["name"])})')
                        st.caption("Lazada")
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์")

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
