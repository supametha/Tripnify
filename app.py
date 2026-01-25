import streamlit as st
import base64
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ 1. ฟังก์ชันหลักในการประมวลผล ---
def process_logic(api_key, country, activity, gender, use_free_mode, uploaded_file, lang, start_date, end_date):
    # Prompt สำหรับโหมด OpenAI API Key
    if lang == "Thai":
        p_critique = f"วิเคราะห์รูปชุดนี้สำหรับอากาศ 1.8°C ใน {country} ระหว่างวันที่ {start_date} ถึง {end_date} โดยสรุปแยกเป็น 5 ข้อหลักตามลำดับ: 1.เสื้อผ้าชั้นนอก 2.กางเกง 3.หมวกและผ้าพันคอ 4.รองเท้า 5.อุปกรณ์เสริม"
        p_outfit = f"แนะนำการเตรียมชุดไป {country} ช่วง {start_date} ถึง {end_date} สำหรับกิจกรรม {activity} (สรุปเป็นหมวดหมู่ ไม่ระบุวัน)"
    else:
        p_critique = f"Critique this outfit for 1.8°C in {country} from {start_date} to {end_date}. Summary in 5 areas: 1.Outerwear 2.Pants 3.Headwear 4.Footwear 5.Accessories."
        p_outfit = f"Recommend clothing for {country} from {start_date} to {end_date} for {activity}."

    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            v_out = "ไม่พบรูปภาพ" if lang == "Thai" else "No image"
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
            
            r_resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": p_outfit}])
            r_out = r_resp.choices[0].message.content
            
            img_prompt = f"3D Pixar style character {gender} in {country} wearing professional winter gear for 1.8C weather, high detail."
            img_resp = client.images.generate(model="dall-e-3", prompt=img_prompt, n=1)
            return v_out, r_out, img_resp.data[0].url
        except Exception as e:
            return f"Error: {str(e)}", "Please check your API Key", None
    else:
        # --- 1. จัดเรียงโหมดฟรีให้เป็นระเบียบตามภาพ (image_4773b2) ---
        v_free = """
        **วิเคราะห์ภาพถ่ายเบื้องต้น:**
        1. **เสื้อชั้นนอก:** ควรใช้ Padding Jacket หรือ Down Coat ที่หนาขึ้น
        2. **กางเกง:** แนะนำกางเกงบุขน (Fleece Lined) หรือ Heattech ชั้นใน
        3. **ส่วนศีรษะ:** ควรเพิ่มหมวกไหมพรมเพื่อป้องกันการสูญเสียความร้อน
        4. **เท้า:** รองเท้าผ้าใบปกติอาจไม่อุ่นพอ ควรใช้ถุงเท้าขนแกะ
        5. **เสริม:** ควรเตรียมถุงมือและแผ่นแปะความร้อน (Hot Pack)
        """
        r_free = f"แผนการเดินทางระยะสั้นใน {country} ควรเน้นการรักษาอุณหภูมิร่างกายเป็นหลัก"
        sample_img = "https://images.unsplash.com/photo-1548126032-079a0fb0099d?q=80&w=1000"
        return v_free, r_free, sample_img

# --- 🎨 2. หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>
        .analysis-box { background: #fdf6e3; padding: 20px; border-radius: 12px; border: 1px solid #eee8d5; color: #657b83; }
        .shop-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 10px; }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        lang = st.radio("เลือกภาษา", ["Thai", "English"], key='lang_choice')
        api_key = st.text_input("OpenAI API Key", type="password")
        use_free_mode = st.toggle("โหมดใช้งานฟรี", value=not api_key)
        if st.button("ออกจากระบบ"): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        with st.container(border=True):
            st.subheader("🗓️ ข้อมูลการเดินทาง")
            country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Vietnam"])
            # --- 2. เพิ่มวันไป-กลับ (ทั้ง 2 โหมด) ---
            start_date = st.date_input("วันที่เริ่มเดินทาง", datetime.now())
            end_date = st.date_input("วันที่สิ้นสุดเดินทาง", datetime.now() + timedelta(days=5))
            
            activity = st.selectbox("กิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย"])
            gender = st.radio("เพศ", ["ชาย", "หญิง"])
            img_file = st.file_uploader("📸 อัปโหลดรูปชุด", type=['jpg', 'png'])
            run_btn = st.button("✨ เริ่มวิเคราะห์")

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, use_free_mode, img_file, lang, start_date, end_date)
            
            st.markdown("### 🔍 ผลวิเคราะห์การแต่งกาย")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            
            st.markdown("### 🎭 ภาพจำลองแนะนำ")
            if img_url: st.image(img_url, use_container_width=True)
            
            # --- 3. เพิ่มรายละเอียดเพิ่มเติมในส่วนสิ่งที่ควรเตรียม (OpenAI Key Mode) ---
            st.markdown("### 📋 สิ่งที่ควรเตรียมเพิ่มเติม")
            st.info(r_out)
            
            st.markdown("### 🛒 รายการที่ควรเลือกซื้อเพิ่ม (5 อย่างหลัก)")
            items = ["เสื้อโค้ทกันหนาวหนาพิเศษ", "กางเกงบุขน", "หมวกไหมพรม/ผ้าพันคอ", "รองเท้าบูท", "แผ่นแปะความร้อน"]
            for it in items:
                st.markdown(f"""<div class="shop-card"><strong>🔹 {it}</strong><br>
                <a href='https://shopee.co.th/search?keyword={quote_plus(it)}' target='_blank'>🛒 Shopee</a> | 
                <a href='https://www.lazada.co.th/catalog/?q={quote_plus(it)}' target='_blank'>🛒 Lazada</a></div>""", unsafe_allow_html=True)
