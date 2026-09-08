from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" const decoded=onlineLegacyDecode(packet.snapshot),next=decoded.g||{};next.online=localOnline;G=next;
 const r=decoded.rule||{};"""
new=""" const decoded=onlineLegacyDecode(packet.snapshot),next=decoded.g||{};
 if(next.online&&Number.isInteger(next.online.botDriverOwner))localOnline.botDriverOwner=next.online.botDriverOwner;
 next.online=localOnline;G=next;
 const r=decoded.rule||{};"""
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
