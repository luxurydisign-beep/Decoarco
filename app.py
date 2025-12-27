import streamlit as st
from PIL import Image
import io
import zipfile

# تنظیمات کلی صفحه
st.set_page_config(page_title="ویرایشگر همه‌کاره تصاویر", layout="wide")

# ایجاد سه زبانه برای ابزارهای مختلف
tab1, tab2, tab3 = st.tabs(["🖼️ افزودن لوگو", "📏 ابعاد ثابت (1024)", "📉 تغییر حجم و سایز دلخواه"])

# ---------------------------------------------------------
# زبانه اول: افزودن لوگو
# ---------------------------------------------------------
with tab1:
    st.header("افزودن لوگو به تصاویر")
    main_files = st.file_uploader("عکس‌های اصلی:", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="logo_m")
    logo_file = st.file_uploader("فایل لوگو:", type=['png', 'jpg'], key="logo_f")
    
    if main_files and logo_file:
        col1, col2 = st.columns(2)
        opacity = col1.slider("شفافیت لوگو:", 0, 100, 100, key="op1")
        size_per = col2.slider("اندازه لوگو (%):", 1, 100, 20, key="sz1")
        
        if st.button("اجرای عملیات لوگو", key="btn1"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
                logo_img = Image.open(logo_file).convert("RGBA")
                for f in main_files:
                    img = Image.open(f).convert("RGBA")
                    lw = int(img.width * (size_per / 100))
                    lh = int(logo_img.height * (lw / logo_img.width))
                    lr = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
                    if opacity < 100:
                        alpha = lr.split()[3].point(lambda p: p * (opacity / 100))
                        lr.putalpha(alpha)
                    img.paste(lr, (img.width - lw - 10, img.height - lh - 10), lr)
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=90)
                    zf.writestr(f"logo_{f.name}", buf.getvalue())
            st.success("انجام شد!")
            st.download_button("📥 دانلود ZIP", zip_buffer.getvalue(), "watermarked.zip")

# ---------------------------------------------------------
# زبانه دوم: ابعاد ثابت (درخواستی امروز)
# ---------------------------------------------------------
with tab2:
    st.header("تغییر سایز به ابعاد استاندارد")
    size_choice = st.radio("انتخاب ابعاد:", ["مربع (1024x1024)", "افقی (1024x768)", "عمودی (768x1024)"], key="rad2")
    if "مربع" in size_choice: tw, th = 1024, 1024
    elif "افقی" in size_choice: tw, th = 1024, 768
    else: tw, th = 768, 1024

    res_files = st.file_uploader("آپلود عکس‌ها:", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="fl2")
    if res_files and st.button("تغییر ابعاد همگانی", key="btn2"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
            for f in res_files:
                img = Image.open(f).convert("RGB")
                resized = img.resize((tw, th), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                resized.save(buf, format="JPEG", quality=90)
                zf.writestr(f"resized_{f.name}", buf.getvalue())
        st.download_button("📥 دانلود ZIP", zip_buffer.getvalue(), "resized.zip")

# ---------------------------------------------------------
# زبانه سوم: تغییر حجم و سایز دلخواه (برنامه قبلی)
# ---------------------------------------------------------
with tab3:
    st.header("کاهش حجم و تغییر سایز دلخواه")
    opt_files = st.file_uploader("آپلود عکس‌ها:", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="fl3")
    
    if opt_files:
        col_a, col_b = st.columns(2)
        quality_val = col_a.slider("کیفیت (برای کاهش حجم):", 10, 100, 70, key="q3")
        scale_val = col_b.slider("مقیاس تصویر (درصد):", 10, 100, 100, key="sc3")
        
        if st.button("بهینه‌سازی حجم", key="btn3"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
                for f in opt_files:
                    img = Image.open(f).convert("RGB")
                    # محاسبه سایز بر اساس درصد
                    nw = int(img.width * (scale_val / 100))
                    nh = int(img.height * (scale_val / 100))
                    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=quality_val)
                    zf.writestr(f"optimized_{f.name}", buf.getvalue())
            st.success("بهینه‌سازی انجام شد!")
            st.download_button("📥 دانلود ZIP", zip_buffer.getvalue(), "optimized.zip")
