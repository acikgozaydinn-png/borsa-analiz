import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

try:
    from deep_translator import GoogleTranslator
    CEVIRI_AKTIF = True
except ImportError:
    CEVIRI_AKTIF = False

# Sayfa Ayarları
st.set_page_config(page_title="Yatırım Noktası - Pro Analiz", layout="wide")


@st.cache_data(ttl=600)
def veri_hazirla(semboller, sure):
    # FIX: list → tuple (Streamlit cache için hashable olmalı)
    paket = {}
    for s in semboller:
        s = s.strip().upper()
        if not s:
            continue
        try:
            t = yf.Ticker(s)
            hist = t.history(period=sure)
            if not hist.empty:
                # FIX: t.get_news() → t.news (yeni yfinance API)
                try:
                    haberler = t.news
                except Exception:
                    haberler = []
                paket[s] = {"df": hist, "info": t.info, "news": haberler}
        except Exception as e:
            st.warning(f"⚠️ {s} verisi çekilemedi.")
            continue
    return paket


@st.cache_data(ttl=3600)
def tr_cevir(metin):
    if not metin or metin == "N/A":
        return "Bilgi mevcut değil."
    if not CEVIRI_AKTIF:
        return metin
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin[:1000])
    except Exception:
        return metin  # FIX: hata olursa çökmek yerine orijinal metni döner


st.title("🏛️ Yatırım Noktası | Stratejik Analiz Terminali")
st.caption("Veriler Yahoo Finance üzerinden çekilmektedir. Yatırım tavsiyesi değildir.")

# --- ÜST PANEL ---
st.markdown("### 🔍 Hisseleri Kıyaslayın")
girdi = st.text_input(
    "Sembolleri virgül ile ayırın (Örn: AAPL, NVDA, TSLA, THYAO.IS):",
    "AAPL, NVDA"
).upper()
sembol_listesi = [s.strip() for s in girdi.split(",") if s.strip()]

period_map = {"1 Ay": "1mo", "1 Yıl": "1y", "3 Yıl": "3y", "5 Yıl": "5y", "Tümü": "max"}

st.markdown("**📅 Zaman Aralığı:**")
btn_cols = st.columns(len(period_map))
if "sure_secim" not in st.session_state:
    st.session_state.sure_secim = "1 Ay"

for i, etiket in enumerate(period_map.keys()):
    with btn_cols[i]:
        secili = st.session_state.sure_secim == etiket
        if st.button(etiket, key=f"btn_{etiket}", type="primary" if secili else "secondary", use_container_width=True):
            st.session_state.sure_secim = etiket

sure = st.session_state.sure_secim

if sembol_listesi:
    # FIX: list → tuple (cache uyumluluğu)
    with st.spinner("Veriler yükleniyor..."):
        tum_paket = veri_hazirla(tuple(sembol_listesi), period_map[sure])


    if tum_paket:
        # --- METRİKLER ---
        metrik_cols = st.columns(len(tum_paket))
        for i, (s, veri) in enumerate(tum_paket.items()):
            df = veri['df']
            # FIX: sıfıra bölme koruması eklendi
            if df.empty or len(df) < 1:
                continue
            fiyat = df['Close'].iloc[-1]
            baslangic = df['Close'].iloc[0]
            perf = ((fiyat / baslangic) - 1) * 100 if baslangic > 0 else 0
            para = "₺" if s.endswith(".IS") else "$"
            with metrik_cols[i]:
                st.metric(s, f"{fiyat:,.2f} {para}", f"{perf:.2f}%")

        # --- KIYASLAMA GRAFİĞİ ---
        fig = go.Figure()
        for s, veri in tum_paket.items():
            df = veri['df']
            if df.empty or len(df) < 2:
                continue
            baslangic_fiyat = df['Close'].iloc[0]
            if baslangic_fiyat == 0:
                continue
            yuzde_perf = (df['Close'] / baslangic_fiyat - 1) * 100
            fig.add_trace(go.Scatter(
                x=df.index,
                y=yuzde_perf,
                name=f"{s} (%)",
                mode='lines',
                line=dict(width=2.5)
            ))

        fig.update_layout(
            hovermode="x unified",
            height=500,
            template="plotly_white",
            yaxis=dict(side="right", ticksuffix="%", title="Getiri (%)", gridcolor="#f1f3f4"),
            xaxis=dict(showgrid=False),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- ŞİRKET DETAYLARI ---
        st.divider()
        ana_hisse = list(tum_paket.keys())[0]
        info = tum_paket[ana_hisse]['info']
        news = tum_paket[ana_hisse]['news']

        c_bilgi, c_haber = st.columns([1.5, 1])
        with c_bilgi:
            st.subheader(f"🏢 {ana_hisse} Şirket Profili")
            raw_cap = info.get('marketCap', 0)
            para = "₺" if ana_hisse.endswith(".IS") else "$"
            # FIX: hatalı .replace() zinciri kaldırıldı
            formatted_cap = f"{raw_cap / 1e9:,.2f} Milyar {para}" if raw_cap else "N/A"
            fk = info.get('trailingPE', 'N/A')
            fk_str = f"{fk:.2f}" if isinstance(fk, float) else str(fk)
            st.markdown(f"**Piyasa Değeri:** {formatted_cap} | **F/K:** {fk_str}")
            st.write(tr_cevir(info.get('longBusinessSummary', '')))

        with c_haber:
            st.subheader("🗞️ Güncel Haberler")
            if news:
                for n in news[:5]:
                    # FIX: yeni yfinance haber yapısına göre güvenli erişim
                    baslik = n.get('title', 'Başlık yok')
                    link = n.get('link') or n.get('url', '#')
                    st.markdown(f"🔗 **[{tr_cevir(baslik)}]({link})**")
                    st.write("---")
            else:
                st.info("Haberler şu an yüklenemiyor.")
    else:
        st.error("❌ Sembolleri kontrol edin; veri çekilemedi.")
