from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old1=""" const me=state.youIndex,oldOnline=G&&G.online?{...G.online}:{};const s=JSON.parse(JSON.stringify(snapshot));G=s.game;G.online={...oldOnline,code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:me,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision,singleEngine:true,engineRevision:Number(state.engineRevision||0),engineDriverIndex:Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null};"""
new1=""" const me=state.youIndex,oldOnline=G&&G.online?{...G.online}:{};
 const localMoveDraft=(G&&G.online&&G.online.singleEngine&&G.phase==='play'&&G.active===me&&dest)?{dest,picks:{...picks}}:null;
 const s=JSON.parse(JSON.stringify(snapshot));G=s.game;G.online={...oldOnline,code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:me,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision,singleEngine:true,engineRevision:Number(state.engineRevision||0),engineDriverIndex:Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null};"""
if old1 not in s:
    raise SystemExit('onlineSingleEngineApply start anchor not found')
s=s.replace(old1,new1,1)

old2=""" // Les brouillons de clic restent locaux : jamais de destination/picks distants injectés.
 dest=null;picks={};onlineEngineRevision=Number(state.engineRevision||0);onlineEngineLastSent=JSON.stringify(s);onlineEngineApplying=false;return true;"""
new2=""" // Le brouillon de déplacement est strictement local, mais il ne doit pas être effacé
 // par un simple écho de synchronisation pendant que le joueur choisit ses unités.
 dest=null;picks={};
 if(localMoveDraft&&G.phase==='play'&&G.active===me&&!battle&&!choiceState&&!oracleState&&!divinationState&&legalSources(localMoveDraft.dest).length){
   dest=localMoveDraft.dest;
   for(const [src,q] of Object.entries(localMoveDraft.picks||{})){
     if(!legalSources(dest).includes(src))continue;
     const n=Math.max(0,Math.min(movableCount(src),Number(q)||0));if(n)picks[src]=n;
   }
 }
 onlineEngineRevision=Number(state.engineRevision||0);onlineEngineLastSent=JSON.stringify(s);onlineEngineApplying=false;return true;"""
if old2 not in s:
    raise SystemExit('onlineSingleEngineApply draft anchor not found')
s=s.replace(old2,new2,1)

p.write_text(s,encoding='utf-8')
print('online movement draft persistence fixed')
