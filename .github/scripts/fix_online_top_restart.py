from pathlib import Path
import re

p=Path('index.html')
s=p.read_text()

# Restaure le bouton de placement Online retiré par erreur, juste après Valider mon installation.
anchor="const ok=document.createElement('button');ok.textContent='Valider mon installation';"
pos=s.find(anchor)
if pos<0: raise SystemExit('setup ok anchor not found')
board=s.find("const boardMapImage=$('boardMapImage');",pos)
if board<0: raise SystemExit('boardMapImage anchor not found')
segment=s[pos:board]
if "Recommencer le placement" not in segment:
    close=segment.rfind('}')
    if close<0: raise SystemExit('setup active block close not found')
    insert="\n  const restart=document.createElement('button');restart.textContent='Recommencer le placement';restart.disabled=onlineSetupSelectedRegions.length===0;restart.onclick=()=>{onlineSetupSelectedRegions=[];renderOnlineAuthoritativeSetup(state)};box.appendChild(restart)"
    segment=segment[:close]+insert+segment[close:]
    s=s[:pos]+segment+s[board:]

# Masque uniquement le bouton global du header quand l'écran de jeu Online est construit.
needle="function onlineDisplayGame(state){"
replacement="function onlineDisplayGame(state){const topRestart=$('restart');if(topRestart)topRestart.classList.add('hidden');"
if needle not in s: raise SystemExit('onlineDisplayGame anchor not found')
s=s.replace(needle,replacement,1)

# Le mode local le réaffiche explicitement.
needle="function launchLegacyMode(mode,humans){"
replacement="function launchLegacyMode(mode,humans){const topRestart=$('restart');if(topRestart)topRestart.classList.remove('hidden');"
if needle not in s: raise SystemExit('launchLegacyMode anchor not found')
s=s.replace(needle,replacement,1)

p.write_text(s)
