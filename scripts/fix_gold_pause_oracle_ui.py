from pathlib import Path
p=Path('index.html')
s=p.read_text()
# 1) Restore playing priority cards during gold reaction; pause/resume gold timer around their resolution.
anchor="function clearGoldReactionTimer(){\n if(goldReactionTick){clearInterval(goldReactionTick);goldReactionTick=null}\n}\n"
insert=anchor+"function pauseGoldReactionForCard(){if(!goldReaction)return false;clearGoldReactionTimer();goldReaction.pausedByCard=true;render();return true}\nfunction resumeGoldReactionAfterCard(){if(!goldReaction||!goldReaction.pausedByCard)return;delete goldReaction.pausedByCard;startGoldReactionTimer();render();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()}\n"
assert anchor in s;s=s.replace(anchor,insert,1)
# Gold timer does not tick while a priority card is resolving.
old="""   if(!goldReaction){clearGoldReactionTimer();return}\n   goldReaction.seconds--;"""
new="""   if(!goldReaction){clearGoldReactionTimer();return}\n   if(goldReaction.pausedByCard)return;\n   goldReaction.seconds--;"""
assert old in s;s=s.replace(old,new,1)
# Council may be played during gold gain; pause it and resume after resolution.
s=s.replace("if(choiceState||goldReaction)return;\n const found=cardFromViewerHand(handIndex,'Conseil de guerre')","if(choiceState)return;\n const found=cardFromViewerHand(handIndex,'Conseil de guerre')",1)
old=""" const actor=found.viewer;\n const battleCouncil=!!battle;"""
new=""" const actor=found.viewer;\n const pausedGold=!!goldReaction;if(pausedGold)pauseGoldReactionForCard();\n const battleCouncil=!!battle;"""
assert old in s;s=s.replace(old,new,1)
old=""" choiceState={kind:'council',selected:[],player:actor,battleCouncil,battleRef:battle,battleSeconds:battle?battle.seconds:null};"""
new=""" choiceState={kind:'council',selected:[],player:actor,battleCouncil,battleRef:battle,battleSeconds:battle?battle.seconds:null,pausedGold};"""
assert old in s;s=s.replace(old,new,1)
old=""" const wasBattle=choiceState.battleCouncil&&choiceState.battleRef===battle;\n const savedSeconds=choiceState.battleSeconds;\n closeChoice();"""
new=""" const wasBattle=choiceState.battleCouncil&&choiceState.battleRef===battle;\n const savedSeconds=choiceState.battleSeconds,pausedGold=!!choiceState.pausedGold;\n closeChoice();"""
assert old in s;s=s.replace(old,new,1)
old=""" render();\n}"""
pos=s.index('function confirmCouncil()')
end=s.index('function cardIndexByName',pos)
chunk=s[pos:end]
# only normal completion tail in confirmCouncil
chunk=chunk.replace(" render();\n}\n"," render();if(pausedGold)resumeGoldReactionAfterCard();\n}\n",1)
s=s[:pos]+chunk+s[end:]
# Generic wrapper: any playable card clicked while gold reaction exists pauses timer until its UI/state completes.
marker=""" if(d.onclick&&c.name!=='Divination de l’Oracle'&&c.name!=='Section de l’ombre'){\n   const cardAction=d.onclick;"""
repl=""" if(d.onclick&&c.name!=='Divination de l’Oracle'&&c.name!=='Section de l’ombre'){\n   const cardAction=d.onclick;"""
assert marker in s
# Add pause before card action for named priority cards, but not Ambush which owns the gold reaction itself.
old="""     if(G.phase==='recruit'&&recruitSnapshot&&recruitSnapshot.player===G.active){\n       resetRecruitmentForPriorityCard(handPlayer,c.name);\n     }\n     return cardAction.call(d,ev);"""
new="""     if(G.phase==='recruit'&&recruitSnapshot&&recruitSnapshot.player===G.active){\n       resetRecruitmentForPriorityCard(handPlayer,c.name);\n     }\n     if(goldReaction&&c.name!=='Embuscade')pauseGoldReactionForCard();\n     return cardAction.call(d,ev);"""
assert old in s;s=s.replace(old,new,1)
# For modal/state-driven priority cards, resume gold when their state is gone on render.
marker="""const onlineLegacyBaseRender=render;\nrender=function(){\n onlineLegacyBaseRender();"""
repl="""const onlineLegacyBaseRender=render;\nrender=function(){\n onlineLegacyBaseRender();\n if(goldReaction&&goldReaction.pausedByCard&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode&&!battle)resumeGoldReactionAfterCard();"""
assert marker in s;s=s.replace(marker,repl,1)
# Divination / shadow explicit pause during gold gain as they bypass generic wrapper.
s=s.replace("function openDivination(handIndex){\n const actor=localViewer()","function openDivination(handIndex){\n if(goldReaction)pauseGoldReactionForCard();\n const actor=localViewer()",1)
s=s.replace("function startShadow(handIndex){","function startShadow(handIndex){\n if(goldReaction)pauseGoldReactionForCard();",1)
# 2) Return rule: empty building regions already legal; make explicit by checking units/hostile only and not building.
# Existing returnRegions already does exactly this; preserve and guard with comment.
needle="// Après décimation, toute région réellement vide est une destination de retour,"
assert needle in s
# 3) Oracle card click preview using existing card zoom overlay.
# Add mapping/functions near oracleName.
marker="function oracleName(){return G.oracleActive===null?'Aucun':ORACLES[G.oracleActive].name}\n"
insert=marker+"const ORACLE_CARD_ART={'Canicule':'assets/images/cards/oracle/canicule.png','Vague de froid':'assets/images/cards/oracle/vague_de_froid.png','Givre mortel':'assets/images/cards/oracle/givre_mortel.png','Tempête de sable':'assets/images/cards/oracle/tempete_de_sable.png','Tempête en mer':'assets/images/cards/oracle/tempete_en_mer.png','En quête de destruction':'assets/images/cards/oracle/en_quete_de_destruction.png'};\nfunction openOracleCardById(id){if(id===null||id===undefined||!ORACLES[id])return;const src=ORACLE_CARD_ART[ORACLES[id].name];if(!src)return;const ov=$('cardZoomOverlay'),img=$('cardZoomImage');if(!ov||!img)return;img.src=src;img.alt=ORACLES[id].name;ov.classList.remove('hidden')}\n"
assert marker in s;s=s.replace(marker,insert,1)
# Wire labels/cards after render updates. Locate text assignments for oracle active/next and add onclick opportunistically by ids.
# Use DOM ids discovered in current UI: oracleActiveName / oracleNextName if present, otherwise query text containers by data attributes.
marker="function render(){"
# Add helper and call from end of base render using robust query selectors.
helper="""function wireOracleCardPreviews(){\n const activeId=G&&G.oracleActive!==null?G.oracleActive:null,nextId=G?nextOracle():null;\n const candidates=[\n   [$('oracleActive'),activeId],[$('oracleActiveName'),activeId],[$('oracleNext'),nextId],[$('oracleNextName'),nextId]\n ];\n candidates.forEach(([el,id])=>{if(!el||id===null||id===undefined)return;el.style.cursor='pointer';el.onclick=e=>{e.stopPropagation();openOracleCardById(id)}});\n document.querySelectorAll('[data-oracle-active]').forEach(el=>{el.style.cursor='pointer';el.onclick=e=>{e.stopPropagation();openOracleCardById(activeId)}});\n document.querySelectorAll('[data-oracle-next]').forEach(el=>{el.style.cursor='pointer';el.onclick=e=>{e.stopPropagation();openOracleCardById(nextId)}});\n}\n"""
# Insert before online wrapper where safe
idx=s.index('const onlineLegacyBaseRender=render;')
s=s[:idx]+helper+s[idx:]
s=s.replace(" onlineLegacyBaseRender();\n if(goldReaction", " onlineLegacyBaseRender();\n wireOracleCardPreviews();\n if(goldReaction",1)
# Also wire local base render by wrapping global after all code; online wrapper covers online, local render calls don't. Add at end after event listeners a MutationObserver fallback.
# 4) Move draw/discard overlay to upper center: CSS overrides appended before </style>.
css="""\n/* vOnline UI: pioche/défausse recentrées pour libérer la zone U */\n#map .deckZone,#map .deckArea,#map .drawDiscard,#map .piles,#map .cardPiles{left:50%!important;right:auto!important;transform:translateX(-50%)!important;top:1.5%!important;display:flex!important;gap:8px!important;flex-direction:row!important}\n.oracleCardClickable{cursor:pointer}\n"""
s=s.replace('</style>',css+'</style>',1)
# Add direct click delegation by visible text as fallback for actual markup names.
deleg="""\ndocument.addEventListener('click',e=>{\n const el=e.target.closest('[id*=oracle],[class*=oracle]');if(!el||!G)return;\n const t=(el.textContent||'').toLowerCase();\n if(t.includes('oracle actif')&&G.oracleActive!==null){e.stopPropagation();openOracleCardById(G.oracleActive)}\n else if(t.includes('oracle prochain')){const id=nextOracle();if(id!==null){e.stopPropagation();openOracleCardById(id)}}\n});\n"""
s=s.replace("document.addEventListener('keydown',e=>{if(e.key==='Escape')closeOfficialCard()});", "document.addEventListener('keydown',e=>{if(e.key==='Escape')closeOfficialCard()});"+deleg,1)
p.write_text(s)
