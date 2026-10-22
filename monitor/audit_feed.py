
import json
import re
import sys
from pathlib import Path
from datetime import date

root = Path(__file__).resolve().parents[1]
errors = []

feed_path = root / "data" / "official_previews.json"
html_path = root / "index.html"

feed = json.loads(feed_path.read_text(encoding="utf-8"))
html = html_path.read_text(encoding="utf-8")

campaigns = feed.get("campaigns", [])
ids = [c["id"] for c in campaigns]

if len(ids) != len(set(ids)):
    errors.append("Tekrarlanan kampanya kimliği var")

for c in campaigns:
    if c.get("start", "") > c.get("end", ""):
        errors.append("Tarih hatası: " + c["id"])

    if not c.get("source", "").startswith("https://"):
        errors.append("Kaynak bağlantısı eksik: " + c["id"])

today = date.today().isoformat()

active = [
    c for c in campaigns
    if c.get("start", "") <= today <= c.get("end", "")
]

match = re.search(
    r"const REAL_RULES=\{(.*?)\n\};",
    html,
    re.DOTALL
)

rule_ids = set()

if match:
    rule_ids = set(re.findall(
        r"^\s*'([^']+)':\{",
        match.group(1),
        re.MULTILINE
    ))
else:
    errors.append("Hesaplama kuralları bulunamadı")

for rule_id in rule_ids:
    if rule_id not in ids:
        errors.append("Kampanyası olmayan kural: " + rule_id)

report = {
    "date": today,
    "total_campaigns": len(campaigns),
    "active_campaigns": len(active),
    "calculation_rules": len(rule_ids),
    "errors": errors
}

print(json.dumps(report, ensure_ascii=False, indent=2))

if errors:
    sys.exit(1)
