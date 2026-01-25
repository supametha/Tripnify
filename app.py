import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล ---
def process_logic(api_key, country, activity, gender, travel_days, use_free_mode, uploaded_file):
    if use_free_mode or not api_key:
        analysis_res = "ประเมินเบื้องต้น: ระบบบันทึกข้อมูลเสื้อผ้าแล้ว (โหมดฟรี)"
        recommendation = f"สรุปแผนสำหรับ {travel_days} วันที่ {country}: แนะนำชุดกันหนาวหนาพิเศษ 3 ชั้น เพื่อรองรับอุณหภูมิ 1.8°C สำหรับกิจกรรม{activity}"
        if gender == "ชาย":
            sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        else:
            sample_img = "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1000"
        return analysis_res, recommendation, sample_img

    try:
        client = OpenAI(api_key=api_key)
        r_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"วางแผนแต่งกายไป {country} {travel_days} วัน กิจกรรม {activity} อากาศ 1.8C"}]
        )
        recommendation = r_resp.choices[0].message.content
        img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} winter outfit", n=1)
        return "วิเคราะห์ AI สำเร็จ", recommendation, img_resp.data[0].url
    except Exception as e:
        return f"Error: {str(e)}", "โปรดเช็ค Key หรือใช้โหมดฟรี", None

# --- 🎨 หน้า Login ---
def login_page():
    st.markdown("<style>.stApp { background-color: #ffffff; } .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; }</style>", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="login-box"><h2>Tripnify Login</h2>', unsafe_allow_html=True)
    st.text_input("อีเมล")
    st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        st.session_state['logged_in'] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .main-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #f1f5f9; margin-bottom: 20px; }
        .metric-box { background: #f8fafc; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e2e8f0; }
        .shop-box { background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 12px; }
        .item-tag { background: #eef2ff; color: #4f46e5; padding: 2px 8px; border-radius: 5px; font-size: 0.85rem; font-weight: 500; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        api_key = st.text_input("OpenAI API Key (ถ้ามี)", type="password")
        use_free_mode = st.toggle("เปิดใช้งานโหมดฟรี (Guest Mode)", value=not api_key)
        st.divider()
        if st.button("ออกจากระบบ"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🗓️ ข้อมูลการเดินทาง")
        country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Thailand", "Vietnam", "Taiwan"])
        d_col1, d_col2 = st.columns(2)
        start_date = d_col1.date_input("วันไป", datetime.now())
        end_date = d_col2.date_input("วันกลับ", datetime.now() + timedelta(days=5))
        travel_days = (end_date - start_date).days
        activity = st.selectbox("กิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย", "ถ่ายรูป/Fashion"])
        gender = st.radio("เพศ", ["ชาย", "หญิง"])
        img_file = st.file_uploader("📸 รูปชุดของคุณ", type=['jpg', 'png'])
        run_btn = st.button("✨ เริ่มวิเคราะห์แผน")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, travel_days, use_free_mode, img_file)
            
            # --- 1. สรุปข้อมูลการเดินทาง ---
            st.markdown("### 📋 สรุปข้อมูลการเดินทาง")
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metric-box"><small>จุดหมาย</small><br><b>{country}</b></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-box"><small>อากาศเฉลี่ย</small><br><b>1.8°C</b></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-box"><small>คำเตือน</small><br><b style="color:#e11d48;">❄️ หนาวจัด</b></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # --- 2. แผนการแต่งกาย (แยกส่วนบน) ---
            st.markdown("### 🎭 แผนการแต่งกายที่แนะนำ")
            if img_url: 
                st.image(img_url, caption="ภาพจำลองตัวละคร 3 มิติ", use_container_width=True)
            st.success(f"**รายละเอียดจาก AI:** {r_out}")
            
            st.divider()

            # --- 3. แหล่งช้อปปิ้ง (แยกส่วนล่าง) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งและคำแนะนำเพิ่มเติม")
            
            shopping_guides = [
                {"item": "เสื้อโค้ทกันหนาว (Down Jacket)", "desc": "เน้นแบบกันลมและกันน้ำเพื่อรักษาความอบอุ่นในร่างกาย"},
                {"item": "ชุดลองจอน (Heattech)", "desc": "ชั้นในสำคัญมากสำหรับการไป {country} ในอุณหภูมิติดลบ"},
                {"item": "ถุงเท้าและรองเท้าบูท", "desc": "ควรเป็นแบบกันลื่นและบุขนหนาภายใน"},
                {"item": "ถุงมือและผ้าพันคอ", "desc": "ช่วยป้องกันผิวแห้งแตกและเก็บความร้อนในส่วนปลายของร่างกาย"},
                {"item": "แผ่นแปะความร้อน (Hot Pack)", "desc": "ตัวช่วยสำคัญสำหรับกิจกรรมกลางแจ้งนานๆ"}
            ]

            for guide in shopping_guides:
                item_name = guide['item']
                st.markdown(f"""
                    <div class="shop-box">
                        <span class="item-tag">แนะนำสำหรับการช้อป</span>
                        <div style="margin-top:8px;"><strong>🔹 {item_name}</strong></div>
                        <div style="font-size:0.9rem; color:#64748b; margin-bottom:10px;">{guide['desc']}</div>
                        <a href='https://shopee.co.th/search?keyword={quote_plus(item_name)}' target='_blank' style='text-decoration:none; font-size:0.85rem; color:#4f46e5;'>🛒 Shopee</a> | 
                        <a href='https://www.lazada.co.th/catalog/?q={quote_plus(item_name)}' target='_blank' style='text-decoration:none; font-size:0.85rem; color:#4f46e5; margin-left:10px;'>🛒 Lazada</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรอกข้อมูลการเดินทางด้านซ้ายเพื่อรับคำแนะนำ")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
