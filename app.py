import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- 1. إعدادات الهوية ---
st.set_page_config(page_title="EdTech-GPT | المرجع الشامل", page_icon="🧠", layout="wide")

def find_any_image(name_part):
    for file in os.listdir("."):
        if name_part.lower() in file.lower() and file.lower().endswith(('.png', '.jpg', '.jpeg')):
            return file
    return None

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    img_left = find_any_image("college")
    if img_left: st.image(img_left, width=120)
with col2:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>EdTech-GPT المرجع الذكي 🧠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>قاعدة بيانات المنهج الشاملة (تكنولوجيا تعليم وحاسب آلي)</p>", unsafe_allow_html=True)
with col3:
    img_right = find_any_image("dept")
    if img_right: st.image(img_right, width=120)

# --- 2. إعداد جيميناي والذاكرة ---
API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)

# اكتشاف الموديل الشغال تلقائياً عشان نمنع أعطال الـ 404
@st.cache_resource(show_spinner=False)
def get_working_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "flash" in m.name or "pro" in m.name: return m.name
    return None

model_name = get_working_model()
if not model_name:
    st.error("⚠️ لم يتم العثور على نماذج مدعومة في مفتاح الـ API الخاص بك.")
    st.stop()

model = genai.GenerativeModel(model_name)

# تحميل الكتب والتخزين المؤقت
@st.cache_data(show_spinner=False)
def load_fixed_books():
    context = ""
    if os.path.exists("books"):
        files = [f for f in os.listdir("books") if f.endswith(".pdf")]
        for file in files:
            try:
                reader = PyPDF2.PdfReader(f"books/{file}")
                context += f"\n--- مصدر: {file} ---\n"
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted: context += extracted
            except Exception as e:
                continue
    return context

with st.spinner("جاري تهيئة العقل المدبر وتحميل المناهج... 🚀"):
    knowledge_base = load_fixed_books()

# --- 3. القائمة الجانبية (فريق العمل، المصادر، والملخص السحري) ---
with st.sidebar:
    st.header("📌 المصادر المثبتة في النظام")
    if knowledge_base:
        st.success("✅ تم استيعاب كتب الترم الثاني بالكامل")
    else:
        st.warning("⚠️ يرجى إضافة ملفات PDF في فولدر 'books'")
    
    st.divider()
    
    # --- الميزة الجديدة: زرار التلخيص ---
    st.markdown("### 📝 المراجعة النهائية ليلة الامتحان:")
    if st.button("✨ توليد ملخص (أهم 50 سؤال)"):
        if knowledge_base:
            with st.spinner("جاري طحن الكتب واستخراج أهم 50 سؤال وجواب... ⏳ (قد يستغرق بعض الوقت)"):
                try:
                    summary_prompt = f"بناءً على محتوى المناهج التالية: {knowledge_base[:60000]}\n\nالمطلوب: استخراج أهم 50 سؤال وجواب متوقعين في الامتحان لتغطية كافة أجزاء المنهج. نسق الإجابات بشكل واضح ومنظم ليتمكن الطالب من المذاكرة منها مباشرة."
                    summary_response = model.generate_content(summary_prompt)
                    
                    st.success("🎉 تم تجهيز الملخص بنجاح!")
                    # زرار التحميل المباشر
                    st.download_button(
                        label="📥 تحميل الملخص الآن (ملف Text)",
                        data=summary_response.text,
                        file_name="Final_Revision_50_QA.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التلخيص: {e}")
        else:
            st.error("⚠️ مفيش كتب في النظام عشان الخصها!")

    st.divider()
    
    st.markdown("### 🎥 قوائم التشغيل (Playlists):")
    st.info("""
    1. [محاضرات وسكاشن - الجزء الأول](https://youtube.com/playlist?list=PLfG6QmZuFXbjjWSsTJtxvR6MZeVHfZe-Z)
    2. [محاضرات وسكاشن - الجزء الثاني](https://youtube.com/playlist?list=PLElQRioaFMAsYRrhrKCe6RIgG9Rf0eTHX)
    3. [محاضرات وسكاشن - الجزء الثالث](https://youtube.com/playlist?list=PLXx5vC7WWgMQtNbfuPNANRfTEpverkXsi)
    4. [محاضرات وسكاشن - الجزء الرابع](https://youtube.com/playlist?list=PLXx5vC7WWgMSb96Uudw7_sMyzKTzZz3GA)
    5. [محاضرات وسكاشن - الجزء الخامس](https://youtube.com/playlist?list=PLXx5vC7WWgMQvyzPHl4Mmvg22G8xXP-lY)
    """)
    
    st.divider()
    
    st.markdown("### 👨‍💻 فريق العمل:")
    st.success("""
    * عبدالرحمن عصام محمد
    * أروى محمود محمد
    """)

# --- 4. محرك الذكاء الاصطناعي (مع الذاكرة السياقية المستمرة) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    avatar = "👤" if message["role"] == "user" else "🖥️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("اسأل في المنهج، أو اطرح مشكلة برمجية لحلها..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🖥️"):
        with st.spinner("جاري التحليل واستخراج الإجابة..."):
            try:
                # --- الميزة الجديدة: بناء ذاكرة المحادثة ---
                # بناخد آخر 6 رسايل عشان الـ AI يفتكر إحنا بنتكلم في إيه ومينساش السياق
                history_context = ""
                for msg in st.session_state.chat_history[-6:]: 
                    role_name = "الطالب" if msg["role"] == "user" else "المساعد"
                    history_context += f"{role_name}: {msg['content']}\n"
                
                # صياغة الطلب الشامل (الكتب + الذاكرة + السؤال الجديد)
                full_prompt = f"""
                أنت مساعد أكاديمي خبير ومتخصص في قسم "تكنولوجيا التعليم والحاسب الآلي".
                
                المصادر المرجعية (كتب المنهج): 
                {knowledge_base[:60000]}
                
                سياق المحادثة السابقة (تذكر هذا السياق لتربط الإجابات ببعضها ولتفهم قصد الطالب إذا أشار لشيء سابق):
                {history_context}
                
                تعليمات الإجابة:
                1. إذا كان السؤال نظرياً أو يخص المناهج، اعتمد بشكل أساسي على الكتب المرجعية واذكر اسم المصدر.
                2. إذا كان السؤال برمجياً، استخدم خبرتك لتقديم الحل الأمثل والأدق فوراً.
                3. كن مترابطاً في حديثك، إذا قال الطالب "أعطني مثالاً على ذلك"، يقصد آخر موضوع تحدثتم عنه في سياق المحادثة.
                
                سؤال الطالب الحالي: {prompt}
                """
                
                response = model.generate_content(full_prompt)
                answer = response.text
                
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى. (التفاصيل: {str(e)})")
