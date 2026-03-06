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

try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    info = stock.info

    # Özet Veriler
    c1, c2 = st.columns(2)
    c1.metric("Güncel Fiyat", f"${info.get('currentPrice', 'N/A')}")
    c2.metric("Piyasa Değeri", f"{info.get('marketCap', 'N/A'):,}")

    # Grafik
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    st.plotly_chart(fig, use_container_width=True)

    # Şirket Bilgisi
    st.subheader("🏢 Şirket Özeti")
    st.write(info.get('longBusinessSummary', "Bilgi bulunamadı."))

except Exception as e:
    st.error("Veri çekilemedi, lütfen sembolü kontrol edin.")
