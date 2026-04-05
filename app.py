import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات "القوة القصوى" (إجبار الظهور) ---
st.set_page_config(
    page_title="EdTech-GPT Final",
    layout="wide",
    initial_sidebar_state="expanded" # فتح البار إجباري
)

# كود CSS لنسف أي مشاكل في العرض
st.markdown("""
    <style>
    /* إخفاء الزبالة التقنية */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* تثبيت البار الجانبي ومنعه من الهروب */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        min-width: 320px !important;
    }
    
    /* تنسيق الخط العربي (Cairo) */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق سجل الشات (History) */
    .stChatMessage { border-radius: 12px; margin-bottom: 10px; border: 1px solid #eee; background-color: #fdfdfd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. تشغيل الـ API (بأضمن موديل) ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except:
    st.error("⚠️ مشكلة في الـ API Key.. اتأكد منه في الـ Secrets!")
    st.stop()

# --- 3. قراءة المنهج (الـ 125 ميجا) ---
@st.cache_data(show_spinner=False)
def load_curriculum():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:30]: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_curriculum()

# --- 4. البار الجانبي (Sidebar) - الهوية وفريق العمل ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 المساعد الأكاديمي</h2>", unsafe_allow_html=True)
    
    # عرض الصور (بيدور على أي ملف فيه اسم logo)
    all_files = os.listdir('.')
    for f in all_files:
        if "logo" in f.lower() and f.lower().endswith(('.png', '.jpg', '.jpeg')):
            st.image(f, use_container_width=True)
    
    st.divider()
    st.markdown("### 👨‍💻 فريق عمل المشروع")
    names = ["عبدالرحمن عصام", "أروى محمود", "إسراء عادل", "أسماء أحمد", "سحر أحمد", "شهد طه", "شيماء يوسف", "شروق عطية"]
    for n in names: st.write(f"• {n}")
    
    st.divider()
    if st.button("🗑️ مسح سجل المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الواجهة الرئيسية وسجل الشات (History) ---
st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Pro 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>قسم تكنولوجيا التعليم والحاسب الآلي</p>", unsafe_allow_html=True)

# تهيئة السجل (History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض السجل التاريخي للمحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. الشات الحي ---
if prompt := st.chat_input("اسأل 'الدحيح' دلوقتي..."):
    # حفظ السؤال في التاريخ
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # بناء السياق التاريخي (بيفتكر اللي اتقال قبل كدة)
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
        
        full_p = f"المنهج: {knowledge_base[:30000]}\nسياق المحادثة:\n{history}\nأجب بالمصري على: {prompt}"
        
        try:
            response = model.generate_content(full_p)
            st.markdown(response.text)
            # حفظ الرد في التاريخ
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error("حصل ضغط على السيرفر، جرب تسأل تاني!")
