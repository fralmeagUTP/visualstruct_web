"""Independent downloaded-C Bellman-Ford endpoint baseline; reports differences, not a pass claim."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
MAX=2147483647
CASES=[{'name': 'single_vertex', 'v': [-1], 'e': [], 'start': -1, 'directed': False}, {'name': 'connected', 'v': [1, 2, 3], 'e': [(1, 2, 4), (1, 3, 1), (3, 2, 2)], 'start': 1, 'directed': False}, {'name': 'disconnected', 'v': [1, 2, 3, 4], 'e': [(1, 2, 2), (3, 4, 3)], 'start': 1, 'directed': False}, {'name': 'isolated_start', 'v': [0, 1, 2], 'e': [(1, 2, 3)], 'start': 0, 'directed': False}, {'name': 'equal_cost', 'v': [1, 2, 3, 4], 'e': [(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1)], 'start': 1, 'directed': False}, {'name': 'zero_weight', 'v': [1, 2, 3], 'e': [(1, 2, 0), (2, 3, 0), (1, 3, 1)], 'start': 1, 'directed': False}, {'name': 'negative_edge', 'v': [1, 2], 'e': [(1, 2, -1)], 'start': 1, 'directed': False}, {'name': 'mixed_negative', 'v': [1, 2, 3], 'e': [(1, 2, -2), (1, 3, 3), (2, 3, 1)], 'start': 1, 'directed': False}, {'name': 'self_loop', 'v': [1, 2], 'e': [(1, 1, -1), (1, 2, 2)], 'start': 1, 'directed': False}, {'name': 'negative_ids', 'v': [-2147483648, -1, 2147483647], 'e': [(-2147483648, -1, 2), (-1, 2147483647, 1)], 'start': -1, 'directed': False}, {'name': 'symmetric_reverse_update', 'v': [1, 2], 'e': [(1, 2, 3), (2, 1, 2)], 'start': 999, 'directed': False}, {'name': 'empty', 'v': [], 'e': [], 'start': 0, 'directed': False}, {'name': 'intmax_minus_one', 'v': [1, 2], 'e': [(1, 2, 2147483646)], 'start': 1, 'directed': False}, {'name': 'intmax_sentinel', 'v': [1, 2], 'e': [(1, 2, 2147483647)], 'start': 1, 'directed': False}, {'name': 'safe_large_total', 'v': [1, 2, 3], 'e': [(1, 2, 2147483646), (2, 3, 2147483646)], 'start': 1, 'directed': False}, {'name': 'intmin_ignored', 'v': [1, 2], 'e': [(1, 2, -2147483648)], 'start': 1, 'directed': False}, {'name': 'directed_native_difference', 'v': [1, 2], 'e': [(1, 2, 3)], 'start': 1, 'directed': True}]

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
 source+=f'printf("\\nBEGIN {i}\\n");ListaArco r=grafo_kruskal(g);emit(g,r,{i});while(r){{ListaArco n=r;r=r->sig;free(n);}}release_graph(g);}}\n'
source+='return 0;}\n';(OUT/'observed-main.c').write_text(source,encoding='utf-8')
compiler=shutil.which('gcc');assert compiler;exe=OUT/'native.exe';build=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(OUT/'observed-main.c'),str(OUT/'tad_grafo.c'),str(OUT/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);(OUT/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0 and not build.stderr,build.stderr
native=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert native.returncode==0; (OUT/'native.stdout.log').write_text(native.stdout);actual={int(m[1]):json.loads(m[2]) for m in re.finditer(r'^RESULT (\d+) (.*)$',native.stdout,re.M)};assert len(actual)==len(CASES)
segments=re.split(r'\nBEGIN (\d+)\n',native.stdout);warnings={int(segments[i]):('Se detecto un ciclo negativo.' in segments[i+1]) for i in range(1,len(segments),2)};assert len(warnings)==len(CASES)
rows=[]
for i,c in enumerate(CASES):
 h=[]
 for op,p in [('create_graph',{'directed':c['directed']}),*[('insert_vertex',{'vertex':v}) for v in c['v']],*[('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in c['e']]]:
  d=S.execute_operation('graph',op,p,h);assert d['success'];h=d['history']
 before=json.loads(json.dumps(h));d=S.execute_operation('graph','run_kruskal',{},h);n=actual[i];r=d.get('result') or {}
 norm=lambda arcs:sorted((min(a,b),max(a,b),w) for a,b,w in arcs)
 rejection=c['directed']
 differences=[]
 if rejection:
  if d['success']:differences.append('missing_required_rejection')
  if c['directed'] and n['arcs']:differences.append('directed_app_rejection_native_selection')
 else:
  if not d['success']:differences.append('unexpected_rejection')
  if norm(r.get('mst_edges',[]))!=norm(n['arcs']):differences.append('edge_set')
  if r.get('total_weight')!=n['cost']:differences.append('total')
 view=S.get_view_model('graph',d['history']);row={'name':c['name'],'input':c,'native':n,'backend':{'success':d['success'],'message':d['message'],'result':d.get('result')},'differences':differences,'history_saved':sum(x['operation']=='run_kruskal' for x in d['history']),'history_reload':sum(x['operation']=='run_kruskal' for x in view['history']),'failure_history_unchanged':d['history']==before if not d['success'] else None,'instruction_verified':False}
 rows.append(row);(OUT/('case-'+str(i)+'.json')).write_text(json.dumps({'row':row,'response':d},ensure_ascii=False,indent=2),encoding='utf-8');print(c['name'],differences,flush=True)
report={'scope':'Kruskal endpoint baseline; not instruction fidelity','cases':len(rows),'downloads_sha256':downloads,'native_strict_c17':True,'rows':rows,'differences_count':sum(bool(r['differences']) for r in rows)};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
