import streamlit as st
import base64
import requests
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
        "reg_btn": "Register",
        "guest_btn": "Guest",
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

# --- 🌦️ 1. ฟังก์ชันดึงข้อมูลพยากรณ์อากาศจริง ---
def get_weather_data(city_name):
    # สำคัญ: ใส่ OpenWeatherMap API Key ของคุณที่นี่
    api_key = "YOUR_OPENWEATHER_API_KEY" 
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    try:
        complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric&lang=th"
        response = requests.get(complete_url, timeout=5)
        data = response.json()
        
        if data["cod"] != "404":
            main = data["main"]
            return {
                "temp": round(main["temp"]),
                "feels_like": round(main["feels_like"]),
                "humidity": main["humidity"],
                "pressure": main["pressure"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 10000) // 1000,
                "desc": data["weather"][0]["description"].capitalize(),
                "main_desc": data["weather"][0]["main"],
                "clouds": data["clouds"]["all"]
            }
    except:
        pass
    
    return {
        "temp": 2, "feels_like": -1, "humidity": 80, "pressure": 1015, 
        "wind_speed": 5, "visibility": 10, "desc": "เมฆมาก (Default)", 
        "main_desc": "Clouds", "clouds": 90
    }

# --- 🖼️ 2. ฟังก์ชันเลือกรูปพื้นหลังตามสภาพอากาศ ---
def get_weather_bg(main_desc):
    main_desc = main_desc.lower()
    bgs = {
        "rain": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?q=80&w=1000",
        "snow": "https://images.unsplash.com/photo-1478265409131-1f65c88f965c?q=80&w=1000",
        "clouds": "https://images.unsplash.com/photo-1534088568595-a066f710b721?q=80&w=1000",
        "clear": "https://images.unsplash.com/photo-1504386106331-3e4e71712b38?q=80&w=1000",
        "default": "https://images.unsplash.com/photo-1476820865390-c52aeebb9891?q=80&w=1000"
    }
    
    if "rain" in main_desc or "drizzle" in main_desc or "thunderstorm" in main_desc: return bgs["rain"]
    elif "snow" in main_desc: return bgs["snow"]
    elif "cloud" in main_desc: return bgs["clouds"]
    elif "clear" in main_desc: return bgs["clear"]
    return bgs["default"]

# --- 🎭 3. 3D Model Character ---
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width:100%;height:400px;
        background:radial-gradient(circle,#334155 0%,#0f172a 100%);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        position:relative;cursor:grab;border:2px solid #6366f1;">
            <div id="character" style="font-size:150px;transition:transform 0.1s linear; user-select:none;">🧥</div>
            <div style="position:absolute;bottom:15px;color:#94a3b8;font-size:12px; pointer-events:none;">
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

# --- ⚙️ 4. AI Analysis Logic ---
def process_analysis(api_key, city, country, activity, free_mode, image, start, end):
    days = (end - start).days + 1
    fallback_msg = "❄️ แนะนำแต่งกายแบบ Layering: เน้นใส่ Long-john, เสื้อไหมพรม และเสื้อโค้ทกันลมกันน้ำ"

    if api_key and not free_mode and image:
        try:
            client = OpenAI(api_key=api_key)
            b64 = base64.b64encode(image.getvalue()).decode()
            prompt = f"วิเคราะห์การแต่งกายสำหรับไป {city} {country} อุณหภูมิ 2°C กิจกรรม: {activity} ระยะเวลา {days} วัน ตอบเป็นภาษาไทย"
            
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }],
                timeout=15.0
            )
            return res.choices[0].message.content, True
        except Exception as e:
            st.error(f"⚠️ AI ขัดข้อง: {str(e)}")
            return fallback_msg, False
    
    return fallback_msg, False

# --- 🎨 5. หน้า Dashboard หลัก ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        st.divider()
        api_key_openai = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key_openai)
        dark_mode = st.toggle(t["theme_label"], value=False)
        
        if dark_mode:
            st.markdown("""<style>.stApp { background-color: #0f172a; color: #f8fafc; } [data-testid="stSidebar"] { background-color: #1e293b; }</style>""", unsafe_allow_html=True)
        
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
            activity = st.multiselect(t["activity_label"], t["activities"], default=[t["activities"][0]])
            gender = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            # ดึงข้อมูล Weather จริง
            w_data = get_weather_data(city)
            bg_url = get_weather_bg(w_data['main_desc'])
            
            # เรียก AI
            result, is_premium = process_analysis(api_key_openai, city, country, activity, use_free_mode, img_file, start, end)

            # --- ส่วนแสดง Weather Card ---
            st.markdown(f"""
                <style>
                .weather-card {{
                    background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.8)), url('{bg_url}');
                    background-size: cover; background-position: center; border-radius: 20px; padding: 25px; color: white; margin-bottom: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                }}
                .weather-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px; }}
                .grid-item {{ background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(15px); padding: 15px; border-radius: 18px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }}
                .grid-label {{ font-size: 11px; opacity: 0.7; margin-bottom: 5px; }}
                .grid-value {{ font-size: 15px; font-weight: 600; }}
                </style>
                <div class="weather-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div style="font-size: 64px; font-weight: bold; line-height: 1;">{w_data['temp']}°C</div>
                            <div style="font-size: 18px; margin-top: 5px;">{w_data['desc']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 13px; opacity: 0.8;">{datetime.now().strftime('%H:%M %p')}</div>
                            <div style="font-size: 22px; font-weight: bold;">{city}</div>
                            <div style="font-size: 13px;">Feels like {w_data['feels_like']}°C</div>
                        </div>
                    </div>
                    <div class="weather-grid">
                        <div class="grid-item"><div class="grid-label">💨 Wind</div><div class="grid-value">{w_data['wind_speed']} m/s</div></div>
                        <div class="grid-item"><div class="grid-label">💧 Humid</div><div class="grid-value">{w_data['humidity']}%</div></div>
                        <div class="grid-item"><div class="grid-label">👁️ Vis</div><div class="grid-value">{w_data['visibility']} km</div></div>
                        <div class="grid-item"><div class="grid-label">🌡️ Pres</div><div class="grid-value">{w_data['pressure']} hPa</div></div>
                        <div class="grid-item"><div class="grid-label">☁️ Cloud</div><div class="grid-value">{w_data['clouds']}%</div></div>
                        <div class="grid-item"><div class="grid-label">❄️ Snow</div><div class="grid-value">Risk: {w_data['temp'] < 2}</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.subheader(t["analysis_title"])
            st.markdown(f'<div style="background:#f1f5f9; padding:20px; border-radius:12px; color:#1e293b;">{result}</div>', unsafe_allow_html=True)

            if is_premium:
                render_3d_model()

            st.divider()
            st.subheader(t["shop_title"])
            for item in t["essentials"]:
                st.markdown(f"""<div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #4f46e5; margin-bottom:10px; color:black;">
                    <strong>🔹 {item}</strong><br><a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank" style="text-decoration:none;color:#4f46e5;">🛒 คลิกเพื่อช้อป</a>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์")

# --- 🔑 6. หน้า Login ---
def login_page():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    st.markdown("""<style>.header-container { text-align: center; padding: 30px 0; }</style>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="header-container"><img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="100">
    <h1>Tripnify</h1><p>{t['login_sub']}</p></div>""", unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.5, 1])
    with c2:
        if st.button("เข้าสู่ระบบด้วย Google", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()
        st.text_input("Username")
        st.text_input("Password", type="password")
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            st.session_state['logged_in'] = True; st.rerun()
        if st.button(t["guest_btn"], use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()

# --- 🚀 7. จุดเริ่มต้นโปรแกรม ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
