'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test');
const source=fs.readFileSync(process.argv[2]||'static/js/sequential.js','utf8');
function fixture(){const box={textContent:'',className:''};const context={window:{},document:{addEventListener(){},getElementById:id=>id==='message-box'?box:id==='seq-printf-console'?{}:null}};vm.createContext(context);vm.runInContext(source,context);return{context,box};}
for(const [name,message] of [['circular buscar_posiciones','El valor 7 está en las posiciones [1, 4].'],['sublist hijos_de','Hijos de 10: [3, 4].']]){
 test(`${name}: host result visible despite separate empty printf panel`,()=>{const f=fixture();f.context.showMessage(message,true);assert.equal(f.box.textContent,message);assert.equal(f.box.className,'message ok');});
 test(`${name}: prepared result hidden until final cursor and hidden again on rewind`,()=>{
  const f=fixture();const start=source.indexOf('        if (consoleState.resultMessage) {'),end=source.indexOf('        const step =',start);assert.ok(start>=0&&end>start,'cursor-based host result gate required');
  const code=source.slice(start,end);f.context.consoleState={resultMessage:{text:message,success:true}};f.context.traceTotalSteps=4;
  for(const cursor of [-1,0,2,3,1]){f.context.cursor=cursor;vm.runInContext(code,f.context);if(cursor===3)assert.equal(f.box.textContent,message);else{assert.match(f.box.textContent,/pendiente/);assert.doesNotMatch(f.box.textContent,/\[1, 4\]|\[3, 4\]/);}}
 });
}
