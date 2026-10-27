"""Independent native query contracts and limits on constructed finite trees."""
from pathlib import Path
import subprocess,shutil
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.tad_wrappers import RojoNegro
from app.domain.hierarchical.tad_rojo_negro import nodoRBT,ROJO,NEGRO

def test_rbt_displayed_query_helper_contracts_and_limits(tmp_path):
 data=CCodeService.get_structure_data('red_black')['operations'];root=Path(__file__).resolve().parents[1];header=(root/'docs/tads_C/tad_rojo_negro.h').read_bytes();(tmp_path/'tad_rojo_negro.h').write_bytes(header)
 code='#include <stdio.h>\n#include "tad_rojo_negro.h"\n'+ '\n'.join(data[x] for x in ['inorden','altura','validar'])+r'''
/** @brief Exercise finite query contracts. @return 0 after all cases. */
int main(void){
 nodoRBT a={.nro=0,.rbt_color=NEGRO},l={.nro=-2147483647-1,.rbt_color=ROJO},rr={.nro=2147483647,.rbt_color=ROJO};
 puts("EMPTY");rbt_inorden(NULL);printf("\n%d %d\n",rbt_altura(NULL),rbt_validar(NULL));
 a.izq=&l;a.der=&rr;l.padre=&a;rr.padre=&a;
 puts("EXTREMA");rbt_inorden(&a);printf("\n%d %d\n",rbt_altura(&a),rbt_validar(&a));
 a.rbt_color=ROJO;printf("ROOT_RED %d\n",rbt_validar(&a));a.rbt_color=NEGRO;
 l.nro=0;printf("DUPLICATE %d\n",rbt_validar(&a));l.nro=-2147483647-1;
 l.nro=1;printf("BAD_ORDER %d\n",rbt_validar(&a));l.nro=-2147483647-1;
 nodoRBT ll={.nro=-2147483647,.rbt_color=ROJO};l.der=&ll;ll.padre=&l;printf("RED_RED %d\n",rbt_validar(&a));l.der=NULL;
 l.rbt_color=NEGRO;printf("UNEQUAL_BLACK_HEIGHT %d\n",rbt_validar(&a));
 l.padre=NULL;printf("WRONG_PARENT %d\n",rbt_validar(&a));
 printf("UNCHANGED %d %d %d %d\n",a.nro,l.nro,rr.nro,a.izq==&l&&a.der==&rr);
 return 0;
}
'''
 (tmp_path/'main.c').write_text(code,encoding='utf-8');build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),'-o',str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0;assert run.stdout=='EMPTY\n\n0 1\nEXTREMA\n-2147483648 0 2147483647 \n2 1\nROOT_RED 0\nDUPLICATE 0\nBAD_ORDER 0\nRED_RED 0\nUNEQUAL_BLACK_HEIGHT 0\nWRONG_PARENT 0\nUNCHANGED 0 -2147483648 2147483647 1\n'
 (tmp_path/'stdout.log').write_text(run.stdout)
 # Confirm the approved full validator rejects the former false-positive representation.
 a=nodoRBT(0,NEGRO);l=nodoRBT(-2147483648,NEGRO);rr=nodoRBT(2147483647,ROJO);a.izq=l;a.der=rr;l.padre=None;rr.padre=a;s=RojoNegro();s._root_ref[0]=a;assert not s.validar()
 a.rbt_color=ROJO;assert not s.validar();a.rbt_color=NEGRO;l.nro=0;assert not s.validar();l.nro=1;assert not s.validar()


def test_rbt_public_search_print_and_console_color_contract(tmp_path):
 root=Path(__file__).resolve().parents[1]
 for ext in ['c','h']:(tmp_path/('tad_rojo_negro.'+ext)).write_bytes((root/'docs/tads_C'/('tad_rojo_negro.'+ext)).read_bytes())
 code=r'''#include <stdio.h>
#include "tad_rojo_negro.h"
/** @brief Query borrowed nodes and print a rotated tree. @return 0 after checks. */
int main(void){
 nodoRBT a={.nro=10,.rbt_color=NEGRO},l={.nro=5,.rbt_color=ROJO},r={.nro=15,.rbt_color=ROJO};a.izq=&l;a.der=&r;l.padre=&a;r.padre=&a;
 printf("EMPTY_ALIAS %d",rbt_buscar(NULL,99)==NULL);
 printf("FOUND_ALIAS %d",rbt_buscar(&a,5)==&l);
 printf("ABSENT_ALIAS %d",rbt_buscar(&a,99)==NULL);
 puts("\nTREE");rbt_verArbol(&a,0);rbt_verArbol(NULL,0);rbt_color(15);
 printf("UNCHANGED %d\n",a.izq==&l&&a.der==&r&&l.padre==&a&&r.padre==&a&&a.nro==10&&l.nro==5&&r.nro==15);
 return 0;
}
'''
 (tmp_path/'main.c').write_text(code);build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_rojo_negro.c'),'-o',str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0;assert run.stdout=='\n\tEl arbol esta vacio\n\nEMPTY_ALIAS 1\n\tEl numero 5 existe en el arbol\nFOUND_ALIAS 1\n\tEl numero 99 NO existe en el arbol\nABSENT_ALIAS 1\nTREE\n   15\n10\n   5\nUNCHANGED 1\n';(tmp_path/'stdout.log').write_text(run.stdout)


def test_rbt_query_history_rebuild_does_not_execute_consultations(monkeypatch):
 from app.services.hierarchical_structure_service import HierarchicalStructureService as S
 from app.adapters.red_black_adapter import RedBlackAdapter
 calls=[];original=RedBlackAdapter.execute
 def observed(self,name,payload):
  calls.append(name);return original(self,name,payload)
 monkeypatch.setattr(RedBlackAdapter,'execute',observed)
 history=[{'operation':'insertar','payload':{'value':10}}]+[{'operation':x,'payload':{'value':10} if x=='buscar' else {}} for x in ['buscar','inorden','altura','validar','inorden','altura','validar']]
 adapter,kept=S._rebuild_adapter('red_black',history);assert kept==history;assert calls==['insertar'];assert adapter.to_visual_state()['root']['value']==10
 invalid=history+[{'operation':'buscar','payload':{'value':'invalid'}}];calls.clear();_,kept=S._rebuild_adapter('red_black',invalid);assert kept==history and calls==['insertar']
