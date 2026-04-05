import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات "الحديد والنار" لضبط أماكن العناصر ---
st.set_page_config(
    page_title="EdTech-GPT Final", 
    page_icon="🧠", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# كود CSS جبار لنقل البار للشمال وإخفاء العلامات وحل مشاكل العرض
st.markdown("""
    <style>
    /* إخفاء الزوائد */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* نقل البار الجانبي ليكون على اليسار حصرياً */
    section[data-testid="stSidebar"] {
        left: 0 !important;
        right: auto !important;
        border-right: 1px solid #ddd !important;
        direction: ltr !important; /* لضمان وجوده جهة اليسار */
    }
    
    /* ضبط محتوى الصفحة الرئيسي ليكون جهة اليمين (اللغة العربية) */
    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
        padding-top: 2rem;
    }
    
    /* تنسيق الأزرار لمنع الانهيار (404) */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background-color: #1E40AF;
        color: white;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر الاحترافي (اللوجوهات جنب العنوان) ---
col_l, col_m, col_r = st.columns([1, 2, 1])

with col_l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=120)
    elif os.path.exists("college_logo.png"): st.image("college_logo.png", width=120)

with col_m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #10B981;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)

with col_r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=120)
    elif os.path.exists("dept_logo.png"): st.image("dept_logo.png", width=120)

st.divider()

# --- 3. إعداد الـ API (الحل النهائي لخطأ 404) ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # استخدام الموديل gemini-1.5-pro كخيار أساسي لأنه الأكثر استقراراً في الاستضافة
    model = genai.GenerativeModel('gemini-1.5-pro') 
except:
    st.error("⚠️ تأكد من الـ API KEY في السيكرتس!")
    st.stop()

@st.cache_data
def load_curriculum():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:20]: text += page.extract_text() + " "
                except: continue
    return text

knowledge = load_curriculum()

# --- 4. البار الجانبي (موجود على الشمال دايماً) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة</h2>", unsafe_allow_html=True)
    st.info("مرحباً بك يا بطل في مرجعك الذكي.")
    st.divider()
    st.markdown("### 👨‍💻 المطورون:")
    st.write("✨ **عبدالرحمن عصام**")
    st.write("✨ **أروى محمود**")
    st.divider()
    if st.button("🗑️ مسح السجل"):
        st.session_state.messages = []
        st.rerun()

# --- 5. سجل الشات (History) والأزرار ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# الأزرار في صدر الصفحة
c1, c2 = st.columns(2)
with c1: btn_sum = st.button("✨ ملخص المنهج")
with c2: btn_quiz = st.button("🃏 سؤال تحدي")

# عرض السجل التاريخي
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 6. معالجة الأوامر (بدون انهيار 404) ---
def get_ai_response(user_query):
    try:
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
        full_p = f"المنهج: {knowledge[:30000]}\nالسياق: {history}\nجاوب بالمصري: {user_query}"
        response = model.generate_content(full_p)
        return response.text
    except Exception as e:
        return f"حصل ضغط بسيط على السيرفر، جرب تضغط تاني يا هندسة. (Error: {str(e)})"

if btn_sum:
    with st.chat_message("assistant"):
        answer = get_ai_response("لخص أهم نقاط المنهج في شكل نقاط سريعة.")
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

if btn_quiz:
    with st.chat_message("assistant"):
        answer = get_ai_response("ولد سؤال MCQ واحد صعب من المنهج مع اختياراته وإجابته.")
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

if prompt := st.chat_input("اسأل 'الدحيح' هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        answer = get_ai_response(prompt)
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
