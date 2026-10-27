"""Whole-trace exact compatibility and independent frozen JSON fixtures."""
from pathlib import Path
import gzip,json
import pytest
from _graph_snapshot_cases import CASES,arguments
from app.domain.graph.numeric_instruction import build_graph_numeric_trace
from app.domain.graph.snapshot_pool import SnapshotPool,expand_graph_trace,CODEC,REFERENCE

def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))

@pytest.mark.parametrize('case',CASES)
def test_every_expanded_event_field_state_and_type_equal_pre_codec_fixture(case):
 expected=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/graph_snapshot_expanded'/f'{case}.json.gz').read_bytes()))
 compact=build_graph_numeric_trace(**arguments(case));expanded=expand_graph_trace(compact)
 assert compact['graph_snapshot_codec']==CODEC
 assert canonical(expanded)==canonical(expected)
 assert expanded['C_instruction_events']==expected['C_instruction_events']
 assert len(expanded['steps'])==len(expected['steps'])
 assert len(canonical(compact))<len(canonical(expected))//4
 # Same logical snapshots share storage instead of copying graph state per line.
 if len(expanded['steps'])>2:assert expanded['steps'][1]['state_snapshot'] is expanded['steps'][0]['state_after']

@pytest.mark.parametrize('reference',[-1,0,True,1.0,999])
def test_forward_out_of_range_or_non_integer_reference_never_invents_state(reference):
 trace={'graph_snapshot_codec':CODEC,'graph_snapshot_pool':[[1,[{REFERENCE:reference}]]],'steps':[]}
 with pytest.raises(ValueError):expand_graph_trace(trace)

def test_boolean_integer_float_and_reserved_key_values_roundtrip_without_alias_confusion():
 pool=SnapshotPool();step={'line_index':0,'console':[],'state_snapshot':{'x':True},'state_after':{'x':1},'debug':{'x':1.0},'pedagogy':{'literal':{REFERENCE:99},'empty':[]}}
 trace={'steps':[pool.intern(step)],'numeric_C_memory':{'returned':None},'C_instruction_events':[]}
 restored=expand_graph_trace(pool.pack(trace));assert canonical(restored)==canonical(trace)
 assert type(restored['steps'][0]['state_snapshot']['x']) is bool
 assert type(restored['steps'][0]['state_after']['x']) is int
 assert type(restored['steps'][0]['debug']['x']) is float

