import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# 1. Sayfa Ayarları
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

# 2. Akıllı Çeviri Fonksiyonu (Sektör ve Haber Düzeltmeli)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    
    # Sektör isimleri için özel sözlük (Yahoo'nun hatalı genel isimlerini düzeltir)
    sozluk = {
        "Industrials": "Sanayi / Havacılık",
        "Airlines": "Hava Yolları",
        "Technology": "Teknoloji",
        "Financial Services": "Finansal Hizmetler",
        "Istanbul": "İstanbul"
    }
    
    if metin in sozluk: return sozluk[metin]
    
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except:
        return metin

# 3. Başlık ve Giriş
st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, EREGL.IS, AAPL):", "THYAO.IS").upper()

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        df = hisse.history(period="1y")
        info = hisse.info

        if not df.empty:
            # Para Birimi Belirleme
            para = "TL" if ticker.endswith(".IS") else "USD"
            
            # Üst Metrikler
            c1, c2, c3 = st.columns(3)
            fiyat = df['Close'].iloc[-1]
            c1.metric("Güncel Fiyat", f"{fiyat:.2f} {para}")
            
            # Şirket Değeri (TL/USD eklenmiş hali)
            deger = info.get('marketCap', 0)
            c2.metric("Piyasa Değeri", f"{deger:,.0f} {para}")
            
            # Sektör (Düzeltilmiş hali)
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            # Grafik (Daha Geniş ve Net)
            st.subheader(f"📈 {ticker} - 1 Yıllık Gelişim")
            st.area_chart(df['Close'])

            st.divider()
            
            # Detaylar
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("📄 Faaliyet Özeti")
                st.info(tr_cevir(info.get('longBusinessSummary', 'Bilgi çekilemedi.')))
            
            with col2:
                st.subheader("🗞️ Son Haberler")
                for haber in hisse.news[:5]:
                    baslik = haber.get('title', 'Haber')
                    link = haber.get('link', '#')
                    # Tıklanabilir Linkler
                    st.markdown(f"🔗 **[{tr_cevir(baslik)}]({link})**")
                    st.write("---")
        else:
            st.error("Veri bulunamadı. Lütfen sembolü kontrol edin.")

    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("⚠️ Yahoo Limiti Doldu! 15 dk bekleyin, sayfayı yenilemeyin.")
        else:
            st.error(f"Teknik Hata: {e}")
​<!-- end list -->
