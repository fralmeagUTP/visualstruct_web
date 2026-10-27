"""Bellman-Ford documentation on fresh actual HTTP downloads."""
from pathlib import Path
from test_graph_bfs_documentation import run_doxygen

def test_bellman_download_and_guides(client,tmp_path):
 files=[]
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   r=client.get('/help/source/'+tad+'/'+kind);assert r.status_code==200;p=tmp_path/(stem+'.'+ext);p.write_bytes(r.data);files.append(p)
 root=Path(__file__).resolve().parents[1]
 for p in files:
  assert p.read_bytes()==(root/'docs'/'tads_C'/p.name).read_bytes()
 source=(tmp_path/'tad_grafo.c').read_text(encoding='utf-8-sig')
 header=(tmp_path/'tad_grafo.h').read_text(encoding='utf-8-sig')
 assert 'grafo_bellman_ford(' in source and 'grafo_bellman_ford(' in header
 assert 'GrafoEstado *estado' in header
 assert 'GRAFO_RANGO' in header and 'GRAFO_DESCONECTADO' in header
 assert 'sumar_seguro' in source and 'long long' in source
 assert 'grafo_liberar_arcos' in header and 'grafo_destruir' in header
 guide=(root/'docs/USER_GUIDE.md').read_text(encoding='utf-8')
 assert 'GrafoEstado' in guide and 'Bellman' in guide
 run_doxygen(tmp_path,files)
