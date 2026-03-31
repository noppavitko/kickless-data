import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ================= 1. ตั้งค่าหน้าจอและการแสดงผล (Mobile-First) =================
st.set_page_config(page_title="Kawasaki Cable Monitor", page_icon="🔌", layout="centered", initial_sidebar_state="collapsed")

CSV_FILE = 'kickless_data.csv'

# ================= 2. ส่วนตั้งค่าสีและสไตล์ (Custom CSS Hack) =================
# จัดการสีและขอบโค้งของกล่องข้อมูล (Data Cards)
st.markdown("""
<style>
    /* ตั้งค่าฟอนต์หลัก */
    @import url('https://fonts.googleapis.com/css2?family=Tahoma:wght@400;700&display=swap');
    body {
        font-family: 'Tahoma', sans-serif !important;
    }
    /* สไตล์ของหัวข้อ Kickless */
    .st-emotion-cache-12fmwca {
        font-size: 38px !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-align: center;
        margin-top: -10px;
    }
    /* สไตล์ของกล่อง Data Card */
    .data-card {
        border-radius: 12px;
        padding: 20px;
        background-color: #2B2B2B; /* สีพื้นหลังกล่อง */
        border: 1px solid #4A4A4A;
        margin-bottom: 20px;
    }
    .data-card-green {
        background-color: #28A745; /* สีพื้นหลังกล่องสีเขียว */
        border-color: #28A745;
    }
    .card-title {
        color: #A0A0A0; /* สีตัวหนังสือหัวข้อในกล่อง */
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 5px;
    }
    .card-value {
        color: #FFFFFF; /* สีตัวหนังสือข้อมูลในกล่อง */
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. ฟังก์ชันจัดการข้อมูล (ห้ามแก้!) =================
def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Cable_Name", "Last_Changed_Date"])
    return pd.read_csv(CSV_FILE, encoding='utf-8-sig')

def save_data(df):
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

# ================= 4. ระบบจัดการการสลับหน้า (Page State) =================
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# ฟังก์ชันสำหรับเปลี่ยนหน้า
def change_page(page_name):
    st.session_state.page = page_name
    st.rerun()

df = load_data()

# ================= 5. ส่วนหัวโปรแกรม (Header Section) =================
# ใช้ custom HTML เพื่อคุมขนาดฟอนต์ให้พอดีๆ
st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-size: 32px;'>🔌 Kickless Cable Monitor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0A0A0; margin-top: -15px;'>ระบบมอนิเตอร์อายุการใช้งานสาย Kickless</p>", unsafe_allow_html=True)
st.divider() # เส้นคั่น

# ================= 6. การแสดงผลตามหน้า (Dashboard Page) =================
if st.session_state.page == 'dashboard':
    if df.empty:
        st.markdown("""
        <div style="background-color: #2B2B2B; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #4A4A4A;">
            <p style="color: #FFFFFF; font-size: 16px; margin-bottom: 5px;">ยังไม่มีข้อมูลในระบบ</p>
            <p style="color: #A0A0A0; font-size: 14px;">กรุณาคลิกปุ่ม 'ลงข้อมูลสายใหม่' เพื่อเริ่มใช้งาน</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # กล่องส่วนค้นหา (Search Section)
        st.markdown("#### ค้นหาข้อมูลสาย (พิมพ์เพื่อค้นหาได้)")
        cable_list = df['Cable_Name'].unique().tolist()
        
        # ปรับ Dropdown ให้ใหญ่และจิ้มง่ายขึ้น
        selected_cable = st.selectbox("รายชื่อสาย:", ["-- กรุณาเลือกสาย --"] + cable_list, label_visibility="collapsed")
        
        # ปุ่มกดค้นหาแบบกว้าง (จิ้มง่ายบนมือถือ)
        if st.button("📊 ค้นหาข้อมูลล่าสุด", type="primary", use_container_width=True):
            if selected_cable != "-- กรุณาเลือกสาย --":
                # ดึงข้อมูลมาคำนวณวันหมดอายุ (+180 วัน)
                cable_data = df[df['Cable_Name'] == selected_cable]
                latest = cable_data.sort_values(by="Last_Changed_Date", ascending=False).iloc[0]
                last_date_str = latest["Last_Changed_Date"]
                
                try:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
                    next_date = last_date + timedelta(days=180)
                    next_date_str = next_date.strftime("%Y-%m-%d %H:%M:%S")
                    days_left = (next_date - datetime.now()).days
                except:
                    last_date_str = "รูปแบบวันที่ไม่ถูกต้อง"
                    next_date_str = "ไม่สามารถคำนวณได้"
                    days_left = None
                
                # ================= ส่วนกล่องแสดงผล (Metric Cards Section) =================
                st.markdown("<br>", unsafe_allow_html=True)
                
                # กล่องวันที่เปลี่ยนสายล่าสุด
                st.markdown(f"""
                <div class="data-card">
                    <p class="card-title">วันที่เปลี่ยนสายล่าสุด</p>
                    <p class="card-value">{last_date_str}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # กล่องวันที่ควรเปลี่ยน (กำหนดอายุ 180 วัน) พร้อมสถานะ
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    if days_left is not None:
                        # คำนวณสีตามสถานะวันเหลือ
                        if days_left < 0:
                            status_val = f"{abs(days_left)} วัน"
                            st.metric(label="เลยกำหนดมา", value=status_val, delta_color="inverse")
                        else:
                            status_val = f"{days_left} วัน"
                            st.metric(label="เหลือเวลา", value=status_val, delta_color="normal")
                    else:
                        st.metric(label="วันเหลือ", value="-", delta_color="normal")
                
                with col_right:
                    # ใส่ข้อมูลลงในกล่องสีเขียว Kawasaki
                    st.markdown(f"""
                    <div class="data-card data-card-green">
                        <p class="card-title" style="color: #FFFFFF;">ควรเปลี่ยนสาย (180 วัน)</p>
                        <p class="card-value" style="font-size: 22px;">{next_date_str}</p>
                    </div>
                    """, unsafe_allow_html=True)
                # =========================================================================
            else:
                st.warning("กรุณาเลือกสายก่อนกดค้นหา")

    # ================= ส่วนปุ่มจัดการข้อมูล (Navigation Section) =================
    st.divider()
    
    # วางปุ่มใหญ่ๆ 2 ปุ่มที่ด้านล่างสุด (จิ้มง่ายบนมือถือ)
    st.markdown("#### จัดการฐานข้อมูลสาย")
    
    # ปรับปุ่มให้กว้างและมีระยะห่าง
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("📝 ลงข้อมูลสายใหม่", type="primary", use_container_width=True, on_click=lambda: change_page('form'))
    
    with btn_col2:
        # ใช้สีเขียวสด Kawasaki
        if st.button("อัพเดทสายเดิม", type="secondary", use_container_width=True, on_click=lambda: change_page('update_form')):
            if df.empty:
                st.warning("ยังไม่มีข้อมูลสายในระบบ กรุณาเพิ่มสายใหม่ก่อน")
                change_page('dashboard') # เด้งกลับมาหน้าหลัก
# ================= 7. การแสดงผลตามหน้า (Form Pages) =================
elif st.session_state.page == 'form' or st.session_state.page == 'update_form':
    
    # กำหนดหัวข้อหน้าฟอร์ม
    form_title = "📝 ลงข้อมูลสายใหม่" if st.session_state.page == 'form' else "📝 อัพเดทสายเดิม"
    
    with st.form("data_form"):
        # กล่องชื่อสาย
        st.markdown(f"#### {form_title}")
        
        if st.session_state.page == 'form':
            cable_name_input = st.text_input("ชื่อ/รหัส สาย Kickless เส้นใหม่:")
        else:
            if df.empty:
                cable_name_input = "" # ไม่ให้เลือกถ้าไม่มีข้อมูล
            else:
                cable_name_input = st.selectbox("เลือกชื่อสายเดิมที่ต้องการอัพเดท:", df['Cable_Name'].unique().tolist())
        
        # ส่วนปฏิทินและนาฬิกา (จิ้มง่ายบนมือถือ)
        st.markdown("<br>**วันที่และเวลา:**", unsafe_allow_html=True)
        col_d, col_t = st.columns(2)
        with col_d:
            new_date = st.date_input("วันที่ (YYYY-MM-DD)", label_visibility="collapsed")
        with col_t:
            new_time = st.time_input("เวลา (HH:MM)", label_visibility="collapsed")
            
        # ปุ่มเซฟสีเขียวสด Kawasaki แบบกว้าง
        submit = st.form_submit_button("💾 บันทึกข้อมูล", use_container_width=True)
        
        if submit:
            if not cable_name_input or cable_name_input == "":
                st.error("กรุณากรอก/เลือกชื่อสาย Kickless!")
            else:
                # รวมวันที่และเวลาเข้าด้วยกัน แล้วเซฟลง DataFrame (ห้ามแก้!)
                dt_str = f"{new_date} {new_time.strftime('%H:%M:%S')}"
                new_row = pd.DataFrame([{"Cable_Name": cable_name_input.strip(), "Last_Changed_Date": dt_str}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                
                st.success(f"บันทึกข้อมูลสาย {cable_name_input} เรียบร้อยแล้ว!")
                # ดีเลย์แป๊บเดียวเพื่อให้ user เห็นข้อความแจ้งเตือน แล้วเด้งกลับหน้าหลัก
                st.info("💡 กำลังกลับไปหน้าหลัก...")
                change_page('dashboard') 
                st.rerun() # รีเฟรชหน้าเว็บอัตโนมัติ

    # ================= ปุ่มย้อนกลับ =================
    st.divider()
    # ปุ่มสีเทาแบบกว้าง
    st.button("ย้อนกลับหน้าแรก", type="secondary", use_container_width=True, on_click=lambda: change_page('dashboard'))
