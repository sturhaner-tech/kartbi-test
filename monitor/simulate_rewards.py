#!/usr/bin/env python3
"""Strictly offline hypothetical reward calculator; never publish results."""
import json
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'data/offline_formula_lab.json').read_text(encoding='utf-8'))
def D(value): return Decimal(str(value))
def simulate(campaign_id, transactions, *, all_conditions_verified=False):
    if CONFIG.get('publicationEnabled') is not False or CONFIG.get('formulaApproval') != 'none':
        raise RuntimeError('Unsafe simulation configuration')
    if all_conditions_verified is not True:
        return {'state':'unknown','reward_try':None,'reason':'Eligibility, participation, card, merchant, POS and history not independently confirmed'}
    rule=next((r for r in CONFIG['rules'] if r['campaign_id']==campaign_id),None)
    if rule is None: return {'state':'unknown','reward_try':None,'reason':'No offline draft'}
    if not isinstance(transactions,list): raise TypeError('transactions must be a list')
    amounts=[]; eligible=[]
    for tx in transactions:
        a=D(tx['amount_try'])
        if not a.is_finite() or a<0: raise ValueError('Invalid amount')
        amounts.append(a)
        if tx.get('eligible') is True: eligible.append((a,tx))
    if rule.get('requires_separate_benefit_evaluation'):
        return {'state':'unknown','reward_try':None,'reason':'Distinct discount and loyalty points cannot be combined as cash'}
    threshold=D(rule['min_amount_try']); reward=D(rule['reward_try']); cap=D(rule['cap_try']);kind=rule['kind']
    qualifying=[(a,t) for a,t in eligible if a>=threshold]
    if kind=='first_qualifying_purchase': val=reward if qualifying else D(0)
    elif kind=='subsequent_qualifying_transactions':
        val=sum((reward+(D(rule.get('qr_extra_try',0)) if tx.get('qr') is True else D(0)) for a,tx in qualifying[1:]),D(0))
    elif kind=='per_qualifying_transaction': val=reward*len(qualifying)
    elif kind=='cumulative_threshold': val=reward if sum((a for a,t in eligible),D(0))>=threshold else D(0)
    elif kind=='cumulative_threshold_strict_below':
        ceiling=D(rule['per_transaction_max_exclusive_try'])
        val=reward if sum((a for a,t in eligible if a<ceiling),D(0))>=threshold else D(0)
    elif kind=='tiered_first_purchase':
        first=eligible[0][0] if eligible else D(0)
        val=max((D(t['reward_try']) for t in rule['tiers'] if first>=D(t['min_amount_try'])),default=D(0))
    else: raise ValueError('Unknown draft kind')
    val=min(val,cap)
    return {'state':'offline_simulation_only','reward_try':int(val),'reason':'Hypothetical calculation only, not a confirmed bank reward'}
