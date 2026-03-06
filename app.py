import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Aydın Yatırım Noktası", layout="wide")
st.title("📈 Nasdaq Teknoloji Analiz Portalı")
st.write("Sistem Canlıda: www.aydinyatirimnoktasi.com")

# Yan Menü
ticker = st.sidebar.text_input("Hisse Kodu (Örn: NVDA, AAPL)", "NVDA").upper()
sorgula_butonu = st.sidebar.button("Analiz Et")

try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    info = stock.info

    # Özet Veriler
    c1, c2 = st.columns(2)
    current_price = info.get('regularMarketPrice') or info.get('currentPrice') or 0
    market_cap = info.get('marketCap', 0)
    
    c1.metric("Güncel Fiyat", f"${current_price:,.2f}")
    c2.metric("Piyasa Değeri", f"${market_cap:,.0f}")

    # Grafik
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'])])
    st.plotly_chart(fig, use_container_width=True)

    # Şirket Bilgisi
    st.write(f"### {ticker} Şirket Özeti")
    if ticker == "NVDA":
        st.info("""
        NVIDIA, yapay zeka (AI) altyapısı ve grafik işlemcileri konusunda dünya lideridir. 
        Oyun dünyası için GeForce GPU'lar, veri merkezleri için yüksek performanslı çipler 
        ve otonom araçlar için çözümler üretmektedir. Merkezi Santa Clara'dadır.
        """)
    else:
        st.write(info.get('longBusinessSummary', 'Bilgi bulunamadı.'))

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
