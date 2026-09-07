from pathlib import Path
p=Path('server/server.js');s=p.read_text()
s=s.replace("game.phase='start';game.movePool={};game.destinationUseCount={};game.attacked=[];game.recruitSnapshot=null;game.lastRoll=null;game.revision++;", "game.phase='start';game.movePool={};game.destinationUseCount={};game.attacked=[];game.recruitSnapshot=null;game.revision++;",1)
p.write_text(s)

p=Path('index.html');s=p.read_text()
old="const sea={};Object.keys(SEA).forEach(id=>sea[id]={fleets:{}});\n const active=Number.isInteger(state.active)?state.active:0;\n G={active,turn:state.turn||0,phase:state.phase||'setup',dragon:state.dragon||'E4',victoryTarget:state.victoryPoints||3,\n   players,b:board,sea,deck:[],discard:[],log:[],oracleDeck:[],oracleDiscard:[],oracleActive:null,"
new="const sea={};Object.keys(SEA).forEach(id=>sea[id]={fleets:{...((state.sea&&state.sea[id]&&state.sea[id].fleets)||{})}});\n const active=Number.isInteger(state.active)?state.active:0;\n G={active,turn:state.turn||0,phase:state.phase||'setup',dragon:state.dragon||'E4',victoryTarget:state.victoryPoints||3,\n   players,b:board,sea,deck:[],discard:[],log:[],oracleDeck:[],oracleDiscard:[],oracleActive:state.oracleActive===null?null:state.oracleActive,"
assert old in s;s=s.replace(old,new,1)
old="Object.entries(state.board||{}).forEach(([r,c])=>G.b[r]={...c});\n state.players.forEach((sp,i)=>{"
new="Object.entries(state.board||{}).forEach(([r,c])=>G.b[r]={...c});Object.keys(SEA).forEach(id=>{if(!G.sea[id])G.sea[id]={fleets:{}};G.sea[id].fleets={...((state.sea&&state.sea[id]&&state.sea[id].fleets)||{})}});\n state.players.forEach((sp,i)=>{"
assert old in s;s=s.replace(old,new,1)
s=s.replace("const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — tour, déplacements et Oracle synchronisés par le serveur.</div>';onlineRefreshPlayUi();", "const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — tour, déplacements et Oracle synchronisés par le serveur.'+(onlineGameState.lastRoll?' Dernier dé Oracle : <b>'+onlineGameState.lastRoll+'</b>.':'')+'</div>';onlineRefreshPlayUi();",1)
p.write_text(s)
