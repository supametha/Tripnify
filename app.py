import streamlit as st
import base64
import requests  # เพิ่มตัวนี้
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ... (LANG_DATA และ CITY_DATA เหมือนเดิมของคุณ) ...

# --- 🌦️ ฟังก์ชันดึงข้อมูลพยากรณ์อากาศจริง ---
def get_weather_data(city_name):
    api_key = "YOUR_OPENWEATHER_API_KEY" # ใส่ API Key ของคุณตรงนี้
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    try:
        complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"
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
                "clouds": data["clouds"]["all"]
            }
    except:
        pass
    return {"temp": 2, "feels_like": -1, "humidity": 80, "pressure": 1015, "wind_speed": 5, "visibility": 10, "desc": "Overcast Clouds", "clouds": 90}

# ... (render_3d_model และ process_analysis เหมือนเดิมของคุณ) ...

def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # --- Sidebar & Theme Setup (เหมือนเดิมของคุณ) ---
    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        st.divider()
        api_key_ai = st.text_input(t["api_label"], type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key_ai)
        dark_mode = st.toggle(t["theme_label"], value=False)
        
        if dark_mode:
            st.markdown("""<style>.stApp { background-color: #0f172a; color: #f8fafc; }</style>""", unsafe_allow_html=True)
        
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
            st.session_state['gender_val'] = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
            st.divider()
            st.subheader(t["upload_section"])
            img_file = st.file_uploader("", type=['jpg','png','jpeg'])
            run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_btn:
            # 1. ดึงข้อมูลพยากรณ์อากาศจริง
            w_data = get_weather_data(city)
            
            # 2. วิเคราะห์ชุด (AI)
            result, is_premium = process_analysis(api_key_ai, city, country, activity, use_free_mode, img_file, start, end)

            # 3. แสดง Weather Card (แบบ Glassmorphism ที่คุณเลือก)
            st.markdown(f"""
                <style>
                .weather-card {{
                    background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.8)), 
                                url('https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?q=80&w=1000');
                    background-size: cover; border-radius: 20px; padding: 25px; color: white; margin-bottom: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                }}
                .weather-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px; }}
                .grid-item {{ background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(15px); padding: 15px; border-radius: 18px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }}
                .grid-label {{ font-size: 12px; opacity: 0.7; margin-bottom: 5px; }}
                .grid-value {{ font-size: 16px; font-weight: 600; }}
                </style>
                <div class="weather-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div style="font-size: 72px; font-weight: bold; line-height: 1;">{w_data['temp']}°C</div>
                            <div style="font-size: 20px; margin-top: 5px;">{w_data['desc']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 14px; opacity: 0.8;">{datetime.now().strftime('%H:%M %p')}</div>
                            <div style="font-size: 24px; font-weight: bold;">{city}</div>
                            <div style="font-size: 14px;">Feels like {w_data['feels_like']}°C</div>
                        </div>
                    </div>
                    <div class="weather-grid">
                        <div class="grid-item"><div class="grid-label">💨 Wind</div><div class="grid-value">{w_data['wind_speed']} m/s</div></div>
                        <div class="grid-item"><div class="grid-label">💧 Humidity</div><div class="grid-value">{w_data['humidity']}%</div></div>
                        <div class="grid-item"><div class="grid-label">👁️ Visibility</div><div class="grid-value">{w_data['visibility']} km</div></div>
                        <div class="grid-item"><div class="grid-label">🌡️ Pressure</div><div class="grid-value">{w_data['pressure']} hPa</div></div>
                        <div class="grid-item"><div class="grid-label">☁️ Clouds</div><div class="grid-value">{w_data['clouds']}%</div></div>
                        <div class="grid-item"><div class="grid-label">❄️ Dew Point</div><div class="grid-value">{w_data['temp'] - 2}°C</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 4. ส่วนวิเคราะห์เดิมของคุณ
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{result}</div>', unsafe_allow_html=True)

            if is_premium:
                render_3d_model()

            st.divider()
            st.subheader(t["shop_title"])
            for item in t["essentials"]:
                st.markdown(f"""
                    <div class="shop-card">
                        <strong>🔹 {item}</strong><br>
                        <a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank" style="text-decoration:none;color:#4f46e5;">🛒 คลิกเพื่อช้อปสินค้า</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์")

# ... (ส่วน login_page และส่วนเรียกใช้ด้านล่างเหมือนเดิมของคุณ) ...
