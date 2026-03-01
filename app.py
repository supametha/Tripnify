import streamlit as st
import base64
import requests
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# --- 🌐 0. ข้อมูลภาษาและเมือง ---
LANG_DATA = {
    "Thai": {
        "settings": "⚙️ ตั้งค่าระบบ",
        "lang_label": "เลือกภาษา (Language)",
        "theme_label": "โหมดแสดงผล (มืด/สว่าง)",
        "api_label": "OpenAI API Key",
        "weather_api_label": "OpenWeatherMap API Key",
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
        "weather_api_label": "OpenWeatherMap API Key",
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

# --- 🌦️ 1. Weather Logic ---
def get_weather_bg(main_desc):
    main_desc = main_desc.lower()
    bgs = {
        "rain": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?q=80&w=1000",
        "snow": "https://images.unsplash.com/photo-1478265409131-1f65c88f965c?q=80&w=1000",
        "clouds": "https://images.unsplash.com/photo-1534088568595-a066f710b721?q=80&w=1000",
        "clear": "https://images.unsplash.com/photo-1504386106331-3e4e71712b38?q=80&w=1000",
        "default": "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?q=80&w=1000"
    }
    if "rain" in main_desc or "drizzle" in main_desc: return bgs["rain"]
    elif "snow" in main_desc: return bgs["snow"]
    elif "cloud" in main_desc: return bgs["clouds"]
    elif "clear" in main_desc: return bgs["clear"]
    return bgs["default"]

def get_real_weather(city_name, api_key):
    if not api_key:
        return {"temp": 2, "feels_like": -1, "desc": "เมฆมาก (Demo)", "main": "Clouds", "wind": 5, "humidity": 80, "visibility": 10, "pressure": 1015, "clouds": 90}
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=th"
        res = requests.get(url, timeout=5).json()
        if res.get("cod") == 200:
            return {
                "temp": int(res["main"]["temp"]),
                "feels_like": int(res["main"]["feels_like"]),
                "desc": res["weather"][0]["description"],
                "main": res["weather"][0]["main"],
                "wind": res["wind"]["speed"],
                "humidity": res["main"]["humidity"],
                "visibility": res.get("visibility", 0) // 1000,
                "pressure": res["main"]["pressure"],
                "clouds": res["clouds"]["all"]
            }
    except: pass
    return {"temp": 2, "feels_like": -1, "desc": "เชื่อมต่อ API ไม่ได้", "main": "Clouds", "wind": 5, "humidity": 80, "visibility": 10, "pressure": 1015, "clouds": 90}

# --- 🎭 2. 3D Model Logic ---
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    # ใส่ URL รูปตัวละครหลักของคุณตรงนี้
    character_img = "https://cdn-icons-png.flaticon.com/512/3534/3534312.png" 

    components.html(f"""
        <div id="viewer-3d" style="width:100%; height:450px; background: radial-gradient(circle, #f8fafc 0%, #cbd5e1 100%);
            border-radius:25px; display:flex; align-items:center; justify-content:center; position:relative; cursor:grab; border:2px solid #6366f1; overflow:hidden;">
            <img id="character" src="{character_img}" style="height:85%; transition:transform 0.1s linear; user-select:none; pointer-events:none;">
            <div style="position:absolute; bottom:15px; color:#475569; font-size:12px; font-family:sans-serif;">[ ลากเพื่อหมุนดูชุด 360° ]</div>
        </div>
        <script>
            const el = document.getElementById('viewer-3d');
            const char = document.getElementById('character');
            let drag = false, rot = 0, startX = 0;
            el.onmousedown = e => {{ drag = true; startX = e.pageX; el.style.cursor = 'grabbing'; }};
            window.onmouseup = () => {{ drag = false; el.style.cursor = 'grab'; }};
            window.onmousemove = e => {{
                if(!drag) return;
                const d = e.pageX - startX;
                rot += d * 0.8;
                char.style.transform = `rotateY(${{rot}}deg)`;
                startX = e.pageX;
            }};
        </script>
    """, height=470)

# --- ⚙️ 3. Analysis Logic ---
def process_analysis(api_key, city, country, activity, free_mode, image, start, end):
    days = (end - start).days + 1
    if api_key and not free_mode and image:
        try:
            client = OpenAI(api_key=api_key)
            b64 = base64.b64encode(image.getvalue()).decode()
            prompt = f"วิเคราะห์การแต่งกายสำหรับ {city} {country} อากาศปัจจุบัน กิจกรรม: {activity} ระยะเวลา {days} วัน ตอบเป็นภาษาไทย"
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                timeout=15.0
            )
            return res.choices[0].message.content, True
        except: return "แนะนำแต่งกายแบบ Layering (เสื้อฮีทเทค + เสื้อไหมพรม + เสื้อโค้ท)", False
    return "โหมดใช้งานฟรี: แนะนำแต่งกายแบบ Layering ตามอุณหภูมิที่แสดงข้างต้น", False

# --- 🎨 4. Dashboard Page ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        st.divider()
        api_key = st.text_input(t["api_label"], type="password")
        weather_api_key = st.text_input(t["weather_api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        
        dark_mode = st.toggle(t["theme_label"], value=False)
        if dark_mode:
            st.markdown("<style>.stApp { background-color: #0f172a; color: #f8fafc; } .analysis-box { background: #1e293b !important; border: 1px solid #334155; padding:20px; border-radius:12px; }</style>", unsafe_allow_html=True)
        else:
            st.markdown("<style>.analysis-box { background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; color: #1e293b; }</style>", unsafe_allow_html=True)

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
            d1, d2 = st.columns(2)
            start = d1.date_input(t["start_date"], datetime.now())
            end = d2.date_input(t["end_date"], datetime.now() + timedelta(days=3))
            activity = st.multiselect(t["activity_label"], t["activities"], default=[t["activities"][0]])
            st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            w = get_real_weather(city, weather_api_key)
            bg_url = get_weather_bg(w["main"])
            result, is_premium = process_analysis(api_key, city, country, activity, use_free_mode, img_file, start, end)

            # --- Animated Glassmorphism Weather Card ---
            st.markdown(f"""
                <style>
                @keyframes panBackground {{ 0% {{background-position:0% 50%}} 50% {{background-position:100% 50%}} 100% {{background-position:0% 50%}} }}
                .weather-card-new {{
                    background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.5)), url('{bg_url}');
                    background-size: 200% 200%; animation: panBackground 20s ease infinite;
                    border-radius: 25px; padding: 25px; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 20px;
                }}
                .glass-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }}
                .glass-item {{
                    background: rgba(255, 255, 255, 0.18); backdrop-filter: blur(10px);
                    padding: 10px; border-radius: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.2); font-size: 12px;
                }}
                </style>
                <div class="weather-card-new">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h1 style="font-size: 60px; margin: 0;">{w['temp']}°C</h1>
                            <h2 style="margin: 0;">{city}</h2>
                            <p style="opacity: 0.8;">Feels like {w['feels_like']}°C • {w['desc']}</p>
                        </div>
                        <div style="text-align: right; font-size: 12px; opacity: 0.7;">{datetime.now().strftime('%H:%M %p')}</div>
                    </div>
                    <div class="glass-grid">
                        <div class="glass-item">💨 Wind<br><strong>{w['wind']}m/s</strong></div>
                        <div class="glass-item">💧 Humid<br><strong>{w['humidity']}%</strong></div>
                        <div class="glass-item">👁️ Vis<br><strong>{w['visibility']}km</strong></div>
                        <div class="glass-item">☁️ Cloud<br><strong>{w['clouds']}%</strong></div>
                        <div class="glass-item">🌡️ Pres<br><strong>{w['pressure']}</strong></div>
                        <div class="glass-item">❄️ Snow<br><strong>{w['main'] == 'Snow'}</strong></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{result}</div>', unsafe_allow_html=True)
            
            if is_premium: render_3d_model()
            
            st.divider()
            st.subheader(t["shop_title"])
            for item in t["essentials"]:
                st.markdown(f'<div style="background:white; padding:12px; border-radius:10px; border-left:5px solid #4f46e5; margin-bottom:10px; color:black;"><strong>🔹 {item}</strong><br><a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank" style="color:#4f46e5; text-decoration:none;">🛒 คลิกเพื่อช้อปสินค้า</a></div>', unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์")

# --- 🔑 5. Login Page ---
def login_page():
    t = LANG_DATA[st.session_state.get('lang_choice', 'Thai')]
    st.markdown("<div style='text-align:center; padding:40px;'><img src='
