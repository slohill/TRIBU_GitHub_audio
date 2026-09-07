from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function onlineSingleEngineLock(){
 if(onlineGameState&&onlineGameState.status==='setup'){const mapEl=$('map'),hand=$('hand');if(mapEl)mapEl.style.pointerEvents='';if(hand)hand.style.pointerEvents='';return}
 if(!G||!G.online||!G.online.singleEngine)return;const can=onlineSingleEngineCanAct(),mapEl=$('map'),hand=$('hand');if(mapEl)mapEl.style.pointerEvents=can?'':'none';if(hand)hand.style.pointerEvents=can?'':'none';
 if(!can)['draw','harvest','recruit','resetRecruit','endRecruit','toOracle','roll'].forEach(id=>{const b=$(id);if(b)b.disabled=true});
 const n=$('status');if(n&&!n.querySelector('.onlineSingleEngineNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineSingleEngineNotice\">🌐 Online — règles du jeu original synchronisées.</div>');
}"""
new="""function onlineSingleEngineLock(){
 if(onlineGameState&&onlineGameState.status==='setup'){const mapEl=$('map'),hand=$('hand');if(mapEl)mapEl.style.pointerEvents='';if(hand)hand.style.pointerEvents='';return}
 if(!G||!G.online||!G.online.singleEngine)return;
 const can=onlineSingleEngineCanAct(),phase=G.phase,mapEl=$('map'),hand=$('hand');if(mapEl)mapEl.style.pointerEvents=can?'':'none';if(hand)hand.style.pointerEvents=can?'':'none';
 const start=can&&phase==='start',recruiting=can&&phase==='recruit',playing=can&&phase==='play',oracleRoll=can&&phase==='oracleRoll';
 $('startTurn').classList.toggle('hidden',!start);
 $('draw').disabled=!start;$('harvest').disabled=!start;$('recruit').disabled=!start;
 const rr=$('resetRecruit');if(rr)rr.disabled=!recruiting;$('endRecruit').disabled=!recruiting;
 $('toOracle').disabled=!playing;$('roll').disabled=!oracleRoll;
 const n=$('status');if(n&&!n.querySelector('.onlineSingleEngineNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineSingleEngineNotice\">🌐 Online — règles du jeu original synchronisées.</div>');
}"""
if old not in s: raise SystemExit('onlineSingleEngineLock anchor not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('start actions lock fixed')
