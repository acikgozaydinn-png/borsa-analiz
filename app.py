import streamlit as st
import streamlit.components.v1 as components

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Aydın | Yatırım Noktası Terminal", layout="wide")

# 2. Kurumsal CSS Tasarımı
st.markdown("""
    <style>
    .main { background-color: #060d18; }
    /* Buton Tasarımları */
    div.stButton > button {
        width: 100%;
        background-color: #0d1f38;
        color: #3d9be9;
        border: 1px solid #1a3050;
        font-family: 'Share Tech Mono', monospace;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #3d9be9;
        color: white;
        border-color: #3d9be9;
    }
    /* Sosyal Medya Butonları */
    .social-btn {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 8px;
        color: white;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        transition: 0.3s;
    }
    .social-btn:hover { opacity: 0.8; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# 3. Başlık ve Logo
st.markdown("<h2 style='text-align: center; color: white; letter-spacing: 2px;'>⬡ STRATEJİK ANALİZ TERMİNALİ</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4a6a8a; font-family: monospace;'>Aydın | Yatırım Noktası — Canlı Piyasa Verileri</p>", unsafe_allow_html=True)

# 4. Kategori ve Sembol Yönetimi
kategoriler = {
    "🇺🇸 NASDAQ DEVLERİ": ["NASDAQ:NVDA", "NASDAQ:AAPL", "NASDAQ:TSLA", "NASDAQ:MSFT", "NASDAQ:AMZN"],
    "🟡 EMTİA & DÖVİZ": ["TVC:GOLD", "TVC:SILVER", "OANDA:USDTRY", "OANDA:EURUSD"],
    "₿ KRİPTO PARA": ["BITSTAMP:BTCUSD", "BITSTAMP:ETHUSD"]
}

if 'active_sym' not in st.session_state:
    st.session_state.active_sym = "NASDAQ:NVDA"

# 5. Piyasa Seçim Paneli
st.write("### 🔍 Piyasa İzleme Listesi")
for kat_adi, semboller in kategoriler.items():
    st.markdown(f"**{kat_adi}**")
    cols = st.columns(len(semboller))
    for i, s in enumerate(semboller):
        with cols[i]:
            label = s.split(":")[-1]
            if st.button(label, key=s):
                st.session_state.active_sym = s

st.divider()

# 6. TRADINGVIEW WIDGET (ÜCRETSİZ)
def render_chart(symbol):
    tv_html = f"""
    <div style="height:600px;">
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
        "container_id": "tv_chart_container"
      }});
      </script>
    </div>
    """
    return components.html(tv_html, height=620)

render_chart(st.session_state.active_sym)

st.divider()

# 7. SORUMLULUK REDDİ (DISCLAIMER)
st.markdown("""
<div style="background: rgba(255,160,0,0.1); border: 1px solid #f0b429; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
    <h4 style="color: #f0b429; margin-top: 0;">⚠️ Sorumluluk Reddi</h4>
    <p style="color: #d1d5db; font-size: 14px; line-height: 1.6;">
        Bu terminalde sunulan veriler ve analizler yalnızca <b>bilgilendirme amaçlıdır</b>. 
        Aydın | Yatırım Noktası tarafından paylaşılan hiçbir içerik yatırım tavsiyesi niteliği taşımaz. 
        Finansal kararlarınızı vermeden önce lisanslı bir danışmana başvurmanız önerilir. 
        Veriler <b>TradingView</b> üzerinden ücretsiz lisansla sağlanmaktadır.
    </p>
</div>
""", unsafe_allow_html=True)

# 8. SOSYAL MEDYA PANELİ
st.markdown("""
<div style="text-align: center; background: #0d1f38; padding: 30px; border-radius: 15px; border: 1px solid #1a3050;">
    <h3 style="color: white; margin-bottom: 20px;">📊 Analizlerimizi Kaçırmayın!</h3>
    <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;">
        <a href="https://www.youtube.com/@AydinYatirimNoktasi" class="social-btn" style="background: #FF0000;">YouTube</a>
        <a href="https://x.com/AydnAkgz9" class="social-btn" style="background: #000000;">X (Twitter)</a>
        <a href="https://www.instagram.com/AYDINACIKGOZ9" class="social-btn" style="background: #E1306C;">Instagram</a>
        <a href="https://linktr.ee/acikgozaydinn" class="social-btn" style="background: #43e55e; color: black;">Linktree</a>
        <a href="https://www.tiktok.com/@yatirim.noktasi" class="social-btn" style="background: #010101;">TikTok</a>
    </div>
    <p style="color: #4a6a8a; font-size: 12px; margin-top: 25px;">
        © 2026 <b>Aydın | Yatırım Noktası</b><br>
        Anadolu Üniversitesi İşletme Mezunu · Finansal Okuryazarlık
    </p>
</div>
""", unsafe_allow_html=True)
