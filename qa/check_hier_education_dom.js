'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const {extractRange}=require('./hier_prediction_harness');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const dom=new JSDOM(input.html,{url:'http://127.0.0.1:43210',runScripts:'outside-only',pretendToBeVisual:true}),w=dom.window,ctx=dom.getInternalVMContext();
try {
 const source=fs.readFileSync('static/js/hierarchical.js','utf8');
 vm.runInContext(source,ctx);vm.runInContext(fs.readFileSync('static/js/contextual_help.js','utf8'),ctx);
 const level=w.document.getElementById('hier-learning-level'),label=level.closest('label'),guides=['hier-level-contract','hier-level-guide'].map(id=>w.document.getElementById(id));
 level.value='advanced';let events=0;level.addEventListener('change',()=>events++);
 w.initHierSimplifiedWorkspace();
 assert.equal(w.document.querySelectorAll('#hier-learning-level').length,1);
 assert.equal(w.document.getElementById('hier-learning-level'),level);assert.equal(level.closest('label'),label);assert.equal(level.value,'advanced');assert.equal(level.closest('section').id,'hier-code-region');
 for(const node of guides){assert.equal(w.document.getElementById(node.id),node);assert.equal(node.closest('section').id,'hier-code-region');}
 for(const id of level.getAttribute('aria-describedby').split(/\s+/))assert.ok(w.document.getElementById(id));
 assert.equal(w.document.querySelector('label[for="hier-learning-level"]'),label);
 assert.equal(w.document.getElementById('hier-guided-example').closest('section').getAttribute('aria-labelledby'),'hier-prepare-title');
 assert.deepEqual([...w.document.querySelectorAll('h3')].map(n=>n.textContent.replace(/\s+/g,' ').trim()).filter(t=>/^[1-5] /.test(t)),['1 Preparar y controlar ejecución','2 Visualizar y ejecutar','3 Relacionar con código','4 Comprender','5 Resultados de ejecución']);
 let writes=0;Object.assign(w,{learningLevel:level,currentPedagogyFrame:input.frame,writePresentation(){writes++;}});
 // Bind the actual handler, not a rewritten version of its behavior.
 const line=source.split(/\r?\n/).find(s=>s.includes('learningLevel?.addEventListener("change"'));
 assert.ok(line,'actual level handler exists');new vm.Script(line);vm.runInContext(line,ctx);
 const initial=JSON.stringify(input.frame);
 for(const value of ['basic','intermediate','advanced']){
  level.value=value;level.dispatchEvent(new w.Event('change'));
  const summary=w.document.getElementById('hier-pedagogy-summary');
  assert.ok(summary.textContent.includes(input.frame.narration[value]),'complete real narration remains reachable in native details');
  assert.ok(w.document.getElementById('hier-level-guide').textContent.includes({basic:'Básico',intermediate:'Intermedio',advanced:'Avanzado'}[value]));
  for(const detail of summary.querySelectorAll('details')){detail.querySelector('summary').click();assert.equal(detail.open,true);}
 }
 assert.equal(writes,3);assert.equal(events,3);assert.equal(JSON.stringify(input.frame),initial);
 // Responsive tab changes move no nodes and do not reset the selected value.
 w.initHierResponsiveWorkspace();for(const tab of w.document.querySelectorAll('[data-hier-tab]')){tab.click();assert.equal(level.value,'advanced');assert.equal(w.document.getElementById('hier-learning-level'),level);}
 process.stdout.write(JSON.stringify({family:input.family,levels:3,singleControl:true,identity:true,ariaRelations:true,narrationRetained:true,tabsPreserveValue:true}));
}finally{w.close();}
