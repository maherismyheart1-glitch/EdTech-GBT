import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Page Config
st.set_page_config(page_title="EdTech-GPT Ultra", layout="wide", initial_sidebar_state="expanded")

# CSS: Sidebar Left, Content Right, FIXED Sidebar Toggle
st.markdown("""
    <style>
    /* شلنا إخفاء الهيدر عشان زرار البار يفضل شغال */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    .stAppDeployButton {display: none !important;}
    
    /* إجبار البار يكون شمال */
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    
    /* المحتوى الأساسي يمين */
    .main .block-container { direction: rtl !important; text-align: right !important; padding-top: 1rem; }
    
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Header (3 Logos Fix)
# اللوجو التالت (تمت إضافة بحث ذكي عشان يتفادى مشكلة الكابيتال والسمول)
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
uni_logos = ["University_logo.png", "university_logo.png", "University_logo.jpg", "university_logo.jpg"]
for logo in uni_logos:
    if os.path.exists(logo):
        st.image(logo, width=120)
        break
st.markdown("</div>", unsafe_allow_html=True)

# لوجو الكلية والقسم
l_col, m_col, r_col = st.columns([1, 2, 1])
with l_col:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=90)
    elif os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=90)
with m_col:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #666;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r_col:
    if os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=90)
    elif os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=90)

st.divider()

# 3. AI Config
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') 
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Smart Chunks (RAG)
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

# 5. Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة الجانبية</h2>", unsafe_allow_html=True)
    st.divider()
    st.write("👤 **Abdelrahman Essam**")
    st.write("👤 **Arwa Mahmoud**")
    st.divider()
    if st.button("🗑️ مسح السجل التاريخي"):
        st.session_state.messages = []
        st.rerun()

# 6. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# 7. AI Generator Function (Streaming)
def stream_ai_response(query):
    relevant = [c for c in chunks if any(w.lower() in c.lower() for w in query.split())]
    context = "\n".join(relevant[:3]) if relevant else "\n".join(chunks[:3])
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
    
    prompt = f"""
    أنت مساعد أكاديمي مصري دحيح.
    سياق من الكتاب: {context}
    المحادثة السابقة: {history}
    سؤال الطالب: {query}
    التعليمات: جاوب باختصار، بشكل مباشر، وبالمصري العامية الراقية بناءً على السياق فقط. لا تكتب خطوات تفكير.
    """
    try:
        # هنا فعلنا الـ Stream عشان يكتب كلمة بكلمة
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield "السيرفر عليه ضغط حالياً، جرب تاني يا بطل."

if user_input := st.chat_input("اسألني أي حاجة في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        # دالة st.write_stream بتعمل الـ Typewriter effect زي ChatGPT
        full_response = st.write_stream(stream_ai_response(user_input))
        st.session_state.messages.append({"role": "assistant", "content": full_response})
