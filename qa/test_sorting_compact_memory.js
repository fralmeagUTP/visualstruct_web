const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context=vm.createContext({window:{},document:{addEventListener(){}}});vm.runInContext(fs.readFileSync('static/js/sorting.js','utf8'),context);
const select=context.sCompactMemoryEntries;
const vars=['n','intervalo','i','temporal','j','unused','index','future'].map(name=>({name,value:2,changed:false}));
vars.at(-1).scope_state='not-entered';
function names(frame){return Array.from(select(frame),e=>e.item.name);}
let frame={source:{line_text:'arreglo[j] = arreglo[j - intervalo];'},variables:vars,pointers:[]};
assert.deepEqual(names(frame).slice(0,2),['intervalo','j']);assert.equal(names(frame).includes('future'),false);assert.ok(names(frame).length<=6);
frame.source.line_text='arreglo[j] = temporal;';assert.deepEqual(names(frame).slice(0,2),['temporal','j']);
frame.source.line_text='i++;';assert.equal(names(frame)[0],'i');
frame.source.line_text='index++;';assert.equal(names(frame)[0],'index');assert.notEqual(names(frame)[0],'i');
frame={source:{line_text:'*a = *b;'},variables:[...vars],pointers:[{name:'a',target:'A[1]'},{name:'b',target:'A[2]'},{name:'old',target:'dead',alive:false}]};
assert.ok(names(frame).includes('a'));assert.ok(names(frame).includes('b'));assert.equal(names(frame).includes('old'),false);assert.ok(names(frame).length<=6);
frame={source:{line_text:'x = y;'},variables:[{name:'x',initialized:false,changed:true},{name:'y',declared:false},{name:'z',scope_state:'ended'}]};
assert.deepEqual(names(frame),['x']);
console.log('PASS compact memory: Shell j/i/temporal, whole identifiers, active pointers, scope boundaries and six-item bound');
