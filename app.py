import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. الإعدادات الأساسية (البار مفتوح والشاشة واسعة) ---
st.set_page_config(page_title="EdTech-GPT", layout="wide", initial_sidebar_state="expanded")

# CSS بسيط جداً للتنسيق من غير تعقيد
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stChatMessage { border-radius: 10px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الاتصال بالذكاء الاصطناعي ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro') # الموديل الأقوى والأثبت
except:
    st.error("تأكد من الـ API KEY في السيكرتس")
    st.stop()

# --- 3. قراءة الكتب (زتونة المنهج) ---
@st.cache_data
def load_data():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:20]: text += page.extract_text() + " "
                except: continue
    return text

curriculum_text = load_data()

# --- 4. البار الجانبي (فريق العمل واللوجوهات) ---
with st.sidebar:
    # عرض الصور بأي امتداد موجود
    for f in os.listdir('.'):
        if any(x in f.lower() for x in ["college", "dept", "logo"]) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
            st.image(f)
    
    st.markdown("### 👨‍💻 فريق العمل")
    team = ["عبدالرحمن عصام", "أروى محمود", "إسراء عادل", "أسماء أحمد", "سحر أحمد", "شهد طه", "شيماء يوسف", "شروق عطية"]
    for n in team: st.write(f"• {n}")
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الواجهة الرئيسية وسجل الشات (History) ---
st.markdown("<h1 style='text-align: center;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>المساعد الذكي لقسم تكنولوجيا التعليم</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة (سجل الشات)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. استقبال الأسئلة ---
if prompt := st.chat_input("اسألني أي حاجة في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("بفكر..."):
            # بياخد آخر رسالتين عشان يفتكر السياق
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            full_query = f"أنت مساعد أكاديمي. المنهج: {curriculum_text[:30000]}\nالسياق: {history}\nجاوب بالمصري على: {prompt}"
            
            try:
                response = model.generate_content(full_query)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("السيرفر مشغول، جرب تسأل تاني.")
