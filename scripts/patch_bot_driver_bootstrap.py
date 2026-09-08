from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" onlineLegacyRevision=full.legacyRevision||0;
 onlineLegacyLastDigest=onlineLegacyDigest();"""
new=""" onlineLegacyRevision=full.legacyRevision||0;
 onlineLegacyBotDriverOwner=null;
 onlineLegacyLastDigest=onlineLegacyDigest();"""
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
