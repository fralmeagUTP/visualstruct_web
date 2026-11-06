'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const dom=new JSDOM(`<div id="${input.prefix}-pedagogy-summary"></div><section><h4>Variables C</h4><div id="${input.target}">Sin variables.</div></section>`,{runScripts:'outside-only'}),w=dom.window,ctx=dom.getInternalVMContext();
try{
 for(const f of ['static/js/contextual_help.js',input.prefix==='hier'?'static/js/hierarchical.js':'static/js/sequential.js'])vm.runInContext(fs.readFileSync(f,'utf8'),ctx);
 const variable=w.document.getElementById(input.target),section=variable.parentElement;
 w.ContextualHelp.operation(input.prefix,{id:input.family,operations:[{name:input.operation,label:input.operation}]},input.operation);
 assert.equal(section.hidden,true);assert.equal(section.id,'');assert.equal(variable.textContent,'Sin variables.');
 let frames=0;
 for(const frame of input.frames){
  if(input.prefix==='hier')w.renderHierPedagogy(frame,'intermediate');else w.renderSequentialPedagogyFrame(frame,'intermediate');
  assert.equal(section.hidden,false,'actual frame must restore the anonymous panel');
  assert.equal(variable.querySelectorAll('tbody tr').length,frame.variables.length);
  for(const item of frame.variables){assert.ok(variable.textContent.includes(item.name));assert.ok(variable.textContent.includes(item.type));}
  frames++;
 }
 w.ContextualHelp.frame(input.prefix,null,'intermediate');assert.equal(section.hidden,true,'return to operation introduction hides frame-only details again');
 process.stdout.write(JSON.stringify({frames,initialHidden:true,frameVisible:true,resetHidden:true}));
}finally{w.close();}
