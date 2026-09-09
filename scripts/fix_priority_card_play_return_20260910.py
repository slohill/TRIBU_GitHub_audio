from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function resumeGameAfterPriorityCard(reason='reprise après carte prioritaire'){
 if(priorityCardResolutionActive())return;
 if(G&&G.players&&G.players[G.active]&&G.players[G.active].bot)queueBot(reason);
}"""
new="""function resumeGameAfterPriorityCard(reason='reprise après carte prioritaire'){
 if(priorityCardResolutionActive())return;
 if(G&&G.phase==='play')render();
 if(G&&G.players&&G.players[G.active]&&G.players[G.active].bot)queueBot(reason);
}"""
if old not in s:
    raise SystemExit('Bloc resumeGameAfterPriorityCard attendu introuvable')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
