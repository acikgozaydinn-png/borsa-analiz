import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Yatırım Noktası - Karşılaştırma", layout="wide")

@st.cache_data(ttl=600)
def veri_getir(sembol, sure):
    try:
        t = yf.Ticker(sembol)
        return t.history(period=sure), t.info, t.get_news()
    except: return None, {}, []

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi mevcut değil."
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except: return metin

st.title("🏛️ Yatırım Noktası | Profesyonel Kıyaslama Terminali")

# --- ÜST PANEL ---
c1, c2, c3, c4 = st.columns([1.2, 1.2, 0.8, 0.8])
ticker = c1.text_input("📊 Ana Hisse (Örn: NVDA):", "AAPL").upper()
kiyas_ticker = c2.text_input("➕ Kıyaslanacak (Örn: TSLA):", "").upper()
grafik_tipi = c3.selectbox("Grafik Türü:", ["Çizgi (Kıyaslama)", "Mum Grafik"])
period_map = {"1G": "1d", "5G": "5d", "1A": "1mo", "1Y": "1y", "YBK": "max"}
sure = c4.selectbox("Zaman Aralığı:", list(period_map.keys()), index=2)

if ticker:
    df, info, news = veri_getir(ticker, period_map[sure])
    
    if df is not None and not df.empty:
        # Piyasa Değeri Formatı (3.039,55 $)
        raw_cap = info.get('marketCap', 0)
        formatted_cap = f"{raw_cap/1e9:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.caption(f"**{ticker}** Piyasa Değeri: {formatted_cap} Milyar | F/K: {info.get('trailingPE', 'N/A')}")

        # --- GRAFİK YAPISI ---
        fig = go.Figure()
        ana_perf = (df['Close'] / df['Close'].iloc[0] - 1) * 100
        
        if grafik_tipi == "Mum Grafik" and not kiyas_ticker:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=ticker), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='silver'), row=2, col=1)
            fig.update_layout(xaxis_rangeslider_visible=False)
        else:
            fig.add_trace(go.Scatter(x=df.index, y=ana_perf, name=f"{ticker} (%)", line=dict(color='#1A73E8', width=3)))
            if kiyas_ticker:
                k_df, _, _ = veri_getir(kiyas_ticker, period_map[sure])
                if k_df is not None and not k_df.empty:
                    k_perf = (k_df['Close'] / k_df['Close'].iloc[0] - 1) * 100
                    fig.add_trace(go.Scatter(x=k_df.index, y=k_perf, name=f"{kiyas_ticker} (%)", line=dict(color='#F9AB00', width=3)))

        fig.update_layout(hovermode="x unified", height=500, template="plotly_white", yaxis=dict(side="right", ticksuffix="%"))
        st.plotly_chart(fig, use_container_width=True)

        # --- SİZİN İSTEDİĞİNİZ: ZAMANA GÖRE KIYAS TABLOSU ---
        st.subheader(f"📈 {sure} Periyodundaki Performans Özeti")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**{ticker}** başlangıçtan bu yana: **%{ana_perf.iloc[-1]:.2f}** getiri sağladı.")
        
        if kiyas_ticker and 'k_perf' in locals():
            with col2:
                fark = ana_perf.iloc[-1] - k_perf.iloc[-1]
                durum = "daha iyi" if fark > 0 else "daha düşük"
                st.warning(f"**{kiyas_ticker}** başlangıçtan bu yana: **%{k_perf.iloc[-1]:.2f}** getiri sağladı.")
                st.write(f"👉 {ticker}, {kiyas_ticker} hissesine göre **%{abs(fark):.2f}** {durum} performans sergiledi.")

        # --- HABERLER ---
        st.divider()
        st.subheader("🗞️ Güncel Gelişmeler")
        if news:
            for n in news[:4]:
                st.markdown(f"🔹 **[{tr_cevir(n.get('title'))}]({n.get('link')})**")
