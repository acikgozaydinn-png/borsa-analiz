import streamlit as st
import yfinance as yf  # Bu satır eksik olduğu için hata alıyorsun
from googletrans import Translator

ı# ... (Kütüphane ithalleri aynı kalacak)

try:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # 1. ŞİRKETİN NE İŞ YAPTIĞI (Otomatik Çeviri ile)
    st.write(f"### 🏢 {ticker} Şirket Faaliyetleri")
    ozet = info.get('longBusinessSummary', 'Bilgi bulunamadı.')
    tr_ozet = translator.translate(ozet, src='en', dest='tr').text
    st.info(tr_ozet)

    # 2. GÜNCEL ANLAŞMALAR VE HABERLER
    st.write(f"### 📰 {ticker} Hakkında Son Gelişmeler")
    haberler = stock.news
    if haberler:
        for haber in haberler[:5]: # Son 5 haberi getir
            baslik = haber['title']
            kaynak = haber['publisher']
            link = haber['link']
            # Haberin başlığını da Türkçeye çevirelim
            tr_baslik = translator.translate(baslik, src='en', dest='tr').text
            st.write(f"**{tr_baslik}** ({kaynak})")
            st.caption(f"[Haberi Oku]({link})")
    else:
        st.write("Şirket hakkında yakın zamanda yayınlanmış spesifik haber bulunamadı.")

    # 3. ÖNEMLİ İSTATİSTİKLER (Anlaşma potansiyeli ve nakit durumu)
    st.write("### 📊 Finansal Sağlık Notları")
    col_a, col_b = st.columns(2)
    nakit = info.get('totalCash', 0)
    borc = info.get('totalDebt', 0)
    col_a.write(f"**Eldeki Toplam Nakit:** ${nakit:,.0f}")
    col_b.write(f"**Toplam Borç:** ${borc:,.0f}")

except Exception as e:
    st.error("Veri çekilirken bir sorun oluştu.")
