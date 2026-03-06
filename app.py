import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Tasarım Ayarları
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        # Metin çok uzunsa çeviri hata verebilir, ilk 1000 karakteri alalım
        return GoogleTranslator(source='en', target='tr').translate(metin[:1000])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, FROTO.IS, AAPL):", "THYAO.IS").upper()

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        # Sadece temel bilgileri çekerek 'Rate Limit' hatasını azaltıyoruz
        info = hisse.info 
        df = hisse.history(period="1y")

        if not df.empty:
            para = "₺" if ticker.endswith(".IS") else "$"
            
            # ÜST ÖZET PANELİ
            c1, c2, c3 = st.columns(3)
            c1.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f} {para}")
            c2.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            st.area_chart(df['Close'])

            # TÜRKÇE DETAYLAR
            st.divider()
            col_sol, col_sag = st.columns([2, 1])

            with col_sol:
                st.subheader("📄 İş Özeti ve Faaliyetler")
                with st.spinner('Çeviriliyor...'):
                    st.write(tr_cevir(info.get('longBusinessSummary', '')))

            with col_sag:
                st.subheader("💰 Finansal Varlıklar")
                st.write(f"**Endüstri:** {tr_cevir(info.get('industry', 'N/A'))}")
                st.write(f"**Çalışan Sayısı:** {info.get('fullTimeEmployees', 'N/A')}")
                st.write(f"**Nakit Varlıklar:** {info.get('totalCash', 'N/A'):,} {para}")

            # HABERLER VE ANLAŞMALAR
            st.divider()
            st.subheader("🗞️ Son Haberler ve Anlaşmalar")
            for haber in hisse.news[:3]:
                st.write(f"🔹 **{tr_cevir(haber['title'])}**")
                st.caption(f"[Kaynağa Git]({haber['link']})")
        else:
            st.error("Hisse verisi bulunamadı.")
            
    except Exception as e:
        st.warning("⚠️ Yahoo Finance şu an yoğun veya limit doldu. Lütfen 15-20 dk sonra tekrar deneyin.")
