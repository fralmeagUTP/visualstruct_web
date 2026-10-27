"""Current downloadable BFS contract and fresh caller ownership; archives retained."""
from pathlib import Path
import hashlib,json,subprocess
import pytest
from scripts.test_tool_paths import resolve_doxygen
from _traversal_caller_contract import validate_caller

def run_doxygen(target,inputs):
    # Document canonical structs/fields externally: protected C/H remain exact,
    # and all existing undocumented/doc-error/parameter checks stay enabled.
    if any(path.name in {'tad_grafo.c','tad_grafo.h'} for path in inputs):
        inputs=[*inputs,Path(__file__).resolve().parents[1]/'docs/graph-book-api.dox']
    warning=target/'warnings.log';cfg=target/'Doxyfile'
    cfg.write_text('\n'.join(['INPUT = '+' '.join('"'+p.as_posix()+'"' for p in inputs),'OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warning.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
    result=subprocess.run([resolve_doxygen(),str(cfg)],capture_output=True,text=True,timeout=45)
    assert result.returncode==0 and warning.read_text(encoding='utf-8')=='',(result.stderr,warning.read_text(encoding='utf-8'))

def test_bfs_fresh_download_contracts_and_manual(client,tmp_path):
    files=[];hashes={};root=Path(__file__).resolve().parents[1]
    for kind,ext in [('source','c'),('header','h')]:
        response=client.get('/help/source/graph/'+kind);assert response.status_code==200
        path=tmp_path/('tad_grafo.'+ext);path.write_bytes(response.data);files.append(path)
        assert response.data==(root/'docs/tads_C'/path.name).read_bytes()
        hashes[path.name]=hashlib.sha256(response.data).hexdigest()
    header=files[1].read_text(encoding='utf-8')
    assert 'ListaVertice grafo_bfs(Grafo g, int inicio, GrafoEstado *estado)' in header
    assert 'GRAFO_MEMORIA' in header and 'GRAFO_NO_EXISTE' in header
    assert 'void grafo_liberar_vertices(ListaVertice *lista)' in header
    source=files[0].read_text(encoding='utf-8')
    assert 't.prev[final++] = s' in source and 'publicar_marcas(g, lista)' in source
    guide=(root/'docs/USER_GUIDE.md').read_text(encoding='utf-8')
    assert 'GrafoEstado' in guide and 'resultados propios' in guide and 'listas' in guide
    run_doxygen(tmp_path,files)
    (tmp_path/'download-review.json').write_text(json.dumps({'hashes':hashes,'doxygen_warnings':0,'contract':'graph-book/v1','native_instruction_parity_claim':False}),encoding='utf-8')

@pytest.mark.parametrize('case',[1,3,4,5,6,7,8,9])
def test_bfs_fresh_canonical_caller_ownership_preserves_historical_case_intent(tmp_path,case):
    root=Path(__file__).resolve().parents[1]
    archived=root/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-bfs-instruction-review/browser-artifacts'/('case-'+str(case))/'main.c'
    validate_caller(root,tmp_path,'bfs',case,archived,run_doxygen)
