import streamlit as st
from PIL import Image
import io
import zipfile
import google.generativeai as genai

# --- تنظیمات امن هوش مصنوعی ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("کلید API در بخش Secrets یافت نشد!")

# تنظیمات صفحه
st.set_page_config(page_title="ابزار جامع تصاویر", layout="wide")

# ایجاد ۵ زبانه
tabs = st.tabs(["🖼️ لوگو", "📏 ابعاد ثابت", "📉 حجم و سایز", "🔄 تبدیل فرمت", "🔍 سئو و تحلیل"])

# --- بخش‌های قبلی (لوگو، ابعاد، حجم، فرمت) بدون تغییر باقی می‌مانند ---
# ... (کد همان کدی است که قبلاً داشتی) ...

# --- زبانه ۵: سئو و تحلیل (فقط این بخش را اضافه یا جایگزین کن) ---
with tabs[4]:
    st.header("تولید متن سئو و Alt Text")
    st.info("تصویر را آپلود کنید تا هوش مصنوعی متن سئویی بسازد.")
    
    up_seo = st.file_uploader("آپلود تصویر برای تحلیل:", type=['jpg','jpeg','png','webp'], key="u6")
    user_desc = st.text_input("کلمات کلیدی (اختیاری):", placeholder="مثلاً: دکوراسیون داخلی مدرن")
    
    if up_seo and st.button("تحلیل تصویر", key="b5"):
        try:
            img_seo = Image.open(up_seo)
            st.image(img_seo, width=300)
            
            with st.spinner("جمنای در حال بررسی تصویر است..."):
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                prompt = f"تحلیل سئو برای این تصویر با تمرکز بر: {user_desc}. 1. متن Alt کوتاه 2. کپشن 3. هشتگ‌ها"
                response = model.generate_content([prompt, img_seo])
                
                st.success("تحلیل انجام شد:")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"خطا: {e}")
