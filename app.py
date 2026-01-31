import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- 🌐 0. ระบบจัดการภาษา ---
LANG_DICT = {
    "Thai": {
        "settings": "⚙️ ตั้งค่า",
        "lang_label": "เลือกภาษา",
        "free_mode": "โหมดใช้งานฟรี",
        "theme_label": "โหมดแอป",
        "light": "สว่าง",
        "dark": "มืด",
        "logout": "ออกจากระบบ",
        "travel_info": "🗓️ ข้อมูลการเดินทาง",
        "dest": "จุดหมาย",
        "start": "วันที่เริ่ม",
        "end": "วันที่สิ้นสุด",
        "activity": "กิจกรรม",
        "gender": "เพศ",
        "male": "ชาย",
        "female": "หญิง",
        "upload": "📸 อัปโหลดรูปชุด",
        "camera": "🤳 หรือเปิดกล้องถ่ายภาพชุด",
        "run": "✨ เริ่มวิเคราะห์",
        "temp": "🌡️ อุณหภูมิเฉลี่ย",
        "warn": "⚠️ **สถานะอากาศ: หนาวจัด** | โปรดเตรียมเครื่องกันหนาวให้พร้อม",
        "analysis_title": "🔍 ผลวิเคราะห์การแต่งกาย",
        "ai_img": "🎭 ภาพจำลองแนะนำ",
        "essential_title": "📋 สิ่งที่ควรเตรียมเพิ่มเติม",
        "shop_title": "🛍️ แหล่งช้อปปิ้งแนะนำ",
        "info_click": "💡 คลิกเพื่อดูรายละเอียด",
        "essentials": [
            "เสื้อโค้ทกันหนาวหนาพิเศษ", "กางเกงบุขนกันหนาว", "หมวกไหมพรมและผ้าพันคอ", "รองเท้าบูทกันหนาว", "แผ่นแปะความร้อนและถุงมือ"
        ]
    },
    "English": {
        "settings": "⚙️ Settings",
        "lang_label": "Language",
        "free_mode": "Free Mode",
        "theme_label": "App Mode",
        "light": "Light",
        "dark": "Dark",
        "logout": "Logout",
        "travel_info": "🗓️ Travel Info",
        "dest": "Destination",
        "start": "Start Date",
        "end": "End Date",
        "activity": "Activity",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "upload": "📸 Upload Outfit",
        "camera": "🤳 or Use Camera",
        "run": "✨ Run Analysis",
        "temp": "🌡️ Avg Temp",
        "warn": "⚠️ **Weather: Extreme Cold** | Please prepare winter gear",
        "analysis_title": "🔍 Outfit Analysis",
        "ai_img": "🎭 AI Generated Image",
        "essential_title": "📋 Additional Essentials",
        "shop_title": "🛍️ Recommended Shopping",
        "info_click": "💡 Click for details",
        "essentials": [
            "Heavy Winter Down Jacket", "Fleece Lined Pants", "Beanie & Scarf", "Winter Boots", "Heat Packs & Gloves"
        ]
    }
}

# --- ⚙️ 1. ฟังก์ชันประมวลผล Logic ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang, start_date, end_date):
    days = (end_date - start_date).days + 1
    t = LANG_DICT[lang]
    
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            p_critique = f"Analyze this outfit for 1.8°C in {country} ({days} days). Summary in {lang}."
            p_detail = f"Packing list for {country} for {days} days, Activity: {activity} in {lang}."

            v_out = "No image found"
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                v_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": p_critique},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}]
                )
                v_out = v_resp.choices[0].message.content
            
            r_resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": p_detail}])
            r_out = r_resp.choices[0].message.content
            
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter gear Pixar style", n=1)
            return v_out, r_out, img_resp.data[0].url
        except Exception as e:
            return f"Error: {e}", "Check API Key", None
    else:
        v_free = "1. **Outer**: Down Jacket\n2. **Bottom**: Fleece Lined\n3. **Head**: Beanie\n4. **Feet**: Wool Socks\n5. **Extra**: Hot Packs" if lang == "English" else "1. **เสื้อชั้นนอก**: ควรใช้ Padding Jacket\n2. **กางเกง**: กางเกงบุขน\n3. **ศีรษะ**: หมวกไหมพรม\n4. **เท้า**: ถุงเท้าขนแกะ\n5. **เสริม**: แผ่นแปะความร้อน"
        r_free = f"Suggest: {max(1, days//2)} extra sets."
        sample_img = "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"
        return v_free, r_free, sample_img

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    # ดึงภาษาที่เลือก
    lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DICT[lang]

    # Sidebar Settings
    with st.sidebar:
        st.title(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice')
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle(t["free_mode"], value=not api_key)
        
        # 2. เพิ่มปุ่มสลับโหมดสว่าง/มืด (Theme Toggle)
        theme_mode = st.toggle(t["theme_label"], value=False, help="Light/Dark Mode")
        theme_css = """
            <style>
            .stApp { background-color: #121212; color: white; }
            .analysis-box { background: #1e1e1e !important; color: #e0e0e0 !important; border: 1px solid #333 !important; }
            .shop-card { background: #252525 !important; color: white !important; border: 1px solid #444 !important; }
            </style>
        """ if theme_mode else """
            <style>
            .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
            .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
            </style>
        """
        st.markdown(theme_css, unsafe_allow_html=True)

        if st.button(t["logout"], use_container_width=True): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader(t["travel_info"])
            # --- แก้ไขบรรทัดที่ 165 เป็นต้นไป ในฟังก์ชัน login_page ---

    # 1. แสดงโลโก้ใหม่และชื่อแอปให้สวยขึ้น
    col_logo, col_text = st.columns([1, 4])
    with col_logo:
        # ใส่ URL รูปโลโก้ที่คุณเลือก (ตัวอย่างนี้ใช้รูปที่คุณอัปโหลดล่าสุด)
        st.image("https://path-to-your-logo/tripnify_logo.png", width=80) 
    with col_text:
        st.markdown("<h1 style='margin-top: -10px;'>Tripnify</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: gray;'>จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ</p>", unsafe_allow_html=True)
    
    st.markdown("---")
            
            w_col1, w_col2 = st.columns([1, 2])
            with w_col1: st.metric(label=t["temp"], value="1.8°C")
            with w_col2: st.warning(t["warn"])
            
            st.divider()
            st.markdown(f"### {t['analysis_title']}")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            if img_url: 
                st.markdown(f"### {t['ai_img']}")
                st.image(img_url, use_container_width=True)
            
            st.markdown(f"### {t['essential_title']}")
            for i, item in enumerate(t["essentials"], 1):
                st.write(f"{i}. **{item}**")
            
            st.markdown(f"### {t['shop_title']}")
            for it in t["essentials"]:
                st.markdown(f"""<div class="shop-card"><strong>🔹 {it}</strong><br>
                    <a href='https://shopee.co.th/search?keyword={quote_plus(it)}' target='_blank'>🛒 Shopee</a> | 
                    <a href='https://www.lazada.co.th/catalog/?q={quote_plus(it)}' target='_blank'>🛒 Lazada</a></div>""", unsafe_allow_html=True)
        else:
            st.info("👈 " + ("Please enter info and run" if lang=="English" else "กรุณากรอกข้อมูลและกดเริ่มวิเคราะห์"))

# --- 🔑 3. หน้า Login ---
def login_page():
    st.markdown("""<style>
        .stButton > button { border-radius: 8px; height: 3.5em; font-weight: 500; }
        .social-container { display: flex; align-items: center; justify-content: center; background-color: white; border: 1px solid #dadce0; border-radius: 8px; padding: 10px; margin-bottom: -48px; pointer-events: none; position: relative; z-index: 10; }
        .social-text { color: #3c4043; font-family: sans-serif; font-weight: 500; font-size: 14px; }
    </style>""", unsafe_allow_html=True)

    st.title("🌍 Tripnify Login")
    st.subheader("จัดกระเป๋าให้พร้อมสำหรับทุกสภาพอากาศ")
    st.markdown("---")
    
    google_logo = "https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png"
    facebook_logo = "https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg"

    st.markdown(f'<div class="social-container"><img src="{google_logo}" width="18px" style="margin-right: 12px;"><span class="social-text">เข้าสู่ระบบด้วยบัญชี Google</span></div>', unsafe_allow_html=True)
    if st.button("", use_container_width=True, key="google_login"):
        st.session_state['logged_in'] = True
        st.rerun()

    st.write("") 
    st.markdown(f'<div class="social-container"><img src="{facebook_logo}" width="20px" style="margin-right: 12px;"><span class="social-text">เข้าสู่ระบบด้วยบัญชี Facebook</span></div>', unsafe_allow_html=True)
    if st.button("", use_container_width=True, key="fb_login"):
        st.session_state['logged_in'] = True
        st.rerun()
    
    st.markdown("<p style='text-align: center; color: gray; margin: 20px 0;'>หรือ</p>", unsafe_allow_html=True)
    user = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="กรอกชื่อผู้ใช้งาน")
    password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน")
    
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("🔑 เข้าสู่ระบบ", use_container_width=True):
            if user: st.session_state['logged_in'] = True; st.rerun()
    with col_r:
        if st.button("👤 ทดลองใช้ (Guest)", use_container_width=True):
            st.session_state['logged_in'] = True; st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("<center>Tripnify - Travel Smart, Dress Right</center>", unsafe_allow_html=True)

# --- 🚀 4. ส่วนควบคุมหลัก ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()
