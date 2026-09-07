from pathlib import Path
p=Path('index.html')
s=p.read_text()

old="  const ok=document.createElement('button');ok.textContent='Valider mon installation';ok.disabled=!(onlineSetupDraft.color&&onlineSetupDraft.portrait&&onlineSetupSelectedRegions.length===2);ok.onclick=()=>onlineAck('setupComplete',{color:onlineSetupDraft.color,portrait:onlineSetupDraft.portrait,regions:onlineSetupSelectedRegions.slice()}).then(()=>{onlineSetupSelectedRegions=[];onlineSetupDraft={color:null,portrait:null}}).catch(onlineError);box.appendChild(ok);\n}"
new=old[:-2]+"\n  const restart=document.createElement('button');restart.textContent='Recommencer le placement';restart.disabled=onlineSetupSelectedRegions.length===0;restart.onclick=()=>{onlineSetupSelectedRegions=[];renderOnlineAuthoritativeSetup(state)};box.appendChild(restart);\n}"
if old not in s: raise SystemExit('setup exact anchor not found')
s=s.replace(old,new,1)

old="function onlineDisplayGame(state){"
new="function onlineDisplayGame(state){const topRestart=$('restart');if(topRestart)topRestart.classList.add('hidden');"
if old not in s: raise SystemExit('onlineDisplayGame anchor not found')
s=s.replace(old,new,1)

old="function launchLegacyMode(mode,victory=3){"
new="function launchLegacyMode(mode,victory=3){const topRestart=$('restart');if(topRestart)topRestart.classList.remove('hidden');"
if old not in s: raise SystemExit('launchLegacyMode anchor not found')
s=s.replace(old,new,1)

p.write_text(s)
