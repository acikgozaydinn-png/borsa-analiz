import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Pro Terminal", layout="wide")

@st.cache_data(ttl=600)
def veri_paketini_cek(sembol, sure):
    try:
        t = yf.Ticker(sembol)
        return t.history(period=sure), t.info, t.get_news()
    except: return None, {}, []

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi mevcut değil."
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except: return metin

st.title("🏛️ Yatırım Noktası | Pro Analiz Paketi")

# --- ÜST PANEL: ARAMA VE KIYASLAMA ---
c1, c2, c3, c4 = st.columns([1.2, 1.2, 0.8, 0.8])
ticker = c1.text_input("📊 Ana Hisse (Örn: NVDA):", "AAPL").upper()
kiyas_ticker = c2.text_input("➕ Kıyasla (Örn: TSLA):", "").upper()
grafik_tipi = c3.selectbox("Grafik Türü:", ["Çizgi (Kıyaslamalı)", "Mum Grafik"])
period_map = {"1G": "1d", "5G": "5d", "1A": "1mo", "1Y": "1y", "YBK": "max"}
sure = c4.selectbox("Zaman Aralığı:", list(period_map.keys()), index=2)

if ticker:
    df, info, news = veri_paketini_cek(ticker, period_map[sure])
    
    if df is not None and not df.empty:
        # --- METRİKLER VE SAYI FORMATI ---
        m1, m2, m3 = st.columns(3)
        para = "₺" if ticker.endswith(".IS") else "$"
        fiyat = df['Close'].iloc[-1]
        
        # Piyasa Değeri Formatı: 3.039,55 $
        raw_cap = info.get('marketCap', 0)
        formatted_cap = f"{raw_cap/1e9:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        m1.metric(f"{ticker} Son", f"{fiyat:,.2f} {para}")
        m2.metric("Piyasa Değeri", f"{formatted_cap} Milyar {para}")
        m3.metric("F/K Oranı", info.get('trailingPE', 'N/A'))

        # --- PROFESYONEL GRAFİK MODÜLÜ ---
        fig = go.Figure()
        ana_perf = (df['Close'] / df['Close'].iloc[0] - 1) * 100
        
        if grafik_tipi == "Mum Grafik" and not kiyas_ticker:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=ticker), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='silver'), row=2, col=1)
        else:
            fig.add_trace(go.Scatter(x=df.index, y=ana_perf, name=f"{ticker} (%)", line=dict(color='#1A73E8', width=3)))
            if kiyas_ticker:
                k_df, _, _ = veri_paketini_cek(kiyas_ticker, period_map[sure])
                if k_df is not None and not k_df.empty:
                    k_perf = (k_df['Close'] / k_df['Close'].iloc[0] - 1) * 100
                    fig.add_trace(go.Scatter(x=k_df.index, y=k_perf, name=f"{kiyas_ticker} (%)", line=dict(color='#F9AB00', width=3)))

        fig.update_layout(hovermode="x unified", height=550, template="plotly_white", yaxis=dict(side="right", ticksuffix="%"))
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # --- KIYASLAMA VERİSİ VE ŞİRKET BİLGİSİ ---
        st.divider()
        col_bilgi, col_haber = st.columns([1.5, 1])
        
        with col_bilgi:
            st.subheader(f"📈 {sure} Performans Özeti")
            st.success(f"**{ticker}** bu sürede **%{ana_perf.iloc[-1]:.2f}** kazandırdı.")
            if kiyas_ticker and 'k_perf' in locals():
                st.warning(f"**{kiyas_ticker}** bu sürede **%{k_perf.iloc[-1]:.2f}** kazandırdı.")
            
            st.subheader("🏢 Şirket Profili")
            st.write(tr_cevir(info.get('longBusinessSummary') or info.get('description')))

        with col_haber:
            st.subheader("🗞️ Haberler")
            if news:
                for n in news[:5]:
                    st.markdown(f"🔗 **[{tr_cevir(n.get('title'))}]({n.get('link')})**")
                    st.write("---")
            else: st.info("Şu an haber çekilemiyor.")
