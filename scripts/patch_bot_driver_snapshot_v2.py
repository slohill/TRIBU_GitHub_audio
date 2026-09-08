from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   oraclePendingNormalMap,turnEpoch,divinationState,recruitSnapshot,gameOverState,commerceDeals,commerceSeq
 };"""
new="""   oraclePendingNormalMap,turnEpoch,divinationState,recruitSnapshot,gameOverState,commerceDeals,commerceSeq,
   onlineLegacyBotDriverOwner:Number.isInteger(onlineLegacyBotDriverOwner)?onlineLegacyBotDriverOwner:null
 };"""
assert old in s;s=s.replace(old,new,1)
old=""" recruitSnapshot=r.recruitSnapshot||null;gameOverState=r.gameOverState||null;commerceDeals=r.commerceDeals||[];commerceSeq=r.commerceSeq||1;
 onlineLegacyRevision=packet.revision||0;dest=null;picks={};
 if(G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverOwner=null;"""
new=""" recruitSnapshot=r.recruitSnapshot||null;gameOverState=r.gameOverState||null;commerceDeals=r.commerceDeals||[];commerceSeq=r.commerceSeq||1;
 onlineLegacyBotDriverOwner=Number.isInteger(r.onlineLegacyBotDriverOwner)?r.onlineLegacyBotDriverOwner:null;
 onlineLegacyRevision=packet.revision||0;dest=null;picks={};
 if(G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverOwner=null;"""
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
