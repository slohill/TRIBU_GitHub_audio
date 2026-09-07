from pathlib import Path

p=Path('index.html')
s=p.read_text()

# Restaure le bouton de recommencement du placement Online retiré par erreur.
needle="box.appendChild(ok);}\n const boardMapImage=$('boardMapImage');"
replacement="box.appendChild(ok);\n  const restart=document.createElement('button');restart.textContent='Recommencer le placement';restart.disabled=onlineSetupSelectedRegions.length===0;restart.onclick=()=>{onlineSetupSelectedRegions=[];renderOnlineAuthoritativeSetup(state)};box.appendChild(restart)}\n const boardMapImage=$('boardMapImage');"
if needle not in s:
    raise SystemExit('setup insertion anchor not found')
s=s.replace(needle,replacement,1)

# Le bouton global Recommencer reste disponible en local mais disparaît dès qu'une partie Online est affichée.
needle="function onlineDisplayGame(state){"
replacement="function onlineSetTopRestartVisibility(){const b=$('restart');if(b)b.classList.toggle('hidden',!!G.online)}\nfunction onlineDisplayGame(state){"
if needle not in s:
    raise SystemExit('onlineDisplayGame anchor not found')
s=s.replace(needle,replacement,1)

# Appelé après l'activation du contexte Online.
needle="G.online={"
pos=s.find(needle,s.find('function onlineDisplayGame(state){'))
if pos<0:
    raise SystemExit('G.online assignment not found in onlineDisplayGame')
# Injecter après la fin de l'affectation G.online, via le prochain point-virgule.
end=s.find(';',pos)
if end<0:
    raise SystemExit('G.online assignment end not found')
s=s[:end+1]+"onlineSetTopRestartVisibility();"+s[end+1:]

# En local, launchLegacyMode réaffiche explicitement le bouton global.
needle="function launchLegacyMode(mode,humans){"
replacement="function launchLegacyMode(mode,humans){const restartBtn=$('restart');if(restartBtn)restartBtn.classList.remove('hidden');"
if needle not in s:
    raise SystemExit('launchLegacyMode anchor not found')
s=s.replace(needle,replacement,1)

p.write_text(s)
