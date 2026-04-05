import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الصفحة (البار الجانبي مفتوح دايماً) ---
st.set_page_config(page_title="EdTech-GPT Ultra", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# CSS لتجميل الموقع وإخفاء علامات Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إعداد الـ API ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # استخدام موديل مستقر جداً لتجنب خطأ NotFound
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("تأكد من وضع API_KEY في Secrets")
    st.stop()

# --- 3. قراءة المنهج (125 ميجا) ---
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

# --- 4. البار الجانبي (Sidebar) ---
with st.sidebar:
    # حل مشكلة اللوجو: هيجرب كل الأسماء المحتملة عشان يضمن الظهور
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", caption="كلية التربية النوعية")
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", caption="كلية التربية النوعية")
    
    st.markdown("---")
    st.markdown("### 👨‍💻 فريق العمل")
    # ضفت لك كل الأسماء اللي كانت في صورتك عشان محدش يزعل
    team = ["عبدالرحمن عصام محمد", "أروى محمود محمد", "إسراء عادل مصطفى", "أسماء أحمد محمد", "سحر أحمد متولي", "شهد طه أبو السعود", "شيماء يوسف سعيد", "شروق عطية"]
    for name in team:
        st.write(f"• {name}")
    
    st.markdown("---")
    if st.button("🗑️ مسح سجل المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الواجهة الرئيسية وسجل الشات ---
st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Pro 🚀</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض سجل المحادثة (Chat History)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. تنفيذ الشات ---
if prompt := st.chat_input("اسأل 'الدحيح' في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("بفكر بالمصري..."):
            # بناء السياق من السجل (آخر 5 رسائل)
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
            
            full_prompt = f"""
            أنت 'الدحيح الأكاديمي'. جاوب بالمصري العامي.
            المنهج: {knowledge_base[:40000]}
            السجل السابق: {history}
            السؤال الحالي: {prompt}
            """
            
            try:
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("السيرفر مهنج شوية، جرب تسأل تاني.")
