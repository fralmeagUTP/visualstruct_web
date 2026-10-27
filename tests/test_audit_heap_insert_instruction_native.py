"""Independent C insert call graph, partial writes and realloc publication."""
from pathlib import Path
import json,re,shutil,subprocess
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
CASES=[([],7,False),([7],7,False),([20,30,40,50],5,False),([1,3,5],100,False),([2147483647,0],-2147483648,False),(list(range(19)),-1,False),(list(range(20)),-1,False),(list(range(20)),0,False),(list(range(20)),-1,True)]
HELPER=r'''
static bool comparar(TipoMonticulo tipo,int a,int b);
static int active,case_id,failure,depth,stack[8],compare_count,swap_count,frame_instance[8];
static int ref,live1,live2,known,old_known,object_capacity,old_capacity,old_values[64];
static int *audit_data;static MonticuloBinario *audit_m;
static int input,objective,ns,nc,ps,pr,os,ov,ui,ups,up_parent,ca,cb,ctype,sa,sb,ts,tv;
static const char *kinds[]={"caller","insert","reserve","up","compare","swap"};
static void audit_enter(int kind){stack[depth]=kind;frame_instance[depth]=kind==4?++compare_count:kind==5?++swap_count:0;depth++;}
static void audit_leave(int kind){depth--;if(kind==2){ns=0;ps=0;}if(kind==3)ups=0;if(kind==5)ts=0;}
static void audit_emit(const char *scope,const char *text,const char *phase,int condition,int returned,int ix,int iy){
 if(!active)return;
 printf("AUDIT {\"case\":%d,\"scope\":\"%s\",\"text\":\"%s\",\"phase\":\"%s\",\"condition\":%d,\"returned\":%d,\"quantity\":%d,\"capacity\":%d,\"reference\":%d,\"live1\":%d,\"live2\":%d,\"known\":%d,\"object_capacity\":%d,\"objective\":%d,\"ns\":%d,\"nc\":%d,\"ps\":%d,\"pr\":%d,\"os\":%d,\"ov\":%d,\"ui\":%d,\"ups\":%d,\"parent\":%d,\"ca\":%d,\"cb\":%d,\"ctype\":%d,\"sa\":%d,\"sb\":%d,\"ts\":%d,\"tv\":%d,\"active_indices\":[",case_id,scope,text,phase,condition,returned,audit_m->cantidad,audit_m->capacidad,ref,live1,live2,known,object_capacity,objective,ns,nc,ps,pr,os,ov,ui,ups,up_parent,ca,cb,ctype,sa,sb,ts,tv);
 if(ix>=0){printf("%d",ix);}if(iy>=0){printf("%s%d",ix>=0?",":"",iy);}printf("],\"frames\":[");
 for(int d=0;d<depth;d++){int k=stack[d];printf("%s{\"kind\":\"%s\",\"id\":\"%s",d?",":"",kinds[k],kinds[k]);if(k>=4)printf("-%d",frame_instance[d]);printf("\",\"params\":{");
  if(k<=3){printf("\"m\":\"M1\"");if(k<=1)printf(",\"valor\":%d",input);if(k==2)printf(",\"capacidad_objetivo\":%d",objective);if(k==3)printf(",\"indice\":%d",ui);}
  if(k==4)printf("\"tipo\":%d,\"a\":%d,\"b\":%d",ctype,ca,cb);
  if(k==5)printf("\"a\":\"&A%d[%d]\",\"b\":\"&A%d[%d]\"",live2?2:1,sa,live2?2:1,sb);
  printf("},\"locals\":{");
  if(k==0&&os){printf("\"ok\":");if(os==1)printf("\"sin inicializar\"");else printf(ov?"true":"false");}
  if(k==2){if(ns){printf("\"nueva_capacidad\":");if(ns==1)printf("\"sin inicializar\"");else printf("%d",nc);}if(ps){printf("%s\"nuevos_datos\":\"%s\"",ns?",":"",ps==1?"sin inicializar":pr==2?"A2":"NULL");}}
  if(k==3&&ups)printf("\"padre\":%d",up_parent);
  if(k==5&&ts)printf("\"temp\":%d",tv);
  printf("}}");
 }printf("],\"array\":[");if(ref>0){for(int i=0;i<known;i++){printf("%s%d",i?",":"",audit_data[i]);}}printf("],\"physical\":[");for(int i=0;i<known;i++){printf("%s%d",i?",":"",audit_data[i]);}printf("],\"historical\":[");if(live2){for(int i=0;i<old_known;i++){printf("%s%d",i?",":"",old_values[i]);}}printf("]}\n");
}
static int audit_condition(const char *s,const char *t,int result){audit_emit(s,t,"condition",result,-2,-1,-1);return result;}
static void *audit_realloc(void *p,size_t n){if(active&&failure)return NULL;if(active){old_known=known;old_capacity=audit_m->capacidad;for(int i=0;i<known;i++){old_values[i]=audit_data[i];}}void *out=realloc(p,n);if(active&&out){audit_data=out;ref=-1;live1=0;live2=1;object_capacity=(int)(n/sizeof(int));}return out;}
static int audit_up_condition(MonticuloBinario *m,int indice,int padre){
 const char *text="while (indice > 0 && comparar(m->tipo, m->datos[indice], m->datos[padre])) {";
 int result=0;if(indice>0){audit_emit("up",text,"call",-2,-2,indice,padre);result=comparar(m->tipo,m->datos[indice],m->datos[padre]);}
 audit_emit("up",text,"condition",indice>0&&result,-2,-1,-1);return indice>0&&result;
}
'''

@pytest.fixture(scope='module')
def heap_insert_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('heap-insert-native');c=create_app().test_client();raw=c.get('/help/source/binary_heap/source').data;header=c.get('/help/source/binary_heap/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(out/('tad_monticulo_binario.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig').replace('\r\n','\n');names={'reserve':'asegurar_capacidad','compare':'comparar','swap':'intercambiar','up':'heapify_up','insert':'monticulo_insertar'};originals={s:CCodeService._extract_function_with_comment(source,n) for s,n in names.items()}
 def body(s):
  code=originals[s];return '\n'.join(code.splitlines()[next(i for i,l in enumerate(code.splitlines()) if re.match(r'(static )?(bool|void) '+names[s]+r'\(',l)):])
 def replace(code,text,new,count=1):return re.sub(r'(?m)^([ \t]*)'+re.escape(text),lambda m:m.group(1)+new,code,count=count)
 def log(s,text,phase,condition='-2',result='-2',ix='-1',iy='-1'):return 'audit_emit('+json.dumps(s)+','+json.dumps(text)+','+json.dumps(phase)+','+','.join([condition,result,ix,iy])+');'
 def cond(s,text,expr):return 'audit_condition('+json.dumps(s)+','+json.dumps(text)+','+expr+')'
 ids={'insert':1,'reserve':2,'up':3,'compare':4,'swap':5}
 for scope in names:
  old=body(scope);new=old;signature=old.splitlines()[0];kind=ids[scope];entry={'insert':'input=valor;','reserve':'objective=capacidad_objetivo;','up':'ui=indice;ups=0;','compare':'ctype=tipo;ca=a;cb=b;','swap':'if(active){sa=(int)(a-audit_data);sb=(int)(b-audit_data);}ts=0;'}[scope]
  new=new.replace('{','{'+entry+f'audit_enter({kind});'+log(scope,signature,'enter'),1)
  if scope=='reserve':
   for text,extra in [('int nueva_capacidad;','ns=1;'),('int *nuevos_datos;','ps=1;')]:new=replace(new,text,text+extra+log(scope,text,'declaration'))
   for text,expr in [('if (m == NULL || capacidad_objetivo <= 0) {','m==NULL||capacidad_objetivo<=0'),('if (m->capacidad >= capacidad_objetivo && m->datos != NULL) {','m->capacidad>=capacidad_objetivo&&m->datos!=NULL'),('while (nueva_capacidad < capacidad_objetivo) {','nueva_capacidad<capacidad_objetivo'),('if (nueva_capacidad > INT_MAX / 2) {','nueva_capacidad>INT_MAX/2'),('if (nuevos_datos == NULL) {','nuevos_datos==NULL')]:new=replace(new,text,('while' if text.startswith('while') else 'if')+'('+cond(scope,text,expr)+'){')
   for text,extra,phase,predicate in [('nueva_capacidad = (m->capacidad > 0) ? m->capacidad : MONTICULO_CAPACIDAD_POR_DEFECTO;','ns=2;nc=nueva_capacidad;','assignment','m->capacidad>0'),('nueva_capacidad *= 2;','nc=nueva_capacidad;','assignment','-2'),('nuevos_datos = (int *)realloc(m->datos, sizeof(int) * (size_t)nueva_capacidad);','ps=2;pr=nuevos_datos?2:0;','allocation','-2'),('m->datos = nuevos_datos;','ref=2;','assignment','-2'),('m->capacidad = nueva_capacidad;','','assignment','-2')]:new=replace(new,text,text+extra+log(scope,text,phase,predicate))
  elif scope=='insert':
   text='if (m == NULL) return false;';new=replace(new,text,'if('+cond(scope,text,'m==NULL')+'){audit_leave(1);'+log(scope,text,'return',result='0')+'return false;}')
   text='if (!asegurar_capacidad(m, m->cantidad + 1)) {';new=replace(new,text,log(scope,text,'call')+'if('+cond(scope,text,'!asegurar_capacidad(m,m->cantidad+1)')+'){')
   text='m->datos[m->cantidad] = valor;';new=replace(new,text,text+'known=m->cantidad+1;'+log(scope,text,'assignment',ix='m->cantidad'))
   text='heapify_up(m, m->cantidad);';new=replace(new,text,log(scope,text,'call')+text+log(scope,text,'resume'))
   text='m->cantidad++;';new=replace(new,text,text+log(scope,text,'assignment'))
  elif scope=='up':
   text='int padre = (indice - 1) / 2;';new=replace(new,text,text+'ups=1;up_parent=padre;'+log(scope,text,'assignment'))
   text='while (indice > 0 && comparar(m->tipo, m->datos[indice], m->datos[padre])) {';new=replace(new,text,'while(audit_up_condition(m,indice,padre)){')
   text='intercambiar(&m->datos[indice], &m->datos[padre]);';new=replace(new,text,log(scope,text,'call')+text+log(scope,text,'resume'))
   for text,extra in [('indice = padre;','ui=indice;'),('padre = (indice - 1) / 2;','up_parent=padre;')]:new=replace(new,text,text+extra+log(scope,text,'assignment'))
  elif scope=='compare':
   text='if (tipo == MONTICULO_MIN) {';new=replace(new,text,'if('+cond(scope,text,'tipo==MONTICULO_MIN')+'){')
  else:
   for text,extra,ix,iy in [('int temp = *a;','ts=1;tv=temp;','sa','-1'),('*a = *b;','','sa','sb'),('*b = temp;','','sb','-1')]:new=replace(new,text,text+extra+log(scope,text,'assignment',ix=ix,iy=iy))
  for text,result in [('return true;','1'),('return false;','0'),('return a < b;','a<b'),('return a > b;','a>b')]:new=replace(new,text,f'audit_leave({kind});'+log(scope,text,'return',result=result)+text,count=0)
  if scope in ['up','swap']:new=new[:-1]+f'audit_leave({kind});'+log(scope,'}','return')+'}'
  assert old in source;source=source.replace(old,new,1)
 source=source.replace('static void intercambiar(',HELPER+'\n#define realloc audit_realloc\nstatic void intercambiar(',1)
 caller='bool ejecutar_insertar(MonticuloBinario *m, int valor) {\n    bool ok = monticulo_insertar(m, valor);\n    return ok;\n}'
 implemented=caller.replace('{','{input=valor;audit_enter(0);'+log('caller',caller.splitlines()[0],'enter'),1)
 text='bool ok = monticulo_insertar(m, valor);';implemented=replace(implemented,text,'os=1;'+log('caller',text,'call')+text+'os=2;ov=ok;'+log('caller',text,'resume'))
 text='return ok;';implemented=replace(implemented,text,'audit_leave(0);'+log('caller',text,'return',result='ok')+text)
 main='\nint main(void){MonticuloBinario m;bool ok;'
 for case,(seed,value,fail) in enumerate(CASES):
  main+='active=0;failure=0;monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join(f'monticulo_insertar(&m,{v});' for v in seed)
  main+=f'case_id={case};audit_m=&m;audit_data=m.datos;object_capacity=m.capacidad;old_known=0;known=m.cantidad;depth=0;compare_count=0;swap_count=0;ns=0;ps=0;os=0;ups=0;ts=0;ref=1;live1=1;live2=0;failure={int(fail)};active=1;ok=ejecutar_insertar(&m,{value});active=0;if(ok!={int(not fail)})return 2;monticulo_destruir(&m);'
 main+='active=0;if(monticulo_insertar(NULL,7))return 3;return 0;}'
 (out/'instrumented.c').write_text(source+'\n'+implemented+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 report={'cases':[{'seed':s,'value':v,'fail':f} for s,v,f in CASES],'events':events,'originals':originals,'caller':caller,'limits':['Real realloc success and deterministic NULL; allocator internals not observed.','Copied initialized prefix and cached old prefix only; no read of original pointer after successful realloc.','Valid MIN product inputs plus raw NULL guard; no arbitrary malformed ownership/out-of-range C int proof.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def injected_insert(original):
 def insert(m,v):return False if m.cantidad>=m.capacidad else original(m,v)
 return insert

@pytest.mark.parametrize('case',range(9))
def test_heap_insert_completed_statements_match_native(heap_insert_native,case,monkeypatch):
 from app.domain.hierarchical import tad_wrappers
 c=create_app().test_client();seed,value,fail=CASES[case]
 for v in seed:assert c.post('/hierarchical/binary_heap/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 if fail:monkeypatch.setattr(tad_wrappers,'monticulo_insertar',injected_insert(tad_wrappers.monticulo_insertar))
 d=c.post('/hierarchical/binary_heap/operate',json={'operation':'insertar','payload':{'value':value}}).json;assert d['success']==(not fail);trace=d['execution_trace'];events=[e for e in heap_insert_native['events'] if e['case']==case];assert len(trace['steps'])==len(events)
 for step,event in zip(trace['steps'],events):
  assert step['line_text'].strip()==event['text'];ped=step['pedagogy'];assert ped['instruction_event']['scope']==event['scope'] and ped['instruction_event']['phase']==event['phase'];state=ped['memory_state']
  assert state['size']==event['quantity'] and state['capacity']==event['capacity'] and state['array']==event['array'] and state['heap_written']==event['known']
  assert state['heap_data_reference']=={-1:'indeterminado (A1 historico)',0:'NULL',1:'A1',2:'A2'}[event['reference']] and state['heap_active_indices']==event['active_indices']
  assert [{'kind':f['kind'],'id':f['id'],'params':f['parameters'],'locals':f['locals']} for f in state['query_frames']]==event['frames']
  live=[o for o in state['heap_allocations'] if o['live']];assert len(live)==1 and live[0]['capacity']==event['object_capacity'];assert [cell['value'] for cell in live[0]['cells'][:event['known']]]==event['physical']
  assert any(o['id']=='A1' and o['live'] for o in live)==bool(event['live1']);assert any(o['id']=='A2' and o['live'] for o in live)==bool(event['live2'])
  assert [cell['value'] for obj in state['heap_retired'] for cell in obj['cells'] if cell['initialized'] is True]==event['historical']
  assert state['heap_pending_index']==(event['quantity'] if event['known']>event['quantity'] else None)
  if event['condition']!=-2:assert step['condition_result']==bool(event['condition'])
  if event['phase']=='return' and event['scope'] not in ['up','swap']:assert ped['instruction_event']['return']==bool(event['returned'])
  assert state['console_stdout']=='' and ped['invariant']['holds'] is None
 assert trace['steps'][-1]['state_after']==d['visual_state'];assert len(d['history'])==len(seed)+(not fail)
