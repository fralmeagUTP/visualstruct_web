const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('static/js/hierarchical.js','utf8');const nodes={};const context=vm.createContext({window:{},document:{addEventListener(){},getElementById:id=>nodes[id]}});vm.runInContext(source,context);
const cases=JSON.parse(fs.readFileSync('qa/hier_prediction_fixtures.json','utf8'));let decisions=0;
for(const item of cases){let trace=item.trace,cursor=-1;const before=JSON.stringify(trace),controller=context.createHierPredictionController(()=>trace,()=>cursor);let target;
 while(target=controller.sync()){
  assert.ok(target.index>cursor);assert.equal(Object.hasOwn(target,'answer'),false);assert.deepEqual(Array.from(target.options,o=>o.value),['true','false']);
  const frame=trace.steps[target.index].pedagogy;assert.equal(typeof frame.condition.result,'boolean');assert.match(target.prompt,new RegExp(`paso ${target.index+1}`));
  assert.match(controller.hint(),/^Pista 1:/);assert.match(controller.hint(),/^Pista 2:/);
  const answer=controller.answer(String(frame.condition.result));assert.equal(answer.correct,true);assert.equal(answer.counted,true);assert.equal(controller.answer(String(frame.condition.result)).counted,false);
  cursor=target.index;controller.sync();cursor=target.index-1;assert.equal(controller.answer(String(frame.condition.result)).counted,false);cursor=target.index;decisions++;
 }
 assert.equal(controller.answer('false'),null);assert.equal(controller.skip(),null);assert.equal(JSON.stringify(trace),before);
 cursor=-1;trace=JSON.parse(before);assert.match(controller.hint(),/^Pista 1:/);const next=controller.sync();controller.skip();assert.equal(controller.answer('true').counted,false);
 // Manual navigation reveals a condition and cannot be used to farm points by backing up.
 trace=JSON.parse(before);cursor=-1;const manual=controller.sync();cursor=manual.index;controller.sync();cursor=manual.index-1;assert.equal(controller.answer('true').counted,false);
}
// Actual UI handlers grade/reveal the upcoming frame; omit advances without a score.
let cursor=-1;const trace=cases[0].trace;function node(){return {value:'',disabled:false,textContent:'',innerHTML:'',handlers:{},addEventListener(name,handler){this.handlers[name]=handler;}};}
for(const key of ['predictionSelect','checkPrediction','hintButton','skipPrediction','predictionFeedback','practiceMode','resetProgress'])context[key]=node();
Object.assign(context,{predictionController:null,predictionTargetKey:'',predictionTraceRef:null,consoleState:{trace},traceCursor:-1,conceptualProgress:{attempts:0,correct:0},renderConceptualProgress(){},practiceCover:{hidden:false},visualContainer:{classList:{remove(){}}}});
nodes['hier-prediction-prompt']=node();context.tracePlayer={hasTrace:()=>true,seek(index){cursor=index;context.traceCursor=index;context.syncPredictionUI();}};
const begin=source.indexOf('  predictionController = createHierPredictionController('),end=source.indexOf('  function compareStateSummary',begin);vm.runInContext(source.slice(begin,end),context);
let pending=context.predictionController.sync();context.predictionSelect.value=String(trace.steps[pending.index].pedagogy.condition.result);context.checkPrediction.handlers.click();assert.equal(cursor,pending.index);assert.equal(context.conceptualProgress.attempts,1);assert.match(context.predictionFeedback.textContent,/Decisión revelada/);
pending=context.predictionController.sync();context.skipPrediction.handlers.click();assert.equal(cursor,pending.index);assert.equal(context.conceptualProgress.attempts,1);assert.match(context.predictionFeedback.textContent,/sin responder/);
console.log(`PASS ${decisions} real decisions in ABB/AVL/RN/heap; future-only targets, two options, immutable traces, hints reset, one score, backward/manual/omit no farming; actual grade/omit handlers advance`);
(async()=>{
 context.traceCursor=-1;context.predictionTraceRef=null;context.practiceMode.checked=true;
 context.simStepButton=node();context.isStepByStepEnabled=()=>true;context.ensureTraceForCurrentSelection=async()=>true;context.predictionSelect.closest=()=>({open:false});
 let steps=0;context.tracePlayer.step=async()=>{steps++;context.traceCursor++;context.syncPredictionUI();};
 const start=source.indexOf('  simStepButton?.addEventListener("click", async () => {'),stop=source.indexOf('  prepareButton?',start);vm.runInContext(source.slice(start,stop),context);
 await context.simStepButton.handlers.click();assert.equal(steps,1,'ordinary instruction advances once');
 const next=context.predictionController.sync();context.traceCursor=next.index-1;await context.simStepButton.handlers.click();assert.equal(steps,1,'practice blocks before condition');assert.match(context.predictionFeedback.textContent,/estado visible aún es el anterior/);
 context.practiceMode.checked=false;await context.simStepButton.handlers.click();assert.equal(steps,2,'normal mode still advances one instruction');
 console.log('PASS actual Next handler: normal one instruction, practice intercepts only before pending decision');
})().catch(error=>{console.error(error);process.exitCode=1;});
