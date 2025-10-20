import os
import kagglehub
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ----------------------------------------------------
# 1️⃣ Ortam değişkenlerini yükle (.env içinde GEMINI_API_KEY olmalı)
# ----------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin.")

# ----------------------------------------------------
# 2️⃣ Kaggle dataset indir
# ----------------------------------------------------
print("📦 Kaggle dataset indiriliyor...")
dataset_path = kagglehub.dataset_download("seymasa/turkish-to-english-translation-dataset")
print(f"✅ Dataset başarıyla indirildi: {dataset_path}")

# ----------------------------------------------------
# 3️⃣ TR2EN.txt dosyasını oku
# ----------------------------------------------------
print("📄 TR2EN.txt dosyası okunuyor...")

texts = []
file_path = os.path.join(dataset_path, "TR2EN.txt")

if not os.path.exists(file_path):
    raise FileNotFoundError(f"❌ TR2EN.txt dosyası {dataset_path} içinde bulunamadı.")

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            eng, tur = parts
            texts.append(f"English: {eng}\nTurkish: {tur}")

print(f"✅ Toplam {len(texts)} çeviri satırı işlendi.")

# ⚙️ Test için sadece ilk 1000 satırı kullan (isteğe bağlı hızlandırma)
if len(texts) > 1000:
    texts = texts[:1000]
    print("⚠️ Uyarı: Test için sadece ilk 1000 satır kullanıldı.")

if len(texts) > 0:
    print("İlk 5 örnek:", texts[:5])

# ----------------------------------------------------
# 4️⃣ Metinleri parçalara ayır
# ----------------------------------------------------
print("🧩 Veri parçacıkları oluşturuluyor...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
documents = splitter.create_documents(texts)

print(f"✅ {len(documents)} metin parçası oluşturuldu.")

# ----------------------------------------------------
# 5️⃣ Embedding + Chroma veritabanı
# ----------------------------------------------------
print("💡 Vektör veritabanı oluşturuluyor...")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    client_options={"api_key": GEMINI_API_KEY}
)

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./chroma_db_translation"
)

print("✅ Vektör veritabanı başarıyla kaydedildi: ./chroma_db_translation")
print("🚀 RAG Setup tamamlandı. Artık `app.py` dosyanı çalıştırabilirsin.")
