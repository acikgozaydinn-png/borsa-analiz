import streamlit as st
import yfinance as yf

# Sayfa Yapısı
st.set_page_config(page_title="Borsa Analiz", layout="wide")

st.title("📈 Temel Borsa Takip Aracı")

# Kullanıcıdan Sembol Alma
ticker = st.text_input("Hisse Sembolü (Örn: THYAO.IS veya AAPL):", "THYAO.IS")

if ticker:
    try:
        # Veriyi Çekme
        data = yf.Ticker(ticker)
        df = data.history(period="1y")
        
        if not df.empty:
            # Fiyat Bilgisi
            current_price = df['Close'].iloc[-1]
            st.metric(label=f"{ticker} Güncel Fiyat", value=f"{current_price:.2f}")
            
            # Grafik
            st.subheader("Son 1 Yıllık Grafik")
            st.line_chart(df['Close'])
            
            # Şirket Bilgisi
            st.subheader("Şirket Bilgileri")
            st.write(data.info.get('longBusinessSummary', 'Bilgi bulunamadı.'))
        else:
            st.error("Sembol bulunamadı, lütfen kontrol edin.")
            
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

            
