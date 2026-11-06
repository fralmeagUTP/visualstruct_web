/* Actual player + rendering dispatch in a DOM. No layout/browser claim. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm');
const {JSDOM}=require('jsdom');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const source=fs.readFileSync('static/js/sequential.js','utf8');
const dom=new JSDOM('<div id="visual-state"></div>',{runScripts:'outside-only'});
const w=dom.window,context=dom.getInternalVMContext();w.structuredClone=structuredClone;
try {
  vm.runInContext(source,context);
  vm.runInContext(fs.readFileSync('static/js/interpreter_runtime.js','utf8'),context);
  const start=source.indexOf('  function renderCurrentVisual('),end=source.indexOf('  let playbackSpeed',start);
  vm.runInContext(source.slice(start,end),context);
  const callbackStart=source.indexOf('      renderState: (stateSnapshot, stepMeta) => {');
  const callbackEnd=source.indexOf('      onCursorChange:',callbackStart);
  vm.runInContext('captureRender = '+source.slice(callbackStart,callbackEnd).trim().replace(/^renderState: /,'').replace(/,$/,'')+';',context);
  vm.runInContext('('+input.observer+')()',context);
  w.lastVisualRender={};w.visualContainer=w.document.getElementById('visual-state');
  const rows=[];
  for(const row of input.traces) for(const view of ['current','linked']) {
    w.model={id:row.family};w.visualContainer.dataset.stackVisualMode=view;
    const player=w.InterpreterRuntime.createTracePlayer({codeElement:null,renderState:w.captureRender});
    player.loadTrace(row.trace);
    const record=cursor=>{player.seek(cursor);
      const prefix=row.op==='encolar'?'priority-enqueue':'priority-dequeue';
      const roots=row.family==='priority_queue'?['front','rear'].map(edge=>{
        const nodes=[...w.visualContainer.querySelectorAll(`[data-${prefix}-${edge}]`)];
        return {edge,count:nodes.length,value:nodes[0]?.getAttribute(`data-${prefix}-${edge}`),text:nodes[0]?.textContent};
      }):[];
      rows.push({family:row.family,op:row.op,view,cursor,event:structuredClone(w.auditRenderEvent),roots});
    };
    for(let cursor=-1;cursor<row.trace.steps.length;cursor++)record(cursor);
    for(let cursor=row.trace.steps.length-2;cursor>=-1;cursor--)record(cursor);
  }
  process.stdout.write(JSON.stringify(rows));
} finally {w.close();}
