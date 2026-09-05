from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""function previewBattleDefenders(id){
 if(battle||G.phase!=='play'||dest!==id)return [];
 if(isSea(id))return seaEnemies(id);
 const c=G.b[id];
 return c&&c.owner!==null&&c.owner!==G.active&&c.units>0?[{owner:c.owner,units:c.units}]:[];
}"""
new="""function previewBattleDefenders(id){
 if(battle||G.phase!=='play'||dest!==id)return [];
 if(isSea(id))return seaEnemies(id);
 const c=G.b[id];
 return c&&c.owner!==null&&c.owner!==G.active&&c.units>0?[{owner:c.owner,units:c.units}]:[];
}
function previewBattleAttackerUnits(id){
 if(!previewBattleDefenders(id).length)return 0;
 return selected();
}"""
if old not in s: raise SystemExit('preview helper anchor missing')
s=s.replace(old,new,1)

old="""   const ad=document.createElement('span');ad.className='battleDie attackerDie previewAttacker';ad.style.backgroundImage='url(\"'+factionDieImage(G.active)+'\")';ad.textContent=selected();ad.title=p(G.active).name+' : '+selected()+' unité(s) sélectionnée(s) — choix en cours';"""
new="""   const ad=document.createElement('span');ad.className='battleDie attackerDie previewAttacker';ad.style.backgroundImage='url(\"'+factionDieImage(G.active)+'\")';ad.textContent=previewBattleAttackerUnits(id);ad.title=p(G.active).name+' : '+previewBattleAttackerUnits(id)+' unité(s) sélectionnée(s) — choix en cours';"""
if old not in s: raise SystemExit('preview attacker anchor missing')
s=s.replace(old,new,1)

old=""".battleDie.previewAttacker{box-shadow:0 0 0 2px #111,0 0 0 4px #fff!important}"""
new=""".battleDie.previewAttacker{min-width:21px;width:21px;height:21px;font-size:10px;align-self:center;box-shadow:0 0 0 2px #111,0 0 0 4px #fff!important}"""
if old not in s: raise SystemExit('preview css anchor missing')
s=s.replace(old,new,1)

old=""" const stormActive=G.oracleActive!==null&&ORACLES[G.oracleActive].name==='Tempête en mer';
 const involvesSea=isSea(target)||sourceIds.some(isSea);
 if(stormActive&&involvesSea&&!seaStormState){
   const stormRoll=1+Math.floor(Math.random()*6);
   recordDestinationUse(target);
   log('🌊 Tempête en mer vers '+target+' : dé '+stormRoll+'.');
   if(stormRoll%2===1){
     // Les unités annoncées sont perdues : on les retire des sources, sans les placer.
     consumePickedSources();
     log(n+' unité(s) sont perdues dans la Tempête en mer.');
     dest=null;picks={};checkDecimations();render();return;
   }
   // Pair : le déplacement se poursuit normalement.
 }"""
new=""" const stormActive=G.oracleActive!==null&&ORACLES[G.oracleActive].name==='Tempête en mer';
 // Une attaque sur une aire maritime est un déplacement, y compris pour les unités
 // déjà présentes sur cette aire. Toutes les unités sélectionnées (sur place ou
 // adjacentes) passent donc ensemble le test de Tempête avant le lancement du combat.
 const involvesSea=isSea(target)||sourceIds.some(isSea);
 if(stormActive&&involvesSea&&!seaStormState){
   const stormRoll=1+Math.floor(Math.random()*6);
   recordDestinationUse(target);
   log('🌊 Tempête en mer vers '+target+' : dé '+stormRoll+'.');
   if(stormRoll%2===1){
     const lost=consumePickedSources().length;
     log(lost+' unité(s) sont perdues dans la Tempête en mer.');
     dest=null;picks={};checkDecimations();render();return;
   }
   // Pair : le déplacement/attaque se poursuit normalement avec toute la sélection.
 }"""
if old not in s: raise SystemExit('storm anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
