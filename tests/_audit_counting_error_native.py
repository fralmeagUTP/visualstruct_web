"""Causal native Counting ERROR oracles; isolated NULL allocator, never real OOM."""
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
import _audit_counting_native_low as base
from app import create_app
from app.domain.sorting.counting_sparse_instructions import SimulatedCountingAllocationFailure
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-error-instructions'
CASES={'range_two':([0,1000000],False),'range_eighty':([0]+[1000000]*79,False),'null_two':([5,0],True),'null_negative_duplicates':([-3,-5,-3,-5,-4],True)}
def simulated(_length):raise SimulatedCountingAllocationFailure('isolated QA NULL allocator equivalent')
def main():
    code=base.native_base()
    # Split JSON closing marker to expose the actual native return value only on ERROR.
    needle=',\\\"frees\\\":%d}\\n",comparisons,moves,allocs,frees);'
    assert needle in code
    code=code.replace(needle,',\\\"frees\\\":%d",comparisons,moves,allocs,frees);if(!strcmp(t,"error_return"))printf(",\\\"native_status\\\":%d",ORDENAMIENTO_ERROR);printf("}\\n");')
    pos=code.index('static int arreglo_valido')
    code=code[:pos]+'static int fail_reserve;static void* qa_calloc(size_t n,size_t s){return fail_reserve?NULL:calloc(n,s);}\nstatic int retire_error(void){iw=ih=ir=io=have_min=have_max=0;emit("error_return",-1);return ORDENAMIENTO_ERROR;}\n'+code[pos:]
    # Observation is inserted immediately before the actual return, not a synthetic sort.
    code=code.replace('return ORDENAMIENTO_ERROR;','return retire_error();')
    code=code.replace('emit("error_return",-1);return retire_error();','emit("error_return",-1);return ORDENAMIENTO_ERROR;')
    code=code.replace('conteo=(int*)calloc(rango,sizeof(int));','conteo=(int*)qa_calloc(rango,sizeof(int));')
    body=[]
    for i,(name,(values,fault)) in enumerate(CASES.items()):
        case=base.c_case(values,i).replace('if(ordenar_counting_sort(a,count)!=ORDENAMIENTO_OK)return 2;','fail_reserve='+str(int(fault))+';if(ordenar_counting_sort(a,count)!=ORDENAMIENTO_ERROR)return 2;')
        body.append(case)
    out=E/'native-errors';exe=base.compile_source(out,code+'int main(void){_Static_assert(sizeof(size_t)==8,"safe size_t64 observer");'+''.join(body)+'return 0;}')
    result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert result.returncode==0,result.stderr
    (out/'native.jsonl').write_text(result.stdout,encoding='utf-8');all_rows=[json.loads(x) for x in result.stdout.splitlines()];report=[]
    for i,(name,(values,fault)) in enumerate(CASES.items()):
        native=[x for x in all_rows if x['case']==i]
        app=create_app();app.testing=True
        if fault:app.config['COUNTING_QA_ALLOCATOR']=simulated
        c=app.test_client();c.post('/api/ordenamiento/create-array',json={'values':values});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'counting_sort'})
        before=c.get('/api/ordenamiento/state').get_json();response=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'});assert response.status_code==400
        data=response.get_json();trace=data['execution_trace'];frames=trace.get('steps')
        if frames is None:frames=c.get(trace['page_url'],query_string={'start':0,'limit':128}).get_json()['steps'] if len(native)<=128 else sum((c.get(trace['page_url'],query_string={'start':start,'limit':128}).get_json()['steps'] for start in range(0,len(native),128)),[])
        assert len(frames)==len(native)
        for index,(actual,frame) in enumerate(zip(native,frames)):
            assert frame['debug']['instruction_event']=={k:v for k,v in actual.items() if k!='case'},(name,index)
            assert frame['state_after']['items']==values
            assert frame['state_snapshot']['items']==values
            assert frame['state_after']['counting_context']['allocations']==frame['state_after']['counting_context']['frees']==0
            assert frame['line_text']==('' if frame['line_index'] is None else trace['source_code'].splitlines()[frame['line_index']])
        assert data['history']==before['history'] and data['main_c']==before['main_c'] and data['visual_state']==before['visual_state']
        assert not trace['success'] and not trace['mutates'] and trace['native_status']==0 and trace['error']['simulated']==fault and not trace['error']['real_c_execution']
        last=frames[-1];assert last['pedagogy']['concept']=='return' and not last['pedagogy']['variables'] and not last['pedagogy']['call_stack'] and not last['pedagogy']['pointers']
        assert 'return ORDENAMIENTO_ERROR' in last['line_text']
        guard=frames[-2];assert guard['pedagogy']['condition']['result'] is True
        if fault:
            ptr=next(v for v in guard['pedagogy']['variables'] if v['name']=='conteo');assert ptr['value']=='NULL' and ptr['initialized']
            assert frames[-3]['debug']['instruction_event']['token']=='count_init'
        else:assert not any(x['token']=='size_guard' for x in native)
        row=dict(case=name,input=values,events=len(native),simulated_calloc=fault,full_native_HTTP_equal=True,status=0,allocations=0,frees=0,live=0,accepted_unchanged=True)
        (out/(name+'.json')).write_text(json.dumps(dict(case=row,native=native,response=data,before=before),ensure_ascii=False,separators=(',',':')),encoding='utf-8');report.append(row)
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
if __name__=='__main__':print(json.dumps(main(),indent=2))
