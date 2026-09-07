from pathlib import Path

p=Path('index.html'); s=p.read_text()
start=s.index("let onlineMoveDraft={target:null,picks:{}};")
end=s.index("function onlinePseudo(){", start)
new=r'''let onlineMoveDraft={target:null,picks:{}};
function onlineResetMoveDraft(){onlineMoveDraft={target:null,picks:{}}}
function onlineMovePool(id){return Number(onlineGameState&&onlineGameState.play&&onlineGameState.play.movePool&&onlineGameState.play.movePool[id]||0)}
function onlinePhysicalNeighbors(id){return isSea(id)?[...(SEA[id]||[]),...(PORTS[id]||[])]:[...(R[id]?R[id][3]:[]),...(R[id]?R[id][4]:[])]}
function onlineOwnUnits(id){const st=onlineGameState;if(!st)return 0;if(isSea(id))return Number(st.sea&&st.sea[id]&&st.sea[id].fleets&&st.sea[id].fleets[st.youIndex]||0);const c=st.board&&st.board[id];return c&&c.owner===st.youIndex?Number(c.units||0):0}
function onlineSeaEnemies(id){const st=onlineGameState,s=st&&st.sea&&st.sea[id];if(!s)return[];return Object.entries(s.fleets||{}).map(([owner,units])=>({owner:+owner,units:+units||0})).filter(x=>x.owner!==st.youIndex&&x.units>0)}
function onlineTargetEnemy(id){const c=onlineGameState&&onlineGameState.board&&onlineGameState.board[id];return !!(c&&(c.hostile||(c.owner!==null&&c.owner!==onlineGameState.youIndex&&c.units>0)))}
function onlineLegalMoveSources(target){
 const st=onlineGameState;if(!st||st.phase!=='play'||st.active!==st.youIndex||!POS[target])return[];
 const play=st.play||{},enemy=!isSea(target)&&onlineTargetEnemy(target);
 if(enemy&&(play.attacked||[]).includes(target))return[];
 if(!enemy&&Number((play.destinationUseCount||{})[target]||0)>=1)return[];
 const src=onlinePhysicalNeighbors(target).filter(id=>onlineOwnUnits(id)>0&&onlineMovePool(id)>0);
 if(isSea(target)&&onlineSeaEnemies(target).length&&onlineOwnUnits(target)>0&&onlineMovePool(target)>0&&!src.includes(target))src.unshift(target);
 return src;
}
function onlineMoveSelected(){return Object.values(onlineMoveDraft.picks||{}).reduce((a,b)=>a+(Number(b)||0),0)}
function onlineMoveAdjust(src,delta){const max=Math.min(onlineMovePool(src),onlineOwnUnits(src)),cur=Number(onlineMoveDraft.picks[src]||0),next=Math.max(0,Math.min(max,cur+delta));if(next)onlineMoveDraft.picks[src]=next;else delete onlineMoveDraft.picks[src];onlineRefreshPlayUi()}
function onlineMoveAll(src){const max=Math.min(onlineMovePool(src),onlineOwnUnits(src));if(max>0)onlineMoveDraft.picks[src]=max;onlineRefreshPlayUi()}
function onlineMoveClick(id){
 if(!onlineGameState||onlineGameState.phase!=='play'||onlineGameState.active!==onlineGameState.youIndex)return;
 const legal=onlineMoveDraft.target?onlineLegalMoveSources(onlineMoveDraft.target):[];
 if(onlineMoveDraft.target&&legal.includes(id)){onlineMoveAdjust(id,1);return}
 if(!onlineLegalMoveSources(id).length)return;
 onlineMoveDraft={target:id,picks:{}};onlineRefreshPlayUi();
}
function onlineFloatingActionPosition(target){const [x,y]=POS[target],sources=onlineLegalMoveSources(target),dirs=[{dx:0,dy:-7},{dx:0,dy:7},{dx:-6,dy:0},{dx:6,dy:0}];let best=dirs[0],score=-Infinity;dirs.forEach(d=>{const px=x+d.dx,py=y+d.dy;if(px<3||px>97||py<3||py>97)return;let nearest=999;sources.forEach(src=>{const [sx,sy]=POS[src];nearest=Math.min(nearest,Math.hypot(px-sx,py-sy))});if(nearest>score){score=nearest;best=d}});return[x+best.dx,y+best.dy]}
function onlineCloseSeaChoice(){hideBattle();battle=null}
function onlineSendMove(defender=null){
 const target=onlineMoveDraft.target;if(!target||onlineMoveSelected()<1)return;
 const sources={...onlineMoveDraft.picks},type=isSea(target)?'MOVE_SEA':'MOVE_LAND';onlineResetMoveDraft();onlineCloseSeaChoice();onlineGameAction(type,{target,sources,defender});
}
function onlineOpenSeaChoice(){
 const target=onlineMoveDraft.target,enemies=onlineSeaEnemies(target),sourceIds=Object.keys(onlineMoveDraft.picks).filter(x=>onlineMoveDraft.picks[x]>0),sameAreaOnly=sourceIds.length>0&&sourceIds.every(x=>x===target);
 if(!enemies.length){onlineSendMove(null);return}
 battle={kind:'seaChoice',target,total:onlineMoveSelected()};showBattle();
 $('battleSideInfo').innerHTML='<b>Aire maritime</b><br>Des flottes adverses sont présentes.';$('priorityInfo').textContent=sameAreaOnly?'Choisissez la flotte à attaquer.':'Choisissez : naviguer ou attaquer une flotte.';$('priorityTimer').textContent='';$('priorityStack').innerHTML='';
 const actions=$('tacticalButtons');actions.innerHTML='';
 if(!sameAreaOnly){const nav=document.createElement('button');nav.textContent='Naviguer';nav.onclick=()=>onlineSendMove(null);actions.appendChild(nav)}
 enemies.forEach(e=>{const b=document.createElement('button');b.textContent='Attaquer '+(G.players[e.owner]?G.players[e.owner].name:'joueur')+' ('+e.units+')';b.onclick=()=>onlineSendMove(e.owner);actions.appendChild(b)});
 const cancel=document.createElement('button');cancel.textContent='Annuler';cancel.onclick=onlineCloseSeaChoice;actions.appendChild(cancel)
}
function onlineCommitMove(){if(!onlineMoveDraft.target||onlineMoveSelected()<1)return;if(isSea(onlineMoveDraft.target)&&onlineSeaEnemies(onlineMoveDraft.target).length)return onlineOpenSeaChoice();onlineSendMove(null)}
function onlineDragonClick(id){const st=onlineGameState;if(!st||st.phase!=='oracleMove'||st.active!==st.youIndex)return;if(!onlinePhysicalNeighbors(st.dragon).includes(id))return;onlineGameAction('DRAGON_MOVE',{target:id})}
function onlineRefreshPlayUi(){
 const st=onlineGameState,map=$('map'),srcBox=$('sources'),hint=$('hint');if(!st||!map)return;
 map.querySelectorAll('.floatActions.onlineMoveFloat').forEach(x=>x.remove());
 map.querySelectorAll('.spot').forEach(x=>{x.classList.remove('onlineMoveAvailable','dest','src','srcHold','onlineOracleTarget');x.querySelectorAll('.sourceMinus,.onlineMovePickBadge,.ghost').forEach(b=>b.remove());x.onpointerdown=null;x.onpointerup=null;x.onpointerleave=null;x.onpointercancel=null;x.onclick=()=>onlineMoveClick(x.dataset.region)});
 if(srcBox){srcBox.innerHTML='';srcBox.style.display=''}
 if(st.status!=='playing'||st.active!==st.youIndex)return;
 if(st.phase==='play'){
   Object.keys(POS).forEach(id=>{if(onlineLegalMoveSources(id).length){const sp=map.querySelector('.spot[data-region="'+id+'"]');if(sp)sp.classList.add('onlineMoveAvailable')}});
   if(onlineMoveDraft.target){
     const target=onlineMoveDraft.target,t=map.querySelector('.spot[data-region="'+target+'"]');if(t){t.classList.add('dest');const total=onlineMoveSelected();if(total){const g=document.createElement('span');g.className='ghost';g.textContent=total;t.appendChild(g)}}
     onlineLegalMoveSources(target).forEach(id=>{const sp=map.querySelector('.spot[data-region="'+id+'"]');if(!sp)return;sp.classList.add('src','srcHold');const q=Number(onlineMoveDraft.picks[id]||0);if(q>0){const minus=document.createElement('button');minus.className='sourceMinus';minus.textContent='−';minus.title='Remettre 1 unité';minus.onpointerdown=e=>e.stopPropagation();minus.onclick=e=>{e.stopPropagation();onlineMoveAdjust(id,-1)};sp.appendChild(minus)}let timer=null,long=false;sp.onpointerdown=e=>{if(e.target!==sp)return;e.preventDefault();long=false;timer=setTimeout(()=>{long=true;onlineMoveAll(id)},480)};sp.onpointerup=()=>{if(timer)clearTimeout(timer)};sp.onpointerleave=()=>{if(timer)clearTimeout(timer)};sp.onpointercancel=()=>{if(timer)clearTimeout(timer)};sp.onclick=e=>{if(e.target!==sp)return;if(long){long=false;return}onlineMoveAdjust(id,1)}});
     if(hint)hint.innerHTML='Destination choisie — cliquez sur une source jaune (+1) ou maintenez pour tout sélectionner.';
     const fp=onlineFloatingActionPosition(target),box=document.createElement('div');box.className='floatActions onlineMoveFloat';box.style.left=fp[0]+'%';box.style.top=fp[1]+'%';box.innerHTML='<button class="no">✕</button><button class="yes">✓ '+onlineMoveSelected()+'</button>';const bs=box.querySelectorAll('button');bs[0].onclick=()=>{onlineResetMoveDraft();onlineRefreshPlayUi()};bs[1].onclick=onlineCommitMove;bs[1].disabled=onlineMoveSelected()===0;map.appendChild(box)
   }else if(hint)hint.textContent='Cliquez sur la destination.';
 }
 if(st.phase==='oracleMove')onlinePhysicalNeighbors(st.dragon).forEach(id=>{const sp=map.querySelector('.spot[data-region="'+id+'"]');if(sp){sp.classList.add('onlineOracleTarget');sp.onclick=()=>onlineDragonClick(id)}})
}
'''
s=s[:start]+new+s[end:]
p.write_text(s)

p=Path('server/server.js'); s=p.read_text()
insert="""function resolveBasicSeaBattle(game,index,target,n,defender){\n  const sea=game.sea[target],defUnits=Number(sea.fleets[defender]||0),coeff=FACTION_DEF[game.players[defender].faction]||1,d=defUnits*coeff,a=n;\n  let result='defense',survivors=0;\n  if(a>d){survivors=Math.min(n,a-d);if(d>=10)game.players[index].pvPermanent=(game.players[index].pvPermanent||0)+1;sea.fleets[defender]=0;sea.fleets[index]=(sea.fleets[index]||0)+survivors;result='attack'}\n  else{if(a>=10)game.players[defender].pvPermanent=(game.players[defender].pvPermanent||0)+1;survivors=a===d?1:Math.max(1,Math.min(defUnits,Math.ceil((d-a)/coeff)));sea.fleets[defender]=survivors}\n  return {kind:'seaBattle',target,attacker:index,defender,attack:a,defense:d,result,survivors};\n}\nfunction ownedMovableAt(game,index,id){if(isSeaId(id))return Number(game.sea[id]&&game.sea[id].fleets&&game.sea[id].fleets[index]||0);const c=game.board[id];return c&&c.owner===index?Number(c.units||0):0}\nfunction consumeAuthoritativeMove(game,index,id,q){if(isSeaId(id)){game.sea[id].fleets[index]=Math.max(0,Number(game.sea[id].fleets[index]||0)-q)}else{const c=game.board[id];c.units-=q;if(c.units<=0){c.units=0;c.owner=null;c.hostile=c.originalHostile}}game.movePool[id]=Math.max(0,Number(game.movePool[id]||0)-q)}\n"""
needle="function scheduleBotTurn(room){"
s=s.replace(needle,insert+needle,1)
old="""        const sc=game.board[src];if(!sc||sc.owner!==index)return rejectGameAction(ack,'Source de déplacement invalide.');\n        if(!(LAND_NEIGHBORS[target]||[]).includes(src))return rejectGameAction(ack,'Une source n’est pas adjacente à la destination.');\n        const available=Math.min(sc.units,Number((game.movePool||{})[src]||0));if(q>available)return rejectGameAction(ack,'Pas assez d’unités encore déplaçables sur une source.');\n        picks.push([src,q]);total+=q;\n      }\n      if(total<1)return rejectGameAction(ack,'Sélectionnez au moins une unité.');\n      picks.forEach(([src,q])=>{const sc=game.board[src];sc.units-=q;game.movePool[src]=Math.max(0,(game.movePool[src]||0)-q);if(sc.units===0){sc.owner=null;sc.hostile=sc.originalHostile}});\n"""
new2="""        if(!POS_PLACEHOLDER && false){}\n        if(!physicalNeighbors(target).includes(src))return rejectGameAction(ack,'Une source n’est pas adjacente à la destination.');\n        const available=Math.min(ownedMovableAt(game,index,src),Number((game.movePool||{})[src]||0));if(q>available)return rejectGameAction(ack,'Pas assez d’unités encore déplaçables sur une source.');\n        picks.push([src,q]);total+=q;\n      }\n      if(total<1)return rejectGameAction(ack,'Sélectionnez au moins une unité.');\n      picks.forEach(([src,q])=>consumeAuthoritativeMove(game,index,src,q));\n""".replace("        if(!POS_PLACEHOLDER && false){}\n","")
if old not in s: raise SystemExit('MOVE_LAND source block not found')
s=s.replace(old,new2,1)
marker="""    if(type==='END_PLAY'){\n"""
sea="""    if(type==='MOVE_SEA'){\n      if(game.phase!=='play')return rejectGameAction(ack,'Vous ne pouvez pas déplacer maintenant.');\n      const target=String(payload.target||''),sea=game.sea[target],raw=payload.sources&&typeof payload.sources==='object'?payload.sources:{},defender=payload.defender===null||payload.defender===undefined?null:Number(payload.defender);\n      if(!isSeaId(target)||!sea)return rejectGameAction(ack,'Destination maritime invalide.');\n      if(Number((game.destinationUseCount||{})[target]||0)>=1)return rejectGameAction(ack,'Cette aire maritime a déjà reçu un déplacement ce tour.');\n      const enemies=Object.entries(sea.fleets||{}).map(([o,u])=>({owner:+o,units:+u||0})).filter(x=>x.owner!==index&&x.units>0);\n      const picks=[];let total=0;\n      for(const [src,v] of Object.entries(raw)){const q=Math.max(0,Math.floor(Number(v)||0));if(!q)continue;const same=src===target&&enemies.length>0;if(!same&&!physicalNeighbors(target).includes(src))return rejectGameAction(ack,'Une source n’est pas adjacente à l’aire maritime.');const available=Math.min(ownedMovableAt(game,index,src),Number((game.movePool||{})[src]||0));if(q>available)return rejectGameAction(ack,'Pas assez d’unités encore déplaçables sur une source.');picks.push([src,q]);total+=q}\n      if(total<1)return rejectGameAction(ack,'Sélectionnez au moins une unité.');\n      if(defender!==null&&!enemies.some(e=>e.owner===defender))return rejectGameAction(ack,'Cette flotte ne peut pas être attaquée.');\n      if(defender===null&&picks.every(([src])=>src===target))return rejectGameAction(ack,'Choisissez une flotte à attaquer.');\n      picks.forEach(([src,q])=>consumeAuthoritativeMove(game,index,src,q));\n      if(defender===null){sea.fleets[index]=(sea.fleets[index]||0)+total;game.lastEvent={kind:'seaMove',target,player:index,units:total}}else game.lastEvent=resolveBasicSeaBattle(game,index,target,total,defender);\n      game.destinationUseCount=game.destinationUseCount||{};game.destinationUseCount[target]=(game.destinationUseCount[target]||0)+1;game.revision++;ack({ok:true,event:game.lastEvent});emitGame(room);return;\n    }\n"""
if marker not in s: raise SystemExit('END_PLAY marker missing')
s=s.replace(marker,sea+marker,1)
p.write_text(s)
