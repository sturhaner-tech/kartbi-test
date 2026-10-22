const fs=require('fs'),assert=require('assert');
const h=fs.readFileSync('index.html','utf8');
const feed=JSON.parse(fs.readFileSync('data/official_previews.json','utf8'));
let n=0;function ok(label,cond){assert(cond,label);n++;console.log('PASS '+label)}
ok('mobile viewport',/name="viewport"[^>]*width=device-width/.test(h));
ok('mobile bottom navigation',h.includes('position:fixed;bottom:0'));
ok('focus visibility',h.includes(':focus-visible'));
ok('touch card selector',h.includes('.cardpick input[type=checkbox]'));
ok('real comparison used',h.includes('function compareView(){return compareRealView();}'));
ok('category not widened',h.includes('(!category||c.category===category)'));
ok('today defaults to device date',/date:new Date\(\)\.toLocaleDateString\('sv-SE'\)/.test(h));
ok('unknown conditions do not promise earnings',h.includes('Kazanç hesaplanmıyor'));
ok('user cards required',h.includes('Önce kartlarını seç'));
ok('amount and date inputs',h.includes('Alışveriş tutarı (TL)')&&h.includes('type="date"'));
ok('campaigns exist',feed.campaigns.length===18);
ok('no confirmed reward displayed in real view',h.slice(h.indexOf('function compareRealView(){'),h.indexOf('function compareView(){')).includes('Puan ve indirimler TL olarak toplanmaz'));
console.log('SUCCESS '+n+' static mobile UI checks; not a browser end-to-end test');
