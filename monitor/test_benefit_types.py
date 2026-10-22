import json
from pathlib import Path
from simulate_rewards import simulate
root=Path(__file__).resolve().parents[1]
b=json.loads((root/'data/benefit_types.json').read_text())
assert b['publicationEnabled'] is False
c=b['campaigns'][0]
assert c['campaign_id']=='yk-ehamal' and c['do_not_sum'] is True
assert {x['type'] for x in c['components']}=={'merchant_discount','worldpuan'}
assert all(x['cash_equivalent_approved'] is False for x in c['components'])
r=simulate('yk-ehamal',[{'amount_try':3500,'eligible':True}],all_conditions_verified=True)
assert r['state']=='unknown' and r['reward_try'] is None
print('Benefit separation tests passed')
