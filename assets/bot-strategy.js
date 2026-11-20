/* Decisions only: all mutations use the existing game actions. No opponent hands. */
function botCanActFor(actor){
 return !!G?.players[actor]?.bot&&actor===G.active&&G.phase==='play'&&!gameOverState&&!battle&&!goldReaction&&
  !priorityCardResolutionActive()&&!oracleState&&!oracleNoticeState&&!morcattAuctionActive()&&
  (!G.online||G.online.legacySync&&onlineLegacyCanExecuteBot());
}
function botKnownCardValue(id,actor=G.active){
 const c=CARDS[id];if(!c)return 0;
 if(c.heroKey)return TribuHeroes.current(G,actor,CARDS)?3:10;
 if(c.allianceTribe)return 7;
 if(c.name==='Plan des trébuchets')return playerHasTrebuchets(actor)?1:6;
 if(c.name==='Espion'||c.name==='Voleur')return p(actor).inPlay.some(x=>CARDS[x].name===c.name)?3:7;
 if(c.name==='Taxe')return p(actor).gold+occupiedCaseCount(actor)>=40?1:7;
 if(c.name==='Conseil de guerre')return 2;
 if(['Catapultes','Pluie de flèches','Montures','Balistes','Mur de pique','Pyrodontes de guerre'].includes(c.name))return 6;
 if(['Assassin','Embuscade','Corruption'].includes(c.name))return 8;
 if(c.name==='Forteresse')return Object.keys(G.b).some(r=>G.b[r].owner===actor&&!hasBuilding(r))?7:2;
 if(c.name==='Icenia, la cité blanche'||c.name==='Sundo, cité du soleil'){
  const terrain=c.name.startsWith('Icenia')?'e':'d';
  return Object.keys(G.b).some(r=>G.b[r].owner===actor&&!hasBuilding(r)&&currentTerrain(r)===terrain)?10:2;
 }
 return 7;
}
function botAllianceConquest(){
 const actor=G.active;
 if(tutorial.active||!botCanActFor(actor)||!TribuCorruption.enabled(G)||TribuAlliances.alliance(p(actor),CARDS))return null;
 const options=[];
 p(actor).hand.forEach((id,handIndex)=>{
  const tribe=CARDS[id]?.allianceTribe;if(!tribe)return;
  Object.keys(G.b).forEach(target=>{
   const c=G.b[target];
   if(c.owner!==null||!c.hostile||c.npcTribe!==tribe||attacked.has(target)||!destinationAvailable(target))return;
   legalSources(target).forEach(source=>{const available=botMovableAvailable(source);if(available>0)options.push({source,target,available,seaEnemy:false,id,handIndex})});
  });
 });
 const choice=options.sort((a,b)=>botExpansionScore(b)-botExpansionScore(a))[0];
 if(!choice)return null;
 agentDefaults(actor);
 const placed=TribuAlliances.place(G,actor,choice.handIndex,choice.id,CARDS);if(!placed)return null;
 audioCardMove();log(p(actor).name+' met '+CARDS[choice.id].name+' en jeu.');
 return choice;
}
function botCouncilDiscards(actor){
 return p(actor).hand.map((id,index)=>({index,value:botKnownCardValue(id,actor)}))
  .sort((a,b)=>a.value-b.value||a.index-b.index).slice(0,2).map(x=>x.index);
}
function botPlayEconomyCard(){
 const actor=G.active;if(!botCanActFor(actor))return false;
 const tax=p(actor).hand.findIndex(id=>CARDS[id].name==='Taxe'),gain=occupiedCaseCount(actor);
 if(tax>=0&&gain>0&&p(actor).gold+gain<40){playTax(tax,actor);return true}
 const council=p(actor).hand.findIndex(id=>CARDS[id].name==='Conseil de guerre');
 if(council>=0&&p(actor).botCouncilEpoch!==turnEpoch&&p(actor).hand.some((id,i)=>i!==council&&botKnownCardValue(id,actor)<=3)){
  p(actor).botCouncilEpoch=turnEpoch;playCouncil(council,actor);return true;
 }
 return false;
}
function botOpponentPriority(actor,target){
 // Public score and army only; card identities in opponents' hands stay unknown.
 return victoryPoints(target)*8+ownRegs(target)*2;
}
function botChooseAgentTarget(actor,targets){
 return [...targets].sort((a,b)=>
  (botOpponentPriority(actor,b)+p(b).hand.length)-(botOpponentPriority(actor,a)+p(a).hand.length))[0];
}
function botChooseAssassinTarget(actor,targets){
 return [...targets].sort((a,b)=>{
  const score=t=>botOpponentPriority(actor,t.owner)+(CARDS[t.id]?.heroKey?20:CARDS[t.id]?.name==='Voleur'?8:4);
  return score(b)-score(a);
 })[0];
}
function botAvailableAttackBonus(actor,target){
 let bonus=(p(actor).attackTurnBonus||0)+TribuAlliances.bonus(G,actor,CARDS,'humans',1);
 for(const id of p(actor).hand){
  const name=CARDS[id]?.name;
  bonus+=name==='Catapultes'?5:name==='Montures'?4:name==='Pluie de flèches'?3:name==='Balistes'?2:
   name==='Pyrodontes de guerre'&&!isSea(target)&&currentTerrain(target)==='t'?5:0;
 }
 return bonus;
}
function botVisibleTargetDefense(target){
 if(isSea(target)){
  const enemies=seaEnemies(target);
  return enemies.length?Math.min(...enemies.map(e=>defendingUnits(e.owner,e.units)+(p(e.owner).defenseTurnBonus||0))):0;
 }
 const c=G.b[target],owner=c.owner;
 const structure=factionName(G.active)==='Yonkaïs'&&TribuHeroes.hasPassive(G,G.active,CARDS,'guide')?0:buildingDefense(target);
 const base=effectiveHostile(target)?5:owner===null||owner===G.active?0:defendingUnits(owner,c.units);
 return base+structure+(owner!==null&&owner!==G.active?(p(owner).defenseTurnBonus||0)+TribuHeroes.unionDefense(G,owner,target,CARDS):0);
}
function botStrategicBattleCard(actor,legal){
 if(!battle||actor!==battle.attacker&&actor!==battle.defender)return null;
 const side=actor===battle.attacker?'attacker':'defender';
 const need=battlePower(side==='attacker'?'defender':'attacker')-battlePower(side)+(side==='attacker'?1:0);
 if(need<=0)return null; // A defending tie already holds the region.
 const options=legal.map(x=>({...x,bonus:CARDS[x.id].name==='Balistes'?2:battleBonusFor(CARDS[x.id],side)})).filter(x=>x.bonus>0);
 // Minimum total bonus that wins; for equal totals prefer fewer cards.
 const sums=new Map([[0,[]]]);
 for(const option of options)for(const [sum,chosen] of [...sums]){
  const next=sum+option.bonus,list=[...chosen,option],old=sums.get(next);
  if(!old||list.length<old.length)sums.set(next,list);
 }
 const winning=[...sums].filter(([sum])=>sum>=need).sort((a,b)=>a[0]-b[0]||a[1].length-b[1].length)[0];
 if(!winning)return null; // Do not discard cards in an unwinnable exchange.
 return winning[1].sort((a,b)=>b.bonus-a.bonus)[0];
}
function botRecruitRegions(){
 const f=FACTIONS[p().faction].name;
 return Object.keys(G.b).filter(r=>G.b[r].owner===G.active&&
  !(f==='Griffes-Blanches'&&currentTerrain(r)==='d')&&!(f==='Reptones'&&currentTerrain(r)==='e'));
}
function botFrontierThreat(r){
 return neighbors(r).reduce((n,t)=>{
  if(isSea(t))return n+seaEnemies(t).reduce((m,e)=>Math.max(m,e.units),0);
  const c=G.b[t];return n+(c.owner!==null&&c.owner!==G.active?c.units:0);
 },0);
}
function botRecruitPriority(r){
 const threat=botFrontierThreat(r),units=G.b[r].units;
 const frontier=neighbors(r).some(t=>!isSea(t)&&G.b[t].owner!==G.active);
 return threat*3-units*2+(frontier?8:0)+(botProtectedRegion(r)?6:0);
}
function botStartDecision(){
 const regs=botRecruitRegions(),room=cap()-totalUnits(),gold=p().gold;
 let harvest=ownRegs(G.active)*2;
 Object.keys(G.b).forEach(r=>{if(cityAt(r)?.owner===G.active)harvest+=5});
 harvest+=TribuAlliances.bonus(G,G.active,CARDS,'dwarves',5);
 const safe=gold+harvest<40;
 const winningPurchase=victoryPoints(G.active)+1>=G.victoryTarget;
 if(gold>=35&&winningPurchase)return 'draw'; // Preserve the winning purchase.
 if(winningPurchase&&gold<35&&gold+harvest>=35&&safe)return 'harvest';
 const threatened=regs.some(r=>botFrontierThreat(r)>defendingUnits(G.active,G.b[r].units)+buildingDefense(r));
 if(regs.length&&room>0&&gold>=2&&(threatened||totalUnits()<ownRegs(G.active)*2))return 'recruit';
 if(harvest>0&&safe&&gold<6)return 'harvest';
 if(p().hand.length<3)return 'draw';
 if(regs.length&&room>0&&gold>=3)return 'recruit';
 if(harvest>=4&&safe&&gold<20)return 'harvest';
 return 'draw';
}
function botStrategicRecruit(){
 const regs=botRecruitRegions();
 for(let k=0;k<6&&p().gold>0&&totalUnits()<cap()&&regs.length;k++){
  regs.sort((a,b)=>botRecruitPriority(b)-botRecruitPriority(a));
  const before=totalUnits();recruitAt(regs[0]);if(totalUnits()===before)break;
 }
 beginPlay();queueBot('après recrutement');
}
function botProvinceOpportunity(target){
 if(isSea(target)||G.b[target].owner===G.active)return 0;
 const province=R[target][0],regs=Object.keys(R).filter(r=>R[r][0]===province);
 const owned=regs.filter(r=>G.b[r].owner===G.active).length,points=PROVINCE_VP[province]||0;
 if(owned===regs.length-1)return victoryPoints(G.active)+points>=G.victoryTarget?10000:300+points*40;
 return owned*8;
}
function botBuyUsefulVictoryPoint(){
 if(!isBot()||G.phase!=='play'||battle||priorityCardResolutionActive()||goldReaction||p().gold<35)return false;
 // Winning immediately, or banking a point before crossing the Dragon threshold.
 purchaseVictoryPoint(G.active);return true;
}
