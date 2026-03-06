import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Sayfa Genişliği
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        # deep-translator kütüphanesini kullanarak çeviri yapar
        return GoogleTranslator(source='en', target='tr').translate(metin[:1500])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, FROTO.IS, AAPL):", "THYAO.IS").upper()

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        info = hisse.info 
        df = hisse.history(period="1y")

        if not df.empty:
            para = "₺" if ticker.endswith(".IS") else "$"
            
            # ÜST PANEL
            c1, c2, c3 = st.columns(3)
            c1.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f} {para}")
            c2.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            # GRAFİK
            st.area_chart(df['Close'])

            st.divider()
            
            # TÜRKÇE DETAYLAR
            col_sol, col_sag = st.columns([2, 1])
            with col_sol:
                st.subheader("📄 İş Özeti")
                st.info(tr_cevir(info.get('longBusinessSummary', '')))
            with col_sag:
                st.subheader("💰 Kurumsal Varlıklar")
                st.write(f"**Endüstri:** {tr_cevir(info.get('industry', 'N/A'))}")
                st.write(f"**Çalışan:** {info.get('fullTimeEmployees', 'N/A')}")
                st.write(f"**Merkez:** {tr_cevir(info.get('city', 'N/A'))}")

            # HABERLER
            st.divider()
            st.subheader("🗞️ Son Haberler")
            for haber in hisse.news[:3]:
                st.write(f"🔹 **{tr_cevir(haber['title'])}**")
                st.caption(f"[Kaynağa Git]({haber['link']})")
        else:
            st.error("Hisse bulunamadı.")
            
    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("⚠️ Yahoo Finance limiti doldu. Lütfen 15 dakika bekleyin.")
        else:
            st.error(f"Hata: {e}")
