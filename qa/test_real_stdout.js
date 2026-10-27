'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test');
const base=process.argv[2]||'static/js/';
const file=name=>fs.readFileSync(base==='static/js/'?`${base}${name}.js`:`${base}${name}_baseline.js`,'utf8');
function extract(source,start,end){const a=source.indexOf(start),b=source.indexOf(end,a);assert.ok(a>=0&&b>a);return source.slice(a,b);}
function fixture(kind){
 const source=file(kind),hier=kind==='hierarchical';
 const code=hier?extract(source,'  function collectHierPrintfLines','  operations.forEach'):extract(source,'  function collectGraphPrintfLines','  function parseJsonArray');
 const consoleEl={dataset:{},textContent:'',innerHTML:'',style:{}},state={trace:null,fallbackMessage:''},page={modelId:'avl',consoleTrace:null,consoleFallbackMessage:''};
 const render=(element,lines,fallback)=>{element.textContent=lines.length?lines.join('\n'):fallback;};
 const push=(out,line)=>{if(String(line).trim()&&out.at(-1)!==line)out.push(line);};
 const context={consoleState:state,pageState:page,printfConsole:consoleEl,renderHierPrintfConsole:render,renderGraphPrintfConsole:render,hPushUniqueConsoleLine:push,gPushUniqueConsoleLine:push};vm.createContext(context);vm.runInContext(code,context);
 return{source,context,state,page,consoleEl,refresh:cursor=>context[hier?'refreshHierPrintfConsole':'refreshGraphPrintfConsole'](cursor)};
}
for(const kind of ['hierarchical','graph'])test(`${kind}: host feedback never assigned as C console fallback`,()=>{
 const source=file(kind);assert.doesNotMatch(source,/(?:consoleFallbackMessage|fallbackMessage)\s*=\s*data\.message/);
});
test('hierarchical fast path retains executed trace and uses final cursor',()=>{
 const f=fixture('hierarchical');const begin=f.source.indexOf('      } else {',f.source.indexOf('const deferQueryResult'));
 const end=f.source.indexOf('        if (!finalOnly)',begin);let code=f.source.slice(begin,end).replace(/^\s*\} else \{/,'');
 const trace={steps:[{console:[]},{console:['C actually printed this']}]};f.context.data={message:'API inserted successfully',execution_trace:trace};f.context.finalOnly=true;
 vm.runInContext(code,f.context);assert.equal(f.state.trace,trace);assert.equal(f.consoleEl.textContent,'C actually printed this');
});
for(const kind of ['hierarchical','graph'])test(`${kind}: non-printing executed path stays empty, query stdout retained exactly`,()=>{
 const f=fixture(kind),hier=kind==='hierarchical';
 const use=trace=>{if(hier)f.state.trace=trace;else f.page.consoleTrace=trace;};
 const memory={console_stdout:'',abb_read_model:true};const step={state_snapshot:{console_stdout:''},pedagogy:{memory_state:memory},console:[]};use({steps:[step]});f.refresh(0);
 assert.ok(f.consoleEl.textContent===''||f.consoleEl.textContent==='(sin salida printf en esta ruta)');
 memory.console_stdout='1 2 3\n';f.refresh(0);assert.equal(f.consoleEl.textContent,'1 2 3\n');
 f.refresh(-1);assert.ok(f.consoleEl.textContent===''||f.consoleEl.textContent==='(sin salida printf en esta ruta)');
});
test('graph create normal path retains actual trace and final cursor',()=>{
 const f=fixture('graph');const begin=f.source.indexOf('    } else {',f.source.indexOf('const data = await executeGraphOperation(controls, "create_graph"'));
 const end=f.source.indexOf('    const createSubroutine',begin);let code=f.source.slice(begin,end).replace(/^\s*\} else \{/,'').replace(/\}\s*$/,'');
 const trace={steps:[{console:['C created output']}]};f.context.data={message:'API graph created',execution_trace:trace};vm.runInContext(code,f.context);
 assert.equal(f.page.consoleTrace,trace);assert.equal(f.consoleEl.textContent,'C created output');
});
