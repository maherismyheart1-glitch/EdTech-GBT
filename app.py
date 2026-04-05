import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الصفحة (إجبار البار الجانبي يفضل مفتوح) ---
st.set_page_config(
    page_title="EdTech-GPT Ultra", 
    page_icon="🧠", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# كود CSS مكثف لإخفاء زوائد Streamlit وتحسين الشكل
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    /* تحسين شكل البار الجانبي */
    section[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
    /* تحسين الخط العربي */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- 2. إعداد الـ API ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    # الموديل ده هو الأضمن حالياً لتجنب خطأ NotFound
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("تأكد من وضع API_KEY في إعدادات Secrets على Streamlit Cloud")
    st.stop()

# --- 3. محرك قراءة الكتب (125 ميجا) ---
@st.cache_data(show_spinner=False)
def load_data():
    full_text = ""
    if os.path.exists("books"):
        files = [f for f in os.listdir("books") if f.endswith(".pdf")]
        for f in files:
            try:
                reader = PyPDF2.PdfReader(f"books/{f}")
                for page in reader.pages[:30]: # قراءة زتونة كل كتاب
                    full_text += page.extract_text() + " "
            except: continue
    return full_text

knowledge_base = load_data()

# --- 4. البار الجانبي (Sidebar) - دايماً ظاهر ---
with st.sidebar:
    # محاولة عرض اللوجوهات بأي اسم موجود في GitHub
    log_path = "college_logo.png.jpg" if os.path.exists("college_logo.png.jpg") else "college_logo.png"
    if os.path.exists(log_path):
        st.image(log_path)
    
    st.markdown("### 👨‍💻 فريق عمل المشروع")
    team_list = [
        "عبدالرحمن عصام محمد", "أروى محمود محمد", "إسراء عادل مصطفى", 
        "أسماء أحمد محمد", "سحر أحمد متولي", "شهد طه أبو السعود", 
        "شيماء يوسف سعيد", "شروق عطية"
    ]
    for member in team_list:
        st.write(f"• {member}")
    
    st.divider()
    if st.button("🗑️ مسح سجل الشات"):
        st.session_state.messages = []
        st.rerun()

# --- 5. الواجهة الرئيسية وسجل الشات ---
st.markdown("<h1 style='text-align: center; color: #1E40AF;'>EdTech-GPT Pro 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>قسم تكنولوجيا التعليم والحاسب الآلي - الترم الثاني</p>", unsafe_allow_html=True)

# تهيئة سجل المحادثة (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض السجل القديم (عشان الطالب يشوف هو سأل في إيه قبل كدة)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. تنفيذ الشات الذكي ---
if prompt := st.chat_input("اسأل 'الدحيح' في أي جزء في المنهج..."):
    # إضافة سؤال المستخدم للسجل
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("بفكر بالمصري..."):
            # بناء السياق من آخر 5 رسائل في السجل
            history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
            
            final_prompt = f"""
            أنت 'الدحيح الأكاديمي'. جاوب باللهجة المصرية العامية الشيك.
            المنهج المتوفر: {knowledge_base[:40000]}
            السياق السابق: {history_context}
            السؤال الحالي: {prompt}
            تعليمات: ابدأ بكلمة تشجيع، استخدم إيموجي، وخليك دقيق من الكتب المرفوعة.
            """
            
            try:
                response = model.generate_content(final_prompt)
                st.markdown(response.text)
                # إضافة إجابة المساعد للسجل
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("السيرفر مشغول شوية يا بطل، جرب تدوس على السهم تاني.")
