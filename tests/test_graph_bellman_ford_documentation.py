"""Bellman-Ford documentation on fresh actual HTTP downloads."""
from pathlib import Path
from test_graph_bfs_documentation import run_doxygen

def test_bellman_download_and_guides(client,tmp_path):
 files=[]
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for kind,ext in [('source','c'),('header','h')]:
   r=client.get('/help/source/'+tad+'/'+kind);assert r.status_code==200;p=tmp_path/(stem+'.'+ext);p.write_bytes(r.data);files.append(p)
 for ext in ['c','h']:
  s=(tmp_path/('tad_grafo.'+ext)).read_text(encoding='utf-8-sig')
  assert 'long long con alcanzabilidad separada' in s and 'INT_MAX es un costo v\u00e1lido' in s
  assert '(n-1)*INT_MIN' in s and 'suma se comprueba antes de ejecutarse' in s
 for name in ['docs/USER_GUIDE.md','docs/qa/graph-teacher-guide.md']:
  s=(Path(__file__).resolve().parents[1]/name).read_text(encoding='utf-8')
  assert '## Bellman-Ford: negativos y límites del C descargado' in s
  section=s.split('## Bellman-Ford:',1)[1].split('\n## ',1)[0]
  assert 'HTTP 400, success=false' in section and 'dos arcos INT_MIN' in section
  assert 'long long' in section and 'INT_MAX es un costo v\u00e1lido' in section
 run_doxygen(tmp_path,files)
