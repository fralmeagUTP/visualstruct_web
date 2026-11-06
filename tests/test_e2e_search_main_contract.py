"""Native evidence for current history query callers; no browser claim."""
import json, re, subprocess
from pathlib import Path
import pytest
from app.services.structure_service import StructureService
from e2e_contract_helpers import observe_before_cleanup

ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('family,search,stem,cleanup,observe',[
 ('linked_list','buscar_elemento','tad_lista','lista_limpiar(&lista);','printf("AUDIT:");for(Tlista p=lista;p!=NULL;p=p->sgte)printf(" %d",p->nro);printf("\\n");'),
 ('circular_list','buscar_posiciones','tad_lista_circular','lcir_destruir(&lc);','int values[32];int count=lcir_copiar_valores(&lc,values,32);printf("AUDIT:");for(int i=0;i<count;i++)printf(" %d",values[i]);printf("\\n");'),
])
def test_history_search_executes_real_query_before_final_cleanup(tmp_path,family,search,stem,cleanup,observe):
 operations=[{'name':'insertar_final','payload':{'value':v},'message':'insert'} for v in [7,7,9]]
 operations += [{'name':search,'payload':{'value':v},'message':'query'} for v in [7,7,99]]
 fixture=[{'id':family,'module':'sequential','model':StructureService.get_view_model(family,[]),'operations':operations}]
 path=tmp_path/'fixture.json';path.write_text(json.dumps(fixture))
 subprocess.run(['node',str(ROOT/'qa/frontend_main_export.js'),str(ROOT),str(path),str(tmp_path)],check=True)
 main=(tmp_path/(family+'.c')).read_text()
 observed=observe_before_cleanup(main,cleanup,observe)
 assert observed.replace('    '+observe+'\n','')==main
 for label,code in [('original',main),('observed',observed)]:
  source=tmp_path/(label+'.c');source.write_text(code)
  built=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(ROOT/'docs/tads_C'),str(ROOT/'docs/tads_C'/f'{stem}.c'),str(source),'-o',str(tmp_path/label)],capture_output=True,text=True,timeout=30)
  assert built.returncode==0,built.stderr
  run=subprocess.run([str(tmp_path/label)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
  if label=='observed':assert 'AUDIT: 7 7 9' in run.stdout.splitlines()
  if family=='circular_list':assert [l for l in run.stdout.splitlines() if l.startswith('Posiciones:')]==['Posiciones: 1 2','Posiciones: 1 2','Posiciones:']
  else:
   for position in [1,2]:assert len(re.findall(fr'Encontrado en la posicion {position}\b',run.stdout))==2
   assert 'Numero no encontrado' in run.stdout
