"""Downloaded heap C/H contracts: null guards, output writes and caller allocation failure."""
import subprocess,shutil
from pathlib import Path

PROBE=r'''#include "tad_monticulo_binario.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
/** @brief Check raw root/copy guards without inventing mutations. @return 0 on success. */
int main(void){
 int output=9876, dest[4]={111,222,333,444};
 assert(!monticulo_raiz(NULL,&output) && output==9876);
 assert(monticulo_copiar_valores(NULL,dest,4)==0 && dest[0]==111);
 for(int type=0;type<2;type++){
  MonticuloBinario m;monticulo_inicializar(&m,(TipoMonticulo)type,16);
  assert(!monticulo_raiz(&m,&output) && output==9876);
  assert(monticulo_copiar_valores(&m,dest,4)==0 && dest[0]==111);
  int seed[]={7,-1,7,0};for(int i=0;i<4;i++)assert(monticulo_insertar(&m,seed[i]));
  int snapshot[4];memcpy(snapshot,m.datos,sizeof snapshot);int *identity=m.datos;int capacity=m.capacidad;
  assert(!monticulo_raiz(&m,NULL));assert(monticulo_raiz(&m,&output));assert(output==(type ? 7 : -1));
  assert(monticulo_copiar_valores(&m,NULL,4)==0);
  assert(monticulo_copiar_valores(&m,dest,0)==0 && dest[0]==111);
  assert(monticulo_copiar_valores(&m,dest,-5)==0 && dest[0]==111);
  assert(monticulo_copiar_valores(&m,dest,2)==2);
  assert(dest[0]==snapshot[0] && dest[1]==snapshot[1] && dest[2]==333 && dest[3]==444);
  assert(m.datos==identity && m.cantidad==4 && m.capacidad==capacity && !memcmp(snapshot,m.datos,sizeof snapshot));
  monticulo_destruir(&m);dest[0]=111;dest[1]=222;output=9876;
 }
 puts("ROOT/COPY CONTRACTS OK");return 0;
}'''

def test_downloaded_heap_raw_query_contracts(client,tmp_path):
 for kind,suffix in [('source','c'),('header','h')]:
  r=client.get('/help/source/binary_heap/'+kind);assert r.status_code==200
  assert r.data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes()
  text=r.data.decode('utf-8-sig');assert 'Si devuelve false, no escribe resultado' in text and 'no un orden total' in text
  (tmp_path/('tad_monticulo_binario.'+suffix)).write_bytes(r.data)
 (tmp_path/'probe.c').write_text(PROBE,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'probe.c'),str(tmp_path/'tad_monticulo_binario.c'),'-o',str(tmp_path/'probe.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(tmp_path/'probe.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0 and run.stdout=='ROOT/COPY CONTRACTS OK\n'
