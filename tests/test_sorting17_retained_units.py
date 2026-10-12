"""Finite retained-body semantics; sorted output is not C instruction certification."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import hashlib
import pytest
from app.domain.sorting.tad_ordenamiento import SortingInterpreter

CASES = [pytest.param([1,2,3,4],id="ordered"),pytest.param([4,3,2,1],id="reverse"),pytest.param([2,2,1,1],id="duplicates"),pytest.param([-3,0,-1,0],id="mixed")]
def context(name):
    try:
        import coverage
    except ImportError:
        return
    c=coverage.Coverage.current()
    if c is not None:
        c.switch_context(name)

def invariants(obj,original):
    assert len(obj.values)==len(original)
    assert Counter(obj.values)==Counter(original)
    previous={"comparisons":0,"swaps":0,"moves":0}
    assert obj.metrics.steps==len(obj._steps)
    snapshots=[]
    for index,step in enumerate(obj._steps,1):
        assert step["step"]==index
        assert len(step["array_snapshot"])==len(original)
        snapshots.append(step["array_snapshot"])
        for key,value in step["metrics"].items():
            assert isinstance(value,int) and value>=previous[key]
            previous[key]=value
        for field in ["comparing_indices","swapping_indices","sorted_indices","pointer_indices"]:
            assert all(isinstance(i,int) and 0<=i<len(original) for i in step[field])
        if step["active_range"] is not None:
            left,right=step["active_range"]
            assert 0<=left<=right<len(original)
        if step["pivot_index"] is not None:assert 0<=step["pivot_index"]<len(original)
    assert len({id(s) for s in snapshots})==len(snapshots)
    assert all(s is not obj.values for s in snapshots)
    saved=deepcopy(obj._steps);final=list(obj.values)
    obj.values[0]+=10000
    assert obj._steps==saved
    obj.values[:]=final
    if snapshots:
        before=list(obj.values);other=deepcopy(obj._steps[1:])
        snapshots[0][0]+=20000
        assert obj.values==before and obj._steps[1:]==other

@pytest.mark.parametrize("algorithm",["quicksort","mergesort","heapsort"])
@pytest.mark.parametrize("values",CASES)
def test_retained_body_semantics(algorithm,values,request):
    original=list(values)
    context("baseline-engine:"+request.node.nodeid)
    engine=SortingInterpreter(values,algorithm).run()
    assert values==original
    assert engine["final_state"]["items"]==sorted(original)
    assert Counter(engine["final_state"]["items"])==Counter(original)
    context("private-unit:"+request.node.nodeid)
    obj=SortingInterpreter(values,algorithm)
    getattr(obj,"_run_"+algorithm)()
    assert obj.values==sorted(original)==engine["final_state"]["items"]
    assert values==original
    if original==[4,3,2,1]:
        fixture_dir=Path(__file__).resolve().parent/"fixtures"/"sorting17-native-v1"
        ref=json.loads((fixture_dir/"manifest.json").read_text(encoding="utf-8"))["native_frozen_reference"][algorithm]
        assert hashlib.sha256((fixture_dir/ref["file"]).read_bytes()).hexdigest()==ref["SHA"]
        assert ref["native_initial_array"]==original
        assert obj.values==ref["native_final_array"]
    invariants(obj,original)

@pytest.mark.parametrize("case",["singleton","interior"])
def test_quick_subrange(case,request):
    context("private-unit:"+request.node.nodeid)
    values=[99,7,-99] if case=="singleton" else [99,4,1,3,2,-99]
    original=list(values);obj=SortingInterpreter(values,"quicksort")
    obj._quicksort_rec(1,len(values)-2)
    assert obj.values==original[:1]+sorted(original[1:-1])+original[-1:]
    assert values==original
    if case=="singleton":assert obj._steps==[] and obj.metrics.comparisons==obj.metrics.swaps==obj.metrics.moves==0
    else:assert obj._steps and all(step["active_range"] is None or 1<=step["active_range"][0]<=step["active_range"][1]<=len(values)-2 for step in obj._steps)
    invariants(obj,original)

@pytest.mark.parametrize("case",["tie_left_remainder","right_remainder"])
def test_merge_subrange(case,request):
    context("private-unit:"+request.node.nodeid)
    values=[99,2,4,2,3,-99] if case=="tie_left_remainder" else [99,1,2,3,4,-99]
    original=list(values);obj=SortingInterpreter(values,"mergesort");aux=list(values)
    obj._merge(aux,1,2,4)
    expected=original[:1]+sorted(original[1:5])+original[5:]
    assert obj.values==expected and aux==expected and values==original
    assert obj.metrics.moves==8
    assert all(step["active_range"]==[1,4] for step in obj._steps)
    invariants(obj,original)

def test_heapify_local_heap_preserves_suffix(request):
    context("private-unit:"+request.node.nodeid)
    values=[1,9,8,7,6,5,4,1000,-1000];original=list(values)
    obj=SortingInterpreter(values,"heapsort");obj._heapify(7,0)
    assert obj.values[7:]==original[7:] and values==original
    assert Counter(obj.values[:7])==Counter(original[:7])
    for child in range(1,7):assert obj.values[(child-1)//2]>=obj.values[child]
    assert obj.values[0]==max(original[:7])
    assert all(step["active_range"]==[0,6] for step in obj._steps)
    invariants(obj,original)
