import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Tasarım Ayarları
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1500])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, AAPL):", "THYAO.IS").upper()

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        # Verileri daha güvenli çekmek için 'fast_info' ve 'history' kullanıyoruz
        df = hisse.history(period="1y")
        info = hisse.info

        if not df.empty:
            para = "₺" if ticker.endswith(".IS") else "$"
            
            # ÜST PANEL
            c1, c2, c3 = st.columns(3)
            c1.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f} {para}")
            c2.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            # GRAFİK (Daha belirgin hale getirildi)
            st.subheader("📈 1 Yıllık Fiyat Hareketi")
            st.line_chart(df['Close'], use_container_width=True)

            # TÜRKÇE İŞ BİLGİLERİ
            st.divider()
            st.subheader("📄 Şirket Hakkında Detaylı Bilgi")
            with st.expander("İş Özetini Okumak İçin Tıklayın", expanded=True):
                st.info(tr_cevir(info.get('longBusinessSummary', 'Bilgi çekilemedi.')))

            # HABERLER VE ANLAŞMALAR (Hata vermeyen yeni yapı)
            st.divider()
            st.subheader("🗞️ Son Haberler ve Gelişmeler")
            try:
                haberler = hisse.news
                if haberler:
                    for haber in haberler[:5]:
                        # Başlık verisini farklı yerlerden kontrol ederek çekiyoruz
                        baslik = haber.get('title', 'Başlık bulunamadı')
                        link = haber.get('link', '#')
                        st.write(f"🔹 **{tr_cevir(baslik)}**")
                        st.caption(f"[Habere Git]({link})")
                else:
                    st.write("Güncel haber bulunamadı.")
            except:
                st.write("Haberler şu an yüklenemiyor.")

        else:
            st.error("Veri alınamadı. Sembolü kontrol edip 5 dk bekleyin.")

    except Exception as e:
        st.warning("⚠️ Veri sağlayıcı şu an yoğun. Lütfen sayfayı yenilemeden 10-15 dk bekleyin.")
