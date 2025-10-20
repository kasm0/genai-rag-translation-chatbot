# 🗣 RAG Destekli Türkçe ↔ İngilizce Çeviri Chatbotu (Gemini)

Bu proje, *Akbank GenAI Bootcamp* kapsamında geliştirilmiş, *Retrieval Augmented Generation (RAG)* mimarisi üzerine kurulu bir *çift yönlü (Türkçe ↔ İngilizce)* çeviri chatbotudur.  
Amaç, zengin çeviri örneklerini (context) kullanarak kullanıcının girdiği cümleleri yüksek doğrulukla ve bağlamsal tutarlılıkla çevirmektir.

---

## 🎯 1. Projenin Amacı

Projenin temel amacı, büyük dil modellerinin (LLM) genel çeviri yeteneklerini, spesifik çeviri çiftlerini içeren bir *vektör veritabanı* ile güçlendirmektir.  
Bu *RAG yaklaşımı* sayesinde model, sadece genel dil bilgisine dayanmak yerine, eğitildiği çeviri örneklerini referans alarak daha *bağlamsal ve tutarlı çeviriler* üretir.

---

## 📊 2. Veri Seti Hakkında Bilgi

| Özellik | Detay |
|----------|--------|
| *Veri Kaynağı* | [Kaggle - seymasa/turkish-to-english-translation-dataset](https://www.kaggle.com/datasets/seymasa/turkish-to-english-translation-dataset) |
| *İçerik* | İngilizce ve karşılığı olan Türkçe cümle çiftleri |
| *İşleme* | LangChain RecursiveCharacterTextSplitter ile 1000 satırlık veri işlenmiştir |
| *Embedding Modeli* | Google GenerativeAIEmbeddings (models/text-embedding-004) |
| *Vektör Veritabanı* | ChromaDB (chroma_db_translation) |

---

## ⚙ 3. Kullanılan Yöntemler ve Mimarî

Sistem, yüksek performanslı ve çift yönlü çeviri için gelişmiş bir *RAG zinciri* üzerine kuruludur.

| Bileşen | Teknoloji | Görev |
|----------|------------|--------|
| *Büyük Dil Modeli (LLM)* | Gemini 2.5 Flash | Çeviri üretimi ve pre-retrieval translation (ön çeviri) |
| *Embedding Modeli* | Google text-embedding-004 | Cümleleri vektör uzayına dönüştürme |
| *Vektör Veritabanı* | ChromaDB | Vektörlerin depolanması ve hızlı arama işlemi |
| *RAG Çerçevesi* | LangChain | Zinciri yönetme, prompt oluşturma ve RAG akışı |
| *Arayüz* | Streamlit | Web tabanlı kullanıcı arayüzü sunumu |

---

## 🔍 Pre-Retrieval Translation (Geri Çekme Öncesi Çeviri)

Bu kritik teknik, Türkçe sorguların İngilizce vektör veritabanında doğru aranmasını sağlar:

1. *Kullanıcı Sorgusu (Türkçe/İngilizce):* Kullanıcının girdiği cümle.
2. *Ön Çeviri (Mini LLM):* Eğer sorgu Türkçe ise, Gemini 2.5 Flash tarafından İngilizce’ye çevrilir (yalnızca arama sorgusu için).
3. *Retrieval (Geri Çekme):* İngilizce sorgu, ChromaDB’de en alakalı çeviri örneklerini bulmak için kullanılır.
4. *Generation (Üretim):* Bulunan bağlam ve orijinal sorgu, ana LLM’e gönderilerek istenen hedef dile çeviri yapılır.

👉 Bu yaklaşım, *alaka düzeyini (relevance)* maksimuma çıkarır ve *çift yönlü çeviride tutarlılık* sağlar.

---

## 🚀 4. Elde Edilen Sonuçlar

✅ *Yüksek Alaka Düzeyi:*  
Pre-Retrieval Translation sayesinde sorgunun dilinden bağımsız olarak doğru çeviri örnekleri RAG bağlamına dahil edilmiştir.

✅ *Temiz Çıktı:*  
Optimize edilmiş prompt’lar sayesinde model, sadece çeviriyi döndürür — ek açıklama veya not eklemez.

✅ *Tam Otomasyon:*  
Uygulama, *Streamlit Cloud* üzerinde otomatik olarak veritabanı kurulumunu yapacak şekilde tek bir app.py dosyasında birleştirilmiştir.

---

## 🛠 5. Kurulum ve Çalıştırma Kılavuzu

### 🔧 Ön Gereklilikler
- Python 3.9+
- Git ve Python Sanal Ortam (venv) bilgisi
- Gemini API Anahtarı (Streamlit Secrets’a eklenecek)
- Kaggle API Anahtarı (Streamlit Secrets’a KAGGLE_USERNAME ve KAGGLE_KEY olarak eklenecek)

---

### 💻 Lokal Kurulum Adımları

*1️⃣ Depoyu Klonlayın ve Klasöre Girin*
```bash
git clone https://github.com/alyekasim/genai-rag-translation-chatbot.git
cd genai-rag-translation-chatbot
2️⃣ Sanal Ortamı Aktif Edin

python -m venv venv
source venv/bin/activate  # (Mac/Linux)
.\venv\Scripts\Activate.ps1 # (Windows/PowerShell)

3️⃣ Bağımlılıkları Yükleyin

pip install -r requirements.txt

4️⃣ Uygulamayı Başlatın

streamlit run app.py

> 💡 Not: Uygulama ilk çalıştığında veritabanını otomatik olarak oluşturacaktır.




---

🌐 6. Web Arayüzü & Deploy Linki

Projenin canlı versiyonuna aşağıdaki linkten ulaşabilirsiniz.
Uygulama, ilk çalıştığında veritabanını otomatik olarak oluşturur ve ardından çeviri arayüzünü açar.

🔗 Canlı Deploy Linki: https://3edkzbyaon5nuxwvnsjahl.streamlit.app/
