from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

anchor="const $=id=>document.getElementById(id),map=$('map'),isSea=id=>!!SEA[id];"
insert="""const $=id=>document.getElementById(id),map=$('map'),isSea=id=>!!SEA[id];

// Online: tous les clients partent de la même graine serveur pour l'initialisation.
// Le mode local continue d'utiliser Math.random() comme avant.
let onlineSeededRandom=null;
function makeOnlineSeededRandom(seed){
 let x=(Number(seed)>>>0)||0x6d2b79f5;
 return ()=>{
   x=(x+0x6D2B79F5)>>>0;
   let t=x;
   t=Math.imul(t^(t>>>15),t|1);
   t^=t+Math.imul(t^(t>>>7),t|61);
   return ((t^(t>>>14))>>>0)/4294967296;
 };
}
function tribuRandom(){return onlineSeededRandom?onlineSeededRandom():Math.random()}
"""
if anchor not in s: raise SystemExit('random anchor missing')
s=s.replace(anchor,insert,1)

repls={
"const j=Math.floor(Math.random()*(i+1))":"const j=Math.floor(tribuRandom()*(i+1))",
"const y=Math.floor(Math.random()*(x+1))":"const y=Math.floor(tribuRandom()*(x+1))",
}
for old,new in repls.items():
    if old not in s: raise SystemExit('shuffle anchor missing: '+old)
    s=s.replace(old,new)

old="function launchOnlineRoom(room){onlineRoom=room;launchLegacyMode(onlineEngineMode(room),room.victoryPoints);"
new="function launchOnlineRoom(room){onlineRoom=room;onlineSeededRandom=makeOnlineSeededRandom(room.seed);launchLegacyMode(onlineEngineMode(room),room.victoryPoints);"
if old not in s: raise SystemExit('launchOnlineRoom anchor missing')
s=s.replace(old,new,1)

# Le mode local ne doit jamais hériter d'une graine Online précédente.
old="function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}"
new="function launchLegacyMode(mode,victory=3){if(!String(mode).includes('online')&&!onlineRoom)onlineSeededRandom=null;$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}"
if old not in s: raise SystemExit('launchLegacyMode anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
