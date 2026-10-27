"""Compile exact frontend-generated mains; source files/TADs remain untouched."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.structure_service import StructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService

def o(name,**payload):return (name,payload)
CASES={
'queue':[o('encolar',value=10),o('encolar',value=20),o('desencolar')],
'priority_queue':[o('encolar',value=5,priority=2),o('encolar',value=9,priority=1),o('frente'),o('desencolar')],
'linked_list':[o('insertar_inicio',value=5),o('insertar_final',value=9),o('buscar_elemento',value=5),o('eliminar_elemento',value=5)],
'circular_list':[o('insertar_inicio',value=5),o('insertar_final',value=9),o('buscar_posiciones',value=5),o('eliminar_primero',value=5)],
'sublist':[o('insertar_padre',parent=1),o('insertar_hijo',parent=1,child=2),o('hijos_de',parent=1)],
'abb':[o('insertar',value=5),o('insertar',value=3),o('buscar',value=3),o('minimo'),o('maximo'),o('altura'),o('inorden'),o('preorden'),o('postorden')],
'avl':[o('insertar',value=5),o('insertar',value=3),o('buscar',value=3),o('minimo'),o('maximo'),o('altura'),o('inorden'),o('validar')],
'red_black':[o('insertar',value=5),o('insertar',value=3),o('buscar',value=3),o('altura'),o('inorden'),o('validar')],
'binary_heap':[o('insertar',value=5),o('insertar',value=3),o('raiz'),o('a_lista'),o('extraer_raiz')],
}
SOURCES=dict(zip(CASES,['tad_cola','tad_cola_prioridad','tad_lista','tad_lista_circular','tad_sublista','tad_abb','tad_avl','tad_rojo_negro','tad_monticulo_binario']))
out=ROOT.parent/'qa_frontend_main';out.mkdir(exist_ok=True);fixtures=[]
for id,ops in CASES.items():
 service=StructureService if id in ['queue','priority_queue','linked_list','circular_list','sublist'] else HierarchicalStructureService
 adapter=service._new_adapter(id);model=service.get_view_model(id,[]);entries=[]
 for name,payload in ops:
  result=adapter.execute(name,payload);entries.append(dict(name=name,payload=payload,message=result['message']))
 fixtures.append(dict(id=id,module='sequential' if service is StructureService else 'hierarchical',model=model,operations=entries))
(out/'fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False,indent=2))
subprocess.run(['node',str(ROOT/'qa/frontend_main_export.js'),str(ROOT),str(out/'fixtures.json'),str(out)],check=True)
results=[]
for id in CASES:
 tad_object=out/f'{id}-tad.o'
 subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-c',str(ROOT/'docs/tads_C'/f'{SOURCES[id]}.c'),'-o',str(tad_object)],check=True)
 for mode in ['exact','diagnostic_forced_headers']:
  exe=out/f'{id}-{mode}';command=['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'docs/tads_C')]
  if mode!='exact':command+=['-include','stdio.h','-include',SOURCES[id]+'.h']
  command += [str(out/f'{id}.c'),str(tad_object),'-o',str(exe)]
  compiled=subprocess.run(command,text=True,capture_output=True)
  (out/f'{id}-{mode}.log').write_text(compiled.stdout+compiled.stderr)
  result=dict(structure=id,mode=mode,compiled=compiled.returncode==0,command=command,errors=compiled.stderr)
  if compiled.returncode==0:
   run=subprocess.run([str(exe)],text=True,capture_output=True,timeout=10);result.update(exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr)
  results.append(result);print(id,mode,'PASS' if compiled.returncode==0 else 'FAIL',flush=True)
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
exact_results=[result for result in results if result['mode']=='exact']
if not all(result['compiled'] and result.get('exit_code')==0 for result in exact_results):
    raise SystemExit('FAIL: at least one exact frontend main failed to compile or execute; see results.json')
