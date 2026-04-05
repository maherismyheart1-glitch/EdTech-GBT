import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Page Config & Professional Styling
st.set_page_config(page_title="EdTech-GPT Ultra", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    /* Sidebar on the LEFT */
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    /* Content on the RIGHT (Arabic Flow) */
    .main .block-container { direction: rtl !important; text-align: right !important; padding-top: 2rem; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .thinking-box { background-color: #f8faff; border-right: 5px solid #1E40AF; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #444; font-size: 0.9rem; line-height: 1.6; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Top Header with 3 Logos
# University Logo at the very top
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
if os.path.exists("University_logo.png"): 
    st.image("University_logo.png", width=120)
st.markdown("</div>", unsafe_allow_html=True)

# College and Dept Logos beside the Title
l_col, m_col, r_col = st.columns([1, 2, 1])
with l_col:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=90)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=90)
with m_col:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT Ultra 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #666;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r_col:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=90)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=90)

st.divider()

# 3. AI Engine Setup
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') 
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Smart Data Ingestion
@st.cache_resource
def load_and_chunk():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages: text += page.extract_text() + " "
                except: continue
    splitter = RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=150)
    return splitter.split_text(text)

chunks = load_and_chunk()

# 5. Sidebar (Left)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة الجانبية</h2>", unsafe_allow_html=True)
    st.divider()
    st.write("👤 **Abdelrahman Essam**")
    st.write("👤 **Arwa Mahmoud**")
    st.divider()
    if st.button("🗑️ مسح السجل التاريخي"):
        st.session_state.messages = []
        st.rerun()

# 6. Interaction Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

def process_query(query):
    # RAG Search
    relevant = [c for c in chunks if any(w.lower() in c.lower() for w in query.split())]
    context = "\n".join(relevant[:3]) if relevant else "\n".join(chunks[:3])
    
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
    
    prompt = f"""
    Context: {context}
    History: {history}
    Query: {query}
    
    Task:
    1. Analyze the text.
    2. Explain your reasoning briefly.
    3. Answer in friendly Egyptian Arabic.
    
    Format:
    THOUGHT: <تحليلك السريع للمعلومة>
    ANSWER: <الإجابة النهائية بالمصري>
    """
    
    try:
        res = model.generate_content(prompt)
        text = res.text
        if "THOUGHT:" in text and "ANSWER:" in text:
            return text.split("THOUGHT:")[1].split("ANSWER:")[0].strip(), text.split("ANSWER:")[1].strip()
        return None, text
    except:
        return None, "حصل ضغط على السيرفر، جرب تاني يا بطل."

# Chat Input
if user_input := st.chat_input("اسألني أي حاجة في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        thought, ans = process_query(user_input)
        if thought:
            with st.expander("🧠 كواليس التفكير (بناءً على المنهج)"):
                st.markdown(f"<div class='thinking-box'>{thought}</div>", unsafe_allow_html=True)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
