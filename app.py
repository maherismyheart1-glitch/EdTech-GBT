import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
import time

# --- 1. إعدادات الصفحة و CSS لإخفاء الزوائد وإظهار الجماليات ---
st.set_page_config(page_title="EdTech-GPT Ultra", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    /* إخفاء السهم الجانبي المزعج وتوسيع الصفحة */
    [data-testid="stSidebar"] {display: none;}
    .main .block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 900px; }
    
    /* ستايل الأزرار الكبيرة */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #2563EB; border: none; color: white; }
    
    /* تحسين الخط العربي */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. الهيدر الثابت (اللوجوهات وأسماء الفريق) ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png.jpg"): st.image("college_logo.png.jpg", width=90)
with col_m:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin-bottom: 0;'>EdTech-GPT Pro 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #10B981; font-weight: bold; font-size: 1.2rem;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with col_r:
    if os.path.exists("dept_logo.png.jpg"): st.image("dept_logo.png.jpg", width=90)

st.divider()

# --- 3. أزرار التحكم السريعة (بديلة للبار الجانبي) ---
st.markdown("### 🛠️ أدوات المراجعة السريعة")
c1, c2, c3 = st.columns(3)
with c1:
    btn_summary = st.button("✨ ملخص الزتونة")
with c2:
    btn_quiz = st.button("🃏 سؤال تحدي")
with c3:
    st.link_button("🎥 المحاضرات", "https://youtube.com/playlist?list=PLfG6QmZuFXbjjWSsTJtxvR6MZeVHfZe-Z")

# --- 4. إعداد الـ API وتحميل الكتب ---
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Missing API Key!")
    st.stop()

@st.cache_data
def load_curriculum():
    text = ""
    if os.path.exists("books"):
        for f in os.listdir("books"):
            if f.endswith(".pdf"):
                try:
                    pdf = PyPDF2.PdfReader(f"books/{f}")
                    for page in pdf.pages[:40]: text += page.extract_text() + " "
                except: continue
    return text

knowledge_base = load_curriculum()

# --- 5. منطق الأزرار (الملخص والكويز) ---
if btn_summary:
    with st.chat_message("assistant"):
        st.write("جاري تحضير ملخص المنهج بالمصري... ⏳")
        res = model.generate_content(f"لخص أهم نقاط المنهج ده بالمصري: {knowledge_base[:30000]}")
        st.markdown(res.text)

if btn_quiz:
    with st.chat_message("assistant"):
        res = model.generate_content(f"ولد سؤال MCQ واحد صعب من المنهج ده واختياراته وإجابته بالمصري: {knowledge_base[:20000]}")
        st.markdown(res.text)

# --- 6. نظام الشات (Streaming) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("اسألني أي حاجة يا بطل..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        sys_prompt = f"أنت 'الدحيح الأكاديمي'. جاوب بالمصري العامي. المنهج: {knowledge_base[:40000]}. ابدأ بيا هندسة أو يا دكتورة."
        
        response = model.generate_content(f"{sys_prompt}\nالسؤال: {p}", stream=True)
        for chunk in response:
            full_response += chunk.text
            response_placeholder.markdown(full_response + "▌")
            time.sleep(0.01)
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
