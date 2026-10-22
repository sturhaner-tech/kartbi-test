#!/usr/bin/env python3
"""V47: Three-valued eligibility triage; never returns money or approval."""
from datetime import date

ALLOWED = {True, False, None}

def assess(rule, context):
    if rule.get('rule_status') != 'provisional' or rule.get('calculation_approved') is not False or rule.get('reward_amount') is not None:
        return {'state':'unknown','reason':'Kural onayı doğrulanamadı','missing':[]}
    day=context.get('date')
    try:
        when=date.fromisoformat(day)
        start=date.fromisoformat(rule['start'])
        end=date.fromisoformat(rule['end'])
    except (TypeError,ValueError,KeyError):
        return {'state':'unknown','reason':'Tarih eksik veya geçersiz','missing':['date']}
    if not start<=when<=end:
        return {'state':'ineligible','reason':'Kampanya tarihleri dışında','missing':[]}
    fields=rule.get('required_evidence',[])
    if not isinstance(fields,list) or not fields or len(fields)!=len(set(fields)):
        return {'state':'unknown','reason':'Koşul şeması geçersiz','missing':[]}
    invalid=[k for k in fields if context.get(k) not in ALLOWED]
    if invalid:
        return {'state':'unknown','reason':'Geçersiz koşul değeri','missing':invalid}
    negative=[k for k in fields if context.get(k) is False]
    if negative:
        return {'state':'ineligible','reason':'Kullanıcı beyanına göre sağlanmayan koşul','failed':negative,'missing':[]}
    missing=[k for k in fields if context.get(k) is not True]
    if missing:
        return {'state':'unknown','reason':'Doğrulanmamış koşullar','missing':missing}
    return {'state':'potentially_eligible_unverified','reason':'Yalnızca kullanıcı beyanına göre ön uygunluk; banka teyidi gerekir','missing':[]}
