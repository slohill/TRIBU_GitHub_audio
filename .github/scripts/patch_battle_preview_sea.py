from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) Contour noir + blanc pour le dé attaquant encore en sélection.
css_anchor=".battleDie{min-width:25px;width:25px;height:25px;padding:0;border:0;border-radius:0;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:11px;color:#111;text-shadow:0 1px 1px #fff9;background-size:contain!important;background-repeat:no-repeat!important;background-position:center!important;box-shadow:none}"
css_new=css_anchor+"\n.battleDie.previewAttacker{box-shadow:0 0 0 2px #111,0 0 0 4px #fff!important}"
if '.battleDie.previewAttacker' not in s:
    if css_anchor not in s: raise SystemExit('battleDie CSS anchor missing')
    s=s.replace(css_anchor,css_new,1)

# 2) Une flotte peut attaquer une flotte adverse déjà présente sur la même aire maritime.
old="function legalSources(d){return neighbors(d).filter(s=>movableCount(s)>0)}"
new="""function legalSources(d){
 const src=neighbors(d).filter(s=>movableCount(s)>0);
 // Sur une aire maritime occupée par plusieurs joueurs, les unités du joueur actif
 // déjà présentes sur cette même aire sont une source légale : attaquer sur place
 // consomme bien un point de déplacement.
 if(isSea(d)&&seaEnemies(d).length&&movableCount(d)>0&&!src.includes(d))src.unshift(d);
 return src;
}"""
if old in s:
    s=s.replace(old,new,1)
elif 'src.unshift(d)' not in s:
    raise SystemExit('legalSources anchor missing')

# Helper pour l'aperçu avant validation du nombre d'unités.
anchor="""function seaEnemies(id){
  return Object.entries(G.sea[id].fleets)
    .filter(([i,n])=>+i!==G.active && n>0)
    .map(([i,n])=>({owner:+i,units:n}));
}"""
helper=anchor+"""
function previewBattleDefenders(id){
 if(battle||G.phase!=='play'||dest!==id)return [];
 if(isSea(id))return seaEnemies(id);
 const c=G.b[id];
 return c&&c.owner!==null&&c.owner!==G.active&&c.units>0?[{owner:c.owner,units:c.units}]:[];
}"""
if 'function previewBattleDefenders(id)' not in s:
    if anchor not in s: raise SystemExit('seaEnemies anchor missing')
    s=s.replace(anchor,helper,1)

# 3) Aperçu de bataille directement sur la case cible pendant la sélection.
old=""" const st=document.createElement('span');st.className='stack';
 const isPvpBattle=battle&&battle.target===id&&battle.defender!==null&&!battle.hostile&&(battle.kind==='land'||battle.kind==='sea');
 if(isSea(id)){
   if(!isPvpBattle){
     Object.entries(G.sea[id].fleets).forEach(([o,n])=>{
       const shown=visibleUnitsForSource(id,+o,n);
       if(shown>0)st.appendChild(die(+o,shown));
     });
   }
 }
 else{
   const c=G.b[id];
   const shown=c.owner!==null?visibleUnitsForSource(id,c.owner,c.units):0;
   if(!isPvpBattle&&c.owner!==null&&shown>0)st.appendChild(die(c.owner,shown,id));
 }
 if(st.children.length)b.appendChild(st);
 if(isPvpBattle){
   const pair=document.createElement('span');pair.className='battleDicePair';
   const ad=document.createElement('span');ad.className='battleDie attackerDie';ad.style.backgroundImage='url(\"'+factionDieImage(battle.attacker)+'\")';ad.textContent=battle.attackUnits;ad.title=p(battle.attacker).name+' : '+battle.attackUnits+' unité(s) attaquante(s)';
   const dd=document.createElement('span');dd.className='battleDie defenderDie';dd.style.backgroundImage='url(\"'+factionDieImage(battle.defender)+'\")';
   const defUnitValue=battle.defOriginalUnits*FACTIONS[p(battle.defender).faction].def+wallCount(battle.defender);
   dd.textContent=defUnitValue;dd.title=p(battle.defender).name+' : '+defUnitValue+' Défense affichée';
   pair.appendChild(ad);pair.appendChild(dd);b.appendChild(pair);
 }"""
new=""" const st=document.createElement('span');st.className='stack';
 const isPvpBattle=battle&&battle.target===id&&battle.defender!==null&&!battle.hostile&&(battle.kind==='land'||battle.kind==='sea');
 const previewDefenders=previewBattleDefenders(id),isPvpPreview=previewDefenders.length>0;
 if(isSea(id)){
   if(!isPvpBattle&&!isPvpPreview){
     Object.entries(G.sea[id].fleets).forEach(([o,n])=>{
       const shown=visibleUnitsForSource(id,+o,n);
       if(shown>0)st.appendChild(die(+o,shown));
     });
   }
 }
 else{
   const c=G.b[id];
   const shown=c.owner!==null?visibleUnitsForSource(id,c.owner,c.units):0;
   if(!isPvpBattle&&!isPvpPreview&&c.owner!==null&&shown>0)st.appendChild(die(c.owner,shown,id));
 }
 if(st.children.length)b.appendChild(st);
 if(isPvpPreview){
   const pair=document.createElement('span');pair.className='battleDicePair previewBattleDice';
   const ad=document.createElement('span');ad.className='battleDie attackerDie previewAttacker';ad.style.backgroundImage='url(\"'+factionDieImage(G.active)+'\")';ad.textContent=selected();ad.title=p(G.active).name+' : '+selected()+' unité(s) sélectionnée(s) — choix en cours';
   pair.appendChild(ad);
   previewDefenders.forEach(e=>{
     const dd=document.createElement('span');dd.className='battleDie defenderDie';dd.style.backgroundImage='url(\"'+factionDieImage(e.owner)+'\")';
     const defUnitValue=e.units*FACTIONS[p(e.owner).faction].def+(isSea(id)?0:wallCount(e.owner));
     dd.textContent=defUnitValue;dd.title=p(e.owner).name+' : '+defUnitValue+' Défense affichée';pair.appendChild(dd);
   });
   b.appendChild(pair);
 }
 if(isPvpBattle){
   const pair=document.createElement('span');pair.className='battleDicePair';
   const ad=document.createElement('span');ad.className='battleDie attackerDie';ad.style.backgroundImage='url(\"'+factionDieImage(battle.attacker)+'\")';ad.textContent=battle.attackUnits;ad.title=p(battle.attacker).name+' : '+battle.attackUnits+' unité(s) attaquante(s)';
   const dd=document.createElement('span');dd.className='battleDie defenderDie';dd.style.backgroundImage='url(\"'+factionDieImage(battle.defender)+'\")';
   const defUnitValue=battle.defOriginalUnits*FACTIONS[p(battle.defender).faction].def+wallCount(battle.defender);
   dd.textContent=defUnitValue;dd.title=p(battle.defender).name+' : '+defUnitValue+' Défense affichée';
   pair.appendChild(ad);pair.appendChild(dd);b.appendChild(pair);
 }"""
if 'isPvpPreview=previewDefenders.length>0' not in s:
    if old not in s: raise SystemExit('renderMap battle block anchor missing')
    s=s.replace(old,new,1)

old="if(dest===id&&selected()>0){const g=document.createElement('span');g.className='ghost';g.textContent=selected();b.appendChild(g)}"
new="if(dest===id&&selected()>0&&!isPvpPreview){const g=document.createElement('span');g.className='ghost';g.textContent=selected();b.appendChild(g)}"
if old in s:
    s=s.replace(old,new,1)
elif '!isPvpPreview' not in s:
    raise SystemExit('ghost preview anchor missing')

# 4) Sur une attaque "sur place", pas de bouton Naviguer absurde : seulement les cibles adverses.
old="""function openSeaChoice(n){
 battle={kind:'seaChoice',target:dest,total:n};
 const src=$('sources');if(src)src.innerHTML='';
 const hint=$('hint');if(hint)hint.textContent='Choisissez uniquement : Naviguer ou attaquer un joueur.';
 $('battlePanel').classList.remove('hidden');
 $('battleSideInfo').innerHTML='<b>Aire maritime '+dest+'</b><br>Des flottes adverses sont présentes.';
 $('priorityInfo').textContent='Choisissez : naviguer ou attaquer une flotte.';
 $('priorityTimer').textContent='';
 $('priorityStack').innerHTML='';
 const actions=$('tacticalButtons');actions.innerHTML='';
 const peaceful=document.createElement('button');
 peaceful.textContent='Naviguer';
 peaceful.onclick=()=>{const total=battle.total;hideBattle();battle=null;commitMovement(total,null)};
 actions.appendChild(peaceful);
 seaEnemies(dest).forEach(e=>{
"""
new="""function openSeaChoice(n){
 const sameAreaOnly=Object.keys(picks).filter(s=>picks[s]>0).every(s=>s===dest);
 battle={kind:'seaChoice',target:dest,total:n};
 const src=$('sources');if(src)src.innerHTML='';
 const hint=$('hint');if(hint)hint.textContent=sameAreaOnly?'Choisissez la flotte à attaquer.':'Choisissez uniquement : Naviguer ou attaquer un joueur.';
 $('battlePanel').classList.remove('hidden');
 $('battleSideInfo').innerHTML='<b>Aire maritime '+dest+'</b><br>Des flottes adverses sont présentes.';
 $('priorityInfo').textContent=sameAreaOnly?'Choisissez une flotte à attaquer.':'Choisissez : naviguer ou attaquer une flotte.';
 $('priorityTimer').textContent='';
 $('priorityStack').innerHTML='';
 const actions=$('tacticalButtons');actions.innerHTML='';
 if(!sameAreaOnly){
   const peaceful=document.createElement('button');
   peaceful.textContent='Naviguer';
   peaceful.onclick=()=>{const total=battle.total;hideBattle();battle=null;commitMovement(total,null)};
   actions.appendChild(peaceful);
 }
 seaEnemies(dest).forEach(e=>{
"""
if 'const sameAreaOnly=Object.keys(picks)' not in s:
    if old not in s: raise SystemExit('openSeaChoice anchor missing')
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
