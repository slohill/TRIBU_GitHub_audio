from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function onlineDisplayGame(state){const topRestart=$('restart');if(topRestart)topRestart.classList.add('hidden');"""
if old not in s: raise SystemExit('onlineDisplayGame anchor missing')
s=s.replace(old,old,1)
s=s.replace("singleEngine:true,engineRevision:Number(state.engineRevision||0),engineDriverIndex:Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null","singleEngine:state.status==='playing',engineRevision:Number(state.engineRevision||0),engineDriverIndex:Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null",1)
s=s.replace("G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;G.online.singleEngine=true;","G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;G.online.singleEngine=state.status==='playing';",1)
s=s.replace("function renderOnlineAuthoritativeSetup(state){\n onlineApplyStateToDisplay(state);setupState=null;","function renderOnlineAuthoritativeSetup(state){\n onlineApplyStateToDisplay(state);if(G&&G.online)G.online.singleEngine=false;const setupMap=$('map');if(setupMap)setupMap.style.pointerEvents='';setupState=null;",1)
s=s.replace("function onlineSingleEngineLock(){\n if(!G||!G.online||!G.online.singleEngine)return;","function onlineSingleEngineLock(){\n if(onlineGameState&&onlineGameState.status==='setup'){const mapEl=$('map'),hand=$('hand');if(mapEl)mapEl.style.pointerEvents='';if(hand)hand.style.pointerEvents='';return}\n if(!G||!G.online||!G.online.singleEngine)return;",1)
p.write_text(s,encoding='utf-8')
print('setup region click fixed')
