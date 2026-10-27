'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test'),path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.join(__dirname,'../static/js/hierarchical.js'),'utf8');
const begin=source.indexOf('  async function executeOperationAndLoadTrace('),end=source.indexOf('  async function ensureTraceForCurrentSelection()',begin);
assert.ok(begin>=0&&end>begin);
const code=source.slice(begin,end)+'\nthis.execute = executeOperationAndLoadTrace;';
for(const kind of ['abb','avl','red_black','binary_heap'])for(const finalOnly of [false,true])for(const marker of ['execution_started','validation'])test(`${kind} pre-C ${marker} rejection, finalOnly=${finalOnly}`,async()=>{
 const messages=[],calls=[];const oldState={items:[4,2]},oldHistory=[{operation:'insertar',payload:{value:4}}];
 const response={success:false,message:'El campo valor debe ser un número entero.',visual_state:oldState,history:oldHistory,execution_trace:{steps:[],[marker]:marker==='validation'?{accepted:false}:false}};
 const context={pendingExecution:false,setSimulationButtonsEnabled:()=>{},resetButton:{disabled:false},form:{dataset:{operateUrl:'/operate'}},
  fetch:async()=>({json:async()=>response}),showHierMessage:(text,success)=>messages.push({text,success}),simStatus:{textContent:''},
  model:{id:kind,visual_state:oldState,history:oldHistory},pageState:{modelId:kind,visualState:oldState},consoleState:{resultMessage:null},
  tracePlayer:{pause:()=>calls.push('pause'),loadTrace:()=>calls.push('loadTrace'),reset:()=>calls.push('reset')},
  updateHierDidacticPanel:()=>calls.push('updateCode'),simulateHierDidacticExecution:()=>calls.push('simulate'),
  hPushUniqueHistoryEntry:()=>calls.push('history'),repaint:()=>calls.push('repaint')};
 vm.createContext(context);vm.runInContext(code,context);
 const result=await context.execute({name:'insertar'},{value:'bad'},'key',{finalOnly});
 assert.equal(result,null,'rejected request must not make caller replay old trace');
 assert.equal(messages.at(-1).text,response.message);assert.equal(messages.at(-1).success,false);
 assert.equal(context.consoleState.resultMessage,null);assert.equal(context.model.visual_state,oldState);assert.equal(context.model.history,oldHistory);
 assert.ok(!calls.some(x=>['loadTrace','reset','simulate','history','repaint','updateCode'].includes(x)));
 assert.equal(context.pendingExecution,false);assert.equal(context.resetButton.disabled,false);
});
