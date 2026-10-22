#!/usr/bin/env python3
"""Boundary and fail-closed tests for all provisional campaign gates."""
import json
from pathlib import Path
from datetime import date,timedelta
from evaluate_rule_gates import evaluate
root=Path(__file__).resolve().parents[1]
rules=json.loads((root/'data/provisional_rule_gates.json').read_text(encoding='utf-8'))['rules']
checks=0
for r in rules:
 start=date.fromisoformat(r['start']); end=date.fromisoformat(r['end'])
 base={'date':str(start),**{k:True for k in r['required_evidence']}}
 cases=[({'date':str(start-timedelta(days=1))},'ineligible'),({'date':str(end+timedelta(days=1))},'ineligible'),({'date':'not-a-date'},'unknown'),({},'unknown'),(base,'potentially_eligible_unverified')]
 for field in r['required_evidence']:
  c=base.copy();c[field]=False;cases.append((c,'ineligible'))
  c=base.copy();c.pop(field);cases.append((c,'unknown'))
 for sc,expected in cases:
  result=evaluate(r,sc)
  assert result['state']==expected,(r['campaign_id'],sc,result)
  assert 'reward' not in result and 'amount' not in result
  checks+=1
 for altered in [{'calculation_approved':True},{'reward_amount':100},{'rule_status':'approved'}]:
  invalid=dict(r,**altered)
  assert evaluate(invalid,base)['state']=='unknown'
  checks+=1
print(json.dumps({'campaigns':len(rules),'passed':checks,'approved_rewards':0},ensure_ascii=False))
