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
        background-color: #00382d;
        padding: 25px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        border-bottom: 6px solid #c5a059;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #c5a059 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #00382d; padding: 10px; border-radius: 12px; }
    .stTabs [aria-selected="true"] { background-color: #c5a059 !important; }
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

def apply_text_advanced(base_image, text, font_size, text_color, opacity, x_pos, y_pos, font_file=None):
    img = base_image.convert("RGBA")
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    try:
        font = ImageFont.truetype(font_file, font_size) if font_file else ImageFont.load_default(size=font_size)
    except:
        font = ImageFont.load_default(size=font_size)
    
    draw = ImageDraw.Draw(txt_layer)
    # تبدیل رنگ HEX به RGB و اضافه کردن شفافیت
    h = text_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    rgba_color = rgb + (int(255 * (opacity / 100)),)
    
    draw.text((x_pos, y_pos), text, font=font, fill=rgba_color)
    combined = Image.alpha_composite(img, txt_layer)
    return combined.convert("RGB")

# --- تب‌ها ---
tabs = st.tabs(["🖼️ لوگو/واترمارک", "📐 ابعاد ثابت", "📉 کاهش حجم", "🔄 تغییر فرمت", "✍️ درج متن حرفه‌ای"])

# (تب‌های ۱ تا ۴ مثل قبل هستند، فقط تب ۵ تغییر اساسی کرده)
# تب ۱: لوگو
with tabs[0]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        up_m = st.file_uploader("عکس محصولات:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u1")
        up_l = st.file_uploader("لوگو طلایی:", type=['png','jpg'], key="u2")
        if up_m and up_l:
            op = st.slider("شفافیت لوگو:", 0, 100, 95)
            sz = st.slider("اندازه لوگو:", 5, 50, 20)
            pos = st.radio("مکان:", ["راست-بالا", "چپ-بالا", "راست-پایین", "چپ-پایین", "وسط"], horizontal=True)
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

# تب‌های ۲، ۳ و ۴ (ابعاد، حجم، فرمت) را به دلیل اختصار اینجا نیاوردم ولی در فایل نهایی تو هستند.
# ... (کدهای قبلی این تب‌ها بدون تغییر باقی می‌مانند) ...

# ۵. درج متن حرفه‌ای (نسخه جدید)
with tabs[4]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        up_t = st.file_uploader("انتخاب تصاویر:", type=['jpg','png','jpeg'], accept_multiple_files=True, key="u6")
        txt = st.text_input("متن مورد نظر:", "DECO ARCO")
        t_color = st.color_picker("رنگ متن:", "#c5a059")
        t_sz = st.number_input("سایز قلم:", 10, 1000, 150)
        t_op = st.slider("شفافیت متن:", 0, 100, 100)
        f_file = st.file_uploader("آپلود فونت (.ttf):", type=['ttf'])
        
        st.info("📍 تنظیم مکان متن:")
        if up_t:
            test_img = Image.open(up_t[0])
            x_val = st.slider("مکان افقی (X):", 0, test_img.width, test_img.width//2)
            y_val = st.slider("مکان عمودی (Y):", 0, test_img.height, test_img.height//2)
    
    with c2:
        if up_t:
            res_preview = apply_text_advanced(Image.open(up_t[0]), txt, t_sz, t_color, t_op, x_val, y_val, f_file)
            st.image(res_preview, use_container_width=True, caption="پیش‌نمایش چیدمان متن")
            
            if st.button("🚀 اعمال روی تمام تصاویر"):
                z_buf = io.BytesIO()
                with zipfile.ZipFile(z_buf, "a", zipfile.ZIP_DEFLATED) as zf:
                    for f in up_t:
                        res = apply_text_advanced(Image.open(f), txt, t_sz, t_color, t_op, x_val, y_val, f_file)
                        buf = io.BytesIO(); res.save(buf, format="JPEG", quality=90)
                        zf.writestr(f"text_{f.name}", buf.getvalue())
                st.download_button("📥 دریافت خروجی نهایی", z_buf.getvalue(), "deco_text_final.zip")
