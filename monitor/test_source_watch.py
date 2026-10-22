import importlib.util, tempfile, shutil, pathlib, json, unittest.mock as m
src=pathlib.Path('monitor/check_sources.py').read_text()
with tempfile.TemporaryDirectory() as tmp:
 root=pathlib.Path(tmp); (root/'monitor').mkdir();(root/'data').mkdir()
 (root/'data/official_previews.json').write_text(json.dumps({'campaigns':[{'id':'test','bank':'QNB','source':'https://example.com/a','end':'2099-01-01'}]}))
 script=root/'monitor/check_sources.py';script.write_text(src)
 class Robots:
  def set_url(self,u):pass
  def read(self):pass
  def can_fetch(self,*args):return True
 class Response:
  headers={'Content-Type':'text/html'}
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def read(self,n):return b'fixed example html'
 with m.patch('urllib.robotparser.RobotFileParser',return_value=Robots()),m.patch('urllib.request.urlopen',return_value=Response()):
  exec(compile(src,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
  r=json.loads((root/'monitor/report.json').read_text());assert r['results'][0]['baseline_missing'] is True
  exec(compile(src,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
  r=json.loads((root/'monitor/report.json').read_text());assert r['results'][0]['changed'] is False
 print('mocked first-run and stable-second-run: OK')
