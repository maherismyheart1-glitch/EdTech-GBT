import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Page Config (Sidebar on Left)
st.set_page_config(page_title="EdTech-GPT Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    .main .block-container { direction: rtl !important; text-align: right !important; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 2. Professional Header (Logos beside Title)
l, m, r = st.columns([1, 2, 1])
with l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=100)
with m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=100)

st.divider()

# 3. AI Config (Correct Model Name)
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') # The Fix
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Smart Chunking (RAG Style)
@st.cache_resource
def get_chunks():
    all_chunks = []
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + " "
                    # Smart Splitting to avoid 404/Busy
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    all_chunks.extend(splitter.split_text(text))
                except: continue
    return all_chunks

chunks_db = get_chunks()

# 5. Sidebar (On the Left)
with st.sidebar:
    st.markdown("### 🎓 القائمة الجانبية")
    st.divider()
    st.write("✨ **عبدالرحمن عصام**")
    st.write("✨ **أروى محمود**")
    st.divider()
    if st.button("🗑️ مسح السجل"):
        st.session_state.messages = []
        st.rerun()

# 6. Interaction Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ ملخص الزتونة")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

def run_ai(query):
    # Search for relevant context (RAG)
    context = "\n".join([c for c in chunks_db if any(w.lower() in c.lower() for w in query.split())][:3])
    if not context: context = "\n".join(chunks_db[:3])
    
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
    prompt = f"System: Answer in Egyptian Arabic using the context.\nContext: {context}\nHistory: {history}\nUser: {query}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "السيرفر مهنج، جرب تاني يا بطل."

if btn_sum:
    with st.chat_message("assistant"):
        ans = run_ai("لخص أهم نقاط المنهج باختصار.")
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

if user_input := st.chat_input("اسأل 'الدحيح' هنا..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        ans = run_ai(user_input)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
