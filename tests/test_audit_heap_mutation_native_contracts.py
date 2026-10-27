"""Native null, output and capacity contracts for visible Heap mutations."""
from pathlib import Path
import json,subprocess,shutil
import pytest
from app import create_app
from app.domain.hierarchical import tad_monticulo_binario as py
from test_audit_heap_list_download import heap_server,compile_download

@pytest.mark.parametrize('tipo,seed,value',[(0,[],7),(0,[7,7,7],7),(0,[-2147483648,2147483647,0,-1],-2147483648),(0,list(range(20)),-1),(1,[-2147483648,2147483647,0,-1],2147483647)])
def test_heap_native_mutation_guards_outputs_and_capacity(tmp_path,tipo,seed,value):
 client=create_app().test_client()
 for kind,suffix in [('source','c'),('header','h')]:
  raw=client.get('/help/source/binary_heap/'+kind).data;assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(tmp_path/('tad_monticulo_binario.'+suffix)).write_bytes(raw)
 program='''#include <assert.h>
#include <stdio.h>
#include "tad_monticulo_binario.h"
int main(void){MonticuloBinario m;int out=123456;assert(!monticulo_insertar(NULL,7));assert(!monticulo_extraer_raiz(NULL,&out));assert(out==123456);
'''+f'monticulo_inicializar(&m,{tipo},16);'+''.join(f'assert(monticulo_insertar(&m,{v}));' for v in seed)
 program+='''{int q=m.cantidad,c=m.capacidad,*p=m.datos,old[64];for(int i=0;i<q;i++)old[i]=p[i];
assert(!monticulo_extraer_raiz(&m,NULL));assert(m.cantidad==q&&m.capacidad==c&&m.datos==p);for(int i=0;i<q;i++)assert(p[i]==old[i]);}
'''
 program+='assert(monticulo_insertar(&m,'+str(value)+'));assert(monticulo_extraer_raiz(&m,&out));printf("%d %d %d",out,m.cantidad,m.capacidad);for(int i=0;i<m.cantidad;i++)printf(" %d",m.datos[i]);puts("");monticulo_destruir(&m);return 0;}'
 (tmp_path/'probe.c').write_text(program,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'probe.c'),str(tmp_path/'tad_monticulo_binario.c'),'-o',str(tmp_path/'probe.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(tmp_path/'probe.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;native=list(map(int,run.stdout.split()))
 assert py.monticulo_insertar(None,7) is False
 out=[123456];assert py.monticulo_extraer_raiz(None,out) is False and out==[123456]
 m=py.MonticuloBinario();py.monticulo_inicializar(m,tipo,16)
 for v in seed:assert py.monticulo_insertar(m,v)
 before=(list(m.datos),m.cantidad,m.capacidad,id(m.datos));assert py.monticulo_extraer_raiz(m,None) is False;assert (m.datos,m.cantidad,m.capacidad,id(m.datos))==before
 assert py.monticulo_insertar(m,value);assert py.monticulo_extraer_raiz(m,out)
 assert [out[0],m.cantidad,m.capacidad,*m.datos]==native
 (tmp_path/'review.json').write_text(json.dumps({'tipo':tipo,'seed':seed,'value':value,'native_result':native,'null_output_preserves_heap':True}),encoding='utf-8')

def test_heap_interpreted_mutation_order_matches_native_statement_boundaries(monkeypatch):
 m=py.MonticuloBinario();py.monticulo_inicializar(m,0,16);original_up=py._subir;seen=[]
 def up(heap,index):seen.append((heap.cantidad,index,list(heap.datos)));return original_up(heap,index)
 monkeypatch.setattr(py,'_subir',up);assert py.monticulo_insertar(m,7);assert seen==[(0,0,[7])]
 for v in [1,3,8]:py.monticulo_insertar(m,v)
 output=[];original_down=py._bajar;root=m.datos[0];old_quantity=m.cantidad
 def down(heap,index):assert output==[root] and heap.cantidad==old_quantity-1;return original_down(heap,index)
 monkeypatch.setattr(py,'_bajar',down);assert py.monticulo_extraer_raiz(m,output)

@pytest.mark.e2e
def test_heap_generated_main_int_min_printf_has_int_argument(heap_server,tmp_path):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(heap_server+'/hierarchical/binary_heap',wait_until='networkidle')
  history=[{'operation':'insertar','payloadRaw':{'value':v},'success':True} for v in [-2147483648,-2147483648,2147483647]]+[{'operation':'extraer_raiz','payloadRaw':{},'success':True} for _ in range(3)]
  main=page.evaluate('h=>buildHierMainCode("binary_heap",h,window.HIER_VIEW_MODEL.didactic)',history)
  assert '(int)(-2147483648)' in main
  stdout=compile_download(main,context,heap_server,tmp_path/'actual-main')
  assert stdout.splitlines()[:3]==['INSERTAR: -2147483648','INSERTAR: -2147483648','INSERTAR: 2147483647']
  extra=[line for line in stdout.splitlines() if line.startswith('EXTRAIDO:')]
  assert [int(line.rsplit(' ',1)[-1]) for line in extra]==[-2147483648,-2147483648,2147483647]
  browser.close()
