const assert=require('node:assert/strict');
const {createQueue}=require('../static/js/multiple_input.js');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 const realTimeout=global.setTimeout,timers=[],calls=[];
 global.setTimeout=(callback)=>{timers.push(callback);return timers.length;};
 try {
  const q=createQueue({execute:async v=>{calls.push(v);return {success:true}}});
  const old=q.start([1,2,3],'normal');await flush();assert.equal(timers.length,1);
  q.stop();const fresh=q.start([8,9,10],'normal');await flush();assert.deepEqual(calls,[1,8]);
  timers.shift()();await flush();assert.deepEqual(calls,[1,8],'old batch continuation cannot send a value from the new batch');await old;
  global.setTimeout=realTimeout;timers.shift()();await fresh;assert.deepEqual(calls,[1,8,9,10]);assert.equal(q.state().phase,'done');
  console.log('PASS stopped normal batch stale continuation cannot enter a newly started batch');
 } finally {global.setTimeout=realTimeout;}
})().catch(e=>{console.error(e);process.exitCode=1});
