'use strict';
const fs=require('fs');
const path=require('path');

const withoutJournal=({journal,hasJournal,...record})=>record;

// Only completed public summaries enter this archive. The game never waits for it.
function createHistoryStore({file,remote=null,logger=console,onChange=()=>{},retryMs=60000}){
 let records=[],fileError=false,remoteError=!!remote,loaded=!remote,closed=false,running=null,timer=null;
 const pending=new Map();
 const report=()=>logger.error('Historique TRIBU : stockage indisponible, nouvelle tentative prévue.');
 const trim=list=>list.map(withoutJournal).sort((a,b)=>a.finishedAt-b.finishedAt||a.id.localeCompare(b.id));
 try{const data=JSON.parse(fs.readFileSync(file,'utf8'));if(Array.isArray(data))records=trim(data.filter(r=>r&&typeof r.id==='string'&&Number.isFinite(r.finishedAt)&&Array.isArray(r.players)))}catch(e){if(e.code!=='ENOENT'){fileError=true;report()}}
 if(remote)for(const record of records)pending.set(record.id,record);
 function cache(){try{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file+'.tmp',JSON.stringify(records));fs.renameSync(file+'.tmp',file);fileError=false}catch{fileError=true;if(!remote)report()}}
 function schedule(){if(!closed&&!timer){timer=setTimeout(()=>{timer=null;flush()},retryMs);timer.unref?.()}}
 function flush(){
   if(!remote||closed)return Promise.resolve();if(running)return running;
   running=(async()=>{try{
     if(!loaded){const saved=await remote.load();const merged=new Map(records.map(r=>[r.id,r]));for(const record of saved){merged.set(record.id,record);pending.delete(record.id)}records=trim([...merged.values()]);loaded=true;cache()}
     while(pending.size){const batch=[...pending.values()];await remote.append(batch);for(const record of batch)pending.delete(record.id)}
     remoteError=false;if(timer){clearTimeout(timer);timer=null}
   }catch{remoteError=true;report();schedule()}finally{running=null;onChange()}})();return running;
 }
 function add(record){record=withoutJournal(record);if(records.some(r=>r.id===record.id))return;records=trim([...records,record]);cache();if(remote){pending.set(record.id,record);flush()}}
 if(records.length)cache();
 const ready=remote?flush():Promise.resolve();
 return {add,list:()=>records.slice(),available:()=>remote?loaded&&!remoteError&&pending.size===0:!fileError,ready,flush,
   async close(){closed=true;if(timer)clearTimeout(timer);if(running)await running;if(remote?.close)await remote.close()}};
}

function createPostgresHistory(connectionString,{Pool}={}){
 if(!Pool)({Pool}=require('pg'));
 const pool=new Pool({connectionString,max:1,idleTimeoutMillis:10000,connectionTimeoutMillis:15000,query_timeout:15000,statement_timeout:15000,application_name:'tribu-history'});
 // Idle connections may disappear while a free database sleeps. Reconnect on next query.
 pool.on('error',()=>{});
 return {
   async load(){
     await pool.query('CREATE TABLE IF NOT EXISTS tribu_public_history (id uuid PRIMARY KEY, finished_at bigint NOT NULL, summary jsonb NOT NULL)');
     await pool.query("UPDATE tribu_public_history SET summary = summary - 'journal' - 'hasJournal' WHERE summary ? 'journal' OR summary ? 'hasJournal'");
     const {rows}=await pool.query('SELECT summary FROM tribu_public_history ORDER BY finished_at DESC, id DESC');
     return rows.map(row=>row.summary);
   },
   async append(records){
     const client=await pool.connect();
     try{await client.query('BEGIN');
       for(const record of records)await client.query('INSERT INTO tribu_public_history (id, finished_at, summary) VALUES ($1, $2, $3::jsonb) ON CONFLICT (id) DO NOTHING',[record.id,record.finishedAt,JSON.stringify(withoutJournal(record))]);
       await client.query('COMMIT');
     }catch(error){await client.query('ROLLBACK').catch(()=>{});throw error}finally{client.release()}
   },
   close:()=>pool.end()
 };
}
module.exports={createHistoryStore,createPostgresHistory};

