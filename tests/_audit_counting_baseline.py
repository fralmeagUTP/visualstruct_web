"""Counting sort LOW observer extracted from canonical C; metrics explicit data writes."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from _audit_sorting_c_source import function_body,replace_once as rep
CASES={'single':[7],'ordered':[1,2,3,4],'reverse':[4,3,2,1],'duplicates':[2,2,2],'negative':[-3,0,-1,0],'extremes':[-2147483647,-2147483648]}
UI_CASES={k:CASES[k] for k in ['ordered','negative','extremes']}
def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);client=create_app().test_client()
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(out/('tad_ordenamiento.'+ext)).write_bytes(r.data)
 src=(out/'tad_ordenamiento.c').read_text(encoding='utf-8')
 observer=r'''
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "tad_ordenamiento.h"
static int *root,*counts,minv,maxv,have_min,have_max,case_id,comparisons,moves,allocs,frees;static size_t count,range,wi,hi,output;static int iw,ih,ir,io;
static void emit(const char*t,int condition){
 printf("{\"case\":%d,\"token\":\"%s\",\"condition\":",case_id,t);if(condition<0)printf("null");else printf(condition?"true":"false");printf(",\"array\":[");for(size_t z=0;z<count;z++){if(z)printf(",");printf("%d",root[z]);}printf("],\"minimo\":");if(have_min)printf("%d",minv);else printf("null");printf(",\"maximo\":");if(have_max)printf("%d",maxv);else printf("null");printf(",\"i\":");if(iw)printf("%zu",wi);else printf("null");printf(",\"helper_i\":");if(ih)printf("%zu",hi);else printf("null");printf(",\"rango\":");if(ir)printf("%zu",range);else printf("null");printf(",\"indice\":");if(io)printf("%zu",output);else printf("null");printf(",\"conteo\":");if(counts){printf("[");for(size_t z=0;z<range;z++){if(z)printf(",");printf("%d",counts[z]);}printf("]");}else printf("null");printf(",\"comparisons\":%d,\"moves\":%d,\"allocations\":%d,\"frees\":%d}\n",comparisons,moves,allocs,frees);
}
static int cond(const char*t,int r){if(!strcmp(t,"min_compare")||!strcmp(t,"max_compare"))comparisons++;emit(t,r);return r;}
'''.replace('#include <stdio.h>','#include <stdio.h>\n#include <string.h>')
 valid=function_body(src,'arreglo_valido').replace('{','{emit("valid_entry",-1);',1);valid=rep(valid,'return arreglo != NULL && n > 0;','return cond("valid_ptr",arreglo!=NULL) && cond("valid_n",n>0);')
 helper=function_body(src,'obtener_minimo_maximo').replace('{','{emit("minmax_entry",-1);',1)
 for old,new in [('size_t i;','size_t i;emit("helper_i_declare",-1);'),('if (!arreglo_valido(arreglo, n) || minimo == NULL || maximo == NULL) return ORDENAMIENTO_ERROR;','if(cond("minmax_guard",!arreglo_valido(arreglo,n) || minimo==NULL || maximo==NULL))return ORDENAMIENTO_ERROR;'),('*minimo = arreglo[0]; *maximo = arreglo[0];','*minimo=arreglo[0];minv=*minimo;have_min=1;emit("min_init",-1);*maximo=arreglo[0];maxv=*maximo;have_max=1;emit("max_init",-1);'),('for (i = 1; i < n; ++i)','for(i=1,hi=i,ih=1,emit("scan_init",-1);cond("scan_test",i<n);++i,hi=i,emit("scan_increment",-1))'),('if (arreglo[i] < *minimo) *minimo = arreglo[i];','if(cond("min_compare",arreglo[i]<*minimo)){*minimo=arreglo[i];minv=*minimo;emit("min_assign",-1);}'),('if (arreglo[i] > *maximo) *maximo = arreglo[i];','if(cond("max_compare",arreglo[i]>*maximo)){*maximo=arreglo[i];maxv=*maximo;emit("max_assign",-1);}'),('return ORDENAMIENTO_OK;','ih=0;emit("minmax_return",-1);return ORDENAMIENTO_OK;')]:helper=rep(helper,old,new)
 body=function_body(src,'ordenar_counting_sort').replace('{','{emit("sort_entry",-1);',1)
 for old,new in [('int minimo, maximo; size_t rango, i, indice; int *conteo;','int minimo,maximo;size_t rango,i,indice;int *conteo;emit("declare",-1);'),('if (!arreglo_valido(arreglo, n)) return ORDENAMIENTO_ERROR;','emit("valid_call",-1);if(cond("sort_guard",!arreglo_valido(arreglo,n)))return ORDENAMIENTO_ERROR;'),('if (!obtener_minimo_maximo(arreglo, n, &minimo, &maximo)) return ORDENAMIENTO_ERROR;','emit("minmax_call",-1);if(cond("minmax_status",!obtener_minimo_maximo(arreglo,n,&minimo,&maximo)))return ORDENAMIENTO_ERROR;'),('rango = (size_t)((long long)maximo - (long long)minimo + 1LL);','rango=(size_t)((long long)maximo-(long long)minimo+1LL);range=rango;ir=1;emit("range_compute",-1);'),('if (rango > ORDENAMIENTO_RANGO_MAX || rango > SIZE_MAX / sizeof(int)) return ORDENAMIENTO_ERROR;','if(cond("range_guard",cond("range_limit",rango>ORDENAMIENTO_RANGO_MAX) || cond("size_guard",rango>SIZE_MAX/sizeof(int))))return ORDENAMIENTO_ERROR;'),('conteo = (int *)calloc(rango, sizeof(int));','conteo=(int*)calloc(rango,sizeof(int));counts=conteo;if(conteo)allocs++;emit("count_init",-1);'),('if (conteo == NULL) return ORDENAMIENTO_ERROR;','if(cond("allocation_guard",conteo==NULL))return ORDENAMIENTO_ERROR;'),('for (i = 0; i < n; ++i) ++conteo[arreglo[i] - minimo];','for(i=0,wi=i,iw=1,emit("fill_init",-1);cond("fill_test",i<n);++i,wi=i,emit("fill_increment",-1)){++conteo[arreglo[i]-minimo];moves++;emit("count_fill",-1);}'),('indice = 0;','indice=0;output=indice;io=1;emit("output_init",-1);'),('for (i = 0; i < rango; ++i)','for(i=0,wi=i,emit("rebuild_init",-1);cond("rebuild_test",i<rango);++i,wi=i,emit("rebuild_increment",-1))'),('while (conteo[i] > 0) { arreglo[indice++] = (int)i + minimo; --conteo[i]; }','while(cond("bucket_test",conteo[i]>0)){arreglo[indice++]=(int)i+minimo;output=indice;moves++;emit("array_write",-1);--conteo[i];moves++;emit("count_write",-1);}'),('free(conteo);','free(conteo);counts=NULL;frees++;emit("count_free",-1);'),('return ORDENAMIENTO_OK;','iw=ir=io=have_min=have_max=0;emit("sort_return",-1);return ORDENAMIENTO_OK;')]:body=rep(body,old,new)
 native=observer+'\n'+valid+'\n'+helper+'\n'+body+'\nint main(void){\n'
 for idx,values in enumerate(CASES.values()):native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);case_id='+str(idx)+';counts=NULL;have_min=have_max=iw=ih=ir=io=comparisons=moves=allocs=frees=0;emit("initial",-1);if(ordenar_counting_sort(a,count)!=ORDENAMIENTO_OK)return 2;}\n'
 native+='return 0;}\n';(out/'observed.c').write_text(native,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);assert p.returncode==0;(out/'native.jsonl').write_text(p.stdout);obs=[json.loads(x) for x in p.stdout.splitlines()];rows=[];mapping={'entry':'sort_entry','validate_array':'sort_guard','count_init':'count_init','count_fill':'count_fill','count_write':'count_write','return':'sort_return'}
 for idx,(name,values) in enumerate(CASES.items()):
  responses={}
  for mode in ['fast','step_by_step']:
   c=create_app().test_client();c.post('/api/ordenamiento/create-array',json={'values':values});d=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':mode}).get_json();assert d['success'];responses[mode]=d
  d=responses['step_by_step'];steps=d['execution_trace']['steps'];actual=[x for x in obs if x['case']==idx];cursor=0;projection=[]
  for k,s in enumerate(steps):
   token=s['state_after']['trace_token'];j=k if 'instruction_event' in s['debug'] else next(j for j in range(cursor,len(actual)) if actual[j]['token']==mapping[token]);c=actual[j];cursor=j+1
   if 'instruction_event' in s['debug']:
    assert s['debug']['instruction_event']=={key:value for key,value in c.items() if key!='case'}
    assert s['state_snapshot']['items']==actual[max(0,k-1)]['array'] and s['state_snapshot']['auxiliary_array']==actual[max(0,k-1)]['conteo']
    assert (s['pedagogy']['condition']['result'] if s['pedagogy']['condition'] else None)==c['condition']
   assert c['array']==s['state_after']['items'];aux=s['state_after'].get('auxiliary_array');projection.append(dict(runtime_index=k,native_index=j,token=token,array_match=True,auxiliary_native=c['conteo'],auxiliary_runtime=aux,metrics_native={'comparisons':c['comparisons'],'moves':c['moves'],'swaps':0},metrics_runtime=s['state_after']['metrics']))
  assert actual[-1]['array']==d['visual_state']['items']==sorted(values)
  row=dict(case=name,native_observations=len(actual),runtime_steps=len(steps),unrepresented_observations=len(actual)-len(steps),native_comparisons=actual[-1]['comparisons'],native_moves=actual[-1]['moves'],runtime_metrics=d['result']['metrics'],native_allocations=actual[-1]['allocations'],native_frees=actual[-1]['frees'],final_array_match=True,instruction_fidelity=len(steps)==len(actual));rows.append(row);(out/(name+'.json')).write_text(json.dumps(dict(input=values,native=actual,response=d,fast_response=responses['fast'],projection=projection),ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(rows=rows,native_observations=sum(r['native_observations'] for r in rows),runtime_steps=sum(r['runtime_steps'] for r in rows),C_H_hashes={ext:hashlib.sha256((out/('tad_ordenamiento.'+ext)).read_bytes()).hexdigest() for ext in ['c','h']},move_definition='Explicit data writes: ++conteo, arreglo[indice++]=..., --conteo. Scalar bound assignments and libc calloc zeroing not charged.',instruction_fidelity=all(x['instruction_fidelity'] for x in rows));(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
if __name__=='__main__':print(json.dumps(audit(sys.argv[1])))
