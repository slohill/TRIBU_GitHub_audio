from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   onlineLegacyBotDriverOwner:Number.isInteger(onlineLegacyBotDriverOwner)?onlineLegacyBotDriverOwner:null
 };"""
new="""   onlineLegacyBotDriverOwner:(G&&G.online&&Number.isInteger(G.online.botDriverOwner))?G.online.botDriverOwner:(Number.isInteger(onlineLegacyBotDriverOwner)?onlineLegacyBotDriverOwner:null)
 };"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
