import streamlit as st
import os

# RAG Setup için gerekli kütüphaneler (rag_setup.py'den taşındı)
import kagglehub
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# Unidecode kütüphanesi (Türkçe karakter düzeltmesi için gerekli olabilir)
import unidecode 

# ----------------------------------------------------
# A. SABİT DEĞİŞKENLER VE GİZLİ ANAHTARLAR
# ----------------------------------------------------
DB_PATH = "./chroma_db_translation"
MODEL_NAME = "gemini-2.5-flash"

# Streamlit Secrets'tan anahtarları al
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # Kullanıcıyı Streamlit Secrets'a yönlendir
    st.error("❌ GEMINI_API_KEY bulunamadı. Lütfen Streamlit Secrets'ı kontrol edin.")
    st.stop()

# ----------------------------------------------------
# B. RAG KURULUM FONKSİYONU (SADECE BİR KEZ ÇALIŞIR)
# ----------------------------------------------------

def setup_rag_database():
    """
    Kaggle'dan veriyi indirir, işler ve ChromaDB veritabanını oluşturur.
    Bu fonksiyon, veritabanı klasörü mevcut değilse çalışır.
    """
    if os.path.exists(DB_PATH):
        # Veritabanı zaten var, kurulumu atla
        return

    st.warning("⚠️ Vektör veritabanı bulunamadı. Kurulum başlatılıyor... Lütfen bekleyiniz.")
    
    # 2️⃣ Kaggle dataset indir (rag_setup.py'den taşındı)
    try:
        st.info("📦 Kaggle dataset indiriliyor... (Kaggle Secrets Kontrol Ediliyor)")
        # Kaggle, ortam değişkenlerini (KAGGLE_USERNAME, KAGGLE_KEY) otomatik kullanır
        dataset_path = kagglehub.dataset_download("seymasa/turkish-to-english-translation-dataset")
        st.success(f"✅ Dataset başarıyla indirildi: {dataset_path}")
    except Exception as e:
        st.error("❌ Kaggle indirme hatası. Lütfen Streamlit Secrets'da KAGGLE_USERNAME ve KAGGLE_KEY'in doğru olduğundan emin olun.")
        st.code(str(e))
        st.stop()

    # 3️⃣ TR2EN.txt dosyasını oku
    st.info("📄 TR2EN.txt dosyası okunuyor ve işleniyor...")
    texts = []
    file_path = os.path.join(dataset_path, "TR2EN.txt")

    if not os.path.exists(file_path):
        st.error(f"❌ TR2EN.txt dosyası {dataset_path} içinde bulunamadı.")
        st.stop()

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                eng, tur = parts
                # Metni RAG için en uygun formata dönüştür
                texts.append(f"Source (EN): {eng}\nTarget (TR): {tur}")

    st.caption(f"Toplam {len(texts)} çeviri satırı işlendi. İlk 5 örnek: {texts[:5]}")
    
    # ⚙️ Test için sadece ilk 1000 satırı kullan
    if len(texts) > 1000:
        texts = texts[:1000]

    # 4️⃣ Metinleri parçalara ayır
    st.info("🧩 Veri parçacıkları oluşturuluyor...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    documents = splitter.create_documents(texts)
    st.caption(f"{len(documents)} metin parçası oluşturuldu.")

    # 5️⃣ Embedding + Chroma veritabanı
    st.info("💡 Vektör veritabanı oluşturuluyor... (Bu kısım biraz zaman alabilir)")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        client_options={"api_key": GEMINI_API_KEY}
    )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    st.success("🎉 Vektör veritabanı başarıyla kaydedildi!")
    st.balloons()
    
    # Kurulum sonrası uygulamayı yeniden yükle
    st.rerun()

# ----------------------------------------------------
# C. CHATBOT UYGULAMA LOGİĞİ
# ----------------------------------------------------

@st.cache_resource
def get_llm():
    """Gemini modelini cache'ler."""
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME, 
        temperature=0.0, 
        client_options={"api_key": GEMINI_API_KEY}
    )

@st.cache_resource
def get_vectorstore():
    """Vektör mağazasını yükler ve cache'ler."""
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            client_options={"api_key": GEMINI_API_KEY}
        )
        return Chroma(
            persist_directory=DB_PATH, 
            embedding_function=embeddings
        )
    except Exception as e:
        # Eğer DB yoksa veya yüklenemiyorsa hata döndürür
        return None

def translate_query(query, llm):
    """
    Türkçe sorguları İngilizceye çevirir (Pre-Retrieval Translation).
    """
    # Sorgunun hangi dilde olduğunu tespit et (Basit Kontrol)
    if any(char in query for char in "çğıöşüÇĞİÖŞÜ"):
        # Türkçe ise İngilizceye çevir
        prompt = f"Translate the following Turkish sentence to English only, strictly without any explanation or extra text: '{query}'"
        result = llm.invoke(prompt)
        return result.content
    else:
        # Zaten İngilizce kabul et veya çeviriye gerek yok.
        return query

def format_docs(docs):
    """
    RAG bağlamı için belgeleri biçimlendirir.
    """
    return "\n\n".join(doc.page_content for doc in docs)

# ----------------------------------------------------
# D. ANA STREAMLIT AKIŞI
# ----------------------------------------------------

def main():
    st.set_page_config(page_title="RAG Çeviri Chatbotu (Gemini)", layout="centered")
    st.title("🗣️ RAG Destekli Türkçe ↔ İngilizce Çeviri")

    # 1. Veritabanı Kontrolü ve Kurulumu
    if not os.path.exists(DB_PATH):
        # Eğer veritabanı yoksa kurulumu başlat
        setup_rag_database()
        return # Kurulumu başlattıktan sonra ana akışı durdur

    # 2. Vektör Mağazasını Yükle
    vectorstore = get_vectorstore()
    if vectorstore is None:
        st.error("Veritabanı yüklenemedi. Lütfen klasörün (chroma_db_translation) varlığını kontrol edin.")
        return

    llm = get_llm()
    retriever = vectorstore.as_retriever()
    
    # 3. Prompt ve Zincir Tanımlama
    template = """
    Sen bir Türkçe/İngilizce çeviri uzmanısın. Görevin, verilen SORGUsunu HEDEF DİL'e çevirmektir.
    Çeviri yaparken, Bağlam (Context) bölümündeki ilgili çeviri örneklerini (Source/Target çiftleri) kullan.
    
    Hedef Dil: SORGUnun dili Türkçe ise Hedef Dil İngilizce'dir. SORGUnun dili İngilizce ise Hedef Dil Türkçe'dir.
    
    Kurallar:
    1. Sadece çeviriyi döndür. Açıklama, uyarı veya ek not EKLEME.
    2. Bağlamdaki kelime ve cümle yapılarını çevirine dahil etmeye çalış.

    Bağlam (Context):
    {context}

    Sorgu: {query}
    """
    rag_prompt = PromptTemplate.from_template(template)

    # 4. RAG Zinciri
    rag_chain = (
        RunnablePassthrough.assign(
            # 1. Sorguyu İngilizceye çevir (RAG arama için)
            retrieval_query=RunnableLambda(lambda x: translate_query(x['query'], llm)),
        )
        # 2. Vektör DB'de arama yap (İngilizce sorgu ile)
        | RunnablePassthrough.assign(
            context=RunnableLambda(lambda x: x['retrieval_query']) | retriever | format_docs
        )
        # 3. Çeviri Promput'unu oluştur
        | rag_prompt
        # 4. LLM'e gönder ve cevabı al
        | llm
        | RunnableLambda(lambda x: x.content)
    )

    # 5. Arayüz ve Sohbet Geçmişi
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Türkçe veya İngilizce bir cümle girin..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Çeviri yapılıyor..."):
                try:
                    # RAG Zincirini Çalıştır
                    response = rag_chain.invoke({"query": prompt})
                except Exception as e:
                    response = f"Çeviri hatası oluştu: {e}"
                    st.error(response)
                    
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
