const assert=require('node:assert/strict');
class Element {
 constructor(id=''){this.id=id;this.disabled=false;this.value='';this.textContent='';this.listeners={};this.members=new Map();this.attrs={};}
 set innerHTML(html){for(const [,id] of html.matchAll(/id="([^"]+)"/g))this.members.set(id,new Element(id));}
 querySelector(selector){return this.members.get(selector.slice(1));}
 contains(node){return node===this||[...this.members.values()].includes(node);}
 setAttribute(k,v){this.attrs[k]=v;}
 addEventListener(type,handler){this.listeners[type]=handler;}
 matches(){return this.id==='multiple-values';}
 closest(){return this;}
}
const external=[new Element('reset-button')], docListeners={};let panel;
global.document={createElement(){return new Element()},querySelectorAll(){return [...external,...(panel?[...panel.members.values()]:[])]},addEventListener(type,fn){docListeners[type]=fn}};
global.window={addEventListener(){},sessionStorage:{getItem(){return null}},location:{reload(){}}};
const api=require('../static/js/multiple_input.js');
let cursor=-1;const player={pause(){},hasTrace(){return false},getTotalSteps(){return 3},getCursor(){return cursor},isAtEnd(){return cursor===2},seek(i){cursor=i},reset(){cursor=-1},async step(){cursor++},prev(){cursor--},async play(){cursor=2}};
let resolve,calls=0;
const adapter={model:{id:'stack',visual_state:{}},form:{insertAdjacentElement(_,el){panel=el}},player,isBusy(){return false},select(){},sync(){},execute(){calls++;return new Promise(r=>resolve=r)}};
api.mount(adapter);const el=id=>panel.querySelector('#multiple-'+id);
(async()=>{
 api.stateChanged();assert.equal(el('status').textContent,'','individual use before first batch does not invent a prior batch');
 el('values').value='1,2';el('values').listeners.input();assert(!el('load').disabled);
 const start=el('step').listeners.click();assert(external[0].disabled);assert(el('load').disabled);
 // Simulate a function chooser rebuilt by the real unit renderer while locked.
 const newButton=new Element('dynamic-function');external.push(newButton);api.lockActiveControls();assert(newButton.disabled);
 let blocked=false;docListeners.click({target:external[0],preventDefault(){blocked=true},stopImmediatePropagation(){}});assert(blocked);
 resolve({success:true});await start;assert.equal(calls,1);assert(el('stop').disabled===false);
 el('stop').listeners.click();assert(!external[0].disabled);assert(!newButton.disabled);assert(el('load').disabled);
 await el('load').listeners.click();assert.equal(calls,1,'late second click cannot restart completed input');
 api.stateChanged();assert.match(el('status').textContent,/cambió/);assert(!el('load').disabled);
 el('values').value='1,';el('values').listeners.input();assert(el('load').disabled);assert.match(el('preview').textContent,/Posición 2/);
 console.log('PASS real mount guards external mutation, restores dynamically created controls, prevents late double start, invalidates summary after reset, validates edits');
})().catch(error=>{console.error(error);process.exitCode=1});
