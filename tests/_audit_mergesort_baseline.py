"""Merge sort LOW observer extracts real C bodies; never reads uninitialized auxiliary cells."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from _audit_sorting_c_source import function_body,replace_once as rep
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS
CASES={'single':[7],'ordered':[1,2,3,4],'reverse':[4,3,2,1],'duplicates':[2,2,2],'negative':[-3,0,-1,0],'extremes':[2147483647,-2147483648,0]}
UI_CASES={k:CASES[k] for k in ['single','reverse','duplicates']}
def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);app=create_app();cl=app.test_client();hashes={}
 for kind,ext in [('source','c'),('header','h')]:
  r=cl.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(out/('tad_ordenamiento.'+ext)).write_bytes(r.data);hashes[ext]=hashlib.sha256(r.data).hexdigest()
 src=(out/'tad_ordenamiento.c').read_text(encoding='utf-8');catalog=[m for m in SORTING_ALGORITHMS if m['id']=='mergesort'];assert len(catalog)==1 and catalog[0]['c_function']=='ordenar_mergesort'
 (out/'inventory.json').write_text(json.dumps({'variant':catalog[0],'total_methods':len(SORTING_ALGORITHMS),'new_methods':0},indent=2),encoding='utf-8')
 observer=r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tad_ordenamiento.h"
typedef struct {const char *function;size_t left,right,mid,i,j,k;int has_mid,has_indices;} Frame;
static Frame frames[20];static int depth;
static int *root,*aux;static size_t count;static int initialized[80],live,comparisons,moves,allocs,frees,fixture,fail;
#define F frames[depth-1]
static void emit(const char*t,const char*f,int condition){
 printf("{\"case\":%d,\"event\":{\"token\":\"%s\",\"function\":",fixture,t);
 if(f)printf("\"%s\"",f);else printf("null");
 printf(",\"comparisons\":%d,\"moves\":%d,\"aux_live\":%s,\"allocations\":%d,\"frees\":%d,\"frames\":[",comparisons,moves,live?"true":"false",allocs,frees);
 for(int z=0;z<depth;z++){Frame q=frames[z];if(z)printf(",");printf("{\"function\":\"%s\",\"izquierda\":%zu,\"derecha\":%zu,\"medio\":",q.function,q.left,q.right);if(q.has_mid)printf("%zu",q.mid);else printf("null");printf(",\"i\":");if(q.has_indices)printf("%zu",q.i);else printf("null");printf(",\"j\":");if(q.has_indices)printf("%zu",q.j);else printf("null");printf(",\"k\":");if(q.has_indices)printf("%zu",q.k);else printf("null");printf("}");}
 printf("]},\"condition\":");if(condition<0)printf("null");else printf(condition?"true":"false");
 printf(",\"array\":[");for(size_t z=0;z<count;z++){if(z)printf(",");printf("%d",root[z]);}printf("],\"auxiliary\":[");
 for(size_t z=0;z<count;z++){if(z)printf(",");if(live && initialized[z])printf("%d",aux[z]);else printf("null");}puts("]}");
}
static int cond(const char*t,const char*f,int r){if(!strcmp(t,"merge_compare"))comparisons++;emit(t,f,r);return r;}
static int checked(int r){emit("valid_return","arreglo_valido",-1);return cond("sort_guard","ordenar_mergesort",!r);}
static void push(const char*f,size_t l,size_t r){frames[depth++]=(Frame){.function=f,.left=l,.right=r};}
static void *reserve(size_t n){if(fail)return NULL;void*p=malloc(n);if(p)allocs++;return p;}
'''
 valid=function_body(src,'arreglo_valido').replace('{','{emit("valid_entry","arreglo_valido",-1);',1);valid=rep(valid,'return arreglo != NULL && n > 0;','return cond("valid_ptr","arreglo_valido",arreglo!=NULL) && cond("valid_n","arreglo_valido",n>0);')
 merge=function_body(src,'mezclar').replace('{','{push("mezclar",izquierda,derecha);F.mid=medio;F.has_mid=1;emit("merge_entry","mezclar",-1);',1)
 changes=[('size_t i = izquierda, j = medio + 1, k = izquierda;','size_t i=izquierda,j=medio+1,k=izquierda;F.i=i;F.j=j;F.k=k;F.has_indices=1;emit("merge_init","mezclar",-1);'),('while (i <= medio && j <= derecha)','while(cond("merge_while","mezclar",cond("merge_left","mezclar",i<=medio) && cond("merge_right","mezclar",j<=derecha)))'),('if (arreglo[i] <= arreglo[j]) auxiliar[k++] = arreglo[i++];','if(cond("merge_compare","mezclar",arreglo[i]<=arreglo[j])) {auxiliar[k++] = arreglo[i++];initialized[k-1]=1;moves++;F.i=i;F.k=k;emit("aux_left_write","mezclar",-1);}'),('else auxiliar[k++] = arreglo[j++];','else {auxiliar[k++] = arreglo[j++];initialized[k-1]=1;moves++;F.j=j;F.k=k;emit("aux_right_write","mezclar",-1);}'),('while (i <= medio) auxiliar[k++] = arreglo[i++];','while(cond("left_tail_test","mezclar",i<=medio)){auxiliar[k++] = arreglo[i++];initialized[k-1]=1;moves++;F.i=i;F.k=k;emit("left_tail_write","mezclar",-1);}'),('while (j <= derecha) auxiliar[k++] = arreglo[j++];','while(cond("right_tail_test","mezclar",j<=derecha)){auxiliar[k++] = arreglo[j++];initialized[k-1]=1;moves++;F.j=j;F.k=k;emit("right_tail_write","mezclar",-1);}'),('for (i = izquierda; i <= derecha; ++i) arreglo[i] = auxiliar[i];','for(i=izquierda,F.i=i,emit("copy_init","mezclar",-1);cond("copy_test","mezclar",i<=derecha);++i,F.i=i,emit("copy_increment","mezclar",-1)){arreglo[i] = auxiliar[i];moves++;emit("copy_write","mezclar",-1);}')]
 for old,new in changes:merge=rep(merge,old,new)
 merge=merge[:-1]+'emit("merge_body_exit","mezclar",-1);depth--;emit("merge_return","mezclar",-1);}'
 rec=function_body(src,'mergesort_recursivo').replace('{','{push("mergesort_recursivo",izquierda,derecha);emit("rec_entry","mergesort_recursivo",-1);',1)
 for old,new in [('if (izquierda >= derecha) return;','if(cond("rec_guard","mergesort_recursivo",izquierda>=derecha)){depth--;emit("rec_return","mergesort_recursivo",-1);return;}'),('size_t medio = izquierda + (derecha - izquierda) / 2;','size_t medio = izquierda + (derecha - izquierda) / 2;F.mid=medio;F.has_mid=1;emit("split","mergesort_recursivo",-1);'),('mergesort_recursivo(arreglo, auxiliar, izquierda, medio);','emit("rec_left_call","mergesort_recursivo",-1);mergesort_recursivo(arreglo, auxiliar, izquierda, medio);emit("rec_left_resume","mergesort_recursivo",-1);'),('mergesort_recursivo(arreglo, auxiliar, medio + 1, derecha);','emit("rec_right_call","mergesort_recursivo",-1);mergesort_recursivo(arreglo, auxiliar, medio + 1, derecha);emit("rec_right_resume","mergesort_recursivo",-1);'),('mezclar(arreglo, auxiliar, izquierda, medio, derecha);','emit("merge_call","mergesort_recursivo",-1);mezclar(arreglo, auxiliar, izquierda, medio, derecha);emit("merge_resume","mergesort_recursivo",-1);')]:rec=rep(rec,old,new)
 rec=rec[:-1]+'emit("rec_body_exit","mergesort_recursivo",-1);depth--;emit("rec_return","mergesort_recursivo",-1);}'
 body=function_body(src,'ordenar_mergesort').replace('{','{emit("sort_entry","ordenar_mergesort",-1);',1)
 for old,new in [('int *auxiliar;','int *auxiliar;emit("aux_declare","ordenar_mergesort",-1);'),('if (!arreglo_valido(arreglo, n)) return ORDENAMIENTO_ERROR;','emit("valid_call","ordenar_mergesort",-1);if(checked(arreglo_valido(arreglo,n))){emit("guard_error","ordenar_mergesort",-1);return ORDENAMIENTO_ERROR;}'),('auxiliar = (int *)malloc(n * sizeof(int));','auxiliar=(int*)reserve(n*sizeof(int));aux=auxiliar;live=aux!=NULL;emit("aux_reserve","ordenar_mergesort",-1);'),('if (auxiliar == NULL) return ORDENAMIENTO_ERROR;','if(cond("allocation_guard","ordenar_mergesort",auxiliar==NULL)){emit("allocation_error","ordenar_mergesort",-1);return ORDENAMIENTO_ERROR;}'),('mergesort_recursivo(arreglo, auxiliar, 0, n - 1);','emit("recursive_call","ordenar_mergesort",-1);mergesort_recursivo(arreglo, auxiliar, 0, n - 1);emit("recursive_resume","ordenar_mergesort",-1);'),('free(auxiliar);','free(auxiliar);live=0;aux=NULL;frees++;emit("aux_free","ordenar_mergesort",-1);'),('return ORDENAMIENTO_OK;','emit("sort_return","ordenar_mergesort",-1);return ORDENAMIENTO_OK;')]:body=rep(body,old,new)
 native=observer+'\n'+valid+'\n'+merge+'\n'+rec+'\n'+body+'\nint main(void){int status;\n'
 def setup(index,fault=0):return f'fixture={index};depth=live=comparisons=moves=allocs=frees=0;aux=NULL;memset(initialized,0,sizeof(initialized));fail={fault};emit("initial",NULL,-1);'
 for index,values in enumerate(CASES.values()):native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);'+setup(index)+'status=ordenar_mergesort(a,count);if(status!=ORDENAMIENTO_OK)return 2;}\n'
 native+='{int a=42;root=&a;count=0;'+setup(6)+'status=ordenar_mergesort(&a,0);if(status!=ORDENAMIENTO_ERROR || a!=42)return 3;}\n{root=NULL;count=0;'+setup(7)+'status=ordenar_mergesort(NULL,1);if(status!=ORDENAMIENTO_ERROR)return 4;}\n{int a[]={2,1};root=a;count=2;'+setup(8,1)+'status=ordenar_mergesort(a,2);if(status!=ORDENAMIENTO_ERROR || a[0]!=2 || a[1]!=1)return 5;}return 0;}\n'
 (out/'observed.c').write_text(native,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(p.stdout);assert p.returncode==0,p.stderr;obs=[json.loads(x) for x in p.stdout.splitlines()];rows=[]
 mapping={'entry':'sort_entry','validate_array':'valid_return','split':'split','merge_compare':'merge_compare','merge_copy_back':'merge_body_exit','return':'sort_return'}
 for index,(name,values) in enumerate(CASES.items()):
  responses={}
  for mode in ['fast','step_by_step']:
   c=app.test_client();c.post('/api/ordenamiento/create-array',json={'values':values});responses[mode]=c.post('/api/ordenamiento/run',json={'algorithm_id':'mergesort','mode':mode}).get_json();assert responses[mode]['success']
  d=responses['step_by_step'];steps=d['execution_trace']['steps'];actual=[r for r in obs if r['case']==index];last=actual[-1];m=d['result']['metrics'];assert last['array']==sorted(values)==d['visual_state']['items']==responses['fast']['visual_state']['items'];assert (m['comparisons'],m['moves'],m['swaps'])==(last['event']['comparisons'],last['event']['moves'],0);assert last['event']['allocations']==last['event']['frees']==1 and not last['event']['aux_live']
  cursor=0;proj=[]
  for k,s in enumerate(steps):
   token=s['state_after']['trace_token'];j=k if 'instruction_event' in s['debug'] else next(j for j in range(cursor,len(actual)) if actual[j]['event']['token']==mapping[token]);c=actual[j];cursor=j+1
   if 'instruction_event' in s['debug']:
    assert s['debug']['instruction_event']==c['event'] and s['state_snapshot']['items']==actual[max(0,j-1)]['array']
    assert (s['pedagogy']['condition']['result'] if s['pedagogy']['condition'] else None)==c['condition'] and s['debug']['console_events']==[]
   assert c['array']==s['state_after']['items'];assert (c['event']['comparisons'],c['event']['moves'])==(s['state_after']['metrics']['comparisons'],s['state_after']['metrics']['moves'])
   aux_runtime=s['state_after'].get('auxiliary_array');interval=s['state_after'].get('active_range');aux_native=(c['auxiliary'] if c['event']['aux_live'] else None) if 'instruction_event' in s['debug'] else c['auxiliary'][interval[0]:interval[1]+1] if interval else None
   variables={v['name']:v['value'] for v in s['pedagogy']['variables']};top=c['event']['frames'][-1] if c['event']['frames'] else {};missing=[key for key,value in top.items() if key!='function' and value is not None and variables.get(key)!=value]
   proj.append({'runtime_index':k,'native_index':j,'token':token,'array_matches':True,'missing_or_wrong_locals':missing,'aux_native':aux_native,'aux_runtime':aux_runtime,'auxiliary_mismatch':aux_runtime is not None and aux_runtime!=aux_native,'native_depth':len(c['event']['frames']),'runtime_stack':[f['function'] for f in s['pedagogy']['call_stack']]})
  gaps=[p for p in proj if p['auxiliary_mismatch']];writes=sum(c['event']['token']=='copy_write' for c in actual);assert sum(c['event']['token'] in ['aux_left_write','aux_right_write','left_tail_write','right_tail_write'] for c in actual)==writes
  short=[i for i,c in enumerate(actual) if c['event']['token']=='merge_left' and c['condition'] is False];assert all(actual[i+1]['event']['token']=='merge_while' for i in short)
  rows.append({'case':name,'native_observations':len(actual),'runtime_steps':len(steps),'unrepresented_observations':len(actual)-len(steps),'missing_local_frames':sum(bool(p['missing_or_wrong_locals']) for p in proj),'auxiliary_mismatch_frames':len(gaps),'max_native_depth':max(len(c['event']['frames']) for c in actual),'copy_writes':writes,'shortcircuits':len(short),'comparisons':m['comparisons'],'moves':m['moves'],'allocations':1,'frees':1,'final_array_metrics_match':True,'instruction_fidelity':len(actual)==len(steps) and all('instruction_event' in s['debug'] for s in steps)})
  (out/(name+'.json')).write_text(json.dumps({'input':values,'native':actual,'response':d,'fast_response':responses['fast'],'projection':proj},ensure_ascii=False,indent=2),encoding='utf-8')
 guards=[r for r in obs if r['case'] in [6,7]];fault=[r for r in obs if r['case']==8];assert not any(c['event']['token']=='valid_n' for c in guards if c['case']==7);assert all(not c['event']['aux_live'] and c['event']['allocations']==0 for c in guards+fault);assert not any(c['event']['token']=='rec_entry' for c in guards+fault)
 empty=app.test_client().post('/api/ordenamiento/run',json={'algorithm_id':'mergesort'}).get_json();assert not empty['success'] and all(h['operation']!='run' for h in empty['history'])
 report={'rows':rows,'C_H_hashes':hashes,'native_observations':sum(r['native_observations'] for r in rows),'runtime_steps':sum(r['runtime_steps'] for r in rows),'native_guard_cases':2,'native_guard_observations':len(guards),'forced_allocation_failure_cases':1,'forced_allocation_failure_observations':len(fault),'empty_API_rejected':True,'strict_C17':True,'instruction_fidelity':all(row['instruction_fidelity'] for row in rows)};(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
if __name__=='__main__':print(json.dumps(audit(sys.argv[1])))
