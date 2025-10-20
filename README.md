# 🗣️ RAG Destekli Türkçe ↔ İngilizce Çeviri Chatbotu

Bu proje, **Akbank GenAI Bootcamp** kapsamında geliştirilmiş, **Retrieval Augmented Generation (RAG)** mimarisi üzerine kurulu bir **çift yönlü (Türkçe ↔ İngilizce)** çeviri chatbotudur.  
Amaç, zengin çeviri örneklerini (context) kullanarak kullanıcının girdiği cümleleri yüksek doğrulukla çevirmektir.

---

## 🎯 1. Projenin Amacı

Projenin temel amacı, dil modellerinin (LLM) genel çeviri yeteneklerini, spesifik çeviri çiftlerini içeren bir **vektör veritabanı** ile güçlendirmektir.  
Bu **RAG yaklaşımı** sayesinde model, sadece genel bilgiye dayanmak yerine, eğitildiği çeviri örneklerini referans alarak **daha bağlamsal ve tutarlı çeviriler** üretir.

---

## 📊 2. Veri Seti Hakkında Bilgi

**Veri Kaynağı:** Kaggle veya benzeri platformlardan (örn: *Helsinki-NLP OPUS-Tatoeba* serisi).  
**İçerik:** Her satır bir İngilizce cümle ve karşılığı olan Türkçe cümleyi içerir.  
> Örnek: `"I am hungry" | "Açım"`

**Hazırlık Süreci:**
- Cümle çiftleri **LangChain Text Splitters** ile işlenmiştir.  
- Ardından, **Google GenerativeAIEmbeddings (models/text-embedding-004)** ile vektörlere dönüştürülmüştür.  
- Bu vektörler **ChromaDB** içerisinde depolanmıştır.

---

## ⚙️ 3. Kullanılan Yöntemler ve Mimarî

Sistem, yüksek performanslı ve çift yönlü çeviri için gelişmiş bir **RAG zinciri (Retrieval + Generation)** üzerine kuruludur.

| Bileşen                    | Teknoloji                   | Görev |
| **Büyük Dil Modeli (LLM)** | Gemini 2.5 Flash            | Çeviri üretimi ve akıl yürütme |
| **Embedding Modeli**       | Google `text-embedding-004` | Veri setindeki cümleleri vektör uzayına dönüştürme |
| **Vektör Veritabanı**      | ChromaDB                    | Vektörlerin depolanması ve arama işlemi |
| **RAG Çerçevesi**          | LangChain                   | Zinciri yönetme ve prompt oluşturma |
| **Arayüz**                 | Streamlit                   | Web tabanlı kullanıcı arayüzü sunumu |

---

### 🔍 Pre-Retrieval Translation (Geri Çekme Öncesi Çeviri)

Bu teknik, Türkçe sorguların İngilizce vektör veritabanında doğru aranmasını sağlar:

1. **Kullanıcı Sorgusu (Türkçe)** → “Günaydın”
2. **Mini LLM (Gemini 2.5 Flash)** → İngilizceye çevrilir: “Good morning”
3. **Retrieval:** İngilizce sorgu ChromaDB’de aranır.
4. **Generation:** Bulunan bağlam ve orijinal sorgu, ana LLM’e gönderilerek hedef dile çeviri yapılır.

Bu sayede, **alaka düzeyi (relevance)** maksimuma çıkar.

---

## 🚀 4. Elde Edilen Sonuçlar

✅ **Yüksek Alaka Düzeyi:** Pre-Retrieval Translation sayesinde Türkçe sorgular bile İngilizce vektörler arasında doğru şekilde eşleşmiştir.  
✅ **Temiz Çıktı:** Optimize edilmiş prompt template’leri sayesinde model yalnızca çeviriyi döndürür.  
✅ **Çift Yönlü Çeviri:** Tek arayüzle hem Türkçe → İngilizce hem İngilizce → Türkçe çeviri yapılabilir.

---

## 🛠️ 5. Kurulum ve Çalıştırma Kılavuzu

### 🔧 Ön Gereklilikler

- Python 3.9+
- VS Code veya benzeri bir IDE
- `.env` dosyasında `GEMINI_API_KEY`
- Eğer Kaggle verisi kullanıyorsanız, `kaggle.json` dosyasını `rag_setup.py` ile aynı klasöre ekleyin.

---

### 💻 Kurulum Adımları

**1️⃣ Depoyu Klonlayın ve Klasöre Girin**
```bash
git clone https://github.com/KullaniciAdiniz/genai-rag-translation-chatbot.git
cd genai-rag-translation-chatbot
2️⃣ Sanal Ortam (venv) Kurun

python -m venv venv


3️⃣ Sanal Ortamı Aktif Edin

# Windows
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate


4️⃣ Bağımlılıkları Yükleyin

pip install -r requirements.txt


5️⃣ Vektör Veritabanını Oluşturun (Bir Kez)

python rag_setup.py


Bu adım sonunda ./chroma_db_translation klasörü oluşacaktır.

6️⃣ Uygulamayı Başlatın

streamlit run app.py


Uygulama otomatik olarak tarayıcıda açılır:
👉 http://localhost:8501

🌐 6. Web Arayüzü & Deploy Linki

Projenin canlı versiyonuna aşağıdaki linkten ulaşabilirsiniz:

🔗 [CANLI UYGULAMA LİNKİ BURAYA EKLENECEK]

⚠️ Not: Streamlit Cloud’a deploy ettikten sonra bu linki ekleyip README.md dosyasını güncellemeyi unutmayın.