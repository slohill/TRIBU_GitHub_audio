from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function closeAgentModal(force=false){
 if(!force&&caravanState&&agentModalState&&agentModalState.kind==='caravan'){
   log('Caravane de commerce : chaque joueur doit choisir une carte avant de continuer.');
   showCaravanChoice();return;
 }
 agentModalState=null;$('agentOverlay').classList.add('hidden');$('agentChoices').innerHTML='';
}"""
new="""function closeAgentModal(force=false){
 if(!force&&caravanState&&agentModalState&&agentModalState.kind==='caravan'){
   log('Caravane de commerce : chaque joueur doit choisir une carte avant de continuer.');
   showCaravanChoice();return;
 }
 const closedAgentKind=agentModalState&&agentModalState.kind;
 agentModalState=null;$('agentOverlay').classList.add('hidden');$('agentChoices').innerHTML='';
 if(!force&&['spy','thief'].includes(closedAgentKind))resumeGameAfterPriorityCard('reprise après capacité Agent');
}"""
if old not in s:
    raise SystemExit('Bloc closeAgentModal attendu introuvable')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
