"""Radix LOW native structural/selected-scalar baseline; canonical C/H untouched."""
from pathlib import Path
import json,sys,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
C=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';E=C/'evidence/visible-sorting-radix-baseline-low'
CASES={'single':[7],'normal':[170,45,75,90],'negative_duplicates':[-3,-5,-3,-4],'mixed_outside_four':[170,45,75,-90,802,24,2,66],'zeros':[0,0,0],'eighty_zeros':[0]*80,'int32_extremes':[2147483647,-2147483648,0,-1],'sign_boundary':[-1,0,1]}
PRELUDE=r'''#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include "tad_ordenamiento.h"
static int *root;static size_t root_n;static int case_id,wrapper_active,helper_active,valid_active;
static uint32_t *obs_neg,*obs_pos,*obs_out,*obs_work;static size_t ng,pg,work_n,wi,di,output_index;static uint32_t obs_exp,obs_max,obs_value,obs_digit;static int have_wi,have_di,have_max,have_exp,have_value,have_digit;
static size_t *obs_counts;static unsigned char output_mask[80];
static void *ptrs[256];static int live[256],used,allocs,frees,attempts,fail_at,max_comp,sign_tests,work_writes,count_writes,output_writes,caller_writes;
static int is_live(void*p){for(int i=0;i<used;i++)if(live[i]&&ptrs[i]==p)return 1;return 0;}
static void *qa_malloc(size_t n){attempts++;if(fail_at && attempts==fail_at)return NULL;void*p=malloc(n);if(p){assert(used<256);ptrs[used]=p;live[used++]=1;allocs++;}return p;}
static void qa_free(void*p){if(p){int found=0;for(int i=0;i<used;i++)if(live[i]&&ptrs[i]==p){live[i]=0;found=1;break;}assert(found);if(p==obs_neg)obs_neg=NULL;if(p==obs_pos)obs_pos=NULL;if(p==obs_out)obs_out=NULL;frees++;}free(p);}
static void json_u32(uint32_t*p,size_t n,unsigned char*mask){printf("[");for(size_t i=0;i<n;i++){if(i)printf(",");if(mask&&!mask[i])printf("null");else printf("%u",p[i]);}printf("]");}
static void scalar(const char*name,int have,unsigned long long value){printf(",\"%s\":",name);if(have)printf("%llu",value);else printf("null");}
static void emit(const char*t,int condition,int status){
 printf("{\"case\":%d,\"token\":\"%s\",\"condition\":",case_id,t);if(condition<0)printf("null");else printf(condition?"true":"false");printf(",\"array\":[");for(size_t z=0;z<root_n;z++){if(z)printf(",");printf("%d",root[z]);}printf("]");
 printf(",\"negative\":");if(obs_neg)json_u32(obs_neg,ng,NULL);else printf("null");printf(",\"positive\":");if(obs_pos)json_u32(obs_pos,pg,NULL);else printf("null");printf(",\"digit_output\":");if(obs_out)json_u32(obs_out,work_n,output_mask);else printf("null");printf(",\"counts\":");if(helper_active&&obs_counts){printf("[");for(int z=0;z<10;z++){if(z)printf(",");printf("%zu",obs_counts[z]);}printf("]");}else printf("null");
 printf(",\"wrapper_active\":%s,\"helper_active\":%s,\"valid_active\":%s",wrapper_active?"true":"false",helper_active?"true":"false",valid_active?"true":"false");scalar("wrapper_i",have_wi,wi);scalar("helper_i",have_di,di);scalar("maximo",have_max,obs_max);scalar("exp",have_exp,obs_exp);scalar("valor",have_value,obs_value);scalar("digito",have_digit,obs_digit);
 printf(",\"negative_count\":%zu,\"positive_count\":%zu,\"caller_output_index\":%zu,\"allocations\":%d,\"frees\":%d,\"live\":%d,\"max_value_comparisons\":%d,\"sign_tests\":%d,\"work_writes\":%d,\"count_writes\":%d,\"digit_output_writes\":%d,\"caller_writes\":%d",ng,pg,output_index,allocs,frees,allocs-frees,max_comp,sign_tests,work_writes,count_writes,output_writes,caller_writes);scalar("return_status",status>=0,(unsigned long long)status);printf("}\n");
}
static int cond(const char*t,int value){if(strstr(t,"max_compare"))max_comp++;if(!strcmp(t,"sign_test"))sign_tests++;emit(t,value,-1);return value;}
#define DIG_RETURN(s) do{helper_active=have_di=have_value=have_digit=0;obs_counts=NULL;obs_work=NULL;emit("digit_return",-1,(s));return(s);}while(0)
#define RAD_RETURN(s) do{wrapper_active=have_wi=have_max=have_exp=0;emit("radix_return",-1,(s));return(s);}while(0)
#define malloc qa_malloc
#define free qa_free
'''
def function(text,name):
 import re
 m=re.search(r'(?:static )?int '+name+r'\([^;]*?\)\s*\{',text);assert m,name
 start=m.start();pos=m.end()-1;depth=0
 for end in range(pos,len(text)):
  depth += (text[end]=='{')-(text[end]=='}')
  if depth==0:return start,end+1,text[start:end+1]
 raise AssertionError(name)
def replace(body,old,new):
 assert old in body,old
 return body.replace(old,new,1)
def instrument(text):
 start,end,b=function(text,'arreglo_valido');b=b.replace('{','{valid_active=1;emit("valid_entry",-1,-1);',1);b=replace(b,'return arreglo != NULL && n > 0;','int observed=cond("valid_ptr",arreglo != NULL) && cond("valid_n",n > 0);valid_active=0;emit("valid_return",-1,observed);return observed;');text=text[:start]+b+text[end:]
 start,end,b=function(text,'counting_por_digito');b=b.replace('{','{helper_active=1;obs_work=arreglo;work_n=n;obs_exp=exp;obs_counts=NULL;have_di=have_value=have_digit=0;emit("digit_entry",-1,-1);',1);b=replace(b,'size_t conteo[10] = {0}; uint32_t *salida; size_t i;','size_t conteo[10] = {0}; uint32_t *salida; size_t i;obs_counts=conteo;memset(output_mask,0,sizeof(output_mask));emit("digit_declare",-1,-1);')
 b=replace(b,'salida = (uint32_t *)malloc(n * sizeof(uint32_t));','salida = (uint32_t *)malloc(n * sizeof(uint32_t));obs_out=salida;emit("digit_allocate",-1,-1);')
 b=replace(b,'if (salida == NULL) return ORDENAMIENTO_ERROR;','if(cond("digit_allocation_guard",salida==NULL))DIG_RETURN(ORDENAMIENTO_ERROR);')
 b=replace(b,'for (i = 0; i < n; ++i) ++conteo[(arreglo[i] / exp) % 10];','for(i=0,di=i,have_di=1,emit("digit_fill_init",-1,-1);cond("digit_fill_test",i<n);++i,di=i,emit("digit_fill_increment",-1,-1)){++conteo[(arreglo[i]/exp)%10];count_writes++;emit("digit_frequency_write",-1,-1);}')
 b=replace(b,'for (i = 1; i < 10; ++i) conteo[i] += conteo[i - 1];','for(i=1,di=i,emit("digit_prefix_init",-1,-1);cond("digit_prefix_test",i<10);++i,di=i,emit("digit_prefix_increment",-1,-1)){conteo[i]+=conteo[i-1];count_writes++;emit("digit_prefix_write",-1,-1);}')
 b=replace(b,'for (i = n; i > 0; --i) {','for(i=n,di=i,emit("digit_reverse_init",-1,-1);cond("digit_reverse_test",i>0);--i,di=i,have_value=have_digit=0,emit("digit_reverse_decrement",-1,-1)){')
 b=replace(b,'uint32_t valor = arreglo[i - 1];','uint32_t valor=arreglo[i-1];obs_value=valor;have_value=1;have_digit=0;emit("digit_value_read",-1,-1);')
 b=replace(b,'uint32_t digito = (valor / exp) % 10U;','uint32_t digito=(valor/exp)%10U;obs_digit=digito;have_digit=1;emit("digit_select",-1,-1);')
 b=replace(b,'salida[conteo[digito] - 1] = valor;','salida[conteo[digito]-1]=valor;output_mask[conteo[digito]-1]=1;output_writes++;emit("digit_output_write",-1,-1);')
 b=replace(b,'--conteo[digito];','--conteo[digito];count_writes++;emit("digit_frequency_decrement",-1,-1);')
 b=replace(b,'for (i = 0; i < n; ++i) arreglo[i] = salida[i];','for(i=0,di=i,emit("digit_copy_init",-1,-1);cond("digit_copy_test",i<n);++i,di=i,emit("digit_copy_increment",-1,-1)){arreglo[i]=salida[i];work_writes++;emit("digit_work_copy",-1,-1);}')
 b=replace(b,'free(salida);','free(salida);emit("digit_free",-1,-1);');b=replace(b,'return ORDENAMIENTO_OK;','DIG_RETURN(ORDENAMIENTO_OK);');text=text[:start]+b+text[end:]
 start,end,b=function(text,'ordenar_radixsort');b=b.replace('{','{wrapper_active=1;emit("radix_entry",-1,-1);',1);b=replace(b,'uint32_t *negativos, *positivos; size_t cant_negativos = 0, cant_positivos = 0, i, indice;','uint32_t *negativos, *positivos; size_t cant_negativos=0,cant_positivos=0,i,indice;emit("radix_declare",-1,-1);')
 b=replace(b,'if (!arreglo_valido(arreglo, n)) return ORDENAMIENTO_ERROR;','if(cond("radix_invalid_guard",!arreglo_valido(arreglo,n)))RAD_RETURN(ORDENAMIENTO_ERROR);')
 b=replace(b,'negativos = (uint32_t *)malloc(n * sizeof(uint32_t));','negativos=(uint32_t*)malloc(n*sizeof(uint32_t));obs_neg=negativos;emit("negative_allocate",-1,-1);')
 b=replace(b,'positivos = (uint32_t *)malloc(n * sizeof(uint32_t));','positivos=(uint32_t*)malloc(n*sizeof(uint32_t));obs_pos=positivos;emit("positive_allocate",-1,-1);')
 b=replace(b,'if (negativos == NULL || positivos == NULL) { free(negativos); free(positivos); return ORDENAMIENTO_ERROR; }','if(cond("split_reserve_guard",cond("negative_null",negativos==NULL)||cond("positive_null",positivos==NULL))){free(negativos);emit("negative_free",-1,-1);free(positivos);emit("positive_free",-1,-1);RAD_RETURN(ORDENAMIENTO_ERROR);}')
 b=replace(b,'for (i = 0; i < n; ++i) {','for(i=0,wi=i,have_wi=1,emit("split_init",-1,-1);cond("split_test",i<n);++i,wi=i,emit("split_increment",-1,-1)){')
 b=replace(b,'if (arreglo[i] < 0) negativos[cant_negativos++] = 0U - (uint32_t)arreglo[i];\n\t\telse positivos[cant_positivos++] = (uint32_t)arreglo[i];','if(cond("sign_test",arreglo[i]<0)){negativos[cant_negativos++]=0U-(uint32_t)arreglo[i];ng=cant_negativos;work_writes++;emit("negative_write",-1,-1);}else{positivos[cant_positivos++]=(uint32_t)arreglo[i];pg=cant_positivos;work_writes++;emit("positive_write",-1,-1);}')
 b=replace(b,'if (cant_negativos > 0) {','if(cond("negative_group_guard",cant_negativos>0)){')
 b=replace(b,'uint32_t maximo = negativos[0], exp = 1U;','uint32_t maximo=negativos[0],exp=1U;obs_max=maximo;obs_exp=exp;have_max=have_exp=1;emit("negative_max_exp_init",-1,-1);')
 b=replace(b,'for (i = 1; i < cant_negativos; ++i) if (negativos[i] > maximo) maximo = negativos[i];','for(i=1,wi=i,emit("negative_scan_init",-1,-1);cond("negative_scan_test",i<cant_negativos);++i,wi=i,emit("negative_scan_increment",-1,-1))if(cond("negative_max_compare",negativos[i]>maximo)){maximo=negativos[i];obs_max=maximo;emit("negative_max_assign",-1,-1);}')
 b=replace(b,'if (!counting_por_digito(negativos, cant_negativos, exp)) { free(negativos); free(positivos); return ORDENAMIENTO_ERROR; }','emit("negative_digit_call",-1,-1);if(cond("negative_digit_status",!counting_por_digito(negativos,cant_negativos,exp))){free(negativos);emit("negative_free",-1,-1);free(positivos);emit("positive_free",-1,-1);RAD_RETURN(ORDENAMIENTO_ERROR);}')
 b=replace(b,'if (exp > maximo / 10U) break;','if(cond("negative_exp_guard",exp>maximo/10U)){emit("negative_break",-1,-1);break;}')
 b=replace(b,'exp *= 10U;','exp*=10U;obs_exp=exp;emit("negative_exp_multiply",-1,-1);')
 b=replace(b,'if (cant_positivos > 0) {','have_max=have_exp=0;emit("negative_block_exit",-1,-1);if(cond("positive_group_guard",cant_positivos>0)){')
 b=replace(b,'uint32_t maximo = positivos[0], exp = 1U;','uint32_t maximo=positivos[0],exp=1U;obs_max=maximo;obs_exp=exp;have_max=have_exp=1;emit("positive_max_exp_init",-1,-1);')
 b=replace(b,'for (i = 1; i < cant_positivos; ++i) if (positivos[i] > maximo) maximo = positivos[i];','for(i=1,wi=i,emit("positive_scan_init",-1,-1);cond("positive_scan_test",i<cant_positivos);++i,wi=i,emit("positive_scan_increment",-1,-1))if(cond("positive_max_compare",positivos[i]>maximo)){maximo=positivos[i];obs_max=maximo;emit("positive_max_assign",-1,-1);}')
 b=replace(b,'if (maximo > 0U) for (;;) {','if(cond("positive_nonzero_guard",maximo>0U))for(;;){')
 b=replace(b,'if (!counting_por_digito(positivos, cant_positivos, exp)) { free(negativos); free(positivos); return ORDENAMIENTO_ERROR; }','emit("positive_digit_call",-1,-1);if(cond("positive_digit_status",!counting_por_digito(positivos,cant_positivos,exp))){free(negativos);emit("negative_free",-1,-1);free(positivos);emit("positive_free",-1,-1);RAD_RETURN(ORDENAMIENTO_ERROR);}')
 b=replace(b,'if (exp > maximo / 10U) break;','if(cond("positive_exp_guard",exp>maximo/10U)){emit("positive_break",-1,-1);break;}')
 b=replace(b,'exp *= 10U;','exp*=10U;obs_exp=exp;emit("positive_exp_multiply",-1,-1);')
 b=replace(b,'indice = 0;','have_max=have_exp=0;emit("positive_block_exit",-1,-1);indice=0;output_index=indice;emit("caller_index_init",-1,-1);')
 b=replace(b,'for (i = cant_negativos; i > 0; --i) {','for(i=cant_negativos,wi=i,emit("negative_join_init",-1,-1);cond("negative_join_test",i>0);--i,wi=i,emit("negative_join_decrement",-1,-1)){')
 b=replace(b,'uint32_t magnitud = negativos[i - 1];','uint32_t magnitud=negativos[i-1];emit("negative_magnitude_read",-1,-1);')
 b=replace(b,'arreglo[indice++] = magnitud == (uint32_t)INT_MAX + 1U ? INT_MIN : -(int)magnitud;','arreglo[indice++]=cond("INT_MIN_magnitude_guard",magnitud==(uint32_t)INT_MAX+1U)?INT_MIN:-(int)magnitud;output_index=indice;caller_writes++;emit("negative_caller_write",-1,-1);')
 b=replace(b,'for (i = 0; i < cant_positivos; ++i) arreglo[indice++] = (int)positivos[i];','for(i=0,wi=i,emit("positive_join_init",-1,-1);cond("positive_join_test",i<cant_positivos);++i,wi=i,emit("positive_join_increment",-1,-1)){arreglo[indice++]=(int)positivos[i];output_index=indice;caller_writes++;emit("positive_caller_write",-1,-1);}')
 b=replace(b,'free(negativos); free(positivos);','free(negativos);emit("negative_free",-1,-1);free(positivos);emit("positive_free",-1,-1);')
 b=replace(b,'return ORDENAMIENTO_OK;','RAD_RETURN(ORDENAMIENTO_OK);');return text[:start]+b+text[end:]
SETUP=r'''static void setup(int*a,size_t n,int id,int fault){root=a;root_n=n;case_id=id;wrapper_active=helper_active=valid_active=have_wi=have_di=have_max=have_exp=have_value=have_digit=0;obs_neg=obs_pos=obs_out=obs_work=NULL;obs_counts=NULL;ng=pg=wi=di=output_index=0;used=allocs=frees=attempts=max_comp=sign_tests=work_writes=count_writes=output_writes=caller_writes=0;fail_at=fault;memset(live,0,sizeof(live));emit("initial",-1,-1);}
static void outcome(const char*name,int status){assert(allocs==frees);assert(wrapper_active==0);printf("{\"outcome\":\"%s\",\"case\":%d,\"status\":%d,\"array\":[",name,case_id,status);for(size_t i=0;i<root_n;i++){if(i)printf(",");printf("%d",root[i]);}printf("],\"allocations\":%d,\"frees\":%d,\"live\":%d,\"attempts\":%d}\n",allocs,frees,allocs-frees,attempts);}
'''
def main():
 out=E/'native';out.mkdir(exist_ok=True)
 for ext in ['c','h']:(out/('tad_ordenamiento.'+ext)).write_bytes((ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext)).read_bytes())
 source=(ROOT/'docs/tads_C/tad_ordenamiento.c').read_text(encoding='utf-8');body=[]
 for i,(name,values) in enumerate(CASES.items()):body.append('{int a[]={'+','.join(map(str,values))+'};setup(a,sizeof(a)/sizeof(a[0]),'+str(i)+',0);int s=ordenar_radixsort(a,root_n);outcome("'+name+'",s);}')
 for i,fault in enumerate([1,2,3,4]):body.append('{int a[]={-5,2};setup(a,2,'+str(20+i)+','+str(fault)+');int s=ordenar_radixsort(a,2);outcome("fault_'+str(fault)+'",s);}')
 body+=['{int a[]={5};setup(a,0,30,0);int s=ordenar_radixsort(a,0);assert(a[0]==5);outcome("empty",s);}','{setup(NULL,0,31,0);int s=ordenar_radixsort(NULL,2);outcome("null",s);}']
 code=PRELUDE+instrument(source)+'\n#undef malloc\n#undef free\n'+SETUP+'int main(void){_Static_assert(sizeof(int)==4,"int32");_Static_assert(sizeof(size_t)==8,"size_t64");'+''.join(body)+'return 0;}'
 # is_live is intentionally used only on live output allocations, never freed pointers.
 code=code.replace('obs_out=salida;emit','obs_out=salida;if(salida)assert(is_live(salida));emit')
 (out/'observed.c').write_text(code,encoding='utf-8');cc=shutil.which('gcc');cmd=[cc,'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=20);(out/'native.jsonl').write_text(p.stdout,encoding='utf-8');assert p.returncode==0,p.stderr
 data=[json.loads(l) for l in p.stdout.splitlines()];outcomes={x['outcome']:x for x in data if 'outcome'in x};rows=[]
 for i,(name,values) in enumerate(CASES.items()):
  events=[x for x in data if x.get('case')==i and 'token'in x];native=outcomes[name];assert native['status']==1 and native['array']==sorted(values) and native['live']==0
  app=create_app();c=app.test_client();c.post('/api/ordenamiento/create-array',json={'values':values});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'radixsort'});before=c.get('/api/ordenamiento/state').get_json();response=c.post('/api/ordenamiento/run',json={'algorithm_id':'radixsort','mode':'step_by_step'});assert response.status_code==200;d=response.get_json();t=d['execution_trace'];frames=t.get('steps',[])
  assert d['result']['array']==native['array'];row=dict(case=name,input=values,native_events=len(events),API_frames=len(frames),events_missing=len(events)-len(frames),result_equal=True,allocations=native['allocations'],frees=native['frees'],live=native['live'],helper_calls=sum(e['token']=='digit_entry' for e in events),API_typed_events=sum('instruction_event'in f['debug'] for f in frames),API_fictional_console_events=sum(len(f['debug'].get('console_events',[])) for f in frames),native_write_classes={k:events[-1][k] for k in ['work_writes','count_writes','digit_output_writes','caller_writes','max_value_comparisons','sign_tests']},API_metrics=d['result']['metrics'])
  (out/(name+'.json')).write_text(json.dumps(dict(case=row,native=events,outcome=native,before=before,response=d),ensure_ascii=False,separators=(',',':')),encoding='utf-8');rows.append(row)
 faults=[outcomes[n] for n in ['fault_1','fault_2','fault_3','fault_4','empty','null']]
 for f in faults:assert f['status']==0 and f['live']==0 and f['allocations']==f['frees'] and f['array']==([-5,2] if f['outcome'].startswith('fault') else [])
 (out/'report.json').write_text(json.dumps(dict(rows=rows,faults=faults,scope='Native statement/control structural and selected scalar snapshots. Full typed locals/scopes/order conformance remains open. Write classes not a silently changed metrics contract. Faults are isolated injection, no actual OOM. Observed int32/size_t64 only.'),indent=2),encoding='utf-8');return rows
if __name__=='__main__':print(json.dumps(main(),indent=2))
