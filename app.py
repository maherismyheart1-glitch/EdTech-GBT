import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import glob
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. Page Config
st.set_page_config(page_title="EdTech-GPT Ultra", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    .stAppDeployButton {display: none !important;}
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    .main .block-container { direction: rtl !important; text-align: right !important; padding-top: 1rem; }
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Header & Logos (صائد اللوجوهات الذكي)
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
# الكود ده هيدور على أي صورة فيها كلمة university سواء كابيتال أو سمول
uni_logo_files = glob.glob("*[Uu]niversity_logo*")
if uni_logo_files:
    st.image(uni_logo_files[0], width=120)
st.markdown("</div>", unsafe_allow_html=True)

l_col, m_col, r_col = st.columns([1, 2, 1])
with l_col:
    college_logos = glob.glob("*college_logo*")
    if college_logos: st.image(college_logos[0], width=90)
with m_col:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #666;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r_col:
    dept_logos = glob.glob("*dept_logo*")
    if dept_logos: st.image(dept_logos[0], width=90)

st.divider()

# 3. AI Config
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') 
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# 4. Enterprise Data Pipeline (البحث الصاروخي بـ FAISS)
@st.cache_resource(show_spinner="بجهز المنهج بذكاء الشركات... ثواني يا بطل ⏳")
def build_vector_database():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages: text += page.extract_text() + " "
                except: continue
    
    if not text:
        return None

    # التقطيع
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_text(text)
    
    # تحويل النصوص لأرقام وبناء قاعدة البيانات (أسرع مليون مرة من البحث العادي)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.from_texts(chunks, embeddings)
    return vector_db

db = build_vector_database()

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

# 7. Ultimate Streaming Generator
def stream_ai_response(query):
    # البحث الذكي بياخد أجزاء من الثانية دلوقتي!
    if db:
        docs = db.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in docs])
    else:
        context = "لا يوجد منهج متاح."

    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
    
    prompt = f"""
    أنت مساعد أكاديمي مصري دحيح.
    سياق من الكتاب: {context}
    المحادثة السابقة: {history}
    سؤال الطالب: {query}
    التعليمات: جاوب باختصار، بشكل مباشر، وبالمصري العامية الراقية بناءً على السياق فقط.
    """
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                # الكود ده بيجبره يكتب "كلمة بكلمة" عشان يديك تأثير الـ Typewriter اللي بتحبه
                words = chunk.text.split(" ")
                for word in words:
                    yield word + " "
                    time.sleep(0.03) # تأخير بسيط جداً لعمل الإيفيكت
    except Exception as e:
        yield "السيرفر مهنج شوية، جرب تاني يا بطل."

if user_input := st.chat_input("اسألني أي حاجة في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        # دالة st.write_stream مع المولد الجديد هتديك شكل خرافي في الكتابة
        full_response = st.write_stream(stream_ai_response(user_input))
        st.session_state.messages.append({"role": "assistant", "content": full_response})
