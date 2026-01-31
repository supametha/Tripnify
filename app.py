# app.py
# -------------------------------
# Tripnify – Clean Version (Run 100%)
# -------------------------------

import streamlit as st
import os
from typing import List, Dict

# -------------------------------
# Basic Config
# -------------------------------
st.set_page_config(page_title="Tripnify", layout="wide")

# -------------------------------
# Constants / Static Data
# -------------------------------
CITY_DATA = {
    "Seoul": {
        "temp": 2,
        "weather": "Cold",
        "style": "Layered winter casual"
    },
    "Tokyo": {
        "temp": 8,
        "weather": "Cool",
        "style": "Light jacket casual"
    },
    "Bangkok": {
        "temp": 32,
        "weather": "Hot",
        "style": "Breathable summer wear"
    }
}

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

# -------------------------------
# Helper Functions
# -------------------------------

def extract_shopping_items(style: str) -> List[Dict]:
    """Mock outfit-to-item mapping (replace with OpenAI later)"""
    if "winter" in style.lower():
        return [
            {"name": "Down Jacket", "reason": "Keeps body warm in cold weather"},
            {"name": "Knit Sweater", "reason": "Layering for insulation"},
            {"name": "Winter Boots", "reason": "Protect feet from cold"}
        ]
    elif "summer" in style.lower():
        return [
            {"name": "Linen Shirt", "reason": "Breathable fabric"},
            {"name": "Shorts", "reason": "Reduce heat accumulation"},
            {"name": "Sandals", "reason": "Comfortable in hot climate"}
        ]
    else:
        return [
            {"name": "Light Jacket", "reason": "Adaptable to cool weather"},
            {"name": "Sneakers", "reason": "Comfort for walking"}
        ]


def render_shop_links(item_name: str):
    cols = st.columns(len(SHOP_PLATFORMS))
    for col, (shop, data) in zip(cols, SHOP_PLATFORMS.items()):
        with col:
            st.image(data["icon"], width=60)
            st.link_button(
                f"Search {shop}",
                data["url"] + item_name.replace(" ", "+")
            )

# -------------------------------
# UI
# -------------------------------

st.title("🧳 Tripnify – Outfit & Shopping Assistant")

city = st.selectbox("Select destination city", CITY_DATA.keys())
city_info = CITY_DATA[city]

st.subheader(f"Weather in {city}")
st.write(f"Temperature: **{city_info['temp']}°C**")
st.write(f"Recommended style: **{city_info['style']}**")

# -------------------------------
# Outfit Recommendation
# -------------------------------

st.subheader("👕 Recommended Items")
items = extract_shopping_items(city_info["style"])

for item in items:
    with st.expander(item["name"]):
        st.write(item["reason"])
        render_shop_links(item["name"])

# -------------------------------
# Premium Section (Mock)
# -------------------------------

st.divider()
st.subheader("✨ Premium Feature")

api_key = st.text_input("OpenAI API Key (Premium)", type="password")

if api_key:
    st.success("3D Outfit Character Preview Enabled (mock)")
    st.image("https://dummyimage.com/400x400/cccccc/000000&text=3D+Outfit+Preview")
else:
    st.info("Free mode: image reference only")
    st.image("https://dummyimage.com/400x400/eeeeee/000000&text=Outfit+Image")
