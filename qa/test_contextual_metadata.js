const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes=new Map();for(const prefix of ['seq','hier','graph','hash'])nodes.set(`${prefix}-pedagogy-summary`,{innerHTML:''});
const window={};vm.runInNewContext(fs.readFileSync('static/js/contextual_help.js','utf8'),{window,document:{getElementById:id=>nodes.get(id)}});
const fixtures=JSON.parse(fs.readFileSync('qa/contextual_metadata_fixtures.json','utf8'));let count=0;
for(const item of fixtures){assert.ok(item.frames.length>1);for(const frame of item.frames){const before=JSON.stringify(frame);window.ContextualHelp.frame(item.prefix,frame,'intermediate');const html=nodes.get(`${item.prefix}-pedagogy-summary`).innerHTML,primary=html.split('<details')[0];assert.doesNotMatch(primary,/\b\w+_model\b|heap_nodes|local_pointer_names|node_ids|\[object Object\]/,`${item.structure}/${item.operation}/${frame.source?.line_text}`);assert.equal(JSON.stringify(frame),before);count++;}}
for(const op of ['insertar_inicio','insertar_final']){const item=fixtures.find(f=>f.operation===op),frame=item.frames.at(-1);window.ContextualHelp.frame('seq',frame,'intermediate');const html=nodes.get('seq-pedagogy-summary').innerHTML;assert.match(html.split('<details')[0],/Termina el ámbito.*Estado de la estructura/);assert.doesNotMatch(html.split('<details')[0],/head:.*sin valor|lista:.*sin valor/);assert.match(html,/<details/);assert.match(html,/insert_model/);}
// Never blacklist genuine C identifiers, even names resembling model metadata.
window.ContextualHelp.frame('seq',{source:{line_text:'head = head->sgte;'},variables:[{name:'head',previous:'N1',value:'N2',changed:true},{name:'search_model',previous:true,value:null,changed:true}],narration:{intermediate:'heap_nodes, search_model'}},'intermediate');
let html=nodes.get('seq-pedagogy-summary').innerHTML.split('<details')[0];assert.match(html,/head: N1 → N2/);assert.doesNotMatch(html,/search_model/);
window.ContextualHelp.frame('graph',{source:{line_text:'vertex_ids = salida;'},variables:[{name:'vertex_ids',previous:1,value:2,changed:true}]},'intermediate');assert.match(nodes.get('graph-pedagogy-summary').innerHTML,/vertex_ids: 1 → 2/);
console.log(`PASS ${count} real frames across sequential, hierarchical, graph and hash; intermediate/final views; genuine C names retained; raw diagnostics and source data preserved`);

for(const variables of [[{name:'vertex_ids',type:'Tlista',value:'N2'}],{vertex_ids:{type:'Tlista',value:'N2'}}]){
 const frame={source:{line_text:'i++;'},scopes:[{variables}],variables:[{name:'vertex_ids',previous:'N1',value:'N2',changed:true},{name:'search_model',previous:true,value:false,changed:true}]};
 const before=JSON.stringify(frame);window.ContextualHelp.frame('graph',frame,'intermediate');const primary=nodes.get('graph-pedagogy-summary').innerHTML.split('<details')[0];
 assert.match(primary,/vertex_ids: N1 → N2/);assert.doesNotMatch(primary,/search_model/);assert.equal(JSON.stringify(frame),before);
}
console.log('PASS dictionary and array scope schemas preserve declared identifiers without modifying frames');
