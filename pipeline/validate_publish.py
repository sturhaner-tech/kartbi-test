#!/usr/bin/env python3
"""Validate approved campaign records supplied through an authorized channel.
Usage: python pipeline/validate_publish.py input.json data/campaigns.json
Input: list of records or {"campaigns": [...]}.
No bank scraping or network access is performed.
"""
import json,sys,datetime,pathlib,urllib.parse
BANKS={'Garanti BBVA','Yapı Kredi','Akbank','İş Bankası','Halkbank','QNB'}
REQUIRED={'id','bank','title','category','start','end','source','status','reviewStatus','usagePermission','reviewedBy','reviewedAt','evidenceCheckedAt'}
def check(c):
    errors=[]
    for field in REQUIRED:
        if not isinstance(c.get(field),str) or not c[field].strip(): errors.append(f'{field}: required text')
    if c.get('bank') not in BANKS:errors.append('unknown bank')
    if c.get('status')!='published' or c.get('reviewStatus')!='approved' or c.get('usagePermission')!='approved': errors.append('publication, human review and usage permission must all be approved')
    for field in ('start','end','reviewedAt','evidenceCheckedAt'):
        try:datetime.date.fromisoformat(c[field])
        except (ValueError,KeyError,TypeError):errors.append(field+': invalid YYYY-MM-DD')
    if c.get('start','')>c.get('end',''):errors.append('start after end')
    u=urllib.parse.urlparse(c.get('source',''))
    if u.scheme!='https' or not u.hostname:errors.append('source must be HTTPS')
    if not isinstance(c.get('includedProducts',[]),list) or not isinstance(c.get('excludedProducts',[]),list):errors.append('product lists required')
    for k in ('minimumSpend','rewardAmount','rewardRate','rewardCap'):
        if k in c and (isinstance(c[k],bool) or not isinstance(c[k],(int,float)) or c[k]<0):errors.append(k+': must be nonnegative number')
    return errors

def main():
    if len(sys.argv)!=3:sys.exit(__doc__)
    raw=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    records=raw['campaigns'] if isinstance(raw,dict) else raw
    if not isinstance(records,list):sys.exit('Input must be an array')
    problems=[];ids=set()
    for i,c in enumerate(records):
        if not isinstance(c,dict):problems.append(f'{i}: not an object');continue
        if c.get('id') in ids:problems.append(f'{i}: duplicate id')
        ids.add(c.get('id'))
        problems += [f'{i} ({c.get("id","?")}): {e}' for e in check(c)]
    if problems:sys.exit('Validation failed; no output written:\n'+'\n'.join(problems))
    out={'schemaVersion':1,'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'campaigns':records}
    dest=pathlib.Path(sys.argv[2]);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Published {len(records)} human-reviewed, authorized campaign records to {dest}')
if __name__=='__main__':main()
