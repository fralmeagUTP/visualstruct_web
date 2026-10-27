from pathlib import Path
import json,subprocess,shutil,hashlib,os
from app import create_app
r=Path(os.environ['AUDIT_REPO']);out=Path(os.environ['AUDIT_OUTPUT_DIR']);assert not any(out.iterdir());client=create_app().test_client()
raw=client.get('/help/source/avl/source').data;header=client.get('/help/source/avl/header').data
for suffix,data in [('c',raw),('h',header)]:assert data==(r/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(data)
source=raw.decode('utf-8-sig');lines=source.splitlines();start=source.index('void avl_liberarAVL(AVL raiz) {');end=source.index('\n}',start)+2;body=source[start:end];first=source.count('\n',0,start)
def line(text):return next(i+1 for i,l in enumerate(lines) if i>=first and l.strip()==text)
helper=r'''
static AVL audit_nodes[128];static int audit_count,audit_live[128],audit_values[128],audit_left[128],audit_right[128],audit_parent[128],audit_fe[128];
static int audit_depth=-1,audit_args[128],audit_invocations[128],audit_next,audit_case,audit_active,audit_root;
static int audit_id(AVL n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(AVL n){if(!n)return;int id=audit_count++;audit_nodes[id]=n;audit_live[id]=1;audit_values[id]=n->nro;audit_fe[id]=n->FE;audit_register(n->izq);audit_register(n->der);}
static int audit_valid(AVL n,AVL parent){if(!n)return 0;int l=audit_valid(n->izq,n),r=audit_valid(n->der,n);if(l<0||r<0||n->padre!=parent||n->FE!=r-l||r-l>1||r-l< -1)return -100;return 1+(l>r?l:r);}
static void audit_emit(int line,const char*phase,int result){if(!audit_active)return;printf("AUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"root_identity\":%d,\"frames\":[",audit_case,line,phase,result,audit_root);for(int d=0;d<=audit_depth;d++){if(d)printf(",");printf("{\"identity\":%d,\"usable\":%d,\"invocation\":%d}",audit_args[d],audit_args[d]==0||audit_live[audit_args[d]-1],audit_invocations[d]);}printf("],\"records\":[");for(int i=0;i<audit_count;i++){if(i)printf(",");printf("{\"id\":%d,\"live\":%d,\"value_before_free\":%d,\"left_identity\":%d,\"right_identity\":%d,\"parent_identity\":%d,\"FE_before_free\":%d}",i+1,audit_live[i],audit_values[i],audit_left[i],audit_right[i],audit_parent[i],audit_fe[i]);}printf("]}\n");}
static void audit_enter(AVL n){audit_depth++;audit_args[audit_depth]=audit_id(n);audit_invocations[audit_depth]=++audit_next;}
static int audit_condition(int line,int result){audit_emit(line,"condition",result);return result;}
'''
body=body.replace('{','{audit_enter(raiz);audit_emit('+str(line('void avl_liberarAVL(AVL raiz) {'))+',"enter",-2);',1)
body=body.replace('if (!raiz)','if (audit_condition('+str(line('if (!raiz'))+',!raiz))') if 'if (!raiz\n' in body else body.replace('if (!raiz)','if (audit_condition('+str(line('if (!raiz)'))+',!raiz))')
body=body.replace('return;','{audit_emit('+str(line('return;'))+',"return",-2);audit_depth--;return;}')
for field in ['izq','der']:
 text='avl_liberarAVL(raiz->'+field+');';number=line(text);assert body.count(text)==1;body=body.replace(text,'audit_emit('+str(number)+',"call",-2);'+text+'audit_emit('+str(number)+',"resume",-2);')
text='free(raiz);';assert body.count(text)==1;body=body.replace(text,'{int saved=audit_args[audit_depth];'+text+'audit_live[saved-1]=0;audit_emit('+str(line(text))+',"free",saved);}')
closing=source.count('\n',0,end-1)+1;last=body.rfind('}');body=body[:last]+'audit_emit('+str(closing)+',"return",-2);audit_depth--;'+body[last:]
seeds=[[],[7],[10,5,15,3,7,12,18],[-5,-10,0],[10,5,15,3]];main='\nint main(void){AVL root=NULL;\n'
for case,seed in enumerate(seeds):
 main+='audit_active=0;audit_count=0;audit_depth=-1;audit_next=0;root=NULL;'+''.join(f'avl_insertar(&root,{v});' for v in seed)
 main+=f'if(audit_valid(root,NULL)<0){{return 9;}}audit_register(root);for(int i=0;i<audit_count;i++){{audit_left[i]=audit_id(audit_nodes[i]->izq);audit_right[i]=audit_id(audit_nodes[i]->der);audit_parent[i]=audit_id(audit_nodes[i]->padre);}}audit_case={case};audit_root=audit_id(root);audit_active=1;avl_liberarAVL(root);audit_emit(0,"caller_resume",0);root=NULL;audit_root=0;audit_emit(0,"caller_assign",0);audit_active=0;for(int i=0;i<audit_count;i++)if(audit_live[i]){{return 10;}}\n'
main+='return 0;}';(out/'instrumented.c').write_text(source[:start]+helper+body+source[end:]+main,encoding='utf-8')
gcc=shutil.which('gcc');assert gcc;build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);(out/'compile.stderr').write_text(build.stderr,encoding='utf-8');assert build.returncode==0,build.stderr
run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr;(out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
cases=[]
for case,seed in enumerate(seeds):
 client=create_app().test_client()
 for v in seed:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 data=client.post('/hierarchical/avl/operate',json={'operation':'limpiar','payload':{}}).json;assert data['success'] and data['visual_state']['root'] is None
 native=[e for e in events if e['case']==case];frees=[e['result'] for e in native if e['phase']=='free'];assert len(frees)==len(seed) and len(set(frees))==len(seed)
 records={n['id']:n for n in native[0]['records']}
 for i,identity in enumerate(frees):assert all(child==0 or child in frees[:i] for child in [records[identity]['left_identity'],records[identity]['right_identity']])
 resume=next(e for e in native if e['phase']=='caller_resume');assert resume['root_identity']==(1 if seed else 0) and not any(n['live'] for n in resume['records'])
 trace=data['execution_trace'];cases.append({'seed':seed,'native_events':len(native),'native_free_order':frees,'endpoint_empty':True,'trace':trace,'trace_steps':len(trace['steps']),'native_identity_model_present':bool(trace['steps'][0].get('pedagogy',{}).get('memory_state',{}).get('avl_read_model'))})
report={'cases':cases,'native_events':len(events),'native_frees':sum(e['phase']=='free' for e in events),'events':events,'downloaded_sha256':hashlib.sha256(raw).hexdigest(),'header_sha256':hashlib.sha256(header).hexdigest(),'native_fixture_invariants_verified':True,'limits':['Baseline only: recorded C lifetime events and final-state parity, no current UI fidelity signoff.','Registry skips retired pointer slots; all references/fields after free are cached integer identities, not reads of indeterminate pointers or released nodes.','Caller root is not read after outer free; NULL assignment is a separate event.','No C/H changes, sanitizer, allocation-failure injection or all-path certificate.']}
(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'cases':len(cases),'events':len(events),'frees':report['native_frees'],'trace_steps':[c['trace_steps'] for c in cases],'identity_model':[c['native_identity_model_present'] for c in cases],'path':str(out)}))
