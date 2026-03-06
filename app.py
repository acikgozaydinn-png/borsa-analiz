import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
import os
from deep_translator import GoogleTranslator

# Anthropic API Key (Streamlit Cloud → Settings → Secrets'tan okunur)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────
# 1. SAYFA AYARLARI
# ─────────────────────────────────────────
st.set_page_config(page_title="Gelişmiş Borsa Analizi", layout="wide")


st.title("📈 Yapay Zeka Destekli Borsa Analiz Aracı")
st.write("Hisse sembolünü yazın (Örn: THYAO.IS, AAPL, BTC-USD) ve analizi izleyin.")

# ─────────────────────────────────────────
# 2. SEKMELER
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Teknik Analiz", "🔄 Hisse Karşılaştırma", "💼 Portföy Takibi"])


# ─────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────

def claude_turkce_ozet(metin: str, tur: str = "profil") -> str:
    """
    Anthropic Claude API ile Türkçe özet üretir.
    tur: "profil" → şirket açıklaması, "haber" → haber özetleme
    """
    if tur == "profil":
        sistem = (
            "Sen bir Türkçe finans asistanısın. "
            "Verilen İngilizce şirket açıklamasını sade ve anlaşılır Türkçeye çevir. "
            "Şu başlıkları madde madde özetle:\n"
            "1) Şirketin ne iş yaptığı\n"
            "2) Ana faaliyet alanları ve ürünler/hizmetler\n"
            "3) Önemli iş ortaklıkları veya anlaşmaları (varsa)\n"
            "4) Yatırım ve büyüme stratejisi\n"
            "Kısa, net ve sade bir dil kullan."
        )
    else:
        sistem = (
            "Sen bir Türkçe finans asistanısın. "
            "Aşağıdaki İngilizce haber başlıklarını ve özetlerini oku. "
            "Bunları Türkçe olarak şu kategorilere göre grupla:\n"
            "📋 Anlaşmalar & Ortaklıklar\n"
            "💰 Yatırımlar & Finansman\n"
            "📈 Büyüme & Genişleme\n"
            "⚠️ Riskler & Uyarılar\n"
            "İlgili kategori yoksa o başlığı atla. Her maddeyi 1-2 cümleyle özetle."
        )

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": sistem,
                "messages": [{"role": "user", "content": metin}]
            },
            timeout=30
        )
        data = response.json()
        return data["content"][0]["text"]
    except Exception as e:
        return f"(AI özet alınamadı: {e})"


def cevir(metin: str) -> str:
    try:
    try:
        return GoogleTranslator(source='auto', target='tr').translate(metin)
    except:
        return metin


def get_ai_signal(df):
    signals = []
    score = 0
    last = df.iloc[-1]

    rsi = last.get('RSI', None)
    if rsi is not None and not pd.isna(rsi):
        if rsi < 30:
            signals.append("✅ RSI aşırı satım bölgesinde (< 30) → **AL sinyali**")
            score += 2
        elif rsi > 70:
            signals.append("🔴 RSI aşırı alım bölgesinde (> 70) → **SAT sinyali**")
            score -= 2
        else:
            signals.append(f"⚪ RSI nötr bölgede ({rsi:.1f})")

    macd = last.get('MACD_12_26_9', None)
    macd_sig = last.get('MACDs_12_26_9', None)
    if macd is not None and macd_sig is not None and not pd.isna(macd) and not pd.isna(macd_sig):
        if macd > macd_sig:
            signals.append("✅ MACD sinyal çizgisinin üzerinde → **AL sinyali**")
            score += 1
        else:
            signals.append("🔴 MACD sinyal çizgisinin altında → **SAT sinyali**")
            score -= 1

    bbl = last.get('BBL_20_2.0', None)
    bbu = last.get('BBU_20_2.0', None)
    close = last.get('Close', None)
    if bbl is not None and bbu is not None and close is not None and not pd.isna(bbl) and not pd.isna(bbu):
        if close < bbl:
            signals.append("✅ Fiyat alt Bollinger bandının altında → **AL sinyali**")
            score += 1
        elif close > bbu:
            signals.append("🔴 Fiyat üst Bollinger bandının üzerinde → **SAT sinyali**")
            score -= 1
        else:
            signals.append("⚪ Fiyat Bollinger bandları içinde → **Nötr**")

    sma20 = last.get('SMA20', None)
    if sma20 is not None and close is not None and not pd.isna(sma20):
        if close > sma20:
            signals.append("✅ Fiyat SMA20 üzerinde → **Yükseliş trendi**")
            score += 1
        else:
            signals.append("🔴 Fiyat SMA20 altında → **Düşüş trendi**")
            score -= 1

    if score >= 3:
        verdict = ("🟢", "GÜÇLÜ AL", "success")
    elif score >= 1:
        verdict = ("🟡", "AL", "warning")
    elif score == 0:
        verdict = ("⚪", "BEKLE / NÖTR", "info")
    elif score >= -2:
        verdict = ("🟠", "SAT", "warning")
    else:
        verdict = ("🔴", "GÜÇLÜ SAT", "error")

    return signals, verdict, score


def fetch_and_compute(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    info = stock.info

    if df.empty:
        return None, None, stock

    df['SMA20'] = ta.sma(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)

    macd = ta.macd(df['Close'])
    if macd is not None:
        df = pd.concat([df, macd], axis=1)

    bb = ta.bbands(df['Close'], length=20)
    if bb is not None:
        df = pd.concat([df, bb], axis=1)

    return df, info, stock


def sirket_bilgi_karti(info: dict):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🏭 Sektör:** {cevir(info.get('sector', 'Bilinmiyor'))}")
        st.markdown(f"**📂 Endüstri:** {cevir(info.get('industry', 'Bilinmiyor'))}")
        st.markdown(f"**🌍 Ülke:** {info.get('country', 'Bilinmiyor')}")
        emp = info.get('fullTimeEmployees')
        st.markdown(f"**👥 Çalışan Sayısı:** {emp:,}" if isinstance(emp, int) else "**👥 Çalışan Sayısı:** N/A")
    with col2:
        st.markdown(f"**🌐 Web:** {info.get('website', 'N/A')}")
        st.markdown(f"**📍 Şehir:** {info.get('city', '')}, {info.get('state', '')}")
        st.markdown(f"**📅 Borsa:** {info.get('exchange', 'N/A')}")
        st.markdown(f"**💱 Para Birimi:** {info.get('currency', 'N/A')}")


def haberler_metni(stock) -> str:
    try:
        news = stock.news
        if not news:
            return ""
        satirlar = []
        for item in news[:10]:
            content = item.get("content", {})
            baslik = content.get("title", item.get("title", ""))
            ozet = content.get("summary", "")
            if baslik:
                satirlar.append(f"- {baslik}. {ozet}")
        return "\n".join(satirlar)
    except:
        return ""


# ─────────────────────────────────────────
# TAB 1: TEKNİK ANALİZ
# ─────────────────────────────────────────
with tab1:
    ticker = st.text_input("Hisse Sembolü Giriniz:", value="THYAO.IS", key="main_ticker").upper()

    try:
        df, info, stock_obj = fetch_and_compute(ticker)

        if df is None:
            st.error("Veri bulunamadı. Lütfen sembolü kontrol edin.")
        else:

            # ── ŞİRKET PROFİLİ ──
            st.subheader(f"🏢 {ticker} — Şirket Profili")
            sirket_bilgi_karti(info)
            st.divider()

            # Şirket açıklaması → Claude ile Türkçe
            raw_desc = info.get('longBusinessSummary', '')
            if raw_desc:
                with st.spinner("🤖 Şirket açıklaması Türkçeye çevriliyor..."):
                    ai_profil = claude_turkce_ozet(raw_desc, tur="profil")
                st.markdown("#### 📝 Şirket Hakkında (AI Türkçe Özet)")
                st.info(ai_profil)
            else:
                st.info("Bu hisse için şirket açıklaması bulunamadı.")

            # ── GÜNCEL HABERLER → Claude ile Türkçe ──
            st.markdown("#### 📰 Güncel Haberler & Anlaşmalar (AI Türkçe Özet)")
            haber_metni = haberler_metni(stock_obj)

            if haber_metni:
                with st.spinner("🤖 Haberler analiz ediliyor..."):
                    ai_haberler = claude_turkce_ozet(haber_metni, tur="haber")
                st.success(ai_haberler)

                with st.expander("📋 Ham Haberler (İngilizce orijinaller)"):
                    try:
                        for item in (stock_obj.news or [])[:10]:
                            content = item.get("content", {})
                            baslik = content.get("title", item.get("title", "—"))
                            link = content.get("canonicalUrl", {}).get("url", "") or item.get("link", "")
                            st.markdown(f"- [{baslik}]({link})" if link else f"- {baslik}")
                    except:
                        st.write(haber_metni)
            else:
                st.warning("Bu hisse için güncel haber bulunamadı.")

            st.divider()

            # ── AI SİNYAL PANELİ ──
            st.subheader("🤖 Yapay Zeka Teknik Sinyal Analizi")
            signals, verdict, score = get_ai_signal(df)

            emoji, label, stype = verdict
            msg = f"{emoji} **Genel Sinyal: {label}** (Puan: {score:+d})"
            if stype == "success":
                st.success(msg)
            elif stype == "error":
                st.error(msg)
            else:
                st.warning(msg)

            with st.expander("📋 Sinyal Detayları"):
                for s in signals:
                    st.markdown(f"- {s}")
                st.caption("⚠️ Bu sinyaller yatırım tavsiyesi değildir. Kendi araştırmanızı yapın.")

            # ── GRAFİK ──
            st.subheader("📊 Teknik Fiyat Grafiği")
            fig = make_subplots(
                rows=3, cols=1, shared_xaxes=True,
                row_heights=[0.55, 0.25, 0.20],
                vertical_spacing=0.03,
                subplot_titles=("Fiyat + Bollinger Bands + SMA20", "MACD", "RSI")
            )

            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name='Mum Grafiği'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA20'],
                line=dict(color='orange', width=1.5), name='SMA 20'
            ), row=1, col=1)

            if 'BBU_20_2.0' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['BBU_20_2.0'],
                    line=dict(color='rgba(100,200,255,0.5)', width=1, dash='dot'),
                    name='BB Üst'
                ), row=1, col=1)
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['BBL_20_2.0'],
                    line=dict(color='rgba(100,200,255,0.5)', width=1, dash='dot'),
                    name='BB Alt', fill='tonexty',
                    fillcolor='rgba(100,200,255,0.07)'
                ), row=1, col=1)

            if 'MACD_12_26_9' in df.columns:
                macd_hist = df.get('MACDh_12_26_9', pd.Series(dtype=float))
                colors = ['green' if (not pd.isna(v) and v >= 0) else 'red' for v in macd_hist]
                fig.add_trace(go.Bar(x=df.index, y=macd_hist, name='MACD Histogram',
                                     marker_color=colors, opacity=0.6), row=2, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'],
                                         line=dict(color='cyan', width=1.2), name='MACD'), row=2, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'],
                                         line=dict(color='yellow', width=1.2), name='Sinyal'), row=2, col=1)

            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                                     line=dict(color='violet', width=1.5), name='RSI'), row=3, col=1)
            fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)

            fig.update_layout(
                xaxis_rangeslider_visible=False, template="plotly_dark", height=750,
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            # ── TEMEL VERİLER ──
            st.subheader("📌 Temel Finansal Veriler")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.metric("Güncel Fiyat", f"{df['Close'].iloc[-1]:.2f}")
            with c2:
                rsi_val = df['RSI'].iloc[-1]
                st.metric("RSI (14)", f"{rsi_val:.2f}",
                          "Aşırı Alım" if rsi_val > 70 else ("Aşırı Satım" if rsi_val < 30 else "Nötr"))
            with c3:
                mc = info.get('marketCap')
                st.metric("Piyasa Değeri", f"{mc:,}" if mc else "N/A")
            with c4:
                pe = info.get('trailingPE')
                st.metric("F/K Oranı", f"{pe:.2f}" if pe else "N/A")
            with c5:
                dy = info.get('dividendYield')
                st.metric("Temettü Verimi", f"%{dy*100:.2f}" if dy else "N/A")
            with c6:
                beta = info.get('beta')
                st.metric("Beta", f"{beta:.2f}" if beta else "N/A")

    except Exception as e:
        st.warning(f"Bir hata oluştu: {e}")


# ─────────────────────────────────────────
# TAB 2: HISSE KARŞILAŞTIRMA
# ─────────────────────────────────────────
with tab2:
    st.subheader("🔄 Çoklu Hisse Karşılaştırma")
    compare_input = st.text_input(
        "Semboller (Örn: AAPL, MSFT, GOOGL veya THYAO.IS, GARAN.IS):",
        value="AAPL, MSFT, GOOGL", key="compare_tickers"
    )
    compare_period = st.selectbox("Dönem:", ["3mo", "6mo", "1y", "2y", "5y"], index=2, key="cperiod")

    if st.button("Karşılaştır", key="compare_btn"):
        tickers_list = [t.strip().upper() for t in compare_input.split(",") if t.strip()]

        if len(tickers_list) < 2:
            st.warning("Lütfen en az 2 hisse sembolü girin.")
        else:
            with st.spinner("Veriler çekiliyor..."):
                compare_df = pd.DataFrame()
                valid_tickers = []
                compare_infos = {}

                for t in tickers_list:
                    try:
                        stk = yf.Ticker(t)
                        data = stk.history(period=compare_period)['Close']
                        if not data.empty:
                            compare_df[t] = data
                            valid_tickers.append(t)
                            compare_infos[t] = stk.info
                    except:
                        st.warning(f"{t} için veri alınamadı.")

            if not compare_df.empty:
                norm_df = (compare_df / compare_df.iloc[0]) * 100

                fig_cmp = go.Figure()
                for col in norm_df.columns:
                    fig_cmp.add_trace(go.Scatter(x=norm_df.index, y=norm_df[col], name=col, mode='lines'))
                fig_cmp.update_layout(
                    title="Normalize Fiyat Performansı (Başlangıç = 100)",
                    template="plotly_dark", height=450,
                    yaxis_title="Normalize Fiyat"
                )
                st.plotly_chart(fig_cmp, use_container_width=True)

                # Performans tablosu
                st.markdown("#### 📊 Performans Özeti")
                perf_rows = []
                for t in valid_tickers:
                    s = compare_df[t].dropna()
                    if len(s) < 2:
                        continue
                    getiri = (s.iloc[-1] / s.iloc[0] - 1) * 100
                    inf = compare_infos.get(t, {})
                    perf_rows.append({
                        "Sembol": t,
                        "Başlangıç": f"{s.iloc[0]:.2f}",
                        "Güncel": f"{s.iloc[-1]:.2f}",
                        "Dönem Getirisi": f"%{getiri:.2f}",
                        "Piyasa Değeri": f"{inf.get('marketCap'):,}" if isinstance(inf.get('marketCap'), int) else "N/A",
                        "F/K": f"{inf.get('trailingPE'):.1f}" if isinstance(inf.get('trailingPE'), float) else "N/A",
                        "Beta": f"{inf.get('beta'):.2f}" if isinstance(inf.get('beta'), float) else "N/A",
                    })
                if perf_rows:
                    st.dataframe(pd.DataFrame(perf_rows).set_index("Sembol"), use_container_width=True)

                # Her şirket için Türkçe AI özeti
                st.markdown("#### 🤖 Şirketler Hakkında Türkçe AI Özetleri")
                for t in valid_tickers:
                    inf = compare_infos.get(t, {})
                    with st.expander(f"🏢 {t} — {inf.get('shortName', '')}"):
                        desc = inf.get('longBusinessSummary', '')
                        if desc:
                            with st.spinner(f"{t} özeti hazırlanıyor..."):
                                ozet = claude_turkce_ozet(desc, tur="profil")
                            st.info(ozet)
                        else:
                            st.write("Açıklama bulunamadı.")


# ─────────────────────────────────────────
# TAB 3: PORTFÖY TAKİBİ
# ─────────────────────────────────────────
with tab3:
    st.subheader("💼 Portföy Takip Paneli")

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = [
            {"sembol": "THYAO.IS", "adet": 100, "alis_fiyati": 200.0},
            {"sembol": "AAPL",     "adet": 10,  "alis_fiyati": 170.0},
        ]

    portfolio_df = pd.DataFrame(st.session_state.portfolio)
    edited_df = st.data_editor(
        portfolio_df,
        num_rows="dynamic",
        column_config={
            "sembol":      st.column_config.TextColumn("Sembol"),
            "adet":        st.column_config.NumberColumn("Adet", min_value=0),
            "alis_fiyati": st.column_config.NumberColumn("Alış Fiyatı", min_value=0.0, format="%.2f"),
        },
        use_container_width=True,
        key="portfolio_editor"
    )

    if st.button("📊 Portföyü Hesapla", key="calc_portfolio"):
        st.session_state.portfolio = edited_df.to_dict("records")
        rows = []
        toplam_maliyet = 0
        toplam_deger = 0

        with st.spinner("Portföy hesaplanıyor..."):
            for row in st.session_state.portfolio:
                sembol = str(row.get("sembol", "")).strip().upper()
                adet = float(row.get("adet", 0))
                alis = float(row.get("alis_fiyati", 0))
                if not sembol or adet <= 0:
                    continue
                try:
                    guncel = yf.Ticker(sembol).history(period="1d")['Close']
                    if guncel.empty:
                        continue
                    guncel_fiyat = guncel.iloc[-1]
                    maliyet = adet * alis
                    deger = adet * guncel_fiyat
                    kar_zarar = deger - maliyet
                    kar_zarar_pct = (kar_zarar / maliyet * 100) if maliyet else 0
                    toplam_maliyet += maliyet
                    toplam_deger += deger
                    rows.append({
                        "Sembol": sembol,
                        "Adet": adet,
                        "Alış Fiyatı": f"{alis:.2f}",
                        "Güncel Fiyat": f"{guncel_fiyat:.2f}",
                        "Maliyet": f"{maliyet:,.2f}",
                        "Güncel Değer": f"{deger:,.2f}",
                        "Kar/Zarar": f"{kar_zarar:+,.2f}",
                        "K/Z %": f"%{kar_zarar_pct:+.2f}",
                    })
                except Exception as ex:
                    st.warning(f"{sembol}: {ex}")

        if rows:
            st.dataframe(pd.DataFrame(rows).set_index("Sembol"), use_container_width=True)

            toplam_kar = toplam_deger - toplam_maliyet
            toplam_kar_pct = (toplam_kar / toplam_maliyet * 100) if toplam_maliyet else 0

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("💰 Toplam Maliyet", f"{toplam_maliyet:,.2f}")
            with c2:
                st.metric("📈 Portföy Değeri", f"{toplam_deger:,.2f}")
            with c3:
                st.metric("💵 Kar/Zarar", f"{toplam_kar:+,.2f}")
            with c4:
                st.metric("📊 Toplam Getiri", f"%{toplam_kar_pct:+.2f}")

            fig_pie = go.Figure(go.Pie(
                labels=[r["Sembol"] for r in rows],
                values=[float(r["Güncel Değer"].replace(",", "")) for r in rows],
                hole=0.4
            ))
            fig_pie.update_layout(
                title="Portföy Dağılımı (Güncel Değer)",
                template="plotly_dark", height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.error("Hiçbir hisse için güncel fiyat alınamadı.")
