#!/usr/bin/env python3
"""Hourly campaign source watcher. Does not invent or overwrite campaign terms."""
import datetime, hashlib, json, pathlib, sys, urllib.error, urllib.parse, urllib.request, urllib.robotparser
BASE=pathlib.Path(__file__).resolve().parent
ROOT=BASE.parent
feed=json.loads((ROOT/'data/official_previews.json').read_text(encoding='utf-8'))
previous_path=BASE/'previous_hashes.json'
try: previous=json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
except (ValueError,OSError): previous={}
now=datetime.datetime.now(datetime.timezone.utc)
results=[]; new=dict(previous)
robots_cache={}
for c in feed['campaigns']:
    url=c.get('source',''); parsed=urllib.parse.urlparse(url)
    item={'id':c['id'],'bank':c['bank'],'url':url,'campaign_end':c['end'],'status':'skipped','changed':None,'review_required':False}
    if c['end']<now.date().isoformat():
        item.update(status='expired',review_required=True)
        results.append(item);continue
    if parsed.scheme!='https' or not parsed.netloc:
        item.update(status='invalid_url',review_required=True)
        results.append(item);continue
    try:
        origin=f'{parsed.scheme}://{parsed.netloc}'
        if origin not in robots_cache:
            rp=urllib.robotparser.RobotFileParser();rp.set_url(origin+'/robots.txt')
            try:rp.read()
            except Exception as exc:raise RuntimeError('robots.txt unavailable') from exc
            robots_cache[origin]=rp
        if not robots_cache[origin].can_fetch('KartbiSourceWatcher',url):
            item.update(status='robots_disallowed',review_required=True)
            results.append(item);continue
        request=urllib.request.Request(url,headers={'User-Agent':'KartbiSourceWatcher/0.2 (manual review only)','Accept':'text/html'})
        with urllib.request.urlopen(request,timeout=12) as response:
            if 'text/html' not in response.headers.get('Content-Type','').lower():raise ValueError('non-html response')
            content=response.read(256001)
            if len(content)>256000:raise ValueError('page exceeds sample limit')
            digest=hashlib.sha256(content).hexdigest()
            old=previous.get(url)
            item.update(status='ok',changed=(digest!=old if old else None),review_required=(digest!=old if old else True),baseline_missing=(old is None))
            new[url]=digest
    except Exception as exc:
        item.update(status='unavailable',review_required=True,reason=str(exc)[:160])
    results.append(item)
report={'checked_at':now.isoformat(),'campaign_count':len(results),'changed_count':sum(x['changed'] is True for x in results),'review_required_count':sum(x['review_required'] for x in results),'results':results,'notice':'Hourly source monitoring. HTML changes are unverified; expired records are hidden automatically by date. No speculative reward or terms updates.'}
(BASE/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
previous_path.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('campaign_count','changed_count','review_required_count')},ensure_ascii=False))

# Public, machine-readable status is safe to publish; raw HTML and guessed terms are not.
public={'schemaVersion':1,'checkedAt':report['checked_at'],'campaignCount':len(results),'changedCount':report['changed_count'],'reviewRequiredCount':report['review_required_count'],'campaigns':[{'id':x['id'],'status':x['status'],'changed':x['changed'],'reviewRequired':x['review_required']} for x in results]}
(ROOT/'data/source_status.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
