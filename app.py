import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImageFont
import io
import zipfile

# --- تنظیمات ظاهر و تم دکوآرکو ---
st.set_page_config(page_title="پنل دکوآرکو", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header {
        background-color: #00382d; /* سبز یشمی */
        padding: 25px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        border-bottom: 6px solid #c5a059; /* خط طلایی */
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #c5a059 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #00382d;
        padding: 10px;
        border-radius: 12px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #c5a059 !important;
        color: white !important;
    }
    .stTabs [data-baseweb="tab"] { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1 style="color: #c5a059; margin:0;">DECO ARCO</h1><p style="color: white; margin:0;">IMAGE STUDIO | مدیریت هوشمند تصاویر</p></div>', unsafe_allow_html=True)

# --- توابع پردازشی ---
def apply_logo(main_img, logo_img, size_per, opacity, position):
    img = main_img.convert("RGBA")
    logo = logo_img.convert("RGBA")
    lw = int(img.width * (size_per / 100))
    lh = int(logo.height * (lw / logo.width))
    lr = logo.resize((lw, lh), Image.Resampling.LANCZOS)
    if opacity < 100:
        r, g, b, a = lr.split()
        a = a.point(lambda p: p * (opacity / 100))
        lr = Image.merge('RGBA', (r, g, b, a))
    p = 25
    if position == "راست-پایین": coords = (img.width-lw-p, img.height-lh-p)
    elif position == "چپ-پایین": coords = (p, img.height-lh-p)
    elif position == "راست-بالا": coords = (img.width-lw-p, p)
    elif position == "چپ-بالا": coords = (p, p)
    else: coords = ((img.width-lw)//2, (img.height-lh)//2)
    img.paste(lr, coords, lr)
    return img.convert("RGB")

def apply_text(base_image, text, font_size, text_color, position, font_file=None):
    img = base_image.convert("RGBA").copy()
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_file, font_size) if font_file else ImageFont.load_default()
    except: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    p = 30
    if position == "راست-پایین": x, y = (img.width-tw-p, img.height-th-p)
    elif position == "وسط": x, y = ((img.width-tw)//2, (img.height-th)//2)
    else: x, y = ((img.width-tw)//2, img.height-th-p)
    draw.text((x, y), text, font=font, fill=text_color)
    return img.convert("RGB")

# --- تب‌ها ---
tabs = st.tabs(["🖼️ لوگو/واترمارک", "📐 ابعاد ثابت", "📉 کاهش حجم", "🔄 تغییر فرمت", "✍️ درج متن"])

# ۱. لوگو
with tabs[0]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        up_m = st.file_uploader("عکس محصولات:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u1")
        up_l = st.file_uploader("لوگو طلایی:", type=['png','jpg'], key="u2")
        if up_m and up_l:
            op = st.slider("شفافیت:", 0, 100, 95); sz = st.slider("اندازه لوگو:", 5, 50, 20)
            pos = st.radio("مکان:", ["راست-پایین", "وسط", "چپ-پایین"], horizontal=True)
    with c2:
        if up_m and up_l:
            st.image(apply_logo(Image.open(up_m[0]), Image.open(up_l), sz, op, pos), use_container_width=True)
            if st.button("🚀 دانلود پکیج ZIP لوگو"):
                z_buf = io.BytesIO()
                with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                    for f in up_m:
                        res = apply_logo(Image.open(f), Image.open(up_l), sz, op, pos)
                        buf = io.BytesIO(); res.save(buf, format="JPEG", quality=90)
                        zf.writestr(f"logo_{f.name}", buf.getvalue())
                st.download_button("📥 دریافت ZIP", z_buf.getvalue(), "deco_logos.zip")

# ۲. ابعاد
with tabs[1]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        choice = st.radio("سایز هدف:", ["مربع (1024x1024)", "افقی (1024x768)", "عمودی (768x1024)"])
        tw, th = (1024, 1024) if "مربع" in choice else ((1024, 768) if "افقی" in choice else (768, 1024))
        method = st.selectbox("حالت:", ["برش هوشمند (Smart Crop)", "کشش (Stretch)"])
        up_r = st.file_uploader("آپلود عکس:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u3")
    with c2:
        if up_r:
            img = Image.open(up_r[0]).convert("RGB")
            res = ImageOps.fit(img, (tw, th), Image.Resampling.LANCZOS) if "هوشمند" in method else img.resize((tw, th), Image.Resampling.LANCZOS)
            st.image(res, width=300)
            if st.button("🚀 تغییر سایز همه"):
                z_buf = io.BytesIO()
                with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                    for f in up_r:
                        img = Image.open(f).convert("RGB")
                        res = ImageOps.fit(img, (tw, th), Image.Resampling.LANCZOS) if "هوشمند" in method else img.resize((tw, th), Image.Resampling.LANCZOS)
                        buf = io.BytesIO(); res.save(buf, format="JPEG", quality=90)
                        zf.writestr(f"size_{f.name}", buf.getvalue())
                st.download_button("📥 دریافت ZIP", z_buf.getvalue(), "deco_sizes.zip")

# ۳. حجم
with tabs[2]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        up_o = st.file_uploader("آپلود برای سئو:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u4")
        if up_o:
            q = st.slider("کیفیت خروجی:", 10, 100, 70)
            sc = st.slider("مقیاس تصویر (%):", 10, 100, 100)
    with c2:
        if up_o:
            img = Image.open(up_o[0]).convert("RGB")
            nw, nh = int(img.width*(sc/100)), int(img.height*(sc/100))
            st.image(img.resize((nw, nh), Image.Resampling.LANCZOS), use_container_width=True)
            if st.button("🚀 بهینه‌سازی نهایی"):
                z_buf = io.BytesIO()
                with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                    for f in up_o:
                        img = Image.open(f).convert("RGB")
                        img = img.resize((int(img.width*(sc/100)), int(img.height*(sc/100))), Image.Resampling.LANCZOS)
                        buf = io.BytesIO(); img.save(buf, format="JPEG", quality=q)
                        zf.writestr(f"opt_{f.name}", buf.getvalue())
                st.download_button("📥 دریافت ZIP", z_buf.getvalue(), "deco_opt.zip")

# ۴. فرمت
with tabs[3]:
    up_c = st.file_uploader("تغییر فرمت دسته جمعی:", type=['jpg','jpeg','png','webp'], accept_multiple_files=True, key="u5")
    fmt = st.selectbox("فرمت مقصد:", ["WEBP", "JPG", "PNG"])
    if up_c and st.button("🔄 شروع تبدیل فرمت"):
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
            for f in up_c:
                img = Image.open(f)
                out_f = "JPEG" if fmt == "JPG" else fmt
                img = img.convert("RGB") if fmt in ["JPG", "WEBP"] else img.convert("RGBA")
                buf = io.BytesIO(); img.save(buf, format=out_f)
                zf.writestr(f"{f.name.split('.')[0]}.{fmt.lower()}", buf.getvalue())
        st.download_button("📥 دریافت ZIP", z_buf.getvalue(), "deco_formats.zip")

# ۵. متن
with tabs[4]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        up_t = st.file_uploader("درج متن/قیمت روی عکس:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u6")
        txt = st.text_input("متن:", "DECO ARCO")
        t_color = st.color_picker("رنگ متن:", "#c5a059")
        t_sz = st.slider("سایز:", 20, 200, 80)
        t_pos = st.selectbox("مکان متن:", ["پایین-وسط", "وسط", "راست-پایین"])
        f_file = st.file_uploader("آپلود فونت فارسی (TTF):", type=['ttf'])
    with c2:
        if up_t:
            st.image(apply_text(Image.open(up_t[0]), txt, t_sz, t_color, t_pos, f_file), use_container_width=True)
            if st.button("🚀 اعمال متن روی همه"):
                z_buf = io.BytesIO()
                with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                    for f in up_t:
                        res = apply_text(Image.open(f), txt, t_sz, t_color, t_pos, f_file)
                        buf = io.BytesIO(); res.save(buf, format="JPEG", quality=90)
                        zf.writestr(f"text_{f.name}", buf.getvalue())
                st.download_button("📥 دریافت ZIP", z_buf.getvalue(), "deco_text.zip")
