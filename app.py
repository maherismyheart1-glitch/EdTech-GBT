import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الصفحة والجماليات ---
st.set_page_config(page_title="EdTech-GPT | المرجع الشامل", page_icon="🧠", layout="wide")

# كود سحري لإخفاء "Made with Streamlit" والبار العلوي لزيادة الاحترافية
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { margin-top: -70px; }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. عرض اللوجوهات والعناوين ---
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if os.path.exists("college_logo.png"):
        st.image("college_logo.png", width=120)
    else:
        st.write("🏛️ [لوجو الكلية]")

with col2:
    st.markdown("<h1 style='text-align: center; color: #3B82F6;'>EdTech-GPT المرجع الذكي 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #6B7280;'>قاعدة بيانات المنهج الشاملة (تكنولوجيا تعليم وحاسب آلي)</p>", unsafe_allow_html=True)

with col3:
    if os.path.exists("dept_logo.png"):
        st.image("dept_logo.png", width=120)
    else:
        st.write("💻 [لوجو القسم]")

# --- 3. إعداد الـ API والذاكرة (من الأسرار) ---
try:
    # بيسحب المفتاح من Secrets اللي عملناها في Streamlit Cloud
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ خطأ: مفتاح الـ API غير مضبوط في Secrets.")
    st.stop()

# اكتشاف أفضل موديل شغال تلقائياً
@st.cache_resource
def load_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "flash" in m.name or "pro" in m.name:
                return genai.GenerativeModel(m.name)
    return None

model = load_model()

# --- 4. محرك قراءة الكتب (تخزين مؤقت ذكي) ---
@st.cache_data(show_spinner=False)
def get_knowledge_base():
    text_content = ""
    if os.path.exists("books"):
        for file in os.listdir("books"):
            if file.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(f"books/{file}")
                    text_content += f"\n--- كتاب: {file} ---\n"
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + " "
                except: continue
    return text_content

knowledge_base = get_knowledge_base()

# --- 5. القائمة الجانبية (الأدوات، الروابط، وفريق العمل) ---
with st.sidebar:
    st.title("🛠️ لوحة التحكم")
    
    # ميزة التلخيص التلقائي
    if st.button("✨ توليد ملخص (أهم 50 سؤال)"):
        if knowledge_base:
            with st.spinner("جاري استخراج الأسئلة المتوقعة..."):
                sum_prompt = f"حلل المنهج التالي: {knowledge_base[:50000]} واستخرج أهم 50 سؤال وجواب ليلة الامتحان."
                summary = model.generate_content(sum_prompt)
                st.download_button("📥 تحميل ملخص PDF/Text", summary.text, "Summary.txt")
        else:
            st.warning("لا توجد كتب للتلخيص.")

    st.divider()
    st.markdown("### 🎥 محاضرات وسكاشن (Playlists):")
    st.caption("[1. الجزء الأول](https://youtube.com/playlist?list=PLfG6QmZuFXbjjWSsTJtxvR6MZeVHfZe-Z)")
    st.caption("[2. الجزء الثاني](https://youtube.com/playlist?list=PLElQRioaFMAsYRrhrKCe6RIgG9Rf0eTHX)")
    st.caption("[3. الجزء الثالث](https://youtube.com/playlist?list=PLXx5vC7WWgMQtNbfuPNANRfTEpverkXsi)")
    st.caption("[4. الجزء الرابع](https://youtube.com/playlist?list=PLXx5vC7WWgMSb96Uudw7_sMyzKTzZz3GA)")
    st.caption("[5. الجزء الخامس](https://youtube.com/playlist?list=PLXx5vC7WWgMQvyzPHl4Mmvg22G8xXP-lY)")

    st.divider()
    st.markdown("### 👨‍💻 فريق العمل:")
    st.info("عبدالرحمن عصام محمد\n\nأروى محمود محمد")

# --- 6. نظام الشات والذاكرة السياقية ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال سؤال جديد
if prompt := st.chat_input("اسأل في المنهج أو اطرح مشكلة برمجية..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # بناء السياق من الذاكرة (آخر 5 رسائل)
        chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
        
        full_query = f"""
        أنت مساعد أكاديمي ذكي لقسم تكنولوجيا التعليم.
        المنهج المتوفر: {knowledge_base[:40000]}
        تاريخ المحادثة الحالي: {chat_context}
        سؤال الطالب: {prompt}
        أجب بدقة بناءً على المنهج، وإذا كان السؤال برمجياً أجب كخبير أكواد.
        """
        
        response = model.generate_content(full_query)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
