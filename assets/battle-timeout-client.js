/* Execute a server-issued timeout once, through legacy Pass/resolveBattle. */
let onlineLegacyBattleTimeoutResolved=null,onlineBattleTimeoutAttempt=null;
const timeoutBaseApply=onlineLegacyApply;
onlineLegacyApply=function(packet){
 const result=timeoutBaseApply(packet);
 if(!packet?.snapshot||Number(packet.revision)!==onlineLegacyRevision)return result;
 onlineLegacyBattleTimeoutResolved=null;
 const rule=packet.snapshot.rule||{},lease=rule.battleTimeout,clock=rule.battleClock;
 if(clock?.deadline&&battle){
  const remaining=Math.max(0,Math.ceil((clock.deadline-clock.serverTime)/1000));
  battle.seconds=remaining;onlineLegacyResumeBattleView();
 }
 if(lease&&lease.executor===G?.online?.myPlayerIndex){
  const attempt=lease.id+':'+packet.revision;
  if(onlineBattleTimeoutAttempt!==attempt){
   onlineBattleTimeoutAttempt=attempt;
   setTimeout(()=>{
    if(onlineLegacyRevision!==Number(packet.revision)||!battle||commerceBattlePaused||priorityCardResolutionActive()||
     oracleState||oracleNoticeState||goldReaction||paidDrawState||onlineLegacyRecoveryPending)return;
    onlineLegacyBattleTimeoutResolved=lease.id;
    clearInterval(battleTick);clearTimeout(botReactionTimer);
    passPriority();
   },0);
  }
 }
 return result;
};
