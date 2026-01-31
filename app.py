import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# --- 🛍️ 0. ข้อมูลสินค้าจำลอง (Shopping Data) ---
SHOP_ITEMS = {
    "Winter": [
        {"name": "Ultra Warm Down Jacket", "price": "2,500 THB", "link": "https://www.uniqlo.com", "img": "🧥"},
        {"name": "Heattech Thermal Set", "price": "990 THB", "link": "https://www.uniqlo.com", "img": "👕"},
        {"name": "Gore-Tex Winter Boots", "price": "4,200 THB", "link": "https://www.decathlon.co.th", "img": "🥾"}
    ],
    "General": [
        {"name": "Cotton T-Shirt Premium", "price": "350 THB", "link": "https://www.shopee.co.th", "img": "👕"},
        {"name": "Walking Sneakers", "price": "1,800 THB", "link": "https://www.adidas.co.th", "img": "👟"}
    ]
}

# --- 🎨 1. ฟังก์ชันแสดงผล 3D Character Viewer ---
def render_3d_viewer():
    # ในอนาคตสามารถเปลี่ยนเป็น Three.js หรือไฟล์ .glb จริงได้
    components.html("""
        <div id="container" style="width: 100%; height: 400px; background: linear-gradient(180deg, #1e293b, #0f172a); border-radius: 15px; display: flex; align-items: center; justify-content: center; cursor: grab; border: 2px solid #334155;">
            <div style="text-align: center; color: white; font-family: sans-serif;">
                <div style="font-size: 80px; margin-bottom: 10px;">👤</div>
                <h3 style="margin: 0;">3D Outfit Preview</h3>
                <p style="font-size: 12px; color: #94a3b8;">[ คลิกแล้วลากเพื่อหมุนตัวละคร 360° ]</p>
                <div style="margin-top: 15px; padding: 5px 15px; background: #6366f1; border-radius: 20px; font-size: 12px;">Premium AI Rendered</div>
            </div>
        </div>
        <script>
            // ส่วนสำหรับจัดการการหมุน (Mockup Logic)
            const container = document.getElementById('container');
            container.onmousedown = () => { container.style.cursor = 'grabbing'; };
            container.onmouseup = () => { container.style.cursor = 'grab'; };
        </script>
    """, height=420)

# --- 🛍️ 2. ฟังก์ชันแสดงรายการซื้อของ (Shopping Recommendation) ---
def render_shopping_list(weather_type="Winter"):
    st.markdown("### 🛒 สินค้าแนะนำสำหรับทริปนี้")
    items = SHOP_ITEMS.get(weather_type, SHOP_ITEMS["General"])
    
    for item in items:
        with st.container(border=True):
            col_img, col_txt, col_btn = st.columns([0.5, 2, 1])
            with col_img:
                st.markdown(f"## {item['img']}")
            with col_txt:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"<small>{item['price']}</small>", unsafe_allow_html=True)
            with col_btn:
                st.markdown(f"""<a href="{item['link']}" target="_blank">
                    <button style="width:100%; border-radius:8px; border:none; background:#4f46e5; color:white; padding:8px; cursor:pointer;">
                        สั่งซื้อ
                    </button>
                </a>""", unsafe_allow_html=True)

# --- 🖥️ 3. ปรับปรุง Dashboard หลัก ---
def main_dashboard():
    current_lang = st.session_state.get('lang_choice', 'Thai')
    t = LANG_DATA[current_lang]

    # Sidebar (ใช้โค้ดเดิมที่คุณมี)
    with st.sidebar:
        st.subheader(t["settings"])
        st.radio(t["lang_label"], ["Thai", "English"], key='lang_choice', horizontal=True)
        api_key = st.text_input(t["api_label"], type="password")
        dark_mode = st.toggle(t["theme_label"], value=False)
        if st.button(t["logout"], use_container_width=True):
            st.session_state['logged_in'] = False; st.rerun()

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
            
            activity = st.multiselect(t["activity_label"], t["activities"], default=t["activities"][0])
            
            st.divider()
            st.subheader(t["upload_section"])
            tabs = st.tabs(["📁 คลังภาพ", "📸 ถ่ายภาพ"])
            with tabs[0]: img = st.file_uploader("", type=['jpg','png','jpeg'], key="up_main")
            with tabs[1]: cam = st.camera_input("")
            
            # ปุ่ม Run Analysis
            run_clicked = st.button(t["run_btn"], use_container_width=True, type="primary")

    with col2:
        if run_clicked:
            st.subheader("🔍 ผลวิเคราะห์และตัวละคร 3D")
            
            # แสดง 3D Viewer
            render_3d_viewer()
            
            st.success(f"วิเคราะห์เสร็จสิ้น: ชุดนี้เหมาะสำหรับอุณหภูมิ 2°C ใน {city}")
            
            st.divider()
            
            # แสดงรายการซื้อของ (หากเมืองนั้นหนาว เช่น ฮอกไกโด ให้เลือกหมวด Winter)
            weather_mode = "Winter" if "ฮอกไกโด" in city or "โซล" in city else "General"
            render_shopping_list(weather_mode)
            
        else:
            st.info("👈 กรุณากรอกข้อมูลการเดินทางและกดเริ่มวิเคราะห์เพื่อดูโมเดล 3D และรายการสินค้า")

# (ส่วน login_page และ Main Controller ใช้ตามโค้ดเดิมที่รวมไว้ได้เลย)
