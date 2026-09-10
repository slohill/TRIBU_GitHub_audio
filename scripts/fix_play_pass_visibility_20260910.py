from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function onlineLegacyLockControls(){
 if(!G||!G.online||!G.online.legacySync)return;
 const me=G.online.myPlayerIndex,mine=me===G.active&&!G.players[me].bot;
 const cardPause=priorityCardResolutionActive();
 const start=mine&&G.phase==='start'&&!paidDrawState&&!goldReaction&&!cardPause,recruiting=mine&&G.phase==='recruit'&&!cardPause,playing=mine&&G.phase==='play'&&!cardPause,oracleRoll=mine&&G.phase==='oracleRoll'&&!cardPause;
 const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 if(!mine||goldReaction||cardPause){['recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}
 if((goldReaction||cardPause)&&s)s.classList.add('hidden')
 if($('draw'))$('draw').disabled=!start;if($('harvest'))$('harvest').disabled=!start;if($('recruit'))$('recruit').disabled=!start;
 if($('endRecruit'))$('endRecruit').disabled=!recruiting;if($('resetRecruit'))$('resetRecruit').disabled=!recruiting;
 if($('toOracle'))$('toOracle').disabled=!playing;if($('roll'))$('roll').disabled=!oracleRoll;
 const map=$('map');if(map)map.style.pointerEvents='';
 const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineLegacyNotice\">🌐 Online — moteur original TRIBU synchronisé.</div>');
}
"""
new="""function onlineLegacyLockControls(){
 if(!G||!G.online||!G.online.legacySync)return;
 const me=G.online.myPlayerIndex,mine=me===G.active&&!G.players[me].bot;
 const cardPause=priorityCardResolutionActive();
 const start=mine&&G.phase==='start'&&!paidDrawState&&!goldReaction&&!cardPause,recruiting=mine&&G.phase==='recruit'&&!cardPause,playing=mine&&G.phase==='play'&&!cardPause,oracleRoll=mine&&G.phase==='oracleRoll'&&!cardPause;
 const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 const rb=$('recruitBox'),pb=$('playBox'),ob=$('oracleBox');
 if(rb)rb.classList.toggle('hidden',!recruiting||!!goldReaction);
 if(pb)pb.classList.toggle('hidden',!playing||!!goldReaction);
 if(ob)ob.classList.toggle('hidden',!oracleRoll||!!goldReaction);
 if((goldReaction||cardPause)&&s)s.classList.add('hidden')
 if($('draw'))$('draw').disabled=!start;if($('harvest'))$('harvest').disabled=!start;if($('recruit'))$('recruit').disabled=!start;
 if($('endRecruit'))$('endRecruit').disabled=!recruiting;if($('resetRecruit'))$('resetRecruit').disabled=!recruiting;
 if($('toOracle'))$('toOracle').disabled=!playing;if($('roll'))$('roll').disabled=!oracleRoll;
 const map=$('map');if(map)map.style.pointerEvents='';
 const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineLegacyNotice\">🌐 Online — moteur original TRIBU synchronisé.</div>');
}
"""
if old not in s: raise SystemExit('onlineLegacyLockControls block not found')
s=s.replace(old,new,1)
old2=""" if(agentModalState&&agentModalState.kind==='assassin'&&agentModalState.actor===me){
   openAgentModal('Assassin','Choisissez l’Agent adverse à assassiner.');
   const box=$('agentChoices');box.innerHTML='';
   assassinTargets(me).forEach(t=>{const b=document.createElement('button');b.textContent=p(t.owner).name+' — '+t.name;b.onclick=()=>resolveAssassin(t);box.appendChild(b)});
 }
}
"""
new2=""" if(agentModalState&&agentModalState.kind==='assassin'&&agentModalState.actor===me){
   openAgentModal('Assassin','Choisissez l’Agent adverse à assassiner.');
   const box=$('agentChoices');box.innerHTML='';
   assassinTargets(me).forEach(t=>{const b=document.createElement('button');b.textContent=p(t.owner).name+' — '+t.name;b.onclick=()=>resolveAssassin(t);box.appendChild(b)});
 }
 const agentOverlay=$('agentOverlay');
 if(agentModalState&&agentModalState.actor===me&&agentOverlay&&agentOverlay.classList.contains('hidden')){
   if(agentModalState.kind==='spy')useSpy(agentModalState.agentIndex);
   else if(agentModalState.kind==='thief')useThief(agentModalState.agentIndex);
 }
}
"""
if old2 not in s: raise SystemExit('restorePriorityCardOverlays tail not found')
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
