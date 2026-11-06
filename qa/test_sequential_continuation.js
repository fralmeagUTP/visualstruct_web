'use strict';
const fs=require('node:fs'),vm=require('node:vm'),test=require('node:test'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const source=fs.readFileSync('static/js/sequential.js','utf8');
for(const [name,provided,value,expected]of [['absent',false,undefined,'No registrada en esta instrucción.'],['null',true,null,'No registrada en esta instrucción.'],['destination',true,'retomar al llamador','retomar al llamador'],['zero',true,0,'0'],['false',true,false,'false'],['empty',true,'','']])test('continuation '+name+' is represented without inventing a C destination',()=>{
 const dom=new JSDOM('<div id="seq-call-view"></div>',{runScripts:'outside-only'}),w=dom.window,ctx=dom.getInternalVMContext();
 try{
  vm.runInContext(source,ctx);
  const call={function:'sublista_insertar_padre_final',parameters:{lista:'&sublista',valor_padre:7},locals:{}};if(provided)call.continuation=value;
  const frame={call_stack:[call]},before=JSON.stringify(frame);w.renderSequentialPedagogyFrame(frame,'intermediate');
  const row=w.document.querySelector('#seq-call-view tbody tr');assert.ok(row);assert.equal(row.children[3].textContent,expected);assert.equal(JSON.stringify(frame),before);
  assert.equal(row.children[0].textContent,'sublista_insertar_padre_final');
 }finally{w.close();}
});
