'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test');
const dir=process.argv[2]||'static/js/';
for(const [module,collector,next] of [['sequential','collectPrintfConsoleLines','refreshPrintfConsole'],['hierarchical','collectHierPrintfLines','refreshHierPrintfConsole'],['graph','collectGraphPrintfLines','refreshGraphPrintfConsole']]){
 const source=fs.readFileSync(dir==='static/js/'?`${dir}${module}.js`:`${dir}${module}_baseline.js`,'utf8');
 const context={window:{},document:{addEventListener(){}}};vm.createContext(context);vm.runInContext(source,context);
 const a=source.indexOf(`  function ${collector}(`),b=source.indexOf(`  function ${next}(`,a);vm.runInContext(source.slice(a,b),context);
 const collect=(trace,cursor)=>Array.from(context[collector](trace,cursor));
 test(`${module} snapshot at exact cursor, reverse/reset reproducible`,()=>{const t={console_mode:'snapshot',steps:[{console:[]},{console:['7\n']},{console:['7\n','7\n']},{console:['7\n','7\n']}]};assert.deepEqual(collect(t,3),['7\n','7\n']);assert.deepEqual(collect(t,1),['7\n']);assert.deepEqual(collect(t,0),[]);assert.deepEqual(collect(t,-1),[]);});
 test(`${module} event fragments never deduplicate or trim Unicode/blank lines`,()=>{const t={console_mode:'events',steps:[{console:['vacía\n']},{console:['vacía\n','\n',' áéñ ']},{console:[]}]};assert.deepEqual(collect(t,2),['vacía\n','vacía\n','\n',' áéñ ']);assert.deepEqual(collect(t,0),['vacía\n']);assert.deepEqual(collect(t,-1),[]);});
}
