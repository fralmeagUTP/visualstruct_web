const assert=require('node:assert/strict');
const {parse,createQueue,fetchUnit}=require('../static/js/multiple_input.js');
function player() {return {cursor:-1,total:3,pause(){},reset(){this.cursor=-1},seek(i){this.cursor=i},hasTrace(){return true},getTotalSteps(){return this.total},getCursor(){return this.cursor},isAtEnd(){return this.cursor===this.total-1},async step(){this.cursor++},prev(){this.cursor=Math.max(-1,this.cursor-1)},async play(){this.cursor=2}};}
(async()=>{
for(const structure of ['stack','queue','linked_list','circular_list','binary_heap']) assert(parse(' -3, +2,2,0 ',structure).valid);
for(const structure of ['abb','avl','red_black']) {assert(!parse('1,2,1',structure).valid);assert(!parse('3,2',structure,[2]).valid);}
for(const bad of ['',',1','1,','1,,2','1.5','1e2','0x20','2147483648','-2147483649','NaN','1 2']) assert(!parse(bad,'stack').valid,bad);
assert(parse('-2147483648,2147483647','stack').valid);assert(!parse(Array(51).fill('1').join(','),'stack').valid);assert(parse(Array(50).fill('1').join(','),'stack').valid);
let calls=[]; const a={player:player(),execute:async(value,fast)=>{calls.push([value,fast]);return {success:true}}};let q=createQueue(a);
await q.start([3,2,1],'normal');assert.deepEqual(calls,[[3,true],[2,true],[1,true]]);assert.equal(q.state().phase,'done');
calls=[];q=createQueue(a);await q.start([3,2],'step');assert.equal(calls.length,1);await q.next();q.prev();assert.equal(a.player.cursor,-1);await q.play();assert.equal(calls.length,1);await q.next();assert.equal(calls.length,2);q.stop();assert.equal(q.state().confirmed,2);assert.equal(q.state().phase,'stopped');assert(a.player.isAtEnd());
let resolve;calls=[];q=createQueue({...a,execute:value=>{calls.push(value);return new Promise(r=>resolve=r)}});const pending=q.start([1,2,3],'normal');await q.start([9],'normal');q.stop();resolve({success:true});await pending;assert.deepEqual(calls,[1]);assert.equal(q.state().phase,'stopped');assert.equal(q.state().confirmed,1);
calls=[];q=createQueue({...a,execute:async value=>{calls.push(value);return value===2?null:{success:true}}});await q.start([1,2,3],'normal');assert.equal(q.state().phase,'uncertain');await q.start([2,3],'normal');assert.deepEqual(calls,[1,2]);assert.equal(q.state().confirmed,1);
calls=[];q=createQueue({...a,execute:async value=>{calls.push(value);return {success:value!==2,message:'Sin reserva'}}});await q.start([1,2,3],'normal');assert.deepEqual(calls,[1,2]);assert.equal(q.state().phase,'failed');assert.equal(q.state().confirmed,1);
// Transport wrapper sends once, keeps body under timeout, never retries broken JSON.
let posts=0;global.fetch=async()=>{posts++;return {ok:true,json:async()=>{throw Error('broken')}}};await assert.rejects(fetchUnit('/unit',{method:'POST'}));assert.equal(posts,1);
console.log('PASS parser boundaries, 8 duplicate policies, queue normal/step, trace boundary, stop-in-flight, double start, uncertain response, known partial failure, no retry');
})().catch(e=>{console.error(e);process.exitCode=1});
