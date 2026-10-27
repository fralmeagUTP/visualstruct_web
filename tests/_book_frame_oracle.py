"""Contract checks for the canonical-book event and memory transport."""
import hashlib
from app.domain.graph.book_source import HASHES

def assert_book_frame(step, trace, index):
    assert trace['book_instruction_model'] is True
    assert hashlib.sha256(trace['source_code'].encode()).hexdigest()==HASHES['tad_grafo.c']
    frame=step['pedagogy'];event=frame['instruction_event']
    before,after=frame['instruction_state_before'],frame['instruction_state_after']
    assert frame['state_before']==step['state_snapshot'] and frame['state_after']==step['state_after']
    assert frame['memory_state']==after==step['debug']['graph_memory']
    assert step['debug']['stage']==event['phase']
    if index:
        prior=trace['steps'][index-1]
        assert prior['state_after']==step['state_snapshot']
        assert prior['pedagogy']['instruction_state_after']==before
    for memory in [before,after]:
        assert {'graph','frames','heap_nodes','external','retired_objects'}<=memory.keys()
        live={node['id'] for node in memory['heap_nodes']}
        assert len(live)==len(memory['heap_nodes'])
        assert live.isdisjoint(node['id'] for node in memory['retired_objects'])
        ids=[row['id'] for row in memory['frames']];assert len(set(ids))==len(ids)
    assert type(event['C_executed']) is bool
    if event['C_executed']:
        assert type(step['line_index']) is int and 0<=step['line_index']<len(trace['source_code'].splitlines())
        assert trace['source_code'].splitlines()[step['line_index']]==step['line_text']
        assert event['line_index']==step['line_index']
        if 'pos' in event:assert trace['source_code'].count('\n',0,event['pos'])==step['line_index']
        ordinal=sum(bool(s['pedagogy']['instruction_event']['C_executed']) for s in trace['steps'][:index])
        assert trace['C_instruction_events'][ordinal]==event
    else:
        assert step['line_index'] is None and step['line_text']==''
        assert event['source_role'] in {'caller','application'}
    if event['phase'] in {'condition','operand'}:assert before==after
    if event['phase']=='allocate':
        old={n['id'] for n in before['heap_nodes']};new={n['id'] for n in after['heap_nodes']}
        assert not old-new and len(new-old)<=1
        assert after['allocation_attempts']==before['allocation_attempts']+1
    if event['phase']=='free':
        old={n['id'] for n in before['heap_nodes']};new={n['id'] for n in after['heap_nodes']}
        assert not new-old and len(old-new)<=1
    if index==len(trace['steps'])-1:
        assert step['state_after']==trace['final_state']
        assert event['phase'] in {'api_publication','api_rejection'} and before==after

def assert_book_body(body):
    trace=body['execution_trace']
    assert trace['final_state']==body['visual_state']
    for index,step in enumerate(trace['steps']):assert_book_frame(step,trace,index)
    assert len(trace['C_instruction_events'])==sum(s['pedagogy']['instruction_event']['C_executed'] for s in trace['steps'])
