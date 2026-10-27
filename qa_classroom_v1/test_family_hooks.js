const fs=require('fs'),vm=require('vm'),assert=require('assert');
const families=[['hierarchical','hier'],['sequential','seq'],['sorting','sorting'],['graph','graph'],['hash','hash']];
for(const [family,prefix] of families){
 const source=fs.readFileSync(`static/js/${family}.js`,'utf8');
 const nodes=new Map();
 const node=key=>nodes.get(key)||nodes.set(key,{id:key,dataset:{consoleCopy:'int x;\n'},classList:{add(){},remove(){}},parentElement:null,closest(){return this;},querySelector(){return null;},querySelectorAll(){return [];},before(other){this.beforeNode=other;},appendChild(other){(this.appended ||= []).push(other);},textContent:'int x;\n'}).get(key);
 const history=node(prefix==='sorting'?'sorting-action-history':'action-history');history.dataset.rawCode='#include <stdio.h>\n\nint main(void) { return 0; }\n';history.parentElement=node('history-panel');
 const record=node(prefix==='sorting'?'sorting-tad-record':'tad-record');record.parentElement=node('record-panel');
 let options;
 const context={window:{ClassroomView:{mount(o){options=o;}}},document:{getElementById:node,querySelector:node,addEventListener(){}}};
 vm.createContext(context);vm.runInContext(source,context);context[`${prefix}MountClassroomView`]();
 assert(options, family);assert.strictEqual(options.results.length,3);assert.strictEqual(options.results[1].getText(),history.dataset.rawCode);assert(!options.results[1].getText().includes('\u00a0'));
 history.dataset.rawCode='int main(void) { return 1; }\n';assert.strictEqual(options.results[1].getText(),history.dataset.rawCode,'copy reads latest render');
 assert.strictEqual(options.results[0].getText(),'int x;\n','stdout not normalized');
 if(family==='sequential'){assert.strictEqual(options.memory.length,0,'TAD nodes never hidden as auxiliary memory');assert.strictEqual(node('.sequential-primary-workspace').beforeNode,node('.sequential-learning-shell .seq-execute'),'same toolbar moved outside preparation, no clone');}
 if(family==='sorting')assert.deepStrictEqual(node('.sorting-execution-controls').appended,[node('sorting-sim-counter'),node('sorting-sim-status')],'same live counter/status move into sticky toolbar');
 assert(source.indexOf(`${prefix}MountClassroomView();`)>source.indexOf('DOMContentLoaded'));
}
console.log('PASS five family hooks, live raw getters, stdout fidelity, sequential TAD visibility');
