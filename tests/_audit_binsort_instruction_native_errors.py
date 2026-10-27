"""Native Binsort wrapper ERROR events over the frozen verified Counting observer."""
from pathlib import Path
import sys,json,subprocess,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
import _audit_counting_native_low as base
from _audit_counting_error_native import CASES,simulated
from app import create_app
C=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';OUT=C/'evidence/visible-sorting-binsort-instructions/native-errors'
OLD=C/'evidence/visible-sorting-counting-error-instructions/native-errors'
def main():
 code=(OLD/'observed.c').read_text(encoding='utf-8').split('int main(void){')[0]
 source=(ROOT/'docs/tads_C/tad_ordenamiento.c').read_text(encoding='utf-8')
 wrapper=re.search(r'int ordenar_binsort\(int arreglo\[\], size_t n\)\s*\{\s*return ordenar_counting_sort\(arreglo, n\);\s*\}',source)
 assert wrapper,'canonical wrapper contract changed'
 observed=wrapper.group().replace('{','{emit("binsort_entry",-1);emit("binsort_delegate",-1);',1).replace('return ordenar_counting_sort(arreglo, n);','int observed_status=ordenar_counting_sort(arreglo, n);emit("binsort_return",-1);return observed_status;')
 body=[]
 for i,(name,(values,fault)) in enumerate(CASES.items()):
  row=base.c_case(values,i).replace('if(ordenar_counting_sort(a,count)!=ORDENAMIENTO_OK)return 2;','fail_reserve='+str(int(fault))+';if(ordenar_binsort(a,count)!=ORDENAMIENTO_ERROR)return 2;')
  body.append(row)
 exe=base.compile_source(OUT,code+observed+'int main(void){_Static_assert(sizeof(size_t)==8,"observed safe size_t64");'+''.join(body)+'return 0;}')
 native_run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert native_run.returncode==0,native_run.stderr
 (OUT/'native.jsonl').write_text(native_run.stdout,encoding='utf-8');events=[json.loads(x) for x in native_run.stdout.splitlines()];report=[]
 for i,(name,(values,fault)) in enumerate(CASES.items()):
  native=[x for x in events if x['case']==i];frozen=json.loads((OLD/(name+'.json')).read_text(encoding='utf-8'))
  assert [native[0],*native[3:-1]]==frozen['native']
  app=create_app();app.testing=True
  if fault:app.config['COUNTING_QA_ALLOCATOR']=simulated
  c=app.test_client();c.post('/api/ordenamiento/create-array',json={'values':values});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'})
  before=c.get('/api/ordenamiento/state').get_json();r=c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'step_by_step'});assert r.status_code==400
  d=r.get_json();t=d['execution_trace'];frames=t.get('steps')
  if frames is None:frames=sum((c.get(t['page_url'],query_string={'start':j,'limit':128}).get_json()['steps'] for j in range(0,t['step_count'],128)),[])
  assert len(frames)==len(native)
  for n,f in zip(native,frames):assert f['debug']['instruction_event']=={k:v for k,v in n.items() if k!='case'}
  assert d['history']==before['history'] and d['main_c']==before['main_c'] and d['visual_state']==before['visual_state']
  row=dict(case=name,input=values,events=len(native),status=0,simulated_calloc=fault,allocations=0,frees=0,live=0,full_native_HTTP_equal=True,delegated_events_equal_frozen=True)
  (OUT/(name+'.json')).write_text(json.dumps(dict(case=row,native=native,before=before,response=d),ensure_ascii=False,separators=(',',':')),encoding='utf-8');report.append(row)
 (OUT/'report.json').write_text(json.dumps(dict(rows=report,scope='New Binsort-context observations; same four error causes, not four additional semantic paths. No real memory exhaustion or 32-bit run.'),indent=2),encoding='utf-8')
 return report
if __name__=='__main__':print(json.dumps(main(),indent=2))
