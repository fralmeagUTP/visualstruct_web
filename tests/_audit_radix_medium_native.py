"""Canonical Radix MEDIUM finite C-event and declared-memory observation gate."""
from pathlib import Path
import json,subprocess,shutil,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from _audit_radix_baseline_low import CASES
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.domain.sorting.radix_instructions import RadixExecutionFailure,SimulatedRadixAllocationFailure
from app.services.radix_trace_service import RadixPageSource
from app.services.sorting_structure_service import SortingStructureService
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-instructions';N=E/'native-expanded';N.mkdir(exist_ok=True)
L=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-baseline-low/native'
s=(L/'observed.c').read_text(encoding='utf-8')
s=s.replace('static int *root;', 'static int wrapper_declared,helper_declared,negative_status,positive_status,output_status,have_magnitude;static uint32_t obs_magnitude;static int block_kind,have_index;\nstatic int *root;')
s=s.replace('if(p==obs_neg)obs_neg=NULL;', 'if(p==obs_neg){obs_neg=NULL;negative_status=4;}').replace('if(p==obs_pos)obs_pos=NULL;', 'if(p==obs_pos){obs_pos=NULL;positive_status=4;}').replace('if(p==obs_out)obs_out=NULL;', 'if(p==obs_out){obs_out=NULL;output_status=4;}')
needle='scalar("return_status",status>=0,(unsigned long long)status);printf("}\\n");'
extra=r'''scalar("return_status",status>=0,(unsigned long long)status);
 printf(",\"typed_observation\":{\"wrapper_declared\":%s,\"helper_declared\":%s,\"negative_status\":%d,\"positive_status\":%d,\"output_status\":%d,\"helper_n\":",wrapper_declared?"true":"false",helper_declared?"true":"false",negative_status,positive_status,output_status);if(helper_active)printf("%zu",work_n);else printf("null");
 printf(",\"helper_alias\":");if(helper_active)printf(obs_work==obs_neg?"\"negative\"":"\"positive\"");else printf("null");
 scalar("magnitud",have_magnitude,obs_magnitude);
 printf(",\"negative_initialized\":");if(obs_neg){printf("[");for(size_t j=0;j<root_n;j++){if(j)printf(",");printf(j<ng?"true":"false");}printf("]");}else printf("null");
 printf(",\"positive_initialized\":");if(obs_pos){printf("[");for(size_t j=0;j<root_n;j++){if(j)printf(",");printf(j<pg?"true":"false");}printf("]");}else printf("null");
 printf(",\"output_initialized\":");if(obs_out){printf("[");for(size_t j=0;j<work_n;j++){if(j)printf(",");printf(output_mask[j]?"true":"false");}printf("]");}else printf("null");
 printf("}}\n");'''
assert needle in s;s=s.replace(needle,extra)
s=s.replace('helper_active=have_di=have_value=have_digit=0;obs_counts=NULL;', 'helper_active=helper_declared=have_di=have_value=have_digit=0;obs_counts=NULL;')
s=s.replace('wrapper_active=have_wi=have_max=have_exp=0;emit(', 'wrapper_active=wrapper_declared=have_wi=have_max=have_exp=have_magnitude=0;emit(')
s=s.replace('obs_counts=conteo;memset(output_mask', 'obs_counts=conteo;helper_declared=1;output_status=1;memset(output_mask')
s=s.replace('obs_out=salida;if(salida)', 'obs_out=salida;output_status=salida?3:2;if(salida)')
s=s.replace('size_t cant_negativos=0,cant_positivos=0,i,indice;emit(', 'size_t cant_negativos=0,cant_positivos=0,i,indice;wrapper_declared=1;negative_status=positive_status=1;emit(')
s=s.replace('obs_neg=negativos;emit(', 'obs_neg=negativos;negative_status=negativos?3:2;emit(').replace('obs_pos=positivos;emit(', 'obs_pos=positivos;positive_status=positivos?3:2;emit(')
s=s.replace('uint32_t magnitud=negativos[i-1];emit(', 'uint32_t magnitud=negativos[i-1];obs_magnitude=magnitud;have_magnitude=1;emit(')
s=s.replace('--i,wi=i,emit("negative_join_decrement"', '--i,wi=i,have_magnitude=0,emit("negative_join_decrement"')
s=s.replace('root=a;root_n=n;', 'wrapper_declared=helper_declared=negative_status=positive_status=output_status=have_magnitude=0;root=a;root_n=n;')

s=s.replace('helper_active=1;obs_work=arreglo;', '_Static_assert(_Generic(arreglo,uint32_t*:1,default:0),"helper uint32 pointer");_Static_assert(_Generic(n,size_t:1,default:0),"helper size_t");_Static_assert(_Generic(exp,uint32_t:1,default:0),"helper uint32 exp");helper_active=1;obs_work=arreglo;')
s=s.replace('wrapper_active=1;emit(', '_Static_assert(_Generic(arreglo,int*:1,default:0),"wrapper int pointer");_Static_assert(_Generic(n,size_t:1,default:0),"wrapper size_t");wrapper_active=1;emit(')
s=s.replace('obs_counts=conteo;helper_declared=1;', '_Static_assert(_Generic(&conteo,size_t(*)[10]:1,default:0),"counts size_t10");_Static_assert(_Generic(salida,uint32_t*:1,default:0),"output uint32 pointer");_Static_assert(_Generic(i,size_t:1,default:0),"helper index size_t");obs_counts=conteo;helper_declared=1;')
s=s.replace('wrapper_declared=1;negative_status=', '_Static_assert(_Generic(negativos,uint32_t*:1,default:0),"negative uint32 pointer");_Static_assert(_Generic(positivos,uint32_t*:1,default:0),"positive uint32 pointer");_Static_assert(_Generic(i,size_t:1,default:0),"wrapper index size_t");wrapper_declared=1;negative_status=')
s=s.replace('obs_max=maximo;obs_exp=exp;have_max=have_exp=1;emit("negative_max_exp_init"', '_Static_assert(_Generic(maximo,uint32_t:1,default:0),"maximum uint32");block_kind=1;obs_max=maximo;obs_exp=exp;have_max=have_exp=1;emit("negative_max_exp_init"')
s=s.replace('obs_max=maximo;obs_exp=exp;have_max=have_exp=1;emit("positive_max_exp_init"', 'block_kind=2;obs_max=maximo;obs_exp=exp;have_max=have_exp=1;emit("positive_max_exp_init"')
s=s.replace('have_max=have_exp=0;emit(', 'block_kind=0;have_max=have_exp=0;emit(').replace('wrapper_active=wrapper_declared=have_wi=have_max=have_exp=have_magnitude=0;', 'block_kind=0;wrapper_active=wrapper_declared=have_wi=have_max=have_exp=have_magnitude=0;')
s=s.replace('indice=0;output_index=indice;', 'indice=0;have_index=1;output_index=indice;')
s=s.replace('obs_value=valor;have_value=1;', '_Static_assert(_Generic(valor,uint32_t:1,default:0),"value uint32");obs_value=valor;have_value=1;').replace('obs_digit=digito;have_digit=1;', '_Static_assert(_Generic(digito,uint32_t:1,default:0),"digit uint32");obs_digit=digito;have_digit=1;').replace('obs_magnitude=magnitud;', '_Static_assert(_Generic(magnitud,uint32_t:1,default:0),"magnitude uint32");obs_magnitude=magnitud;')

s=s.replace('wrapper_declared=helper_declared=negative_status=', 'block_kind=have_index=0;wrapper_declared=helper_declared=negative_status=')

maxvalues=[-2147483648,2147483647]*40
second_cases=[('normal_second',sorted(CASES['normal']),0,50),('negative_second',sorted(CASES['negative_duplicates']),0,51),('extremes_second',sorted(CASES['int32_extremes']),0,52)]
maxblock='{int a[]={'+','.join(map(str,maxvalues))+'};setup(a,80,40,0);int s=ordenar_radixsort(a,80);outcome("maximum",s);}'
pos=s.rindex('return 0;}');more=''.join('{int a[]={'+','.join(map(str,v))+'};setup(a,sizeof(a)/sizeof(a[0]),'+str(case)+',0);int s=ordenar_radixsort(a,root_n);outcome("'+name+'",s);}' for name,v,fault,case in second_cases)
s=s[:pos]+maxblock+more+s[pos:]
s=s.replace(r'printf("}}\n");',r'printf(",\"block\":%d,\"index_initialized\":%s}}\n",block_kind,have_index?"true":"false");')
(N/'observed.c').write_text(s,encoding='utf-8');shutil.copyfile(ROOT/'docs/tads_C/tad_ordenamiento.h',N/'tad_ordenamiento.h')
command=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'observed.c'),'-o',str(N/'observed.exe')]
r=subprocess.run(command,capture_output=True,text=True);(N/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
r=subprocess.run([str(N/'observed.exe')],capture_output=True,text=True);(N/'native.jsonl').write_text(r.stdout,encoding='utf-8');assert r.returncode==0,r.stderr
rows=[json.loads(line) for line in r.stdout.splitlines()];report=[]
status_map={'undeclared':0,'uninitialized':1,'NULL':2,'live':3,'freed':4}
for name,values,fault,case in [(k,v,0,i) for i,(k,v) in enumerate(CASES.items())]+[('fault_'+str(i),[-5,2],i,19+i) for i in range(1,5)]+[('maximum',maxvalues,0,40)]+second_cases:
 def allocator(buffer,capacity,attempt):
  if attempt==fault:raise SimulatedRadixAllocationFailure('private gate injection')
 try:result=SortingInterpreter(values,'radixsort',radix_allocator=allocator if fault else None).run();tape=result['steps'];info=None
 except RadixExecutionFailure as error:tape=error.steps;info=error.error_info
 native=[row for row in rows if row.get('case')==case and 'token'in row];assert len(tape)==len(native),(name,len(tape),len(native))
 for i,row in enumerate(native):
  raw=tape[i];expected={k:v for k,v in row.items() if k not in {'case','typed_observation'}};assert raw['instruction_event']==expected,(name,i)
  ctx=raw['radix_context'];buf=ctx['buffers'];obs=dict(wrapper_declared=ctx['wrapper_declared'],helper_declared=ctx['helper_declared'],negative_status=status_map[buf['negative']['status']],positive_status=status_map[buf['positive']['status']],output_status=status_map[buf['output']['status']],helper_n=ctx['helper_n'] if ctx['helper_active'] else None,helper_alias=ctx['group'] if ctx['helper_active'] else None,magnitud=ctx['magnitud'],block=1 if ctx['block']=='negative' else 2 if ctx['block']=='positive' else 0,index_initialized=ctx['indice'] is not None)
  for key,target in [('negative','negative'),('positive','positive'),('output','output')]:obs[key+'_initialized']=[v is not None for v in buf[target]['cells']] if buf[target]['live'] else None
  assert obs==row['typed_observation'],(name,i,raw['line_token'],obs,row['typed_observation'])
 outcome=next(row for row in rows if row.get('outcome')==name);assert outcome['array']==tape[-1]['array_snapshot'] and outcome['live']==0
 source=RadixPageSource(tape,'',error_info=info);report.append(dict(case=name,events=len(tape),exact_selected_events=True,exact_declared_memory_observations=True,retained_bytes=source.retained_bytes,outcome=outcome))
(N/'report.json').write_text(json.dumps(dict(cases=report,source='extended LOW observer; C/H canonical unchanged',simulated_faults=[1,2,3,4],real_memory_exhaustion=False,platform='int32/uint32/size_t64 GCC C17; finite observations'),indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
