import streamlit as st
import yfinance as yf
from deep_translator import GoogleTranslator
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Terminal", layout="wide")

# Hızlandırılmış Çeviri Fonksiyonu
@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A": return "Bilgi Yok"
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1200])
    except:
        return metin

st.title("🏛️ Kurumsal Şirket Analiz Terminali")

# Sembol Girişi ve Zaman Aralığı
c_input1, c_input2 = st.columns([2, 1])
ticker = c_input1.text_input("Hisse Sembolü (Örn: THYAO.IS, AAPL):", "THYAO.IS").upper()
period_map = {"1 Gün": "1d", "5 Gün": "5d", "1 Ay": "1mo", "6 Ay": "6mo", "1 Yıl": "1y", "Tümü": "max"}
secilen_sure = c_input2.selectbox("Zaman Aralığı:", list(period_map.keys()), index=4)

if ticker:
    try:
        hisse = yf.Ticker(ticker)
        df = hisse.history(period=period_map[secilen_sure])
        info = hisse.info

        if not df.empty:
            para = "₺" if ticker.endswith(".IS") else "$"
            
            # --- Üst Panel Metrikleri ---
            c1, c2, c3, c4 = st.columns(4)
            fiyat = df['Close'].iloc[-1]
            degisim = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
            c1.metric("Fiyat", f"{fiyat:,.2f} {para}", f"{degisim:.2f}%")
            
            deger = info.get('marketCap', 0)
            deger_str = f"{deger/1e9:.1f} Milyar" if deger > 1e9 else f"{deger:,.0f}"
            c2.metric("Piyasa Değeri", f"{deger_str} {para}")
            c3.metric("Sektör", tr_cevir(info.get('sector', 'N/A')))
            c4.metric("Ülke", tr_cevir(info.get('country', 'N/A')))

            # --- Google Finans Tarzı Kıyaslamalı Grafik ---
            st.subheader(f"📈 {ticker} - Analiz ve Kıyaslama")
            
            kiyas_secim = st.selectbox("Kıyaslama:", ["Yok", "Endeks (BIST 100)", "Özel Hisse"])
            fig = go.Figure()

            # Ana Hisse Çizgisi
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                fill='tozeroy', line=dict(color='#1A73E8', width=3),
                name=ticker, hovertemplate="<b>Fiyat:</b> %{y:.2f} " + para + "<extra></extra>"
            ))

            # Kıyaslama Mantığı
            if kiyas_secim != "Yok":
                k_ticker = "XU100.IS" if kiyas_secim == "Endeks (BIST 100)" else st.text_input("Hisse Gir:").upper()
                if k_ticker:
                    k_df = yf.Ticker(k_ticker).history(period=period_map[secilen_sure])
                    if not k_df.empty:
                        # Yüzdesel Kıyaslama (Google Finans gibi)
                        ana_yuzde = (df['Close'] / df['Close'].iloc[0] - 1) * 100
                        kiyas_yuzde = (k_df['Close'] / k_df['Close'].iloc[0] - 1) * 100
                        fig.data[0].y = ana_yuzde
                        fig.add_trace(go.Scatter(x=k_df.index, y=kiyas_yuzde, name=k_ticker, line=dict(dash='dot')))
                        fig.update_layout(yaxis_title="Performans (%)")

            fig.update_layout(hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
                             yaxis=dict(side="right", showgrid=True, gridcolor="#f1f3f4"))
            st.plotly_chart(fig, use_container_width=True)

            # --- Alt Panel: Haberler ---
            st.divider()
            col_ozet, col_haber = st.columns([1.5, 1])
            with col_ozet:
                st.subheader("📄 Faaliyet Özeti")
                st.write(tr_cevir(info.get('longBusinessSummary', 'Bilgi Yok')))
            with col_haber:
                st.subheader("🗞️ Haberler")
                for h in hisse.news[:5]:
                    st.markdown(f"🔹 **[{tr_cevir(h['title'])}]({h['link']})**")
                    st.write("---")

    except Exception as e:
        st.error(f"Hata: {e}")
