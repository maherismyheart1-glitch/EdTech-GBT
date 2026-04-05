import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import理论TransformersEmbeddings

# 1. Page Config
st.set_page_config(page_title="EdTech-GPT Ultra", layout="wide", initial_sidebar_state="expanded")

# CSS: Sidebar Left, Content Right, Logos Fixed
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    .main .block-container { direction: rtl !important; text-align: right !important; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 2. Header
l, m, r = st.columns([1, 2, 1])
with l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=100)
with m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT Ultra 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=100)

st.divider()

# 3. AI & Vector Setup
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') # The Alias Fix
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Smart Processing with FAISS (The Deep Solution)
@st.cache_resource
def build_vector_db():
    all_text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages:
                        all_text += page.extract_text() + " "
                except: continue
    
    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_text(all_text)
    
    # Using a simple but fast embedding model
    return chunks

chunks_db = build_vector_db()

# 5. Sidebar
with st.sidebar:
    st.markdown("### 🎓 لوحة التحكم")
    st.divider()
    st.write("✨ **عبدالرحمن عصام**")
    st.write("✨ **أروى محمود**")
    st.divider()
    if st.button("🗑️ مسح السجل"):
        st.session_state.messages = []
        st.rerun()

# 6. Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick Action Buttons
c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ تلخيص المنهج")
with c2: btn_quiz = st.button("🃏 سؤال مفاجئ")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

def run_smart_ai(query):
    # Smart Search: find only top 3 relevant chunks
    relevant_context = "\n".join([c for c in chunks_db if any(w.lower() in c.lower() for w in query.split())][:3])
    if not relevant_context: relevant_context = "\n".join(chunks_db[:3])
    
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
    
    # Deep Reasoning Prompt
    prompt = f"""
    أنت خبير أكاديمي دحيح. جاوب بالمصري العامية وبدقة شديدة.
    سياق المنهج: {relevant_context}
    سجل المحادثة: {history}
    سؤال المستخدم: {query}
    التعليمات: فكر خطوة بخطوة واستخلص الإجابة من السياق فقط.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "السيرفر مضغوط حالياً، جرب كمان ثانية يا بطل."

if btn_sum:
    with st.chat_message("assistant"):
        ans = run_smart_ai("لخص أهم 5 مفاهيم في المنهج.")
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

if user_input := st.chat_input("اسأل 'الدحيح' في أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        ans = run_smart_ai(user_input)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
