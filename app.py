import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ================= 1. ตั้งค่าหน้าจอ =================
st.set_page_config(page_title="Kickless Cable Data", layout="centered")

CSV_FILE = 'kickless_data.csv'

# ================= 2. ฟังก์ชันจัดการข้อมูล =================
def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Cable_Name", "Last_Changed_Date"])
    return pd.read_csv(CSV_FILE, encoding='utf-8-sig')

def save_data(df):
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

df = load_data()

# ================= 3. ตกแต่งสีและฟอนต์ตามดีไซน์เดิมของคุณ =================
st.markdown("""
<style>
    /* หัวข้อสีฟ้าสว่าง #00e5ff */
    .main-title {
        text-align: center;
        color: #00e5ff;
        font-size: 45px;
        font-weight: bold;
        font-family: Tahoma, sans-serif;
        margin-bottom: 20px;
    }
    /* หัวข้อย่อยสีขาว */
    .sub-title {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    /* วันที่เปลี่ยนล่าสุดสีแดง #ff1111 */
    .date-red {
        text-align: center;
        color: #ff1111;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    /* วันที่ควรเปลี่ยนสีเหลืองทอง #fecc37 */
    .date-yellow {
        text-align: center;
        color: #fecc37;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ================= 4. ส่วนแสดงผลบนแอป =================

# หัวแอป
st.markdown('<div class="main-title">Kickless Cable Data</div>', unsafe_allow_html=True)

# ใช้ระบบ Tab เพื่อความสะอาดตาและกดง่าย
tab1, tab2 = st.tabs(["🔍 ค้นหาข้อมูลล่าสุด", "📝 จัดการลงข้อมูล/อัพเดท"])

# ----------------- แท็บ 1: ค้นหาข้อมูล -----------------
with tab1:
    st.markdown("#### เลือกรหัสสาย Kickless (พิมพ์ค้นหาได้):")
    cable_list = df['Cable_Name'].unique().tolist()
    
    selected_cable = st.selectbox("รายชื่อสาย:", ["-- กรุณาเลือกสาย --"] + cable_list, label_visibility="collapsed")
    
    # ปุ่มค้นหาสีฟ้า
    if st.button("ค้นหาข้อมูลล่าสุด", type="primary", use_container_width=True):
        if selected_cable == "-- กรุณาเลือกสาย --":
            st.warning("กรุณาเลือกสายก่อนกดค้นหา")
        else:
            # คำนวณวันที่
            cable_data = df[df['Cable_Name'] == selected_cable]
            latest = cable_data.sort_values(by="Last_Changed_Date", ascending=False).iloc[0]
            last_date_str = latest["Last_Changed_Date"]
            
            try:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
                next_date = last_date + timedelta(days=180)
                next_date_str = next_date.strftime("%Y-%m-%d %H:%M:%S")
            except:
                next_date_str = "รูปแบบวันที่ไม่ถูกต้อง"
            
            st.divider()
            
            # โชว์ข้อมูลสีแดงและสีเหลืองตามที่คุณออกแบบไว้เป๊ะๆ
            st.markdown('<div class="sub-title">วันที่เปลี่ยนสายล่าสุด:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="date-red">{last_date_str}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="sub-title">วันที่ควรเปลี่ยนสาย (กำหนดอายุ 180 วัน):</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="date-yellow">{next_date_str}</div>', unsafe_allow_html=True)
            
            # กราฟแท่ง (ค่า 0 และ 1)
            st.divider()
            st.markdown('<div class="sub-title">แผนภูมิการเปลี่ยนสาย (รายเดือน)</div>', unsafe_allow_html=True)
            
            history = df[df['Cable_Name'] == selected_cable].copy()
            history['Month'] = pd.to_datetime(history['Last_Changed_Date']).dt.month
            months_th = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
            
            chart_data = pd.DataFrame({'เดือน': months_th, 'เปลี่ยนสาย': 0})
            for m in history['Month'].unique():
                chart_data.loc[m-1, 'เปลี่ยนสาย'] = 1
                
            # วาดกราฟเส้นสีฟ้าแบบที่คุณชอบ
            st.bar_chart(chart_data.set_index('เดือน'), color="#00e5ff")

# ----------------- แท็บ 2: ฟอร์มจัดการข้อมูล -----------------
with tab2:
    action = st.radio("เลือกรูปแบบการทำงาน:", ["อัพเดทสายเดิม", "ลงข้อมูลสายเส้นใหม่"], horizontal=True)
    
    with st.form("manage_form"):
        if action == "ลงข้อมูลสายเส้นใหม่":
            cable_name = st.text_input("ชื่อ/รหัส สาย Kickless เส้นใหม่:")
        else:
            if df.empty:
                cable_name = st.selectbox("เลือกสายที่ต้องการอัพเดท:", ["(ยังไม่มีข้อมูลในระบบ)"])
            else:
                cable_name = st.selectbox("เลือกชื่อสายเดิมที่ต้องการอัพเดท:", df['Cable_Name'].unique().tolist())
        
        st.markdown("**วันที่และเวลาที่เปลี่ยนสาย:**")
        col1, col2 = st.columns(2)
        new_date = col1.date_input("วันที่ (YYYY-MM-DD)")
        new_time = col2.time_input("เวลา (HH:MM)")
        
        # ปุ่มกดบันทึกข้อมูล (นำ st.rerun ออกแล้ว ไม่มีแจ้งเตือนกวนใจ)
        submit = st.form_submit_button("💾 บันทึกข้อมูลลงฐานระบบ", use_container_width=True)
        
        if submit:
            if not cable_name or cable_name == "(ยังไม่มีข้อมูลในระบบ)":
                st.error("กรุณากรอก/เลือกชื่อสาย Kickless!")
            else:
                dt_str = f"{new_date} {new_time.strftime('%H:%M:%S')}"
                new_row = pd.DataFrame([{"Cable_Name": cable_name.strip(), "Last_Changed_Date": dt_str}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                
                st.success(f"บันทึกข้อมูลสาย {cable_name} เรียบร้อยแล้ว! (สลับไปแท็บค้นหาเพื่อดูข้อมูลอัปเดตได้เลย)")
