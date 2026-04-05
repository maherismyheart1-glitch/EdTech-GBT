import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. الإعدادات (البار الجانبي واللغة) ---
st.set_page_config(page_title="EdTech-GPT", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    /* تنسيق الأزرار */
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1E40AF; color: white; border: none; }
    .stButton>button:hover { background-color: #3B82F6; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إعداد الـ API ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
except:
    st.error("تأكد من API_KEY في Secrets")
    st.stop()

# --- 3. قراءة المنهج ---
@st.cache_data
def load_curriculum():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:25]: text += page.extract_text() + " "
                except: continue
    return text

knowledge = load_curriculum()

# --- 4. البار الجانبي (أنت وأروى بس) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 المساعد الذكي</h2>", unsafe_allow_html=True)
    
    # إظهار اللوجوهات
    for f in os.listdir('.'):
        if any(x in f.lower() for x in ["college", "dept", "logo"]) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
            st.image(f)
            
    st.divider()
    st.markdown("### 👨‍💻 إعداد وتطوير:")
    st.success("✨ **عبدالرحمن عصام**")
    st.success("✨ **أروى محمود**")
    
    st.divider()
    if st.button("🗑️ مسح السجل"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الأزرار والواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)

# أزرار "الزتونة" و "التحدي"
col1, col2 = st.columns(2)
with col1: btn_sum = st.button("✨ ملخص الزتونة")
with col2: btn_quiz = st.button("🃏 سؤال تحدي")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الشات القديم
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# منطق الأزرار
if btn_sum:
    with st.chat_message("assistant"):
        res = model.generate_content(f"لخص المنهج ده بالمصري: {knowledge[:30000]}")
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})

if btn_quiz:
    with st.chat_message("assistant"):
        res = model.generate_content(f"ولد سؤال MCQ بالمصري من المنهج ده: {knowledge[:20000]}")
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})

# --- 6. الشات المباشر ---
if p := st.chat_input("اسأل 'الدحيح' هنا..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
        try:
            resp = model.generate_content(f"المنهج: {knowledge[:30000]}\nالسياق: {history}\nجاوب بالمصري: {p}")
            st.markdown(resp.text)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
        except: st.error("حاول تاني كمان شوية.")
