import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import time

# --- 1. إعدادات متقدمة و CSS للهوية البصرية ---
st.set_page_config(page_title="EdTech-GPT Ultra", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    .main .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    /* ستايل لفقاعات الشات */
    .stChatMessage { border-radius: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    /* تحسين الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر (فريق العمل واللوجوهات) ---
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
with col2:
    st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Ultra 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem;'><b>إعداد: عبدالرحمن عصام & أروى محمود</b></p>", unsafe_allow_html=True)
with col3:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)

# --- 3. إعداد الـ API ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Missing API Key!")
    st.stop()

# --- 4. تحميل المنهج الـ 125 ميجا (تخزين مؤقت) ---
@st.cache_data
def load_heavy_curriculum():
    all_text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    all_text += f"\n[المصدر: {f}]\n"
                    for page in pdf.pages[:50]: # يقرأ أول 50 صفحة من كل كتاب للسرعة
                        all_text += page.extract_text() + " "
                except: continue
    return all_text

knowledge_base = load_heavy_curriculum()

# --- 5. نظام الشات مع ميزة الـ Streaming (الكتابة التدريجية) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# استقبال السؤال الجديد
if p := st.chat_input("اسأل 'الدحيح' في أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"):
        st.markdown(p)

    with st.chat_message("assistant"):
        # تعليمات "الدحيح المصري"
        sys_prompt = f"""
        أنت 'الدحيح الأكاديمي'. اشرح بالمصري العامي بتاع السكاشن.
        المنهج المتوفر: {knowledge_base[:45000]}
        قواعدك:
        1. ابدأ بكلمة تشجيع (يا هندسة، يا بطل، يا دكتورة).
        2. جاوب من الكتب المرفوعة أولاً.
        3. استخدم Emojis عشان الكلام يكون مبهج.
        4. لو في خطوات، رتبها (1، 2، 3).
        """
        
        full_q = f"{sys_prompt}\nالسؤال: {p}"
        
        # تفعيل الـ Streaming (الكتابة التدريجية)
        response_placeholder = st.empty() # مكان فاضي بيتملي تدريجياً
        full_response = ""
        
        # طلب الإجابة بنظام التدفق (Stream)
        with st.spinner("بقرأ الكتب وبفكرلك في أحسن إجابة... 🤔"):
            response = model.generate_content(full_q, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                # عرض النص تدريجياً مع تأخير بسيط لمحاكاة الكتابة البشرية
                response_placeholder.markdown(full_response + "▌")
                time.sleep(0.01) # سرعة الكتابة
        
        response_placeholder.markdown(full_response) # المسح النهائي للعلامة
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- 6. القائمة الجانبية المطورة ---
with st.sidebar:
    st.title("🚀 لوحة التحكم")
    st.success(f"📚 المنهج جاهز: تم تحميل {len(os.listdir('books')) if os.path.exists('books') else 0} ملفات")
    
    if st.button("✨ توليد الزتونة (ملخص سريع)"):
        with st.status("جاري تلخيص الـ 125 ميجا...", expanded=True) as status:
            res = model.generate_content(f"لخص المنهج ده في نقاط بالمصري: {knowledge_base[:30000]}")
            st.write(res.text)
            status.update(label="تم التلخيص بنجاح!", state="complete", expanded=False)
    
    st.divider()
    st.markdown("### 🎥 فيديوهات المادة")
    st.caption("[قائمة التشغيل الرئيسية](https://youtube.com/playlist?list=PLfG6QmZuFXbjjWSsTJtxvR6MZeVHfZe-Z)")
