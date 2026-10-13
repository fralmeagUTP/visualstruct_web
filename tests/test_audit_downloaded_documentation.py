"""Validate documentation against executed C downloaded through the app."""
import re, shutil, subprocess
import pytest

def test_downloaded_sorting_error_contract_matches_native_behavior_and_manual(client,tmp_path):
 compiler=shutil.which('gcc')
 if not compiler:pytest.skip('gcc unavailable: native documentation contract not executed')
 files={}
 for kind,ext in [('source','c'),('header','h')]:
  response=client.get('/help/source/sorting_array/'+kind)
  assert response.status_code==200
  files[ext]=response.data.decode('utf-8-sig')
  (tmp_path/('tad_ordenamiento.'+ext)).write_bytes(response.data)
 for function in ['ordenar_mergesort','ordenar_counting_sort','ordenar_binsort','ordenar_radixsort']:
  for source in files.values():
   block=re.search(r'/\*\*(?:(?!/\*\*).)*?\*/\s*int\s+'+function+r'\s*\(',source,re.S).group()
   assert 'arreglo NULL' in block and 'n == 0' in block and 'memoria' in block
   if function in ['ordenar_counting_sort','ordenar_binsort']:
    assert 'ORDENAMIENTO_RANGO_MAX' in block and 'tamaño no representable' in block
 code=r'''
#include "tad_ordenamiento.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
int main(void) {
 int values[]={-1,3,0}, huge[]={INT_MIN,INT_MAX};
 int (*methods[])(int[],size_t)={ordenar_mergesort,ordenar_counting_sort,ordenar_binsort,ordenar_radixsort};
 for(size_t i=0;i<4;i++){
  assert(methods[i](NULL,1)==ORDENAMIENTO_ERROR);
  assert(methods[i](values,0)==ORDENAMIENTO_ERROR);
  int ordinary[]={3,-1,0};
  assert(methods[i](ordinary,3)==ORDENAMIENTO_OK);
  assert(ordinary[0]==-1&&ordinary[1]==0&&ordinary[2]==3);
 }
 assert(ordenar_counting_sort(huge,2)==ORDENAMIENTO_ERROR);
 assert(ordenar_binsort(huge,2)==ORDENAMIENTO_ERROR);
 assert(huge[0]==INT_MIN&&huge[1]==INT_MAX);
 puts("14 native return/status cases passed");
 return 0;
}
'''
 (tmp_path/'oracle.c').write_text(code,encoding='utf-8')
 exe=tmp_path/'oracle.exe'
 compiled=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'oracle.c'),str(tmp_path/'tad_ordenamiento.c'),'-o',str(exe)],capture_output=True,text=True)
 assert compiled.returncode==0,compiled.stderr
 native=subprocess.run([str(exe)],capture_output=True,text=True)
 assert native.returncode==0,native.stderr
 assert '14 native return/status cases passed' in native.stdout
 manual=client.get('/help/manual')
 assert manual.status_code==200
 text=manual.data.decode('utf-8')
 assert 'ORDENAMIENTO_RANGO_MAX' in text
 assert 'no incluyen un programa principal' in text
 assert 'Binsort delega en Counting Sort' in text
