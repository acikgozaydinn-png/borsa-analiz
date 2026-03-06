import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Sayfa Ayarları
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")
st.caption("Borsa İstanbul (.IS) ve Nasdaq Hisseleri İçin Optimize Edilmiştir")

ticker_input = st.text_input("Hisse Sembolü (Örn: THYAO.IS, AAPL):", "THYAO.IS").upper()

if ticker_input:
    try:
        hisse = yf.Ticker(ticker_input)
        info = hisse.info
        df = hisse.history(period="1y")

        if not df.empty:
            # --- 1. MONTE EDİLEN YER (PARA BİRİMİ) ---
            para = "₺" if ticker_input.endswith(".IS") else "$"
            # -----------------------------------------
            
            fiyat = df['Close'].iloc[-1]
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Güncel Fiyat", f"{fiyat:.2f} {para}")
            with c2:
                st.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            with c3:
                st.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            st.subheader("📈 1 Yıllık Fiyat Grafiği")
            st.area_chart(df['Close'])

            st.divider()
            st.subheader("📄 Kurumsal İş Özeti")
            st.info(tr_cevir(info.get('longBusinessSummary', 'Bilgi yok.')))

            # --- 2. MONTE EDİLEN YER (HABERLER) ---
            st.subheader("🗞️ Son Haberler ve Gelişmeler")
            try:
                haberler = hisse.news
                if haberler:
                    for haber in haberler[:5]:
                        baslik = haber.get('title', 'Başlık Yok')
                        link = haber.get('link', '#')
                        # BURASI: Tıklanabilir markdown formatı
                        st.markdown(f"🔗 **[{tr_cevir(baslik)}]({link})**")
                        st.caption(f"Kaynak: {haber.get('publisher', 'Bilinmiyor')}")
                else:
                    st.write("Güncel haber bulunamadı.")
            except:
                st.write("Haberler şu an yüklenemiyor.")

        else:
            st.error("Veri alınamadı. Lütfen sembolü kontrol edin.")

    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("⚠️ Yahoo Finance limiti doldu. Lütfen 15 dakika bekleyin ve sayfayı yenilemeyin.")
        else:
            st.error(f"Bir hata oluştu: {e}")
                
