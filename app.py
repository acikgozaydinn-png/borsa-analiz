import streamlit as st
import yfinance as yf
from googletrans import Translator

# Sayfa Yapılandırması
st.set_page_config(page_title="Borsa Analiz Pro", layout="wide")
translator = Translator()

def cevir(metin):
    try:
        return translator.translate(metin, src='en', dest='tr').text
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

# Giriş Alanı
ticker_input = st.text_input("Hisse Sembolü (Örn: THYAO.IS, FROTO.IS, AAPL):", "THYAO.IS").upper()

if ticker_input:
    try:
        hisse = yf.Ticker(ticker_input)
        df = hisse.history(period="1y")
        info = hisse.info

        if not df.empty:
            # 1. PARA BİRİMİ VE FİYAT PANELİ
            para_birimi = "₺" if ticker_input.endswith(".IS") else "$"
            col1, col2, col3 = st.columns(3)
            col1.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f} {para_birimi}")
            col2.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            col3.metric("Sektör", cevir(info.get('sector', 'Bilinmiyor')))

            # 2. GRAFİK
            st.subheader("📊 1 Yıllık Fiyat Değişimi")
            st.area_chart(df['Close'])

            # 3. İŞ BİLGİLERİ VE VARLIKLAR (TÜRKÇE)
            st.divider()
            st.subheader("📄 Şirket Özet Bilgisi ve İş Modeli")
            ozet = info.get('longBusinessSummary', 'Bilgi bulunamadı.')
            st.info(cevir(ozet))

            # 4. HABERLER, ANLAŞMALAR VE MERKEZ BİLGİLERİ
            tab1, tab2 = st.tabs(["🗞️ Son Haberler & Anlaşmalar", "💰 Kurumsal Varlıklar"])
            
            with tab1:
                haberler = hisse.news[:5] # Son 5 gelişme
                if haberler:
                    for haber in haberler:
                        st.write(f"🔹 **{cevir(haber['title'])}**")
                        st.caption(f"Kaynak: {haber['publisher']} | [Detaya Git]({haber['link']})")
                else:
                    st.write("Güncel haber veya anlaşma kaydı bulunamadı.")

            with tab2:
                st.write(f"**Tam Zamanlı Çalışan:** {info.get('fullTimeEmployees', 'N/A')}")
                st.write(f"**Şirket Merkezi:** {cevir(info.get('city', 'N/A'))}, {cevir(info.get('country', 'N/A'))}")
                st.write(f"**Endüstri:** {cevir(info.get('industry', 'N/A'))}")
                if 'totalAssets' in info:
                    st.write(f"**Toplam Varlıklar:** {info['totalAssets']:,} {para_birimi}")

        else:
            st.error("Hisse verisi çekilemedi, lütfen sembolü kontrol edin.")

    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("⚠️ Yahoo Finance şu an yoğun. Lütfen 10 dakika bekleyip sayfayı yenileyin.")
        else:
            st.error(f"Bir hata oluştu: {e}")
