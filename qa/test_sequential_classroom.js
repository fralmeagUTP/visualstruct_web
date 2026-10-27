const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes={}; const context=vm.createContext({window:{},document:{addEventListener(){},getElementById(id){return nodes[id] ||= {innerHTML:'',parentElement:{tagName:'SECTION'}};}}});
const source=fs.readFileSync('static/js/sequential.js','utf8');
vm.runInContext(fs.readFileSync('static/js/contextual_help.js','utf8'),context);vm.runInContext(source,context);
const cases=JSON.parse(fs.readFileSync('qa/sequential_ui_fixtures.json','utf8'));
for(const item of cases){for(const step of item.trace.steps){context.renderSequentialPedagogyFrame(step.pedagogy,'intermediate');const html=nodes['seq-pedagogy-summary'].innerHTML;assert.doesNotMatch(html,/>Call<|>Condition<|>Allocation<|>Link<|>Assignment</);assert.doesNotMatch(nodes['seq-heap-view'].innerHTML,/ · linked<| · temporary</);}}
const cleanup=cases[1].trace.steps.find(s=>s.pedagogy.cleanup_memory);context.renderSequentialPedagogyFrame(cleanup.pedagogy,'intermediate');assert.match(nodes['seq-heap-view'].innerHTML,/<details[^>]*><summary>Registro técnico completo/);assert.match(nodes['seq-heap-view'].innerHTML,/<pre>/);
for(const label of ['Call','Condition','Allocation','Link','Assignment'])assert.notEqual(context.window.ContextualHelp.phaseLabel({phase:{id:'generic',label}}),label);
const begin=source.indexOf('  function collectPrintfConsoleLines('),end=source.indexOf('  const tracePlayer =',begin);vm.runInContext(source.slice(begin,end),context);
for(const item of cases){const final=context.collectPrintfConsoleLines(item.trace,item.trace.steps.length-1);context.data={execution_trace:item.trace,message:item.message};context.consoleState={};const actual=source.match(/consoleState\.fallbackMessage = collectPrintfConsoleLines[^;]+;/)[0];vm.runInContext(actual,context);assert.equal(context.consoleState.fallbackMessage,Array.from(final).join('\n')||'(sin salida printf en esta ruta)');if(item.operation==='limpiar')assert.doesNotMatch(context.consoleState.fallbackMessage,/limpió correctamente/);if(item.operation==='desencolar')assert.match(context.consoleState.fallbackMessage,/Cola vacía/);}
assert.doesNotMatch(source,/innerHeight - top/);
const css=fs.readFileSync('static/css/contextual_help.css','utf8');assert.match(css,/height: clamp\(420px, 62vh, 570px\); min-height: 420px/);assert.match(css,/sequential-learning-shell #op-pseudocode \.code-line \{ width: auto/);
// A focused node changes only panel-local scroll, never the document.
let shown=null;context.window.CCodeNavigation={revealLine(panel,node){shown=node;}};
const frame=cases[0].trace.steps.find(s=>s.pedagogy.push_memory?.aux?.value)?.pedagogy.push_memory;
const active={dataset:{stackPushNode:frame.aux.value},classList:{add(name){assert.equal(name,'sim-active');}}};
context.renderStackPushState({},frame,{dataset:{},querySelectorAll(){return [active];}});assert.equal(shown,active);
console.log('PASS 23 real sequential frames; Spanish phases/heap; diagnostic disclosure; normal stdout equals final-step stdout; local active node and stable CSS contracts');

assert.equal(context.window.ContextualHelp.phaseLabel(cases[0].trace.steps[6].pedagogy), 'Actualizar un dato del nodo');
assert.equal(context.window.ContextualHelp.phaseLabel(cases[0].trace.steps[7].pedagogy), 'Actualizar un enlace');
console.log('PASS real push nro store distinguished from sgte link store');
// A call on a return line and a prototype must not become duplicate index entries.
const code={dataset:{rawCode:'int sublista_copiar_hijos(int x);\nint sublista_copiar_hijos(int x) {\n  return x;\n}\nint consulta(int x) {\n  return sublista_copiar_hijos(x);\n}'},classList:{toggle(){}},querySelectorAll(){return [];}};
nodes['op-pseudocode']=code;nodes['seq-function-list']={innerHTML:'',querySelectorAll(){return [];}};
context.document.querySelector=()=>null;
vm.runInContext(fs.readFileSync('static/js/c_code_navigation.js','utf8'),context);
context.enhanceSequentialCodeNavigation(5);
const index=nodes['seq-function-list'].innerHTML;
assert.equal((index.match(/>sublista_copiar_hijos<\/button>/g)||[]).length,1);
assert.equal((index.match(/>consulta<\/button>/g)||[]).length,1);
assert.match(index,/is-active[^>]*data-line="4"/);
assert.equal(context.window.ContextualHelp.phaseLabel({phase:{id:'invariant',label:'Invariant'},concept:'invariant',source:{line_text:'cola->cantidad--;'}}),'Actualizar la cantidad');
console.log('PASS function index deduplicates declarations/call sites; quantity decrement is not mislabeled invariant checking');
