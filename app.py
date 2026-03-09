import streamlit as st
import streamlit.components.v1 as components

# 1. Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası | Stratejik Terminal", layout="wide")

# 2. Kurumsal Stil (Koyu Tema)
st.markdown("""
    <style>
    .main { background-color: #060d18; }
    div.stButton > button {
        width: 100%;
        background-color: #0d1f38;
        color: #3d9be9;
        border: 1px solid #1a3050;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #3d9be9;
        color: white;
        border-color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Başlık Alanı
st.markdown("<h2 style='text-align: center; color: white;'>⬡ STRATEJİK ANALİZ TERMİNALİ</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4a6a8a;'>Aydın | Yatırım Noktası — Canlı Küresel Veri Ekranı</p>", unsafe_allow_html=True)

# 4. Kategori ve Sembol Tanımlamaları (Hepsi Burada)
kategoriler = {
    "🇺🇸 NASDAQ DEVLERİ": ["NASDAQ:NVDA", "NASDAQ:AAPL", "NASDAQ:TSLA", "NASDAQ:MSFT", "NASDAQ:AMZN"],
    "🟡 EMTİA & DÖVİZ": ["TVC:GOLD", "TVC:SILVER", "OANDA:USDTRY", "OANDA:EURUSD"],
    "₿ KRİPTO PARA": ["BITSTAMP:BTCUSD", "BITSTAMP:ETHUSD", "BINANCE:SOLUSD"]
}

# 5. Butonlarla Seçim Paneli
if 'secili_sembol' not in st.session_state:
    st.session_state.secili_sembol = "NASDAQ:NVDA"

st.write("### 🔍 İzleme Listesi")
for kat_isim, semboller in kategoriler.items():
    st.markdown(f"**{kat_isim}**")
    cols = st.columns(len(semboller))
    for i, s in enumerate(semboller):
        with cols[i]:
            # Buton ismi sembolün kısa hali olsun (Örn: NVDA)
            buton_adi = s.split(":")[-1]
            if st.button(buton_adi, key=s):
                st.session_state.secili_sembol = s

st.divider()

# 6. TRADINGVIEW ÜCRETSİZ GRAFİK MOTORU (HTML)
def render_tv_chart(symbol):
    tv_html = f"""
    <div style="height:620px;">
      <div id="tv_chart_container" style="height:100%;"></div>
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
        "toolbar_bg": "#0a1628",
        "enable_publishing": false,
        "withdateranges": true,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "show_popup_button": true,
        "popup_width": "1000",
        "popup_height": "650",
        "container_id": "tv_chart_container"
      }});
      </script>
    </div>
    """
    return components.html(tv_html, height=630)

# Seçilen grafiği ekrana bas
render_tv_chart(st.session_state.secili_sembol)

# 7. Alt Bilgi (Footer)
st.divider()
st.markdown("<p style='text-align: center; color: #5a7a9a; font-size: 12px;'>Veriler TradingView üzerinden ücretsiz lisansla sağlanmaktadır. Yatırım tavsiyesi değildir.</p>", unsafe_allow_html=True)
