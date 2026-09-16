from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""   const c=G.b[id];\n   const shown=c.owner!==null?visibleUnitsForSource(id,c.owner,c.units):0;\n   if(!isPvpBattle&&!isPvpPreview&&c.owner!==null&&shown>0)st.appendChild(die(c.owner,shown,id));"""
new="""   const c=G.b[id];\n   // Sur une destination terrestre déjà alliée, le total prévisionnel doit être\n   // l'unique compteur visible : ne pas laisser le dé physique le masquer/dupliquer.\n   const ownDestinationPreview=dest===id&&selected()>0&&c.owner===G.active;\n   const shown=ownDestinationPreview?0:(c.owner!==null?visibleUnitsForSource(id,c.owner,c.units):0);\n   if(!isPvpBattle&&!isPvpPreview&&c.owner!==null&&shown>0)st.appendChild(die(c.owner,shown,id));"""
if old not in s: raise SystemExit('target not found')
if s.count(old)!=1: raise SystemExit('target not unique')
s=s.replace(old,new)
p.write_text(s)
