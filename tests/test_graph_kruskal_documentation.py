"""Fresh Kruskal HTTP documentation; instruction fidelity remains separate."""
from pathlib import Path
from test_graph_bfs_documentation import run_doxygen

def test_kruskal_download_docs(client,tmp_path):
 files=[]
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   r=client.get('/help/source/'+tad+'/'+kind);assert r.status_code==200;p=tmp_path/(stem+'.'+ext);p.write_bytes(r.data);files.append(p)
 for ext in ['c','h']:
  s=(tmp_path/('tad_grafo.'+ext)).read_text(encoding='utf-8-sig')
  assert 'ordena punteros a arcos por burbuja estable' in s and 'El C no tiene bandera dirigida' in s
 for name in ['docs/USER_GUIDE.md','docs/qa/graph-teacher-guide.md']:
  s=(Path(__file__).resolve().parents[1]/name).read_text(encoding='utf-8')
  assert '## Kruskal: contrato del C descargado' in s and 'arcos simétricos' in s
 run_doxygen(tmp_path,files)
