import streamlit as st
import subprocess
import os

# Gerekli dosya yollarını tanımla
DB_PATH = "chroma_db_translation"
SETUP_SCRIPT = "rag_setup.py"

st.set_page_config(page_title="RAG Kurulumu", layout="wide")

st.title("⚠️ RAG Veritabanı Kurulumu ⚠️")
st.warning("Bu uygulama şu anda veritabanını oluşturmaktadır. Lütfen işlem bitene kadar bekleyiniz.")

# Kurulum dosyasının varlığını kontrol et
if not os.path.exists(SETUP_SCRIPT):
    st.error(f"Kurulum dosyası bulunamadı: {SETUP_SCRIPT}")
    st.stop()

# Kurulum başarılı olduysa, veritabanının varlığını kontrol et
if os.path.exists(DB_PATH):
    st.success(f"✅ Veritabanı (Klasör: {DB_PATH}) Zaten Mevcut. Orijinal Kodu Geri Yükleyebilirsiniz.")
    st.balloons()
    st.stop()
    
# Veritabanı bulunamazsa, kurulumu başlat
st.info("Veritabanı Kurulumu Başlatılıyor... Bu işlem (veri indirme ve embedding) birkaç dakika sürebilir.")

try:
    # rag_setup.py'yi çalıştır
    process = subprocess.run(
        ["python", SETUP_SCRIPT], 
        capture_output=True, 
        text=True, 
        check=True,
        timeout=600 # Maksimum 10 dakika süre veriyoruz
    )
    
    # İşlem tamamlandığında tekrar kontrol et
    if os.path.exists(DB_PATH):
        st.success("🎉 Veritabanı Başarıyla Oluşturuldu! 🎉")
        st.subheader("Kurulum Tamamlandı.")
        st.write("Lütfen şimdi **orijinal chatbot kodunuzu** `app.py`'ye geri yükleyin ve GitHub'a push yapın.")
        st.caption("Loglar:")
        st.code(process.stdout)
    else:
        st.error("Kurulum tamamlandı, ancak veritabanı klasörü oluşturulamadı. Logları kontrol edin.")
        st.code(process.stderr or process.stdout)
        
except subprocess.CalledProcessError as e:
    st.error(f"Kurulum hatası: {e}")
    st.code(e.stderr)
except subprocess.TimeoutExpired:
    st.error("Kurulum zaman aşımına uğradı (10 dakika). Lütfen tekrar deneyin.")
