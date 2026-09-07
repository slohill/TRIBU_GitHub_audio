from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old=""" const players=state.players.map((sp,i)=>({
   name:sp.pseudo,faction:Number.isInteger(sp.faction)?sp.faction:0,gold:sp.gold||0,pvPermanent:sp.pvPermanent||0,
   hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:[],attackTurnBonus:0,defenseTurnBonus:0,
   bot:!!sp.bot,decimated:false,portrait:sp.portrait||null
 }));"""
new=""" const players=state.players.map((sp,i)=>({
   name:sp.pseudo,faction:Number.isInteger(sp.faction)?sp.faction:0,gold:sp.gold||0,pvPermanent:sp.pvPermanent||0,
   hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:[],attackTurnBonus:0,defenseTurnBonus:0,
   bot:!!sp.bot,decimated:false,portrait:sp.portrait||null,color:sp.color||null
 }));
 state.players.forEach((sp,i)=>{if(sp.color)COLORS[i]=sp.color});"""
assert old in s
s=s.replace(old,new,1)

old="""   const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.remoteHandCount=sp.handCount||0;
   if(Array.isArray(sp.hand))pl.hand=sp.hand.slice();"""
new="""   const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.color=sp.color||null;pl.remoteHandCount=sp.handCount||0;
   if(sp.color)COLORS[i]=sp.color;
   if(Array.isArray(sp.hand))pl.hand=sp.hand.slice();"""
assert old in s
s=s.replace(old,new,1)

old="function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}"
new="function launchLegacyMode(mode,victory=3){COLORS.splice(0,COLORS.length,...BASE_COLORS);$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}"
assert old in s
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
