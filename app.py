import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ================= ตั้งค่าหน้าจอเว็บ/มือถือ =================
st.set_page_config(page_title="Kickless Cable Data", layout="centered", initial_sidebar_state="collapsed")

CSV_FILE = 'kickless_data.csv'

# ================= ฟังก์ชันจัดการฐานข้อมูล =================
def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Cable_Name", "Last_Changed_Date"])
    return pd.read_csv(CSV_FILE, encoding='utf-8-sig')

def save_data(df):
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

df = load_data()

# ================= ส่วนหัวโปรแกรม (ใช้สีเดียวกับที่คุณตั้งไว้) =================
st.markdown("<h1 style='text-align: center; color: #00e5ff;'>Kickless Cable Data</h1>", unsafe_allow_html=True)
st.write("---")

# สร้างเมนูแบบ Tab สำหรับกดสลับหน้าบนมือถือ
tab_search, tab_manage = st.tabs(["🔍 ค้นหาข้อมูลล่าสุด", "📝 ลงข้อมูล / อัพเดทสาย"])

# ================= หน้า 1: ค้นหาข้อมูล =================
with tab_search:
    st.markdown("#### เลือกรหัสสาย Kickless (พิมพ์ค้นหาได้)")
    
    if df.empty:
        st.info("ไม่มีข้อมูลในระบบ กรุณาไปที่แท็บ 'ลงข้อมูล'")
    else:
        # ดึงรายชื่อสายที่ไม่ซ้ำกันมาใส่ Dropdown
        cable_list = df['Cable_Name'].unique().tolist()
        selected_cable = st.selectbox("รายชื่อสาย:", ["-- กรุณาเลือกสาย --"] + cable_list, label_visibility="collapsed")
        
        # ปุ่มกดค้นหา
        if st.button("ค้นหาข้อมูลล่าสุด", type="primary", use_container_width=True):
            if selected_cable == "-- กรุณาเลือกสาย --":
                st.warning("กรุณาเลือกสายก่อนกดค้นหา")
            else:
                # ดึงข้อมูลสายเส้นที่เลือก และหาอันที่ใหม่ที่สุด
                cable_data = df[df['Cable_Name'] == selected_cable]
                latest = cable_data.sort_values(by="Last_Changed_Date", ascending=False).iloc[0]
                last_date_str = latest["Last_Changed_Date"]
                
                # คำนวณวันที่ควรเปลี่ยน (+180 วัน)
                try:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
                    next_date = last_date + timedelta(days=180)
                    next_date_str = next_date.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    next_date_str = "รูปแบบวันที่ไม่ถูกต้อง"

                # กล่องแสดงผลลัพธ์ (ดึงสีที่คุณตั้งค่าไว้มาใช้)
                st.markdown("<br><h5>วันที่เปลี่ยนสายล่าสุด:</h5>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='color: #ff1111; text-align: center;'>{last_date_str}</h2>", unsafe_allow_html=True)
                
                st.markdown("<h5>วันที่ควรเปลี่ยนสาย (กำหนดอายุ 180 วัน):</h5>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='color: #fecc37; text-align: center;'>{next_date_str}</h2>", unsafe_allow_html=True)

# ================= หน้า 2: ลงข้อมูลและอัพเดท =================
with tab_manage:
    # สลับโหมดการทำงาน
    action = st.radio("เลือกการทำงาน:", ["ลงข้อมูลสายใหม่", "อัพเดทสายเดิม"], horizontal=True)
    
    with st.form("data_form"):
        # กล่องชื่อสาย
        if action == "ลงข้อมูลสายใหม่":
            cable_name = st.text_input("ชื่อสาย Kickless เส้นใหม่:")
        else:
            if df.empty:
                st.warning("ยังไม่มีข้อมูลสายในระบบให้เลือกอัพเดท")
                cable_name = ""
            else:
                cable_name = st.selectbox("เลือกชื่อสายเดิมที่ต้องการอัพเดท:", df['Cable_Name'].unique().tolist())
        
        st.markdown("**วันที่และเวลา:**")
        # กล่องปฏิทินและนาฬิกา (จิ้มง่ายบนมือถือ)
        col1, col2 = st.columns(2)
        new_date = col1.date_input("วันที่ (YYYY-MM-DD)")
        new_time = col2.time_input("เวลา (HH:MM)")
        
        # ปุ่มเซฟ
        submit = st.form_submit_button("บันทึกข้อมูล", use_container_width=True)
        
        if submit:
            if not cable_name:
                st.error("กรุณากรอก/เลือกชื่อสาย Kickless!")
            else:
                # รวมวันที่และเวลาเข้าด้วยกัน แล้วเซฟลง DataFrame
                dt_str = f"{new_date} {new_time.strftime('%H:%M:%S')}"
                new_row = pd.DataFrame([{"Cable_Name": cable_name.strip(), "Last_Changed_Date": dt_str}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                
                st.success(f"บันทึกข้อมูลสาย {cable_name} เรียบร้อยแล้ว!")
                st.info("💡 ข้อมูลถูกอัปเดตแล้ว กรุณาสลับไปแท็บ 'ค้นหาข้อมูลล่าสุด' เพื่อดูผลลัพธ์")