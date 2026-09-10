from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old_move=""" }else if(G.phase==='play'&&dest&&!isSea(dest)&&!(battle&&battle.kind==='seaChoice')){
   $('hint').innerHTML='Destination <b>'+dest+'</b> — cliquez sur plusieurs sources jaunes si besoin.';
   legalSources(dest).forEach(s=>{const d=document.createElement('div');d.className='source';d.innerHTML='<button title=\"Clic : +1 / maintenir sur la région : tout\">'+s+'</button><button>−</button><span>'+(picks[s]||0)+'/'+movableCount(s)+'</span><button>+</button><button>Tout</button>';const bs=d.querySelectorAll('button');bs[0].onclick=()=>adjust(s,1);bs[1].onclick=()=>adjust(s,-1);bs[2].onclick=()=>adjust(s,1);bs[3].onclick=()=>pickAllFromSource(s);src.appendChild(d)})
 }else if(G.phase==='play'&&dest&&isSea(dest)){"""
new_move=""" }else if(G.phase==='play'&&dest&&!isSea(dest)&&!(battle&&battle.kind==='seaChoice')){
   $('hint').innerHTML='Destination <b>'+dest+'</b> — sélectionnez vos unités directement sur la map.';
 }else if(G.phase==='play'&&dest&&isSea(dest)){"""
if old_move not in s:
    raise SystemExit('manual movement block not found')
s=s.replace(old_move,new_move,1)

old_shadow="""function shadowTargetLegal(r){
 if(!shadowState||shadowState.stage!=='target'||isSea(r))return false;
 const s=shadowState,c=G.b[r];
 // Une région actuellement en bataille ne peut jamais être ciblée par Section de l'ombre.
 // En revanche, n'importe quel joueur peut lancer sa Section ailleurs pendant la bataille.
 if(s.parentBattle&&s.parentBattle.target===r)return false;
 if(c.owner===s.player)return false;
 return true;
}"""
new_shadow="""function shadowTargetLegal(r){
 if(!shadowState||shadowState.stage!=='target'||isSea(r))return false;
 const s=shadowState,c=G.b[r];
 // Pendant une bataille, la région attaquée est une cible légale uniquement pour
 // son défenseur : Section de l'ombre peut alors y amener jusqu'à 6 unités en défense.
 if(s.parentBattle&&s.parentBattle.target===r){
   return s.parentBattle.kind==='land'&&s.parentBattle.defender===s.player&&c.owner===s.player;
 }
 if(c.owner===s.player)return false;
 return true;
}"""
if old_shadow not in s:
    raise SystemExit('shadowTargetLegal block not found')
s=s.replace(old_shadow,new_shadow,1)

path.write_text(s,encoding='utf-8')
