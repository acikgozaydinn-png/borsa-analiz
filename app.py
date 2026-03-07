# --- Grafiği Hazırlama ve Kıyaslama Bölümü ---
st.subheader(f"📈 {ticker} - Analiz ve Kıyaslama")

# Kıyaslama Seçenekleri
c_k1, c_k2 = st.columns(2)
kiyas_turu = c_k1.selectbox("Kıyaslama Türü:", ["Yok", "Endeks (BIST 100)", "Özel Hisse"])
ikinci_hisse_ticker = ""

if kiyas_turu == "Özel Hisse":
    ikinci_hisse_ticker = c_k2.text_input("Kıyaslanacak Hisse (Örn: SASA.IS, NVDA):").upper()

# Grafik Çizimi
fig = go.Figure()

# 1. Ana Hisse (Daha belirgin mavi çizgi)
fig.add_trace(go.Scatter(
    x=df.index, y=df['Close'],
    mode='lines',
    line=dict(color='#1A73E8', width=3),
    name=ticker,
    hovertemplate="<b>" + ticker + "</b>: %{y:.2f} " + para + "<extra></extra>"
))

# 2. Kıyaslama Verisi Ekleme
if kiyas_turu != "Yok":
    try:
        k_ticker = "XU100.IS" if kiyas_turu == "Endeks (BIST 100)" else ikinci_hisse_ticker
        if k_ticker:
            k_verisi = yf.Ticker(k_ticker).history(period=period_map[secilen_sure])
            if not k_verisi.empty:
                # Yüzdesel değişim bazlı kıyaslama (Google Finans mantığı)
                # İki kağıdı da %0'dan başlatıyoruz ki performans farkı görünsün
                ana_norm = (df['Close'] / df['Close'].iloc[0]) - 1
                kiyas_norm = (k_verisi['Close'] / k_verisi['Close'].iloc[0]) - 1
                
                # Grafiği güncelle (Yüzdesel görünüme geç)
                fig.data[0].y = ana_norm * 100
                fig.add_trace(go.Scatter(
                    x=k_verisi.index, y=kiyas_norm * 100,
                    mode='lines',
                    line=dict(color='#FF9800', width=2, dash='dot'),
                    name=k_ticker,
                    hovertemplate="<b>" + k_ticker + "</b>: %{y:.2f}% <extra></extra>"
                ))
                fig.update_layout(yaxis_title="Performans (%)")
    except:
        st.warning("Kıyaslama verisi alınamadı.")

# Google Finans Tarzı Görünüm Ayarları
fig.update_layout(
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=False, linecolor="#dadce0"),
    yaxis=dict(side="right", showgrid=True, gridcolor="#f1f3f4"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

                
