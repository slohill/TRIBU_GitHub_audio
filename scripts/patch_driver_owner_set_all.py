from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   onlineLegacyBotDriverOwner=previousActive;
   if(G.online.myPlayerIndex===previousActive)G.online.botDriverOwner=previousActive;
 }"""
new="""   onlineLegacyBotDriverOwner=previousActive;
   G.online.botDriverOwner=previousActive;
 }"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
