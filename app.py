import streamlit as st
from PIL import Image
import io
import zipfile

# ۱. تنظیمات اولیه صفحه
st.set_page_config(page_title="ویرایشگر حرفه‌ای تصاویر", layout="wide")

# ۲. تعریف زبانه‌ها - دقت کنید که تعداد نام‌ها باید ۴ تا باشد
tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️ افزودن لوگو", 
    "📏 ابعاد ثابت (1024)", 
    "📉 تغییر حجم و سایز", 
    "🔄 تبدیل فرمت"
])

# ---------------------------------------------------------
# زبانه اول: افزودن لوگو
# ---------------------------------------------------------
with tab1:
    st.header("افزودن لوگو")
    m_files = st.file_uploader("انتخاب عکس‌های اصلی:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="k1")
    l_file = st.file_uploader("انتخاب لوگو:", type=['png','jpg'], key="k2")
    if m_files and l_file:
        c1, c2 = st.columns(2)
        op = c1.slider("شفافیت:", 0, 100, 100, key="k3")
        sz = c2.slider("اندازه لوگو (%):", 1, 100, 20, key="k4")
        if st.button("شروع عملیات لوگو", key="k5"):
            z_buf = io.BytesIO()
            with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                l_img = Image.open(l_file).convert("RGBA")
                for f in m_files:
                    img = Image.open(f).convert("RGBA")
                    lw = int(img.width * (sz / 100))
                    lh = int(l_img.height * (lw / l_img.width))
                    lr = l_img.resize((lw, lh), Image.Resampling.LANCZOS)
                    if op < 100:
                        r, g, b, a = lr.split()
                        a = a.point(lambda p: p * (op / 100))
                        lr = Image.merge('RGBA', (r, g, b, a))
                    img.paste(lr, (img.width - lw - 10, img.height - lh - 10), lr)
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=90)
                    zf.writestr(f"logo_{f.name}", buf.getvalue())
            st.success("انجام شد")
            st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "logo_images.zip", key="k6")

# ---------------------------------------------------------
# زبانه دوم: ابعاد ثابت
# ---------------------------------------------------------
with tab2:
    st.header("تغییر ابعاد به ۱۰۲۴")
    s_choice = st.radio("سایز مقصد:", ["مربع (1024x1024)", "افقی (1024x768)", "عمودی (768x1024)"], key="k7")
    if "مربع" in s_choice: tw, th = 1024, 1024
    elif "افقی" in s_choice: tw, th = 1024, 768
    else: tw, th = 768, 1024
    r_files = st.file_uploader("آپلود عکس:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="k8")
    if r_files and st.button("تغییر سایز همه", key="k9"):
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
            for f in r_files:
                img = Image.open(f).convert("RGB")
                resized = img.resize((tw, th), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                resized.save(buf, format="JPEG", quality=90)
                zf.writestr(f"resized_{f.name}", buf.getvalue())
        st.success("انجام شد")
        st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "resized.zip", key="k10")

# ---------------------------------------------------------
# زبانه سوم: تغییر حجم
# ---------------------------------------------------------
with tab3:
    st.header("کاهش حجم")
    o_files = st.file_uploader("آپلود عکس:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="k11")
    if o_files:
        ca, cb = st.columns(2)
        q = ca.slider("کیفیت:", 10, 100, 75, key="k12")
        sc = cb.slider("مقیاس (%):", 10, 100, 100, key="k13")
        if st.button("بهینه‌سازی حجم", key="k14"):
            z_buf = io.BytesIO()
            with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                for f in o_files:
                    img = Image.open(f).convert("RGB")
                    nw, nh = int(img.width * (sc/100)), int(img.height * (sc/100))
                    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=q)
                    zf.writestr(f"opt_{f.name}", buf.getvalue())
            st.success("انجام شد")
            st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "opt.zip", key="k15")

# ---------------------------------------------------------
# زبانه چهارم: تبدیل فرمت
# ---------------------------------------------------------
with tab4:
    st.header("تبدیل فرمت")
    c_files = st.file_uploader("آپلود برای تبدیل:", type=['jpg','jpeg','png','webp'], accept_multiple_files=True, key="k16")
    t_format = st.selectbox("فرمت مقصد:", ["JPG", "PNG", "WEBP"], key="k17")
    if c_files and st.button("تبدیل فرمت همه", key="k18"):
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
            for f in c_files:
                img = Image.open(f)
                f_name = f.name.split('.')[0]
                # تبدیل فرمت
                out_format = "JPEG" if t_format == "JPG" else t_format
                if t_format in ["JPG", "WEBP"]:
                    img = img.convert("RGB")
                else:
                    img = img.convert("RGBA")
                buf = io.BytesIO()
                img.save(buf, format=out_format)
                zf.writestr(f"{f_name}.{t_format.lower()}", buf.getvalue())
        st.success("تبدیل انجام شد")
        st.download_button("📥 دانلود ZIP", z_buf.getvalue(), "converted.zip", key="k19")
