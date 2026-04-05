import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Config & Styling
st.set_page_config(page_title="EdTech-GPT Ultra", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    .main .block-container { direction: rtl !important; text-align: right !important; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .thinking-box { background-color: #f0f7ff; border-right: 5px solid #1E40AF; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-style: italic; color: #555; }
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

# 3. AI Setup
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') 
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Books Processing (Smart RAG)
@st.cache_resource
def build_kb():
    all_text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages: all_text += page.extract_text() + " "
                except: continue
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_text(all_text)

chunks = build_kb()

# 5. Sidebar
with st.sidebar:
    st.markdown("### 🎓 لوحة التحكم")
    st.write("✨ **Abdelrahman Essam**")
    st.write("✨ **Arwa Mahmoud**")
    st.divider()
    if st.button("🗑️ مسح السجل"):
        st.session_state.messages = []
        st.rerun()

# 6. Interaction Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns(2)
with col1: btn_sum = st.button("✨ ملخص الزتونة")
with col2: btn_quiz = st.button("🃏 سؤال تحدي")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

def run_deep_ai(user_query):
    # Smart search for relevant context
    relevant = [c for c in chunks if any(w.lower() in c.lower() for w in user_query.split())]
    context = "\n".join(relevant[:3]) if relevant else "\n".join(chunks[:3])
    
    # 💡 SYSTEM PROMPT: Forces Thinking Process
    prompt = f"""
    Context: {context}
    Query: {user_query}
    
    Instructions:
    1. First, analyze the user query and the provided context.
    2. Think step-by-step about the answer.
    3. Provide the final answer in Egyptian Arabic.
    
    Format your response EXACTLY like this:
    THOUGHT: <your step-by-step thinking in Arabic>
    ANSWER: <your final friendly answer in Egyptian Arabic>
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        # Parsing Thinking vs Answer
        if "THOUGHT:" in raw_text and "ANSWER:" in raw_text:
            thought = raw_text.split("THOUGHT:")[1].split("ANSWER:")[0].strip()
            answer = raw_text.split("ANSWER:")[1].strip()
            return thought, answer
        return None, raw_text
    except:
        return None, "السيرفر مهنج، جرب تاني يا بطل."

if btn_sum:
    with st.chat_message("assistant"):
        thought, ans = run_deep_ai("لخص أهم نقاط المنهج.")
        if thought: st.markdown(f"<div class='thinking-box'><b>🧠 بفكر في إيه:</b><br>{thought}</div>", unsafe_allow_html=True)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

if user_input := st.chat_input("اسألني أي حاجة يا بطل..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        thought, ans = run_deep_ai(user_input)
        if thought: st.markdown(f"<div class='thinking-box'><b>🧠 بفكر في إيه:</b><br>{thought}</div>", unsafe_allow_html=True)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
