import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات "الحديد والنار" لإجبار البار واللوجو على الظهور ---
st.set_page_config(
    page_title="EdTech-GPT Ultra", 
    layout="wide", 
    initial_sidebar_state="expanded" # ده اللي بيفتح البار أوتوماتيك
)

# كود CSS جبار لفرض التنسيق ومنع الاختفاء
st.markdown("""
    <style>
    /* إخفاء زوائد ستريمليت */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* إجبار البار الجانبي على الظهور بلون مميز */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
        background-color: #f1f5f9 !important;
    }
    
    /* تحسين الخط العربي (Cairo) */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    
    /* ستايل فقاعات الشات (History) */
    .stChatMessage { border-radius: 15px; margin-bottom: 8px; border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. إعداد الـ API (استخدام gemini-pro للأمان) ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-pro') 
except:
    st.error("⚠️ تأكد من الـ API KEY في الـ Secrets!")
    st.stop()

# --- 3. قراءة المنهج (الـ 125 ميجا) ---
@st.cache_data
def load_books():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.lower().endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:25]: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_books()

# --- 4. البار الجانبي (Sidebar) - الهوية وفريق العمل ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة الرئيسية</h2>", unsafe_allow_html=True)
    
    # حل "ذكي" لمشكلة اللوجوهات (بيدور على أي ملف صورة في الفولدر الرئيسي)
    images = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for img in images:
        if "college" in img.lower() or "dept" in img.lower():
            st.image(img, use_container_width=True)
    
    st.divider()
    st.markdown("### 👨‍💻 فريق العمل")
    names = ["عبدالرحمن عصام", "أروى محمود", "إسراء عادل", "أسماء أحمد", "سحر أحمد", "شهد طه", "شيماء يوسف", "شروق عطية"]
    for n in names: st.write(f"• {n}")
    
    st.divider()
    if st.button("🗑️ مسح سجل المحادثة"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الواجهة الرئيسية وسجل الشات (History) ---
st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Pro 🚀</h1>", unsafe_allow_html=True)

# تهيئة سجل المحادثة لو مش موجود
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض كل الرسائل القديمة (ده السجل اللي طلبته)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. الشات المباشر ---
if prompt := st.chat_input("اسأل 'الدحيح' دلوقتي..."):
    # حفظ سؤال المستخدم في السجل
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("بفكر بالمصري..."):
            # دمج التاريخ مع السؤال الجديد عشان "يفتكر" الكلام
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            full_prompt = f"المنهج: {knowledge_base[:30000]}\nسياق المحادثة:\n{history}\nأجب بالمصري على: {prompt}"
            
            try:
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                # حفظ رد الدحيح في السجل
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("حصل ضغط على السيرفر، جرب تاني!")
