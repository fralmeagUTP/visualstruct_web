from pathlib import Path
import os,sys,json,hashlib,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph import tad_grafo as G
from _audit_graph_bfs_native_observer import CASES
out=Path(os.environ['AUDIT_OUTPUT_DIR']);out.mkdir(exist_ok=False);os.environ['SESSION_CACHE_DIR']=str(out/'cache');client=create_app().test_client();hashes={}
for sid,name in [('graph','tad_grafo'),('queue','tad_cola')]:
 for ext,part in [('c','source'),('h','header')]:
  response=client.get('/help/source/'+sid+'/'+part);assert response.status_code==200
  raw=response.data;assert raw==(ROOT/'docs/tads_C'/(name+'.'+ext)).read_bytes();(out/(name+'.'+ext)).write_bytes(raw);hashes[name+'.'+ext]=hashlib.sha256(raw).hexdigest()
main='#include "tad_grafo.h"\n#include <stdio.h>\n#include <stdlib.h>\nint main(void){\n'
for idx,c in enumerate(CASES):
 main+='{Grafo g=grafo_crear();'+''.join(f'g=grafo_insertar_vertice(g,{v});' for v in c['vertices'])+''.join(f'g=grafo_insertar_arco(g,{u},{v},1);' for u,v in c['edges'])+'for(ListaVertice n=g.v;n;n=n->sig)n->marcado=7;'
 for run in range(c.get('repeat',1)):
  main+=f'ListaVertice r{run}=grafo_dfs(g,{c["start"]});printf("RESULT {idx} {run} [");int first{run}=1;for(ListaVertice n=r{run};n;n=n->sig){{printf("%s%d",first{run}?"":",",n->dato);first{run}=0;}}printf("] MARKS [");first{run}=1;for(ListaVertice n=g.v;n;n=n->sig){{printf("%s[%d,%d]",first{run}?"":",",n->dato,n->marcado);first{run}=0;}}printf("] OUTPUTMARKS [");first{run}=1;for(ListaVertice n=r{run};n;n=n->sig){{printf("%s%d",first{run}?"":",",n->marcado);first{run}=0;}}puts("]");while(r{run}){{ListaVertice n=r{run};r{run}=n->sig;free(n);}}'
 main+='while(g.a){ListaArco n=g.a;g.a=n->sig;free(n);}while(g.v){ListaVertice n=g.v;g.v=n->sig;free(n);}}\n'
main+='return 0;}';(out/'main.c').write_text(main,encoding='utf-8')
cmd=[shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'main.c'),str(out/'tad_grafo.c'),str(out/'tad_cola.c'),'-o',str(out/'observed.exe')]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0 and not p.stderr,p.stderr
p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);assert p.returncode==0;pout=p.stdout;(out/'stdout.log').write_text(pout,encoding='utf-8')
import re
native={}
for m in re.finditer(r'^RESULT (\d+) (\d+) (.*?) MARKS (.*?) OUTPUTMARKS (.*)$',pout,re.M):native[int(m[1]),int(m[2])]=[json.loads(m[k]) for k in [3,4,5]]
records=[]
for idx,c in enumerate(CASES):
 g=G.grafo_crear()
 for v in c['vertices']:g=G.grafo_insertar_vertice(g,v)
 for u,v in c['edges']:g=G.grafo_insertar_arco(g,u,v,1)
 g._marcas={v:7 for v in c['vertices']};G._sync_graph_lists(g)
 h=[{'operation':'create_graph','payload':{'directed':True}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in c['vertices']],*[{'operation':'insert_edge','payload':{'origin':u,'target':v,'weight':1}} for u,v in c['edges']]]
 for run in range(c.get('repeat',1)):
  n=G.grafo_dfs(g,c['start']);order=[];outputmarks=[]
  while n:order.append(n.dato);outputmarks.append(n.marcado);n=n.sig
  expected,marks,om=native[idx,run];assert order==expected,(c,order,expected)
  data=S.execute_operation('graph','run_dfs',{'start':c['start']},h);h=data['history'];trace=data['execution_trace']
  if c['start'] in c['vertices']:assert data['success'] and data['result']==expected
  else:assert not data['success'] and expected==[]
  records.append({'case':idx,'run':run,'name':c['name'],'native_order':expected,'native_marks':marks,'python_marks':g._marcas,'marks_match':dict(marks)==g._marcas,'output_marks_match':om==outputmarks,'native_output_marks':om,'python_output_marks':outputmarks,'backend_success':data['success'],'history_count':sum(x['operation']=='run_dfs' for x in h),'trace_steps':len(trace['steps']),'source_definitions':re.findall(r'^(?:static\s+)?(?:Grafo|ListaVertice|void|int)\s+(\w+)\s*\(',trace['source_code'],re.M),'scope_functions':sorted({f.get('function','') for st in trace['steps'] for f in st.get('pedagogy',{}).get('call_stack',[])}),'instruction_events':sum('instruction_event' in st.get('pedagogy',{}) for st in trace['steps'])})
report={'records':records,'source_hashes':hashes,'cases':len(CASES),'native_runs':len(native),'final_orders_match':True,'marks_mismatches':sum(not x['marks_match'] for x in records),'output_marks_mismatches':sum(not x['output_marks_match'] for x in records),'successful_history_missing':sum(x['backend_success'] and not x['history_count'] for x in records),'limits':['Final-state/contract baseline only, no instruction identity/alias or UI conformance proof.','Normal allocation, finite directed fixtures; raw invalid C call distinguished from API rejection.','No allocation-failure injection or sanitizer proof.']}
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['records','source_hashes']}),flush=True)
