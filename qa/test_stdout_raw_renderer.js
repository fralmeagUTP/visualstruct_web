'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test');
const source=fs.readFileSync(process.argv[2]||'static/js/sequential.js','utf8');
const fixtures=JSON.parse(fs.readFileSync('../qa_trazas/stdout_review/fixtures-all.json','utf8'));
function fixture(){
 const context={window:{},document:{addEventListener(){}}};vm.createContext(context);vm.runInContext(source,context);
 const start=source.indexOf('  function collectPrintfConsoleLines('),end=source.indexOf('  const tracePlayer =',start);assert.ok(start>=0&&end>start);vm.runInContext(source.slice(start,end),context);
 let text='',html='';const element={dataset:{},style:{},scrollHeight:0,scrollTop:0,set textContent(value){text=value;html=String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');},get textContent(){return text;},set innerHTML(value){html=value;text='';},get innerHTML(){return html;}};
 context.printfConsole=element;context.consoleState={trace:null,fallbackMessage:'host is not stdout',rawStdout:null};
 return{context,element};
}
test('private queue helper raw DOM text equals native bytes, not five block lines',()=>{
 const f=fixture(),trace=fixtures.find(x=>x.label==='private queue mostrar [7, 3, 7]').trace;
 f.context.consoleState.trace=trace;f.context.refreshPrintfConsole(trace.steps.length-1);
 const native=fs.readFileSync('../qa_trazas/stdout_review/native-queue-stdout-raw.bin');
 assert.deepEqual(Buffer.from(f.element.textContent,'utf8'),native);assert.doesNotMatch(f.element.innerHTML,/<div\b/);assert.equal(f.element.style.whiteSpace,'pre-wrap');
});
test('raw step/previous/start reflects exact current producer stdout, including duplicate values',()=>{
 for(const item of fixtures.filter(x=>x.label.startsWith('private ') && x.label.includes(' mostrar '))){
  const f=fixture();f.context.consoleState.trace=item.trace;
  for(let cursor=item.trace.steps.length-1;cursor>=-1;cursor--){
   f.context.refreshPrintfConsole(cursor);const expected=cursor<0?'':item.trace.steps[cursor].console.join('');
   assert.equal(f.element.textContent,expected,`${item.label} cursor ${cursor}`);assert.doesNotMatch(f.element.innerHTML,/<div\b/);
  }
 }
});
test('normal mode retains raw stdout after clearing player, line mode remains separate',()=>{
 const item=fixtures.find(x=>x.label==='private queue mostrar [7, 3, 7]'),f=fixture();
 f.context.data={execution_trace:item.trace};
 const statement=source.match(/consoleState\.rawStdout = collectPrintfStdout\([^;]+;/)?.[0];assert.ok(statement,'normal-mode producer stream transfer required');vm.runInContext(statement,f.context);
 f.context.refreshPrintfConsole(-1);assert.equal(f.element.textContent,'Cola: 7 3 7 \n');assert.doesNotMatch(f.element.innerHTML,/<div\b/);
 const lineTrace=fixtures.find(x=>x.label==='public linked mostrar [7, 3, 7]').trace;f.context.consoleState.trace=lineTrace;f.context.refreshPrintfConsole(lineTrace.steps.length-1);
 assert.equal((f.element.innerHTML.match(/class="console-line"/g)||[]).length,3);assert.match(f.element.innerHTML,/ 1\) 7/);assert.match(f.element.innerHTML,/ 2\) 3/);assert.match(f.element.innerHTML,/ 3\) 7/);
});
