#!/usr/bin/env python3
"""Validate tracked review decisions against current campaign IDs and source URLs.
No approval is interpreted as permission to publish campaign terms.
"""
import json, pathlib, sys, datetime
root=pathlib.Path(__file__).resolve().parents[1]
feed=json.loads((root/'data/official_previews.json').read_text(encoding='utf-8'))
known={c['id']:c for c in feed['campaigns']}
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'monitor/review_decisions.json'
try: data=json.loads(path.read_text(encoding='utf-8'))
except (OSError,ValueError) as exc:sys.exit(f'Invalid review file: {exc}')
errors=[]
if not isinstance(data,dict) or not isinstance(data.get('decisions'),dict):sys.exit('Expected object with decisions map')
for cid,d in data['decisions'].items():
    if cid not in known:errors.append(f'{cid}: unknown campaign');continue
    if not isinstance(d,dict):errors.append(f'{cid}: decision must be an object');continue
    if d.get('status') not in ('pending','reviewed','followup'):errors.append(f'{cid}: invalid status')
    if d.get('source_url')!=known[cid]['source']:errors.append(f'{cid}: source URL mismatch; re-review required')
    if not isinstance(d.get('source_checked_at'),str) or not d['source_checked_at']:errors.append(f'{cid}: source_checked_at missing')
    if not isinstance(d.get('note',''),str) or len(d.get('note',''))>3000:errors.append(f'{cid}: note too long or invalid')
    if d.get('status')=='reviewed' and not d.get('note','').strip():errors.append(f'{cid}: reviewed requires written evidence note')
if errors:
    print('Review validation failed:');print('\n'.join(errors));sys.exit(1)
print(f"Review file valid: {len(data['decisions'])} decisions; none published automatically.")
