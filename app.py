import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import quote_plus

def main_dashboard():
    # 1. ตั้งค่าหน้าจอให้กว้างที่สุด
    # หมายเหตุ: ควรใส่ st.set_page_config(layout="wide") ไว้ที่บรรทัดแรกสุดของไฟล์ Python
    
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # --- ✨ Enhanced CSS for Full Screen Balance ---
    st.markdown(f"""
        <style>
        /* จัดการพื้นหลังและ Font */
        .stApp {{
            background-color: #f1f5f9;
        }}
        
        /* Header ด้านบน */
        .top-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 30px;
            background: white;
            border-bottom: 1px solid #e2e8f0;
            margin: -6rem -5rem 2rem -5rem;
        }}

        /* Card Style */
        .glass-card {{
            background: white;
            padding: 25px;
            border-radius: 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }}
        
        /* ผลวิเคราะห์ */
        .analysis-box {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 15px;
            border-left: 6px solid #6366f1;
            font-size: 1rem;
            line-height: 1.6;
            color: #334155;
        }}

        .stButton>button {{
            border-radius: 12px;
            font-weight: 600;
        }}
        </style>
        
        <div class="top-nav">
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://cdn-icons-png.flaticon.com/512/201/201623.png" width="40">
                <h2 style="margin: 0; color: #1e293b;">Tripnify</h2>
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
                <span style="color: #64748b;">ยินดีต้อนรับ, นักเดินทาง 👋</span>
                <div style="width: 40px; height: 40px; background: #6366f1; border-radius: 50%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 🏗️ Main Layout (40:60 Split) ---
    col_input, col_display = st.columns([1, 1.5], gap="large")

    # ---------- ⬅️ ฝั่งซ้าย: ข้อมูลการเดินทาง (Inputs) ----------
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"📍 {t['travel_info']}")
        
        dest_col1, dest_col2 = st.columns(2)
        with dest_col1:
            country = st.selectbox(t["dest"], list(CITY_DATA.keys()))
        with dest_col2:
            city = st.selectbox(t["city"], CITY_DATA[country])

        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start = st.date_input(t["start_date"], datetime.now())
        with date_col2:
            end = st.date_input(t["end_date"], datetime.now() + timedelta(days=3))

        activity = st.multiselect(t["activity_label"], t["activities"], default=[t["activities"][0]])
        gender = st.radio(t["gender"], [t["male"], t["female"]], horizontal=True)
        st.session_state['gender_val'] = gender

        st.divider()
        st.subheader(f"📸 {t['upload_section']}")
        img_tabs = st.tabs(["📁 คลังภาพ", "📸 ถ่ายภาพ"])
        with img_tabs[0]:
            img_file = st.file_uploader("", type=['jpg','png','jpeg'])
        with img_tabs[1]:
            cam_file = st.camera_input("")
        
        active_img = img_file if img_file else cam_file
        
        run_btn = st.button(t["run_btn"], use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- ➡️ ฝั่งขวา: ผลลัพธ์และการแสดงผล (Output) ----------
    with col_display:
        if run_btn:
            # จำลอง/เรียกใช้ Logic การวิเคราะห์
            # (ใส่ตัวแปร api_key, use_free_mode ตามโครงสร้างเดิมของคุณ)
            result, is_premium = process_analysis(None, city, country, activity, True, active_img, start, end)

            # 🌤️ Weather & Summary Section
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            w_col1, w_col2 = st.columns([1, 2])
            with w_col1:
                st.metric(t["temp_label"], "2°C", "-1°C")
            with w_col2:
                st.info(f"❄️ **สภาพอากาศ:** หนาวจัดและอาจมีหิมะใน {city} แนะนำให้เตรียมชุดกันลม")
            
            st.markdown(f'<div class="analysis-box"><b>🔍 วิเคราะห์ชุดแต่งกาย:</b><br>{result}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 🎭 3D Model Section (โดดเด่นที่สุด)
            st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
            render_3d_model() # เรียกฟังก์ชัน Full Body ที่เราทำไว้
            st.markdown('</div>', unsafe_allow_html=True)

            # 🛍️ Shopping Recommendation
            with st.expander(f"🛍️ {t['shop_title']}", expanded=False):
                shop_cols = st.columns(len(t["essentials"]))
                for idx, item in enumerate(t["essentials"]):
                    with shop_cols[idx]:
                        st.markdown(f"""
                            <div style="text-align: center; padding: 10px; border: 1px solid #eee; border-radius: 10px;">
                                <small>{item}</small><br>
                                <a href="https://shopee.co.th/search?keyword={quote_plus(item)}" target="_blank" style="font-size: 12px; color: #6366f1;">ช้อปเลย</a>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            # หน้าว่างเมื่อยังไม่มีการวิเคราะห์
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; color: #94a3b8; border: 2px dashed #e2e8f0; border-radius: 24px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1048/1048953.png" width="100" style="opacity: 0.3; margin-bottom: 20px;">
                    <h3>พร้อมสำหรับการเดินทางหรือยัง?</h3>
                    <p>กรอกข้อมูลด้านซ้ายแล้วกดปุ่มเพื่อเริ่มวางแผนชุดแต่งกายของคุณ</p>
                </div>
            """, unsafe_allow_html=True)

    # ปุ่ม Logout อยู่ในจุดที่เหมาะสม (เช่น Sidebar หรือปุ่มจิ๋วที่มุม)
    if st.sidebar.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
