const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const start=html.indexOf('function v48Check(c){');
// V53 signature may include an optional selected date
const a=html.indexOf('function v48Check('),b=html.indexOf('function legacyCompareView(){',a);
assert(a>=0&&b>a);
const feed=JSON.parse(fs.readFileSync('data/official_previews.json','utf8')).campaigns;
const gates=JSON.parse(fs.readFileSync('data/provisional_rule_gates.json','utf8'));
const rules=Array.isArray(gates)?gates:(gates.rules||gates.campaigns||[]);
const context={scenario:{date:'2026-10-15',category:'',amount:3000},v48Answers:{},V48_RULES:rules,V48_LABELS:{},officialPreviews:feed,CARDS:[],S:{selected:[]},esc:x=>String(x),officialLink:()=>'',console};
vm.createContext(context);vm.runInContext(html.slice(a,b),context);
let n=0;const test=(cond,msg)=>{assert(cond,msg);n++};
test(feed.length===18&&rules.length===18,'18 campaign records');
for(const c of feed){
 const r=rules.find(x=>x.campaign_id===c.id);test(!!r,'missing rule '+c.id);
 context.scenario.date=c.start;delete context.v48Answers[c.id];
 test(context.v48Check(c).state==='unknown','missing evidence '+c.id);
 for(const f of r.required_evidence){
  context.v48Answers[c.id]={[f]:false};test(context.v48Check(c).state==='ineligible','negative '+c.id+' '+f);
 }
 context.v48Answers[c.id]=Object.fromEntries(r.required_evidence.map(f=>[f,true]));
 test(context.v48Check(c).state==='potential','all affirmative '+c.id);
 test(context.v48Check(c,'2026-02-30').state==='unknown','invalid calendar date '+c.id);
 test(context.v48Check(c,'2026-11-01').state==='ineligible','expired '+c.id);
 const card={id:'x',bank:c.bank,family:(c.eligibleFamilies||[])[0]||'test',product:'test'};
 const row=context.v50Rows([card],[c],c.end,c.category)[0];
 test(row.items.length===1,'end boundary '+c.id);
 test(row.counts.potential===1,'date passed to eligibility '+c.id);
 test(context.v50Rows([card],[c],c.start,'Not-this-category')[0].items.length===0,'category filtering '+c.id);
}
console.log('V53 SUCCESS: '+n+' scenario assertions across '+feed.length+' campaigns');
