 import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Sayfa Yapılandırması
st.set_page_config(page_title="Borsa İstanbul Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    duzeltmeler = {
        "Industrials": "Sanayi / Endüstri",
        "Airlines": "Hava Yolları",
        "Technology": "Teknoloji",
        "Financial Services": "Finansal Hizmetler"
    }
    if metin in duzeltmeler: return duzeltmeler[metin]
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1000])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, EREGL.IS, AAPL):", "THYAO.IS").upper()

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        df = hisse.history(period="1y")
        info = hisse.info

        if not df.empty:
            is_bist = ticker.endswith(".IS")
            para = "TL" if is_bist else "USD"
            
            c1, c2, c3 = st.columns(3)
            fiyat = df['Close'].iloc[-1]
            piyasa_degeri = info.get('marketCap', 0)
            
            c1.metric("Güncel Fiyat", f"{fiyat:.2f} {para}")
            c2.metric("Piyasa Değeri", f"{piyasa_degeri:,.0f} {para}")
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            st.subheader(f"📈 {ticker} - 1 Yıllık Gelişim")
            st.area_chart(df['Close'])

            st.divider()
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("📄 İş Özeti")
                st.info(tr_cevir(info.get('longBusinessSummary', '')))
            
            with col2:
                st.subheader("🗞️ Haberler")
                for haber in hisse.news[:4]:
                    baslik = haber.get('title', 'Haber Başlığı')
                    link = haber.get('link', '#')
                    st.markdown(f"🔗 **[{tr_cevir(baslik)}]({link})**")
                    st.write("---")
        else:
            st.error("Veri bulunamadı.")
    except Exception as e:
        st.error(f"Hata: {e}")
 
