import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الصفحة وإخفاء العلامات المائية بأقصى قوة ---
st.set_page_config(page_title="EdTech-GPT | المرجع الشامل", page_icon="🧠", layout="wide")

# كود CSS مكثف لإخفاء "Hosted with Streamlit" و "Made with Streamlit" وأي زوائد تانية
hide_all_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* إخفاء زرار الـ Deploy والـ Badge الإجباري في الموبايل */
    .stAppDeployButton {display: none !important;}
    .viewerBadge_container__1QS1n {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    /* إضافة مسافة في أسفل الصفحة عشان البار ميرخمش على الكلام */
    .main .block-container { padding-bottom: 150px; }
    /* تحسين شكل الشات */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
"""
st.markdown(hide_all_style, unsafe_allow_html=True)

# --- 2. عرض اللوجوهات والعناوين ---
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    # الأسامي هنا مطابقة للي موجود في الـ GitHub بتاعك بالظبط
    if os.path.exists("college_logo.png.jpg"):
        st.image("college_logo.png.jpg", width=110)
    else:
        st.write("🏛️ [لوجو الكلية]")

with col2:
    st.markdown("<h1 style='text-align: center; color: #3B82F6;'>EdTech-GPT المرجع الذكي 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; color: #888;'>قاعدة بيانات المنهج الشاملة (تكنولوجيا تعليم وحاسب آلي)</p>", unsafe_allow_html=True)

with col3:
    if os.path.exists("dept_logo.png.jpg"):
        st.image("dept_logo.png.jpg", width=110)
    else:
        st.write("💻 [لوجو القسم]")

# --- 3. إعداد الـ API من الـ Secrets ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ تأكد من إضافة API_KEY في إعدادات الـ Secrets على Streamlit Cloud")
    st.stop()

# البحث عن الموديل المتاح تلقائياً
@st.cache_resource
def get_working_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "flash" in m.name or "pro" in m.name:
                return genai.GenerativeModel(m.name)
    return None

model = get_working_model()

# --- 4. محرك قراءة الكتب (Caching لزيادة السرعة) ---
@st.cache_data(show_spinner=False)
def load_all_books():
    full_text = ""
    if os.path.exists("books"):
        files = [f for f in os.listdir("books") if f.endswith(".pdf")]
        for file in files:
            try:
                reader = PyPDF2.PdfReader(f"books/{file}")
                full_text += f"\n--- مصدر: {file} ---\n"
                for page in reader.pages:
                    full_text += page.extract_text() + " "
            except: continue
    return full_text

with st.spinner("جاري فحص المنهج..."):
    knowledge_base = load_all_books()

# --- 5. القائمة الجانبية (الأدوات وفريق العمل) ---
with st.sidebar:
    st.title("🛠️ أدوات المراجعة")
    
    # ميزة التلخيص
    if st.button("✨ توليد ملخص ليلة الامتحان"):
        if knowledge_base:
            with st.spinner("جاري طحن الكتب واستخراج 50 سؤال..."):
                prompt_sum = f"استخرج أهم 50 سؤال وجواب متوقعين في الامتحان من هذا المنهج: {knowledge_base[:40000]}"
                summary_res = model.generate_content(prompt_sum)
                st.success("تم التلخيص بنجاح!")
                st.download_button("📥 تحميل الملخص (Text)", summary_res.text, "Final_Revision.txt")
        else:
            st.warning("⚠️ لا توجد كتب في فولدر books للتلخيص.")

    st.divider()
    st.markdown("### 👨‍💻 فريق العمل:")
    st.success("**عبدالرحمن عصام محمد**\n\n**أروى محمود محمد**")
    
    st.divider()
    st.markdown("### 🎥 القوائم التعليمية:")
    st.caption("[Playlists - محاضرات وسكاشن](https://youtube.com/playlist?list=PLfG6QmZuFXbjjWSsTJtxvR6MZeVHfZe-Z)")

# --- 6. نظام الشات والذاكرة المستمرة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال الجديد
if user_input := st.chat_input("اسألني أي شيء في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("بفكر..."):
            # بناء سياق المحادثة (الذاكرة)
            chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
            
            final_prompt = f"""
            أنت مساعد أكاديمي خبير. المنهج: {knowledge_base[:35000]}
            تاريخ المحادثة: {chat_history}
            سؤال الطالب: {user_input}
            أجب بدقة بناءً على المنهج المتاح، وإذا كان السؤال برمجياً أجب كخبير.
            """
            
            response = model.generate_content(final_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
