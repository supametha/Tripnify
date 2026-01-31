# =============================
# Tripnify - Clean Streamlit App
# =============================

import streamlit as st
from openai import OpenAI
from urllib.parse import quote_plus
import json

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="Tripnify", layout="wide")

# -----------------------------
# Shopping Platforms
# -----------------------------
SHOP_PLATFORMS = {
    "Shopee": {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/f/fe/Shopee.svg",
        "url": "https://shopee.co.th/search?keyword="
    },
    "Uniqlo": {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/9/92/UNIQLO_logo.svg",
        "url": "https://www.uniqlo.com/th/th/search?q="
    },
    "Lazada": {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Lazada_logo_2019.svg",
        "url": "https://www.lazada.co.th/catalog/?q="
    }
}

# -----------------------------
# Analysis (Mock / AI)
# -----------------------------

def process_analysis(api_key, country, city, activity, free_mode):
    if free_mode or not api_key:
        return "อากาศหนาว เหมาะกับการใส่เสื้อผ้าหลายชั้น เน้นกันลมและกันหนาว"

    client = OpenAI(api_key=api_key)
    prompt = f"""
    วิเคราะห์การแต่งกายสำหรับ:
    ประเทศ: {country}
    เมือง: {city}
    กิจกรรม: {activity}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

# -----------------------------
# Extract Shopping Items
# -----------------------------

def extract_shopping_items(api_key, analysis_text, free_mode):
    if free_mode or not api_key:
        return [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "ป้องกันลมและอากาศหนาว"},
            {"name": "Heattech แขนยาว", "reason": "ช่วยเก็บความร้อน"},
            {"name": "รองเท้ากันลื่น", "reason": "ลดการลื่นบนพื้นหิมะ"}
        ]

    client = OpenAI(api_key=api_key)
    prompt = f"""
    จากผลวิเคราะห์:
    {analysis_text}

    สรุปรายการสินค้าที่ควรซื้อ 3-5 รายการ
    ตอบเป็น JSON เท่านั้น
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(res.choices[0].message.content)

# -----------------------------
# UI
# -----------------------------

def main_dashboard():
    st.title("🧳 Tripnify – Outfit & Shopping Assistant")

    with st.sidebar:
        api_key = st.text_input("OpenAI API Key (Premium)", type="password")
        free_mode = st.checkbox("Free Mode", value=not bool(api_key))
        country = st.text_input("Country", "Japan")
        city = st.text_input("City", "Sapporo")
        activity = st.text_input("Activity", "Travel")
        run_btn = st.button("Analyze")

    if not run_btn:
        st.info("กรอกข้อมูลแล้วกด Analyze")
        return

    # Analysis
    result = process_analysis(api_key, country, city, activity, free_mode)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🧠 Analysis Result")
        st.write(result)

        if not free_mode:
            st.success("🎭 3D Outfit Character Preview (Premium)")
            st.write("[3D Model Render Placeholder]")
        else:
            st.image("https://images.unsplash.com/photo-1520975916090-3105956dac38",
                     caption="Outfit Reference", use_column_width=True)

    with col2:
        st.subheader("🛍️ Shopping Recommendations")
        shopping_items = extract_shopping_items(api_key, result, free_mode)

        for item in shopping_items:
            st.markdown(f"**🧥 {item['name']}**")
            st.caption(item['reason'])

            cols = st.columns(len(SHOP_PLATFORMS))
            for i, (platform, data) in enumerate(SHOP_PLATFORMS.items()):
                with cols[i]:
                    url = data['url'] + quote_plus(item['name'])
                    st.markdown(
                        f"<a href='{url}' target='_blank'>"
                        f"<img src='{data['icon']}' style='height:40px'>"
                        f"</a>",
                        unsafe_allow_html=True
                    )
            st.divider()

# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    main_dashboard()
