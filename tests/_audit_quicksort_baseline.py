"""Actual-C Quick sort LOW oracle: recursion, scans, helper alias and counters."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from _audit_sorting_c_source import function_body,replace_once as rep
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS
CASES={'single':[7],'ordered':[1,2,3,4],'reverse':[4,3,2,1],'duplicates':[2,2,2],'negative':[-3,0,-1,0],'extremes':[2147483647,-2147483648,0]}
UI_CASES={name:CASES[name] for name in ['single','reverse','duplicates']}
def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);app=create_app();client=app.test_client();hashes={}
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(out/('tad_ordenamiento.'+ext)).write_bytes(r.data);hashes[ext]=hashlib.sha256(r.data).hexdigest()
 source=(out/'tad_ordenamiento.c').read_text(encoding='utf-8');catalog=[m for m in SORTING_ALGORITHMS if m['id']=='quicksort'];assert len(catalog)==1 and catalog[0]['c_function']=='ordenar_quicksort'
 (out/'inventory.json').write_text(json.dumps({'variant':catalog[0],'total_methods':len(SORTING_ALGORITHMS),'helpers':['arreglo_valido','quicksort_recursivo','intercambiar'],'partition_function':False,'new_methods':0},indent=2),encoding='utf-8')
 observer=r'''
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
#include <assert.h>
typedef struct {int first,last,*i,*j,*pivot,initialized;} Frame;
static Frame frames[64];static int depth;
static int *root,*pa,*pb,*pt,has_t,fixture,comparisons,swaps,moves;static size_t count;
static void emit(const char*t,const char*f,int condition){
 printf("{\"case\":%d,\"event\":{\"token\":\"%s\",\"function\":",fixture,t);
 if(f){printf("\"%s\"",f);}else{printf("null");}
 printf(",\"frames\":[");for(int k=0;k<depth;k++){Frame *q=&frames[k];if(k){printf(",");}printf("{\"primero\":%d,\"ultimo\":%d,\"i\":",q->first,q->last);if(q->initialized){printf("%d",*q->i);}else{printf("null");}printf(",\"j\":");if(q->initialized){printf("%d",*q->j);}else{printf("null");}printf(",\"pivote\":");if(q->initialized){printf("%d",*q->pivot);}else{printf("null");}printf("}");}printf("]");
 printf(",\"temporal\":");if(pt && has_t){printf("%d",*pt);}else{printf("null");}
 printf(",\"a\":");if(pa){printf("%td",pa-root);}else{printf("null");}printf(",\"b\":");if(pb){printf("%td",pb-root);}else{printf("null");}
 printf(",\"comparisons\":%d,\"swaps\":%d,\"moves\":%d},\"condition\":",comparisons,swaps,moves);
 if(condition<0){printf("null");}else{printf(condition?"true":"false");}
 printf(",\"array\":[");for(size_t k=0;k<count;k++){if(k){printf(",");}printf("%d",root[k]);}puts("]}");
}
static int cond(const char*t,const char*f,int r){if(!strcmp(t,"i_test") || !strcmp(t,"j_test") || !strcmp(t,"cross_test")){comparisons++;}emit(t,f,r);return r;}
static int checked(int r){emit("valid_return","arreglo_valido",-1);return cond("sort_guard","ordenar_quicksort",!r);}
'''
 valid=function_body(source,'arreglo_valido').replace('{','{emit("valid_entry","arreglo_valido",-1);',1);valid=rep(valid,'return arreglo != NULL && n > 0;','return cond("valid_ptr","arreglo_valido",arreglo!=NULL) && cond("valid_n","arreglo_valido",n>0);')
 swap=function_body(source,'intercambiar').replace('{','{pa=a;pb=b;emit("swap_entry","intercambiar",-1);',1)
 for old,new in [('int temporal;','int temporal;pt=&temporal;has_t=0;emit("swap_declare","intercambiar",-1);'),('if (a == NULL || b == NULL)','if(cond("swap_guard","intercambiar",a==NULL || b==NULL))'),('temporal = *a;','temporal=*a;has_t=1;moves++;emit("swap_temp","intercambiar",-1);'),('*a = *b;','*a=*b;moves++;emit("swap_assign_a","intercambiar",-1);'),('*b = temporal;','*b=temporal;moves++;swaps++;emit("swap_assign_b","intercambiar",-1);')]:swap=rep(swap,old,new)
 # Retire temporal before returning, not after its stack lifetime ends.
 swap=swap[:-1]+'pt=NULL;has_t=0;pa=pb=NULL;}\n'
 rec=function_body(source,'quicksort_recursivo').replace('{','{assert(depth<64);frames[depth++]=(Frame){primero,ultimo,NULL,NULL,NULL,0};emit("rec_entry","quicksort_recursivo",-1);',1)
 edits=[('int i = primero, j = ultimo, pivote = arreglo[(primero + ultimo) / 2];','int i=primero,j=ultimo,pivote=arreglo[(primero+ultimo)/2];frames[depth-1].i=&i;frames[depth-1].j=&j;frames[depth-1].pivot=&pivote;frames[depth-1].initialized=1;emit("rec_init","quicksort_recursivo",-1);'),('while (i <= j)','while(cond("outer_test","quicksort_recursivo",i<=j))'),('while (arreglo[i] < pivote) ++i;','while(cond("i_test","quicksort_recursivo",arreglo[i]<pivote)){++i;emit("i_increment","quicksort_recursivo",-1);}'),('while (arreglo[j] > pivote) --j;','while(cond("j_test","quicksort_recursivo",arreglo[j]>pivote)){--j;emit("j_decrement","quicksort_recursivo",-1);}'),('if (i <= j)','if(cond("cross_test","quicksort_recursivo",i<=j))'),('intercambiar(&arreglo[i], &arreglo[j]);','emit("swap_call","quicksort_recursivo",-1);intercambiar(&arreglo[i],&arreglo[j]);emit("swap_return","intercambiar",-1);emit("swap_resume","quicksort_recursivo",-1);'),('++i; --j;','++i;emit("cross_i_increment","quicksort_recursivo",-1);--j;emit("cross_j_decrement","quicksort_recursivo",-1);'),('if (primero < j) quicksort_recursivo(arreglo, primero, j);','if(cond("left_test","quicksort_recursivo",primero<j)){emit("left_call","quicksort_recursivo",-1);quicksort_recursivo(arreglo,primero,j);emit("left_resume","quicksort_recursivo",-1);}'),('if (i < ultimo) quicksort_recursivo(arreglo, i, ultimo);','if(cond("right_test","quicksort_recursivo",i<ultimo)){emit("right_call","quicksort_recursivo",-1);quicksort_recursivo(arreglo,i,ultimo);emit("right_resume","quicksort_recursivo",-1);}')] 
 for old,new in edits:rec=rep(rec,old,new)
 rec=rec[:-1]+'depth--;emit("rec_return","quicksort_recursivo",-1);}\n'
 body=function_body(source,'ordenar_quicksort').replace('{','{emit("sort_entry","ordenar_quicksort",-1);',1);body=rep(body,'if (!arreglo_valido(arreglo, n)) return;','emit("valid_call","ordenar_quicksort",-1);if(checked(arreglo_valido(arreglo,n))){emit("guard_return","ordenar_quicksort",-1);return;}');body=rep(body,'quicksort_recursivo(arreglo, 0, (int)n - 1);','emit("rec_call","ordenar_quicksort",-1);quicksort_recursivo(arreglo,0,(int)n-1);emit("rec_resume","ordenar_quicksort",-1);')
 native=observer+'\n'+valid+'\n'+swap+'\n'+rec+'\n'+body+'\nint main(void){\n'
 def setup(idx):return f'fixture={idx};depth=has_t=comparisons=swaps=moves=0;pa=pb=pt=NULL;emit("initial",NULL,-1);'
 for idx,values in enumerate(CASES.values()):native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);'+setup(idx)+'ordenar_quicksort(a,count);emit("sort_return","ordenar_quicksort",-1);}\n'
 native+='{int a=42;root=&a;count=0;'+setup(6)+'ordenar_quicksort(&a,0);}\n{root=NULL;count=0;'+setup(7)+'ordenar_quicksort(NULL,1);}\nreturn 0;}\n';(out/'observed.c').write_text(native,encoding='utf-8')
 p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(p.stdout);assert p.returncode==0,p.stderr;obs=[json.loads(line) for line in p.stdout.splitlines()];rows=[]
 mapping={'entry':'sort_entry','validate_array':'valid_return','pivot':'rec_init','move_i':'i_test','move_j':'j_test','partition_swap':'swap_call','swap_guard':'swap_guard','swap_temp':'swap_temp','swap_assign_a':'swap_assign_a','swap_assign_b':'swap_assign_b','return':'sort_return'}
 for idx,(name,values) in enumerate(CASES.items()):
  responses={}
  for mode in ['fast','step_by_step']:
   cl=app.test_client();cl.post('/api/ordenamiento/create-array',json={'values':values});responses[mode]=cl.post('/api/ordenamiento/run',json={'algorithm_id':'quicksort','mode':mode}).get_json();assert responses[mode]['success']
  d=responses['step_by_step'];steps=d['execution_trace']['steps'];actual=[o for o in obs if o['case']==idx];assert actual[-1]['array']==sorted(values)==d['visual_state']['items']==responses['fast']['visual_state']['items'];cursor=0;projection=[]
  for k,step in enumerate(steps):
   token=step['state_after']['trace_token']
   if 'instruction_event' in step['debug']:
    ci=k;actual_step=actual[ci];assert step['debug']['instruction_event']==actual_step['event']
    assert step['state_snapshot']['items']==actual[max(0,ci-1)]['array']
    assert (step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)==actual_step['condition'] and step['debug']['console_events']==[]
   else:
    wanted=mapping[token];ci=next(j for j in range(cursor,len(actual)) if actual[j]['event']['token']==wanted);actual_step=actual[ci]
   cursor=ci+1;assert actual_step['array']==step['state_after']['items']
   variables={v['name']:v for v in step['pedagogy']['variables']};frame=actual_step['event']['frames'][-1] if actual_step['event']['frames'] else {};missing=[local for local,value in frame.items() if value is not None and (local not in variables or variables[local]['value']!=value)]
   projection.append({'runtime_index':k,'native_index':ci,'token':token,'array_matches':True,'missing_or_wrong_locals':missing,'condition_native':actual_step['condition'],'condition_runtime':step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None,'moves_native':actual_step['event']['moves'],'moves_runtime':step['state_after']['metrics']['moves'],'console_events':step['debug'].get('console_events')})
  final=actual[-1]['event'];m=d['result']['metrics'];rows.append({'case':name,'native_observations':len(actual),'runtime_steps':len(steps),'unrepresented_observations':len(actual)-len(steps),'missing_local_frames':sum(bool(x['missing_or_wrong_locals']) for x in projection),'max_recursion_depth':max(len(o['event']['frames']) for o in actual),'native_rec_calls':sum(o['event']['token']=='rec_entry' for o in actual),'native_self_swaps':sum(o['event']['token']=='swap_call' and o['event']['frames'][-1]['i']==o['event']['frames'][-1]['j'] for o in actual),'final_array_match':True,'native_metrics':{k:final[k] for k in ['comparisons','swaps','moves']},'runtime_metrics':{k:m[k] for k in ['comparisons','swaps','moves']},'metrics_match':all(m[k]==final[k] for k in ['comparisons','swaps','moves']),'instruction_fidelity':len(actual)==len(steps) and all('instruction_event' in x['debug'] for x in steps)})
  (out/(name+'.json')).write_text(json.dumps({'input':values,'native':actual,'response':d,'fast_response':responses['fast'],'projection':projection},ensure_ascii=False,indent=2),encoding='utf-8')
 guards=[o for o in obs if o['case']>=6];assert not any(o['event']['token']=='valid_n' for o in guards if o['case']==7);assert not any(o['event']['frames'] for o in guards)
 empty=app.test_client().post('/api/ordenamiento/run',json={'algorithm_id':'quicksort'}).get_json();assert not empty['success']
 report={'rows':rows,'C_H_hashes':hashes,'native_observations':sum(x['native_observations'] for x in rows),'runtime_steps':sum(x['runtime_steps'] for x in rows),'native_guard_cases':2,'native_guard_observations':len(guards),'empty_API_rejected':True,'strict_C17':True,'instruction_fidelity':all(x['instruction_fidelity'] for x in rows)};(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
if __name__=='__main__':print(json.dumps(audit(sys.argv[1])))
