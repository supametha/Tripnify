import streamlit as st
import base64
import re
from openai import OpenAI
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# --- ⚙️ ฟังก์ชันประมวลผล (เน้นความต่างระหว่าง Key vs No Key) ---
def process_logic(api_key, country, activity, gender, travel_days, use_free_mode, uploaded_file):
    # 1. กรณีผู้ใช้พิเศษ (มี OpenAI API Key)
    if api_key and not use_free_mode:
        try:
            client = OpenAI(api_key=api_key)
            analysis_feedback = "ไม่พบรูปภาพสำหรับวิเคราะห์"
            
            # ฟีเจอร์วิเคราะห์รูปชุด (Vision AI)
            if uploaded_file:
                b64_img = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                v_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": f"Analyze if this outfit is suitable for {country} at 1.8°C for {activity}. Give a professional fashion critique and suggest what's missing."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}]
                )
                analysis_feedback = v_resp.choices[0].message.content
            
            # แนะนำการแต่งกายเพิ่มเติม
            r_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"วางแผนการแต่งกาย {travel_days} วัน ใน {country} อากาศ 1.8C กิจกรรม {activity}"}]
            )
            recommendation = r_resp.choices[0].message.content
            
            # สร้างภาพ 3D
            img_resp = client.images.generate(model="dall-e-3", prompt=f"3D character {gender} in {country} stylish winter outfit", n=1)
            return analysis_feedback, recommendation, img_resp.data[0].url

        except Exception as e:
            return f"Error: {str(e)}", "กรุณาเช็ค Key ของคุณ", None

    # 2. กรณีผู้ใช้ทั่วไป (โหมดฟรี)
    else:
        analysis_res = "💡 โหมดฟรี: ระบบประเมินเบื้องต้นว่าควรเน้นเสื้อผ้าที่กักเก็บความร้อน (Thermal Clothes)"
        recommendation = f"แผนพื้นฐานสำหรับ {country}: แนะนำการแต่งกายแบบ Layering System (Base, Mid, Outer layer)"
        sample_img = "https://images.unsplash.com/photo-1520975954732-4cdd221ee434?q=80&w=1000" if gender == "ชาย" else "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1000"
        return analysis_res, recommendation, sample_img

# --- 🎨 หน้า Login (คงเดิมจากเวอร์ชันที่แล้ว) ---
def login_page():
    st.markdown("""<style>.stApp { background-color: #ffffff; } .login-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 450px; margin: auto; } .google-btn { display: flex; align-items: center; justify-content: center; width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 10px; cursor: pointer; margin-bottom: 20px; color: #475569; } .divider { display: flex; align-items: center; margin: 20px 0; color: #cbd5e1; font-size: 12px; } .divider::before, .divider::after { content: ''; flex: 1; border-bottom: 1px solid #f1f5f9; } .divider span { padding: 0 10px; } .stButton>button { width: 100%; background-color: #4f46e5 !important; color: white !important; border-radius: 10px !important; } .footer-link { font-size: 13px; color: #6366f1; text-decoration: none; }</style>""", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="login-box"><h2>Tripnify Login</h2><div class="google-btn"><img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" width="18" style="margin-right:10px;"> ดำเนินการต่อด้วย Google</div><div class="divider"><span>หรือเข้าสู่ระบบด้วยอีเมล</span></div>', unsafe_allow_html=True)
    st.text_input("อีเมล", placeholder="example@email.com")
    st.text_input("รหัสผ่าน", type="password", placeholder="••••••••")
    if st.button("เข้าสู่ระบบ"): st.session_state['logged_in'] = True; st.rerun()
    st.markdown('<div style="margin-top: 25px; display: flex; justify-content: space-between;"><a class="footer-link">สมัครสมาชิกใหม่</a><span style="color: #e2e8f0;">|</span><a class="footer-link" style="color: #64748b;">ทดลองใช้งาน (Guest)</a></div></div>', unsafe_allow_html=True)

# --- 📊 หน้า Dashboard ---
def main_dashboard():
    st.markdown("""<style>.main-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #f1f5f9; margin-bottom: 20px; } .metric-card { background: #f8fafc; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; } .analysis-box { background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fef3c7; color: #92400e; margin-bottom: 20px; } .shop-item { background: white; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; margin-bottom: 15px; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ ตั้งค่า")
        api_key = st.text_input("OpenAI API Key (รับสิทธิวิเคราะห์รูปภาพ)", type="password")
        use_free_mode = st.toggle("ใช้งานโหมดพื้นฐาน (ฟรี)", value=not api_key)
        st.divider()
        if st.button("ออกจากระบบ"): st.session_state['logged_in'] = False; st.rerun()

    st.title("🌍 Tripnify Dashboard")
    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🗓️ ข้อมูลการเดินทาง")
        country = st.selectbox("จุดหมาย", ["South Korea", "Japan", "Thailand", "Vietnam", "Taiwan"])
        d_col1, d_col2 = st.columns(2)
        start_date = d_col1.date_input("วันไป", datetime.now())
        end_date = d_col2.date_input("วันกลับ", datetime.now() + timedelta(days=5))
        activity = st.selectbox("กิจกรรม", ["ท่องเที่ยวพักผ่อน", "ติดต่อธุรกิจ", "ผจญภัย", "ถ่ายรูป/Fashion"])
        gender = st.radio("เพศ", ["ชาย", "หญิง"])
        img_file = st.file_uploader("📸 อัปโหลดรูปชุดของคุณ (เพื่อให้ AI วิเคราะห์)", type=['jpg', 'png'])
        run_btn = st.button("✨ เริ่มวิเคราะห์แผนการแต่งกาย")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if run_btn:
            v_out, r_out, img_url = process_logic(api_key, country, activity, gender, (end_date-start_date).days, use_free_mode, img_file)
            
            # --- ส่วนที่ 1: สรุปข้อมูลพื้นฐาน ---
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metric-card"><small>จุดหมาย</small><br><b>{country}</b></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><small>อากาศ</small><br><b>1.8°C</b></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card"><small>สถานะ</small><br><b style="color:#10b981;">{"Premium AI" if api_key else "Free Mode"}</b></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # --- ส่วนที่ 2: วิเคราะห์รูปชุด (เฉพาะผู้ใช้มี Key) ---
            st.markdown("### 🔍 ผลการวิเคราะห์ชุดของคุณ")
            st.markdown(f'<div class="analysis-box"><b>AI Critique:</b><br>{v_out}</div>', unsafe_allow_html=True)
            
            # --- ส่วนที่ 3: แผนการแต่งกาย ---
            st.markdown("### 🎭 แผนการแต่งกายที่แนะนำ")
            if img_url: st.image(img_url, use_container_width=True)
            st.success(f"**คำแนะนำเพิ่มเติม:** {r_out}")
            
            st.divider()

            # --- ส่วนที่ 4: แหล่งช้อปปิ้ง (แยกส่วนชัดเจน) ---
            st.markdown("### 🛍️ แหล่งช้อปปิ้งและไอเทมแนะนำ")
            shop_items = [
                {"item": "เสื้อโค้ทกันหนาว (Down Jacket)", "desc": "สำหรับอากาศ 1.8°C"},
                {"item": "ชุดลองจอน (Heattech)", "desc": "ชั้นในเก็บความร้อน"},
                {"item": "ถุงเท้าและรองเท้าบูท", "desc": "เน้นกันลื่นและอุ่น"},
                {"item": "อุปกรณ์เสริม (หมวก/ถุงมือ)", "desc": "ป้องกันลมหนาว"},
                {"item": "แผ่นแปะความร้อน (Hot Pack)", "desc": "ตัวช่วยสำคัญ"}
            ]
            for s in shop_items:
                st.markdown(f"""<div class="shop-item"><strong>🔹 {s['item']}</strong><br><small>{s['desc']}</small><br><br><a href='https://shopee.co.th/search?keyword={quote_plus(s['item'])}' target='_blank' style='text-decoration:none; color:#4f46e5;'>🛒 Shopee</a> | <a href='https://www.lazada.co.th/catalog/?q={quote_plus(s['item'])}' target='_blank' style='text-decoration:none; color:#4f46e5; margin-left:10px;'>🛒 Lazada</a></div>""", unsafe_allow_html=True)
        else:
            st.info("👈 กรอกข้อมูลเพื่อเริ่มต้นการวิเคราะห์")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if st.session_state['logged_in']: main_dashboard()
else: login_page()
