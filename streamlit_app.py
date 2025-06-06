import streamlit as st
import pandas as pd
import re
from io import BytesIO

# ------------------------
# 1. CHUẨN HÓA HỌ TÊN
# ------------------------
def normalize_name(name):
    if pd.isna(name):
        return ""
    return " ".join(str(name).strip().title().split())

# ------------------------
# 2. CHUẨN HÓA SỐ ĐIỆN THOẠI
# ------------------------
def normalize_phone(phone):
    if pd.isna(phone):
        return ""
    phone = re.sub(r"[^\d]", "", str(phone))  # Loại ký tự không phải số
    if phone.startswith("84"):
        phone = "0" + phone[2:]
    elif phone.startswith("+84"):
        phone = "0" + phone[3:]
    elif len(phone) == 9 and not phone.startswith("0"):
        phone = "0" + phone
    return phone if len(phone) == 10 and phone.startswith("0") else ""

# ------------------------
# 3. CHUẨN HÓA EMAIL
# ------------------------
def is_valid_email(email):
    if pd.isna(email):
        return False
    email = str(email).strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def normalize_email(email):
    email = str(email).strip().lower()
    return email if is_valid_email(email) else ""

# ------------------------
# 4. LOẠI TRÙNG VỚI DATA TỔNG
# ------------------------
def remove_duplicates(df_new, df_total):
    phones_total = df_total['SĐT'].astype(str).dropna().apply(normalize_phone).unique()
    emails_total = df_total['Email'].astype(str).dropna().apply(normalize_email).unique()

    def is_duplicate(row):
        phone = normalize_phone(row['Phone'])
        email = normalize_email(row['Email'])
        return (phone in phones_total) or (email and email in emails_total)

    df_filtered = df_new[~df_new.apply(is_duplicate, axis=1)].copy()
    return df_filtered

# ------------------------
# 5. CHIA ĐỀU TV - CS
# ------------------------
def assign_staff(df, tv_list, cs_list):
    tv_len = len(tv_list)
    cs_len = len(cs_list)
    df = df.reset_index(drop=True)
    df["TV"] = [tv_list[i % tv_len] for i in range(len(df))] if tv_len else ""
    df["CS"] = [cs_list[i % cs_len] for i in range(len(df))] if cs_len else ""
    return df

# ------------------------
# 6. TẢI FILE DƯỚI DẠNG EXCEL
# ------------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Processed Data')
    processed_data = output.getvalue()
    return processed_data

# ------------------------
# 7. GIAO DIỆN STREAMLIT
# ------------------------
st.set_page_config(page_title="Data MRT Processor", layout="wide")
st.title("📊 Ứng dụng Xử lý Dữ liệu MRT")

st.markdown("""
### 📝 Hướng dẫn:
1. **Tải lên** file dữ liệu mới (`Data_MRT.xlsx`) và file dữ liệu tổng (`DATA_TONG.xlsx`).
2. **Nhập** danh sách tên nhân viên TV và CS, cách nhau bởi dấu phẩy.
3. **Nhấn nút** "Xử lý dữ liệu" để bắt đầu quá trình xử lý.
4. **Tải xuống** file kết quả sau khi xử lý.
""")

# Tải lên file dữ liệu mới
uploaded_new_file = st.file_uploader("📤 Tải lên file dữ liệu mới (Data_MRT.xlsx)", type=["xlsx"], key="new_file")

# Tải lên file dữ liệu tổng
uploaded_total_file = st.file_uploader("📤 Tải lên file dữ liệu tổng (DATA_TONG.xlsx)", type=["xlsx"], key="total_file")

# Nhập danh sách nhân viên TV và CS
tv_input = st.text_input("👥 Nhập danh sách nhân viên TV (cách nhau bởi dấu phẩy):", "")
cs_input = st.text_input("👥 Nhập danh sách nhân viên CS (cách nhau bởi dấu phẩy):", "")

# Nút xử lý dữ liệu
if st.button("🚀 Xử lý dữ liệu"):
    if uploaded_new_file is None:
        st.warning("Vui lòng tải lên file dữ liệu mới.")
    elif uploaded_total_file is None:
        st.warning("Vui lòng tải lên file dữ liệu tổng.")
    else:
        # Đọc dữ liệu từ các file Excel
        df_new = pd.read_excel(uploaded_new_file)
        df_total = pd.read_excel(uploaded_total_file)

        # Chuẩn hóa dữ liệu mới
        df_new['User'] = df_new['User'].apply(normalize_name)
        df_new['Phone'] = df_new['Phone'].apply(normalize_phone)
        df_new['Email'] = df_new['Email'].apply(normalize_email)

        # Loại bỏ các dòng trùng lặp
        df_filtered = remove_duplicates(df_new, df_total)

        # Phân chia nhân viên TV và CS
        tv_list = [name.strip() for name in tv_input.split(',') if name.strip()]
        cs_list = [name.strip() for name in cs_input.split(',') if name.strip()]
        df_assigned = assign_staff(df_filtered, tv_list, cs_list)

        # Hiển thị dữ liệu đã xử lý
        st.success(f"✅ Đã xử lý {len(df_assigned)} dòng dữ liệu sau khi loại bỏ trùng lặp và phân chia nhân viên.")
        st.dataframe(df_assigned)

        # Tải xuống file kết quả
        processed_file = to_excel(df_assigned)
        st.download_button(
            label="📥 Tải xuống file kết quả",
            data=processed_file,
            file_name="Data_MRT_Processed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
