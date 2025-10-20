import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# ----------------------------------------------------
# 1️⃣ Ortam değişkenlerini yükle
# ----------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found. Please add it to your .env file.")
    st.stop()

# ----------------------------------------------------
# 2️⃣ Başlık
# ----------------------------------------------------
st.set_page_config(page_title="🗣️ Çeviri Chatbotu", layout="wide")
st.title("🗣️ Türkçe ↔ İngilizce Çeviri Chatbotu (RAG Destekli)")
st.markdown("Cümleyi Türkçe yazarsanız İngilizceye, İngilizce yazarsanız Türkçeye çevirir. Çeviri örnekleri için RAG veritabanını kullanır.")

# ----------------------------------------------------
# 3️⃣ Chroma veritabanını yükle
# ----------------------------------------------------
PERSIST_DIRECTORY = "./chroma_db_translation"

if not os.path.exists(PERSIST_DIRECTORY):
    st.warning("⚠️ Vektör veritabanı bulunamadı. Lütfen önce `python rag_setup.py` komutunu çalıştırın.")
    st.stop()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    client_options={"api_key": GEMINI_API_KEY}
)

try:
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    retriever = db.as_retriever(search_kwargs={"k": 5}) # Daha fazla bağlam için k=5 yapıldı
except Exception as e:
    st.error(f"❌ Veritabanı yüklenirken hata oluştu: {e}")
    st.stop()

# ----------------------------------------------------
# 4️⃣ LLM (Gemini) - RAG için
# ----------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    client_options={"api_key": GEMINI_API_KEY}
)

# ----------------------------------------------------
# 5️⃣ Türkçe sorguları İngilizceye çeviren mini LLM (ESKİ MANTIK)
# ----------------------------------------------------
translator = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    client_options={"api_key": GEMINI_API_KEY}
)

def translate_to_english(text):
    """Kullanıcının Türkçe metnini İngilizceye çevirir (Retrieval optimizasyonu için)."""
    # 💡 NOT: Bu fonksiyon, LangChain'den bağımsız olarak doğrudan LLM çağrısı yapar.
    try:
        # Sorgunun Türkçe olup olmadığını basitçe kontrol et
        if any(char in text for char in 'çğıöşüÇĞIÖŞÜ'):
             prompt = f"Translate this Turkish text into English only: {text}"
             # ESKİ KODDAKİ GİBİ SADECE İNGİLİZCE ÇEVİRİ İSTİYORUZ
             return translator.invoke(prompt).content.strip()
        
        return text  # Zaten İngilizce ise, olduğu gibi bırak
    except Exception as e:
        return text  # Hata olursa, orijinal sorguyu RAG zincirine gönder
# ----------------------------------------------------
# 6️⃣ OPTİMİZE EDİLMİŞ PROMPT TEMPLATE (Çıktı hatasını önlemek için bu kısım temiz tutuldu)
# ----------------------------------------------------
template_text = """
You are a highly efficient bilingual translation assistant.
Your task is to provide the best possible translation for the user's QUESTION.

If the QUESTION is in Turkish, translate it into English.
If the QUESTION is in English, translate it into Turkish.

Use the provided CONTEXT (translation pairs) only as a reference or example.
If the provided CONTEXT does not contain a direct translation, use your general language knowledge to translate the QUESTION.

CONTEXT (Reference Pairs):
{context}

QUESTION: {question}

TRANSLATION (Provide ONLY the translated sentence):
"""

custom_prompt = PromptTemplate.from_template(template_text)

# ----------------------------------------------------
# 7️⃣ OPTİMİZE EDİLMİŞ RAG zinciri (Retrieval ve Generation adımını ayırmak için basitleştirildi)
# ----------------------------------------------------
# Context'i alacak ve soruyu Prompt'a yerleştirecek Runnable grubu.
# Artık soru RunnablePassthrough() değil, çünkü bunu manuel olarak 9. adımda sağlayacağız.
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# RAG zincirinin sadece Generation (Üretim) kısmı
rag_generation_chain = (
    custom_prompt
    | llm
    | StrOutputParser()
)

# ----------------------------------------------------
# 8️⃣ Sohbet geçmişi
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------------------------
# 9️⃣ Kullanıcıdan giriş al (ÇİFT SORGULU DÜZELTME)
# ----------------------------------------------------
user_input = st.chat_input("Çeviri için bir cümle yazın (Örn: 'Günaydın' veya 'I'm hungry')")

if user_input:
    # Kullanıcı mesajını göster
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Çevriliyor..."):
            try:
                # 1. Mini LLM ile Retrieval için sorguyu İngilizceye çeviriyoruz.
                retrieval_query = translate_to_english(user_input)
                
                # 2. Retrieval Adımı: Çevrilmiş sorguyu kullanarak veritabanından bağlam çek.
                retrieved_docs = retriever.invoke(retrieval_query)
                context = format_docs(retrieved_docs)
                
                # 3. Generation Adımı: Ana LLM'e (rag_generation_chain) *hem bağlamı* hem de *orijinal kullanıcı girdisini* gönder.
                response = rag_generation_chain.invoke({
                    "context": context,
                    # 💡 DÜZELTME BURADA: Ana LLM'e çevrilmiş sorguyu değil, Orijinal sorguyu gönderiyoruz.
                    "question": user_input 
                }) 
                
                st.markdown(response)
            except Exception as e:
                response = f"⚠️ Hata: Çeviri yapılamadı. Detay: {e}"
                st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
