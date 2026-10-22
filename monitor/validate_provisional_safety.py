#!/usr/bin/env python3
"""Fail-closed publication guard for provisional campaigns. Does not verify bank terms."""
import json, sys
from pathlib import Path
from datetime import date
root=Path(__file__).resolve().parents[1]
feed=json.loads((root/'data/official_previews.json').read_text(encoding='utf-8'))['campaigns']
rules=json.loads((root/'data/provisional_rule_gates.json').read_text(encoding='utf-8'))['rules']
errors=[]
feed_ids=[x['id'] for x in feed]
rule_ids=[x['campaign_id'] for x in rules]
if len(feed_ids)!=len(set(feed_ids)): errors.append('Duplicate feed IDs')
if len(rule_ids)!=len(set(rule_ids)): errors.append('Duplicate rule IDs')
if set(feed_ids)!=set(rule_ids): errors.append('Feed/rule ID mismatch: '+str(sorted(set(feed_ids)^set(rule_ids))))
for r in rules:
 cid=r['campaign_id']
 if r.get('rule_status')!='provisional' or r.get('calculation_approved') is not False or r.get('reward_amount') is not None:
  errors.append('Unsafe reward approval: '+cid)
 if not r.get('source','').startswith('https://'): errors.append('Missing HTTPS source: '+cid)
 try:
  if date.fromisoformat(r['start'])>date.fromisoformat(r['end']): errors.append('Bad dates: '+cid)
 except (ValueError,KeyError,TypeError): errors.append('Invalid dates: '+cid)
 if not isinstance(r.get('required_evidence'),list) or not r['required_evidence']:
  errors.append('Missing evidence gates: '+cid)
report={'feed_count':len(feed),'rule_count':len(rules),'approved_reward_rules':sum(r.get('calculation_approved') is True for r in rules),'errors':errors}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
