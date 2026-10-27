"""Enumerate successful adapter operations and compile the UI main for each."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.structure_service import StructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
SEEDS={
'queue':[('encolar',{'value':5}),('encolar',{'value':9})],
'priority_queue':[('encolar',{'value':5,'priority':2}),('encolar',{'value':9,'priority':1})],
'linked_list':[('insertar_inicio',{'value':5}),('insertar_final',{'value':9})],
'circular_list':[('insertar_inicio',{'value':5}),('insertar_final',{'value':9})],
'sublist':[('insertar_padre',{'parent':1}),('insertar_hijo',{'parent':1,'child':2})],
'abb':[('insertar',{'value':5}),('insertar',{'value':9})],
'avl':[('insertar',{'value':5}),('insertar',{'value':9})],
'red_black':[('insertar',{'value':5}),('insertar',{'value':9})],
'binary_heap':[('insertar',{'value':5}),('insertar',{'value':9})],
}
SOURCES=dict(zip(SEEDS,['tad_cola','tad_cola_prioridad','tad_lista','tad_lista_circular','tad_sublista','tad_abb','tad_avl','tad_rojo_negro','tad_monticulo_binario']))
out=ROOT.parent/'qa_frontend_main_matrix';out.mkdir(exist_ok=True);fixtures=[]
for id,seeds in SEEDS.items():
 service=StructureService if id in list(SEEDS)[:5] else HierarchicalStructureService
 model=service.get_view_model(id,[])
 for op in model['operations']:
  adapter=service._new_adapter(id);entries=[]
  payload={f['name']:{'value':5,'priority':1,'parent':1,'child':2,'position':1,'relative':0}[f['name']] for f in op['inputs']}
  if op['name']=='insertar':payload['value']=7
  if op['name']=='insertar_padre':payload['parent']=3
  for name,params in seeds+[(op['name'],payload)]:
   r=adapter.execute(name,params);entries.append(dict(name=name,payload=params,message=r['message']))
  fixtures.append(dict(case_name=id+'__'+op['name'],id=id,module='sequential' if service is StructureService else 'hierarchical',model=model,operations=entries))
(out/'fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False,indent=2))
subprocess.run(['node',str(ROOT/'qa/frontend_main_export.js'),str(ROOT),str(out/'fixtures.json'),str(out)],check=True)
results=[]
for id in SEEDS:
 subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-c',str(ROOT/'docs/tads_C'/f'{SOURCES[id]}.c'),'-o',str(out/f'{id}-tad.o')],check=True)
for test in fixtures:
 id,case=test['id'],test['case_name'];exe=out/case
 command=['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'docs/tads_C'),str(out/f'{case}.c'),str(out/f'{id}-tad.o'),'-o',str(exe)]
 r=subprocess.run(command,text=True,capture_output=True);record=dict(case=case,compiled=r.returncode==0,errors=r.stderr)
 if r.returncode==0:
  run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);record.update(exit_code=run.returncode,stdout=run.stdout)
 results.append(record)
(out/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
print('Exact frontend main compile:',sum(r['compiled'] for r in results),'/',len(results))
for r in results:
 if not r['compiled']:print(r['case'],next((s for s in r['errors'].splitlines() if 'error:' in s),'unknown'))
if not all(result['compiled'] and result.get('exit_code')==0 for result in results):
    raise SystemExit('FAIL: at least one frontend operation main failed to compile or execute; see results.json')
