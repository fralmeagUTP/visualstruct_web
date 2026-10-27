"""Independent downloaded-C Bellman-Ford endpoint baseline; reports differences, not a pass claim."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
MAX=2147483647
CASES=[{'name': 'same_vertex', 'v': [0], 'e': [], 'start': 0, 'end': 0}, {'name': 'negative_edge', 'v': [1, 2], 'e': [(1, 2, -3)], 'start': 1, 'end': 2}, {'name': 'cheaper_negative_alternative', 'v': [1, 2, 3], 'e': [(1, 2, 4), (1, 3, 1), (3, 2, -5)], 'start': 1, 'end': 2}, {'name': 'reachable_negative_cycle', 'v': [1, 2, 3, 4], 'e': [(1, 2, 1), (2, 3, -3), (3, 2, 1), (3, 4, 1)], 'start': 1, 'end': 4}, {'name': 'reachable_cycle_with_direct_target', 'v': [1, 2, 4], 'e': [(1, 2, -2), (2, 1, 1), (1, 4, 7)], 'start': 1, 'end': 4}, {'name': 'unreachable_negative_cycle', 'v': [1, 2, 3, 4], 'e': [(1, 2, 3), (3, 4, -3), (4, 3, 1)], 'start': 1, 'end': 2}, {'name': 'unreachable_destination', 'v': [1, 2, 3], 'e': [(1, 2, -1)], 'start': 1, 'end': 3}, {'name': 'zero_cycle', 'v': [1, 2, 3], 'e': [(1, 2, 0), (2, 1, 0), (2, 3, -1), (1, 3, 2)], 'start': 1, 'end': 3}, {'name': 'equal_cost_order', 'v': [1, 2, 3, 4], 'e': [(1, 2, 1), (1, 3, 1), (2, 4, -1), (3, 4, -1)], 'start': 1, 'end': 4}, {'name': 'negative_ids', 'v': [-2147483648, -1, 2147483647], 'e': [(-2147483648, -1, -2), (-1, 2147483647, 1)], 'start': -2147483648, 'end': 2147483647}, {'name': 'missing_start', 'v': [1, 2], 'e': [(1, 2, 1)], 'start': 999, 'end': 2}, {'name': 'missing_end', 'v': [1, 2], 'e': [(1, 2, 1)], 'start': 1, 'end': 999}, {'name': 'intmax_minus_one', 'v': [1, 2], 'e': [(1, 2, 2147483646)], 'start': 1, 'end': 2}, {'name': 'intmax_infinity', 'v': [1, 2], 'e': [(1, 2, 2147483647)], 'start': 1, 'end': 2}, {'name': 'upper_bound_guard', 'v': [1, 2, 3], 'e': [(1, 2, 2147483646), (2, 3, 2)], 'start': 1, 'end': 3}, {'name': 'intmin_edge', 'v': [1, 2], 'e': [(1, 2, -2147483648)], 'start': 1, 'end': 2}, {'name': 'lower_bound_guard', 'v': [1, 2, 3], 'e': [(1, 2, -2147483648), (2, 3, -1)], 'start': 1, 'end': 3}, {'name': 'undirected_negative_cycle', 'v': [1, 2], 'e': [(1, 2, -1)], 'start': 1, 'end': 2, 'directed': False}, {'name': 'negative_cycle_bound_missed', 'v': [1, 2], 'e': [(1, 2, -2147483648), (2, 1, -2147483648)], 'start': 1, 'end': 2}, {'name': 'empty_graph', 'v': [], 'e': [], 'start': 0, 'end': 0}]

if len(sys.argv)>2:
 selected_name=sys.argv[2]
 CASES=[case for case in CASES if case['name']==selected_name]
 assert len(CASES)==1,'Unknown or duplicate requested native/application case'
app=create_app();client=app.test_client();downloads={}
for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
 for part,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/'+tad+'/'+part);assert r.status_code==200;p=OUT/(stem+'.'+ext);p.write_bytes(r.data);downloads[p.name]=hashlib.sha256(r.data).hexdigest()
source=r"""#include "tad_grafo.h"
#include <stdio.h>
#include <stdlib.h>
static void release_graph(Grafo g){while(g.a){ListaArco n=g.a;g.a=n->sig;free(n);}while(g.v){ListaVertice n=g.v;g.v=n->sig;free(n);}}
static void emit(Grafo g,ListaArco r,int c){printf("\nRESULT %d {\"null\":%s,\"arcs\":[",c,r?"false":"true");int first=1;long long cost=0;for(ListaArco p=r;p;p=p->sig){printf("%s[%d,%d,%d]",first?"":",",p->origen,p->destino,p->costo);first=0;cost+=p->costo;}printf("],\"cost\":%lld,\"vertex_order\":[",cost);first=1;for(ListaVertice p=g.v;p;p=p->sig){printf("%s%d",first?"":",",p->dato);first=0;}puts("]}");}
int main(void){
"""
for i,c in enumerate(CASES):
 source+='{Grafo g=grafo_crear();'
 for v in c['v']:source+=f'g=grafo_insertar_vertice(g,{v});'
 for a,b,w in c['e']:
  source+=f'g=grafo_insertar_arco(g,{a},{b},{w});'
  if not c.get('directed',True) and a!=b:source+=f'g=grafo_insertar_arco(g,{b},{a},{w});'
 source+=f'printf("\\nBEGIN {i}\\n");ListaArco r=grafo_bellman_ford(g,{c["start"]},{c["end"]});emit(g,r,{i});while(r){{ListaArco n=r;r=r->sig;free(n);}}release_graph(g);}}\n'
source+='return 0;}\n';(OUT/'observed-main.c').write_text(source,encoding='utf-8')
compiler=shutil.which('gcc');assert compiler;exe=OUT/'native.exe';build=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(OUT/'observed-main.c'),str(OUT/'tad_grafo.c'),str(OUT/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);(OUT/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0 and not build.stderr,build.stderr
native=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert native.returncode==0; (OUT/'native.stdout.log').write_text(native.stdout);actual={int(m[1]):json.loads(m[2]) for m in re.finditer(r'^RESULT (\d+) (.*)$',native.stdout,re.M)};assert len(actual)==len(CASES)
segments=re.split(r'\nBEGIN (\d+)\n',native.stdout);warnings={int(segments[i]):('Se detecto un ciclo negativo.' in segments[i+1]) for i in range(1,len(segments),2)};assert len(warnings)==len(CASES)
rows=[]
for i,c in enumerate(CASES):
 h=[]
 for op,p in [('create_graph',{'directed':c.get('directed',True)}),*[('insert_vertex',{'vertex':v}) for v in c['v']],*[('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in c['e']]]:
  data=S.execute_operation('graph',op,p,h);assert data['success'];h=data['history']
 before=json.loads(json.dumps(h));d=S.execute_operation('graph','run_bellman_ford',{'start':c['start'],'end':c['end']},h);n=actual[i];r=d.get('result') or {};path=[]
 if n['arcs']:path=[n['arcs'][0][0]]+[a[1] for a in n['arcs']]
 elif c['start']==c['end'] and c['start'] in c['v'] and not warnings[i]:path=[c['start']]
 expected_reachable=bool(path);expect_rejection=c['start'] not in c['v'] or warnings[i]
 differences=[]
 if bool(r.get('has_negative_cycle'))!=warnings[i]:differences.append('negative_cycle')
 if expect_rejection:
  if d['success']:differences.append('missing_required_rejection')
  if not n['null']:differences.append('native_rejection_not_null')
 else:
  if not d['success']:differences.append('unexpected_backend_rejection')
  if r.get('path')!=path:differences.append('path')
  if r.get('reachable')!=expected_reachable:differences.append('reachable')
  if r.get('distance_to_destination')!=(n['cost'] if path else None):differences.append('distance')
 saved=sum(x['operation']=='run_bellman_ford' for x in d['history']);view=S.get_view_model('graph',d['history']);reloaded=sum(x['operation']=='run_bellman_ford' for x in view['history'])
 trace=d['execution_trace'];row={'case':i,'name':c['name'],'input':c,'native':n,'native_cycle_warning':warnings[i],'cycle_result_matches_error_spec':(not d['success']) if warnings[i] else None,'backend':{'success':d['success'],'message':d['message'],'result':d.get('result')},'native_decoded_path':path,'differences':differences,'successful_query_saved':saved,'successful_query_after_reload':reloaded,'failure_history_unchanged':d['history']==before if not d['success'] else None,'trace_steps':len(trace.get('steps',[])),'console_lines':[line for step in trace.get('steps',[]) for line in step.get('console',[])],'source_functions':sorted({str(x.get('pedagogy',{}).get('instruction_event',{}).get('function')) for x in trace.get('steps',[])})};rows.append(row)
 (OUT/('case-'+str(i)+'.json')).write_text(json.dumps({'case':c,'native':n,'response':d},ensure_ascii=False,indent=2,allow_nan=True),encoding='utf-8')
 print(c['name'],'differences='+','.join(differences),'history='+str(saved)+'/'+str(reloaded),flush=True)
report={'scope':'endpoint baseline only; not instruction verification','cases':len(rows),'downloads_sha256':downloads,'native_strict_c17':True,'rows':rows,'differences_count':sum(bool(r['differences']) for r in rows),'negative_weights_permitted':True,'native_cycle_warning_cases':sum(warnings.values())};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=True),encoding='utf-8');print('Collected',len(rows),'cases,',report['differences_count'],'endpoint divergences')
