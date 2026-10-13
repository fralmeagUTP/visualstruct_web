"""Binsort wrapper C baseline; frozen Counting bodies reused when input matches."""
from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
import _audit_counting_native_low as native
from app import create_app
C=ROOT/'openspec/changes/audit-local-quality-and-unified-controls'
E=C/'evidence/visible-sorting-binsort-baseline-low'
CASES={'single':[7],'normal':[3,1,2],'negative_duplicates':[-3,-5,-3,-4],'outside_five':[5,4,3,2,1],'range_six':[0,5],'eighty_equal':[2]*80,'near_min':[-2147483643,-2147483648],'range_thousand':[0,1000]}
REUSE={'single':C/'evidence/visible-sorting-counting-baseline-low/native-final/single.json'}
for name,old in [('outside_five','n5_k5'),('range_six','n2_k6'),('eighty_equal','n80_k1'),('near_min','near_min'),('range_thousand','n2_k1001')]:
 REUSE[name]=C/'evidence/visible-sorting-counting-native-fault-low/outside-four-full'/(old+'.json')
def main():
 code=native.native_base()
 code=code.replace('static void emit(const char*t,int condition){','static int wrapper_only,fail_reserve;\nstatic void emit(const char*t,int condition){\n if(wrapper_only && strcmp(t,"initial") && strncmp(t,"binsort_",8))return;')
 at=code.index('static int arreglo_valido')
 code=code[:at]+'static void* qa_calloc(size_t n,size_t s){return fail_reserve?NULL:calloc(n,s);}\nstatic int retire_error(void){iw=ih=ir=io=have_min=have_max=0;return ORDENAMIENTO_ERROR;}\n'+code[at:]
 code=code.replace('return ORDENAMIENTO_ERROR;','return retire_error();').replace('have_min=have_max=0;return retire_error();','have_min=have_max=0;return ORDENAMIENTO_ERROR;')
 code=code.replace('conteo=(int*)calloc(rango,sizeof(int));','conteo=(int*)qa_calloc(rango,sizeof(int));')
 wrapper=r'''int ordenar_binsort(int arreglo[],size_t n){emit("binsort_entry",-1);emit("binsort_delegate",-1);int observed_status=ordenar_counting_sort(arreglo,n);emit("binsort_return",-1);return observed_status;}
static void setup(int*a,size_t n,int id){root=a;count=n;case_id=id;counts=NULL;have_min=have_max=iw=ih=ir=io=comparisons=moves=allocs=frees=fail_reserve=0;emit("initial",-1);}
static void outcome(const char*name,int status){printf("{\"outcome\":\"%s\",\"case\":%d,\"status\":%d,\"array\":[",name,case_id,status);for(size_t z=0;z<count;z++){if(z)printf(",");printf("%d",root[z]);}printf("],\"allocations\":%d,\"frees\":%d,\"live\":%s,\"comparisons\":%d,\"moves\":%d}\n",allocs,frees,counts?"true":"false",comparisons,moves);}
'''
 body=[]
 for i,(name,values) in enumerate(CASES.items()):
  body.append('{int a[]={'+','.join(map(str,values))+'};wrapper_only='+str(int(name in REUSE))+';setup(a,sizeof(a)/sizeof(a[0]),'+str(i)+');int status=ordenar_binsort(a,count);outcome("'+name+'",status);}')
 body+=['{int a[]={0,1000000};wrapper_only=1;setup(a,2,20);outcome("range_reject",ordenar_binsort(a,2));}','{int a[]={5,0};wrapper_only=1;setup(a,2,21);fail_reserve=1;outcome("calloc_null_simulated",ordenar_binsort(a,2));}','{int a[]={5,0};wrapper_only=1;setup(a,0,22);outcome("empty",ordenar_binsort(a,0));}','{wrapper_only=1;setup(NULL,0,23);outcome("null",ordenar_binsort(NULL,2));}']
 out=E/'native'
 exe=native.compile_source(out,code+wrapper+'int main(void){_Static_assert(sizeof(size_t)==8,"safe observed size_t64");'+''.join(body)+'return 0;}')
 result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15);assert result.returncode==0,result.stderr
 (out/'native.jsonl').write_text(result.stdout,encoding='utf-8')
 data=[json.loads(s) for s in result.stdout.splitlines()]
 outcomes={x['outcome']:x for x in data if 'outcome' in x};rows=[]
 for i,(name,values) in enumerate(CASES.items()):
  observed=[x for x in data if x.get('case')==i and 'token' in x]
  wrapper_rows=[x for x in observed if x['token'].startswith('binsort_')]
  assert [x['token'] for x in wrapper_rows]==['binsort_entry','binsort_delegate','binsort_return']
  if name in REUSE:
   frozen=json.loads(REUSE[name].read_text(encoding='utf-8'))
   assert (frozen.get('input') or frozen['case']['input'])==values
   delegate=frozen['native']
   composed=[observed[0],*wrapper_rows[:2],*[{**x,'case':i} for x in delegate[1:]],wrapper_rows[-1]]
   assert wrapper_rows[-1]['array']==delegate[-1]['array'] and wrapper_rows[-1]['comparisons']==delegate[-1]['comparisons'] and wrapper_rows[-1]['moves']==delegate[-1]['moves']
  else:composed=observed
  oracle=outcomes[name]
  assert oracle['status']==1 and oracle['array']==sorted(values) and oracle['allocations']==oracle['frees']==1 and not oracle['live']
  assert oracle['comparisons']==2*(len(values)-1) and oracle['moves']==3*len(values)
  app=create_app();c=app.test_client()
  c.post('/api/ordenamiento/create-array',json={'values':values});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'})
  before=c.get('/api/ordenamiento/state').get_json()
  r=c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'step_by_step'})
  assert r.status_code==200
  response=r.get_json();steps=response['execution_trace']['steps'];m=response['result']['metrics'];assert response['result']['array']==oracle['array']
  row=dict(case=name,input=values,native_events=len(composed),API_frames=len(steps),omitted_events=len(composed)-len(steps),result_equal=True,native_metrics={k:oracle[k] for k in ['comparisons','moves']},API_metrics=m,metrics_equal=(m['comparisons']==oracle['comparisons'] and m['moves']==oracle['moves']),native_wrapper_events=3,delegated_oracle_reused=name in REUSE,delegate_source=str(REUSE.get(name,'new Binsort-context observer')),allocations=1,frees=1,live=0,fictional_console_events=sum(len(f['debug'].get('console_events',[])) for f in steps),typed_instruction_events=sum('instruction_event' in f['debug'] for f in steps))
  (out/(name+'.json')).write_text(json.dumps(dict(case=row,native=composed,native_wrapper=wrapper_rows,outcome=oracle,before=before,response=response),ensure_ascii=False,separators=(',',':')),encoding='utf-8');rows.append(row)
 for name in ['range_reject','calloc_null_simulated','empty','null']:
  row=outcomes[name];assert row['status']==0 and row['allocations']==row['frees']==0 and not row['live']
  assert row['array']==([0,1000000] if name=='range_reject' else [5,0] if name=='calloc_null_simulated' else [])
 (out/'report.json').write_text(json.dumps(dict(rows=rows,faults=[outcomes[n] for n in ['range_reject','calloc_null_simulated','empty','null']],counting_reused_events_not_new_standalone_tests=True),indent=2),encoding='utf-8')
 return rows
if __name__=='__main__':print(json.dumps(main(),indent=2))
