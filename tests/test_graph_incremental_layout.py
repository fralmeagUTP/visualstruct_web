"""Presentation-only growth: retain the mental map without a size-triggered ring."""
from pathlib import Path
import subprocess
import shutil
import pytest

CASES = {
    'growth_22': r'''
let nodes=[], edges=[], old=new Map();
for(let i=1;i<=22;i++){
 nodes.push({id:String(i)});if(i>1)edges.push({source:String(i-1),target:String(i)});
 const p=layout(nodes,edges);
 for(const [id,q] of old)assert.deepStrictEqual(p.get(id),q,'existing vertex moved on insertion '+i);
 for(const q of p.values())assert(Number.isFinite(q.x)&&Number.isFinite(q.y));
 old=p;
}
assert.strictEqual(old.size,22);
''',
    'threshold_15_16': r'''
const nodes=Array.from({length:15},(_,i)=>({id:String(i+1)}));
const edges=nodes.map((n,i)=>({source:n.id,target:String((i+1)%15+1)}));
const before=layout(nodes,edges);
nodes.push({id:'16'});edges.push({source:'15',target:'16'});
const after=layout(nodes,edges);
for(const [id,q] of before)assert.deepStrictEqual(after.get(id),q);
assert.strictEqual(after.size,16);
''',
    'edge_local_adjustment': r'''
const nodes=[{id:'1'},{id:'2'},{id:'3'}];
const before=layout(nodes,[]),after=layout(nodes,[{source:'1',target:'3'}]);
assert.deepStrictEqual(after.get('2'),before.get('2'));
for(const id of ['1','3'])assert(Math.hypot(after.get(id).x-before.get(id).x,after.get(id).y-before.get(id).y)<=24.000001);
assert([...after.values()].every(q=>Number.isFinite(q.x)&&Number.isFinite(q.y)));
''',
    'replay_and_metadata': r'''
const nodes=[{id:'a'},{id:'b'},{id:'c'}], edges=[{source:'a',target:'b',weight:1}];
const pristine=JSON.stringify([nodes,edges]), before=layout(nodes,edges);
layout(nodes,[...edges,{source:'b',target:'c'}]);
const back=layout([...nodes].reverse(),[{source:'b',target:'a',weight:99},{source:'a',target:'a',weight:2}],{replay:true});
assert.deepStrictEqual([...back],[...before]);assert.strictEqual(JSON.stringify([nodes,edges]),pristine);
const again=layout(nodes,edges);assert.deepStrictEqual([...again],[...before]);
''',
    'cold_30_without_ring_or_overlap': r'''
const nodes=Array.from({length:30},(_,i)=>({id:String(i+1)}));
const edges=nodes.map((n,i)=>({source:n.id,target:String((i+1)%30+1)}));
const p=[...layout(nodes,edges).values()];
assert.strictEqual(p.length,30);
for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)assert(Math.hypot(p[i].x-p[j].x,p[i].y-p[j].y)>=99.999);
const center={x:p.reduce((v,q)=>v+q.x,0)/30,y:p.reduce((v,q)=>v+q.y,0)/30};
const radii=p.map(q=>Math.hypot(q.x-center.x,q.y-center.y));assert(Math.max(...radii)-Math.min(...radii)>30,'must not force a ring');
''',
    'editing_does_not_restore_stale_topology': r'''
const nodes=[{id:'1'},{id:'2'},{id:'3'}], a=[{source:'1',target:'3'}], b=[{source:'1',target:'2'}];
const initial=layout(nodes,[]);
const first=layout(nodes,a);layout(nodes,[...a,...b]);
layout(nodes,b);layout(nodes,[...b,{source:'2',target:'3'}]);
const removed=layout(nodes,b);layout.beginExecution();
const reinserted=layout(nodes,[...a,...b],{replay:true});
assert.deepStrictEqual(reinserted.get('2'),removed.get('2'),'unrelated vertex must stay anchored');
for(const id of ['1','3'])assert(Math.hypot(reinserted.get(id).x-removed.get(id).x,reinserted.get(id).y-removed.get(id).y)<=24.000001);
const playback=layout(nodes,b,{replay:true});assert.deepStrictEqual([...playback],[...removed]);
assert.deepStrictEqual([...layout(nodes,[...a,...b],{replay:true})],[...reinserted]);
''',
    'empty_renderer_replay_preserves_previous_snapshot': r'''
const fs=require('fs'),vm=require('vm');
const context=vm.createContext({document:{addEventListener(){}},window:{},gAdaptiveGraphPositions:layout});
vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),context);
layout([{id:'1'},{id:'2'}],[]);
const singleton=[{id:'2'}],before=layout(singleton,[],{replay:true});
assert.notStrictEqual(before.get('2').x,70,'fixture requires an inherited position');
layout.beginExecution();
assert(context.renderGraphSvg({nodes:[],edges:[]},null,null,true).includes('Grafo vacío'));
assert.deepStrictEqual([...layout(singleton,[],{replay:true})],[...before]);
context.renderGraphSvg({nodes:[],edges:[]},null,{stage:'api_publication'});
assert.deepStrictEqual([...layout(singleton,[],{replay:true})],[...before]);
context.renderGraphSvg({nodes:[],edges:[]},null,null,false);
assert.strictEqual(layout(singleton,[]).get('2').x,70,'a real clear must start a new map');
''',
    'clear_resets_history': r'''
const nodes=[{id:'1'},{id:'2'}],edges=[{source:'1',target:'2'}];
const before=layout(nodes,edges);layout([...nodes,{id:'3'}],edges);assert.strictEqual(layout([],[]).size,0);
const after=layout(nodes,edges);assert.deepStrictEqual([...after],[...before]);
''',
}

@pytest.mark.parametrize('case', CASES)
def test_incremental_graph_layout(case):
    node = shutil.which('node')
    assert node, 'Node is required for the real graph layout contract'
    root = Path(__file__).resolve().parents[1]
    script = "const assert=require('assert');const {gAdaptiveGraphPositions:layout}=require('./static/js/graph_layout.js');\n" + CASES[case]
    subprocess.run([node, '-e', script], cwd=root, check=True, timeout=25, capture_output=True, text=True)
