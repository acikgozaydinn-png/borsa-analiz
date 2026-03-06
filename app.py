import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Sayfa Ayarları
st.set_page_config(page_title="Borsa Analiz Pro", layout="wide")

def cevir(metin):
    try:
        # deep-translator çok daha kararlı çalışır
        return GoogleTranslator(source='en', target='tr').translate(metin)
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker_input = st.text_input("Hisse Sembolü (Örn: THYAO.IS, AAPL):", "THYAO.IS").upper()

if ticker_input:
    try:
        hisse = yf.Ticker(ticker_input)
        df = hisse.history(period="1y")
        info = hisse.info

        if not df.empty:
            para_birimi = "₺" if ticker_input.endswith(".IS") else "$"
            
            # Üst Göstergeler
            col1, col2, col3 = st.columns(3)
            col1.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f} {para_birimi}")
            col2.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            col3.metric("Sektör", cevir(info.get('sector', 'Bilinmiyor')))

            st.area_chart(df['Close'])

            st.divider()
            st.subheader("📄 Şirket Özet Bilgisi (Türkçe)")
            ozet = info.get('longBusinessSummary', 'Bilgi bulunamadı.')
            st.info(cevir(ozet))

            # Haberler
            st.subheader("🗞️ Son Gelişmeler")
            for haber in hisse.news[:3]:
                st.write(f"🔹 **{cevir(haber['title'])}**")
                st.caption(f"[Habere Git]({haber['link']})")
        else:
            st.error("Hisse bulunamadı.")
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
