'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test'),path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.join(__dirname,'../static/js/counting_runtime.js'),'utf8');
const common=fs.readFileSync(path.join(__dirname,'../static/js/interpreter_runtime.js'),'utf8');
function fixture(){
 const requests=[],events=[],timers=[];let state=null;
 const window={setTimeout:fn=>timers.push(fn)};
 const document={readyState:'loading',addEventListener:()=>{}};
 const fetch=url=>new Promise(resolve=>requests.push({url,resolve}));
 const context={window,document,fetch,URLSearchParams,setTimeout:window.setTimeout};vm.runInNewContext(common,context);vm.runInNewContext(source,context);
 const lines=Array.from({length:3},()=>{const classes=new Set();return{classes,classList:{add:(...xs)=>xs.forEach(x=>classes.add(x)),remove:(...xs)=>xs.forEach(x=>classes.delete(x))},scrollIntoView:()=>{}}});
 const code={querySelectorAll:()=>lines},counter={textContent:''},status={textContent:''};
 const player=window.CountingRuntime.createCompatiblePlayer({codeElement:code,counterElement:counter,statusElement:status,renderState:s=>{state=s;},onCursorChange:e=>events.push(e)});
 const makeStep=(index,base=0)=>({step_index:index,line_index:index%3,state_snapshot:{value:base+index},state_after:{value:base+index+1},debug:{note:`step ${index}`}});
 const paged=(id='paged',base=0)=>({schema:'counting-paged-trace/v1',trace_id:id,step_count:70,manifest:{page_url:`/${id}`},initial_page:{steps:[makeStep(0,base)]}});
 const legacy={steps:[makeStep(0,100),makeStep(1,100)]};
 const tick=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
 const respond=async(id='paged',base=0)=>{await tick();const request=requests.shift();assert.ok(request,'expected delayed page request');const start=Number(new URL(request.url,'http://local').searchParams.get('start'));request.resolve({ok:true,json:async()=>({success:true,trace_id:id,steps:Array.from({length:Math.min(64,70-start)},(_,n)=>makeStep(start+n,base))})});await tick();};
 return {player,paged,legacy,requests,events,counter,status,respond,tick,lines,get state(){return state;},active:()=>lines.flatMap((line,i)=>line.classes.has('sim-active')?[i]:[])};
}
test('paged clear removes highlighted code, counts and cached exposed trace',async()=>{
 const f=fixture();const p=f.player;p.loadTrace(f.paged());await p.step();assert.deepEqual(f.active(),[0]);p.clear();
 assert.deepEqual(f.active(),[]);assert.equal(p.getCursor(),-1);assert.equal(f.counter.textContent,'Paso: 0/0');assert.equal(f.events.at(-1).step,null);assert.equal(await p.getStep(0),null);
});
for(const action of ['reset','clear','load-paged','load-legacy'])test(`${action} blocks delayed old page from painting`,async()=>{
 const f=fixture();const p=f.player;p.loadTrace(f.paged());const pending=p.seek(65);await f.tick();
 if(action==='reset')p.reset();else if(action==='clear')p.clear();else if(action==='load-paged')p.loadTrace(f.paged('new',200));else p.loadTrace(f.legacy);
 const before={state:f.state,active:f.active(),counter:f.counter.textContent,cursor:p.getCursor(),events:f.events.length};
 await f.respond();await pending;
 assert.deepEqual({state:f.state,active:f.active(),counter:f.counter.textContent,cursor:p.getCursor(),events:f.events.length},before);
});
test('paged to invalid trace notifies empty observers and cancels fetch',async()=>{
 const f=fixture();const p=f.player;p.loadTrace(f.paged());const pending=p.seek(65);await f.tick();p.loadTrace(null);await f.respond();await pending;
 assert.equal(p.hasTrace(),false);assert.equal(p.getCursor(),-1);assert.deepEqual(f.active(),[]);assert.equal(f.events.at(-1).trace,null);assert.equal(f.events.at(-1).step,null);assert.equal(f.counter.textContent,'Paso: 0/0');
});
test('paged navigation follows latest seek, resets, and steps from initial state',async()=>{
 const f=fixture();const p=f.player;p.loadTrace(f.paged());await p.step();assert.equal(f.state.value,1);
 const old=p.seek(65);await f.tick();await p.seek(0);await f.respond();await old;assert.equal(f.state.value,1);assert.equal(p.getCursor(),0);
 await p.seek(65);assert.equal(f.state.value,66);await p.prev();assert.equal(f.state.value,65);p.reset();assert.equal(f.state.value,0);assert.deepEqual(f.active(),[]);await p.step();assert.equal(f.state.value,1);
});
