"""Independent native frame, lexical lifetime and actual UI gates for Counting sort."""
from pathlib import Path
import json,hashlib
import pytest
from _audit_approved_source_supersessions import assert_historical_protected_hash
from _audit_counting_baseline import audit,CASES
from _audit_sorting_c_source import function_body
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-instructions';LOW=E.parent/'visible-sorting-counting-baseline-low'
@pytest.fixture(scope='module')
def full(tmp_path_factory):
    out=tmp_path_factory.mktemp('counting-full');audit(out);return out
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_native_instruction_scope_alias_before_source_and_memory(case,full):
    d=json.loads((audit_input_path(full/(case+'.json'))).read_text(encoding='utf-8'));source=d['response']['execution_trace']['source_code'];canonical=(audit_input_path(ROOT/'docs/tads_C/tad_ordenamiento.c')).read_text(encoding='utf-8')
    for function in ['ordenar_counting_sort','obtener_minimo_maximo','arreglo_valido']:assert function_body(canonical,function) in source
    declared=False;helper_declared=False;previous={};filled=written=consumed=0
    for idx,(s,c) in enumerate(zip(d['response']['execution_trace']['steps'],d['native'])):
        token=c['token'];p=s['pedagogy'];ctx=s['state_after']['counting_context'];v={(v['scope'],v['name']):v for v in p['variables']}
        assert s['debug']['instruction_event']=={key:value for key,value in c.items() if key!='case'}
        old=d['native'][max(0,idx-1)];assert s['state_snapshot']['items']==old['array'] and s['state_snapshot']['auxiliary_array']==old['conteo']
        assert s['state_after']['items']==c['array'] and s['state_after']['auxiliary_array']==c['conteo']
        assert (p['condition']['result'] if p['condition'] else None)==c['condition']
        assert s['line_text']==('' if token=='initial' else source.splitlines()[s['line_index']])
        if token!='initial':assert s['line_text'] in function_body(canonical,p['source']['function'])
        if token=='declare':declared=True
        if token=='helper_i_declare':helper_declared=True
        if token=='minmax_return':helper_declared=False
        if token=='sort_return':declared=False
        if declared:
            for name,key,ctype in [('minimo','minimo','int'),('maximo','maximo','int'),('rango','rango','size_t'),('i','i','size_t'),('indice','indice','size_t')]:
                var=v['ordenar_counting_sort',name];assert var['type']==ctype and var['value']==c[key] and var['initialized']==(c[key] is not None)
        else:assert not any(key[0]=='ordenar_counting_sort' and key[1] not in ('arreglo','n') for key in v)
        if helper_declared:assert v['obtener_minimo_maximo','i']['value']==c['helper_i'] and v['obtener_minimo_maximo','i']['initialized']==(c['helper_i'] is not None)
        calls=p['call_stack'];helper=[f for f in calls if f['function']=='obtener_minimo_maximo']
        if helper:
            assert helper[0]['parameters']==dict(arreglo='arreglo del caller',n=len(CASES[case]),minimo='&minimo (ordenar_counting_sort)',maximo='&maximo (ordenar_counting_sort)')
            for name in ['minimo','maximo']:
                alias=next(ptr for ptr in p['pointers'] if ptr['name']==name);assert alias['target']==f'&{name} (ordenar_counting_sort)' and alias['value']==(c[name] if c[name] is not None else 'sin inicializar')
        else:assert all(key[0]!='obtener_minimo_maximo' for key in v)
        assert any(ptr['name']=='conteo' for ptr in p['pointers'])==(c['conteo'] is not None)
        for key,var in v.items():
            oldvar=previous.get(key);assert var['previous']==(oldvar['value'] if oldvar else None);assert var['changed']==(oldvar is None or (oldvar['value'],oldvar['initialized'])!=(var['value'],var['initialized']))
        previous=v
        if token=='count_fill':filled+=1
        if token=='array_write':written+=1
        if token=='count_write':consumed+=1
        assert (ctx['filled'],ctx['written'],ctx['consumed'],ctx['pending_decrement'])==(filled,written,consumed,written-consumed)
        assert ctx['live']==(c['conteo'] is not None) and ctx['allocations']==c['allocations'] and ctx['frees']==c['frees']
        if ctx['live']:
            assert ctx['buckets']==[dict(index=k,value=c['minimo']+k,count=f) for k,f in enumerate(c['conteo'])]
            assert sum(c['conteo'])==filled-consumed
        else:assert not ctx['buckets']
        assert p['invariant']['holds']
        if token=='sort_return':assert not v and not calls
    assert len(d['native'])==len(d['response']['execution_trace']['steps'])

def test_native_zeroing_partial_write_decrement_ties_retirement_and_oracle_reuse(full):
    counts=dict(zero=0,partial=0,tie=0,freed=0,invalid_bucket=0)
    for case,values in CASES.items():
        d=json.loads((audit_input_path(full/(case+'.json'))).read_text(encoding='utf-8'));native=d['native']
        for idx,c in enumerate(native):
            token=c['token'];s=d['response']['execution_trace']['steps'][idx]
            if token=='count_init':counts['zero']+=1;assert c['conteo']==[0]*c['rango'] and c['array']==values
            if token=='array_write':
                counts['partial']+=1;before=native[idx-1];assert c['conteo']==before['conteo'] and c['indice']==before['indice']+1 and c['moves']==before['moves']+1
                after=native[idx+1];assert after['token']=='count_write' and after['array']==c['array'] and after['conteo'][c['i']]==c['conteo'][c['i']]-1 and after['moves']==c['moves']+1
            if token in ('min_compare','max_compare'):
                limit=c['minimo' if token=='min_compare' else 'maximo']
                if c['array'][c['helper_i']]==limit:counts['tie']+=1;assert c['condition'] is False
            if token=='bucket_test' and not c['condition']:counts['invalid_bucket']+=1;assert native[idx+1]['token']=='rebuild_increment'
            if token=='range_limit':assert c['condition'] is False and native[idx+1]['token']=='size_guard'
            if token=='count_free':counts['freed']+=1;assert c['conteo'] is None and all(x==0 for x in native[idx-1]['conteo']) and c['allocations']==c['frees']==1
    assert all(counts.values())
    for name in ['observed.c','native.jsonl']:assert (audit_input_path(full/name)).read_bytes()==(audit_input_path(LOW/'native-final'/name)).read_bytes()
    for name in ['tad_ordenamiento.c','tad_ordenamiento.h']:
        assert (audit_input_path(full/name)).read_bytes()==(audit_input_path(ROOT/'docs/tads_C'/name)).read_bytes()
        assert_historical_protected_hash(ROOT,'docs/tads_C/'+name,hashlib.sha256((audit_input_path(LOW/'native-final'/name)).read_bytes()).hexdigest())
@pytest.mark.parametrize('case',list(CASES))
def test_actual_full_browser_and_callers_with_native_calloc_fault(case):
    r=json.loads((audit_input_path(E/'browser-final-current/report.json')).read_text());row=next(x for x in r['rows'] if x['case']==case)
    assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['five_stages'] and row['reload_main_preserved'] and row['JSON_exact_cursor_state_main_preserved'] and row['typed_scopes_calloc_free_and_buckets_match_C']
    c=row['caller'];assert c['strict_C17'] and c['doxygen_warnings']==0 and c['allocations']==c['frees']==1 and c['live']==0 and c['successful_native_runs']==1
    assert c['first_allocation_failure']==dict(returncode=1,allocations=0,frees=0,live=0,no_success_array_after_failure=True)
    assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0

def test_original_IDs_and_eight_closed_modules_preserved_and_64bit_limit():
    original=json.loads((audit_input_path(E/'original-regressions.json')).read_text());assert hashlib.sha256((audit_input_path(ROOT/original['path'])).read_bytes()).hexdigest()==original['sha256']
    protected=json.loads((audit_input_path(LOW/'protected-closed-modules.json')).read_text());assert len(protected)==8
    for rel,sha in protected.items():assert hashlib.sha256((audit_input_path(ROOT/rel)).read_bytes()).hexdigest()==sha
    assert '_Static_assert(sizeof(size_t)==8' in (audit_input_path(ROOT/'tests/_audit_counting_limits.py')).read_text(encoding='utf-8-sig')


def test_outside_small_scope_keeps_existing_path_without_full_bucket_snapshot(monkeypatch):
    import app.domain.sorting.counting_instructions as module
    from app.domain.sorting.tad_ordenamiento import SortingInterpreter
    monkeypatch.setattr(module,'run_counting_trace',lambda *args:pytest.fail('full bucket snapshots outside authorized small scope'))
    for values in ([0,4],[3,1,2,0,1]):
        d=SortingInterpreter(list(values),'counting_sort').run()
        assert d['final_state']['items']==sorted(values) and d['metrics']['moves']==3*len(values) and d['metrics']['comparisons']==2*(len(values)-1)
        assert all('instruction_event' in s for s in d['steps'])
        assert d['steps'][-2]['instruction_event']['token']=='count_free' and d['steps'][-1]['instruction_event']['token']=='sort_return'
    called=[]
    def aggregate_probe(self):called.append(list(self.values));pytest.fail('aggregate fallback on admitted full Counting domain')
    monkeypatch.setattr(SortingInterpreter,'_run_counting_sort',aggregate_probe)
    d=SortingInterpreter([0,999999],'counting_sort').run()
    assert called==[] and d['final_state']['items']==[0,999999]
    assert d['metrics']['moves']==6 and d['metrics']['comparisons']==2
    steps=d['steps'];assert not isinstance(steps,list) and len(steps)>1000000
    assert 'instruction_event' in steps[0] and steps[-2]['instruction_event']['token']=='count_free' and steps[-1]['instruction_event']['token']=='sort_return'
