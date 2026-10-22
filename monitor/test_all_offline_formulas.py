import json
from pathlib import Path
from simulate_rewards import simulate
root=Path(__file__).resolve().parents[1]
config=json.loads((root/'data/offline_formula_lab.json').read_text(encoding='utf-8'))
feed=json.loads((root/'data/official_previews.json').read_text(encoding='utf-8'))
assert config['publicationEnabled'] is False and config['formulaApproval']=='none'
assert len(config['rules'])==18
assert {r['campaign_id'] for r in config['rules']}=={c['id'] for c in feed['campaigns']}
assert not any(c.get('calculationApproved',False) for c in feed['campaigns'])
checks=0
for rule in config['rules']:
    id=rule['campaign_id']; low=max(0,rule['min_amount_try']-1)
    for txs in [[],[{'amount_try':low,'eligible':True}],[{'amount_try':rule['min_amount_try'],'eligible':True}],[{'amount_try':1000000,'eligible':True}]*10]:
        unknown=simulate(id,txs)
        assert unknown['state']=='unknown' and unknown['reward_try'] is None
        out=simulate(id,txs,all_conditions_verified=True)
        if rule.get('requires_separate_benefit_evaluation'):
            assert out['state']=='unknown' and out['reward_try'] is None
        else:
            assert out['state']=='offline_simulation_only' and 0<=out['reward_try']<=rule['cap_try']
        checks+=2
    try: simulate(id,[{'amount_try':-1,'eligible':True}],all_conditions_verified=True)
    except ValueError: checks+=1
    else: raise AssertionError('negative transaction accepted')
assert simulate('is-market',[{'amount_try':1499,'eligible':True}]*11,all_conditions_verified=True)['reward_try']==750
assert simulate('is-market',[{'amount_try':1500,'eligible':True}]*11,all_conditions_verified=True)['reward_try']==0
assert simulate('ak-mobilya-v29',[{'amount_try':120000,'eligible':True}],all_conditions_verified=True)['reward_try']==2000
assert simulate('qnb-zara',[{'amount_try':6500,'eligible':True}]*2,all_conditions_verified=True)['reward_try']==1000
print(f'{checks+4} offline draft checks passed; 18 formulas; 0 approved; publication disabled')
