'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const test = require('node:test');
const source = fs.readFileSync('static/js/sequential.js', 'utf8');
function fixture() {
  const button = answer => ({dataset:{answer}, addEventListener(_, fn){this.click=fn;}});
  const buttons = [button('true'), button('false')];
  const masked = [{style:{display:''}, aria:null}, {style:{display:'none'}, aria:'true'}].map(node => Object.assign(node, {
    getAttribute(){return this.aria;}, setAttribute(_,value){this.aria=value;}, removeAttribute(){this.aria=null;}
  }));
  const c = {
    document:{querySelectorAll:()=>masked},
    visualContainer:{classList:{remove(){}}},
    predictionPanel:{hidden:true}, predictionQuestion:{textContent:'',setAttribute(){},focus(){}},
    predictionFeedback:{textContent:''}, predictionChoices:{innerHTML:'',querySelectorAll:()=>buttons}, predictionHint:{},
    predictionsEnabled:{checked:true}, practiceMode:{checked:true},
    predictionPendingIndex:-1, predictionHintLevel:0, predictionAutoplay:false,
    predictionMaskedElements:new Map(), learningProgress:{attempts:0,correct:0,concepts:{}},
    saveLearningProgress(){}, setSimulationButtonsEnabled(){}, simStatus:{textContent:''},
    lockStepUntilInput:false, traceWasNavigated:false, cursor:0, total:4,
    consoleState:{trace:{steps:[]}},
  };
  c.tracePlayer={pause(){},getCursor:()=>c.cursor,isAtEnd:()=>c.cursor===c.total-1,
    async step(){c.cursor++;c.clearPrediction();return true;},reset(){c.cursor=-1;c.clearPrediction();},async play(){c.played=true;}};
  vm.createContext(c);
  vm.runInContext(source.slice(source.indexOf('  function predictionForStep('),source.indexOf('  function collectPayload(',source.indexOf('  function predictionForStep('))),c);
  return {c,buttons,masked};
}
const step = {pedagogy:{concept:'condition',condition:{source:'p == NULL',substituted:'&p == NULL',result:false}}};
test('question gates next event and masks all registered textual aids; skip applies exactly one event', async()=>{
  const {c,masked}=fixture();
  assert.equal(c.requestPrediction(step,1),true);
  assert.equal(c.cursor,0);
  assert.equal(c.predictionPendingIndex,1);
  assert.match(c.predictionQuestion.textContent,/Antes del paso 2/);
  masked.forEach(n=>assert.equal(n.style.display,'none'));
  assert.equal(c.requestPrediction(step,1),false);
  await c.advancePendingPrediction(false);
  assert.equal(c.cursor,1);assert.equal(c.predictionPanel.hidden,true);
  assert.equal(masked[0].style.display,'');assert.equal(masked[0].aria,null);
  assert.equal(masked[1].style.display,'none');assert.equal(masked[1].aria,'true');
  await c.advancePendingPrediction(false);assert.equal(c.cursor,1);
});
test('answer records once, reveals effect and retains retrospective feedback, including final event',async()=>{
  const {c,buttons}=fixture();c.cursor=2;
  c.requestPrediction(step,3);buttons[1].click();await new Promise(setImmediate);
  assert.equal(c.cursor,3);assert.equal(c.learningProgress.correct,1);
  assert.equal(c.learningProgress.attempts,1);assert.equal(c.lockStepUntilInput,true);
  assert.equal(c.predictionPanel.hidden,true);assert.match(c.simStatus.textContent,/Correcto.*Paso 4 mostrado/);
  buttons[1].click();assert.equal(c.learningProgress.attempts,1);
});
test('hints never leak final answer and stale answers cannot advance after navigation',async()=>{
  const {c,buttons}=fixture();c.requestPrediction(step,1);
  for(let i=0;i<8;i++)c.predictionHint.onclick();
  assert.doesNotMatch(c.predictionFeedback.textContent,/no entra|entra al cuerpo/);
  c.clearPrediction();buttons[0].click();await new Promise(setImmediate);assert.equal(c.cursor,0);
  assert.equal(c.learningProgress.attempts,0);
});
test('malformed conditions are not scored as false; opt-out does not block',()=>{
  const {c}=fixture();assert.equal(c.predictionForStep({pedagogy:{concept:'condition'}}),null);
  c.predictionsEnabled.checked=false;assert.equal(c.requestPrediction(step,1),false);
});
test('autoplay asks before first event and cursor callback pauses before subsequent predictive event',async()=>{
  const {c}=fixture();c.consoleState.trace.steps=[step];await c.playWithPredictions();
  assert.equal(c.cursor,-1);assert.equal(c.predictionPendingIndex,0);assert.equal(c.played,undefined);
  assert.match(source,/if \(predictionAutoplay && cursor < traceTotalSteps - 1\) \{\s*requestPrediction\(event.trace.steps\[cursor \+ 1\], cursor \+ 1\)/);
});
test('all navigation clears pending questions; practice targets code, conditions, captions and results',()=>{
  assert.match(source,/onCursorChange: \(event\) => \{[\s\S]*?clearPrediction\(\)/);
  for(const selector of ['#seq-code-region','#seq-pedagogy-summary','.seq-c-semantics','#seq-printf-console','#action-history','.classroom-caption']) assert.ok(source.includes(selector));
  assert.match(source,/predictionSkip\?\.addEventListener\("click", \(\) => advancePendingPrediction\(false\)\)/);
  assert.match(source,/if \(prepare\) prepare.after\(controls\)/);
  assert.doesNotMatch(source,/getElementById\("seq-code-region"\)\?\.classList.remove\("didactic-technical"\)/);
});
test('real trace player autoplay stops before condition effect and resumes only on answer',async()=>{
  const {c,buttons}=fixture();const timers=[];
  c.window={setTimeout:fn=>timers.push(fn)};
  c.document.readyState='loading';c.document.addEventListener=()=>{};
  vm.runInContext(fs.readFileSync('static/js/interpreter_runtime.js','utf8'),c);
  let state=null;
  c.tracePlayer=c.window.InterpreterRuntime.createTracePlayer({codeElement:null,statusElement:c.simStatus,
    renderState:s=>{state=s;},onCursorChange:event=>{
      c.clearPrediction();if(event.reason!=='advance')c.predictionAutoplay=false;
      if(c.predictionAutoplay && event.cursor<event.trace.steps.length-1)c.requestPrediction(event.trace.steps[event.cursor+1],event.cursor+1);
    }});
  c.consoleState.trace={steps:[
    {state_snapshot:{value:0},state_after:{value:1},pedagogy:{concept:'call'}},
    {...step,state_snapshot:{value:1},state_after:{value:2}},
  ]};
  c.tracePlayer.loadTrace(c.consoleState.trace);
  const play=c.playWithPredictions();
  while(timers.length){timers.shift()();await new Promise(setImmediate);}
  await play;
  assert.equal(c.tracePlayer.getCursor(),0);assert.equal(state.value,1);assert.equal(c.predictionPendingIndex,1);
  buttons[1].click();await new Promise(setImmediate);
  assert.equal(c.tracePlayer.getCursor(),1);assert.equal(state.value,2);assert.equal(c.predictionPanel.hidden,true);
  assert.match(c.simStatus.textContent,/Correcto/);
});
test('completed trace unlocks when reset, rewound or sought to an earlier step',()=>{
  const {c}=fixture();
  c.refreshPrintfConsole=()=>{};
  const start=source.indexOf('      onCursorChange: (event) => {');
  const end=source.indexOf('        if (consoleState.resultMessage)',start);
  const callback=source.slice(start,end).replace('      onCursorChange: (event) => {','function cursorChanged(event) {')+'}';
  vm.runInContext(callback,c);
  const trace={steps:[{},{},{}]};
  for(const reason of ['reset','prev','seek','load','prev_to_start']) {
    c.cursorChanged({reason:'advance',cursor:2,trace});
    assert.equal(c.lockStepUntilInput,true);
    c.cursorChanged({reason,cursor:reason==='reset'?-1:0,trace});
    assert.equal(c.lockStepUntilInput,false,reason);
  }
  c.cursorChanged({reason:'clear',cursor:-1,trace:null});
  assert.equal(c.lockStepUntilInput,false);
});
test('disabling questions restores aids without advancing or leaving a pending status',()=>{
  const {c,masked}=fixture();
  c.requestPrediction(step,1);c.predictionAutoplay=true;
  c.predictionsEnabled.addEventListener=(_,fn)=>{c.disableQuestions=fn;};
  const start=source.indexOf('  predictionsEnabled?.addEventListener("change",');
  const end=source.indexOf('  resetLearningButton?',start);
  vm.runInContext(source.slice(start,end),c);
  c.predictionsEnabled.checked=false;c.disableQuestions();
  assert.equal(c.cursor,0);assert.equal(c.predictionPendingIndex,-1);
  assert.equal(c.predictionPanel.hidden,true);assert.equal(c.predictionAutoplay,false);
  assert.equal(masked[0].style.display,'');assert.match(c.simStatus.textContent,/Preguntas desactivadas/);
});
