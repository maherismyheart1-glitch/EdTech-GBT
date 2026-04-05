import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import time

# --- 1. إعدادات الصفحة و CSS لإخفاء الزوائد ---
st.set_page_config(page_title="EdTech-GPT Ultra", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    .main .block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 950px; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر (اللوجوهات وأسماء الفريق) ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=100)
with col_m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin-bottom: 0;'>EdTech-GPT Pro 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #10B981; font-weight: bold; font-size: 1.2rem;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with col_r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=100)

st.divider()

# --- 3. إعداد الـ API وتحميل المنهج ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # التعديل هنا: استخدام gemini-pro لأنه الأكثر استقراراً حالياً
    model = genai.GenerativeModel('gemini-pro') 
except:
    st.error("Missing API Key in Secrets!")
    st.stop()

@st.cache_data
def load_data():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:30]: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_data()

# --- 4. الأزرار السريعة ---
st.markdown("### 🛠️ أدوات المراجعة السريعة")
c1, c2, c3 = st.columns(3)
with c1: btn_sum = st.button("✨ ملخص الزتونة")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")
with c3: st.link_button("🎥 المحاضرات", "https://youtube.com/playlist?list=PLfG6QmZuFXbjjWSsTJtxvR6MZeVHfZe-Z")

if btn_sum:
    with st.chat_message("assistant"):
        res = model.generate_content(f"لخص المنهج ده في نقاط بالمصري: {knowledge_base[:30000]}")
        st.markdown(res.text)

if btn_quiz:
    with st.chat_message("assistant"):
        res = model.generate_content(f"ولد سؤال MCQ واحد من المنهج ده وإجابته بالمصري: {knowledge_base[:20000]}")
        st.markdown(res.text)

# --- 5. نظام الشات المتطور (Streaming) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("اسألني أي حاجة يا بطل..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        sys_p = f"أنت 'الدحيح الأكاديمي'. جاوب بالمصري. المنهج: {knowledge_base[:40000]}"
        
        try:
            # استخدام generate_content العادي لو الـ streaming فيه مشكلة في الموديل ده
            response = model.generate_content(f"{sys_p}\nالسؤال: {p}")
            full_res = response.text
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"حصلت مشكلة بسيطة: {e}")
