"""Current DFS contract and fresh callers; frozen browser artifacts remain history."""
from pathlib import Path
import pytest
from test_graph_bfs_documentation import run_doxygen
from _traversal_caller_contract import validate_caller

def test_dfs_fresh_download_contracts_and_manual(client,tmp_path):
    root=Path(__file__).resolve().parents[1];files=[]
    for kind,ext in [('source','c'),('header','h')]:
        response=client.get('/help/source/graph/'+kind);assert response.status_code==200
        path=tmp_path/('tad_grafo.'+ext);path.write_bytes(response.data);files.append(path)
        assert response.data==(root/'docs/tads_C'/path.name).read_bytes()
    header=files[1].read_text(encoding='utf-8');source=files[0].read_text(encoding='utf-8')
    assert 'ListaVertice grafo_dfs(Grafo g, int inicio, GrafoEstado *estado)' in header
    assert 'grafo_dfs_recursivo' in source and 'publicar_marcas(g, lista)' in source
    assert 'grafo_liberar_vertices(&suces)' in source
    guide=(root/'docs/USER_GUIDE.md').read_text(encoding='utf-8')
    assert 'GrafoEstado' in guide and 'resultados propios' in guide and 'NO_EXISTE' in guide
    run_doxygen(tmp_path,files)

@pytest.mark.parametrize('case',[1,3,4,5,6,7,8,9,'context'])
def test_dfs_fresh_canonical_caller_ownership_preserves_historical_case_intent(tmp_path,case):
    root=Path(__file__).resolve().parents[1]
    archived=root/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-dfs-history-context-low/browser-artifacts'/('case-'+str(case))/'main.c'
    validate_caller(root,tmp_path,'dfs',case,archived,run_doxygen)
