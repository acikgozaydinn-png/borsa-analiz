import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator

# Sayfa Ayarları
st.set_page_config(page_title="Borsa Analiz Terminali", layout="wide")

def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        # Uzun metinlerde çeviri hatasını önlemek için karakter sınırı
        return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")
st.caption("Borsa İstanbul (.IS) ve Nasdaq Hisseleri İçin Optimize Edilmiştir")

# Kullanıcı girişi
ticker_input = st.text_input("Hisse Sembolü (Örn: THYAO.IS, AAPL, MSFT):", "THYAO.IS").upper()

if ticker_input:
    try:
        hisse = yf.Ticker(ticker_input)
        info = hisse.info
        df = hisse.history(period="1y")

        if not df.empty:
            # 1. PARA BİRİMİ VE SEKTÖR ANALİZİ
            # Eğer sembol .IS ile bitiyorsa Türk Lirası, bitmiyorsa Dolar kabul et
            para = "₺" if ticker_input.endswith(".IS") else "$"
            fiyat = df['Close'].iloc[-1]
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Güncel Fiyat", f"{fiyat:.2f} {para}")
            with c2:
                st.metric("Piyasa Değeri", f"{info.get('marketCap', 0):,}")
            with c3:
                # Sektör bilgisini direkt Türkçeye çeviriyoruz
                st.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))

            # 2. GELİŞMİŞ GRAFİK
            st.subheader("📈 1 Yıllık Fiyat Grafiği")
            st.area_chart(df['Close'])

            st.divider()

            # 3. ŞİRKET ÖZETİ (Garantili Çekim)
            st.subheader("📄 Kurumsal İş Özeti")
            ozet_ham = info.get('longBusinessSummary', 'Şirket özeti şu an çekilemiyor.')
            st.info(tr_cevir(ozet_ham))

            # 4. TIKLANABİLİR HABERLER VE ANLAŞMALAR
            st.subheader("🗞️ Son Haberler ve Gelişmeler")
            try:
                haberler = hisse.news
                if haberler:
                    for haber in haberler[:5]:
                        baslik = haber.get('title', 'Başlık Yok')
                        link = haber.get('link', '#')
                        # Markdown kullanarak linki tıklanabilir yapıyoruz
                        st.markdown(f"🔗 **[{tr_cevir(baslik)}]({link})**")
                        st.caption(f"Kaynak: {haber.get('publisher', 'Bilinmiyor')}")
                else:
                    st.write("Güncel haber bulunamadı.")
            except:
                st.write("Haberler şu an teknik bir nedenle yüklenemiyor.")

        else:
            st.error("Veri alınamadı. Lütfen sembolü (Örn: EREGL.IS veya TSLA) kontrol edin.")

    except Exception as e:
        st.warning(f"Bağlantı hatası veya limit aşımı: {e}")
