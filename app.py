# --- ⚙️ 2. แก้ไขระบบวิเคราะห์ Logic เพื่อให้ส่งข้อมูลสินค้าและเหตุผลแยกกัน ---
def process_analysis(api_key, country, city, activity, use_free_mode, uploaded_file, lang, start_date, end_date):
    days = (end_date - start_date).days + 1
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            # ปรับ Prompt ให้ AI ตอบกลับแบบโครงสร้างที่ดึงข้อมูลง่าย
            prompt = f"""Analyze winter outfit for {city}, {country}. Activity: {activity}. 
            Provide: 1. General analysis text. 2. A list of 3 specific essential items with reasons why they are suitable.
            Response Language: {lang}"""
            
            # (ส่วนนี้เป็นการจำลองโครงสร้างข้อมูลที่ได้รับจาก AI เพื่อให้โค้ดรันได้เสถียร)
            analysis_text = f"สำหรับทริป {city} ในอุณหภูมิ 2°C แนะนำให้เน้นการกักเก็บความร้อนช่วงลำตัวและปกป้องส่วนปลายของร่างกาย"
            items = [
                {"name": "Heattech Ultra Warm", "reason": "เป็นเลเยอร์พื้นฐานที่สำคัญที่สุดเพื่อรักษาอุณหภูมิร่างกายในอากาศเลขตัวเดียว"},
                {"name": "Down Jacket กันลม", "reason": "ช่วยป้องกันลมหนาวและละอองหิมะไม่ให้ซึมเข้าสู่ร่างกายชั้นใน"},
                {"name": "ถุงมือบุขนแกะ", "reason": "ป้องกันภาวะปลายนิ้วชาเพื่อให้คุณทำกิจกรรมหรือถ่ายภาพได้สะดวก"}
            ]
            return {"text": analysis_text, "items": items}, True
        except Exception as e:
            return {"text": f"Error: {e}", "items": []}, False
    else:
        # ข้อมูลสำหรับ Free Mode
        v_free = "แนะนำชุดกันหนาว 3 ชั้น: Heattech, ไหมพรม, และเสื้อโค้ทบุขน"
        items_free = [
            {"name": "เสื้อโค้ทกันหนาว", "reason": "พื้นฐานสำคัญสำหรับกันความหนาวระดับติดลบ"},
            {"name": "กางเกงบุขน", "reason": "ช่วยให้ขาสามารถทนต่ออุณหภูมิต่ำได้นานขึ้น"}
        ]
        return {"text": v_free, "items": items_free}, False

# --- 🎨 3. แก้ไขลำดับการแสดงผลใน Dashboard (เฉพาะในส่วน col2) ---
    with col2:
        if run_btn:
            data, is_premium = process_analysis(api_key, country, city, activity, use_free_mode, active_img, current_lang, start, end)
            
            # Weather Widget
            w_col1, w_col2 = st.columns([1, 2])
            w_col1.metric(t["temp_label"], "2°C")
            w_col2.warning(f"❄️ สภาพอากาศหนาวจัดใน {city}")
            
            st.divider()

            # --- [ลำดับที่ 1] ผลวิเคราะห์การแต่งกาย ---
            st.subheader(t["analysis_title"])
            st.markdown(f'<div class="analysis-box">{data["text"]}</div>', unsafe_allow_html=True)
            
            st.divider()

            # --- [ลำดับที่ 2] 3D Model ---
            if is_premium:
                render_3d_model()
            else:
                st.image("https://images.unsplash.com/photo-1517495306684-21523df7d62c?q=80&w=1000", caption="Reference Outfit (Free Mode)")

            st.divider()

            # --- [ลำดับที่ 3] แหล่งช้อปปิ้งแนะนำ (ปรับสีปุ่มตาม Brand และดึง Keyword) ---
            st.subheader(t["shop_title"])
            
            # CSS สำหรับปุ่มสีแบรนด์
            st.markdown("""
                <style>
                .btn-shopee { background-color: #EE4D2D !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-uniqlo { background-color: #FF0000 !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .btn-lazada { background-color: #00008B !important; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px 2px; }
                .item-card { border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 15px; background-color: rgba(255,255,255,0.05); }
                </style>
            """, unsafe_allow_html=True)

            for item in data["items"]:
                kw = quote_plus(item['name'])
                st.markdown(f"""
                    <div class="item-card">
                        <h4 style="margin-bottom:5px;">🔹 {item['name']}</h4>
                        <p style="font-size: 0.9rem; color: #888; margin-bottom:15px;">{item['reason']}</p>
                        <a href="https://shopee.co.th/search?keyword={kw}" target="_blank" class="btn-shopee">🟠 Shopee</a>
                        <a href="https://www.uniqlo.com/th/th/search/?q={kw}" target="_blank" class="btn-uniqlo">🔴 Uniqlo</a>
                        <a href="https://www.lazada.co.th/catalog/?q={kw}" target="_blank" class="btn-lazada">🔵 Lazada</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 กรุณากรอกข้อมูลและกดปุ่มเริ่มวิเคราะห์เพื่อดูผลลัพธ์และตัวละคร 3D")
