from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """function commerceViewer(){
 const h=commerceHumans();
 if(Number.isInteger(commerceViewerOverride)&&h.includes(commerceViewerOverride))return commerceViewerOverride;
 let v=localViewer();if(v==null||G.players[v].bot)return h.length?h[0]:G.active;return v
}"""
new = """function commerceViewer(){
 const h=commerceHumans();
 // Online : chaque navigateur ne peut consulter que l'interface Commerce de son propre joueur.
 if(G&&G.online&&G.online.legacySync){
   const v=localViewer();
   return Number.isInteger(v)&&h.includes(v)?v:(h[0]??G.active);
 }
 if(Number.isInteger(commerceViewerOverride)&&h.includes(commerceViewerOverride))return commerceViewerOverride;
 let v=localViewer();if(v==null||G.players[v].bot)return h.length?h[0]:G.active;return v
}"""
assert old in s, 'commerceViewer exact block not found'
s = s.replace(old, new, 1)

old = "function commerceExecute(d){\n if(d.status!=='accepted'||!commerceCanExecute(d))return;"
new = "function commerceSyncOnline(){if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()}\nfunction commerceExecute(d){\n if(d.status!=='accepted'||!commerceCanExecute(d))return;"
assert old in s, 'commerceExecute anchor not found'
s = s.replace(old, new, 1)

old = "d.status='done';log('Commerce : échange #'+d.id+' conclu entre '+p(d.from).name+' et '+p(d.to).name+'.');renderCommerce();render();\n}"
new = "d.status='done';log('Commerce : échange #'+d.id+' conclu entre '+p(d.from).name+' et '+p(d.to).name+'.');renderCommerce();render();commerceSyncOnline();\n}"
assert old in s, 'commerceExecute completion not found'
s = s.replace(old, new, 1)

old = "function commerceAccept(id){const d=commerceDeals.find(x=>x.id===id);if(!d||d.status!=='pending')return;d.status='accepted';d.expires=0;log(p(commerceViewer()).name+' accepte la négociation #'+d.id+'.');if(commerceCanExecute(d))commerceExecute(d);else{renderCommerce();render()}}"
new = "function commerceAccept(id){const d=commerceDeals.find(x=>x.id===id);if(!d||d.status!=='pending')return;d.status='accepted';d.expires=0;log(p(commerceViewer()).name+' accepte la négociation #'+d.id+'.');if(commerceCanExecute(d))commerceExecute(d);else{renderCommerce();render();commerceSyncOnline()}}"
assert old in s, 'commerceAccept exact block not found'
s = s.replace(old, new, 1)

old = "function commerceRefuse(id){const d=commerceDeals.find(x=>x.id===id);if(!d)return;d.status='refused';d.expires=0;log('Commerce : proposition #'+d.id+' refusée.');renderCommerce()}"
new = "function commerceRefuse(id){const d=commerceDeals.find(x=>x.id===id);if(!d)return;d.status='refused';d.expires=0;log('Commerce : proposition #'+d.id+' refusée.');renderCommerce();commerceSyncOnline()}"
assert old in s, 'commerceRefuse exact block not found'
s = s.replace(old, new, 1)

old = "function commerceReopenExpired(id){const d=commerceDeals.find(x=>x.id===id);if(!d||d.closed||d.type==='show'||d.status!=='expired')return;d.status='pending';d.expires=Date.now()+120000;log('Commerce : négociation #'+d.id+' réouverte pour 2 minutes.');renderCommerce();render()}"
new = "function commerceReopenExpired(id){const d=commerceDeals.find(x=>x.id===id);if(!d||d.closed||d.type==='show'||d.status!=='expired')return;d.status='pending';d.expires=Date.now()+120000;log('Commerce : négociation #'+d.id+' réouverte pour 2 minutes.');renderCommerce();render();commerceSyncOnline()}"
assert old in s, 'commerceReopenExpired exact block not found'
s = s.replace(old, new, 1)

old = "function commerceOpen(){if(!G)return;const lv=localViewer(),h=commerceHumans();commerceViewerOverride=h.includes(lv)?lv:(h[0]??null);$('commerceOverlay').classList.remove('hidden');commerceDraft=null;renderCommerce()}"
new = "function commerceOpen(){if(!G)return;const lv=localViewer(),h=commerceHumans();commerceViewerOverride=(G.online&&G.online.legacySync)?null:(h.includes(lv)?lv:(h[0]??null));$('commerceOverlay').classList.remove('hidden');commerceDraft=null;renderCommerce()}"
assert old in s, 'commerceOpen exact block not found'
s = s.replace(old, new, 1)

old = "commerceDraft=null;renderCommerce();render();\n}"
new = "commerceDraft=null;renderCommerce();render();commerceSyncOnline();\n}"
# This exact text first occurs at commerceSubmit in the commerce block after its log.
commerce_start = s.index('function commerceSubmit()')
idx = s.find(old, commerce_start)
assert idx >= 0, 'commerceSubmit completion not found'
s = s[:idx] + new + s[idx+len(old):]

old = "let viewerBar=humans.length>1?'<div class=\"commerceBox\" style=\"margin-bottom:10px\"><b>Commerce consulté par :</b><div class=\"commerceActions\">'+humans.map(i=>'<button data-commerce-viewer=\"'+i+'\" '+(i===v?'disabled':'')+'>'+p(i).name+'</button>').join('')+'</div><div class=\"commerceHint\">Sur le même appareil, choisissez ici le joueur qui consulte ses propositions et contre-propositions.</div></div>':'';"
new = "let viewerBar=(!(G.online&&G.online.legacySync)&&humans.length>1)?'<div class=\"commerceBox\" style=\"margin-bottom:10px\"><b>Commerce consulté par :</b><div class=\"commerceActions\">'+humans.map(i=>'<button data-commerce-viewer=\"'+i+'\" '+(i===v?'disabled':'')+'>'+p(i).name+'</button>').join('')+'</div><div class=\"commerceHint\">Sur le même appareil, choisissez ici le joueur qui consulte ses propositions et contre-propositions.</div></div>':'';"
assert old in s, 'viewerBar exact line not found'
s = s.replace(old, new, 1)

old = "document.querySelectorAll('[data-seen]').forEach(b=>b.onclick=()=>{const d=commerceDeals.find(x=>x.id===+b.dataset.seen);if(d){d.expires=0;d.status='seen';renderCommerce();render()}});"
new = "document.querySelectorAll('[data-seen]').forEach(b=>b.onclick=()=>{const d=commerceDeals.find(x=>x.id===+b.dataset.seen);if(d){d.expires=0;d.status='seen';renderCommerce();render();commerceSyncOnline()}});"
assert old in s, 'seen handler exact line not found'
s = s.replace(old, new, 1)

# Structural invariants requested by the project.
assert "$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};" in s
assert 'Naviguer' in s
assert 'commerceDeals,commerceSeq' in s
assert "if(G&&G.online&&G.online.legacySync){\n   const v=localViewer();" in s
assert "commerceSyncOnline();" in s
assert "(!(G.online&&G.online.legacySync)&&humans.length>1)" in s

p.write_text(s, encoding='utf-8')
print('Commerce Online patch applied')
