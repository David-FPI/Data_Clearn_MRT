import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components
from datetime import datetime
from io import BytesIO

# ----------------------------
# 🚀 Giao diện Streamlit
# ----------------------------
st.title("🧼 Chuẩn hóa & Thống kê dữ liệu")
# ----------------------------
# 🔧 Các hàm chuẩn hóa
# ----------------------------
def normalize_name(name):
    if pd.isna(name): return ""
    return " ".join(str(name).strip().title().split())


def normalize_phone(phone):
    if pd.isna(phone):
        return ""

    # Bước 1: Làm sạch các ký tự thừa như =, +, khoảng trắng, dấu gạch nối, v.v.
    phone = str(phone).strip()
    phone = phone.replace("=", "").replace("+", "")
    phone = re.sub(r"[^\d]", "", phone)  # Giữ lại chỉ các chữ số

    # Bước 2: Xử lý đầu số quốc tế và loại bỏ số 0 đầu
    if phone.startswith("0084"):
        phone = phone[4:]
    elif phone.startswith("84") and len(phone) > 9:
        phone = phone[2:]
    elif phone.startswith("0"):
        phone = phone[1:]

    # Bước 3: Trả về nếu đủ 9 số
    if len(phone) == 9 and phone.isdigit():
        return phone
    else:
        return ""  # Số không hợp lệ

def normalize_email(email):
    if pd.isna(email): return ""
    email = str(email).strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return email if re.match(pattern, email) else ""

def normalize_date(date):
    try:
        if pd.isna(date): return ""
        parsed = pd.to_datetime(date, errors="coerce")
        if pd.isna(parsed): return ""
        return parsed.strftime("%d/%m/%Y")
    except:
        return ""



uploaded_file = st.file_uploader("📂 Tải file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Đọc sheet tên "DATA" và ép kiểu về chuỗi để xử lý ổn định
        df_full = pd.read_excel(uploaded_file, sheet_name="DATA", header=None, dtype=str)
        df_data = df_full.iloc[1:].reset_index(drop=True)  # Bỏ dòng tiêu đề

        # ----------------------------
        # 🧩 Vị trí cột trong Excel (theo index)
        # ----------------------------
        col_stt = 0
        col_name = 3       # Họ tên KH
        col_phone = 4      # SĐT
        col_email = 6      # Email
        col_date = 8       # Ngày đăng ký

        # ✅ Chuẩn hóa dữ liệu
        df_data[col_name] = df_data[col_name].apply(normalize_name)
        df_data[col_phone] = df_data[col_phone].apply(normalize_phone)
        df_data[col_email] = df_data[col_email].apply(normalize_email)
        df_data[col_date] = df_data[col_date].apply(normalize_date)

        st.success("✅ Dữ liệu đã được chuẩn hóa")
        st.subheader("👁️ Dữ liệu mẫu sau chuẩn hóa:")
        # st.dataframe(df_data[[col_stt, col_name, col_phone, col_email, col_date]].head(10), use_container_width=True)
        st.dataframe(df_data, use_container_width=True)


        # # 📊 Thống kê kết quả
        # total_rows = len(df_data)

        # valid_phones = df_data[df_data[col_phone] != ""]
        # invalid_phones = total_rows - len(valid_phones)

        # valid_emails = df_data[df_data[col_email] != ""]
        # invalid_emails = total_rows - len(valid_emails)

        # st.subheader("📈 Thống kê dữ liệu")
        # st.markdown(f"""
        # 📄 **Tổng số dòng dữ liệu:** {total_rows}

        # 📞 **SĐT hợp lệ duy nhất:** {valid_phones[col_phone].nunique()}

        # ❌ **SĐT lỗi hoặc thiếu:** {invalid_phones} dòng

        # ✉️ **Email hợp lệ duy nhất:** {valid_emails[col_email].nunique()}

        # ❌ **Email lỗi hoặc thiếu:** {invalid_emails} dòng
        # """)

        # st.subheader("👁️ Dữ liệu mẫu sau chuẩn hóa:")
        # st.dataframe(df_data[[col_stt, col_name, col_phone, col_email, col_date]].head(15))
        # ----------------------------
        # 📊 Thống kê
        # ----------------------------
        total_rows = len(df_data)

        valid_phones = df_data[df_data[col_phone] != ""]
        valid_emails = df_data[df_data[col_email] != ""]

        # Trùng SĐT
        duplicate_phones = valid_phones[valid_phones.duplicated(subset=col_phone, keep=False)]
        duplicate_phone_values = duplicate_phones[col_phone].nunique()
        duplicate_phone_rows = len(duplicate_phones)

        # Trùng Email
        duplicate_emails = valid_emails[valid_emails.duplicated(subset=col_email, keep=False)]
        duplicate_email_values = duplicate_emails[col_email].nunique()
        duplicate_email_rows = len(duplicate_emails)

        st.subheader("📈 Thống kê dữ liệu")
        st.markdown(f"""
        📄 **Tổng số dòng dữ liệu:** {total_rows}

        📞 **SĐT hợp lệ và không bị trống:** {valid_phones[col_phone].nunique()}
        - 🔁 Trong đó: **{duplicate_phone_values} số bị trùng** (xuất hiện nhiều hơn 1 lần)
        - 📄 Tổng cộng **{duplicate_phone_rows} dòng** chứa số trùng
        - ✅ **{valid_phones[col_phone].nunique() - duplicate_phone_values} số là duy nhất**

        ✉️ **Email hợp lệ và không bị trống:** {valid_emails[col_email].nunique()}
        - 🔁 Trong đó: **{duplicate_email_values} email bị trùng**
        - 📄 Tổng cộng **{duplicate_email_rows} dòng** chứa email trùng
        - ✅ **{valid_emails[col_email].nunique() - duplicate_email_values} email là duy nhất**
        """)


        # ----------------------------
        # 🔁 Kiểm tra dữ liệu trùng (gộp chung)
        # ----------------------------
        st.subheader("🔁 Kiểm tra dữ liệu trùng")

        # 📞 Trùng SĐT
        duplicate_phone_series = df_data[col_phone].value_counts()
        duplicated_phones = duplicate_phone_series[duplicate_phone_series > 1].index.tolist()
        df_duplicated_phones = df_data[df_data[col_phone].isin(duplicated_phones)][[col_stt, col_name, col_phone, col_email, col_date]]

        st.markdown(f"🔢 **SĐT bị trùng:** {len(duplicated_phones)} số – {len(df_duplicated_phones)} dòng")
        with st.expander("📞 Xem các dòng trùng SĐT"):
            st.dataframe(df_duplicated_phones.sort_values(by=col_phone), use_container_width=True)

        # 📧 Trùng Email
        duplicate_email_series = df_data[col_email].value_counts()
        duplicated_emails = duplicate_email_series[duplicate_email_series > 1].index.tolist()
        df_duplicated_emails = df_data[df_data[col_email].isin(duplicated_emails)][[col_stt, col_name, col_phone, col_email, col_date]]

        st.markdown(f"📨 **Email bị trùng:** {len(duplicated_emails)} email – {len(df_duplicated_emails)} dòng")
        with st.expander("✉️ Xem các dòng trùng Email"):
            st.dataframe(df_duplicated_emails.sort_values(by=col_email), use_container_width=True)

                # ----------------------------
        # 🧹 Xác định & ghi lý do bị xóa rõ ràng kèm dòng STT gốc
        # ----------------------------
        st.subheader("🧹 Xóa dữ liệu trùng & Ghi rõ lý do")

        # Tạo từ điển: giá trị trùng → STT dòng giữ lại (đầu tiên)
        first_phone_map = df_data[~df_data.duplicated(subset=col_phone, keep="first") & (df_data[col_phone] != "")].set_index(col_phone)[col_stt].to_dict()
        first_email_map = df_data[~df_data.duplicated(subset=col_email, keep="first") & (df_data[col_email] != "")].set_index(col_email)[col_stt].to_dict()

        # Ghi lý do xóa cho từng dòng
        removal_reason = []
        for idx, row in df_data.iterrows():
            phone = row[col_phone]
            email = row[col_email]
            stt = row[col_stt]

            phone_dup = df_data.duplicated(subset=col_phone, keep="first")[idx] and phone != ""
            email_dup = df_data.duplicated(subset=col_email, keep="first")[idx] and email != ""

            reason = ""
            if phone_dup and email_dup:
                reason = f"Trùng SĐT với dòng {first_phone_map.get(phone)} & Trùng Email với dòng {first_email_map.get(email)}"
            elif phone_dup:
                reason = f"Trùng SĐT với dòng {first_phone_map.get(phone)}"
            elif email_dup:
                reason = f"Trùng Email với dòng {first_email_map.get(email)}"
            
            removal_reason.append(reason)

        df_data["🔍 Lý do xóa"] = removal_reason

        # Phân tách
        df_removed = df_data[df_data["🔍 Lý do xóa"] != ""].copy()
        df_cleaned = df_data[df_data["🔍 Lý do xóa"] == ""].drop(columns=["🔍 Lý do xóa"]).reset_index(drop=True)

        # Thống kê
        st.success(f"🧹 Đã lọc {len(df_removed)} dòng bị trùng.")

        # Hiển thị bảng các dòng đã bị loại bỏ
        with st.expander("🗑️ Xem các dòng đã bị xóa (vì trùng)"):
            st.dataframe(df_removed[[col_stt, col_name, col_phone, col_email, col_date, "🔍 Lý do xóa"]], use_container_width=True)

        @st.cache_data
        def to_excel_bytes(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Da_Xoa", index=False)
            return output.getvalue()

        # Tải dòng đã xóa
        st.download_button(
            label="📥 Tải các dòng đã xóa (có lý do)",
            data=to_excel_bytes(df_removed),
            file_name="dong_bi_xoa_vi_trung_co_ly_do.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


        # ----------------------------
        # 📤 Hiển thị & Tải dữ liệu sau khi lọc
        # ----------------------------
        st.subheader("📄 Dữ liệu sau khi đã lọc trùng (Sạch):")

        # 👉 Bộ lọc theo ngày đăng ký
        df_cleaned[col_date] = pd.to_datetime(df_cleaned[col_date], format="%d/%m/%Y", errors="coerce")

        min_date = df_cleaned[col_date].min()
        max_date = df_cleaned[col_date].max()

        if pd.isna(min_date) or pd.isna(max_date):
            st.warning("⚠️ Không thể lọc theo ngày vì dữ liệu ngày không đầy đủ.")
            df_filtered = df_cleaned
        else:
            start_date, end_date = st.date_input("📅 Chọn khoảng ngày đăng ký", [min_date, max_date])
            st.markdown(f"🗓️ Bạn đã chọn: **{start_date.strftime('%d/%m/%Y')} – {end_date.strftime('%d/%m/%Y')}**")
            df_filtered = df_cleaned[(df_cleaned[col_date] >= pd.to_datetime(start_date)) & 
                                    (df_cleaned[col_date] <= pd.to_datetime(end_date))]

        # ✅ Hiển thị preview
        df_display = df_filtered.copy()
        df_display[col_date] = df_display[col_date].dt.strftime("%d/%m/%Y")
        st.dataframe(df_display[[col_stt, col_name, col_phone, col_email, col_date]], use_container_width=True)



        # 👉 Tải dữ liệu sạch (đã lọc theo ngày nếu có)
        st.download_button(
            label="📁 Tải dữ liệu sau khi lọc và filter",
            data=to_excel_bytes(df_filtered),
            file_name="du_lieu_sach.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
                # Tải dữ liệu sạch
        st.download_button(
            label="📁 Tải tất cả dữ liệu",
            data=to_excel_bytes( df_cleaned),
            file_name="du_lieu_sach.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # # Tải dữ liệu sạch
        # st.download_button(
        #     label="📁 Tải dữ liệu sau khi lọc",
        #     data=to_excel_bytes( df_cleaned),
        #     file_name="du_lieu_sach.xlsx",
        #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )


    

    
    except Exception as e:
        st.error(f"❌ Lỗi khi xử lý file: {e}")



