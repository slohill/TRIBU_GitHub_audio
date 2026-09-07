from pathlib import Path

p=Path('index.html')
s=p.read_text()

anchor="function onlineRefreshPlayUi(){\n const st=onlineGameState,map=$('map'),srcBox=$('sources'),hint=$('hint');if(!st||!map)return;"
helper="function onlineRestoreMovePreviewDice(map){\n (map||$('map')).querySelectorAll('.die[data-online-move-original-text]').forEach(d=>{\n   d.textContent=d.dataset.onlineMoveOriginalText||'';\n   d.title=d.dataset.onlineMoveOriginalTitle||'';\n   d.style.display=d.dataset.onlineMoveOriginalDisplay||'';\n   delete d.dataset.onlineMoveOriginalText;delete d.dataset.onlineMoveOriginalTitle;delete d.dataset.onlineMoveOriginalDisplay;\n });\n}\nfunction onlineRefreshPlayUi(){\n const st=onlineGameState,map=$('map'),srcBox=$('sources'),hint=$('hint');if(!st||!map)return;\n onlineRestoreMovePreviewDice(map);"
if anchor not in s:
    raise SystemExit('onlineRefreshPlayUi anchor not found')
s=s.replace(anchor,helper,1)

old="if(ownDie){ownDie.textContent=remaining;ownDie.title='Unités : '+remaining;ownDie.style.display=remaining>0?'':'none'}"
new="if(ownDie){ownDie.dataset.onlineMoveOriginalText=ownDie.textContent;ownDie.dataset.onlineMoveOriginalTitle=ownDie.title||'';ownDie.dataset.onlineMoveOriginalDisplay=ownDie.style.display||'';ownDie.textContent=remaining;ownDie.title='Unités : '+remaining;ownDie.style.display=remaining>0?'':'none'}"
if old not in s:
    raise SystemExit('ownDie preview block not found')
s=s.replace(old,new,1)

restart="  const restart=document.createElement('button');restart.textContent='Recommencer le placement';restart.disabled=onlineSetupSelectedRegions.length===0;restart.onclick=()=>{onlineSetupSelectedRegions=[];renderOnlineAuthoritativeSetup(state)};box.appendChild(restart)"
if restart not in s:
    raise SystemExit('online setup restart line not found')
s=s.replace(restart,'',1)

p.write_text(s)
