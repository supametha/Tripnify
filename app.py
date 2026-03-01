import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import requests

# -------------------------------
# 🌦️ Weather Function (เพิ่มใหม่)
# -------------------------------
def get_real_weather(city_name, api_key):
    if not api_key:
        return {
            "temp": 2,
            "feels_like": -1,
            "desc": "กรุณาใส่ API Key",
            "main": "Clouds",
            "wind": 5,
            "humidity": 80,
            "visibility": 10,
            "pressure": 1015,
            "clouds": 90
        }
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
    except:
        pass

    return {
        "temp": 2,
        "feels_like": -1,
        "desc": "Error: เชื่อมต่อไม่ได้",
        "main": "Clouds",
        "wind": 5,
        "humidity": 80,
        "visibility": 10,
        "pressure": 1015,
        "clouds": 90
    }

def get_weather_bg(main):
    if main == "Snow":
        return "https://images.unsplash.com/photo-1608889175123-8ee362201f3d"
    elif main == "Rain":
        return "https://images.unsplash.com/photo-1501696461415-6bd6660c6742"
    elif main == "Clear":
        return "https://images.unsplash.com/photo-1501973801540-537f08ccae7b"
    elif main == "Clouds":
        return "https://images.unsplash.com/photo-1499346030926-9a72daac6c63"
    else:
        return "https://images.unsplash.com/photo-1502082553048-f009c37129b9"

# -------------------------------
# 🎭 3D Model
# -------------------------------
def render_3d_model():
    st.markdown("### 🎭 3D Outfit Character Preview")
    components.html("""
        <div id="viewer-3d" style="width:100%;height:400px;
        background:radial-gradient(circle,#334155 0%,#0f172a 100%);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        position:relative;cursor:grab;border:2px solid #6366f1;">
            <div id="character" style="font-size:150px;transition:transform 0.1s linear;">🧥</div>
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
# ⚙️ AI Analysis
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
# 🌍 Dashboard
# -------------------------------
def main_dashboard():

    with st.sidebar:
        st.subheader("⚙️ Settings")
        api_key = st.text_input("OpenAI API Key", type="password")

        # เพิ่มช่อง Weather API
        weather_api_key = st.text_input(
            "🌦️ OpenWeatherMap API Key",
            type="password"
        )

        use_free_mode = st.toggle("Free Mode", value=not api_key)

    st.title("🌍 Tripnify Dashboard")

    country = st.selectbox("Country", ["ญี่ปุ่น", "เกาหลีใต้"])
    city = st.selectbox("City", ["โตเกียว", "โซล"])

    start = st.date_input("Start", datetime.now())
    end = st.date_input("End", datetime.now() + timedelta(days=3))

    img = st.file_uploader("Upload Image")

    if st.button("✨ Start Analysis"):

        # ดึง Weather จริง
        w = get_real_weather(city, weather_api_key)
        bg_url = get_weather_bg(w["main"])

        result, is_premium = process_analysis(
            api_key, city, country, [],
            use_free_mode, img, start, end
        )

        # Weather Card ใหม่
        st.markdown(f"""
        <div style="
            background: linear-gradient(rgba(0,0,0,0.4),rgba(0,0,0,0.5)), url('{bg_url}');
            background-size: cover;
            border-radius: 25px;
            padding: 25px;
            color: white;
            margin-bottom: 20px;">
            <h1 style="font-size:60px;margin:0;">{w['temp']}°C</h1>
            <h3 style="margin:0;">{city}</h3>
            <p>Feels like {w['feels_like']}°C • {w['desc']}</p>
            <hr>
            💨 {w['wind']} m/s |
            💧 {w['humidity']}% |
            ☁️ {w['clouds']}%
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🔍 Outfit Analysis")
        st.write(result)

        if is_premium:
            render_3d_model()


# -------------------------------
# 🚀 Run
# -------------------------------
main_dashboard()
