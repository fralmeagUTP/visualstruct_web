"""Existing improved-bubble baseline: independent real-C controls and partial swaps."""
from pathlib import Path
import sys,re,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS
from _audit_sorting_c_source import function_body,replace_once as rep
CASES={'single':[7],'ordered':[1,2,3,4],'reverse':[4,3,2,1],'duplicates':[2,2,2],'negative':[-3,0,-1,0],'extremes':[2147483647,-2147483648,0],'early_after_swap':[2,1,3,4]}
UI_CASES={'ordered':CASES['ordered'],'reverse':CASES['reverse'],'early_after_swap':CASES['early_after_swap']}

def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);app=create_app();client=app.test_client();hashes={}
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(out/('tad_ordenamiento.'+ext)).write_bytes(r.data);hashes[ext]=hashlib.sha256(r.data).hexdigest()
 source=(out/'tad_ordenamiento.c').read_text(encoding='utf-8');header=(out/'tad_ordenamiento.h').read_text(encoding='utf-8')
 declarations=re.findall(r'\bvoid (ordenar_\w*burbuja\w*)\(',header);definitions=re.findall(r'^void (ordenar_\w*burbuja\w*)\(',source,re.M);catalog=[item for item in SORTING_ALGORITHMS if 'burbuja' in item['id'] or 'burbuja' in item['c_function']]
 assert declarations==definitions==['ordenar_burbuja'] and len(catalog)==1 and catalog[0]['id']=='burbuja'
 inventory={'registered_variants':catalog,'C_definitions':definitions,'H_declarations':declarations,'API_variants':[item for item in client.get('/api/ordenamiento/state').get_json()['algorithms'] if 'burbuja' in item['id']],'shared_C_helper':'intercambiar','graph_exclusion':'grafo_kruskal has embedded bubble over arc pointers, different type/contract,not sorting_array variant','no_new_methods':True,'total_sorting_ids':len(SORTING_ALGORITHMS)};(out/'inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
 observer=r'''
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
static int *root,*pa,*pb,*pt,*pf;static size_t count,*pp,*pj,cp,cj;
static int has_p,has_j,has_t,has_flag,ct,cf,comparisons,swaps,moves,fixture;
static void emit(const char *token,const char *function,int condition){
 if(pp && has_p){cp=*pp;}if(pj && has_j){cj=*pj;}if(pt && has_t){ct=*pt;}if(pf && has_flag){cf=*pf;}
 printf("{\"case\":%d,\"event\":{\"token\":\"%s\",\"function\":",fixture,token);
 if(function){printf("\"%s\"",function);}else{printf("null");}
 printf(",\"pasada\":");if(has_p){printf("%zu",cp);}else{printf("null");}
 printf(",\"j\":");if(has_j){printf("%zu",cj);}else{printf("null");}
 printf(",\"hubo_intercambio\":");if(has_flag){printf("%d",cf);}else{printf("null");}
 printf(",\"temporal\":");if(pt && has_t){printf("%d",ct);}else{printf("null");}
 printf(",\"a\":");if(pa){printf("%td",pa-root);}else{printf("null");}
 printf(",\"b\":");if(pb){printf("%td",pb-root);}else{printf("null");}
 printf(",\"comparisons\":%d,\"swaps\":%d,\"moves\":%d},\"condition\":",comparisons,swaps,moves);
 if(condition<0){printf("null");}else{printf(condition?"true":"false");}
 printf(",\"array\":[");for(size_t k=0;k<count;k++){if(k){printf(",");}printf("%d",root[k]);}puts("]}");
}
static int cond(const char*t,const char*f,int r){if(!strcmp(t,"compare")){comparisons++;}emit(t,f,r);return r;}
static int checked(int r){emit("valid_return","arreglo_valido",-1);return cond("sort_guard","ordenar_burbuja",!r);}
'''
 valid=function_body(source,'arreglo_valido').replace('{','{emit("valid_entry","arreglo_valido",-1);',1);valid=rep(valid,'return arreglo != NULL && n > 0;','return cond("valid_ptr","arreglo_valido",arreglo!=NULL) && cond("valid_n","arreglo_valido",n>0);')
 swap=function_body(source,'intercambiar').replace('{','{pa=a;pb=b;emit("swap_entry","intercambiar",-1);',1)
 for old,new in [('int temporal;','int temporal;pt=&temporal;has_t=0;emit("swap_declare","intercambiar",-1);'),('if (a == NULL || b == NULL)','if (cond("swap_guard","intercambiar",a==NULL || b==NULL))'),('temporal = *a;','temporal=*a;has_t=1;moves++;emit("swap_temp","intercambiar",-1);'),('*a = *b;','*a=*b;moves++;emit("swap_assign_a","intercambiar",-1);'),('*b = temporal;','*b=temporal;moves++;swaps++;emit("swap_assign_b","intercambiar",-1);')]:swap=rep(swap,old,new)
 body=function_body(source,'ordenar_burbuja').replace('{','{emit("sort_entry","ordenar_burbuja",-1);',1)
 for old,new in [('size_t pasada, j;','size_t pasada,j;pp=&pasada;pj=&j;emit("sort_declare_indices","ordenar_burbuja",-1);'),('int hubo_intercambio;','int hubo_intercambio;pf=&hubo_intercambio;emit("sort_declare_flag","ordenar_burbuja",-1);'),('if (!arreglo_valido(arreglo, n)) return;','emit("valid_call","ordenar_burbuja",-1);if(checked(arreglo_valido(arreglo,n))){pp=pj=NULL;pf=NULL;emit("guard_return","ordenar_burbuja",-1);return;}'),('for (pasada = 0; pasada + 1 < n; ++pasada)','for(pasada=0,has_p=1,emit("outer_init","ordenar_burbuja",-1);cond("outer_test","ordenar_burbuja",pasada+1<n);++pasada,emit("outer_increment","ordenar_burbuja",-1))'),('hubo_intercambio = 0;','hubo_intercambio=0;has_flag=1;emit("flag_reset","ordenar_burbuja",-1);'),('for (j = 0; j + 1 < n - pasada; ++j)','for(j=0,has_j=1,emit("inner_init","ordenar_burbuja",-1);cond("inner_test","ordenar_burbuja",j+1<n-pasada);++j,emit("inner_increment","ordenar_burbuja",-1))'),('if (arreglo[j] > arreglo[j + 1])','if(cond("compare","ordenar_burbuja",arreglo[j]>arreglo[j+1]))'),('intercambiar(&arreglo[j], &arreglo[j + 1]);','emit("swap_call","ordenar_burbuja",-1);intercambiar(&arreglo[j],&arreglo[j+1]);pa=pb=pt=NULL;has_t=0;emit("swap_return","intercambiar",-1);emit("swap_resume","ordenar_burbuja",-1);'),('hubo_intercambio = 1;','hubo_intercambio=1;emit("flag_set","ordenar_burbuja",-1);'),('if (!hubo_intercambio) break;','if(cond("stop_test","ordenar_burbuja",!hubo_intercambio)){emit("early_break","ordenar_burbuja",-1);break;}')]:body=rep(body,old,new)
 boundary=body.rfind('\t}');assert boundary!=-1;body=body[:boundary]+'emit("outer_complete","ordenar_burbuja",-1);'+body[boundary:];body=body[:-1]+'pp=pj=NULL;pf=NULL;}\n'
 native=observer+'\n'+swap+'\n'+valid+'\n'+body+'\nint main(void){\n'
 for index,values in enumerate(CASES.values()):native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);fixture='+str(index)+';has_p=has_j=has_t=has_flag=comparisons=swaps=moves=0;pp=pj=NULL;pa=pb=pt=pf=NULL;emit("initial",NULL,-1);ordenar_burbuja(a,count);emit("sort_return","ordenar_burbuja",-1);}\n'
 native+='{int a=42;root=&a;count=0;fixture=7;has_p=has_j=has_t=has_flag=comparisons=swaps=moves=0;pp=pj=NULL;pa=pb=pt=pf=NULL;emit("initial",NULL,-1);ordenar_burbuja(&a,0);}\n{root=NULL;count=0;fixture=8;has_p=has_j=has_t=has_flag=comparisons=swaps=moves=0;pp=pj=NULL;pa=pb=pt=pf=NULL;emit("initial",NULL,-1);ordenar_burbuja(NULL,1);}\nreturn 0;}\n'
 (out/'observed.c').write_text(native,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(p.stdout);assert p.returncode==0,p.stderr;observations=[json.loads(line) for line in p.stdout.splitlines()];rows=[]
 mapping={'entry':'sort_entry','validate_array':'valid_return','compare':'compare','swap':'swap_call','swap_guard':'swap_guard','swap_temp':'swap_temp','swap_assign_a':'swap_assign_a','swap_assign_b':'swap_assign_b','break':'early_break','return':'sort_return'}
 for index,(name,values) in enumerate(CASES.items()):
  responses={}
  for mode in ['fast','step_by_step']:
   client=app.test_client();client.post('/api/ordenamiento/create-array',json={'values':values});responses[mode]=client.post('/api/ordenamiento/run',json={'algorithm_id':'burbuja','mode':mode}).get_json();assert responses[mode]['success']
  d=responses['step_by_step'];steps=d['execution_trace']['steps'];actual=[r for r in observations if r['case']==index];assert actual[-1]['array']==sorted(values)==d['visual_state']['items']==responses['fast']['visual_state']['items'];metrics=d['result']['metrics'];assert metrics['comparisons']==actual[-1]['event']['comparisons'] and metrics['swaps']==actual[-1]['event']['swaps']
  cursor=0;projection=[]
  for runtime_index,step in enumerate(steps):
   token=step['state_after']['trace_token']
   if 'instruction_event' in step['debug']:
    wanted=token;cindex=runtime_index;c=actual[cindex]
    assert step['debug']['instruction_event']==c['event'],(name,runtime_index,c,step['debug'])
    assert step['state_snapshot']['items']==actual[max(0,cindex-1)]['array']
    assert (step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)==c['condition']
    assert step['debug']['console_events']==[]
   else:
    wanted=mapping[token];cindex=next(k for k in range(cursor,len(actual)) if actual[k]['event']['token']==wanted);c=actual[cindex]
   cursor=cindex+1;assert c['array']==step['state_after']['items']
   variables={v['name']:v for v in step['pedagogy']['variables']};missing=[name for name in ([] if wanted=='sort_return' else ['pasada','j','hubo_intercambio']) if c['event'][name] is not None and (name not in variables or variables[name]['value']!=c['event'][name])]
   projection.append({'runtime_index':runtime_index,'native_index':cindex,'token':token,'missing_or_wrong_locals':missing,'array_matches':True,'moves_native':c['event']['moves'],'moves_runtime':step['state_after']['metrics']['moves'],'line_missing':step['line_index'] is None and token!='initial'})
  early=any(r['event']['token']=='early_break' for r in actual);assert early==any(s['state_after']['trace_token'] in {'break','early_break'} for s in steps)
  row={'case':name,'native_observations':len(actual),'runtime_steps':len(steps),'unrepresented_observations':len(actual)-len(steps),'final_comparison_swap_parity':True,'native_moves':actual[-1]['event']['moves'],'runtime_moves':metrics['moves'],'moves_match':metrics['moves']==actual[-1]['event']['moves'],'array_differences':0,'missing_local_frames':sum(bool(r['missing_or_wrong_locals']) for r in projection),'source_missing_frames':sum(r['line_missing'] for r in projection),'completed_passes':sum(r['event']['token']=='stop_test' for r in actual),'comparisons':metrics['comparisons'],'swaps':metrics['swaps'],'early_stop':early,'instruction_fidelity':len(actual)==len(steps) and all('instruction_event' in step['debug'] for step in steps)};rows.append(row)
  (out/(name+'.json')).write_text(json.dumps({'input':values,'native':actual,'response':d,'fast_response':responses['fast'],'projection':projection},ensure_ascii=False,indent=2),encoding='utf-8')
 guards=[r for r in observations if r['case']>=7];assert not any(r['event']['token']=='valid_n' for r in guards if r['case']==8);assert not any(r['event']['token'] in {'compare','swap_call','flag_reset'} for r in guards)
 empty=app.test_client().post('/api/ordenamiento/run',json={'algorithm_id':'burbuja','mode':'step_by_step'}).get_json();assert not empty['success'] and all(e['operation']!='run' for e in empty['history'])
 report={'rows':rows,'C_H_hashes':hashes,'variants':1,'native_observations':sum(r['native_observations'] for r in rows),'runtime_steps':sum(r['runtime_steps'] for r in rows),'native_guard_cases':2,'native_guard_observations':len(guards),'empty_API_rejected':True,'strict_C17':True,'instruction_fidelity':all(row['instruction_fidelity'] for row in rows)};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');return report
if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
