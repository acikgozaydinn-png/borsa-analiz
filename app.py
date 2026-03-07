import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Analiz Terminali", layout="wide")

# Çeviri Fonksiyonu (Daha Hızlı ve Güvenli)
@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    sozluk = {
        "Industrials": "Sanayi / Havacılık", "Technology": "Teknoloji",
        "Financial Services": "Finansal Hizmetler", "Basic Materials": "Temel Maddeler",
        "Communication Services": "İletişim", "Consumer Defensive": "Tüketim Ürünleri"
    }
    if metin in sozluk: return sozluk[metin]
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

# Sembol Girişi
ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS, EREGL.IS, AAPL, NVDA):", "THYAO.IS").upper()

# Grafik ve Veri İçin Zaman Aralığı Seçimi
period_map = {"1 Gün": "1d", "5 Gün": "5d", "1 Ay": "1mo", "6 Ay": "6mo", "1 Yıl": "1y", "Tümü": "max"}
secilen_sure = st.selectbox("Grafik Zaman Aralığı Seçin:", list(period_map.keys()), index=4)

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        # Grafik için veri çekme
        df = hisse.history(period=period_map[secilen_sure])
        info = hisse.info

        if not df.empty:
            # Para Birimi Belirleme (USD/TL Ayrımı)
            is_bist = ticker.endswith(".IS")
            para = "₺" if is_bist else "$"
            
            # Üst Panel - Metrikler
            c1, c2, c3, c4 = st.columns(4)
            fiyat = df['Close'].iloc[-1]
            degisim = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
            
            c1.metric("Güncel Fiyat", f"{fiyat:,.2f} {para}", f"{degisim:.2f}%")
            
            # Piyasa Değeri Formatlama
            deger = info.get('marketCap', 0)
            if deger > 1e9:
                deger_str = f"{deger/1e9:.2f} Milyar"
            else:
                deger_str = f"{deger:,.0f}"
            
            c2.metric("Piyasa Değeri", f"{deger_str} {para}")
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))
            c4.metric("Ülke", tr_cevir(info.get('country', 'N/A')))

            # Grafik Bölümü (Plotly ile Daha Profesyonel)
            st.subheader(f"📈 {ticker} - {secilen_sure} Fiyat Grafiği")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', line_color='#1f77b4', name="Kapanış"))
            fig.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            
            # Alt Panel: Özet ve Haberler
            col1, col2 = st.columns([1.5, 1])
            with col1:
                st.subheader("📄 Faaliyet Özeti")
                with st.expander("Şirket Hakkında Detaylı Bilgi", expanded=True):
                    st.write(tr_cevir(info.get('longBusinessSummary', 'Bilgi yok.')))
            
            with col2:
                st.subheader("🗞️ Son Haberler & Anlaşmalar")
                # Haberleri çekme (yfinance bazen boş dönebilir, kontrol ekledik)
                haberler = hisse.news
                if haberler:
                    for haber in haberler[:6]: # İlk 6 haberi göster
                        baslik = haber.get('title', 'Haber Başlığı')
                        link = haber.get('link', '#')
                        yayin = haber.get('publisher', 'Kaynak Belirsiz')
                        st.markdown(f"🔹 **[{tr_cevir(baslik)}]({link})**")
                        st.caption(f"Kaynak: {yayin}")
                        st.write("---")
                else:
                    st.warning("Bu hisse için güncel haber akışı şu an sağlanamıyor.")
        else:
            st.error("Veri bulunamadı. Lütfen sembolün doğru olduğundan emin olun (Örn: AAPL).")

    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("⚠️ Yahoo Finance limiti doldu. Lütfen 10-15 dakika sonra tekrar deneyin.")
        else:
            st.error(f"Teknik Hata: {e}")
