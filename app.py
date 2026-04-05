import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الصفحة (البار الجانبي يفتح ع الشمال) ---
st.set_page_config(
    page_title="EdTech-GPT Pro", 
    page_icon="🧠", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# كود CSS جبار لضبط كل مليمتر في الصفحة
st.markdown("""
    <style>
    /* إخفاء الزوائد */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* ضبط الخط العربي وتجاه الصفحة */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق الهيدر (العنوان واللوجوهات) */
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 10px; }
    
    /* تنسيق الشات (History) */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #eee; }
    
    /* إجبار البار الجانبي يظهر بشكل شيك */
    [data-testid="stSidebar"] { background-color: #f8f9fa; min-width: 300px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر (اللوجوهات جنب العنوان بالظبط) ---
# بنعمل 3 عواميد فوق خالص: لوجو - عنوان - لوجو
col_logo1, col_title, col_logo2 = st.columns([1, 3, 1])

with col_logo1:
    # لوجو الكلية
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=120)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=120)

with col_title:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin-bottom: 0;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #10B981;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)

with col_logo2:
    # لوجو القسم
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=120)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=120)

st.divider()

# --- 3. إعداد الـ API وتحميل المنهج ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
except:
    st.error("تأكد من وضع الـ API_KEY في الـ Secrets")
    st.stop()

@st.cache_data
def load_data():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:30]: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_data()

# --- 4. البار الجانبي (Sidebar) - دايماً على الشمال في اللاب ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة الجانبية</h2>", unsafe_allow_html=True)
    st.info("مرحباً بك في النسخة الاحترافية من المرجع الذكي.")
    
    st.divider()
    st.markdown("### 👨‍💻 المطورون:")
    st.write("• **عبدالرحمن عصام محمد**")
    st.write("• **أروى محمود محمد**")
    
    st.divider()
    if st.button("🗑️ مسح سجل المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الأزرار السريعة وسجل الشات (History) ---
# الأزرار تحت الهيدر علطول
c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ ملخص الزتونة")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض سجل المحادثة (عشان يفتكر الطالب سأل في إيه)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. تنفيذ الأوامر والشات ---
if btn_sum:
    with st.chat_message("assistant"):
        with st.spinner("بجهزلك الزتونة..."):
            res = model.generate_content(f"لخص المنهج ده بالمصري في شكل نقاط: {knowledge_base[:30000]}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})

if btn_quiz:
    with st.chat_message("assistant"):
        res = model.generate_content(f"ولد سؤال MCQ صعب وإجابته بالمصري من المنهج ده: {knowledge_base[:20000]}")
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})

# استقبال الشات الجديد
if prompt := st.chat_input("اسألني أي حاجة يا بطل..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("بفكر..."):
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            full_p = f"أنت 'الدحيح'. جاوب بالمصري. المنهج: {knowledge_base[:35000]}\nالسياق: {history}\nسؤال الطالب: {prompt}"
            try:
                resp = model.generate_content(full_p)
                st.markdown(resp.text)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except:
                st.error("السيرفر مشغول، حاول تاني.")
