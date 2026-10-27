"""Actual displayed leaf helper contract, not instruction/replay certification."""
from pathlib import Path
import re,json,shutil,subprocess
import pytest
from app.services.c_code_service import CCodeService

@pytest.mark.parametrize('seed,expected',[([],0),([7],1),([10,5,15,3,7,12,18],4),([1,2,3,4],1),([4,3,2,1],1)])
def test_actual_displayed_leaf_helper_against_downloaded_c_h_and_api(client,tmp_path,seed,expected):
 gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable: helper contract unverified')
 for kind,suffix in [('source','c'),('header','h')]:
  raw=client.get('/help/source/abb/'+kind).data;assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_abb.'+suffix)).read_bytes();(tmp_path/('tad_abb.'+suffix)).write_bytes(raw);assert b'abb_contarHojas' not in raw
 for value in seed:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 actual=client.post('/hierarchical/abb/operate',json={'operation':'contar_hojas','payload':{}}).json;assert actual['success'] and actual['result']==expected
 helper=CCodeService.get_structure_data('abb')['operations']['contar_hojas'];assert helper in actual['execution_trace']['source_code']
 body=re.sub(r'/\*.*?\*/','',helper,flags=re.S)
 expected_body='int abb_contarHojas(ABBNodo* nodo) { if (nodo == NULL) { return 0; } if (nodo->izquierdo == NULL && nodo->derecho == NULL) { return 1; } return abb_contarHojas(nodo->izquierdo) + abb_contarHojas(nodo->derecho); }'
 assert re.sub(r'\s','',body)==re.sub(r'\s','',expected_body) # document-only delta
 assert '@param nodo' in helper and '@return 0 para NULL' in helper and 'C no fija el orden' in helper and 'No declara locales' in helper
 seed_code=''.join(f'r=abb_insertar(r,{v});' for v in seed)
 main='#include "tad_abb.h"\n#include <assert.h>\n#include <stdio.h>\n'+helper+'\nint main(void){ABBNodo*r=NULL;'+seed_code+f'abb_inorden(r);printf("\\n");assert(abb_contarHojas(r)=={expected});abb_inorden(r);printf("\\n");abb_liberarArbol(r);return 0;}}'
 p=tmp_path/'leaves-contract.c';p.write_text(main,encoding='utf-8');exe=tmp_path/'leaves-contract.exe'
 run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_abb.c'),str(p),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
 line=''.join(str(v)+' ' for v in sorted(seed))+'\n';assert run.stdout==line+line
 (tmp_path/'contract.json').write_text(json.dumps({'seed':seed,'expected':expected,'api_result':actual['result'],'native_stdout':run.stdout,'helper':helper,'body_unchanged':True,'source_header_have_helper':False,'instruction_signoff':False},indent=2),encoding='utf-8')

from scripts.test_tool_paths import resolve_doxygen
def test_leaf_helper_doxygen_and_manual(client,tmp_path):
 helper=CCodeService.get_structure_data('abb')['operations']['contar_hojas'];p=tmp_path/'displayed-leaves.c';p.write_text(helper,encoding='utf-8')
 tool=Path(resolve_doxygen())
 if not tool.exists():pytest.skip('Doxygen unavailable: generated helper documentation unverified')
 warnings=tmp_path/'warnings.log';cfg=tmp_path/'Doxyfile';cfg.write_text('\n'.join(['PROJECT_NAME = "Displayed ABB leaves helper"','INPUT = "'+p.as_posix()+'"','OUTPUT_DIRECTORY = "'+tmp_path.as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warnings.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 run=subprocess.run([str(tool),str(cfg)],capture_output=True,text=True,timeout=60);assert run.returncode==0,run.stderr;assert warnings.read_text(encoding='utf-8')==''
 text=client.get('/help/hierarchical/abb').data.decode('utf-8');assert 'C no fija cual llamada' in text and 'no una garantia del lenguaje' in text and 'no variables locales declaradas' in text and 'no estan declarados en el C/H descargado' in text
