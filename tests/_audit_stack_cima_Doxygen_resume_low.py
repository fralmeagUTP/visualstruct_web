"""Resume Doxygen only; preserve completed native/browser executions and their logs."""
from pathlib import Path
import sys,json,hashlib,re
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from tests.test_graph_bfs_documentation import run_doxygen
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-cima-baseline-low';N=E/'native';O=E/'caller-ownership';D=E/'caller-doxygen';cases=[('empty',[]),('top',[9,17,3]),('bounds',[-2147483648,0,2147483647]),('minus1',[-1])];rows=[]
# Original observer completed/asserted all native loops, then failed to find PATH Doxygen.
assert 'line 38' in (E/'browser-caller-Doxygen-discovery-failure.log').read_text()
for name,values in cases:
 runs={};expected=''.join('push:'+str(v)+'\n' for v in reversed(values))+'state:['+','.join(map(str,values))+']\n'
 for label in ['C17','ownership']:
  assert not (O/name/(label+'-compile.log')).read_text().strip()
  log=(O/name/(label+'-run.log')).read_text();assert log.startswith(expected);suffix=log[len(expected):]
  assert suffix==('OWNERSHIP '+str(len(values))+' '+str(len(values))+' 0\n' if label=='ownership' and values else '')
  runs[label]={'exit':0,'stdout':expected,'stderr':suffix,'exit_provenance':'Completed original observer asserts exit0 before Doxygen discovery failure; exact logs recovered, no rerun'}
 faults=[]
 for point in range(1,len(values)+1):
  log=(O/name/f'NULL-{point}.log').read_text();assert f'OWNERSHIP {point-1} {point-1} 0' in log;faults.append({'point':point,'exit':1,'stderr':log,'exit_provenance':'Completed original observer asserts exit1 before Doxygen failure'})
 main=E/'actual-callers'/name/'main.c';rows.append({'case':name,'SHA':hashlib.sha256(main.read_bytes()).hexdigest(),'runs':runs,'alloc':len(values),'free':len(values),'live':0,'faults':faults,'scope':'3actualDOM+HTTP callers and emptyHTTP-only main; rejected query not recorded. Integrated setup Cima calls only.'})
inputs=[N/'tad_pila.c',N/'tad_pila.h']+[E/'actual-callers'/name/'main.c' for name,_ in cases];run_doxygen(D,inputs)
import xml.etree.ElementTree as ET
mains=[];symbols=[]
for p in (D/'doxygen/xml').glob('*.xml'):
 for symbol in ET.parse(p).findall('.//memberdef'):
  if symbol.findtext('name') in ('main','pila_cima'):symbols.append({'file':p.name,'name':symbol.findtext('name'),'documented':bool(''.join(symbol.find('briefdescription').itertext()).strip())})
mains=[x for x in symbols if x['name']=='main'];assert len(mains)==4 and all(x['documented'] for x in symbols)
(E/'caller-report.json').write_text(json.dumps({'cases':rows,'Doxygen_warnings':0,'documented_mains':4,'inputs':6,'public_Cima_doc_verified':True,'documented_symbols':symbols,'limits':'Ownership7/7/0 and7controlledNULL belong setup/cleanup. No independent accepted query in caller; no OOM/sanitizer certification. Doxygen resumed only using installed tool in C artifact directory; all tested sources canonical D copies.'},indent=2)+'\n',encoding='utf-8');print('Doxygen resumed:0warnings4mains+publicCima documented; recovered 4C17caller exits/7allocfree0live7NULL, no rerun')
