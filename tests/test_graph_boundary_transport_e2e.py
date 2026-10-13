"""Exercise actual compact HTTP packets through unchanged bidirectional players."""
import pytest
from app.config import Config
from app.domain.graph.snapshot_pool import expand_graph_trace
from test_graph_vertex_instruction_e2e import test_vertex_actual_player_reverse_and_reload_no_redispatch as _vertex
from test_graph_bfs_instruction_e2e import test_bfs_actual_browser_views_and_caller as _bfs
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('case',['vertex','bfs'])
def test_existing_real_DOM_oracle_after_lossless_HTTP_decode(tmp_path,monkeypatch,case):
    from playwright.sync_api import Response
    monkeypatch.setattr(Config,'SESSION_CACHE_DIR',str(tmp_path/'private-sessions'))
    monkeypatch.setattr(Config,'SECRET_KEY','graph-boundary-private')
    monkeypatch.setattr(Config,'TESTING',True,raising=False)
    original=Response.json;packets=[]
    def decoded(response):
        data=original(response)
        if isinstance(data,dict) and isinstance(data.get('execution_trace'),dict):
            trace=data['execution_trace'];assert trace['graph_snapshot_codec']=='graph-snapshot-pool/v1'
            assert trace['graph_snapshot_stats']['sampling'] is False
            packets.append(trace['graph_snapshot_stats'])
            data={**data,'execution_trace':expand_graph_trace(trace)}
        return data
    monkeypatch.setattr(Response,'json',decoded)
    if case=='vertex':_vertex(tmp_path,'insert_vertex',[],7,False)
    else:_bfs(tmp_path,3)
    assert packets

