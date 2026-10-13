"""The explicitly retired linked-list reverse must not survive in API/downloads."""
import shutil,subprocess
import pytest
from app.adapters.linked_list_adapter import LinkedListAdapter
from app.domain.sequential import ListaEnlazada
from app.services.c_code_service import CCodeService
VISIBLE={'insertar_inicio','insertar_final','lista_insertar_elemento','buscar_elemento','eliminar_elemento','eliminar_repetidos','limpiar'}

def test_linked_reverse_retired_without_removing_required_menu_or_mutating_state(client):
 adapter=LinkedListAdapter();operations=adapter.get_supported_operations()
 assert {op['name'] for op in operations if not op.get('hidden')}==VISIBLE
 assert 'invertir' not in {op['name'] for op in operations}
 assert not hasattr(ListaEnlazada(),'invertir')
 assert 'invertir' not in CCodeService.get_structure_data('linked_list')['operations']
 assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':7}}).get_json()['success']
 response=client.post('/sequential/linked_list/operate',json={'operation':'invertir','payload':{}})
 assert response.status_code==400
 data=response.get_json();assert not data['success']
 assert 'no está soportada' in data['message'].lower()
 assert data['visual_state']['items']==[{'value':7}]
 # Circular reversal remains an existing visible contract.
 assert client.post('/sequential/circular_list/operate',json={'operation':'insertar_final','payload':{'value':1}}).get_json()['success']
 assert client.post('/sequential/circular_list/operate',json={'operation':'insertar_final','payload':{'value':2}}).get_json()['success']
 circular=client.post('/sequential/circular_list/operate',json={'operation':'invertir','payload':{}}).get_json()
 assert circular['success'] and [x['value'] for x in circular['visual_state']['items']]==[2,1]

@pytest.mark.skipif(shutil.which('gcc') is None,reason='gcc unavailable: downloaded linked contracts unverified')
def test_downloaded_linked_c_h_exclude_retired_reverse_and_execute_seven_required_methods(client,tmp_path):
 for kind,ext in [('source','c'),('header','h')]:
  response=client.get('/help/source/linked_list/'+kind);assert response.status_code==200
  text=response.data.decode('utf-8');assert 'lista_invertir' not in text
  for name in VISIBLE:
   function=name if name=='lista_insertar_elemento' else 'lista_'+name
   assert function in text
  (tmp_path/('tad_lista.'+ext)).write_bytes(response.data)
 program=r'''#include "tad_lista.h"
#include <assert.h>
#include <stddef.h>
int main(void){Tlista l=NULL;lista_insertar_inicio(&l,1);lista_insertar_final(&l,2);lista_insertar_elemento(&l,3,1);assert(l&&l->nro==3&&l->sgte->nro==1&&l->sgte->sgte->nro==2);lista_buscar_elemento(l,1);lista_eliminar_elemento(&l,1);assert(l->nro==3&&l->sgte->nro==2&&l->sgte->sgte==NULL);lista_eliminar_repetidos(&l,3);assert(l->nro==2&&l->sgte==NULL);lista_limpiar(&l);assert(l==NULL);return 0;}'''
 probe=tmp_path/'probe.c';probe.write_text(program,encoding='utf-8');exe=tmp_path/'probe.exe'
 result=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(probe),str(tmp_path/'tad_lista.c'),'-o',str(exe)],capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 result=subprocess.run([str(exe)],capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 assert 'posicion 2' in result.stdout
