import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Pro Terminal", layout="wide")

@st.cache_data(ttl=600)
def veri_getir(sembol, sure):
    try:
        t = yf.Ticker(sembol)
        return t.history(period=sure), t.info, t.get_news()
    except: return None, {}, []

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi mevcut değil."
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1500])
    except: return metin

st.title("📊 Yatırım Noktası | Stratejik Analiz Terminali")

# --- ÜST PANEL ---
c1, c2, c3 = st.columns([1, 2, 1])
populer = ["AAPL", "NVDA", "TSLA", "THYAO.IS", "TUPRS.IS", "EREGL.IS"]
secim = c1.selectbox("Hızlı Erişim:", ["Seçiniz..."] + populer)
manuel = c2.text_input("Hisse/Borsa Ara (Örn: MSFT, SASA.IS):", "").upper()
ticker = manuel if manuel else (secim if secim != "Seçiniz..." else "AAPL")
period_map = {"1G": "1d", "5G": "5d", "1A": "1mo", "1Y": "1y", "YBK": "max"}
sure = c3.selectbox("Zaman Aralığı:", list(period_map.keys()), index=2)

if ticker:
    df, info, news = veri_getir(ticker, period_map[sure])
    
    if df is not None and not df.empty:
        # --- ŞİRKET ÖZET METRİKLERİ ---
        m1, m2, m3, m4 = st.columns(4)
        para = "₺" if ticker.endswith(".IS") else "$"
        fiyat = df['Close'].iloc[-1]
        degisim = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
        
        m1.metric("Son Fiyat", f"{fiyat:,.2f} {para}", f"{degisim:.2f}%")
        m2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f} Milyar {para}")
        m3.metric("F/K Oranı", info.get('trailingPE', 'N/A'))
        m4.metric("Temettü Verimi", f"%{info.get('dividendYield', 0)*100:.2f}" if info.get('dividendYield') else "N/A")

        # --- TRADINGVIEW TARZI MUM GRAFİK ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='rgba(0,0,255,0.3)'), row=2, col=1)
        
        fig.update_layout(height=500, template="plotly_white", xaxis_rangeslider_visible=False, showlegend=False)
        fig.update_yaxes(side="right")
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # --- "BİLGİ BULUNSA İYİ OLUR" DEDİĞİNİZ BÖLÜM ---
        st.divider()
        col_sol, col_sag = st.columns([1.5, 1])
        
        with col_sol:
            st.subheader("🏢 Şirket Profili & Strateji")
            with st.expander("Detaylı Açıklamayı Oku", expanded=True):
                st.write(tr_cevir(info.get('longBusinessSummary')))
            
            # Ekstra Bilgi Tablosu
            st.markdown("### 📊 Temel Veriler")
            st.table({
                "Sektör": [tr_cevir(info.get('sector'))],
                "Çalışan Sayısı": [info.get('fullTimeEmployees', 'N/A')],
                "52 Haftalık Zirve": [f"{info.get('fiftyTwoWeekHigh', 0):,.2f} {para}"],
                "52 Haftalık Dip": [f"{info.get('fiftyTwoWeekLow', 0):,.2f} {para}"]
            })

        with col_sag:
            st.subheader("🗞️ Global Haber Akışı")
            if news:
                for n in news[:6]:
                    st.markdown(f"📌 **[{tr_cevir(n.get('title'))}]({n.get('link')})**")
                    st.caption(f"Kaynak: {n.get('publisher')}")
                    st.write("---")
            else:
                st.info("Bu şirket için güncel haber bulunamadı.")
