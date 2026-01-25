with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, (end_date-start_date).days, use_free_mode, img_file, lang)
            
            # --- ส่วนที่ 1: AI Critique (แสดงผลวิเคราะห์รูปที่อัปโหลด) ---
            st.markdown("### 🔍 AI Critique & Analysis")
            st.markdown(f'<div class="analysis-box">{v_out}</div>', unsafe_allow_html=True)
            st.divider()

            # --- ส่วนที่ 2: รูป 3D (สอดคล้องกับวิเคราะห์) ---
            st.markdown("### 🎭 Outfit Visual")
            if img_url: 
                st.image(img_url, caption="ภาพจำลองชุดที่แนะนำตามผลวิเคราะห์", use_container_width=True)
            
            # --- ส่วนที่ 3: คำแนะนำประเภทชุด (ไม่มีชื่อวัน) ---
            st.markdown("### 📋 ชุดที่ควรเตรียมเพิ่มเติม")
            st.info(r_out)
            st.divider()

            # --- ส่วนที่ 4: แหล่งช้อปปิ้งและไอเทมแนะนำ (แยกตาม 5 ส่วนหลัก) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งและไอเทมแนะนำ")
            st.write("เลือกซื้อไอเทมที่ AI แนะนำให้ปรับปรุงหรือเพิ่มเติม:")
            
            # กำหนดหัวข้อสินค้า 5 ส่วนหลักที่อ้างอิงจากการวิเคราะห์
            shop_categories = [
                {"name": "เสื้อผ้าชั้นนอก (Coats/Jackets)", "icon": "🧥"},
                {"name": "กางเกง (Pants/Leggings)", "icon": "👖"},
                {"name": "หมวกและผ้าพันคอ (Headwear)", "icon": "🧣"},
                {"name": "รองเท้า (Footwear/Boots)", "icon": "🥾"},
                {"name": "อุปกรณ์เสริม (Accessories/Gloves)", "icon": "🧤"}
            ]

            for cat in shop_categories:
                st.markdown(f"""
                    <div class="shop-item">
                        <strong>{cat['icon']} {cat['name']}</strong><br>
                        <div style="margin-top: 8px;">
                            <a href='https://shopee.co.th/search?keyword={quote_plus(cat['name'])}' target='_blank' style='text-decoration:none; color:#4f46e5; font-size:14px;'>🛒 Shopee</a> | 
                            <a href='https://www.lazada.co.th/catalog/?q={quote_plus(cat['name'])}' target='_blank' style='text-decoration:none; color:#4f46e5; font-size:14px; margin-left:10px;'>🛒 Lazada</a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
