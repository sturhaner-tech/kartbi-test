#!/usr/bin/env python3
import json
from pathlib import Path
from simulate_rewards import simulate, CONFIG
root=Path(__file__).resolve().parents[1]
assert CONFIG['publicationEnabled'] is False
assert CONFIG['formulaApproval']=='none'
feed=json.loads((root/'data/official_previews.json').read_text(encoding='utf-8'))
assert all(not c.get('calculationApproved',False) for c in feed['campaigns'])
assert len({r['campaign_id'] for r in CONFIG['rules']})==len(CONFIG['rules'])
assert {r['campaign_id'] for r in CONFIG['rules']} <= {c['id'] for c in feed['campaigns']}
def tx(n,qr=False,eligible=True):return {'amount_try':n,'qr':qr,'eligible':eligible}
assert simulate('ak-market',[tx(2750)],all_conditions_verified=True)['reward_try']==0
assert simulate('ak-market',[tx(2750),tx(2750)],all_conditions_verified=True)['reward_try']==75
assert simulate('ak-market',[tx(2750),tx(2750,True)],all_conditions_verified=True)['reward_try']==100
assert simulate('ak-market',[tx(2750)]+[tx(2750,True)]*30,all_conditions_verified=True)['reward_try']==1000
assert simulate('ak-market',[tx(2750),tx(2749),tx(2750)],all_conditions_verified=True)['reward_try']==75
assert simulate('ak-flo',[tx(2499)],all_conditions_verified=True)['reward_try']==0
assert simulate('ak-flo',[tx(2500)],all_conditions_verified=True)['reward_try']==300
assert simulate('ak-flo',[tx(2500)]*3,all_conditions_verified=True)['reward_try']==300
assert simulate('qnb-sporthink',[tx(5000)],all_conditions_verified=True)['reward_try']==500
assert simulate('qnb-sporthink',[tx(4999)],all_conditions_verified=True)['reward_try']==0
assert simulate('ak-flo',[tx(2500)])['reward_try'] is None
assert simulate('unknown',[tx(2500)],all_conditions_verified=True)['reward_try'] is None
print('12 offline simulation checks passed; live publication remains disabled')
