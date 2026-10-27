"""LOW bounded native baseline for the existing insertion implementation."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from _audit_sorting_c_source import function_body,replace_once as rep
CASES={'single':[7],'ordered':[1,2],'reverse':[2,1],'duplicates':[2,2],'negative':[-3,0,-1,0],'extremes':[2147483647,-2147483648,0]}


def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);app=create_app();client=app.test_client();hashes={}
 for kind,ext in [('source','c'),('header','h')]:
  response=client.get('/help/source/sorting_array/'+kind);assert response.status_code==200
  (out/('tad_ordenamiento.'+ext)).write_bytes(response.data);hashes[ext]=hashlib.sha256(response.data).hexdigest()
 source=(out/'tad_ordenamiento.c').read_text(encoding='utf-8')
 observer=r'''
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
static int *root,*pk,key;static size_t count,*pi,*pj,ci,cj;
static int has_i,has_j,has_key,comparisons,moves,fixture;
static void emit(const char*token,const char*function,int condition){
 if(pi && has_i){ci=*pi;}if(pj && has_j){cj=*pj;}if(pk && has_key){key=*pk;}
 printf("{\"case\":%d,\"event\":{\"token\":\"%s\",\"function\":",fixture,token);
 if(function){printf("\"%s\"",function);}else{printf("null");}
 printf(",\"i\":");if(has_i){printf("%zu",ci);}else{printf("null");}
 printf(",\"j\":");if(has_j){printf("%zu",cj);}else{printf("null");}
 printf(",\"clave\":");if(has_key){printf("%d",key);}else{printf("null");}
 printf(",\"comparisons\":%d,\"moves\":%d},\"condition\":",comparisons,moves);
 if(condition<0){printf("null");}else{printf(condition?"true":"false");}
 printf(",\"array\":[");for(size_t k=0;k<count;k++){if(k){printf(",");}printf("%d",root[k]);}puts("]}");
}
static int cond(const char*t,const char*f,int r){if(!strcmp(t,"while_compare")){comparisons++;}emit(t,f,r);return r;}
static int checked(int r){emit("valid_return","arreglo_valido",-1);return cond("sort_guard","ordenar_insercion",!r);}
'''
 valid=function_body(source,'arreglo_valido').replace('{','{emit("valid_entry","arreglo_valido",-1);',1)
 valid=rep(valid,'return arreglo != NULL && n > 0;','return cond("valid_ptr","arreglo_valido",arreglo!=NULL) && cond("valid_n","arreglo_valido",n>0);')
 body=function_body(source,'ordenar_insercion').replace('{','{emit("sort_entry","ordenar_insercion",-1);',1)
 body=rep(body,'size_t i;','size_t i;pi=&i;emit("sort_declare","ordenar_insercion",-1);')
 body=rep(body,'if (!arreglo_valido(arreglo, n)) return;','emit("valid_call","ordenar_insercion",-1);if(checked(arreglo_valido(arreglo,n))){pi=NULL;emit("guard_return","ordenar_insercion",-1);return;}')
 body=rep(body,'for (i = 1; i < n; ++i)','for(i=1,has_i=1,emit("outer_init","ordenar_insercion",-1);cond("outer_test","ordenar_insercion",i<n);++i,emit("outer_increment","ordenar_insercion",-1))')
 body=rep(body,'int clave = arreglo[i];','int clave=arreglo[i];pk=&clave;has_key=1;moves++;emit("key_take","ordenar_insercion",-1);')
 body=rep(body,'size_t j = i;','size_t j=i;pj=&j;has_j=1;emit("j_init","ordenar_insercion",-1);')
 body=rep(body,'while (j > 0 && arreglo[j - 1] > clave)','while(cond("while_test","ordenar_insercion",cond("while_left","ordenar_insercion",j>0) && cond("while_compare","ordenar_insercion",arreglo[j-1]>clave)))')
 body=rep(body,'arreglo[j] = arreglo[j - 1];','arreglo[j]=arreglo[j-1];moves++;emit("shift","ordenar_insercion",-1);')
 body=rep(body,'--j;','--j;emit("j_decrement","ordenar_insercion",-1);')
 body=rep(body,'arreglo[j] = clave;','arreglo[j]=clave;moves++;emit("key_write","ordenar_insercion",-1);')
 boundary=body.rfind('\t}');assert boundary!=-1
 # Retire pointers before their lexical block ends; no expired/local uninitialized reads.
 body=body[:boundary]+'pj=NULL;pk=NULL;has_j=has_key=0;emit("body_exit","ordenar_insercion",-1);'+body[boundary:]
 body=body[:-1]+'pi=NULL;}\n'
 native=observer+'\n'+valid+'\n'+body+'\nint main(void){\n'
 for index,values in enumerate(CASES.values()):
  native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);fixture='+str(index)+';has_i=has_j=has_key=comparisons=moves=0;pi=pj=NULL;pk=NULL;emit("initial",NULL,-1);ordenar_insercion(a,count);emit("sort_return","ordenar_insercion",-1);}\n'
 native+='{int a=42;root=&a;count=0;fixture=6;has_i=has_j=has_key=comparisons=moves=0;pi=pj=NULL;pk=NULL;emit("initial",NULL,-1);ordenar_insercion(&a,0);}\n'
 native+='{root=NULL;count=0;fixture=7;has_i=has_j=has_key=comparisons=moves=0;pi=pj=NULL;pk=NULL;emit("initial",NULL,-1);ordenar_insercion(NULL,1);}\nreturn 0;}\n'
 (out/'observed.c').write_text(native,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(p.stdout);assert p.returncode==0,p.stderr
 observations=[json.loads(line) for line in p.stdout.splitlines()];rows=[]
 start=source[:source.index(function_body(source,'ordenar_insercion'))].count('\n');end=start+function_body(source,'ordenar_insercion').count('\n')
 mapping={'entry':'sort_entry','validate_array':'valid_return','take_key':'key_take','while_compare':'while_compare','shift':'shift','insert_key':'key_write','return':'sort_return'}
 for index,(name,values) in enumerate(CASES.items()):
  client=app.test_client();assert client.post('/api/ordenamiento/create-array',json={'values':values}).get_json()['success']
  responses={}
  for mode in ['fast','step_by_step']:
   client=app.test_client();client.post('/api/ordenamiento/create-array',json={'values':values});responses[mode]=client.post('/api/ordenamiento/run',json={'algorithm_id':'insercion','mode':mode}).get_json();assert responses[mode]['success']
  d=responses['step_by_step'];steps=d['execution_trace']['steps'];trace_source=d['execution_trace']['source_code'];trace_body=function_body(trace_source,'ordenar_insercion');start=trace_source[:trace_source.index(trace_body)].count('\n');end=start+trace_body.count('\n');actual=[row for row in observations if row['case']==index]
  assert actual[-1]['array']==sorted(values)==d['visual_state']['items']==responses['fast']['visual_state']['items']
  metrics=d['result']['metrics'];assert metrics['comparisons']==actual[-1]['event']['comparisons'] and metrics['moves']==actual[-1]['event']['moves'] and metrics['swaps']==0
  projection=[];cursor=0
  for runtime_index,step in enumerate(steps):
   token=step['state_after']['trace_token']
   if 'instruction_event' in step['debug']:
    cindex=runtime_index;wanted=token;event=actual[cindex]
    assert step['debug']['instruction_event']==event['event'],(name,runtime_index,event,step['debug'])
    assert step['state_snapshot']['items']==actual[max(0,cindex-1)]['array']
    assert event['condition']==(step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)
    assert step['debug']['console_events']==[]
   else:
    wanted=mapping[token];cindex=next(k for k in range(cursor,len(actual)) if actual[k]['event']['token']==wanted);event=actual[cindex]
   cursor=cindex+1
   assert event['array']==step['state_after']['items'],(name,runtime_index)
   if token=='while_compare':assert event['condition']==step['pedagogy']['condition']['result']
   variables={v['name']:v for v in step['pedagogy']['variables']}
   absent=[local for local in ([] if wanted=='sort_return' else ['i','j','clave']) if event['event'][local] is not None and (local not in variables or variables[local]['value']!=event['event'][local])]
   in_source_scope=token=='initial' and step['line_index'] is None
   if event['event']['function']:
    scope_body=function_body(trace_source,event['event']['function']);scope_start=trace_source[:trace_source.index(scope_body)].count('\n');scope_end=scope_start+scope_body.count('\n')
    in_source_scope=step['line_index'] is not None and scope_start<=step['line_index']<=scope_end
   projection.append({'runtime_index':runtime_index,'native_index':cindex,'token':token,'array_matches':True,'missing_or_wrong_locals':absent,'line_in_sort_scope':in_source_scope,'condition_matches':event['condition']==(step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)})
  zero_short=[k for k,row in enumerate(actual) if row['event']['token']=='while_left' and row['condition'] is False];assert all(actual[k+1]['event']['token']=='while_test' for k in zero_short)
  outside=[r for r in projection if not r['line_in_sort_scope'] and r['token']!='validate_array']
  rows.append({'case':name,'native_observations':len(actual),'runtime_steps':len(steps),'projected_array_differences':0,'final_and_metrics_match':True,'unrepresented_observations':len(actual)-len(steps),'missing_local_frames':sum(bool(r['missing_or_wrong_locals']) for r in projection),'incorrect_source_frames':len(outside),'j_zero_shortcircuits':len(zero_short),'comparisons':metrics['comparisons'],'moves':metrics['moves'],'shifts':sum(r['event']['token']=='shift' for r in actual),'instruction_fidelity':len(actual)==len(steps) and all('instruction_event' in step['debug'] for step in steps)})
  (out/(name+'.json')).write_text(json.dumps({'input':values,'native':actual,'response':d,'fast_response':responses['fast'],'projection':projection,'sort_scope':[start,end]},ensure_ascii=False,indent=2),encoding='utf-8')
 guards=[r for r in observations if r['case']>=6];assert not any(r['event']['token']=='valid_n' for r in guards if r['case']==7);assert not any(r['event']['token'] in {'key_take','j_init','while_compare','shift'} for r in guards)
 empty=app.test_client();h=empty.get('/api/ordenamiento/state').get_json()['history'];rejected=empty.post('/api/ordenamiento/run',json={'algorithm_id':'insercion','mode':'step_by_step'}).get_json();assert not rejected['success'] and rejected['history']==h
 report={'rows':rows,'C_H_hashes':hashes,'native_observations':sum(r['native_observations'] for r in rows),'runtime_steps':sum(r['runtime_steps'] for r in rows),'native_guard_cases':2,'native_guard_observations':len(guards),'api_empty_rejected':True,'strict_C17':True,'instruction_fidelity':all(row['instruction_fidelity'] for row in rows),'scope':'Six finite <=4 entries; no tagged-stability or full insertion signoff; native-only guards separate from API empty rejection'};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');return report

if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
