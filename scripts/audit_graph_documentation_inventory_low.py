"""Fresh all-TAD HTTP/Doxygen documentary inventory; no closed functional oracle reruns."""
from pathlib import Path
import sys,json,hashlib,collections,xml.etree.ElementTree as ET,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from app import create_app
from test_graph_bfs_documentation import run_doxygen
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
PAIRS=[('stack','tad_pila'),('queue','tad_cola'),('priority_queue','tad_cola_prioridad'),('linked_list','tad_lista'),('circular_list','tad_lista_circular'),('sublist','tad_sublista'),('abb','tad_abb'),('avl','tad_avl'),('red_black','tad_rojo_negro'),('binary_heap','tad_monticulo_binario'),('graph','tad_grafo'),('hash_table','tad_tabla_hash'),('sorting_array','tad_ordenamiento')]
client=create_app().test_client();files=[];hashes={}
for tad,stem in PAIRS:
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/'+tad+'/'+kind);assert r.status_code==200,(tad,kind,r.status_code)
  p=OUT/(stem+'.'+ext);p.write_bytes(r.data);assert r.data==(ROOT/'docs/tads_C'/p.name).read_bytes();files.append(p);hashes[p.name]=hashlib.sha256(r.data).hexdigest()
run_doxygen(OUT,files)
# Test real Union-Find helpers in the downloaded translation unit, no reimplementation.
source=r"""#include "tad_grafo.c"
#include <assert.h>
int main(void){int parent[4]={0,0,1,3};Conjunto c={parent,4};
 assert(grafo_encontrar_conjunto(NULL,0)==-1);Conjunto empty={NULL,4};assert(grafo_encontrar_conjunto(&empty,0)==-1);
 assert(grafo_encontrar_conjunto(&c,-1)==-1);assert(grafo_encontrar_conjunto(&c,4)==-1);
 assert(grafo_encontrar_conjunto(&c,2)==0&&parent[2]==0);
 grafo_unir_conjuntos(&c,2,3);assert(parent[3]==0);grafo_unir_conjuntos(&c,-1,3);assert(parent[3]==0);
 grafo_unir_conjuntos(NULL,0,1);grafo_unir_conjuntos(&c,1,2);assert(parent[0]==0);return 0;}
"""
(OUT/'union-find-helpers.c').write_text(source,encoding='utf-8');compiler=shutil.which('gcc');assert compiler
p=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(OUT/'union-find-helpers.c'),str(OUT/'tad_cola.c'),'-o',str(OUT/'union-find-helpers.exe')],capture_output=True,text=True,timeout=30);(OUT/'helpers-compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0 and not p.stderr,p.stderr
p=subprocess.run([str(OUT/'union-find-helpers.exe')],capture_output=True,text=True,timeout=10);(OUT/'helpers-run.log').write_text(p.stdout+p.stderr);assert p.returncode==0
base=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';ledger=base/'evidence/visible-linked-six-method-review/documentation-symbol-signoff-ledger.json';shutil.copy2(ledger,OUT/'ledger-before.json');shutil.copy2(base/'documentation-symbol-signoff-ledger.md',OUT/'ledger-before.md');d=json.loads(ledger.read_text(encoding='utf-8'));decl={};members=0
for p in (OUT/'doxygen/xml').glob('*.xml'):
 t=ET.parse(p)
 for m in t.findall('.//memberdef'):
  members+=1
  if m.attrib.get('kind')!='function':continue
  name=m.findtext('name');loc=m.find('location')
  if loc is None:continue
  file=Path(loc.attrib.get('file','')).name
  if file not in hashes:continue
  key=(Path(file).stem,name);row={'file':file,'line':int(loc.attrib['line']),'sha256':hashes[file]};decl.setdefault(key,[])
  if row not in decl[key]:decl[key].append(row)
review={'grafo_bellman_ford':'visible-graph-bellman-ford-baseline-low:20native cases, numeric/cycle guards and NULL/ownership notes; instruction pending','grafo_prim':'visible-graph-prim-baseline-low:17native cases, forest/negative/sentinel/tie/direction notes and3actual callers; instruction pending','grafo_kruskal':'visible-graph-kruskal-baseline-low:17native cases, stable bubble/negative/extremes/symmetric/forest/direction/NULL and ownership notes; instruction pending','grafo_encontrar_conjunto':'visible-graph-kruskal-baseline-low/documentation-inventory: actual downloaded C17 helper NULL/invalid index/root/compression asserts; parent array valid acyclic precondition, recursion not cycle-safe','grafo_unir_conjuntos':'visible-graph-kruskal-baseline-low/documentation-inventory: actual downloaded C17 helper union/NULL/invalid/no-op asserts; root y linked to root x without rank'}
for entity in d['entities']:
 key=(entity['tad_file_base'],entity['symbol']);assert key in decl,key
 entity['declarations']=sorted(decl[key],key=lambda x:x['file'])
 if entity['tad_file_base']=='tad_grafo' and entity['symbol'] in review:
  assert entity['status']=='semantic_documentation_signoff_not_recorded',(entity['symbol'],entity['status'])
  entity['status']='code_contract_reviewed_for_current_graph_shortest_mst_low';entity['evidence']='evidence/'+review[entity['symbol']]
d['source']+=' All26HTTP C/H refreshed with matching canonical bytes and collective Doxygen0; every declaration SHA/line refreshed from current XML. Five additional individual graph contracts reviewed, normal allocation only; no instruction or global QA closure.'
d['status_counts']=dict(collections.Counter(x['status'] for x in d['entities']));d['declaration_records']=sum(len(x['declarations']) for x in d['entities']);d['xml_member_records']=members
ledger.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
reviewed=sum(n for status,n in d['status_counts'].items() if status.startswith('code_contract_reviewed'));pending=len(d['entities'])-reviewed
lines=['# Exactitud documental: pendientes por símbolo','',f'Inventario actual: {len(d["entities"])} entidades de función; {d["declaration_records"]} declaraciones C/H; {members} miembros XML. {reviewed} contratos revisados individualmente; {pending} pendientes. Derivado del ledger JSON, no contador independiente.','', '| Archivo base | Símbolos pendientes |','|---|---|']
for stem in sorted({e['tad_file_base'] for e in d['entities']}):
 symbols=[e['symbol'] for e in d['entities'] if e['tad_file_base']==stem and not e['status'].startswith('code_contract_reviewed')]
 if symbols:lines.append('| '+stem+' | '+', '.join(symbols)+' |')
lines+=['','Evidencia nueva:evidence/visible-graph-kruskal-baseline-low/documentation-inventory;26descargas HTTP,hashes canónicos,XML colectivo/Doxygen0 y2helpers C17. Los cinco contratos añadidos son Bellman-Ford,Prim,Kruskal y2helpers Union-Find; conserva el resto de evidencia previa. Doxygen0 no demuestra exactitud general.','Normal allocation only; no fidelity-by-instruction signoff, malloc-failure injection, all-input proof or global audit closure. Numerical/decimal/cycle decisions remain pending.']
(base/'documentation-symbol-signoff-ledger.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
summary={'downloads':26,'hashes':hashes,'doxygen_warnings':0,'function_entities':len(d['entities']),'declaration_records':d['declaration_records'],'xml_member_records':members,'reviewed':reviewed,'pending':pending,'new_symbols':list(review),'union_find_helpers_strict_c17':True,'limits':['documentation inventory only; no closed functional reruns','normal allocation','instruction fidelity remains open']};(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
