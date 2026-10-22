import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('discovery',Path(__file__).with_name('discover_campaigns.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
html='<a href="/kampanyalar/yeni-urun?utm=1">Yeni</a><a href="https://evil.test/kampanyalar/x">x</a><a href="/hakkimizda">h</a><a href="/kampanyalar/yeni-urun#top">duplicate</a>'
assert m.candidates(html,'https://www.example.com/kampanyalar') == ['https://www.example.com/kampanyalar/yeni-urun']
assert m.candidates('<a href="/kampanyalar">Index</a>','https://www.example.com/kampanyalar') == []
print('Discovery link parsing tests: OK')
