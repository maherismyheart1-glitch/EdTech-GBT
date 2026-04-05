import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الصفحة وإخفاء العلامات المائية نهائياً ---
st.set_page_config(page_title="EdTech-GPT | المرجع الشامل", page_icon="🧠", layout="wide")

# كود CSS مكثف لإخفاء Hosted with و Made with Streamlit وأي زوائد
hide_all_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    [data-testid="stStatusWidget"] {display: none;}
    .viewerBadge_container__1QS1n {display: none !important;}
    .stAppDeployButton {display: none !important;}
    </style>
"""
st.markdown(hide_all_style, unsafe_allow_html=True)

# --- 2. عرض اللوجوهات (تعديل الأسامي حسب GitHub عندك) ---
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    # عدلت الاسم هنا ليكون مطابق لصورتك في GitHub
    if os.path.exists("college_logo.png.jpg"):
        st.image("college_logo.png.jpg", width=100)
    else:
        st.write("🏛️")

with col2:
    st.markdown("<h1 style='text-align: center; color: #3B82F6;'>EdTech-GPT المرجع الذكي 🧠</h1>", unsafe_allow_html=True)

with col3:
    # عدلت الاسم هنا ليكون مطابق لصورتك في GitHub
    if os.path.exists("dept_logo.png.jpg"):
        st.image("dept_logo.png.jpg", width=100)
    else:
        st.write("💻")

# --- 3. إعداد الـ API ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Missing API Key in Secrets")
    st.stop()

# اختيار الموديل
@st.cache_resource
def get_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "flash" in m.name or "pro" in m.name:
                return genai.GenerativeModel(m.name)
    return None

model = get_model()

# --- 4. قراءة الكتب ---
@st.cache_data
def load_data():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages:
                        text += page.extract_text()
                except: continue
    return text

knowledge_base = load_data()

# --- 5. القائمة الجانبية ---
with st.sidebar:
    st.header("🛠️ خيارات")
    if st.button("✨ ملخص الـ 50 سؤال"):
        if knowledge_base:
            with st.spinner("جاري التلخيص..."):
                res = model.generate_content(f"لخص المنهج التالي في 50 سؤال وجواب: {knowledge_base[:40000]}")
                st.download_button("تحميل الملخص", res.text, "Summary.txt")
    
    st.divider()
    st.markdown("### 👨‍💻 فريق العمل:\n**عبدالرحمن عصام & أروى محمود**")

# --- 6. الشات والذاكرة ---
if "msgs" not in st.session_state:
    st.session_state.msgs = []

for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if p := st.chat_input("اسألني أي شيء..."):
    st.session_state.msgs.append({"role": "user", "content": p})
    with st.chat_message("user"):
        st.markdown(p)

    with st.chat_message("assistant"):
        history = "\n".join([f"{m['role']}:{m['content']}" for m in st.session_state.msgs[-5:]])
        full_p = f"المنهج: {knowledge_base[:30000]}\nالسياق: {history}\nالسؤال: {p}"
        resp = model.generate_content(full_p)
        st.markdown(resp.text)
        st.session_state.msgs.append({"role": "assistant", "content": resp.text})
