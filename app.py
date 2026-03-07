import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Terminal", layout="wide")

# 1. ÖNBELLEK (CACHE) MEKANİZMASI: Yahoo'yu yormadan veriyi hafızaya alır
@st.cache_data(ttl=900) # 15 dakika boyunca aynı hisse için Yahoo'ya gitmez
def veri_cek(sembol, sure):
    try:
        data = yf.Ticker(sembol)
        return data.history(period=sure), data.info, data.get_news()
    except:
        return None, None, None

@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try: return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except: return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

# Sembol ve Zaman Seçimi
c1, c2 = st.columns([3, 1])
ticker = c1.text_input("Hisse Sembolü (Örn: AAPL, NVDA, THYAO.IS):", "AAPL").upper()
period_map = {"1 Gün": "1d", "5 Gün": "5d", "1 Ay": "1mo", "1 Yıl": "1y", "Tümü": "max"}
secilen_sure = c2.selectbox("Zaman Aralığı:", list(period_map.keys()), index=2)

if ticker:
    # Veriyi yeni "Korumalı" fonksiyonla çekiyoruz
    df, info, haberler = veri_cek(ticker, period_map[secilen_sure])
    
    if df is not None and not df.empty:
        st.markdown("### 🔍 Karşılaştırma Ekle")
        kiyas_ticker = st.text_input("Kıyaslanacak Sembol (Örn: QQQ, TUPRS.IS):", "").upper()
        
        fig = go.Figure()
        # Performans (%) - Google Finans Tarzı
        ana_perf = (df['Close'] / df['Close'].iloc[0] - 1) * 100
        fig.add_trace(go.Scatter(x=df.index, y=ana_perf, name=f"{ticker} (%)", line=dict(color='#1A73E8', width=2.5)))

        if kiyas_ticker:
            k_df, _, _ = veri_cek(kiyas_ticker, period_map[secilen_sure])
            if k_df is not None and not k_df.empty:
                k_perf = (k_df['Close'] / k_df['Close'].iloc[0] - 1) * 100
                fig.add_trace(go.Scatter(x=k_df.index, y=k_perf, name=f"{kiyas_ticker} (%)", line=dict(color='#F9AB00', width=2.5)))

        fig.update_layout(
            hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white", height=450,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(side="right", ticksuffix="%", gridcolor="#f1f3f4")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        col_a, col_b = st.columns([1.5, 1])
        with col_a:
            st.subheader(f"📄 {ticker} Şirket Özeti")
            st.write(tr_cevir(info.get('longBusinessSummary', 'Özet bulunamadı.')))
        with col_b:
            st.subheader("🗞️ Haber Akışı")
            if haberler:
                for h in haberler[:5]:
                    st.markdown(f"🔹 **[{tr_cevir(h.get('title'))}]({h.get('link')})**")
                    st.write("---")
            else:
                st.info("Haber akışı şu an Yahoo kısıtlaması nedeniyle yüklenemiyor.")
    else:
        st.warning("Veri çekilemedi. Lütfen 15 dakika bekleyin veya sembolü kontrol edin.")
