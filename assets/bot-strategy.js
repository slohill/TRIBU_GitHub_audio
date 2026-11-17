/* Decisions only: all mutations use the existing game actions. No opponent hands. */
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
