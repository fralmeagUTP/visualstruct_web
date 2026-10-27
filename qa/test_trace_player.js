/* Dependency-free contract tests for shared playback. Supply a baseline JS path
 * as argv[2] to reproduce failures without modifying the original application. */
'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const test = require('node:test');
const path = require('node:path');
const runtime = fs.readFileSync(process.argv[2] || path.join(__dirname, '../static/js/interpreter_runtime.js'), 'utf8');
function fixture(extra = {}) {
  const timers = [];
  const window = {setTimeout: fn => timers.push(fn)};
  const document = {readyState:'loading', addEventListener: () => {}};
  vm.runInNewContext(runtime, {window, document});
  const lines = Array.from({length:3}, () => {
    const classes = new Set();
    return {classList:{add:x=>classes.add(x),remove:x=>classes.delete(x)},classes,scrollIntoView:()=>{}};
  });
  const code = {querySelectorAll:()=>lines};
  const counter = {textContent:''}, status={textContent:''};
  let state = null;
  const events=[];
  const player = window.InterpreterRuntime.createTracePlayer({codeElement:code,counterElement:counter,statusElement:status,
    renderState:s=>{state=s;},onCursorChange:e=>events.push(e), ...extra});
  const trace = {steps:[0,1,2].map(n=>({line_index:n,state_snapshot:{value:n},state_after:{value:n+1},debug:{note:`value = ${n+1}`}}))};
  const flush = async () => { while(timers.length) { timers.shift()(); await Promise.resolve(); await Promise.resolve(); } };
  const active = () => lines.flatMap((line,i)=>line.classes.has('sim-active')?[i]:[]);
  return {player,trace,lines,counter,status,events,active,flush,get state(){return state;}};
}
test('step, previous, seek, reset and repeat recover identical frames', async () => {
  const f=fixture(); const p=f.player; p.loadTrace(f.trace);
  assert.equal(p.getCursor(),-1);assert.equal(f.state.value,0);assert.deepEqual(f.active(),[]);
  for(let i=0;i<3;i++){assert.equal(await p.step(),true);assert.equal(f.state.value,i+1);assert.deepEqual(f.active(),[i]);}
  assert.equal(p.isAtEnd(),true);assert.equal(await p.step(),false);
  for(let i=1;i>=-1;i--){assert.equal(p.prev(),true);assert.equal(p.getCursor(),i);assert.equal(f.state.value,i+1);assert.deepEqual(f.active(),i<0?[]:[i]);}
  assert.equal(p.prev(),false);p.seek(99);assert.equal(f.state.value,3);p.seek(-99);assert.equal(f.state.value,0);
  p.seek(1);p.reset();assert.equal(f.state.value,0);assert.deepEqual(f.active(),[]);
  const play=p.playFromStart();await f.flush();await play;assert.equal(f.state.value,3);assert.equal(p.getCursor(),2);
  const repeat=p.play();await f.flush();await repeat;assert.equal(f.state.value,3);assert.equal(p.getCursor(),2);
});
test('pause during automatic delay preserves the same executed code and state', async () => {
  const f=fixture();const p=f.player;p.loadTrace(f.trace);await p.step();
  const play=p.play();p.pause();await f.flush();await play;
  assert.equal(p.getCursor(),0);assert.equal(f.state.value,1);assert.deepEqual(f.active(),[0]);assert.equal(f.counter.textContent,'Paso: 1/3');
});
test('invalid load removes prior cursor, highlighted code and observer frame',async()=>{
  const f=fixture();const p=f.player;p.loadTrace(f.trace);await p.step();p.loadTrace(null);
  assert.equal(p.hasTrace(),false);assert.equal(p.getCursor(),-1);assert.deepEqual(f.active(),[]);assert.equal(f.counter.textContent,'Paso: 0/0');
  assert.equal(f.events.at(-1).trace,null);assert.equal(f.events.at(-1).step,null);
});
for(const action of ['clear','reset','seek','load'])test(`${action} cancels pending automatic updates`,async()=>{
  const f=fixture();const p=f.player;p.loadTrace(f.trace);await p.step();const play=p.play();
  if(action==='clear')p.clear();else if(action==='reset')p.reset();else if(action==='seek')p.seek(2);else p.loadTrace(f.trace);
  const before={cursor:p.getCursor(),state:f.state,active:f.active(),counter:f.counter.textContent};
  await f.flush();await play;
  assert.deepEqual({cursor:p.getCursor(),state:f.state,active:f.active(),counter:f.counter.textContent},before);
});
test('manual step cancels autoplay without duplicate advancement',async()=>{
  const f=fixture();const p=f.player;p.loadTrace(f.trace);const play=p.play();await p.step();await f.flush();await play;
  assert.equal(p.getCursor(),0);assert.equal(f.state.value,1);assert.deepEqual(f.active(),[0]);
});
test('second play invalidates first loop and emits every frame once',async()=>{
  const f=fixture();const p=f.player;p.loadTrace(f.trace);const first=p.play();const second=p.play();await f.flush();await Promise.all([first,second]);
  assert.equal(p.getCursor(),2);assert.equal(f.events.filter(e=>e.reason==='advance').length,3);
});
test('retained completed lines stay synchronized while playback is paused',async()=>{
  const f=fixture({retainDoneLines:true});const p=f.player;p.loadTrace(f.trace);await p.step();
  const play=p.play();p.pause();await f.flush();await play;
  assert.deepEqual(f.active(),[0]);assert.equal(f.lines[0].classes.has('sim-done'),false);
  await p.step();assert.deepEqual(f.active(),[1]);assert.equal(f.lines[0].classes.has('sim-done'),true);
  p.prev();assert.deepEqual(f.active(),[0]);assert.equal(f.lines[1].classes.has('sim-done'),false);
});
test('a player without a code panel still loads initial state and navigates',async()=>{
  const f=fixture({codeElement:null});const p=f.player;p.loadTrace(f.trace);
  assert.equal(f.state.value,0);assert.equal(p.getCursor(),-1);assert.equal(f.counter.textContent,'Paso: 0/3');
  await p.step();assert.equal(f.state.value,1);p.reset();assert.equal(f.state.value,0);
});
test('empty replacement trace cancels old playback and removes old line selection',async()=>{
  const f=fixture();const p=f.player;p.loadTrace(f.trace);await p.step();const play=p.play();p.loadTrace({steps:[]});await f.flush();await play;
  assert.equal(p.hasTrace(),false);assert.equal(p.getCursor(),-1);assert.deepEqual(f.active(),[]);assert.equal(f.counter.textContent,'Paso: 0/0');
  assert.equal(f.events.at(-1).step,null);
});
