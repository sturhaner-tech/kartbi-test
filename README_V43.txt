Kartbi V43 — Provisional rule safety / development only

V42 uzerine tam paket. Yeni: 18 kural icin ek guvenlik denetimi ve
sinir senaryolari, GitHub Actions kontrolu.

ONEMLI: Kampanya kaynaklarinin gunluk dogrulamasini yapmaz.
Hicbir odul formulu onaylanmadi; gercek kazanc hesaplamasi acilmadi.

Test:
python monitor/validate_provisional_safety.py
python monitor/test_rule_boundaries.py
python monitor/test_rule_scenarios.py

Web yuklemede gizli .github klasoru ayri guncellenmelidir.
Bu paket henuz yayina hazir bir gercek-kazanc urunu degildir.
