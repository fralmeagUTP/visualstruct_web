'use strict';
const fs=require('node:fs'),vm=require('node:vm'),{JSDOM}=require('jsdom');
const trace=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const source=fs.readFileSync('static/js/sequential.js','utf8');
const dom=new JSDOM('<pre id="console"></pre>',{runScripts:'outside-only'}),w=dom.window,ctx=dom.getInternalVMContext();
try {
 vm.runInContext(source,ctx);
 const start=source.indexOf('  function collectPrintfConsoleLines('),end=source.indexOf('  const tracePlayer =',start);
 if(start<0||end<=start)throw Error('Missing actual stdout renderer');
 vm.runInContext(source.slice(start,end),ctx);
 w.printfConsole=w.document.getElementById('console');w.consoleState={trace,fallbackMessage:'(sin salida printf en esta ruta)',rawStdout:null};
 const rows=[];
 for(const cursor of [...Array(trace.steps.length+1).keys()].map(i=>i-1).concat([...Array(trace.steps.length+1).keys()].map(i=>trace.steps.length-1-i))){
  w.refreshPrintfConsole(cursor);rows.push({cursor,raw:w.printfConsole.dataset.consoleCopy,text:w.printfConsole.textContent});
 }
 process.stdout.write(JSON.stringify(rows));
}finally{w.close();}
