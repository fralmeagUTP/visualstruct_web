"""Actual downloaded C observation; bounded Selection only."""
from pathlib import Path
import sys,re,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
CASES={'single':[7],'ordered':[1,2],'reverse':[2,1],'duplicates':[2,2],'negative':[-3,0,-1,0],'extremes':[2147483647,-2147483648,0]}
def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);app=create_app();client=app.test_client();hashes={}
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(out/('tad_ordenamiento.'+ext)).write_bytes(r.data);hashes[ext]=hashlib.sha256(r.data).hexdigest()
 source=(out/'tad_ordenamiento.c').read_text(encoding='utf-8')
 from _audit_sorting_c_source import function_body
 def body(name): return function_body(source,name)
 observer=r'''
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
static int *root,*pa,*pb,*pt;static size_t count,*pi,*pj,*pm,ci,cj,cm;
static int has_i,has_j,has_m,has_t,ct,comparisons,swaps,moves,fixture;
static void emit(const char *token,const char *function,int condition){
 if(pi && has_i){ci=*pi;}if(pj && has_j){cj=*pj;}if(pm && has_m){cm=*pm;}if(pt && has_t){ct=*pt;}
 printf("{\"case\":%d,\"event\":{\"token\":\"%s\",\"function\":",fixture,token);
 if(function){printf("\"%s\"",function);}else{printf("null");}
 printf(",\"i\":");if(has_i){printf("%zu",ci);}else{printf("null");}
 printf(",\"j\":");if(has_j){printf("%zu",cj);}else{printf("null");}
 printf(",\"indice_menor\":");if(has_m){printf("%zu",cm);}else{printf("null");}
 printf(",\"temporal\":");if(pt && has_t){printf("%d",ct);}else{printf("null");}
 printf(",\"a\":");if(pa){printf("%td",pa-root);}else{printf("null");}
 printf(",\"b\":");if(pb){printf("%td",pb-root);}else{printf("null");}
 printf(",\"comparisons\":%d,\"swaps\":%d,\"moves\":%d},\"condition\":",comparisons,swaps,moves);
 if(condition<0){printf("null");}else{printf(condition?"true":"false");}
 printf(",\"array\":[");for(size_t k=0;k<count;k++){if(k){printf(",");}printf("%d",root[k]);}puts("]}");
}
static int cond(const char*t,const char*f,int r){if(!strcmp(t,"compare_min")){comparisons++;}emit(t,f,r);return r;}
static int checked(int r){emit("valid_return","arreglo_valido",-1);return cond("sort_guard","ordenar_seleccion",!r);}
'''
 valid=body('arreglo_valido').replace('{','{emit("valid_entry","arreglo_valido",-1);',1).replace('return arreglo != NULL && n > 0;','return cond("valid_ptr","arreglo_valido",arreglo!=NULL) && cond("valid_n","arreglo_valido",n>0);')
 swap=body('intercambiar').replace('{','{pa=a;pb=b;emit("swap_entry","intercambiar",-1);',1).replace('int temporal;','int temporal;pt=&temporal;has_t=0;emit("swap_declare","intercambiar",-1);').replace('if (a == NULL || b == NULL)','if (cond("swap_guard","intercambiar",a==NULL || b==NULL))').replace('temporal = *a;','temporal=*a;has_t=1;moves++;emit("swap_temp","intercambiar",-1);').replace('*a = *b;','*a=*b;moves++;emit("swap_assign_a","intercambiar",-1);').replace('*b = temporal;','*b=temporal;moves++;swaps++;emit("swap_assign_b","intercambiar",-1);')
 sort=body('ordenar_seleccion')
 from _audit_sorting_c_source import replace_once as rep
 sort=rep(sort,'{','{emit("sort_entry","ordenar_seleccion",-1);') if sort.count('{')==1 else sort.replace('{','{emit("sort_entry","ordenar_seleccion",-1);',1)
 sort=rep(sort,'size_t i, j, indice_menor;','size_t i,j,indice_menor;pi=&i;pj=&j;pm=&indice_menor;emit("sort_declare","ordenar_seleccion",-1);')
 sort=rep(sort,'if (!arreglo_valido(arreglo, n)) return;','emit("valid_call","ordenar_seleccion",-1);if(checked(arreglo_valido(arreglo,n))){pi=pj=pm=NULL;emit("guard_return","ordenar_seleccion",-1);return;}')
 sort=rep(sort,'for (i = 0; i + 1 < n; ++i)','for(i=0,has_i=1,emit("outer_init","ordenar_seleccion",-1);cond("outer_test","ordenar_seleccion",i+1<n);++i,emit("outer_increment","ordenar_seleccion",-1))')
 sort=rep(sort,'indice_menor = i;','indice_menor=i;has_m=1;emit("min_init","ordenar_seleccion",-1);')
 sort=rep(sort,'for (j = i + 1; j < n; ++j)','for(j=i+1,has_j=1,emit("inner_init","ordenar_seleccion",-1);cond("inner_test","ordenar_seleccion",j<n);++j,emit("inner_increment","ordenar_seleccion",-1))')
 sort=rep(sort,'if (arreglo[j] < arreglo[indice_menor]) indice_menor = j;','if(cond("compare_min","ordenar_seleccion",arreglo[j]<arreglo[indice_menor])){indice_menor=j;emit("min_set","ordenar_seleccion",-1);}')
 sort=rep(sort,'if (indice_menor != i) intercambiar(&arreglo[i], &arreglo[indice_menor]);','if(cond("swap_decision","ordenar_seleccion",indice_menor!=i)){emit("swap_call","ordenar_seleccion",-1);intercambiar(&arreglo[i],&arreglo[indice_menor]);pa=pb=pt=NULL;has_t=0;emit("swap_return","intercambiar",-1);emit("swap_resume","ordenar_seleccion",-1);}')
 # Observe real outer-body completion before its closing brace.
 split=sort.rfind('\t}')
 assert split!=-1
 sort=sort[:split]+'emit("outer_complete","ordenar_seleccion",-1);'+sort[split:]
 sort=sort[:-1]+'pi=pj=pm=NULL;}\n'
 native=observer+'\n'+swap+'\n'+valid+'\n'+sort+'\nint main(void){\n'
 for idx,values in enumerate(CASES.values()):
  native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);fixture='+str(idx)+';has_i=has_j=has_m=has_t=comparisons=swaps=moves=0;pi=pj=pm=NULL;pa=pb=pt=NULL;emit("initial",NULL,-1);ordenar_seleccion(a,count);emit("sort_return","ordenar_seleccion",-1);}\n'
 native+='{int a=42;root=&a;count=0;fixture=6;has_i=has_j=has_m=has_t=comparisons=swaps=moves=0;pi=pj=pm=NULL;emit("initial",NULL,-1);ordenar_seleccion(&a,0);}\n'
 native+='{root=NULL;count=0;fixture=7;has_i=has_j=has_m=has_t=comparisons=swaps=moves=0;pi=pj=pm=NULL;emit("initial",NULL,-1);ordenar_seleccion(NULL,1);}\nreturn 0;}\n'
 (out/'observed.c').write_text(native,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(p.stdout);assert p.returncode==0,p.stderr
 observations=[json.loads(line) for line in p.stdout.splitlines()];rows=[]
 for idx,(name,values) in enumerate(CASES.items()):
  client=app.test_client();assert client.post('/api/ordenamiento/create-array',json={'values':values}).get_json()['success'];d=client.post('/api/ordenamiento/run',json={'algorithm_id':'seleccion','mode':'step_by_step'}).get_json();assert d['success'],d
  steps=d['execution_trace']['steps'];actual=[r for r in observations if r['case']==idx];assert len(actual)==len(steps),(name,len(actual),len(steps))
  for k,(c,step) in enumerate(zip(actual,steps)):
   assert c['event']==step['debug']['instruction_event'],(name,k,c,step['debug'])
   assert c['array']==step['state_after']['items'],(name,k)
   assert c['condition']==(step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None),(name,k)
   assert step['state_snapshot']['items']==actual[max(0,k-1)]['array'];assert step['line_index'] is not None or k==0;assert step['debug']['console_events']==[]
  (out/(name+'.json')).write_text(json.dumps({'input':values,'native':actual,'response':d},ensure_ascii=False,indent=2),encoding='utf-8');rows.append({'case':name,'instructions':len(steps),'comparisons':d['result']['metrics']['comparisons'],'swaps':d['result']['metrics']['swaps'],'moves':d['result']['metrics']['moves'],'differences':0})
 empty=app.test_client();h=empty.get('/api/ordenamiento/state').get_json()['history'];r=empty.post('/api/ordenamiento/run',json={'algorithm_id':'seleccion','mode':'step_by_step'}).get_json();assert not r['success'] and r['history']==h
 guards=[r for r in observations if r['case']>=6];assert not any(r['event']['token']=='valid_n' for r in guards if r['case']==7);assert all(r['event']['token'] not in {'compare_min','min_init','swap_call','swap_entry'} for r in guards)
 report={'rows':rows,'hashes':hashes,'native_guard_cases':2,'api_empty_rejected':True,'instruction_rows':sum(r['instructions'] for r in rows),'native_empty_null_rows':len(guards),'differences':0,'strict_c17':True,'scope':'6 finite cases <=4 values; no NULL swap path; no tagged stability proof; actual main verified separately from native instruction oracle'};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return report
if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
