🗣️ RAG Destekli Türkçe ↔ İngilizce Çeviri Chatbotu

Bu proje, Akbank GenAI Bootcamp kapsamında geliştirilmiş, Retrieval Augmented Generation (RAG) mimarisi üzerine kurulu bir çeviri chatbotudur. Amacı, zengin çeviri örneklerini (Context) kullanarak kullanıcının girdiği cümleleri Türkçe'den İngilizce'ye veya İngilizce'den Türkçe'ye yüksek doğrulukla çevirmektir.

1. 🎯 Projenin Amacı

Projenin temel amacı, dil modellerinin (LLM) genel çeviri yeteneklerini, spesifik çeviri çiftlerini içeren bir vektör veritabanı ile güçlendirmektir. Bu RAG yaklaşımı sayesinde, model sadece genel bilgiye dayanmak yerine, eğitildiği çeviri örneklerini referans alarak daha bağlamsal ve tutarlı çeviriler üretir.

2. 📊 Veri Seti Hakkında Bilgi

Bu projede, Türkçe ve İngilizce karşılıklı cümle çiftlerini içeren bir çeviri veri seti kullanılmıştır.

Veri Kaynağı: Kaggle veya benzeri platformlardan (Örn: Helsinki-NLP OPUS-Tatoeba serisinden) türetilen bir İngilizce-Türkçe çeviri çiftleri seti.

İçerik: Her bir satır, bir İngilizce cümle ve onun karşılığı olan Türkçe cümleyi içerir (Örn: "I am hungry" | "Açım").

Hazırlık Metodolojisi: Veri setindeki cümleler, LangChain Text Splitters kullanılarak işlenmiş ve Google GenerativeAIEmbeddings (models/text-embedding-004) ile vektörlere dönüştürülerek ChromaDB'ye kaydedilmiştir.

3. ⚙️ Kullanılan Yöntemler ve Çözüm Mimarisi

Çözüm mimarisi, yüksek performanslı ve çift yönlü çeviri yapabilmek için gelişmiş bir RAG zinciri üzerine kurulmuştur:

Bileşen

Teknoloji

Görev

Büyük Dil Modeli (LLM)

Gemini 2.5 Flash

Çeviri Üretimi (Generation) ve akıl yürütme.

Embedding Modeli

Google (text-embedding-004)

Veri setindeki cümleleri vektör uzayına dönüştürme.

Vektör Veritabanı

ChromaDB

Vektörlerin depolanması ve arama (Retrieval) işlemi.

RAG Çerçevesi

LangChain

Tüm zinciri yönetme ve Prompt oluşturma.

Arayüz

Streamlit

Web tabanlı kullanıcı arayüzü sunumu.

Çözüm Mimarisi Detayları: Pre-Retrieval Translation

Proje, özellikle Türkçe sorguların Vektör Veritabanında (İngilizce cümlelerden oluşan) doğru bir şekilde aranabilmesi için Pre-Retrieval Translation (Geri Çekme Öncesi Çeviri) tekniğini kullanır:

Kullanıcı Sorgusu (Türkçe): Kullanıcı, Türkçe bir cümle girer.

Mini LLM (Gemini 2.5 Flash): Bu sorgu, ana RAG zincirine girmeden önce ayrı bir Mini LLM (hızlı çevirmen) tarafından İngilizce'ye çevrilir. (Örn: "Günaydın" -> "Good morning")

Arama (Retrieval): İngilizceye çevrilmiş sorgu, Vektör DB'de arama yapmak için kullanılır. Bu, alaka düzeyini (relevance) maksimize eder.

Üretim (Generation): Arama sonucu bulunan bağlam (context) ve kullanıcının orijinal (Türkçe veya İngilizce) sorusu, ana Gemini LLM'e gönderilir. LLM, orijinal soruya bakarak doğru hedef dile çeviriyi yapar.

4. 🚀 Elde Edilen Sonuçlar

Yüksek Alaka Düzeyi: Pre-Retrieval Translation sayesinde, Türkçe sorgular bile İngilizce vektörler arasında yüksek doğrulukla aranabilmektedir.

Temiz Çıktı: Prompt Template optimizasyonu sayesinde LLM, gereksiz hata mesajları olmadan (Örn: "Sorry, I could not find...") sadece çeviriyi döndürmektedir.

Çift Yönlü Çeviri: Tek bir arayüz ve mimari ile hem Türkçe-İngilizce hem de İngilizce-Türkçe çeviriler başarılı bir şekilde gerçekleştirilmiştir.

5. 🛠️ Kodunuzun Çalışma Kılavuzu (Lokal Ortam İçin)

Projenin yerel bilgisayarınızda (Windows veya Mac/Linux) çalıştırılması için aşağıdaki adımları takip ediniz:

Ön Gereklilikler

Python 3.9+

VS Code veya tercih edilen IDE.

Hassas Dosyalar:

GEMINI_API_KEY'inizin bulunduğu bir .env dosyası.

Kaggle veri setini kullanıyorsanız, kaggle.json dosyasını rag_setup.py ile aynı klasöre yerleştirin.

Kurulum Adımları

Git Klonlama ve Klasöre Girme:

git clone [https://github.com/KullaniciAdiniz/genai-rag-translation-chatbot.git](https://github.com/KullaniciAdiniz/genai-rag-translation-chatbot.git)
cd genai-rag-translation-chatbot


Sanal Ortam Kurulumu (venv):

python -m venv venv


Sanal Ortamı Aktif Etme:

Windows (PowerShell): .\venv\Scripts\Activate.ps1

Mac/Linux: source venv/bin/activate

Bağımlılıkları Yükleme:

pip install -r requirements.txt


Vektör Veritabanını Oluşturma (Sadece Bir Kez):

python rag_setup.py


Bu komut, veriyi indirir, işler ve ./chroma_db_translation klasörünü oluşturur.

Uygulamayı Başlatma:

streamlit run app.py


Uygulama tarayıcınızda açılacaktır (genellikle http://localhost:8501).

6. 🌐 Web Arayüzü & Deploy Linki

Projenin canlı ve çalışan versiyonuna aşağıdaki linkten ulaşabilirsiniz.

[CANLI UYGULAMA LİNKİ BURAYA EKLENECEK]

NOT: Bu linki, Streamlit Cloud'a deploy ettikten sonra almayı unutmayın. Linki ekledikten sonra, README.md dosyasını son kez GitHub'a yükleyiniz.