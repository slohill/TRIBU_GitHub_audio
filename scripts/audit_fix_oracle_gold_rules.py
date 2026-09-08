from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function openOracleCardById(id){if(id===null||id===undefined||!ORACLES[id])return;const src=ORACLE_CARD_ART[ORACLES[id].name];if(!src)return;const ov=$('cardZoomOverlay'),img=$('cardZoomImage');if(!ov||!img)return;img.src=src;img.alt=ORACLES[id].name;ov.classList.remove('hidden')}"""
new="""function openOracleCardById(id){
 if(id===null||id===undefined||!ORACLES[id])return;
 const name=ORACLES[id].name;
 if(!ORACLE_CARD_ART[name])return;
 openOfficialCard(name,'Oracle',oracleEffectText(name));
}"""
assert old in s
s=s.replace(old,new,1)
old=""" if(isViewerHand&&!choiceState&&!goldReaction&&c.name==='Conseil de guerre'){d.classList.add('playablePermanent');d.title='Jouer Conseil de guerre maintenant';d.onclick=()=>playCouncil(handIndex)}"""
new=""" if(isViewerHand&&!choiceState&&c.name==='Conseil de guerre'){d.classList.add('playablePermanent');d.title='Jouer Conseil de guerre maintenant';d.onclick=()=>playCouncil(handIndex)}"""
assert old in s
s=s.replace(old,new,1)
old="""function wireOracleCardPreviews(){
 const activeId=G&&G.oracleActive!==null?G.oracleActive:null,nextId=G?nextOracle():null;
 const candidates=[
   [$('oracleActive'),activeId],[$('oracleActiveName'),activeId],[$('oracleNext'),nextId],[$('oracleNextName'),nextId]
 ];
 candidates.forEach(([el,id])=>{if(!el||id===null||id===undefined)return;el.style.cursor='pointer';el.onclick=e=>{e.stopPropagation();openOracleCardById(id)}});
 document.querySelectorAll('[data-oracle-active]').forEach(el=>{el.style.cursor='pointer';el.onclick=e=>{e.stopPropagation();openOracleCardById(activeId)}});
 document.querySelectorAll('[data-oracle-next]').forEach(el=>{el.style.cursor='pointer';el.onclick=e=>{e.stopPropagation();openOracleCardById(nextId)}});
}"""
new="""function wireOracleCardPreviews(){
 const activeId=G&&G.oracleActive!==null?G.oracleActive:null,nextId=G?nextOracle():null;
 const activeName=$('oracleActiveName'),nextName=$('oracleNextName');
 const activeBox=activeName&&activeName.closest('.oracleMini'),nextBox=nextName&&nextName.closest('.oracleMini');
 const bind=(el,id)=>{
   if(!el)return;
   const available=id!==null&&id!==undefined;
   el.style.cursor=available?'pointer':'';
   el.onclick=available?(e=>{e.preventDefault();e.stopPropagation();openOracleCardById(id)}):null;
 };
 bind(activeBox,activeId);bind(activeName,activeId);bind(nextBox,nextId);bind(nextName,nextId);
}"""
assert old in s
s=s.replace(old,new,1)
# Make council pause only after battle priority validation, to avoid pausing a gold gain on an invalid click.
old=""" const actor=found.viewer;
 const pausedGold=!!goldReaction;if(pausedGold)pauseGoldReactionForCard();
 const battleCouncil=!!battle;
 if(battleCouncil){
   if(currentPriorityPlayer()!==actor)return;
   clearInterval(battleTick);clearTimeout(botReactionTimer);
 }"""
new=""" const actor=found.viewer;
 const battleCouncil=!!battle;
 if(battleCouncil&&currentPriorityPlayer()!==actor)return;
 const pausedGold=!!goldReaction;if(pausedGold)pauseGoldReactionForCard();
 if(battleCouncil){
   clearInterval(battleTick);clearTimeout(botReactionTimer);
 }"""
assert old in s
s=s.replace(old,new,1)
p.write_text(s)
