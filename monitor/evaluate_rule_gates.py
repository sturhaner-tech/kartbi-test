#!/usr/bin/env python3
"""Conservative scenario triage. Never computes or approves monetary rewards."""
from datetime import date

def evaluate(rule, scenario):
    if rule.get('calculation_approved') is not False or rule.get('rule_status') != 'provisional' or rule.get('reward_amount') is not None:
        return {'state':'unknown','reason':'Kuralın onay durumu beklenmedik'}
    day = scenario.get('date')
    if not day:
        return {'state':'unknown','reason':'İşlem tarihi bilinmiyor'}
    try:
        date.fromisoformat(day)
    except (ValueError,TypeError):
        return {'state':'unknown','reason':'İşlem tarihi geçersiz'}
    if day < rule['start'] or day > rule['end']:
        return {'state':'ineligible','reason':'Kampanya tarihleri dışında'}
    # Explicit false is a negative finding, missing evidence is unknown.
    for field in rule['required_evidence']:
        if scenario.get(field) is False:
            return {'state':'ineligible','reason':field+' koşulu sağlanmıyor (kullanıcı beyanı)'}
    missing=[field for field in rule['required_evidence'] if scenario.get(field) is not True]
    if missing:
        return {'state':'unknown','reason':'Doğrulanmamış koşullar: '+', '.join(missing)}
    return {'state':'potentially_eligible_unverified','reason':'Beyan edilen ön koşullar olumlu; banka doğrulaması ve ödül hesabı bekliyor'}
