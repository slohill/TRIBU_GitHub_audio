from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'anchor not found: {label}')
    s=s.replace(old,new,1)

rep("main{display:grid;grid-template-columns:100px minmax(0,780px) 320px;gap:12px;padding:12px;align-items:start;justify-content:center}",
    "main{display:grid;grid-template-columns:210px minmax(0,780px) 320px;gap:12px;padding:12px;align-items:start;justify-content:center}",
    'main grid')
rep(".playerRail{position:sticky;top:10px;display:flex;flex-direction:column;gap:5px;z-index:50}\n.playerCard{background:#19201d;border:3px solid #777;border-radius:9px;padding:4px 5px;text-align:center;font-weight:900;cursor:pointer;position:relative;line-height:1.08}",
    ".playerRail{position:sticky;top:10px;display:flex;flex-direction:column;gap:5px;z-index:50}\n.playerHandSummary{background:#19201d;border:3px solid #777;border-radius:9px;padding:5px 6px;display:flex;align-items:center;justify-content:space-between;gap:5px;font-size:9px;font-weight:900;white-space:nowrap}\n.playerCard{background:#19201d;border:3px solid #777;border-radius:9px;padding:4px 5px;text-align:center;font-weight:900;cursor:pointer;position:relative;line-height:1.08}",
    'left summary css')
rep("@media(max-width:900px){main{grid-template-columns:76px minmax(0,1fr)}.rightRail{grid-column:2;position:static;max-height:none}.playerCard{font-size:11px}.bottomZone{grid-template-columns:1fr!important}.battleBanner{font-size:12px!important}}",
    "@media(max-width:900px){main{grid-template-columns:76px minmax(0,1fr)}.rightRail{grid-column:2;position:static;max-height:none}.playerCard{font-size:11px}.playerHandSummary{white-space:normal;flex-direction:column;gap:1px}.bottomZone{grid-template-columns:1fr!important}.battleBanner{font-size:12px!important}}",
    'responsive summary css')
rep("      <h3 class=\"compactHandTitle\">Main — <span id=\"handCount\">0</span> carte(s)</h3>\n      <div id=\"hand\" class=\"handHorizontal\"></div>",
    "      <span id=\"handCount\" class=\"hidden\">0</span>\n      <div id=\"hand\" class=\"handHorizontal\"></div>",
    'move hand title')

rep("function botAdvance(){\n if(!G || !isBot() || battle || goldReaction || priorityCardResolutionActive())return;\n\n\n\n if(G.phase==='start'){",
    "function botHandleReturn(){\n if(!isBot()||G.phase!=='returnChoice'||!returnState||returnState.player!==G.active)return false;\n const strongholds=returnStrongholds(G.active);\n const regions=(strongholds.length?strongholds:returnRegions(G.active)).slice().sort();\n if(!regions.length){\n   log(p().name+' (bot) ne peut pas revenir : aucune région libre sans PNJ.');\n   passReturn();\n   return true;\n }\n reformAt(regions[0]);\n return true;\n}\nfunction botAdvance(){\n if(!G || !isBot() || battle || goldReaction || priorityCardResolutionActive())return;\n\n if(G.phase==='returnChoice'){botHandleReturn();return}\n\n if(G.phase==='start'){",
    'bot return handler')
rep("function beginReturnChoice(){\n if(!isDecimated(G.active))return false;\n returnState={player:G.active};G.phase='returnChoice';\n log(p().name+' est décimé : voulez-vous revenir ?');render();\n return true;\n}",
    "function beginReturnChoice(){\n if(!isDecimated(G.active))return false;\n returnState={player:G.active};G.phase='returnChoice';\n log(p().name+' est décimé : voulez-vous revenir ?');render();\n if(G.players[G.active].bot)queueBot('retour après décimation');\n return true;\n}",
    'queue bot return')

rep("   rail.appendChild(card);\n });\n\n renderInPlay(localViewer());\n const buy=document.createElement('button');",
    "   rail.appendChild(card);\n });\n\n const viewer=localViewer();\n if(Number.isInteger(viewer)&&G.players[viewer]){\n   const pl=G.players[viewer],summary=document.createElement('div');\n   summary.className='playerHandSummary';summary.style.borderColor=COLORS[viewer];summary.style.color=COLORS[viewer];\n   summary.innerHTML='<span>Main - '+pl.hand.length+' carte(s)</span><span>Or : '+pl.gold+'</span><span>Unités : '+totalUnits(viewer)+'/'+cap(viewer)+'</span>';\n   rail.appendChild(summary);\n }\n renderInPlay(viewer);\n const buy=document.createElement('button');",
    'left player summary')
rep(" const viewer=localViewer();\n buy.disabled=isDecimated(viewer)||G.players[viewer].bot||G.players[viewer].gold<5||!!paidDrawState||!!dragonRichState||!!dragonCurseState;",
    " buy.disabled=isDecimated(viewer)||G.players[viewer].bot||G.players[viewer].gold<5||!!paidDrawState||!!dragonRichState||!!dragonCurseState;",
    'reuse viewer')
rep("function renderInPlay(i){\n const rail=$('playerRail'),list=publicInPlay(i);\n const card=document.createElement('div');card.className='inPlayRailCard';\n card.innerHTML='<div class=\"inPlayRailTitle\">EN JEU</div><div class=\"inPlayTitleList\"></div>';",
    "function renderInPlay(i){\n const rail=$('playerRail'),list=publicInPlay(i);\n const card=document.createElement('div');card.className='inPlayRailCard';card.style.borderColor=COLORS[i];\n card.innerHTML='<div class=\"inPlayRailTitle\" style=\"color:'+COLORS[i]+'\">EN JEU</div><div class=\"inPlayTitleList\"></div>';",
    'in play title color')

p.write_text(s,encoding='utf-8')
