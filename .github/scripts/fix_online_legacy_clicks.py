from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='play'&&onlineGameState.active===onlineGameState.youIndex)onlineMoveClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='oracleMove'&&onlineGameState.active===onlineGameState.youIndex)onlineDragonClick(id);return}"
new="if(G&&G.online&&onlineGameState&&!(G.online&&G.online.legacySync)){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='play'&&onlineGameState.active===onlineGameState.youIndex)onlineMoveClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='oracleMove'&&onlineGameState.active===onlineGameState.youIndex)onlineDragonClick(id);return}\n if(G&&G.online&&G.online.legacySync){\n   const me=G.online.myPlayerIndex;\n   const reactionMap=(oracleState&&oracleState.kind==='sacrifice'&&oracleState.queues&&oracleState.queues[oracleState.index]&&oracleState.queues[oracleState.index].player===me)||(oracleState&&oracleState.kind==='dragon5'&&oracleState.player===me)||(dragonRichState&&dragonRichState.player===me);\n   if(me!==G.active&&!reactionMap)return;\n }"
if old not in s: raise SystemExit('clickSpot online interception not found')
s=s.replace(old,new,1)
old2="const map=$('map');if(map)map.style.pointerEvents=onlineLegacyViewerNeedsMap(me)?'':'none';"
new2="const map=$('map');if(map)map.style.pointerEvents='';"
if old2 not in s: raise SystemExit('map pointer lock not found')
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
print('patched legacy click ownership and map pointer events')
