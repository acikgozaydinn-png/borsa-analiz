import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Pro Analiz", layout="wide")

@st.cache_data(ttl=600)
def veri_hazirla(semboller, sure):
    paket = {}
    for s in semboller:
        try:
            t = yf.Ticker(s.strip().upper())
            hist = t.history(period=sure)
            if not hist.empty:
                paket[s.strip().upper()] = {"df": hist, "info": t.info, "news": t.get_news()}
        except: continue
    return paket

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi mevcut değil."
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except: return metin

st.title("🏛️ Yatırım Noktası | Stratejik Analiz Terminali")

# --- ÜST PANEL: ÇOKLU GİRİŞ VE AYARLAR ---
c1, c2, c3 = st.columns([2.5, 0.8, 0.7])
# SİZİN İSTEDİĞİNİZ: Çoklu Kıyaslama (Virgül ile ayırın)
girdi = c1.text_input("📊 Hisseleri Kıyaslayın (Örn: AAPL, TSLA, NVDA, THYAO.IS):", "AAPL, NVDA").upper()
sembol_listesi = [s.strip() for s in girdi.split(",")]

grafik_tipi = c2.selectbox("Grafik Türü:", ["Çizgi (Kıyaslamalı)", "Mum Grafik (Tekli)"])
period_map = {"1G": "1d", "5G": "5d", "1A": "1mo", "1Y": "1y", "YBK": "max"}
sure = c3.selectbox("Zaman Aralığı:", list(period_map.keys()), index=2)

if sembol_listesi:
    tum_paket = veri_hazirla(sembol_listesi, period_map[sure])
    
    if tum_paket:
        # --- ÜST METRİKLER ---
        metrik_cols = st.columns(len(tum_paket))
        for i, (s, veri) in enumerate(tum_paket.items()):
            df = veri['df']
            fiyat = df['Close'].iloc[-1]
            perf = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
            para = "₺" if s.endswith(".IS") else "$"
            with metrik_cols[i]:
                st.metric(s, f"{fiyat:,.2f} {para}", f"{perf:.2f}%")

        # --- PROFESYONEL GRAFİK MODÜLÜ ---
        fig = go.Figure()
        
        if grafik_tipi == "Mum Grafik (Tekli)":
            # Tekli odaklanma (Listenin ilk hissesi)
            ilk_s = sembol_listesi[0]
            df = tum_paket[ilk_s]['df']
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=ilk_s), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='silver'), row=2, col=1)
            fig.update_layout(xaxis_rangeslider_visible=False)
        else:
            # Çoklu Kıyaslama (Yüzdesel)
            for s, veri in tum_paket.items():
                df = veri['df']
                yuzde_perf = (df['Close'] / df['Close'].iloc[0] - 1) * 100
                fig.add_trace(go.Scatter(x=df.index, y=yuzde_perf, name=f"{s} (%)", line=dict(width=2.5)))

        fig.update_layout(hovermode="x unified", height=550, template="plotly_white", yaxes=dict(side="right", ticksuffix="%" if grafik_tipi != "Mum Grafik (Tekli)" else ""))
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # --- ŞİRKET BİLGİLERİ VE HABERLER (İlk Hisse Odaklı) ---
        st.divider()
        ana_s = sembol_listesi[0]
        info = tum_paket[ana_s]['info']
        news = tum_paket[ana_s]['news']
        
        col_bilgi, col_haber = st.columns([1.5, 1])
        with col_bilgi:
            st.subheader(f"🏢 {ana_s} Şirket Künyesi")
            # Piyasa Değeri Formatı: 3.039,55 $
            raw_cap = info.get('marketCap', 0)
            formatted_cap = f"{raw_cap/1e9:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.write(f"**Piyasa Değeri:** {formatted_cap} Milyar | **F/K:** {info.get('trailingPE', 'N/A')}")
            st.write(tr_cevir(info.get('longBusinessSummary')))
            
        with col_haber:
            st.subheader("🗞️ Haber Akışı")
            if news:
                for n in news[:5]:
                    st.markdown(f"🔗 **[{tr_cevir(n.get('title'))}]({n.get('link')})**")
                    st.write("---")
            else: st.info("Haberler şu an yüklenemiyor.")
