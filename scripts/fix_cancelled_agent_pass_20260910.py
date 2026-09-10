from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="if(!force&&(!closedAgentKind||['spy','thief'].includes(closedAgentKind)))resumeGameAfterPriorityCard('reprise après capacité Agent');"
new="if(!force)resumeGameAfterPriorityCard('reprise après fermeture Agent');"
if old not in s:
    raise SystemExit('target not found')
s=s.replace(old,new,1)
p.write_text(s)
