from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" if(G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverOwner=null;"""
new=""" if(G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot){onlineLegacyBotDriverOwner=null;delete G.online.botDriverOwner;}"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
