import json
from pathlib import Path
from assess_eligibility import assess
root=Path(__file__).resolve().parents[1]
rules=json.loads((root/'data/provisional_rule_gates.json').read_text(encoding='utf-8'))['rules']
assert len(rules)==18
count=0
for r in rules:
    fields=r['required_evidence']
    base={'date':r['start']}
    checks=[
      (base,'unknown'),
      ({**base,fields[0]:False},'ineligible'),
      ({**base,**{f:True for f in fields}},'potentially_eligible_unverified'),
      ({**base,**{f:True for f in fields},fields[0]:None},'unknown'),
      ({**base,fields[0]:'yes'},'unknown'),
      ({**base,**{f:True for f in fields},fields[0]:False},'ineligible'),
      ({'date':'not-a-date'},'unknown'),
      ({'date':'2027-01-01'},'ineligible')
    ]
    for context,expected in checks:
      result=assess(r,context)
      assert result['state']==expected,(r['campaign_id'],result,expected)
      assert 'reward' not in result and 'amount' not in result
      count+=1
print(json.dumps({'campaigns':len(rules),'eligibility_scenarios_passed':count,'approved_reward_rules':0}))
