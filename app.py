import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import time

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="EdTech-GPT Ultra", page_icon="🧠", layout="wide")

# CSS لإخفاء العلامات المائية وتحسين مظهر البار والشات
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إعداد الـ API (مع نظام حماية من الأخطاء) ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # استخدام الموديل الاحترافي الأضمن
    model = genai.GenerativeModel('gemini-1.5-pro') 
except Exception as e:
    st.error(f"⚠️ خطأ في الاتصال: {e}")
    st.stop()

# --- 3. معالجة كتب المنهج (125 ميجا) ---
@st.cache_data
def load_curriculum():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    # قراءة عينة ذكية من كل كتاب لضمان السرعة والدقة
                    for page in pdf.pages[:30]: 
                        text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_curriculum()

# --- 4. البار الجانبي (فريق العمل + سجل المحادثة + الأدوات) ---
with st.sidebar:
    # عرض اللوجوهات في البار الجانبي لضمان رؤيتها
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg")
    elif os.path.exists("college_logo.png"): st.image("college_logo.png")
    
    st.markdown("### 👨‍💻 فريق العمل")
    st.success("**عبدالرحمن عصام & أروى محمود**")
    
    st.divider()
    st.markdown("### 🛠️ الزتونة السريعة")
    btn_summary = st.button("✨ ملخص المنهج")
    btn_quiz = st.button("🃏 سؤال تحدي")
    
    if st.button("🗑️ مسح السجل"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الهيدر الرئيسي ---
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
with col_m2:
    st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Ultra 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>قاعدة بيانات تكنولوجيا التعليم الشاملة</p>", unsafe_allow_html=True)

# --- 6. نظام الشات والسجل (Chat History) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض السجل القديم
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# منطق الأزرار (لو ضغطنا ملخص يظهر في الشات)
if btn_summary:
    prompt_sum = "لخص أهم نقاط المنهج ده بالمصري في شكل نقاط سريعة."
    st.session_state.messages.append({"role": "user", "content": "ممكن ملخص للمنهج؟"})
    # تنفيذ الطلب (سيتم في بلوك الإجابة تحت)

# استقبال سؤال الطالب
if user_query := st.chat_input("اسألني أي حاجة يا بطل..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("بفكر بالمصري..."):
            # بناء سياق المحادثة من السجل
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
            
            sys_instruction = f"""
            أنت 'الدحيح الأكاديمي'. جاوب بالمصري العامي بتاع السكاشن.
            المنهج المتوفر: {knowledge_base[:40000]}
            قواعدك: ابدأ بيا هندسة، استخدم الإيموجي، وخليك دقيق من الكتب.
            """
            
            try:
                response = model.generate_content(f"{sys_instruction}\nالسجل:\n{history}\nالسؤال: {user_query}")
                full_res = response.text
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error("السيرفر مشغول شوية، جرب تدوس تاني!")
