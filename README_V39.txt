KARTBI V39 - SAATLIK KAYNAK IZLEME

1. ZIP dosyasini GitHub deposunun kokune, klasor yapisini koruyarak yukleyin.
2. Settings > Actions > General > Workflow permissions: Read and write permissions secin.
3. Actions > Kartbi campaign source watch > Run workflow.
4. data/source_status.json dosyasi saatlik yenilenir, monitor/previous_hashes.json degisiklik karsilastirmasi icin saklanir.
5. Banka sayfasi degisikligi kampanya kosulu degisikligi olarak otomatik kabul edilmez.
6. Suresi dolan kampanyalar mevcut istemci tarih filtresiyle otomatik gizlenir.
7. Yeni kampanya, tutar, uygunluk veya odul kurali otomatik cikarilip yayinlanmaz: kaynak HTML'i tek basina guvenilir yapilandirilmis veri degildir.
8. GitHub Actions schedule gecikebilir. Saatlik kontrol hedeflenir, garanti edilmez.
9. Depo public oldugundan source_status.json ve izleme raporlari herkesce gorulebilir.
