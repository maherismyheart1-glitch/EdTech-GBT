import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. الإعدادات ---
st.set_page_config(page_title="EdTech-GPT", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    /* تنسيق الأزرار */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر الاحترافي (اللوجوهات جنب العنوان) ---
# هنا السر: بنقسم الصفحة 3 عواميد عشان نحط اللوجوهات جنب العنوان
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    # لوجو الكلية على اليمين (أو الشمال حسب اتجاه الصفحة)
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=100)

with col_mid:
    # العنوان في النص بالظبط
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin-top: 10px;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)

with col_right:
    # لوجو القسم على الناحية التانية
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=100)

st.divider()

# --- 3. إعداد الـ API والمنهج ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
except:
    st.error("Check API_KEY in Secrets")
    st.stop()

@st.cache_data
def load_data():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:20]: text += page.extract_text()
                except: continue
    return text

knowledge = load_data()

# --- 4. البار الجانبي (فارغ من اللوجوهات عشان الزحمة) ---
with st.sidebar:
    st.markdown("### 🎓 القائمة الجانبية")
    st.info("✨ مجهود مشترك بين عبدالرحمن وأروى لتطوير مرجع ذكي للقسم.")
    
    st.divider()
    if st.button("🗑️ مسح سجل المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الأزرار وسجل الشات ---
c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ ملخص الزتونة")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# تنفيذ الأزرار والشات (نفس المنطق السابق)
if btn_sum:
    with st.chat_message("assistant"):
        res = model.generate_content(f"لخص المنهج بالمصري: {knowledge[:30000]}")
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})

if prompt := st.chat_input("اسأل 'الدحيح' هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
        resp = model.generate_content(f"المنهج: {knowledge[:30000]}\nالسياق: {history}\nجاوب بالمصري: {prompt}")
        st.markdown(resp.text)
        st.session_state.messages.append({"role": "assistant", "content": resp.text})
