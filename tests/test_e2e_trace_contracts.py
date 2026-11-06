"""Finite stdout checks keep whitespace, duplicates, snapshots and causal order."""
import pytest
from e2e_trace_contracts import trace_stdout

@pytest.mark.parametrize('mode,expected', [
    ('events', ['', ' same \n', ' same \n\n same \n\n', ' same \n\n same \n\n\nlast']),
    ('snapshot', ['', ' same \n', ' same \n\n', 'last']),
])
def test_trace_stdout_preserves_every_chunk_and_cursor(mode, expected):
    trace={'console_mode':mode,'steps':[{'console':[' same \n']},
           {'console':[' same \n','']},{'console':['last']}]}
    assert [trace_stdout(trace,i) for i in range(-1,3)]==expected
    assert [trace_stdout(trace,i) for i in range(2,-2,-1)]==expected[::-1]


def test_raw_stdout_takes_precedence_without_normalizing_bytes():
    trace={'steps':[{'console_stdout':' 7\n7\n','console':['host feedback']} ]}
    assert trace_stdout(trace,-1)==''
    assert trace_stdout(trace,0)==' 7\n7\n'

@pytest.mark.parametrize('trace,cursor',[
    ({'steps':[{'console_stdout':None}]},0),
    ({'console_mode':'unknown','steps':[{'console':[]}]},0),
    ({'console_mode':'events','steps':[{'console':[7]}]},0),
    ({'steps':[{}]},1),
    ({'steps':[{}]},-2),
])
def test_stdout_observer_rejects_uncontracted_or_invalid_data(trace,cursor):
    with pytest.raises(AssertionError):trace_stdout(trace,cursor)
