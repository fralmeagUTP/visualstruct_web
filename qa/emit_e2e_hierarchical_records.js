'use strict';
const fs=require('node:fs'),vm=require('node:vm');
const {JSDOM}=require('jsdom');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
(async()=>{
 const dom=new JSDOM(`<main id="root"><div id="visual-region"><div id="visual-state"></div></div><div id="hier-path-view"></div><div id="hier-stack-view"></div><div id="hier-variables-view"></div><div id="hier-printf-console" data-console-copy="">(sin salida printf en esta ruta)</div><div id="hier-sim-counter"></div><button id="hier-sim-step"></button><button id="hier-sim-prev"></button><div id="message-box"></div><div id="op-pseudocode"></div></main>`,{runScripts:'outside-only',pretendToBeVisual:true});
 const w=dom.window,ctx=dom.getInternalVMContext();w.structuredClone=structuredClone;
 try {
  for(const path of ['static/js/hierarchical.js','static/js/classroom_view.js'])vm.runInContext(fs.readFileSync(path,'utf8'),ctx);
  const d=w.document,container=d.getElementById('visual-state');
  w.ClassroomView.mount({root:'#root',visual:'#visual-region',stage:'#visual-state',memory:['.abb-instruction-memory','.hier-retired-memory']});
  let cursor=-1;
  function render(){
   const ped=cursor<0?input.trace.steps[0].pedagogy.initial_frame:input.trace.steps[cursor].pedagogy;
   const state=ped.memory_state;w.auditState=structuredClone(state);
   w.renderHierState(input.family,state,container,null,null,null,null,null,null);
   w.renderHierPedagogy(ped,'intermediate');
   d.getElementById('hier-sim-counter').textContent='Paso: '+(cursor+1)+'/'+input.trace.steps.length;
  }
  d.getElementById('hier-sim-step').onclick=()=>{cursor++;render();};
  d.getElementById('hier-sim-prev').onclick=()=>{cursor--;render();};
  render();await new Promise(resolve=>w.requestAnimationFrame(resolve));
  const collect=vm.runInContext('('+input.collect+')',ctx);
  const records=await collect({steps:input.trace.steps.length});
  process.stdout.write(JSON.stringify(records));
 }finally{w.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
