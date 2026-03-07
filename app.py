import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Analiz", layout="wide")

@st.cache_data(ttl=900)
def veri_cek(sembol, sure):
    try:
        t = yf.Ticker(sembol)
        return t.history(period=sure), t.info, t.get_news()
    except:
        return None, None, None

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "Bilgi Yok": return metin
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except: return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

# --- AKILLI ARAMA VE SEÇİM BÖLÜMÜ ---
# Kullanıcıya hem hazır liste sunuyoruz hem de manuel yazma imkanı
populer_hisseler = ["AAPL", "NVDA", "TSLA", "THYAO.IS", "SASA.IS", "TUPRS.IS", "BTC-USD"]

c1, c2 = st.columns([1, 3])

secim = c1.selectbox("Hızlı Seç:", ["Arama Yap..."] + populer_hisseler)
manuel_arama = c2.text_input("Veya Hisse Kodu Yazın (Örn: MSFT, ASELS.IS):", "")

# Hangi kutu doluysa onu baz alıyoruz
if manuel_arama:
    ticker = manuel_arama.upper()
elif secim != "Arama Yap...":
    ticker = secim
else:
    ticker = "AAPL" # Varsayılan açılış hissesi

# Zaman Butonları
period_map = {"1 Gün": "1d", "5 Gün": "5d", "1 Ay": "1mo", "1 Yıl": "1y", "Tümü": "max"}
secilen_sure = st.select_slider("Zaman Aralığı:", options=list(period_map.keys()), value="1 Ay")

if ticker:
    df, info, haberler = veri_cek(ticker, period_map[secilen_sure])
    
    if df is not None and not df.empty:
        # Fiyat ve Grafik
        fiyat = df['Close'].iloc[-1]
        st.metric(label=f"{ticker} Son Fiyat", value=f"{fiyat:,.2f}", 
                  delta=f"{((df['Close'].iloc[-1]/df['Close'].iloc[0])-1)*100:.2f}%")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', 
                                 line=dict(color='#1A73E8', width=2), name=ticker))

        fig.update_layout(
            dragmode='pan', # Grafiği el ile kaydırma
            hovermode="x unified",
            plot_bgcolor="white",
            height=450,
            xaxis=dict(rangeslider=dict(visible=True), type="date", showgrid=False),
            yaxis=dict(side="right", showgrid=True, gridcolor="#f1f3f4")
        )
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # Haberler
        st.divider()
        st.subheader("🗞️ Güncel Gelişmeler")
        if haberler:
            for h in haberler[:5]:
                st.markdown(f"🔹 **[{tr_cevir(h.get('title'))}]({h.get('link')})**")
    else:
        st.warning("Veri bulunamadı. Lütfen sembolü kontrol edin.")
