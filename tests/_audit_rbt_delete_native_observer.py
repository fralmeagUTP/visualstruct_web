"""Independent actual-C deletion LOW events with safe live/retired identity registry."""
from pathlib import Path
import re,json,hashlib,subprocess,shutil,os
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from _audit_rbt_insert_native_observer import plain,CHECK
SEEDS=[[],[10],[10,5],[10,15],[10,5,15],[20,10,30,5,15,25,35],[11,2,14,1,7,15,5,8,4],[41,38,31,12,19,8],[7,3,18,10,22,8,11,26],list(range(1,16)),list(range(15,0,-1)),[0,-2147483648,2147483647]]
CASES=[{'seed':s,'value':v} for s in SEEDS for v in [*s,99]]
FUNCTIONS=['colorOf','transplantar','minimo','arreglarEliminacion','rbt_eliminar','rbt_rotar_dcha','rbt_rotar_izda']
HELPER=r'''
static RBT audit_nodes[128],*audit_root;static int audit_live[128],audit_count,audit_depth=-1,audit_case,audit_active,audit_serial,audit_frees,audit_allocations,audit_last_free;static const char*audit_functions[128];static int audit_invocations[128];
static int audit_id(RBT n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(RBT n){if(!n)return;int i=audit_count++;audit_nodes[i]=n;audit_live[i]=1;audit_register(n->izq);audit_register(n->der);}
static void audit_enter(const char*fn){if(!audit_active)return;audit_depth++;audit_functions[audit_depth]=fn;audit_invocations[audit_depth]=++audit_serial;}
static void audit_exit(void){if(audit_active)audit_depth--;}
static void audit_emit(int line,const char*fn,const char*phase,int result){if(!audit_active)return;
 printf("AUDIT {\"case\":%d,\"line\":%d,\"function\":\"%s\",\"phase\":\"%s\",\"result\":%d,\"root\":%d,\"frees\":%d,\"allocations\":%d,\"frames\":[",audit_case,line,fn,phase,result,audit_id(*audit_root),audit_frees,audit_allocations);
 for(int d=0;d<=audit_depth;d++){printf("%s{\"function\":\"%s\",\"invocation\":%d}",d?",":"",audit_functions[d],audit_invocations[d]);}printf("],\"heap\":[");int first=1;
 for(int i=0;i<audit_count;i++){if(!audit_live[i])continue;RBT n=audit_nodes[i];printf("%s{\"id\":%d,\"value\":%d,\"left\":%d,\"right\":%d,\"parent\":%d,\"color\":\"%s\"}",first?"":",",i+1,n->nro,audit_id(n->izq),audit_id(n->der),audit_id(n->padre),n->rbt_color==ROJO?"RED":"BLACK");first=0;}printf("],\"retired_ids\":[");first=1;for(int i=0;i<audit_count;i++)if(!audit_live[i]){printf("%s%d",first?"":",",i+1);first=0;}puts("]}");}
static int audit_condition(int line,const char*fn,int result){audit_emit(line,fn,"condition",!!result);return result;}
static RBT audit_return_ptr(int line,const char*fn,RBT n){if(audit_active){audit_emit(line,fn,"return",audit_id(n));audit_exit();}return n;}
static int audit_return_int(int line,const char*fn,int result){if(audit_active){audit_emit(line,fn,"return",result);audit_exit();}return result;}
static void *audit_malloc(size_t size){if(audit_active)audit_allocations++;return malloc(size);}
static void audit_free(void*p){if(audit_active){int id=audit_id(p);if(id<=0)exit(71);audit_last_free=id;audit_live[id-1]=0;audit_frees++;}free(p);}
#define malloc audit_malloc
#define free audit_free
'''

def instrument(source):
 masked=plain(source);changes=[]
 for fn in FUNCTIONS:
  m=re.search(r'^(?:static\s+)?(RBT|void|char)\s+'+fn+r'\([^;]*?\)\s*\{',masked,re.M);assert m,fn
  start=m.end();end=start;depth=1
  while depth:
   if masked[end]=='{':depth+=1
   if masked[end]=='}':depth-=1
   end+=1
  body=source[start:end-1];mask=masked[start:end-1];updates=[]
  def line(pos):return source.count('\n',0,start+pos)+1
  for c in re.finditer(r'\b(?:if|while)\s*\(',mask):
   a=c.end();z=a;d=1
   while d:
    if mask[z]=='(':d+=1
    if mask[z]==')':d-=1
    z+=1
   updates.append((a,z-1,f'audit_condition({line(c.start())},__func__,!!({body[a:z-1]}))'))
  for c in re.finditer(r'\breturn\s*([^;]*);',mask):
   expr=body[c.start(1):c.end(1)].strip();ln=line(c.start())
   repl=f'return audit_return_ptr({ln},__func__,({expr}));' if m.group(1)=='RBT' else f'return (char)audit_return_int({ln},__func__,({expr}));' if m.group(1)=='char' else f'{{audit_emit({ln},__func__,"return",-2);audit_exit();return;}}'
   updates.append((c.start(),c.end(),repl))
  for c in re.finditer(r'\b(?:RBT|char|int)\s+\w+\s*=[^;]+;',mask):updates.append((c.end(),c.end(),f'audit_emit({line(c.start())},__func__,"local",-2);'))
  pattern=r'(?:\*\w+|\(\*\w+\)|\b\w+)(?:->\w+)*\s*=(?!=)[^;]+;'
  for c in re.finditer(pattern,mask):
   if re.search(r'\b(?:RBT|char|int)\s+$',mask[:c.start()]):continue
   text=body[c.start():c.end()];phase='recolor' if 'rbt_color' in text.split('=',1)[0] else 'link' if ('->' in text.split('=',1)[0] or text.startswith('*')) else 'local';updates.append((c.start(),c.end(),'{ '+text+f'audit_emit({line(c.start())},__func__,"{phase}",-2);'+' }'))
  for c in re.finditer(r'\b(?:transplantar|arreglarEliminacion|rbt_rotar_dcha|rbt_rotar_izda)\([^;]*?\);',mask):
   text=body[c.start():c.end()];updates.append((c.start(),c.end(),f'{{audit_emit({line(c.start())},__func__,"call",-2);'+text+f'audit_emit({line(c.start())},__func__,"resume",-2);'+'}'))
  for c in re.finditer(r'\bfree\(z\);',mask):updates.append((c.start(),c.end(),'{'+body[c.start():c.end()]+f'audit_emit({line(c.start())},__func__,"free",audit_last_free);'+'}'))
  last=-1
  for a,z,repl in sorted(updates):assert a>=last,(fn,a,last);last=z
  for a,z,repl in sorted(updates,reverse=True):body=body[:a]+repl+body[z:]
  entry=f'audit_enter(__func__);audit_emit({source.count(chr(10),0,m.start())+1},__func__,"enter",-2);';tail=f'audit_emit({source.count(chr(10),0,end-1)+1},__func__,"return",-2);audit_exit();' if m.group(1)=='void' else ''
  changes.append((start,end-1,entry+body+tail))
 for a,z,text in sorted(changes,reverse=True):source=source[:a]+text+source[z:]
 anchor='typedef struct nodoRBT *RBT;';assert source.count(anchor)==1;return source.replace(anchor,anchor+'\n'+HELPER)

def observe(out):
 out=Path(out);out.mkdir();root=Path(__file__).resolve().parents[1];client=create_app().test_client();raw=client.get('/help/source/red_black/source').data;header=client.get('/help/source/red_black/header').data
 for ext,data in [('c',raw),('h',header)]:assert data==(root/'docs/tads_C'/('tad_rojo_negro.'+ext)).read_bytes();(out/('tad_rojo_negro.'+ext)).write_bytes(data)
 source=raw.decode('utf-8-sig').replace('\r\n','\n');main='\n'+CHECK+'\nint main(void){RBT root=NULL;audit_root=&root;\n'
 for case,meta in enumerate(CASES):
  main+='audit_active=0;root=NULL;'+''.join(f'rbt_insertar(&root,{v});' for v in meta['seed'])
  main+=f'audit_count=0;audit_register(root);audit_frees=0;audit_allocations=0;audit_depth=-1;audit_serial=0;audit_case={case};printf("BEGIN {case}\\n");audit_active=1;audit_emit(0,"main","before",-2);rbt_eliminar(&root,{meta["value"]});audit_emit(0,"main","after",-2);audit_active=0;'
  main+=f'if((root&&root->rbt_color!=NEGRO)||audit_valid(root,NULL,-2147483649LL,2147483648LL)<0||audit_depth!=-1)return 80;printf("END {case}\\nROOT {case} ");audit_tree(root);printf("\\n");rbt_liberar(root);root=NULL;\n'
 main+='return 0;}';(out/'instrumented.c').write_text(instrument(source)+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'instrumented.exe')],capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(build.stderr);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(out/'instrumented.exe')],capture_output=True,text=True,timeout=15);(out/'stdout.log').write_text(run.stdout,encoding='utf-8');assert run.returncode==0,(run.returncode,run.stdout[-1200:],run.stderr)
 events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')];trees={int(m.group(1)):json.loads(m.group(2)) for m in re.finditer(r'^ROOT (\d+) (.*)$',run.stdout,re.M)};cases=[]
 for case,meta in enumerate(CASES):
  ev=[e for e in events if e['case']==case];chunk=run.stdout.split(f'BEGIN {case}\n',1)[1].split(f'END {case}\n',1)[0];stdout=''.join(l+'\n' for l in chunk.splitlines() if not l.startswith('AUDIT '));assert not stdout
  history=[{'operation':'insertar','payload':{'value':v}} for v in meta['seed']];data=S.execute_operation('red_black','eliminar',{'value':meta['value']},history);present=meta['value'] in meta['seed'];assert data['success']==present and data['visual_state']['root']==trees[case],case;trace=data['execution_trace']
  cases.append({**meta,'case':case,'native_root':trees[case],'present':present,'frees':ev[-1]['frees'],'allocations':ev[-1]['allocations'],'native_events':len(ev),'function_entries':{fn:sum(e['phase']=='enter' and e['function']==fn for e in ev) for fn in FUNCTIONS},'trace_steps':len(trace['steps']),'trace_functions':sorted({f['function'] for step in trace['steps'] for f in step['pedagogy'].get('call_stack',[])}),'trace_has_memory_state':all('memory_state' in step['pedagogy'] for step in trace['steps']),'native_stdout':stdout})
 report={'cases':cases,'events':events,'native_events':len(events),'source_sha256':hashlib.sha256(raw).hexdigest(),'header_sha256':hashlib.sha256(header).hexdigest(),'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'strong_native_invariants':True,'limits':['LOW baseline; typed locals/short-circuit operand events/callsite borrowed-return details not yet recorded.','Live registry never reads retired pointer slots or freed fields; retired records contain integer identities only.','Native NULL root storage is NOT tested: rbt_eliminar dereferences arbol and requires nonNULL writable storage.','Empty/absent are native void no-op but application rejection.','No native printf/allocation occurs in deletion; caller output is separate.','Endpoint comparison and strong final invariants do not prove instruction UI fidelity.']}
 (out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'cases':len(cases),'native_events':len(events),'frees':sum(c['frees'] for c in cases),'path':str(out)}),flush=True);return report
if __name__=='__main__':observe(os.environ['AUDIT_OUTPUT_DIR'])
