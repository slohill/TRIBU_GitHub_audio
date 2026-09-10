from pathlib import Path
p=Path('index.html')
s=p.read_text()
old=""" const closedAgentKind=agentModalState&&agentModalState.kind;\n agentModalState=null;$('agentOverlay').classList.add('hidden');$('agentChoices').innerHTML='';\n if(!force&&['spy','thief'].includes(closedAgentKind))resumeGameAfterPriorityCard('reprise après capacité Agent');\n}"""
new=""" const closedAgentKind=agentModalState&&agentModalState.kind;\n agentModalState=null;$('agentOverlay').classList.add('hidden');$('agentChoices').innerHTML='';\n if(!force&&(!closedAgentKind||['spy','thief'].includes(closedAgentKind)))resumeGameAfterPriorityCard('reprise après capacité Agent');\n}"""
if old not in s:
    raise SystemExit('closeAgentModal block not found')
s=s.replace(old,new,1)
p.write_text(s)
