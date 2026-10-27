'use strict';
const fs=require('node:fs'),vm=require('node:vm'),test=require('node:test'),assert=require('node:assert/strict');
const source=fs.readFileSync('static/js/classroom_view.js','utf8');
const old=fs.readFileSync('qa_classroom_v1/test_shared_controller.js','utf8');
const context={source,vm}; vm.createContext(context);
vm.runInContext(old.slice(old.indexOf('function fixture(){'),old.indexOf("test('mount starts"))+';this.fixture=fixture;',context);
test('current C reader is keyboard-focusable and locally marked without touching bytes',()=>{
 const f=context.fixture(),code=new f.Node('pre'),parent=new f.Node();parent.append(code);f.root.append(parent);
 const text='  int long_name;\n\n';code.textContent=text;f.api.mount({...f,code});
 assert.ok(code.classList.contains('classroom-code-scroll'));assert.equal(code.attrs.tabindex,'0');assert.equal(code.textContent,text);
});
test('closing enlarged code restores both local axes and page, on same node',()=>{
 const f=context.fixture(),panel=new f.Node('pre');f.root.append(panel);panel.scrollLeft=173;panel.scrollTop=93;f.api.enlarge(panel,'Código C');
 panel.scrollLeft=8;panel.scrollTop=2;f.document.body.children[0].close();assert.equal(panel.scrollLeft,173);assert.equal(panel.scrollTop,93);assert.equal(JSON.stringify(f.window.restored),'[10,120]');
});
test('C viewport contract is no-wrap, intrinsic lines, bounded width and visible scrollbars',()=>{
 const css=fs.readFileSync('static/css/classroom_view.css','utf8');
 const contract=css.slice(css.indexOf('/* C readers share'));
 for(const rule of ['overflow-x: auto !important','overflow-y: auto !important','white-space: pre !important','max-width: 100% !important','min-width: 0 !important','width: max-content !important','scrollbar-width: auto'])assert.ok(contract.includes(rule),rule);
 assert.ok(!/scrollIntoView/.test(source));assert.ok(source.includes('copyLabel !== "Copiar salida"'));
});

test('opening enlarged code reapplies pan after native dialog reflow',()=>{
 const f=context.fixture(),panel=new f.Node('pre');f.root.append(panel);panel.scrollLeft=173;panel.scrollTop=93;
 f.Node.prototype.showModal=function(){this.open=true;panel.scrollLeft=0;panel.scrollTop=0;};
 f.api.enlarge(panel,'Código C');assert.equal(panel.scrollLeft,173);assert.equal(panel.scrollTop,93);
});
test('active-line reveal changes local vertical only, never selected horizontal pan',()=>{
 const ctx={window:{}};vm.createContext(ctx);vm.runInContext(fs.readFileSync('static/js/c_code_navigation.js','utf8'),ctx);
 const panel={scrollLeft:317,scrollTop:10,clientHeight:100,clientTop:1,getBoundingClientRect:()=>({top:20})};
 ctx.window.CCodeNavigation.revealLine(panel,{getBoundingClientRect:()=>({top:170,bottom:190,left:900,right:1200})});
 assert.equal(panel.scrollLeft,317);assert.equal(panel.scrollTop,79);
 ctx.window.CCodeNavigation.revealLine(panel,{getBoundingClientRect:()=>({top:0,bottom:20,left:-900,right:-700})});
 assert.equal(panel.scrollLeft,317);assert.equal(panel.scrollTop,58);
});
