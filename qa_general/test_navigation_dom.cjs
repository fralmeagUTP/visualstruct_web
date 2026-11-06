/* DOM emulation only, no layout/browser proof. Uses actual rendered pages and scripts. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require(process.env.JSDOM_MODULE||'jsdom');
const root=path.resolve(__dirname,'..'),rows=JSON.parse(fs.readFileSync(path.join(__dirname,'navigation.json'))).pages;
(async()=>{let readers=0,links=0,tabs=0;
for(let i=0;i<rows.length;i++){
 const route=rows[i].route,errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(fs.readFileSync(path.join(__dirname,'tmp/navigation-dom',i+'.html'),'utf8'),{url:'https://example.invalid'+route,runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
 const w=dom.window,d=w.document;w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=()=>{};
 w.requestAnimationFrame=cb=>w.setTimeout(()=>cb(Date.now()),0);w.cancelAnimationFrame=id=>w.clearTimeout(id);
 w.fetch=async()=>{throw Error('unexpected fetch on page init')};
 for(const script of [...d.scripts])w.eval(script.src?fs.readFileSync(path.join(root,new URL(script.src).pathname),'utf8'):script.textContent);
 await new Promise(resolve=>w.setTimeout(resolve,30));assert.deepEqual(errors,[],route);
 for(const pre of d.querySelectorAll('pre.didactic-code,pre.didactic-history-main')){
  assert.equal(pre.dataset.cSyntax,'c',route+' syntax init');
  if(pre.dataset.rawCode!==undefined)assert.equal(w.ClassroomView.sourceText(pre),pre.dataset.rawCode,route+' literal copy');
  readers++;
 }
 for(const link of d.querySelectorAll('[data-book-function]')){
  link.click();const code=d.querySelector('#graph-canonical-code');
  assert(d.querySelector('#graph-canonical-source').open,route+' help source opens');
  assert(code.contains(d.activeElement),route+' keyboard focus moves to source');links++;
 }
 const tablist=d.querySelector('[role=tablist]');
 if(tablist){const ts=[...tablist.querySelectorAll('[role=tab]')];if(ts.length>1){
  ts[0].focus();ts[0].dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
  assert.equal(d.activeElement,ts[1],route+' tab key focus');assert.equal(ts[1].getAttribute('aria-selected'),'true');
  ts[1].dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));
  assert.equal(d.activeElement,ts[0],route+' left key focus');
  ts[0].dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));
  assert.equal(d.activeElement,ts.at(-1),route+' wrap key focus');
  tabs++;
 }}
 assert.deepEqual(errors,[],route+' interaction errors');dom.window.close();if(global.gc)global.gc();console.log('PASS DOM '+route);
}
console.log(`PASS ${rows.length} page DOM/script initializations, ${readers} C readers, ${links} graph help focus links, ${tabs} keyboard tab sets. No browser or layout claim.`);
})().catch(e=>{console.error(e);process.exitCode=1});
