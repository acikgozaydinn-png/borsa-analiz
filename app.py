 import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Nasdaq & BIST", layout="wide")

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except: return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

# Sembol ve Zaman Seçimi
c1, c2 = st.columns([3, 1])
# Kullanıcıya Nasdaq için ipucu veriyoruz
ticker = c1.text_input("Hisse Sembolü (BIST için: THYAO.IS | Nasdaq için: AAPL, TSLA, NVDA):", "AAPL").upper()
period_map = {"1 Gün": "1d", "5 Gün": "5d", "1 Ay": "1mo", "1 Yıl": "1y", "Tümü": "max"}
secilen_sure = c2.selectbox("Zaman Aralığı:", list(period_map.keys()), index=2)

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        df = hisse.history(period=period_map[secilen_sure])
        
        if not df.empty:
            # --- GOOGLE FINANS TARZI KIYASLAMA ---
            st.markdown("### 🔍 Karşılaştırma Ekle")
            kiyas_ticker = st.text_input("Kıyaslanacak Sembol (Örn: QQQ, SPY veya NVDA):", "").upper()
            
            fig = go.Figure()
            # Performans Hesaplama (%)
            ana_perf = (df['Close'] / df['Close'].iloc[0] - 1) * 100
            fig.add_trace(go.Scatter(x=df.index, y=ana_perf, name=f"{ticker} (%)", line=dict(color='#1A73E8', width=2.5)))

            if kiyas_ticker:
                k_df = yf.Ticker(kiyas_ticker).history(period=period_map[secilen_sure])
                if not k_df.empty:
                    k_perf = (k_df['Close'] / k_df['Close'].iloc[0] - 1) * 100
                    fig.add_trace(go.Scatter(x=k_df.index, y=k_perf, name=f"{kiyas_ticker} (%)", line=dict(color='#F9AB00', width=2.5)))

            # Tasarım Ayarları
            fig.update_layout(
                hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white", height=400,
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(side="right", ticksuffix="%", gridcolor="#f1f3f4", title="Performans")
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- HABERLER VE ÖZET ---
            st.divider()
            info = hisse.info
            col_a, col_b = st.columns([1.5, 1])
            
            with col_a:
                st.subheader(f"📄 {ticker} Şirket Özeti")
                # Nasdaq hisselerinde özet genelde doludur
                st.write(tr_cevir(info.get('longBusinessSummary', 'Özet bulunamadı.')))
            
            with col_b:
                st.subheader("🗞️ Nasdaq Haber Akışı")
                # get_news() Nasdaq hisselerinde çok iyi çalışır
                haberler = hisse.get_news()
                if haberler:
                    for h in haberler[:5]:
                        t_baslik = tr_cevir(h.get('title'))
                        link = h.get('link')
                        st.markdown(f"🔹 **[{t_baslik}]({link})**")
                        st.write("---")
                else:
                    st.warning("Haber akışı şu an teknik nedenlerle yüklenemiyor.")

    except Exception as e:
        st.error(f"Veri hatası: {e}")
                       
