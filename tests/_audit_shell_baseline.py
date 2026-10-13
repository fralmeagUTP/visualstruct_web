"""LOW actual Shell C baseline, preserving causal gaps as findings."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from _audit_sorting_c_source import function_body,replace_once as rep
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS
CASES={'single':[7],'ordered':[1,2,3,4],'reverse':[4,3,2,1],'duplicates':[2,2,2],'negative':[-3,0,-1,0],'extremes':[2147483647,-2147483648,0]}
UI_CASES={name:CASES[name] for name in ['ordered','reverse','negative']}
def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);app=create_app();client=app.test_client();hashes={}
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(out/('tad_ordenamiento.'+ext)).write_bytes(r.data);hashes[ext]=hashlib.sha256(r.data).hexdigest()
 source=(out/'tad_ordenamiento.c').read_text(encoding='utf-8');catalog=[m for m in SORTING_ALGORITHMS if m['id']=='shell'];assert len(catalog)==1 and catalog[0]['c_function']=='ordenar_shell'
 (out/'inventory.json').write_text(json.dumps({'variant':catalog[0],'total_methods':len(SORTING_ALGORITHMS),'new_methods':0},indent=2),encoding='utf-8')
 observer=r'''
#include <stdio.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
static int *root,*pt,ct;static size_t count,*pg,*pi,*pj,cg,ci,cj;
static int hg,hi,hj,ht,comparisons,moves,fixture;
static void emit(const char*t,const char*f,int condition){
 if(pg && hg){cg=*pg;}if(pi && hi){ci=*pi;}if(pj && hj){cj=*pj;}if(pt && ht){ct=*pt;}
 printf("{\"case\":%d,\"event\":{\"token\":\"%s\",\"function\":",fixture,t);
 if(f){printf("\"%s\"",f);}else{printf("null");}
 printf(",\"intervalo\":");if(hg){printf("%zu",cg);}else{printf("null");}
 printf(",\"i\":");if(hi){printf("%zu",ci);}else{printf("null");}
 printf(",\"j\":");if(hj){printf("%zu",cj);}else{printf("null");}
 printf(",\"temporal\":");if(ht){printf("%d",ct);}else{printf("null");}
 printf(",\"comparisons\":%d,\"moves\":%d},\"condition\":",comparisons,moves);
 if(condition<0){printf("null");}else{printf(condition?"true":"false");}
 printf(",\"array\":[");for(size_t k=0;k<count;k++){if(k){printf(",");}printf("%d",root[k]);}puts("]}");
}
static int cond(const char*t,const char*f,int r){if(!strcmp(t,"while_compare")){comparisons++;}emit(t,f,r);return r;}
static int checked(int r){emit("valid_return","arreglo_valido",-1);return cond("sort_guard","ordenar_shell",!r);}
'''
 valid=function_body(source,'arreglo_valido').replace('{','{emit("valid_entry","arreglo_valido",-1);',1);valid=rep(valid,'return arreglo != NULL && n > 0;','return cond("valid_ptr","arreglo_valido",arreglo!=NULL) && cond("valid_n","arreglo_valido",n>0);')
 body=function_body(source,'ordenar_shell').replace('{','{emit("sort_entry","ordenar_shell",-1);',1)
 edits=[('size_t intervalo;','size_t intervalo;pg=&intervalo;emit("gap_declare","ordenar_shell",-1);'),('if (!arreglo_valido(arreglo, n)) return;','emit("valid_call","ordenar_shell",-1);if(checked(arreglo_valido(arreglo,n))){pg=NULL;emit("guard_return","ordenar_shell",-1);return;}'),('for (intervalo = n / 2; intervalo > 0; intervalo /= 2)','for(intervalo=n/2,hg=1,emit("gap_init","ordenar_shell",-1);cond("gap_test","ordenar_shell",intervalo>0);intervalo/=2,emit("gap_divide","ordenar_shell",-1))'),('size_t i;','size_t i;pi=&i;hi=0;emit("i_declare","ordenar_shell",-1);'),('for (i = intervalo; i < n; ++i)','for(i=intervalo,hi=1,emit("i_init","ordenar_shell",-1);cond("i_test","ordenar_shell",i<n);++i,emit("i_increment","ordenar_shell",-1))'),('int temporal = arreglo[i];','int temporal=arreglo[i];pt=&temporal;ht=1;moves++;emit("temp_take","ordenar_shell",-1);'),('size_t j = i;','size_t j=i;pj=&j;hj=1;emit("j_init","ordenar_shell",-1);'),('while (j >= intervalo && arreglo[j - intervalo] > temporal)','while(cond("while_test","ordenar_shell",cond("while_left","ordenar_shell",j>=intervalo) && cond("while_compare","ordenar_shell",arreglo[j-intervalo]>temporal)))'),('arreglo[j] = arreglo[j - intervalo];','arreglo[j]=arreglo[j-intervalo];moves++;emit("shift","ordenar_shell",-1);'),('j -= intervalo;','j-=intervalo;emit("j_subtract","ordenar_shell",-1);'),('arreglo[j] = temporal;','arreglo[j]=temporal;moves++;emit("temp_write","ordenar_shell",-1);')]
 for old,new in edits:body=rep(body,old,new)
 body=rep(body,'\t\t}\n\t}','\t\tpt=NULL;pj=NULL;ht=hj=0;emit("inner_body_exit","ordenar_shell",-1);}\n\tpi=NULL;hi=0;emit("gap_body_exit","ordenar_shell",-1);}')
 body=body[:-1]+'pg=NULL;}\n';native=observer+'\n'+valid+'\n'+body+'\nint main(void){\n'
 def setup(index):return f'fixture={index};hg=hi=hj=ht=comparisons=moves=0;pg=pi=pj=NULL;pt=NULL;emit("initial",NULL,-1);'
 for index,values in enumerate(CASES.values()):native+='{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);'+setup(index)+'ordenar_shell(a,count);emit("sort_return","ordenar_shell",-1);}\n'
 native+='{int a=42;root=&a;count=0;'+setup(6)+'ordenar_shell(&a,0);}\n{root=NULL;count=0;'+setup(7)+'ordenar_shell(NULL,1);}\nreturn 0;}\n'
 (out/'observed.c').write_text(native,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(p.stdout);assert p.returncode==0,p.stderr;observations=[json.loads(line) for line in p.stdout.splitlines()];rows=[]
 mapping={'entry':'sort_entry','validate_array':'valid_return','gap':'gap_test','take_temp':'j_init','gap_compare':'while_compare','gap_shift':'shift','gap_insert':'temp_write','return':'sort_return'}
 for index,(name,values) in enumerate(CASES.items()):
  responses={}
  for mode in ['fast','step_by_step']:
   cl=app.test_client();cl.post('/api/ordenamiento/create-array',json={'values':values});responses[mode]=cl.post('/api/ordenamiento/run',json={'algorithm_id':'shell','mode':mode}).get_json();assert responses[mode]['success']
  d=responses['step_by_step'];steps=d['execution_trace']['steps'];actual=[r for r in observations if r['case']==index];assert actual[-1]['array']==sorted(values)==d['visual_state']['items']==responses['fast']['visual_state']['items'];m=d['result']['metrics'];assert m['comparisons']==actual[-1]['event']['comparisons'] and m['moves']==actual[-1]['event']['moves'] and m['swaps']==0
  cursor=0;projection=[]
  for k,step in enumerate(steps):
   token=step['state_after']['trace_token']
   if 'instruction_event' in step['debug']:
    wanted=token;ci=k;c=actual[ci];assert step['debug']['instruction_event']==c['event']
    assert step['state_snapshot']['items']==actual[max(0,ci-1)]['array']
    assert (step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)==c['condition'] and step['debug']['console_events']==[]
   else:
    wanted=mapping[token];ci=next(j for j in range(cursor,len(actual)) if actual[j]['event']['token']==wanted);c=actual[ci]
   cursor=ci+1;assert c['array']==step['state_after']['items']
   variables={v['name']:v for v in step['pedagogy']['variables']};missing=[local for local in ([] if wanted=='sort_return' else ['intervalo','i','j','temporal']) if c['event'][local] is not None and (local not in variables or variables[local]['value']!=c['event'][local])]
   projection.append({'runtime_index':k,'native_index':ci,'token':token,'array_matches':True,'missing_or_wrong_locals':missing,'condition_native':c['condition'],'condition_runtime':step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None})
  short=[k for k,r in enumerate(actual) if r['event']['token']=='while_left' and r['condition'] is False];assert all(actual[k+1]['event']['token']=='while_test' for k in short)
  gaps=[r['event']['intervalo'] for r in actual if r['event']['token']=='gap_test' and r['condition']];assert gaps==([2,1] if len(values)==4 else [1] if len(values)>1 else [])
  rows.append({'case':name,'native_observations':len(actual),'runtime_steps':len(steps),'unrepresented_observations':len(actual)-len(steps),'missing_local_frames':sum(bool(p['missing_or_wrong_locals']) for p in projection),'final_array_metrics_match':True,'comparisons':m['comparisons'],'moves':m['moves'],'gaps':gaps,'shortcircuits':len(short),'shifts':sum(r['event']['token']=='shift' for r in actual),'instruction_fidelity':len(actual)==len(steps) and all('instruction_event' in s['debug'] for s in steps)})
  (out/(name+'.json')).write_text(json.dumps({'input':values,'native':actual,'response':d,'fast_response':responses['fast'],'projection':projection},ensure_ascii=False,indent=2),encoding='utf-8')
 guards=[r for r in observations if r['case']>=6];assert not any(r['event']['token']=='valid_n' for r in guards if r['case']==7);assert not any(r['event']['token'] in {'temp_take','shift','gap_init'} for r in guards)
 empty=app.test_client().post('/api/ordenamiento/run',json={'algorithm_id':'shell'}).get_json();assert not empty['success'] and all(h['operation']!='run' for h in empty['history'])
 report={'rows':rows,'C_H_hashes':hashes,'native_observations':sum(r['native_observations'] for r in rows),'runtime_steps':sum(r['runtime_steps'] for r in rows),'native_guard_cases':2,'native_guard_observations':len(guards),'empty_API_rejected':True,'strict_C17':True,'instruction_fidelity':all(r['instruction_fidelity'] for r in rows)};(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
if __name__=='__main__':print(json.dumps(audit(sys.argv[1])))
