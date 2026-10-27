const fs=require('fs'),vm=require('vm'),assert=require('assert');
for(const [family,fn] of [['sorting','renderSortingConsole'],['sequential','renderPrintfConsole'],['hierarchical','renderHierPrintfConsole'],['graph','renderGraphPrintfConsole'],['hash','renderHashPrintfConsole']]){
 const ctx=vm.createContext({window:{},document:{addEventListener(){}}});vm.runInContext(fs.readFileSync(`static/js/${family}.js`,'utf8'),ctx);
 const node={dataset:{},style:{},innerHTML:'',textContent:''};ctx[fn](node,['7','3','7']);assert.strictEqual(node.dataset.consoleCopy,'7\n3\n7',family);
 ctx[fn](node,[]);assert.strictEqual(node.dataset.consoleCopy,'',family);
 if(family==='sequential'){ctx[fn](node,[],null,'á\n\n7 7\n');assert.strictEqual(node.dataset.consoleCopy,'á\n\n7 7\n');}
}
console.log('PASS five stdout-copy renderers: repeated lines separated, empty placeholder excluded, raw UTF8/blank/trailing newline preserved');
