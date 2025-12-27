import streamlit as st
from PIL import Image
import io
import zipfile

# تنظیمات صفحه
st.set_page_config(page_title="ابزار جامع تصاویر", layout="wide")

# ایجاد ۴ زبانه
tabs = st.tabs(["🖼️ لوگو", "📏 ابعاد ثابت", "📉 حجم و سایز", "🔄 تبدیل فرمت"])

# --- زبانه ۱: لوگو (با قابلیت انتخاب مکان) ---
with tabs[0]:
    st.header("افزودن لوگو")
    up_m = st.file_uploader("عکس اصلی:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u1")
    up_l = st.file_uploader("لوگو:", type=['png','jpg'], key="u2")
    
    if up_m and up_l:
        col1, col2 = st.columns(2)
        sl_op = col1.slider("شفافیت لوگو:", 0, 100, 100, key="s1")
        sl_sz = col2.slider("اندازه لوگو (%):", 1, 100, 20, key="s2")
        
        # گزینه انتخاب مکان لوگو
        pos_choice = st.radio(
            "مکان قرارگیری لوگو:",
            ["راست-پایین", "چپ-پایین", "راست-بالا", "چپ-بالا", "وسط"],
            horizontal=True,
            key="p1"
        )

        if st.button("اجرای لوگو", key="b1"):
            z_buf = io.BytesIO()
            with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                logo = Image.open(up_l).convert("RGBA")
                for f in up_m:
                    img = Image.open(f).convert("RGBA")
                    
                    # محاسبه اندازه لوگو
                    lw = int(img.width * (sl_sz / 100))
                    lh = int(logo.height * (lw / logo.width))
                    lr = logo.resize((lw, lh), Image.Resampling.LANCZOS)
                    
                    # تنظیم شفافیت
                    if sl_op < 100:
                        r, g, b, a = lr.split()
                        a = a.point(lambda p: p * (sl_op / 100))
                        lr = Image.merge('RGBA', (r, g, b, a))
                    
                    # محاسبه مختصات بر اساس انتخاب کاربر
                    padding = 10
                    if pos_choice == "راست-پایین":
                        coords = (img.width - lw - padding, img.height - lh - padding)
                    elif pos_choice == "چپ-پایین":
                        coords = (padding, img.height - lh - padding)
                    elif pos_choice == "راست-بالا":
                        coords = (img.width - lw - padding, padding)
                    elif pos_choice == "چپ-بالا":
                        coords = (padding, padding)
                    else:  # وسط
                        coords = ((img.width - lw) // 2, (img.height - lh) // 2)
                    
                    # چسباندن لوگو
                    img.paste(lr, coords, lr)
                    
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=90)
                    zf.writestr(f"logo_{f.name}", buf.getvalue())
            
            st.success("لوگو با موفقیت روی تمامی عکس‌ها قرار گرفت.")
            st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "logo_images.zip", key="d1")

# --- زبانه ۲: ابعاد ثابت ---
with tabs[1]:
    st.header("ابعاد ۱۰۲۴")
    choice = st.radio("سایز:", ["مربع (1024x1024)", "افقی (1024x768)", "عمودی (768x1024)"], key="r2")
    tw, th = (1024, 1024) if "مربع" in choice else ((1024, 768) if "افقی" in choice else (768, 1024))
    up_r = st.file_uploader("آپلود:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u3")
    if up_r and st.button("تغییر سایز", key="b2"):
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
            for f in up_r:
                img = Image.open(f).convert("RGB")
                resized = img.resize((tw, th), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                resized.save(buf, format="JPEG", quality=90)
                zf.writestr(f"resized_{f.name}", buf.getvalue())
        st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "resized.zip", key="d2")

# --- زبانه ۳: حجم و سایز ---
with tabs[2]:
    st.header("کاهش حجم")
    up_o = st.file_uploader("آپلود:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u4")
    if up_o:
        q = st.slider("کیفیت:", 10, 100, 75, key="s3")
        sc = st.slider("مقیاس:", 10, 100, 100, key="s4")
        if st.button("بهینه سازی", key="b3"):
            z_buf = io.BytesIO()
            with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                for f in up_o:
                    img = Image.open(f).convert("RGB")
                    nw, nh = int(img.width * (sc/100)), int(img.height * (sc/100))
                    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=q)
                    zf.writestr(f"opt_{f.name}", buf.getvalue())
            st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "opt.zip", key="d3")

# --- زبانه ۴: تبدیل فرمت ---
with tabs[3]:
    st.header("تبدیل فرمت")
    up_c = st.file_uploader("آپلود:", type=['jpg','jpeg','png','webp'], accept_multiple_files=True, key="u5")
    fmt = st.selectbox("فرمت مقصد:", ["JPG", "PNG", "WEBP"], key="sel1")
    if up_c and st.button("تبدیل همه", key="b4"):
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
            for f in up_c:
                img = Image.open(f)
                out_fmt = "JPEG" if fmt == "JPG" else fmt
                img = img.convert("RGB") if fmt in ["JPG", "WEBP"] else img.convert("RGBA")
                buf = io.BytesIO()
                img.save(buf, format=out_fmt)
                zf.writestr(f"{f.name.split('.')[0]}.{fmt.lower()}", buf.getvalue())
        st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "converted.zip", key="d4")
