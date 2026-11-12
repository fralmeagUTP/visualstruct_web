"""Render actual book MST publication after the owned list has been freed."""
import json
import shutil
import subprocess
from pathlib import Path
import pytest

@pytest.mark.parametrize('operation,payload', [('run_prim', {'start': 1}), ('run_kruskal', {})])
def test_mst_publication_keeps_result_without_restoring_freed_memory(client, operation, payload):
    for op, values in [('create_graph', {'directed': False}),
                       ('insert_edge', {'origin': 1, 'target': 2, 'weight': 1}),
                       ('insert_edge', {'origin': 2, 'target': 3, 'weight': 2}),
                       ('insert_edge', {'origin': 1, 'target': 3, 'weight': 5}),
                       (operation, payload)]:
        response = client.post('/graph/graph/operate', json={
            'operation': op, 'payload': values, 'execution_mode': 'normal'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
    node = shutil.which('node')
    assert node, 'Node is required for actual JavaScript renderer regression'
    script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const c=vm.createContext({document:{addEventListener(){}},window:{}});
vm.runInContext(fs.readFileSync('static/js/graph_layout.js','utf8'),c);
c.gAdaptiveGraphPositions=c.window.gAdaptiveGraphPositions;
vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),c);
const data=JSON.parse(fs.readFileSync(0,'utf8'));
const trace=c.gExpandGraphInstructionTrace(data.execution_trace);
const final=trace.steps.at(-1), before=JSON.stringify(final);
assert.equal(final.debug.stage,'api_publication');
assert.equal(final.debug.graph_progress.edges.length,0); // owned list already released
assert.equal(final.state_after.last_result.result.total_weight,3);
const count=svg=>(svg.match(/class="viz-graph-edge mst"/g)||[]).length;
const render=step=>c.renderGraphSvg(step.state_after,null,step.debug);
assert.equal(count(c.renderGraphSvg(data.visual_state,null,null)),2);
assert.equal(count(render(final)),2); // normal finalOnly and playback terminal frame
assert.equal(JSON.stringify(final),before); // never mutate/resurrect memory
for (const step of trace.steps.slice(0,-1)) {
  const expected=c.getTraceDebugHighlights(step.debug).mstEdges;
  const edges=step.state_after.edges || [];
  const accepted=edges.filter(e=>expected.has(`${e.source}->${e.target}`)).length;
  assert.equal(count(render(step)),accepted); // no future result before publication
}
for (const stage of ['initial','write','free','scope_exit','caller_receipt']) {
  const debug={stage,graph_progress:{mode:'mst',nodes:[],edges:[]}};
  assert.equal(count(c.renderGraphSvg(data.visual_state,null,debug)),0);
}
const svg=render(final);
for (const edge of final.state_after.edges) {
  const path=svg.match(new RegExp(`<path data-graph-source="${edge.source}" data-graph-target="${edge.target}"[^>]+>`))[0];
  const chosen=final.state_after.last_result.result.mst_edges.some(([a,b])=>
    (String(a)===edge.source && String(b)===edge.target) || (String(b)===edge.source && String(a)===edge.target));
  assert.equal(path.includes('class="viz-graph-edge mst"'),chosen);
}
assert.equal(count(render(trace.steps.at(-2))),0); // reverse from publication clears result
assert.equal(count(render(final)),2); // forward again, same recorded execution
console.log('PASS actual MST publication, all earlier frames, reverse/forward, immutable memory');
'''
    result = subprocess.run([node, '-e', script], input=json.dumps(data), text=True,
                            capture_output=True, cwd=Path(__file__).resolve().parents[1])
    assert result.returncode == 0, result.stdout + result.stderr
