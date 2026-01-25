import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล Logic (ปรับปรุงข้อ 5, 6, 8, 9, 10, 11) ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang):
    # Prompt ภาษาไทย (ข้อ 8)
    if lang == "Thai":
        p_critique = "วิเคราะห์รูปชุดที่อัปโหลดสำหรับอุณหภูมิ 1.8°C ในเกาหลีใต้ ประเมินว่าเหมาะสมหรือไม่ และต้องปรับปรุง 5 ส่วนหลัก: เสื้อนอก, กางเกง, หมวก/พันคอ, รองเท้า, อุปกรณ์เสริม"
        p_outfit = f"แนะนำประเภทชุดที่ต้องเตรียมสำหรับ {country} กิจกรรม {activity} (ไม่ระบุชื่อวัน)"
    else:
        p_critique = "Analyze this outfit for 1.8°C. Critique 5 parts: Outerwear, Pants, Headwear, Footwear, Accessories."
        p_outfit = f"Recommend outfit types for {country} activity {activity} (No daily names)"

    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            v_out = "ไม่พบรูปภาพ" if lang == "Thai" else "No image"
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                v_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": p_critique}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                )
                v_out = v_resp.choices[0].message.content
            
            r_resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": p_outfit}])
            r_out = r_resp.choices[0].message.content
            
            # ข้อ 9: สร้าง 3D สอดคล้องกับผลวิเคราะห์
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D Pixar style {gender} character wearing optimized winter outfit for 1.8C based on: {v_out[:100]}", n=1)
            return v_out, r_out, img_resp.data[0].url
        except Exception as e:
            return f"Error: {e}", "Check API Key", None
    else:
        # ข้อ 5, 6: โหมดฟรี (จำลองการวิเคราะห์ให้สอดคล้องกับรูปที่อัปโหลดเบื้องต้น)
        v_free = "วิเคราะห์เบื้องต้น: ควรเพิ่มความหนาของเสื้อชั้นนอกและเตรียมอุปกรณ์กันหนาวเพิ่ม" if lang == "Thai" else "Basic Analysis: Suggest thicker coat and more accessories."
        r_free = "ประเภทชุดที่ควรเตรียม: เสื้อโค้ท, กางเกงบุขน, รองเท้าบูท" if lang == "Thai" else "Recommended: Heavy coat, Thermal pants, Boots."
        sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000"
        return v_free, r_free, sample_img

# --- 🎨 หน้า Dashboard (ปรับปรุงข้อ 2, 3, 4, 7) ---
def main_dashboard():
    st.markdown("""<style>.analysis-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; line-height: 1.6; } .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ " + ("ตั้งค่า" if lang == "Thai" else "Settings"))
        lang_choice = st.radio("เลือกภาษา (Select Language)", ["Thai", "English"])
        st.divider()
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี" if lang_choice == "Thai" else "Free Mode", value=not api_key)
        if st.button("ออกจากระบบ" if lang_choice == "Thai" else "Logout"): st.session_state['logged_in'] = False; st.rerun()

    # ข้อ 2, 3, 7: ปรับคำสั่งตามภาษาที่เลือก
    label = {
        "dest": "จุดหมาย" if lang_choice == "Thai" else "Destination",
        "start": "วันที่เริ่ม" if lang_choice == "Thai" else "Start Date",
        "end": "วันที่สิ้นสุด" if lang_choice == "Thai" else "End Date",
        "act": "กิจกรรม" if lang_choice == "Thai" else "Activity",
        "gen": "เพศ" if lang_choice == "Thai" else "Gender",
        "up": "📸 อัปโหลดชุด" if lang_choice == "Thai" else "📸 Upload Outfit",
        "btn": "✨ เริ่มวิเคราะห์" if lang_choice == "Thai" else "✨ Analyze"
    }

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ " + ("ข้อมูลการเดินทาง" if lang_choice == "Thai" else "Travel Info"))
            country = st.selectbox(label["dest"], ["South Korea", "Japan", "Vietnam"])
            start_date = st.date_input(label["start"], datetime.now())
            end_date = st.date_input(label["end"], datetime.now() + timedelta(days=5))
            activity = st.selectbox(label["act"], ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio(label["gen"], ["ชาย", "หญิง"] if lang_choice == "Thai" else ["Male", "Female"])
            img_file = st.file_uploader(label["up"], type=['jpg', 'png'])
            run_btn = st.button(label["btn"])

    with col2:
        if run_btn:
            # วิเคราะห์ข้อมูล
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang_choice)
            
            # ข้อ 8: การวิเคราะห์ภาพ (แสดงก่อน)
            st.markdown("### 🔍 " + ("ผลวิเคราะห์การแต่งกาย" if lang_choice == "Thai" else "Outfit Analysis"))
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            st.divider()

            # ข้อ 9, 10: แสดงภาพ 3D ที่สอดคล้อง
            st.markdown("### 🎭 " + ("ภาพจำลองแนะนำ (3D)" if lang_choice == "Thai" else "3D Visual Guide"))
            if img_url: st.image(img_url, use_container_width=True)
            
            # แสดงรายการชุดที่ควรเตรียม (ไม่มีชื่อวัน)
            st.markdown("### 📋 " + ("ประเภทชุดที่ควรเตรียม" if lang_choice == "Thai" else "Recommended Items"))
            st.info(r_out)
            st.divider()

            # ข้อ 11: Shopping Links (แยกส่วนชัดเจน)
            st.markdown("### 🛍️ " + ("แหล่งช้อปปิ้งแนะนำ" if lang_choice == "Thai" else "Shopping Links"))
            shop_items = ["เสื้อโค้ทกันหนาว", "ชุดลองจอน", "หมวกและถุงมือ", "รองเท้าบูท", "แผ่นแปะความร้อน"]
            if lang_choice == "English": shop_items = ["Winter Coat", "Heattech", "Gloves & Beanie", "Winter Boots", "Hot Packs"]

            for item in shop_items:
                st.markdown(f"""<div class="shop-card"><strong>🔹 {item}</strong><br>
                <a href='https://shopee.co.th/search?keyword={quote_plus(item)}' target='_blank'>🛒 Shopee</a> | 
                <a href='https://www.lazada.co.th/catalog/?q={quote_plus(item)}' target='_blank'>🛒 Lazada</a></div>""", unsafe_allow_html=True)
