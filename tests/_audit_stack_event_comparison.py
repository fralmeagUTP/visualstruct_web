"""Compare existing native stack effects with private backend trace projections."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def values(nodes,head):
    output=[];seen=set()
    while head:
        assert head not in seen and head in nodes;seen.add(head)
        node=nodes[head];assert node['value_known'] and node['next_known']
        output.append(node['value']);head=node['next']
    return output

def actual_heap(step):
    debug=step.get('debug') or {}
    if 'heap' in debug:return debug['heap'],'debug.heap'
    pedagogy=step.get('pedagogy') or {}
    if 'heap_objects' in pedagogy:return pedagogy['heap_objects'],'pedagogy.heap_objects (may be logical-only)'
    return None,'missing'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',required=True);parser.add_argument('--native-name',default='stack-native-pilot-final');parser.add_argument('--backend-name',default='stack-backend-event-cases');parser.add_argument('--report-name',default='stack-native-backend-comparison.json');args=parser.parse_args();base=Path(args.evidence_dir)
    native_dir=base/args.native_name;native_report=json.loads((native_dir/'report.json').read_text(encoding='utf-8'))
    source=(ROOT/'docs/tads_C/tad_pila.c').read_bytes();assert hashlib.sha256(source).hexdigest()==native_report['source_sha256'];lines=source.decode('utf-8-sig').splitlines()
    events=[json.loads(line) for line in (native_dir/'nominal.events.jsonl').read_bytes().splitlines()]
    cases={i:json.loads((base/args.backend_name/f'{i}-{op}.json').read_text(encoding='utf-8')) for i,op in [(1,'apilar'),(2,'apilar'),(3,'desapilar'),(4,'limpiar')]}
    nodes={};head=0;push=1;checks=[];issues=[];recovered=[]
    for event in events:
        kind=event.get('event')
        if event.get('phase')!='after' or kind not in {'allocation','value_assignment','link_assignment','head_assignment','free'}:continue
        identifier=event['id']
        if kind=='allocation':nodes[identifier]={'value_known':False,'next_known':False}
        elif kind=='value_assignment':nodes[identifier].update(value=event['value'],value_known=True)
        elif kind=='link_assignment':nodes[identifier].update(next=event['next'],next_known=True)
        elif kind=='head_assignment':head=event['head']
        elif kind=='free':del nodes[identifier]
        fn=event['function'];case_id=push if fn=='pila_apilar' else 3 if fn=='pila_desapilar' else 4
        source_line=event['line']
        if kind in {'allocation','free'}:
            start=next(i for i,text in enumerate(lines) if text.startswith(('void '+fn+'(', 'int '+fn+'(')))
            end=next((i for i in range(start+1,len(lines)) if lines[i]=='}'),len(lines))
            token='malloc(' if kind=='allocation' else 'free(aux);'
            anchors=[i+1 for i in range(start,end) if token in lines[i]]
            assert len(anchors)==1,(fn,token,anchors)
            source_line=anchors[0]
            if source_line!=event['line']:
                recovered.append({'native_sequence':event['sequence'],'raw_recorded_line':event['line'],'canonical_line':source_line,'method':'unique function/call anchor against identical canonical C hash; no C reexecution'})
        line=lines[source_line-1].strip();steps=cases[case_id]['execution_trace']['steps'];candidates=[s for s in steps if s['line_text'].strip()==line]
        if kind=='allocation':candidates.sort(key=lambda s:s.get('event_type')!='allocator_success_return')
        assert candidates,(case_id,line)
        step=candidates[0];state=step.get('state_after');assert isinstance(state,dict) and isinstance(state.get('items'),list)
        actual=[x['value'] if isinstance(x,dict) else x for x in state['items']];expected=values(nodes,head)
        heap,heap_source=actual_heap(step)
        actual_live=None if heap is None else sum(obj.get('alive',True) and obj.get('allocated',True) and not obj.get('freed',False) for obj in heap)
        check={'case':case_id,'native_sequence':event['sequence'],'event':kind,'c_function':fn,'c_line':source_line,'raw_native_line':event['line'],'line_text':line,'backend_step':step['step_index'],'native_values':expected,'backend_values':actual,'logical_projection_match':expected==actual,'native_heap_live':len(nodes),'backend_heap_live':actual_live,'heap_source':heap_source,'heap_projection_match':actual_live==len(nodes)}
        checks.append(check)
        if expected!=actual:issues.append({'kind':'LOGICAL_STATE_DIVERGENCE',**check})
        if actual_live!=len(nodes):issues.append({'kind':'HEAP_WITNESS_NOT_EQUIVALENT','scope':'strict full-live heap; logical-only abstraction does not certify physical lifecycle',**check})
        if fn=='pila_apilar' and kind=='head_assignment':push+=1
    for step in cases[3]['execution_trace']['steps']:
        if step['line_text'].strip() not in ['*p = aux->sgte;','free(aux);']:continue
        pointer=next((x for x in step.get('pedagogy',{}).get('pointers',[]) if x.get('name')=='p'),None)
        if pointer:
            type_name=pointer.get('type','');depth=type_name.count('*')+(1 if 'ptrPila' in type_name else 0)
            if depth!=2:issues.append({'kind':'BORROWED_PARAMETER_DEPTH_MISMATCH','case':3,'line_text':step['line_text'].strip(),'canonical_declaration':'int pila_desapilar(ptrPila *p)','canonical_pointer_depth':2,'backend_pointer_type':type_name,'backend_pointer_depth':depth,'backend_target':pointer.get('target'),'logical_result_unchanged':True})
    result={'schema':'native-backend-stack-projection-comparison/v1','existing_native_program_reexecuted':False,'source_sha256':native_report['source_sha256'],'after_effects_compared':len(checks),'logical_projection_matches':sum(x['logical_projection_match'] for x in checks),'heap_projection_matches':sum(x['heap_projection_match'] for x in checks),'checks':checks,'issues':issues,'observer_macro_locations_recovered':recovered,'observer_location_repair_still_required':bool(recovered),'full_fidelity_closed':False,'scope':'after-effects/root values and declared heap counts; no UI frame-by-frame, complete alias bijection, malloc-fault API or all families certified'}
    (base/args.report_name).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['after_effects_compared','logical_projection_matches','heap_projection_matches','full_fidelity_closed']}));print(json.dumps(issues,ensure_ascii=True))
if __name__=='__main__':main()
