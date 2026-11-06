"""Real stack-renderer rows and negatives for missing/old/wrong active frames."""
import copy
import json
import subprocess
from pathlib import Path
import pytest
from e2e_sorting_stack_contract import EMPTY_STACK, assert_sorting_stack
from test_remaining_audit_presentation_contract import ROOT

CALLS = [{'function':'ordenar_burbuja','parameters':{'n':5},'continuation':'Esperar a intercambiar.'}, {'function':'intercambiar','parameters':{'a':'A[0]','b':'A[1]'},'continuation':'Retornar.'}]


def test_real_sorting_stack_renderer_observation(tmp_path):
    script = r"""
const fs=require('fs'),vm=require('vm'),{JSDOM}=require('./qa/node_modules/jsdom');
const dom=new JSDOM('<ul id="sorting-call-stack"></ul>',{runScripts:'outside-only'});
try {
 const ctx=dom.getInternalVMContext(),w=dom.window;
 const source=fs.readFileSync('static/js/sorting.js','utf8');vm.runInContext(source,ctx);
 const start=source.indexOf('    const stack = Array.isArray(currentPedagogy.call_stack)'),end=source.indexOf('    const loop = currentPedagogy.loop;',start);
 if(start<0||end<start)throw Error('Production stack renderer missing');
 w.callStack=w.document.getElementById('sorting-call-stack');
 const observations=[];
 for(const calls of JSON.parse(fs.readFileSync(process.argv[1],'utf8'))){
  w.currentPedagogy={call_stack:calls};vm.runInContext('{'+source.slice(start,end)+'}',ctx);
  observations.push([...w.callStack.querySelectorAll(':scope > li')].map(row=>({function:row.querySelector('strong')?.textContent??null,text:row.textContent})));
 }
 process.stdout.write(JSON.stringify(observations));
}finally{dom.window.close();}
"""
    sequences=[[],CALLS[:1],CALLS,CALLS[:1],[],CALLS[:1],CALLS,[]]
    path=tmp_path/'calls.json';path.write_text(json.dumps(sequences))
    run=subprocess.run(['node','-e',script,str(path)],cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert run.returncode==0,run.stderr
    for rows,calls in zip(json.loads(run.stdout),sequences,strict=True):
        assert assert_sorting_stack(rows,calls)==bool(calls)


@pytest.mark.parametrize('corruption',['placeholder','missing','duplicate','wrong_function','wrong_parameters','wrong_continuation','stale_parent'])
def test_active_frame_cannot_be_replaced_by_placeholder_or_wrong_call(corruption):
    rows=[dict(function=c['function'],text=c['function']+'('+json.dumps(c['parameters'],separators=(',',':'))+')'+c['continuation']) for c in CALLS]
    if corruption=='placeholder': rows=[dict(function=None,text=EMPTY_STACK)]
    elif corruption=='missing': rows=[]
    elif corruption=='duplicate': rows.append(copy.deepcopy(rows[-1]))
    elif corruption=='wrong_function': rows[-1]['function']='ordenar_shell'
    elif corruption=='wrong_parameters': rows[-1]['text']=rows[-1]['text'].replace('A[0]','A[99]')
    elif corruption=='wrong_continuation': rows[-1]['text']=rows[-1]['text'].replace('Retornar.','Continuar otra instrucción.')
    else: rows=rows[:1]
    with pytest.raises(AssertionError): assert_sorting_stack(rows,CALLS)


def test_ended_scope_cannot_keep_active_rows():
    with pytest.raises(AssertionError): assert_sorting_stack([dict(function='intercambiar',text='intercambiar({})')],[])
