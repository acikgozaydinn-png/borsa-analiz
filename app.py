import streamlit as st
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası | Pro Analiz", layout="wide")

# Kurumsal Başlık
st.markdown("<h2 style='text-align: center; color: #3d9be9;'>🏛️ Yatırım Noktası | Stratejik Analiz Terminali</h2>", unsafe_allow_html=True)
st.caption("Canlı veriler TradingView altyapısı ile sağlanmaktadır. Yatırım tavsiyesi değildir.")

# --- NASDAQ HİSSE SEÇİCİ ---
st.sidebar.header("Hisse Seçimi")
hisse_listesi = {
    "NVIDIA": "NASDAQ:NVDA",
    "APPLE": "NASDAQ:AAPL",
    "TESLA": "NASDAQ:TSLA",
    "MICROSOFT": "NASDAQ:MSFT",
    "AMAZON": "NASDAQ:AMZN",
    "META": "NASDAQ:META"
}

secilen_hisse = st.sidebar.selectbox("Analiz Edilecek Hisse:", list(hisse_listesi.keys()))
sembol = hisse_listesi[secilen_hisse]

# --- TRADINGVIEW GRAFİĞİ (HTML BİLEŞENİ) ---
# Bu kısım Python içinde TradingView'in o meşhur siyah grafiğini çalıştırır.
def tradingview_grafik(symbol):
    html_kodu = f"""
    <div class="tradingview-widget-container" style="height:600px; width:100%;">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Europe/Istanbul",
        "theme": "dark",
        "style": "1",
        "locale": "tr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    return components.html(html_kodu, height=600)

# Grafiği Ekrana Bas
tradingview_grafik(sembol)

# --- ALT PANEL (BİLGİ) ---
st.divider()
st.markdown(f"### 📊 {secilen_hisse} Teknik Analiz Görünümü")
st.write("Yukarıdaki grafik üzerinden indikatör ekleyebilir (RSI, MACD vb.) ve çizim yapabilirsiniz.")

# Sosyal Medya Hatırlatıcısı
st.sidebar.divider()
st.sidebar.info("Aydın | Yatırım Noktası Sosyal Medya hesaplarımızı takip etmeyi unutmayın.")
