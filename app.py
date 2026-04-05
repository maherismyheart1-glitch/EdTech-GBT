import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
import glob

# ==========================================
# 1. إعدادات الصفحة والـ CSS (البار شمال والمحتوى يمين)
# ==========================================
st.set_page_config(page_title="EdTech-GPT Ultra", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* إخفاء القوائم الافتراضية وزرار الرفع */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    .stAppDeployButton {display: none !important;}
    
    /* إجبار البار الجانبي على اليسار */
    section[data-testid="stSidebar"] { left: 0 !important; right: auto !important; direction: ltr !important; border-right: 1px solid #ddd; }
    
    /* المحتوى الأساسي يمين (عربي) */
    .main .block-container { direction: rtl !important; text-align: right !important; padding-top: 1rem; }
    
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الهيدر واللوجوهات (بحث ذكي عن الصور)
# ==========================================
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
uni_logos = glob.glob("*[Uu]niversity*[Ll]ogo*.*")
if uni_logos:
    st.image(uni_logos[0], width=120)
st.markdown("</div>", unsafe_allow_html=True)

l_col, m_col, r_col = st.columns([1, 2, 1])
with l_col:
    col_logos = glob.glob("*college_logo*.*")
    if col_logos: st.image(col_logos[0], width=90)
with m_col:
    st.markdown("<h1 style='text-align: center; color: #1E40AF; margin: 0;'>EdTech-GPT 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #666;'>إعداد: عبدالرحمن عصام & أروى محمود</p>", unsafe_allow_html=True)
with r_col:
    dept_logos = glob.glob("*dept_logo*.*")
    if dept_logos: st.image(dept_logos[0], width=90)

st.divider()

# ==========================================
# 3. إعداد الاتصال بالذكاء الاصطناعي وقاعدة البيانات
# ==========================================
try:
    # استخدام المفاتيح الجديدة من الـ Secrets
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest') 
    
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    index = pc.Index("edtech-db") # الفهرس اللي عملناه على موقع Pinecone
except Exception as e:
    st.error("⚠️ في مشكلة في الاتصال بالمفاتيح السرية. اتأكد إنك ضفتهم في إعدادات Streamlit.")
    st.stop()

# ==========================================
# 4. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 القائمة الجانبية</h2>", unsafe_allow_html=True)
    st.divider()
    st.write("👤 **Abdelrahman Essam**")
    st.write("👤 **Arwa Mahmoud**")
    st.divider()
    if st.button("🗑️ مسح السجل التاريخي"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 5. واجهة المحادثة (Chat Logic)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسايل القديمة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# دالة البحث الصاروخي والرد
def stream_rag_answer(query):
    try:
        # أ. تحويل سؤال الطالب لأرقام
        query_vector = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )['embedding']
        
        # ب. البحث في Pinecone في أقل من ثانية
        search_results = index.query(
            vector=query_vector,
            top_k=3, 
            include_metadata=True 
        )
        
        # ج. تجميع النص اللي جيه من قاعدة البيانات
        context = "\n\n".join([match['metadata']['text'] for match in search_results['matches']])
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-2:]])
        
        # د. إرسال الخلاصة لـ Gemini
        prompt = f"""
        أنت مساعد أكاديمي مصري دحيح.
        معلومات من المنهج: {context}
        السجل: {history}
        سؤال الطالب: {query}
        التعليمات: جاوب باختصار، بشكل مباشر، وبالمصري العامية الراقية بناءً على السياق فقط. لا تكتب خطوات تفكير.
        """
        
        # هـ. الرد بـ Streaming (كلمة بكلمة)
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text: 
                yield chunk.text
                
    except Exception as e:
        yield "السيرفر عليه ضغط حالياً، جرب تاني يا بطل."

# استقبال سؤال المستخدم
if user_input := st.chat_input("اسألني أي حاجة في المنهج..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        # دالة st.write_stream بتعمل الـ Typewriter effect زي ChatGPT
        full_response = st.write_stream(stream_rag_answer(user_input))
        st.session_state.messages.append({"role": "assistant", "content": full_response})
