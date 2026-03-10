import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Aydın | Yatırım Noktası", layout="wide")

st.title("📈 Kurumsal Şirket Analiz Terminali")
st.write("Canlı piyasa verileri — www.aydinyatirimnoktasi.com")

# Popüler hisseler
POPULER = {
    "🇺🇸 Nasdaq/NYSE": {
        "NVIDIA": "NVDA",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Tesla": "TSLA",
        "Amazon": "AMZN",
        "Meta": "META",
        "Google": "GOOGL",
    },
    "🇹🇷 BIST": {
        "THYAO (THY)": "THYAO.IS",
        "GARAN (Garanti)": "GARAN.IS",
        "ASELS (Aselsan)": "ASELS.IS",
        "KCHOL (Koç)": "KCHOL.IS",
        "SISE (Şişecam)": "SISE.IS",
        "EREGL (Ereğli)": "EREGL.IS",
        "BIMAS (BİM)": "BIMAS.IS",
    },
    "🛢️ Emtia / ETF": {
        "Ham Petrol (WTI)": "CL=F",
        "Brent Petrol": "BZ=F",
        "Altın": "GC=F",
        "Gümüş": "SI=F",
        "Doğalgaz": "NG=F",
        "S&P 500 ETF (SPY)": "SPY",
        "Nasdaq ETF (QQQ)": "QQQ",
        "Yarı İletken (SMH)": "SMH",
        "Enerji ETF (XLE)": "XLE",
        "Altın ETF (GLD)": "GLD",
    },
    "💱 Döviz": {
        "USD/TRY": "USDTRY=X",
        "EUR/TRY": "EURTRY=X",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "BTC/USD": "BTC-USD",
        "ETH/USD": "ETH-USD",
    }
}

# Sidebar
st.sidebar.header("🔍 Hisse Seçimi")
kategori = st.sidebar.selectbox("Kategori", list(POPULER.keys()))
secim = st.sidebar.selectbox("Hisse / Varlık", list(POPULER[kategori].keys()))
ticker_symbol = POPULER[kategori][secim]

st.sidebar.markdown("---")
st.sidebar.write("**Ya da manuel gir:**")
manuel = st.sidebar.text_input("Ticker (örn: NVDA, THYAO.IS)", "")
if manuel:
    ticker_symbol = manuel.upper()

period = st.sidebar.selectbox("Dönem", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
period_labels = {"1mo":"1 Ay","3mo":"3 Ay","6mo":"6 Ay","1y":"1 Yıl","2y":"2 Yıl","5y":"5 Yıl"}

st.sidebar.markdown("---")
st.sidebar.write("📊 **Aydın | Yatırım Noktası**")
st.sidebar.write("[aydinyatirimnoktasi.com](https://www.aydinyatirimnoktasi.com)")

# Veri çek
try:
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(period=period)
    info = stock.info

    if df.empty:
        st.error(f"'{ticker_symbol}' için veri bulunamadı. Ticker kodunu kontrol edin.")
        st.stop()

    # Özet metrikler
    st.subheader(f"📊 {info.get('longName', ticker_symbol)} — {period_labels.get(period, period)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    guncel = info.get('currentPrice') or info.get('regularMarketPrice') or df['Close'].iloc[-1]
    onceki = info.get('previousClose') or df['Close'].iloc[-2]
    degisim = ((guncel - onceki) / onceki * 100) if onceki else 0
    
    col1.metric("Güncel Fiyat", f"{guncel:.2f}", f"{degisim:+.2f}%")
    col2.metric("En Yüksek (52H)", f"{info.get('fiftyTwoWeekHigh', df['High'].max()):.2f}")
    col3.metric("En Düşük (52H)", f"{info.get('fiftyTwoWeekLow', df['Low'].min()):.2f}")
    
    market_cap = info.get('marketCap')
    if market_cap:
        if market_cap >= 1e12:
            cap_str = f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            cap_str = f"${market_cap/1e9:.2f}B"
        else:
            cap_str = f"${market_cap/1e6:.2f}M"
        col4.metric("Piyasa Değeri", cap_str)
    else:
        col4.metric("Hacim", f"{df['Volume'].iloc[-1]:,.0f}")

    # Mum grafik
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#22c55e',
        decreasing_line_color='#ef4444'
    )])
    fig.update_layout(
        title=f"{ticker_symbol} — {period_labels.get(period, period)} Grafik",
        xaxis_title="Tarih",
        yaxis_title="Fiyat",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Şirket bilgisi
    aciklama = info.get('longBusinessSummary')
    if aciklama:
        st.subheader("🏢 Şirket Hakkında")
        st.write(aciklama[:800] + "..." if len(aciklama) > 800 else aciklama)

    # Temel veriler
    st.subheader("📋 Temel Veriler")
    col_a, col_b = st.columns(2)
    veriler = {
        "Sektör": info.get('sector', 'N/A'),
        "Endüstri": info.get('industry', 'N/A'),
        "Ülke": info.get('country', 'N/A'),
        "Çalışan Sayısı": f"{info.get('fullTimeEmployees', 'N/A'):,}" if isinstance(info.get('fullTimeEmployees'), int) else 'N/A',
        "F/K Oranı": info.get('trailingPE', 'N/A'),
        "Temettü Getirisi": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A',
    }
    items = list(veriler.items())
    for i, (k, v) in enumerate(items[:3]):
        col_a.write(f"**{k}:** {v}")
    for i, (k, v) in enumerate(items[3:]):
        col_b.write(f"**{k}:** {v}")

except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.info("Lütfen farklı bir hisse kodu deneyin veya internet bağlantınızı kontrol edin.")

st.markdown("---")
st.markdown("⚠️ *Bu uygulama yalnızca bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.* | **Aydın | Yatırım Noktası**")
