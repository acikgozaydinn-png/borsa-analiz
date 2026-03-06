import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        # Uzun metinlerde hata almamak için parçalayarak çeviri yapar
        return GoogleTranslator(source='en', target='tr').translate(metin[:1500])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, FROTO.IS, AAPL):", "THYAO.IS").upper()

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        # Verileri çekiyoruz
        info = hisse.info 
        df = hisse.history(period="1y")

        if not df.empty:
            para = "₺" if ticker.endswith(".IS") else "$"
            
            # ÜST PANEL: TEMEL METRİKLER
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f} {para}")
            with c2:
                st.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            with c3:
                st.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            # GRAFİK ALANI
            st.area_chart(df['Close'])

            st.divider()
            
            # ŞİRKET DETAYLARI VE VARLIKLAR
            col_sol, col_sag = st.columns([2, 1])

            with col_sol:
                st.subheader("📄 İş Özeti ve Faaliyetler")
                with st.spinner('Çeviri yapılıyor, lütfen bekleyin...'):
                    st.info(tr_cevir(info.get('longBusinessSummary', '')))

            with col_sag:
                st.subheader("💰 Kurumsal Varlıklar")
                st.write(f"**Endüstri:** {tr_cevir(info.get('industry', 'N/A'))}")
                st.write(f"**Çalışan Sayısı:** {info.get('fullTimeEmployees', 'N/A')}")
                st.write(f"**Şirket Merkezi:** {tr_cevir(info.get('city', 'N/A'))}, {tr_cevir(info.get('country', 'N/A'))}")

            # HABERLER VE ANLAŞMALAR
            st.divider()
            st.subheader("🗞️ Son Haberler ve Gelişmeler")
            haberler = hisse.news[:5]
            if haberler:
                for haber in haberler:
                    st.write(f"🔹 **{tr_cevir(haber['title'])}**")
                    st.caption(f"Kaynak: {haber['publisher']} | [Habere Git]({haber['link']})")
            else:
                st.write("Şu an güncel haber bulunamadı.")
                
        else:
            st.error("Hisse sembolü hatalı veya veri yok.")
            
    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("⚠️ Yahoo Finance limiti doldu. Lütfen 15 dakika bekleyin.")
        else:
            st.error(f"Hata oluştu: {e}")
