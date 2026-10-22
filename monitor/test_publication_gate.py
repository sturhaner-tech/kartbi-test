#!/usr/bin/env python3
"""Safety gate: never publish rewards until each rule is independently verified."""
import json, pathlib, re, sys
root=pathlib.Path(__file__).resolve().parents[1]
feed=json.loads((root/'data/official_previews.json').read_text(encoding='utf-8'))
html=(root/'index.html').read_text(encoding='utf-8')
errors=[]
for c in feed['campaigns']:
 if c.get('calculationApproved') is not False: errors.append('Unexpected reward approval: '+c['id'])
 if c.get('publicationStatus')!='source-summary-only': errors.append('Unsafe publication: '+c['id'])
 if c.get('ruleValidationStatus')!='pending-full-condition-and-transaction-tests': errors.append('Missing validation hold: '+c['id'])
if not re.search(r'function compareView\(\)\{return compareRealView\(\);\}',html):errors.append('Safe comparison route missing')
if 'Kazanç hesaplanmıyor; güncel koşulları bankadan kontrol et.' not in html:errors.append('Safety disclaimer missing')
if 'let demoCalculation=false;' not in html:errors.append('Demo flag state changed unexpectedly')
print(json.dumps({'campaigns':len(feed['campaigns']),'reward_approved':sum(c.get('calculationApproved') is True for c in feed['campaigns']),'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
