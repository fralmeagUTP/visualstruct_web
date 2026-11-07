from pathlib import Path
from e2e_graph_dependency_contract import verify_graph_only_bfs

def test_bfs_compiles_with_only_current_graph_source_and_header(tmp_path):
    root=Path(__file__).resolve().parents[1]/'docs/tads_C'
    verify_graph_only_bfs((root/'tad_grafo.c').read_bytes(),(root/'tad_grafo.h').read_bytes(),tmp_path)
