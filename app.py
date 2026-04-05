import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import random

# --- 1. إعدادات الصفحة والـ CSS الاحترافي ---
st.set_page_config(page_title="EdTech-GPT Pro", page_icon="🎓", layout="wide")

hide_style = """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    .viewerBadge_container__1QS1n {display: none !important;}
    .main .block-container { padding-top: 2rem; padding-bottom: 100px; }
    /* تحسين شكل الكروت والأسئلة */
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .answer-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-right: 5px solid #3B82F6; }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. الهيدر (اللوجوهات والعناوين) ---
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=100)
with col2:
    st.markdown("<h1 style='text-align: center; color: #3B82F6;'>EdTech-GPT | المرجع الذكي 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #10B981;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with col3:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=100)

# --- 3. الاتصال بـ Gemini ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Missing API Key in Secrets!")
    st.stop()

# --- 4. معالجة البيانات (الكتب) ---
@st.cache_data
def get_knowledge():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = get_knowledge()

# --- 5. ميزة الفلاش كاردز (MCQ Quiz) ---
def generate_quiz():
    prompt = f"""
    بناءً على المنهج ده: {knowledge_base[:20000]}
    ولد سؤال واحد 'اختيار من متعدد' (MCQ) مع 4 اختيارات، وحدد الإجابة الصحيحة.
    تنسيق الإجابة لازم يكون كدة:
    السؤال: [نص السؤال]
    أ) [الاختيار 1]
    ب) [الاختيار 2]
    ج) [الاختيار 3]
    د) [الاختيار 4]
    الاجابة: [حرف الاختيار الصحيح فقط]
    جاوب بالمصري البسيط.
    """
    response = model.generate_content(prompt)
    return response.text

# --- 6. القائمة الجانبية (الأدوات) ---
with st.sidebar:
    st.title("🛠️ أدوات الطالب")
    
    if st.button("🃏 اختبرني (سؤال سريع)"):
        with st.spinner("بجهز لك سؤال من المنهج..."):
            st.session_state.quiz_data = generate_quiz()
            st.session_state.show_quiz = True

    if st.button("📥 تحميل ملخص ليلة الامتحان"):
        res = model.generate_content(f"لخص أهم 50 نقطة في المنهج بالمصري: {knowledge_base[:30000]}")
        st.download_button("تحميل الملخص", res.text, "Summary_EdTech.txt")

    st.divider()
    st.info("💡 نصيحة: اسأل 'الدحيح' عن أي حاجة مش فاهمها في السكاشن.")

# --- 7. نظام الشات (باللهجة المصرية والدقة العالية) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الكويز لو الطالب طلبه
if "show_quiz" in st.session_state and st.session_state.show_quiz:
    with st.expander("📝 سؤال التحدي!", expanded=True):
        st.markdown(st.session_state.quiz_data)
        if st.button("خلصت؟ اضغط هنا عشان تولد سؤال غيره"):
            st.session_state.show_quiz = False
            st.rerun()

# عرض المحادثة
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("اسألني أي حاجة يا بطل..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context = "\n".join([f"{m['role']}:{m['content']}" for m in st.session_state.messages[-5:]])
        
        # الـ System Prompt المعدل (اللهجة المصرية + الدقة)
        system_instruction = f"""
        أنت 'الدحيح الأكاديمي'، مساعد ذكي لطلبة تكنولوجيا التعليم.
        المنهج المتوفر: {knowledge_base[:40000]}
        
        قواعدك:
        1. الإجابة لازم تكون بالعامية المصرية (زي شرح المعيدين في السكاشن).
        2. استخدم الكتب المرفوعة كمصدر أساسي وأولويّة قصوى للإجابة.
        3. لو السؤال مش في الكتب، ابحث في معلوماتك العامة بس نبه الطالب.
        4. ابدأ بكلمات زي 'بص يا هندسة'، 'يا بطل'، 'يا دكتورة'.
        5. لو في كود برمجي، اشرحه سطر سطر ببساطة.
        6. خليك دقيق ومختصر ومفيد.
        """
        
        full_prompt = f"{system_instruction}\nسياق المحادثة:\n{context}\nسؤال الطالب: {prompt}"
        response = model.generate_content(full_prompt)
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
