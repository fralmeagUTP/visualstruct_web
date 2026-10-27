"""Downloaded Heap clear contract: destructor then fresh initialization."""
from pathlib import Path
import json,shutil,subprocess
import pytest
from app import create_app
from app.domain.hierarchical.tad_wrappers import MonticuloBinario

@pytest.mark.parametrize('seed,repeats',[([],1),([7],1),(list(range(21)),1),([7,-1,7],2)])
def test_heap_clear_downloaded_lifetime_and_capacity(tmp_path,seed,repeats):
 client=create_app().test_client()
 for kind,suffix in [('source','c'),('header','h')]:
  response=client.get('/help/source/binary_heap/'+kind);assert response.status_code==200
  assert response.data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes()
  (tmp_path/('tad_monticulo_binario.'+suffix)).write_bytes(response.data)
 prelude='''#include <assert.h>
#include <stdlib.h>
#include "tad_monticulo_binario.h"
static int frees,reserves;
static void audit_free(void *p){assert(p!=NULL);frees++;free(p);}
static void *audit_realloc(void *p,size_t n){reserves++;return realloc(p,n);}
#define free audit_free
#define realloc audit_realloc
'''
 source=(tmp_path/'tad_monticulo_binario.c').read_text(encoding='utf-8-sig')
 main='''\nint main(void){MonticuloBinario m;monticulo_destruir(NULL);assert(frees==0);
monticulo_inicializar(&m,MONTICULO_MIN,16);assert(m.cantidad==0&&m.capacidad==20&&m.datos!=NULL);'''
 main+=''.join('assert(monticulo_insertar(&m,'+str(v)+'));' for v in seed)
 main+='assert(m.cantidad=='+str(len(seed))+'&&m.capacidad=='+str(40 if len(seed)>20 else 20)+');'
 for iteration in range(repeats):
  main+='''{int before_free=frees,before_reserve=reserves;
monticulo_destruir(&m);assert(frees==before_free+1);assert(m.datos==NULL&&m.cantidad==0&&m.capacidad==0);
monticulo_inicializar(&m,MONTICULO_MIN,16);assert(reserves==before_reserve+1);assert(m.datos!=NULL&&m.cantidad==0&&m.capacidad==20);}
'''
 main+='monticulo_destruir(&m);assert(m.datos==NULL&&m.cantidad==0&&m.capacidad==0);return 0;}'
 (tmp_path/'probe.c').write_text(prelude+source+main,encoding='utf-8')
 gcc=shutil.which('gcc');assert gcc
 p=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'probe.c'),'-o',str(tmp_path/'probe.exe')],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr
 p=subprocess.run([str(tmp_path/'probe.exe')],capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr
 heap=MonticuloBinario(iter(seed));assert heap.capacidad()==(40 if len(seed)>20 else 20)
 for iteration in range(repeats):
  heap.limpiar();assert heap.a_lista()==[] and heap.tamano()==0 and heap.capacidad()==20
  assert heap._m.tipo==0 # MONTICULO_MIN, preserved through destroy/reinit
 max_heap=MonticuloBinario(iter(seed),min_heap=False)
 max_heap.limpiar();assert max_heap._m.tipo==1 and max_heap.capacidad()==20
 (tmp_path/'contract.json').write_text(json.dumps({'seed':seed,'repeats':repeats,'native_free_and_new_reserve':True,'python_capacity':20,'instruction_ui_signoff':False}),encoding='utf-8')
