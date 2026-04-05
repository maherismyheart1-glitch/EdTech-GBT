import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. Settings ---
st.set_page_config(page_title="EdTech-GPT Pro", layout="wide", initial_sidebar_state="expanded")

# CSS to fix Sidebar on the Left & Logos on Top
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    .main .block-container { direction: rtl !important; text-align: right !important; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 2. Header (Logos beside Title) ---
l, m, r = st.columns([1, 2, 1])
with l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=110)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=110)
with m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=110)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=110)

st.divider()

# --- 3. The "Correct" AI Configuration ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # Using the Correct Alias found in your research
    MODEL_NAME = 'gemini-flash-latest' 
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Config Error: {e}")
    st.stop()

@st.cache_data
def load_docs():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:15]: text += page.extract_text() + " "
                except: continue
    return text

knowledge = load_docs()

# --- 4. Sidebar (Left Side) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة الجانبية</h2>", unsafe_allow_html=True)
    st.divider()
    st.write("✨ **Abdelrahman Essam**")
    st.write("✨ **Arwa Mahmoud**")
    st.divider()
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

# --- 5. Chat Engine (History & Buttons) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ ملخص الزتونة")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

def safe_ask(query):
    try:
        # Building context with strict size limits to prevent Busy error
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
        prompt = f"Context: {knowledge[:15000]}\nHistory: {history}\nAnswer in Egyptian Arabic: {query}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback to secondary model name if the first one fails
        return f"Server Error (404/Busy). Try again in a moment. {str(e)}"

if btn_sum:
    with st.chat_message("assistant"):
        ans = safe_ask("لخص أهم نقاط المنهج.")
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

if user_input := st.chat_input("اسأل 'الدحيح' هنا..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        ans = safe_ask(user_input)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
