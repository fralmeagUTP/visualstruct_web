/* Entire Flask HTML/script/controller circuit in jsdom, not browser/layout evidence. */
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
let inputs=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),mode=process.argv[3]||'normal';
// One page per process prevents unrelated RAF callbacks from surviving DOM teardown.
if(process.argv[4]===undefined && inputs.length>1){
 const {spawnSync}=require('node:child_process'),results=[];
 for(let i=0;i<inputs.length;i++){
  const run=spawnSync(process.execPath,[__filename,process.argv[2],mode,String(i)],{encoding:'utf8',timeout:60000});
  if(run.status!==0){process.stderr.write(run.stderr||String(run.error));process.exit(1);}
  results.push(...JSON.parse(run.stdout));
 }
 process.stdout.write(JSON.stringify(results),()=>process.exit(0));
}else{
 if(process.argv[4]!==undefined)inputs=[inputs[Number(process.argv[4])]];
const tick=()=>new Promise(r=>setImmediate(r));
const plain=x=>JSON.parse(JSON.stringify(x));
(async()=>{const results=[];
for(const entry of inputs){
 const errors=[],calls=[];const dom=new JSDOM(entry.html,{runScripts:'outside-only',url:'http://localhost/'+entry.route,pretendToBeVisual:true});const w=dom.window,ctx=dom.getInternalVMContext(),raf=new Set();
 const nativeRAF=w.requestAnimationFrame.bind(w),nativeCancel=w.cancelAnimationFrame.bind(w);
 w.requestAnimationFrame=callback=>{const id=nativeRAF(time=>{raf.delete(id);callback(time);});raf.add(id);return id;};
 w.cancelAnimationFrame=id=>{raf.delete(id);nativeCancel(id);};
 try{
 await tick();w.structuredClone=structuredClone;
 // Geometry-only browser APIs. No state, renderer, player or controller is stubbed.
 w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});w.HTMLElement.prototype.scrollIntoView=function(){};w.ResizeObserver=class{observe(){}disconnect(){}};
 w.addEventListener('error',e=>errors.push(e.error?.stack||e.message));
 const expectedRequest={url:'/'+entry.route+'/operate',method:'POST',body:JSON.stringify({operation:entry.op,payload:Object.fromEntries(Object.entries(entry.payload).map(([k,v])=>[k,String(v)]))})};
 w.fetch=async(url,options)=>{
  // Record every attempt before validation, including caught/invalid requests.
  const attempt={url:String(url),method:options?.method||'GET',body:options?.body??null};calls.push(attempt);
  assert.equal(attempt.url,expectedRequest.url);assert.equal(attempt.method,expectedRequest.method);
  assert.deepEqual(JSON.parse(attempt.body),JSON.parse(expectedRequest.body));attempt.validated=true;
  return {ok:entry.http_status>=200&&entry.http_status<300,status:entry.http_status,json:async()=>structuredClone(entry.data)};
 };
 const transport=()=>{
  assert.equal(calls.length,1,'TRANSPORT_ATTEMPTS '+JSON.stringify(calls));
  assert.deepEqual(calls[0],{...expectedRequest,validated:true},'TRANSPORT_VALIDATION');
 };
 let mutated=0;
 for(const script of w.document.querySelectorAll('script')){
  if(script.src){const path=new URL(script.src).pathname.slice(1);if(mode==='omit_contextual'&&path==='static/js/contextual_help.js')continue;
   let source=fs.readFileSync(path,'utf8');
   if(mode==='renderer_only'&&path==='static/js/'+(entry.prefix==='hier'?'hierarchical':'sequential')+'.js'){
    const statement=`if (cursor < 0) window.ContextualHelp?.frame("${entry.prefix}", null);`;
    assert.equal(source.split(statement).length,2);source=source.replace(statement,'');mutated++;
   }
   if(path==='static/js/sequential.js'&&['no_linked_handler','no_current_handler','stale_view_dom'].includes(mode)){
    const view=mode==='no_current_handler'?'current':'linked';
    const statement=mode==='stale_view_dom'?'renderSublistDeletionState(state, container.dataset.stackVisualMode === "linked" || container.dataset.structuralVisualMode === "nodes")':`${view}ViewButton?.addEventListener("click", () => setStackVisualMode("${view}"));`;
    assert.equal(source.split(statement).length,2);
    source=source.replace(statement,mode==='stale_view_dom'?'renderSublistDeletionState(state, false)':'');mutated++;
   }
   vm.runInContext(source,ctx,{filename:path});
  }else if(script.textContent.trim())vm.runInContext(script.textContent,ctx);
 }
 w.document.dispatchEvent(new w.Event('DOMContentLoaded'));await tick();
 const generic=entry.prefix==='hier'?'renderHierState':'renderVisualState',original=w[generic];
 w[generic]=function(...args){w.auditState=structuredClone(args[1]);return original(...args);};
 const prefix=entry.prefix,select=w.document.getElementById('operation-select');
 const choose=op=>{select.value=op;select.dispatchEvent(new w.Event('change',{bubbles:true}));};
 const card=expected=>assert.deepEqual([...w.document.querySelectorAll('#'+prefix+'-pedagogy-summary > .contextual-help-points > li')].map(x=>x.textContent),expected,'OPERATION_CARD '+entry.family+' '+entry.op+' '+mode);
 choose(entry.op);
 for(const[k,v]of Object.entries(entry.payload)){const el=w.document.querySelector('[name="'+k+'"]');assert(el);el.value=String(v);el.dispatchEvent(new w.Event('input',{bubbles:true}));}
 w.document.getElementById(prefix+'-step-mode').click();w.document.getElementById(prefix==='hier'?'hier-sim-play':'seq-sim-execute').click();
 for(let n=0;n<100&&!calls.length;n++)await tick();await tick();await tick();
 transport();assert.deepEqual(errors,[]);
 if(!entry.data.success){results.push({case:entry.case,rejected:true});continue;}
 if(mode.startsWith('extra_fetch_')){
  const url=mode==='extra_fetch_url'?'/unexpected-probe':expectedRequest.url;
  const method=mode==='extra_fetch_method'?'GET':'POST';
  const body=mode==='extra_fetch_body'?'{}':expectedRequest.body;
  await w.fetch(url,{method,body}).catch(()=>{});
 }
 const steps=entry.data.execution_trace.steps;let frames=0,activeView=null;
 const assertView=state=>{
  const visual=w.document.getElementById('visual-state');
  assert.equal(visual.dataset.stackVisualMode,activeView,'VIEW_MODE');
  for(const view of ['current','linked']){
   const button=w.document.getElementById('stack-view-'+view);
   assert.equal(button.getAttribute('aria-pressed'),String(view===activeView),'VIEW_PRESSED');
   assert.equal(button.classList.contains('is-active'),view===activeView,'VIEW_ACTIVE');
  }
  const groups=visual.querySelectorAll('.seq-sublist-classroom > div[style]');
  assert.equal(groups.length,1,'VIEW_DOM_GROUP');assert.equal(groups[0].style.display,activeView==='linked'?'block':'flex','VIEW_DOM_DISPLAY');
  const expected=state.items.map(x=>({parent:x.parent,children:x.children}));
  const currentValues=[...visual.querySelectorAll('.viz-svg-node-text')].map(x=>x.textContent);
  if(activeView==='current')assert.deepEqual(currentValues,expected.flatMap(x=>[x.parent,...x.children]).map(String),'VIEW_DOM_CURRENT_VALUES');
  else{
   assert.deepEqual(currentValues,[],'VIEW_DOM_LINKED_CLASSES');
   const linked=[...visual.querySelectorAll('.stack-sublist-parent')].map(x=>({parent:Number(x.querySelector('.stack-sublist-parent-node .stack-linked-field strong').textContent),children:[...x.querySelectorAll('.stack-sublist-child .stack-linked-field:not(.stack-linked-next) strong')].map(y=>Number(y.textContent))}));
   assert.deepEqual(linked,expected,'VIEW_DOM_LINKED_VALUES');
  }
 };
 const observe=index=>{
  transport();
  assert.equal(w.document.getElementById(prefix+'-sim-counter').textContent,'Paso: '+(index+1)+'/'+steps.length);
  const state=index<0?steps[0].state_snapshot:steps[index].pedagogy.memory_state;
  assert.deepEqual(plain(w.auditState),plain(state),'exact memory projection '+entry.case+' '+index);
  if(entry.family==='sublist')assertView(state);
  if(prefix==='hier'){
   assert.deepEqual([...w.document.querySelectorAll('[data-abb-frame]')].map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)})),state.tree_frames.map(x=>({id:x.id,depth:x.depth})), 'DOM recursive scopes');
  }else{
   assert.deepEqual([...w.document.querySelectorAll('[data-sublist-frame]')].map(x=>x.dataset.sublistFrame),state.sublist_frames.map(x=>x.function), 'DOM sublist scopes');
  }
  if(index<0){
   assert.equal(w.document.querySelectorAll(prefix==='hier'?'#hier-variables-view tbody tr':'#seq-variable-view [data-seq-variable]').length,entry.family==='red_black'?steps[0].pedagogy.initial_frame.variables.length:0);
   assert.equal(w.document.querySelectorAll('[data-abb-frame], [data-sublist-frame]').length,0);
   if(entry.family==='abb')assert.equal(w.document.querySelectorAll('[data-abb-caller]').length,0);
   card(entry.card);
  }
  frames++;
 };
 for(const view of entry.family==='sublist'?['current','linked']:['current']){
  if(entry.family==='sublist'){activeView=view;w.document.getElementById('stack-view-'+view).click();}observe(-1);
  for(let i=0;i<steps.length;i++){const b=w.document.getElementById(prefix+'-sim-step');assert(!b.disabled);b.click();await tick();observe(i);}
  assert(w.document.getElementById(prefix+'-sim-step').disabled);
  for(let i=steps.length-2;i>=-1;i--){const b=w.document.getElementById(prefix+'-sim-prev');assert(!b.disabled);b.click();await tick();observe(i);}
  assert(w.document.getElementById(prefix+'-sim-prev').disabled);
 }
 if(entry.family==='sublist'){activeView='current';w.document.getElementById('stack-view-current').click();observe(-1);}
 choose(entry.other);card(entry.other_card);choose(entry.op);card(entry.card);await tick();await tick();
 transport();assert.deepEqual(errors,[]);if(mode==='renderer_only')assert.equal(mutated,1);
 results.push({case:entry.case,frames,post_count:calls.length});
 }catch(error){console.error('CASE',entry.case);throw error;}finally{for(const id of raf)nativeCancel(id);w.close();}
}
process.stdout.write(JSON.stringify(results),()=>process.exit(0));
})().catch(e=>{console.error(e);process.exit(1);});
}
