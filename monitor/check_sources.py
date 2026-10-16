#!/usr/bin/env python3
"""Conservative public-source availability watcher. No content publication or login."""
import json, hashlib, datetime, urllib.request, urllib.robotparser, urllib.error, urllib.parse, pathlib, sys
BASE=pathlib.Path(__file__).resolve().parent
sources=json.loads((BASE/'sources.json').read_text())
previous_path=BASE/'previous_hashes.json'
previous=json.loads(previous_path.read_text()) if previous_path.exists() else {}
results=[]; new_hashes={}
for item in sources:
    url=item['url']; parsed=urllib.parse.urlparse(url)
    result={'bank':item['bank'],'url':url,'status':'skipped','changed':None}
    try:
        robots=urllib.robotparser.RobotFileParser(); robots.set_url(f'{parsed.scheme}://{parsed.netloc}/robots.txt')
        try: robots.read()
        except Exception as e: raise RuntimeError('robots.txt okunamadı; güvenli tarafta kalmak için atlandı') from e
        if not robots.can_fetch('KartbiSourceWatcher',url):
            result['status']='robots_disallowed'; results.append(result);continue
        req=urllib.request.Request(url,headers={'User-Agent':'KartbiSourceWatcher/0.1 (manual-review-only; no republication)','Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=12) as response:
            typ=response.headers.get('Content-Type','')
            if 'text/html' not in typ: raise ValueError('HTML olmayan yanıt')
            # Bounded read; hash only, do not save or republish source HTML.
            body=response.read(256_001)
            if len(body)>256_000: raise ValueError('Sayfa örneklem limiti aşıldı; kontrol atlandı')
            digest=hashlib.sha256(body).hexdigest()
            result.update(status='ok',changed=(digest!=previous[url] if url in previous else None),hash=digest)
            new_hashes[url]=digest
    except Exception as e: result.update(status='unavailable',reason=str(e)[:180])
    results.append(result)
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'note':'Hash değişimi yeni kampanya anlamına gelmez. İçerik alınmaz/yayınlanmaz.','results':results}
(BASE/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Preserve old hashes for sources that could not be checked.
previous.update(new_hashes)
previous_path.write_text(json.dumps(previous,indent=2))
print(json.dumps({'ok':sum(r['status']=='ok' for r in results),'changed':sum(r['changed'] is True for r in results),'skipped':sum(r['status']!='ok' for r in results)}))
