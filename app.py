import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Page Configuration (Sidebar on Left)
st.set_page_config(page_title="EdTech-GPT Enterprise", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    .main .block-container { direction: rtl !important; text-align: right !important; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 2. Advanced Header with Logos
l, m, r = st.columns([1, 2, 1])
with l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
with m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Pro 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)

st.divider()

# 3. AI Configuration (The Fixed Model Name)
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') # The definitive fix
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Professional Document Processing (Smart Chunking)
@st.cache_resource
def process_curriculum():
    all_chunks = []
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + " "
                    
                    # Splitting text into chunks (Like big companies do)
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    chunks = splitter.split_text(text)
                    all_chunks.extend(chunks)
                except: continue
    return all_chunks

chunks_db = process_curriculum()

# 5. Smart Search (Retrieval Logic)
def get_relevant_context(query, db, top_k=3):
    # This mimics a Vector DB by searching for keywords in chunks
    relevant = [c for c in db if any(word.lower() in c.lower() for word in query.split())]
    return "\n".join(relevant[:top_k]) if relevant else "\n".join(db[:3])

# 6. Sidebar & History
with st.sidebar:
    st.markdown("### 🎓 Control Panel")
    st.write("✨ **Abdelrahman Essam**")
    st.write("✨ **Arwa Mahmoud**")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick Actions
c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ ملخص الزتونة")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# 7. Execution Logic
def run_ai(user_query):
    # Smart Retrieval: only send what matters
    context = get_relevant_context(user_query, chunks_db)
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
    
    prompt = f"System: You are an academic expert. Use the context below to answer in Egyptian Arabic.\nContext: {context}\nHistory: {history}\nUser: {user_query}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "السيرفر مضغوط، جرب كمان ثانية يا بطل."

if btn_sum:
    with st.chat_message("assistant"):
        ans = run_ai("لخص أهم مفاهيم المنهج باختصار شديد.")
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

if user_input := st.chat_input("اسأل 'الدحيح الأكاديمي'..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        ans = run_ai(user_input)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
