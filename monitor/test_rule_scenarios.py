#!/usr/bin/env python3
"""3 cases per campaign: negative, unknown, potential (not approved)."""
import json
from pathlib import Path
from evaluate_rule_gates import evaluate
root=Path(__file__).resolve().parents[1]
rules=json.loads((root/'data/provisional_rule_gates.json').read_text(encoding='utf-8'))['rules']
assert len(rules)==18
assert len({r['campaign_id'] for r in rules})==18
checks=0
for r in rules:
    date=r['start']; field=r['required_evidence'][0]
    negative={'date':date,field:False}
    assert evaluate(r,negative)['state']=='ineligible',r['campaign_id'];checks+=1
    assert evaluate(r,{'date':date})['state']=='unknown',r['campaign_id'];checks+=1
    positive={'date':date,**{key:True for key in r['required_evidence']}}
    res=evaluate(r,positive)
    assert res['state']=='potentially_eligible_unverified' and 'reward' not in res,r['campaign_id'];checks+=1
    assert r['calculation_approved'] is False and r['reward_amount'] is None
print(json.dumps({'campaigns':len(rules),'scenario_tests_passed':checks,'approved_reward_rules':0,'reward_amounts_computed':0},ensure_ascii=False))
