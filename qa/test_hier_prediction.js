'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {extractRange,harness}=require('./hier_prediction_harness');
const source=fs.readFileSync('static/js/hierarchical.js','utf8');
const context=vm.createContext({window:{},document:{addEventListener(){}}});vm.runInContext(source,context);
const cases=JSON.parse(fs.readFileSync('qa/hier_prediction_fixtures.json','utf8'));let decisions=0;
for(const item of cases){let trace=item.trace,cursor=-1;const before=JSON.stringify(trace),controller=context.createHierPredictionController(()=>trace,()=>cursor);let target;
 while(target=controller.sync()){
  const unchanged=JSON.stringify(target);assert.equal(controller.answer('none'),null);assert.equal(controller.answer(''),null);assert.equal(JSON.stringify(controller.sync()),unchanged);
  assert.ok(target.index>cursor);assert.equal(Object.hasOwn(target,'answer'),false);assert.equal(Object.hasOwn(target,'evidence'),false);assert.deepEqual(Array.from(target.options,o=>o.value),['true','false']);
  const frame=trace.steps[target.index].pedagogy;assert.equal(typeof frame.condition.result,'boolean');assert.match(target.prompt,new RegExp(`paso ${target.index+1}`));
  const hints=[controller.hint(),controller.hint(),controller.hint()];hints.forEach((hint,i)=>assert.match(hint,new RegExp(`^Pista ${i+1}:`)));assert.equal(new Set(hints).size,3);assert.equal(controller.hint(),hints[2]);
  const oldCursor=cursor,answer=controller.answer(String(frame.condition.result));assert.equal(cursor,oldCursor);assert.equal(answer.correct,true);assert.equal(answer.counted,true);assert.ok(answer.evidence.includes(frame.condition.substituted||frame.condition.source));assert.equal(controller.answer(String(frame.condition.result)).counted,false);
  cursor=target.index;controller.sync();cursor=target.index-1;assert.equal(controller.answer(String(frame.condition.result)).counted,false);cursor=target.index;decisions++;
 }
 assert.equal(controller.answer('false'),null);assert.equal(controller.skip(),null);assert.equal(JSON.stringify(trace),before);
 cursor=-1;trace=JSON.parse(before);assert.match(controller.hint(),/^Pista 1:/);controller.skip();assert.equal(controller.answer('true').counted,false);
 // Manual navigation reveals a condition and cannot farm points by backing up.
 trace=JSON.parse(before);cursor=-1;const manual=controller.sync();cursor=manual.index;controller.sync();cursor=manual.index-1;assert.equal(controller.answer('true').counted,false);
 trace=JSON.parse(before);cursor=-1;const wrongTarget=controller.sync();const correct=trace.steps[wrongTarget.index].pedagogy.condition.result;assert.equal(controller.answer(String(!correct)).correct,false);assert.equal(controller.answer(String(correct)).counted,false);
}
assert.equal(decisions,79,'preserve the complete historical real-decision fixture corpus');
// Missing or changed extraction boundaries must fail explicitly, not slice to -1.
assert.throws(()=>extractRange(source,'MISSING START','MISSING END','negative'),/missing start/);
assert.throws(()=>extractRange(source+source,'  predictionController = createHierPredictionController(','  let comparisonRequestVersion =','negative'),/ambiguous start/);
assert.throws(()=>extractRange(source,'  predictionController = createHierPredictionController(','MISSING END','negative'),/missing end/);
(async()=>{
 for(const item of cases){
  const {context:c,nodes,listeners,Element,counts}=harness(item.trace);const trace=item.trace,before=JSON.stringify(trace);
  let pending=c.predictionController.sync();const answer=String(trace.steps[pending.index].pedagogy.condition.result);
  c.predictionSelect.value=answer;const originalCursor=c.traceCursor;c.checkPrediction.handlers.click();
  assert.equal(c.traceCursor,originalCursor);assert.equal(c.conceptualProgress.attempts,1);assert.equal(c.conceptualProgress.correct,1);assert.match(c.predictionFeedback.textContent,/Decisión revelada/);assert.match(c.predictionFeedback.textContent,/cursor se conserva/);assert.match(c.predictionFeedback.textContent,/condición futura del paso/);
  c.checkPrediction.handlers.click();assert.equal(c.conceptualProgress.attempts,1);c.skipPrediction.handlers.click();assert.equal(c.traceCursor,originalCursor);assert.equal(c.conceptualProgress.attempts,1);assert.match(c.predictionFeedback.textContent,/sin responder/);
  c.resetProgress.handlers.click();assert.equal(c.conceptualProgress.attempts,0);c.checkPrediction.handlers.click();assert.equal(c.conceptualProgress.attempts,0,'reset metrics does not rescore the same target');
  // A new trace clears target/hints/scoring. Practice preserves prior state until manual Next.
  c.consoleState.trace=JSON.parse(before);c.traceCursor=-1;c.syncPredictionUI();c.practiceMode.checked=true;
  const next=c.predictionController.sync();c.traceCursor=next.index-1;c.syncPredictionUI();const count=counts().steps;
  await c.simStepButton.handlers.click();assert.equal(counts().steps,count);assert.equal(c.traceCursor,next.index-1);assert.match(c.predictionFeedback.textContent,/estado visible aún es el anterior/);
  const event={key:'ArrowRight',target:new Element(),preventDefault(){}};
  const prepare=c.ensureTraceForCurrentSelection;c.ensureTraceForCurrentSelection=()=>{throw new Error('Keyboard must not prepare or POST');};
  await listeners.keydown(event);assert.equal(counts().steps,count,'keyboard obeys the same unresolved condition gate');
  c.skipPrediction.handlers.click();assert.equal(c.traceCursor,next.index-1);assert.equal(c.conceptualProgress.attempts,0);assert.ok(c.predictionFeedback.textContent.includes(trace.steps[next.index].pedagogy.condition.substituted));
  await listeners.keydown(event);c.ensureTraceForCurrentSelection=prepare;assert.equal(counts().steps,count+1);assert.equal(c.traceCursor,next.index,'resolved condition permits exactly one manual step');
  c.tracePlayer.prev();assert.equal(c.traceCursor,next.index-1);c.predictionSelect.value=answer;c.checkPrediction.handlers.click();assert.equal(c.conceptualProgress.attempts,0,'backward/reveal cannot farm points');
  await c.simStepButton.handlers.click();assert.equal(counts().steps,count+2);assert.equal(c.traceCursor,next.index);
  const distinct=c.predictionController.sync();
  if (distinct) {
   assert.notEqual(distinct.index,next.index);assert.equal(distinct.scored,false,'resolving one target does not unlock another');
   let stepsBefore=counts().steps;
   while(c.traceCursor+1<distinct.index){await c.simStepButton.handlers.click();stepsBefore++;assert.equal(counts().steps,stepsBefore);}
   await c.simStepButton.handlers.click();assert.equal(counts().steps,stepsBefore);await listeners.keydown(event);assert.equal(counts().steps,stepsBefore);
   assert.match(c.predictionController.hint(),/^Pista 1:/,'new target resets hints');
   c.predictionSelect.value=String(trace.steps[distinct.index].pedagogy.condition.result);const old=c.traceCursor;c.checkPrediction.handlers.click();assert.equal(c.traceCursor,old);assert.equal(c.conceptualProgress.attempts,1);
   c.skipPrediction.handlers.click();c.checkPrediction.handlers.click();assert.equal(c.conceptualProgress.attempts,1);
  }
  const normal=counts().steps;c.practiceMode.checked=false;await c.simStepButton.handlers.click();assert.equal(counts().steps,normal+1,'normal next still advances once');
  assert.equal(counts().seeks,0);assert.equal(JSON.stringify(trace),before);assert.ok(nodes['hier-prediction-context'].textContent.includes('Insertar'));
 }
 console.log(`PASS ${decisions} real decisions in ABB/AVL/RN/heap: future targets, true/false, three distinct hints, immutable traces, one score and backward/manual/omit/reset no farming`);
 console.log('PASS real grade/omit handlers keep cursor, reveal recorded evidence, preserve metrics; click/ArrowRight block unresolved condition and permit one manual step after resolving');
})().catch(error=>{console.error(error);process.exitCode=1;});
