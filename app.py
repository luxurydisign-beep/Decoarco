import streamlit as st
from PIL import Image
import io
import zipfile

st.title("📷 پردازشگر تصویر حرفه‌ای (نسخه ابری)")

# تنظیمات در منوی کناری
st.sidebar.header("تنظیمات")
target_format = st.sidebar.selectbox("فرمت مقصد", ["JPG", "PNG", "WebP"])
quality_val = st.sidebar.slider("کیفیت خروجی", 10, 100, 85)
resize_factor = st.sidebar.slider("تغییر سایز (ضریب)", 0.1, 1.0, 1.0)

uploaded_files = st.file_uploader("عکس‌های خود را انتخاب کنید", accept_multiple_files=True)

if uploaded_files:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
            
            # تغییر سایز
            if resize_factor < 1.0:
                new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # تبدیل فرمت
            img_io = io.BytesIO()
            if target_format == "JPG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            img.save(img_io, format=target_format, quality=quality_val)
            
            # اضافه کردن به فایل زیپ برای دانلود یکجا
            filename = uploaded_file.name.rsplit('.', 1)[0] + f".{target_format.lower()}"
            zip_file.writestr(filename, img_io.getvalue())

    st.success(f"{len(uploaded_files)} عکس با موفقیت پردازش شد.")
    st.download_button(
        label="📥 دانلود همه عکس‌ها بصورت یکجا (ZIP)",
        data=buf.getvalue(),
        file_name="processed_images.zip",
        mime="application/zip"
    )
