#!/usr/bin/env python3
"""Offline quality and expiry audit for the manually curated campaign feed."""
import json,datetime,pathlib,collections,sys,re
root=pathlib.Path(__file__).resolve().parents[1]
feed=json.loads((root/'data/official_previews.json').read_text(encoding='utf-8'))
rules=json.loads((root/'data/rule_coverage.json').read_text(encoding='utf-8'))
today=datetime.date.today().isoformat()
banks=['Akbank','Yapı Kredi','Garanti BBVA','İş Bankası','Halkbank','QNB']
rows=feed['campaigns']; ids=[c['id'] for c in rows]
rulemap={r['id']:r for r in rules['campaigns']}
html=(root/'index.html').read_text(encoding='utf-8')
block=html.split('const REAL_RULES={',1)[1].split('\n};',1)[0]
runtime_ids=set(re.findall(r"^ '([^']+)':\{",block,re.M))
errors=[]
if len(ids)!=len(set(ids)):errors.append('Duplicate campaign ids')
for c in rows:
 if c['bank'] not in banks:errors.append('Unknown bank '+c['id'])
 if c['start']>c['end']:errors.append('Invalid dates '+c['id'])
 if not c.get('source','').startswith('https://'):errors.append('Missing HTTPS source '+c['id'])
for k in rulemap:
 if k not in ids:errors.append('Rule without campaign '+k)
for c in rows:
 expected='conditional-rule' if c['id'] in runtime_ids else 'manual-review'
 if rulemap.get(c['id'],{}).get('ruleStatus')!=expected:errors.append('Coverage mismatch '+c['id'])
for k in runtime_ids:
 if k not in ids:errors.append('Runtime rule without campaign '+k)
active=[c for c in rows if c['start']<=today<=c['end']]
expired=[c for c in rows if c['end']<today]
future=[c for c in rows if c['start']>today]
missing=[c['id'] for c in active if c['id'] not in runtime_ids]
report={'date':today,'last_manual_review':feed.get('checkedOn'),'total':len(rows),'active':len(active),'expired':len(expired),'upcoming':len(future),'active_by_bank':dict(collections.Counter(c['bank'] for c in active)),'expired_ids':[c['id'] for c in expired],'runtime_rule_count':len(runtime_ids),'active_missing_rule_ids':missing,'errors':errors,'disclaimer':'No automatic source verification; review and update campaign terms manually.'}
dest=root/'monitor'/'feed_audit.json'
dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
