from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="function onlineSetupRegionsFor(state){const me=state.players[state.youIndex];return me&&me.province?Object.keys(R).filter(r=>R[r][0]===me.province&&!R[r][2]):[]}"
new=old+"\nfunction onlineSetupMapFeedback(state,active){\n const map=$('map');if(!map)return;const ids=Object.keys(POS),spots=[...map.querySelectorAll('.spot')],allowed=active?onlineSetupRegionsFor(state):[];\n ids.forEach((id,i)=>{const spot=spots[i];if(!spot)return;spot.classList.remove('onlineSetupAvailable','onlineSetupChosen');if(allowed.includes(id))spot.classList.add('onlineSetupAvailable');if(onlineSetupSelectedRegions.includes(id)){spot.classList.add('onlineSetupChosen');const die=document.createElement('div');die.className='onlineSetupPreviewDie';die.textContent='3';die.style.backgroundColor=onlineSetupDraft.color||'#f4f4f4';spot.appendChild(die)}});\n}"
assert old in s
s=s.replace(old,new,1)
old="if(!active){const current=state.players[state.setup.activePlayer];$('setupText').innerHTML='Votre province : <b>'+(me&&me.province||'—')+'</b><br>En attente de <b>'+(current?current.pseudo:'un autre joueur')+'</b>.'}"
new="if(!active){const current=state.players[state.setup.activePlayer];$('setupText').innerHTML='En attente de <b>'+(current?current.pseudo:'un autre joueur')+'</b> pendant son installation.'}"
assert old in s
s=s.replace(old,new,1)
old="else{$('setupText').innerHTML='Province <b>'+me.province+'</b><br>Choisissez votre couleur et votre faction, puis cliquez sur <b>2 régions</b> de votre province directement sur la carte.<br>Placement : <b>'+onlineSetupSelectedRegions.length+'/2</b>';"
new="else{$('setupText').innerHTML='Choisissez votre couleur et votre faction, puis cliquez directement sur <b>2 des régions en surbrillance</b> sur la carte.<br>Placement : <b>'+onlineSetupSelectedRegions.length+'/2</b>';"
assert old in s
s=s.replace(old,new,1)
old="const boardMapImage=$('boardMapImage');if(boardMapImage)boardMapImage.src='assets/images/maps/map_normal.png';renderMap();renderPlayerRail()"
new="const boardMapImage=$('boardMapImage');if(boardMapImage)boardMapImage.src='assets/images/maps/map_normal.png';renderMap();onlineSetupMapFeedback(state,active);renderPlayerRail()"
assert old in s
s=s.replace(old,new,1)
css="""
/* Guidage visuel du placement Online : les identifiants internes restent invisibles. */
.spot.onlineSetupAvailable{outline:5px solid #52e57e!important;background:#52e57e55!important;box-shadow:0 0 0 3px #52e57e55,0 0 18px #52e57ecc!important;cursor:pointer!important;animation:onlineSetupPulse .9s ease-in-out infinite alternate}
.spot.onlineSetupChosen{outline:6px solid #f4d35e!important;background:#f4d35e44!important;box-shadow:0 0 0 4px #f4d35e55,0 0 22px #f4d35ecc!important;animation:none}
.onlineSetupPreviewDie{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:31px;height:31px;display:flex;align-items:center;justify-content:center;border:2px solid #111;border-radius:4px;color:#111!important;font-size:13px!important;font-weight:900;line-height:1!important;text-shadow:0 1px 1px #fff9;z-index:150;pointer-events:none;box-shadow:0 2px 5px #0009}
@keyframes onlineSetupPulse{from{filter:brightness(1)}to{filter:brightness(1.35)}}
@media(prefers-reduced-motion:reduce){.spot.onlineSetupAvailable{animation:none}}
"""
assert '</style>' in s
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
