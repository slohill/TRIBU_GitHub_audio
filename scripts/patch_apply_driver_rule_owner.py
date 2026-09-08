from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" onlineLegacyBotDriverOwner=Number.isInteger(r.onlineLegacyBotDriverOwner)?r.onlineLegacyBotDriverOwner:null;
 onlineLegacyRevision=packet.revision||0;dest=null;picks={};"""
new=""" onlineLegacyBotDriverOwner=Number.isInteger(r.onlineLegacyBotDriverOwner)?r.onlineLegacyBotDriverOwner:null;
 if(Number.isInteger(onlineLegacyBotDriverOwner))G.online.botDriverOwner=onlineLegacyBotDriverOwner;
 else delete G.online.botDriverOwner;
 onlineLegacyRevision=packet.revision||0;dest=null;picks={};"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
