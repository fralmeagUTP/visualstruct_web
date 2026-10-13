"""Help contracts must describe observable downloaded native C, not generic guesses."""
import shutil, subprocess
import pytest
from app.services.conformance.runner import ConformanceRunner, ScenarioOperation

@pytest.mark.skipif(shutil.which('gcc') is None,reason='gcc unavailable: native help contract unverified')
def test_help_describes_remove_all_and_priority_selection_from_actual_downloads(client,tmp_path):
 runner=ConformanceRunner()
 for tad,source in [('linked_list','tad_lista'),('priority_queue','tad_cola_prioridad')]:
  for kind,ext in [('source','c'),('header','h')]:
   response=client.get('/help/source/'+tad+'/'+kind)
   assert response.status_code==200
   (tmp_path/(source+'.'+ext)).write_bytes(response.data)
 runner.c_tads_dir=tmp_path
 source=tmp_path/'remove_all.c'
 source.write_text('#include "tad_lista.h"\n#include <assert.h>\n#include <stddef.h>\nint main(void){Tlista list=NULL;lista_insertar_final(&list,3);lista_insertar_final(&list,3);lista_insertar_final(&list,5);lista_eliminar_repetidos(&list,3);assert(list!=NULL&&list->nro==5&&list->sgte==NULL);lista_limpiar(&list);assert(list==NULL);return 0;}',encoding='utf-8')
 exe=tmp_path/'remove_all.exe'
 compiled=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(source),str(tmp_path/'tad_lista.c'),'-o',str(exe)],capture_output=True,text=True)
 assert compiled.returncode==0,compiled.stderr
 assert subprocess.run([str(exe)],capture_output=True).returncode==0
 for value in [3,3,5]:client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':value}})
 data=client.post('/sequential/linked_list/operate',json={'operation':'eliminar_repetidos','payload':{'value':3}}).get_json()
 assert [x['value'] for x in data['execution_trace']['final_state']['items']]==[5]
 priority=runner.compare('priority_queue',[ScenarioOperation('encolar',{'value':10,'priority':2}),ScenarioOperation('encolar',{'value':20,'priority':1}),ScenarioOperation('desencolar',{})])
 assert priority.equivalent
 assert priority.c_state['state']['items']==[{'value':10,'priority':2}]
 linked_help=client.get('/help/sequential/linked_list').data.decode('utf-8')
 priority_help=client.get('/help/sequential/priority_queue').data.decode('utf-8')
 hash_help=client.get('/help/hash/hash_table').data.decode('utf-8')
 assert 'Elimina todas las ocurrencias del valor solicitado' in linked_help
 assert 'conserva solo una por valor' not in linked_help
 assert 'Selecciona el nodo con menor número de prioridad' in priority_help
 assert 'Consulta el candidato de menor número de prioridad' in priority_help
 assert 'La capacidad es fija' in hash_help
 assert 'no hay resize' in hash_help
 assert 'ni rehash automático' in hash_help
 assert 'eventos de rehash al crecer' not in hash_help

def test_heap_help_distinguishes_internal_array_from_linked_nodes(client):
 text=client.get('/help/hierarchical/binary_heap').data.decode('utf-8')
 assert 'Libera el arreglo interno del montículo y lo reinicializa' in text
 assert 'Recorre la estructura liberando todos los nodos' not in text
