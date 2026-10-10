'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {createHistoryStore}=require('../history-store');
const file=()=>path.join(fs.mkdtempSync(path.join(os.tmpdir(),'tribu-remote-history-')),'history.json');
const record=n=>({id:'12345678-1234-1234-1234-'+String(n).padStart(12,'0'),finishedAt:n,players:[{name:'Alice'}],winner:0});
const logger={error(){}};
function database(){const rows=new Map();return {rows,load:async()=>[...rows.values()],append:async records=>{for(const r of records)if(!rows.has(r.id))rows.set(r.id,r)}}}
test('external history survives replacement of the entire local filesystem',async()=>{
 const remote=database(),a=createHistoryStore({file:file(),remote,logger});await a.ready;a.add(record(1));await a.flush();await a.close();
 const b=createHistoryStore({file:file(),remote,logger});await b.ready;assert.deepEqual(b.list(),[record(1)]);assert.equal(b.available(),true);await b.close();
});
test('a victory arriving during initial load is merged with existing results',async()=>{
 let finishLoad;const remote=database();remote.rows.set(record(1).id,record(1));remote.load=()=>new Promise(r=>{finishLoad=r});
 const store=createHistoryStore({file:file(),remote,logger});store.add(record(2));assert.equal(store.available(),false);finishLoad([record(1)]);await store.ready;
 assert.deepEqual(store.list(),[record(1),record(2)]);assert.equal(remote.rows.size,2);await store.close();
});
test('failed connection never replaces remote history; a retry merges pending results',async()=>{
 const remote=database();remote.rows.set(record(1).id,record(1));const load=remote.load;remote.load=async()=>{throw Error('SECRET_CONNECTION_STRING')};const logs=[];
 const store=createHistoryStore({file:file(),remote,logger:{error:s=>logs.push(s)}});await store.ready;store.add(record(2));await store.flush();assert.equal(store.available(),false);assert.equal(remote.rows.size,1);
 remote.load=load;await store.flush();assert.deepEqual(store.list(),[record(1),record(2)]);assert.equal(store.available(),true);assert(!logs.join('').includes('SECRET'));await store.close();
});
test('a retry after lost write acknowledgement creates no duplicate, and caches pending writes',async()=>{
 const remote=database(),append=remote.append;let fail=true;remote.append=async records=>{await append(records);if(fail)throw Error('connection dropped after commit')};
 const local=file(),store=createHistoryStore({file:local,remote,logger});await store.ready;store.add(record(1));await store.flush();assert.equal(store.available(),false);assert.equal(JSON.parse(fs.readFileSync(local))[0].id,record(1).id);
 fail=false;await store.flush();store.add(record(1));await store.flush();assert.equal(remote.rows.size,1);assert.equal(store.available(),true);await store.close();
});
test('a second victory arriving during a write is also saved',async()=>{
 const remote=database(),append=remote.append;let release;remote.append=async records=>{await new Promise(r=>{release=r});await append(records)};
 const store=createHistoryStore({file:file(),remote,logger});await store.ready;store.add(record(1));store.add(record(2));remote.append=append;release();await store.flush();assert.equal(remote.rows.size,2);assert.equal(store.available(),true);await store.close();
});


test('old and new archived journals are removed while match results survive',async()=>{
 const target=file(),old={...record(1),journal:['old event'],hasJournal:true};fs.writeFileSync(target,JSON.stringify([old]));
 const store=createHistoryStore({file:target,logger});await store.ready;assert.deepEqual(store.list(),[record(1)]);assert.deepEqual(JSON.parse(fs.readFileSync(target)),[record(1)]);
 store.add({...record(2),journal:['new event']});assert.deepEqual(store.list(),[record(1),record(2)]);await store.close();
 const remote=database();remote.rows.set(old.id,old);const next=createHistoryStore({file:file(),remote,logger});await next.ready;assert.deepEqual(next.list(),[record(1)]);next.add({...record(3),journal:['ignored']});await next.flush();assert.deepEqual(remote.rows.get(record(3).id),record(3));await next.close();
});
