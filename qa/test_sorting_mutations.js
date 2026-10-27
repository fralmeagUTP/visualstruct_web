const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(process.env.SORTING_SOURCE || 'static/js/sorting.js','utf8');
function harness(){
 const calls=[],messages=[],rendered=[],codeUpdates=[];const buttons={};
 for(const name of ['createButton','randomButton','resetButton','playButton','prepareButton','loadExampleButton','algorithmSelect','manualInput','randomSize','randomMin','randomMax','stepNavigation','countingNavigation','countingJump','stepButton','speedSlider','prevButton','nextButton','pauseButton','startButton','endButton','repeatButton','restartExecutionButton','progress','stepToggle'])buttons[name]={disabled:false,checked:true,value:''};
 buttons.algorithmSelect.value='radixsort';buttons.manualInput.value='3,1,2,1';
 const context=vm.createContext({window:{confirm:()=>true,sessionStorage:{setItem(){},removeItem(){}}},document:{addEventListener(){},querySelectorAll:()=>[],getElementById:()=>null},console, ...buttons,runPending:false,trace:{operation_name:'radixsort'},model:{visual_state:{algorithm:'radixsort',items:[3,1,2,1]},execution_trace:{}},history:[],pendingPredictionIndex:7,currentAttemptState:{},comparison:null,comparisonVersion:0,predictionCard:null,codePanel:null,functionList:null,hideComments:null,visualContainer:{},historyBox:{},consoleBox:{},exampleExplanation:null,guidedExample:null,
  createUrl:'/create',randomUrl:'/random',algorithmUrl:'/algorithm',runUrl:'/run',resetUrl:'/reset',controls:{querySelectorAll:()=>[]},
  fetch:(url,options)=>new Promise((resolve,reject)=>calls.push({url,options,resolve:data=>resolve({json:async()=>data}),reject})),
  setMessage:(...args)=>messages.push(args),renderSortingVisualState:state=>rendered.push(state),renderSortingHistory(){},renderSortingConsole(){},renderAnalysis(){},renderCountingOutcome(){},renderPedagogy(){},renderLiveMemory(){},updateCodeByAlgorithm:()=>codeUpdates.push(buttons.algorithmSelect.value),sHistoryFromSaved:x=>x||[],isStepByStepEnabled:()=>true,
  tracePlayer:{hasTrace:()=>true,isAtEnd:()=>false,getCursor:()=>0,getTotalSteps:()=>2,loadTrace(){},seek:async()=>{},playFromStart:async()=>{},clear(){},pause(){}},sEnhanceCodeNavigation(){},sById:()=>null});
 const stateStart=source.indexOf('  function setButtonsState() {'),stateEnd=source.indexOf('  function setSpeed(',stateStart);vm.runInContext(source.slice(stateStart,stateEnd),context);
 const start=source.indexOf('  async function postJson('),end=source.indexOf('  function fillAlgorithmSelect()',start);vm.runInContext(source.slice(start,end),context);
 return {context,calls,messages,rendered,codeUpdates,buttons};
}
const runResponse={success:true,message:'run',visual_state:{algorithm:'radixsort',items:[1,1,2,3]},history:[{operation:'run'}],main_c:'main',execution_trace:{operation_name:'radixsort',steps:[{}]}};
const resetResponse={success:true,message:'reset',visual_state:{algorithm:'burbuja',items:[]},history:[],main_c:'empty'};
test('deferred run blocks reset and create until mutation finishes',async()=>{
 const h=harness(),run=h.context.runSorting(false,false);const reset=h.context.resetSorting(),create=h.context.createArray();const count=h.calls.length;
 for(const call of h.calls)call.resolve(call.url==='/run'?runResponse:resetResponse);
 await Promise.all([run,reset,create]);assert.equal(count,1,'only run may reach backend while pending');assert.equal(h.context.runPending,false);assert.equal(h.buttons.resetButton.disabled,false);
});
test('reset restores one coherent algorithm, input, model and code selection',async()=>{
 const h=harness(),reset=h.context.resetSorting();h.calls[0].resolve(resetResponse);await reset;
 assert.equal(h.context.model.visual_state.algorithm,'burbuja');assert.equal(h.buttons.algorithmSelect.value,'burbuja');assert.equal(h.buttons.manualInput.value,'');assert.equal(h.context.model.execution_trace,null);assert.equal(h.context.trace,null);assert.deepEqual(h.codeUpdates,['burbuja']);
});
test('network failure restores controls and reports a recoverable message',async()=>{
 const h=harness(),run=h.context.runSorting(false,false);h.calls[0].reject(new Error('offline'));await run;
 assert.equal(h.context.runPending,false);assert.equal(h.buttons.resetButton.disabled,false);assert.ok(h.messages.some(([text,ok])=>ok===false));
});
test('controls are disabled during a request, cancel reset makes no request',async()=>{
 const h=harness(),run=h.context.runSorting(false,false);
 assert.equal(h.buttons.createButton.disabled,true);assert.equal(h.buttons.resetButton.disabled,true);assert.equal(h.buttons.algorithmSelect.disabled,true);
 h.calls[0].resolve(runResponse);await run;assert.equal(h.buttons.algorithmSelect.disabled,false);
 h.context.window.confirm=()=>false;const count=h.calls.length;await h.context.resetSorting();assert.equal(h.calls.length,count);assert.equal(h.context.model.visual_state.algorithm,'radixsort');
});
test('algorithm selection uses returned visual state and serializes with run',async()=>{
 const h=harness();h.buttons.algorithmSelect.value='shell';const selection=h.context.selectAlgorithm();const run=h.context.runSorting(false,false);assert.equal(h.calls.length,1);
 h.calls[0].resolve({...resetResponse,visual_state:{algorithm:'shell',items:[3,1,2,1]}});await Promise.all([selection,run]);assert.equal(h.context.model.visual_state.algorithm,'shell');assert.equal(h.context.model.execution_trace,null);assert.equal(h.buttons.algorithmSelect.disabled,false);
});
