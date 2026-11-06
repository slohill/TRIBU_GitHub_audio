(function(root){'use strict';
function create(receiver,amount,source,after,turnOwner,turnEpoch,pausedBattle,details={}){
 return {...details,receiver,amount,source,after,seconds:10,turnOwner,turnEpoch,pausedBattle:!!pausedBattle};
}
const api=Object.freeze({create});root.TribuGoldReactionState=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
