const assert=require('node:assert/strict');
const path=require('node:path');
const {chromium}=require('playwright');
(async()=>{
 let browser;
 try{
  browser=await chromium.launch({channel:process.env.TRIBU_BROWSER_CHANNEL||'msedge',headless:true});
  const page=await browser.newPage();
  await page.setContent(`<div id="map" style="position:relative;width:600px;height:400px">
   <div data-region="A" style="position:absolute;left:40px;top:100px;width:40px;height:40px"></div>
   <div data-region="B" style="position:absolute;left:240px;top:100px;width:40px;height:40px"></div>
   <div data-region="C" style="position:absolute;left:440px;top:100px;width:40px;height:40px"></div>
   <div data-region="U" style="position:absolute;left:40px;top:250px;width:40px;height:40px"></div>
   </div><aside id="panel"></aside>`);
  for(const file of ['corruption-revolts.js','corruption-alliance-loss-ui.js'])
   await page.addScriptTag({path:path.resolve(__dirname,'../../assets',file)});
  await page.evaluate(()=>{
   window.sample={b:{A:{owner:1,units:3}},sea:{U:{fleets:{1:2,0:5}}}};
   window.battles=[{attacker:1,target:'B',attackOrigins:[{region:'A',moves:[0,1]}]},
    {attacker:1,target:'C',attackOrigins:[{region:'A',moves:[0]}]}];
   window.plan=TribuRevolts.plan(sample,1,battles);window.commits=0;
   window.draw=(viewer=0)=>{
    window.view?.destroy();window.view=TribuAllianceLossUI.mount({
     map:document.querySelector('#map'),panel:document.querySelector('#panel'),
     plan,mode:'revolts',actor:0,viewer,playerName:'Joueur 1',
     onChoose:(region,key)=>{TribuRevolts.choose(plan,region,key);draw(viewer)},
     onReset:()=>{TribuRevolts.reset(plan);draw(viewer)},onConfirm:()=>{window.commits++}
    });
   };draw();
  });
  const chip=(region,key)=>page.locator(`[data-loss-region="${region}"][data-loss-group="${key}"]`);
  const ok=page.locator('[data-loss-confirm]');
  assert(await ok.isDisabled());
  await chip('A','battle:0:0').click();assert.equal(await ok.isDisabled(),false);
  assert(await chip('U','stationed').isDisabled());
  await chip('A','battle:1:0').click();assert(await chip('A','stationed').isDisabled());
  assert.deepEqual(await page.evaluate(()=>plan.chosen),{'battle:0:0':1,'battle:1:0':1});
  assert.equal(await page.locator('line[stroke="#ef4444"]').count(),2);
  assert.equal(await page.evaluate(()=>sample.b.A.units),3);
  await ok.click();assert.equal(await page.evaluate(()=>commits),1);
  await page.locator('[data-loss-reset]').click();assert(await ok.isDisabled());
  await chip('U','stationed').click();assert.equal(await ok.isDisabled(),false);
  assert(await chip('A','stationed').isDisabled());
  await page.evaluate(()=>draw(1));assert.equal(await ok.count(),0);
  assert(await chip('U','stationed').isDisabled());
  assert((await page.locator('#panel').innerText()).includes('En attente de Joueur 1'));
  await page.setViewportSize({width:768,height:1024});await page.evaluate(()=>view.layout());
  const geometry=await page.locator('line').first().evaluate(e=>({x:e.getAttribute('x1'),y:e.getAttribute('y1'),z:e.parentElement.style.zIndex}));
  assert.equal(geometry.x,'60');assert.equal(geometry.y,'120');assert.equal(geometry.z,'19');
  await page.evaluate(()=>view.destroy());assert.equal(await page.locator('[data-loss-group],line,#panel section').count(),0);
  console.log('PASS Revolts UI: actor ownership, red source links, 1/2 provisional losses, single origin, sea, reset, observer, responsive cleanup.');
 }finally{await browser?.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
