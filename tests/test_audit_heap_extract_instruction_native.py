"""Independent observations from compiled HTTP-downloaded C extraction."""
from pathlib import Path
import json,re,shutil,subprocess
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
CASES=[[],[7],[7,7,7],[1,3,2,8,7,9,4],[1,8,2,9,10,3,4],list(range(20)),list(range(21)),[-2147483648,2147483647,0,-1],[9,8,7,6,5,4,3,2,1]]
HELPER=r'''
static bool comparar(TipoMonticulo tipo,int a,int b);
static int active,case_id,depth,stack[8],instance[8],cc,sc,known;
static MonticuloBinario *am;static int *ad,*ao;static int output_known,os,ov,ui,ds,left,right,selected,ca,cb,ct,sa,sb,ts,tv;
static const char *kinds[]={"caller","extract","down","compare","swap"};
static void enter(int k){stack[depth]=k;instance[depth]=k==3?++cc:k==4?++sc:0;depth++;}
static void leave(int k){depth--;if(k==2)ds=0;if(k==4)ts=0;}
static void emit(const char*s,const char*t,const char*p,int c,int ret,int ix,int iy){
 if(!active)return;
 printf("AUDIT {\"case\":%d,\"scope\":\"%s\",\"text\":\"%s\",\"phase\":\"%s\",\"condition\":%d,\"returned\":%d,\"quantity\":%d,\"capacity\":%d,\"known\":%d,\"output_known\":%d,\"output_value\":",case_id,s,t,p,c,ret,am->cantidad,am->capacidad,known,output_known);
 if(output_known)printf("%d",*ao);else printf("null");
 printf(",\"active_indices\":[");if(ix>=0)printf("%d",ix);if(iy>=0)printf("%s%d",ix>=0?",":"",iy);printf("],\"frames\":[");
 for(int d=0;d<depth;d++){int k=stack[d];printf("%s{\"kind\":\"%s\",\"id\":\"%s",d?",":"",kinds[k],kinds[k]);if(k>=3)printf("-%d",instance[d]);printf("\",\"params\":{");
  if(k<=2){printf("\"m\":\"M1\"");if(k<=1)printf(",\"resultado\":\"R1\"");else printf(",\"indice\":%d",ui);}
  if(k==3)printf("\"tipo\":%d,\"a\":%d,\"b\":%d",ct,ca,cb);
  if(k==4)printf("\"a\":\"&A1[%d]\",\"b\":\"&A1[%d]\"",sa,sb);
  printf("},\"locals\":{");
  if(k==0&&os){printf("\"ok\":");if(os==1)printf("\"sin inicializar\"");else printf(ov?"true":"false");}
  if(k==2&&ds){printf("\"hijo_izq\":");if(ds<2)printf("\"sin inicializar\"");else printf("%d",left);printf(",\"hijo_der\":");if(ds<3)printf("\"sin inicializar\"");else printf("%d",right);printf(",\"seleccionado\":");if(ds<4)printf("\"sin inicializar\"");else printf("%d",selected);}
  if(k==4&&ts){printf("\"temp\":%d",tv);}printf("}}");
 }printf("],\"array\":[");for(int i=0;i<am->cantidad;i++)printf("%s%d",i?",":"",ad[i]);printf("],\"physical\":[");for(int i=0;i<known;i++)printf("%s%d",i?",":"",ad[i]);printf("]}\n");
}
static int condition(const char*s,const char*t,int c){emit(s,t,"condition",c,-2,-1,-1);return c;}
static int child_condition(MonticuloBinario*m,int child,int selected_index,const char*t){
 int result=0;if(child<m->cantidad){emit("down",t,"call",-2,-2,child,selected_index);result=comparar(m->tipo,m->datos[child],m->datos[selected_index]);}
 return condition("down",t,child<m->cantidad&&result);
}
'''

@pytest.fixture(scope='module')
def heap_extract_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('heap-extract-native');c=create_app().test_client()
 raw=c.get('/help/source/binary_heap/source').data;header=c.get('/help/source/binary_heap/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(out/('tad_monticulo_binario.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig').replace('\r\n','\n');names={'compare':'comparar','swap':'intercambiar','down':'heapify_down','extract':'monticulo_extraer_raiz'}
 originals={s:CCodeService._extract_function_with_comment(source,n) for s,n in names.items()}
 def body(s):
  rows=originals[s].splitlines();return '\n'.join(rows[next(i for i,l in enumerate(rows) if re.match(r'(static )?(bool|void) '+names[s]+r'\(',l)):])
 def replace(code,text,new,count=1):return re.sub(r'(?m)^([ \t]*)'+re.escape(text),lambda m:m.group(1)+new,code,count=count)
 def log(s,t,p,c='-2',ret='-2',ix='-1',iy='-1'):return 'emit('+','.join([json.dumps(s),json.dumps(t),json.dumps(p),c,ret,ix,iy])+');'
 def cond(s,t,expr):return 'condition('+','.join([json.dumps(s),json.dumps(t),expr])+')'
 ids={'extract':1,'down':2,'compare':3,'swap':4}
 for scope in names:
  old=body(scope);new=old;signature=old.splitlines()[0];kind=ids[scope]
  entry={'extract':'','down':'ui=indice;ds=0;','compare':'ct=tipo;ca=a;cb=b;','swap':'if(active){sa=(int)(a-ad);sb=(int)(b-ad);}ts=0;'}[scope]
  new=new.replace('{','{'+entry+f'enter({kind});'+log(scope,signature,'enter'),1)
  if scope=='extract':
   t='if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;';new=replace(new,t,'if('+cond(scope,t,'m==NULL||m->cantidad==0||resultado==NULL')+'){leave(1);'+log(scope,t,'return',ret='0')+'return false;}')
   t='*resultado = m->datos[0];';new=replace(new,t,t+'output_known=1;'+log(scope,t,'assignment',ix='0'))
   t='m->cantidad--;';new=replace(new,t,t+log(scope,t,'assignment'))
   t='if (m->cantidad > 0) {';new=replace(new,t,'if('+cond(scope,t,'m->cantidad>0')+'){')
   t='m->datos[0] = m->datos[m->cantidad];';new=replace(new,t,t+log(scope,t,'assignment',ix='0',iy='m->cantidad'))
   t='heapify_down(m, 0);';new=replace(new,t,log(scope,t,'call')+t+log(scope,t,'resume'))
  elif scope=='down':
   t='int hijo_izq, hijo_der, seleccionado;';new=replace(new,t,t+'ds=1;'+log(scope,t,'declaration'))
   t='while (1) {';new=replace(new,t,'while('+cond(scope,t,'1')+'){')
   for t,extra in [('hijo_izq = 2 * indice + 1;','left=hijo_izq;if(ds<2)ds=2;'),('hijo_der = 2 * indice + 2;','right=hijo_der;if(ds<3)ds=3;'),('seleccionado = indice;','selected=seleccionado;ds=4;'),('seleccionado = hijo_izq;','selected=seleccionado;'),('seleccionado = hijo_der;','selected=seleccionado;'),('indice = seleccionado;','ui=indice;')]:new=replace(new,t,t+extra+log(scope,t,'assignment'))
   for child in ['hijo_izq','hijo_der']:
    t=f'if ({child} < m->cantidad && comparar(m->tipo, m->datos[{child}], m->datos[seleccionado])) {{';new=replace(new,t,'if(child_condition(m,'+child+',seleccionado,'+json.dumps(t)+')){')
   t='if (seleccionado != indice) {';new=replace(new,t,'if('+cond(scope,t,'seleccionado!=indice')+'){')
   t='intercambiar(&m->datos[indice], &m->datos[seleccionado]);';new=replace(new,t,log(scope,t,'call')+t+log(scope,t,'resume'))
   t='break;';new=replace(new,t,log(scope,t,'assignment')+t)
  elif scope=='compare':
   t='if (tipo == MONTICULO_MIN) {';new=replace(new,t,'if('+cond(scope,t,'tipo==MONTICULO_MIN')+'){')
  else:
   for t,extra,ix,iy in [('int temp = *a;','ts=1;tv=temp;','sa','-1'),('*a = *b;','','sa','sb'),('*b = temp;','','sb','-1')]:new=replace(new,t,t+extra+log(scope,t,'assignment',ix=ix,iy=iy))
  for t,result in [('return true;','1'),('return a < b;','a<b'),('return a > b;','a>b')]:new=replace(new,t,f'leave({kind});'+log(scope,t,'return',ret=result)+t,count=0)
  if scope in ['down','swap']:new=new[:-1]+f'leave({kind});'+log(scope,'}','return')+'}'
  assert old in source;source=source.replace(old,new,1)
 source=source.replace('static void intercambiar(',HELPER+'\nstatic void intercambiar(',1)
 caller='bool ejecutar_extraer(MonticuloBinario *m, int *resultado) {\n    bool ok = monticulo_extraer_raiz(m, resultado);\n    return ok;\n}'
 implemented=caller.replace('{','{enter(0);'+log('caller',caller.splitlines()[0],'enter'),1)
 t='bool ok = monticulo_extraer_raiz(m, resultado);';implemented=replace(implemented,t,'os=1;'+log('caller',t,'call')+t+'os=2;ov=ok;'+log('caller',t,'resume'))
 t='return ok;';implemented=replace(implemented,t,'leave(0);'+log('caller',t,'return',ret='ok')+t)
 main='\nint main(void){MonticuloBinario m;int output=123456;bool ok;'
 for case,seed in enumerate(CASES):
  main+='active=0;monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join(f'monticulo_insertar(&m,{v});' for v in seed)
  main+=f'case_id={case};am=&m;ad=m.datos;ao=&output;output_known=0;known=m.cantidad;depth=cc=sc=os=ds=ts=0;active=1;ok=ejecutar_extraer(&m,&output);active=0;if(ok!={int(bool(seed))})return 2;monticulo_destruir(&m);'
 main+='active=0;if(monticulo_extraer_raiz(NULL,&output))return 3;monticulo_inicializar(&m,MONTICULO_MIN,16);monticulo_insertar(&m,7);if(monticulo_extraer_raiz(&m,NULL)||m.cantidad!=1)return 4;monticulo_destruir(&m);return 0;}'
 (out/'instrumented.c').write_text(source+'\n'+implemented+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 report={'cases':CASES,'events':events,'caller':caller,'originals':originals};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

@pytest.mark.parametrize('case',range(9))
def test_heap_extract_completed_statements_match_native(heap_extract_native,case):
 c=create_app().test_client();seed=CASES[case]
 for v in seed:assert c.post('/hierarchical/binary_heap/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 d=c.post('/hierarchical/binary_heap/operate',json={'operation':'extraer_raiz','payload':{}}).json;assert d['success']==bool(seed)
 events=[e for e in heap_extract_native['events'] if e['case']==case];steps=d['execution_trace']['steps'];assert len(steps)==len(events)
 for step,e in zip(steps,events):
  p=step['pedagogy'];st=p['memory_state'];assert step['line_text'].strip()==e['text'];assert p['instruction_event']['scope']==e['scope'] and p['instruction_event']['phase']==e['phase']
  assert st['size']==e['quantity'] and st['capacity']==e['capacity'] and st['array']==e['array'] and st['heap_written']==e['known'] and st['heap_active_indices']==e['active_indices']
  assert st['caller_output']=={'initialized':bool(e['output_known']),'value':e['output_value']}
  assert [{'kind':f['kind'],'id':f['id'],'params':f['parameters'],'locals':f['locals']} for f in st['query_frames']]==e['frames']
  assert [cell['value'] for cell in st['heap_allocations'][0]['cells'][:e['known']]]==e['physical']
  assert st['heap_data_reference']=='A1' and not st['heap_retired'] and st['console_stdout']=='' and p['invariant']['holds'] is None
  if e['condition']!=-2:assert step['condition_result']==bool(e['condition'])
  if e['phase']=='return' and e['scope'] not in ['down','swap']:assert p['instruction_event']['return']==bool(e['returned'])
 assert steps[-1]['state_after']==d['visual_state'];assert len(d['history'])==len(seed)+bool(seed)
