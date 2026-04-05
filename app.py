import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

st.set_page_config(
    page_title="EdTech-GPT Pro", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    section[data-testid="stSidebar"] {
        left: 0 !important;
        right: auto !important;
        direction: ltr !important;
        border-right: 1px solid #ddd;
    }
    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

col_logo1, col_title, col_logo2 = st.columns([1, 2, 1])

with col_logo1:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=110)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=110)

with col_title:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #10B981;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)

with col_logo2:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=110)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=110)

st.divider()

try:
    api_key = st.secrets["API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Credentials Error: {e}")
    st.stop()

@st.cache_data
def load_curriculum():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:20]: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_curriculum()

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 Sidebar</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 👨‍💻 Developed by:")
    st.write("✨ **Abdelrahman Essam**")
    st.write("✨ **Arwa Mahmoud**")
    st.divider()
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns(2)
with col1: btn_sum = st.button("✨ ملخص الزتونة")
with col2: btn_quiz = st.button("🃏 سؤال تحدي")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

def generate_ai_reply(query):
    try:
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
        full_p = f"You are an academic assistant. Context: {knowledge_base[:30000]}\nHistory:\n{history}\nAnswer in Egyptian Arabic: {query}"
        response = model.generate_content(full_p)
        return response.text
    except:
        return "Server busy, please try again."

if btn_sum:
    with st.chat_message("assistant"):
        reply = generate_ai_reply("لخص أهم نقاط المنهج في نقاط سريعة.")
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

if prompt := st.chat_input("Ask EdTech-GPT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = generate_ai_reply(prompt)
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
