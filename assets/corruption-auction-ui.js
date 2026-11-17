/* Auction UI: server-authoritative online, legacy local execution otherwise. */
let morcattClockSample=null;
function morcattClockNow(){
 return G?.online&&morcattClockSample?morcattClockSample.serverTime+performance.now()-morcattClockSample.observedAt:Date.now();
}
const morcattBaseApply=onlineLegacyApply;
onlineLegacyApply=function(packet){
 if(Number.isFinite(packet?.serverTime)&&(!Number.isInteger(packet.revision)||packet.revision>=onlineLegacyRevision)){
  morcattClockSample={serverTime:packet.serverTime,observedAt:performance.now()};
 }
 return morcattBaseApply(packet);
};
function morcattAuctionActive(){TribuAuction.upgrade(G?.morcattAuction);return !!G?.morcattAuction&&G.morcattAuction.stage!=='finished'}
function startMorcattAuction(seller,gain,dwarfHarvest=null){
 if(morcattAuctionActive())return;
 const cards=[];for(let i=0;i<3;i++){const id=drawOneToPool();if(id===null||id===undefined)break;cards.push(id)}
 G.morcattAuction=TribuAuction.create(seller,cards,gain);G.morcattAuction.dwarfHarvest=dwarfHarvest;G.phase='auction';render();
 if(!G.online&&p(seller).bot){cards.forEach((id,i)=>TribuAuction.price(G.morcattAuction,seller,i,TribuAuction.botPrice(id,CARDS)));TribuAuction.start(G.morcattAuction,seller,G.players,G.discard);morcattAuctionChanged()}
}
function morcattAuctionChanged(){
 const s=G.morcattAuction;
 if(s?.stage==='finished'&&!s.gainOffered){
  s.gainOffered=true;let gain=TribuAuction.total(s);
  const dwarfHarvest=s.dwarfHarvest?{...s.dwarfHarvest,baseAmount:s.dwarfHarvest.baseAmount+s.receipts-s.unsold}:null;
  if(dwarfHarvest){const pending={amount:gain,dwarfHarvest};refreshDwarfHarvestGain(pending);gain=pending.amount;}
  log(p(s.seller).name+' termine ses enchères : '+s.receipts+' Or de ventes, '+s.unsold+' invendue(s).');
  G.phase='start';offerGoldGain(s.seller,gain,'Récolte Morcatt','beginPlay',{dwarfHarvest});return;
 }
 render();
}
function morcattAuctionAction(kind,value,index){
 const s=G?.morcattAuction;if(!s)return;
 if(G.online){
  onlineAck('morcattAuctionAction',{kind,amount:value,index,revision:s.revision}).then(result=>{if(result.current)onlineLegacyApply(result.current)}).catch(error=>{if(error.current)onlineLegacyApply(error.current);else onlineError(error)});
  return;
 }
 const actor=localViewer();let changed=false;
 if(kind==='price')changed=TribuAuction.price(s,actor,index,value);
 if(kind==='start')changed=TribuAuction.start(s,actor,G.players,G.discard);
 if(kind==='bid')changed=TribuAuction.bid(s,actor,value,G.players,G.discard,s.revision,Date.now(),index);
 if(kind==='cancel')changed=TribuAuction.cancel(s,actor,G.players,s.revision,Date.now(),index);
 if(kind==='extend')changed=TribuAuction.extend(s,actor,G.players,s.revision);
 if(changed)morcattAuctionChanged();
}
let morcattNoticeKey=null,morcattNoticeUntil=0,morcattNoticeTimer=null;
const morcattBidDrafts=new Map();
function renderMorcattAuction(){
 // Keep unfinished edits and focus through incoming bids/snapshots.
 const old=$('morcattAuctionPanel'),focused=document.activeElement;
 let focusKey=null,selection=null;
 old?.querySelectorAll('[data-auction-draft]').forEach(input=>{
  if(document.activeElement===input){focusKey=input.dataset.auctionDraft;selection=input.value;morcattBidDrafts.set(focusKey,selection)}
 });
 old?.remove();$('morcattAuctionNotice')?.remove();
 const pending=G?.morcattAuction;
 if(pending?.stage==='finished'&&!pending.gainOffered&&(!G.online||G.online.myPlayerIndex===pending.seller||p(pending.seller).bot&&onlineLegacyCanExecuteBot())){
  setTimeout(()=>{if(G?.morcattAuction===pending&&!pending.gainOffered)morcattAuctionChanged()},0);
 }
 if(!morcattAuctionActive()){morcattNoticeKey=null;return}
 const s=G.morcattAuction,root=$('commerceBoard');if(!root)return;
 const noticeKey=[G.turn,G.active,s.seller,s.cards.join(',')].join(':');
 if(morcattNoticeKey!==noticeKey){
  morcattNoticeKey=noticeKey;morcattNoticeUntil=performance.now()+5000;morcattBidDrafts.clear();
  clearTimeout(morcattNoticeTimer);morcattNoticeTimer=setTimeout(()=>$('morcattAuctionNotice')?.remove(),5000);
 }
 if(performance.now()<morcattNoticeUntil){
  const notice=document.createElement('button');notice.id='morcattAuctionNotice';
  notice.textContent='Des enchères Morcatts sont disponibles ! — cliquez pour aller voir —';
  notice.style.cssText='position:absolute;top:4px;left:10%;width:80%;z-index:95';
  notice.onclick=()=>$('morcattAuctionPanel')?.scrollIntoView({behavior:'smooth',block:'center'});$('map').appendChild(notice);
 }
 const panel=document.createElement('section');panel.id='morcattAuctionPanel';panel.className='commerceBoardRow';
 const title=document.createElement('h3');title.textContent='Enchères — '+p(s.seller).name;panel.appendChild(title);
 const list=document.createElement('div');list.style.cssText='display:flex;gap:10px;flex-wrap:wrap';panel.appendChild(list);
 const viewer=localViewer(),canBid=s.stage==='bidding'&&viewer!==s.seller&&!!G.players[viewer]&&!p(viewer).decimated;
 const button=(host,text,action)=>{const b=document.createElement('button');b.type='button';b.textContent=text;b.onclick=action;host.appendChild(b);return b};
 s.cards.forEach((id,i)=>{
  const card=CARDS[id],offer=s.bids[i],box=document.createElement('div');box.dataset.auctionCard=i;
  box.style.cssText='padding:8px;border:3px solid '+(offer?COLORS[offer.player]:'#fff')+';border-radius:8px;width:180px';
  const face=button(box,card.name,()=>morcattAuctionAction('bid',(offer?.amount??s.prices[i])+1,i));face.dataset.auctionBid=i;
  face.disabled=!canBid||TribuAuction.available(s,viewer,G.players,i)<(offer?.amount??s.prices[i])+1;
  const art=OFFICIAL_CARD_ART[card.name];if(art){const img=document.createElement('img');img.src=art;img.alt=card.name;img.draggable=false;img.style.cssText='display:block;width:100%;pointer-events:none';face.prepend(img)}
  const zoom=button(box,'🔍',()=>openOfficialCard(card.name,card.type,card.effect));zoom.setAttribute('aria-label','Agrandir '+card.name);zoom.dataset.auctionZoom=i;
  const label=document.createElement('p');label.textContent=offer?p(offer.player).name+' : '+offer.amount+' Or':'Aucune offre — départ '+s.prices[i]+' Or';box.appendChild(label);
  if(s.stage==='prepare'&&viewer===s.seller){
   const input=document.createElement('input');input.type='number';input.min='1';input.step='1';input.value=s.prices[i];input.setAttribute('aria-label','Mise de départ carte '+(i+1));input.style.width='85px';
   input.onchange=()=>morcattAuctionAction('price',Number(input.value),i);box.appendChild(input);
  }
  if(canBid){
   const amount=document.createElement('input'),key=noticeKey+':'+viewer+':'+i;
   amount.type='number';amount.min=String(TribuAuction.minimum(s,i));amount.max=String(TribuAuction.available(s,viewer,G.players,i));amount.step='1';
   amount.value=morcattBidDrafts.get(key)??amount.min;amount.dataset.auctionDraft=key;amount.setAttribute('aria-label','Votre enchère carte '+(i+1));amount.style.width='85px';
   amount.oninput=()=>morcattBidDrafts.set(key,amount.value);box.appendChild(amount);
   button(box,'Valider',()=>{const value=Number(amount.value);if(Number.isSafeInteger(value)&&value>=Number(amount.min)&&value<=Number(amount.max)){morcattBidDrafts.delete(key);morcattAuctionAction('bid',value,i)}});
   if(offer?.player===viewer)button(box,'Annuler',()=>morcattAuctionAction('cancel',undefined,i)).dataset.auctionCancel=i;
  }
  list.appendChild(box);
 });
 if(s.stage==='prepare'){if(viewer===s.seller)button(panel,'Lancer les enchères',()=>morcattAuctionAction('start'))}
 else{
  const timer=document.createElement('strong');timer.id='morcattAuctionTimer';panel.appendChild(timer);
  if(canBid)button(panel,'⏳ ajouter 15 secondes ⏳',()=>morcattAuctionAction('extend'));
 }
 root.appendChild(panel);updateMorcattAuctionTimer();
 if(focusKey){const input=[...panel.querySelectorAll('[data-auction-draft]')].find(x=>x.dataset.auctionDraft===focusKey);input?.focus({preventScroll:true})}
}
function updateMorcattAuctionTimer(){const timer=$('morcattAuctionTimer'),s=G?.morcattAuction;if(timer&&s?.deadline)timer.textContent=Math.max(0,Math.ceil((s.deadline-morcattClockNow())/1000))+' s'}
const morcattBaseRenderCommerceBoard=renderCommerceBoard;
renderCommerceBoard=function(){morcattBaseRenderCommerceBoard();renderMorcattAuction()};
setInterval(()=>{
 if(!morcattAuctionActive())return;
 updateMorcattAuctionTimer();
 if(G.online)return;
 const s=G.morcattAuction;
 if(s.stage!=='bidding')return;
 if(TribuAuction.tick(s,G.players,G.discard)){morcattAuctionChanged();return}
 for(let i=0;i<G.players.length;i++){
  if(!p(i).bot)continue;const action=TribuAuction.botAction(s,i,G.players,CARDS);if(!action)continue;
  const changed=TribuAuction.bid(s,i,action.amount,G.players,G.discard,s.revision,Date.now(),action.index);
  if(changed){morcattAuctionChanged();break}
 }
 updateMorcattAuctionTimer();
},500);
