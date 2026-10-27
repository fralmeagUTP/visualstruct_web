"""Focal successful stack-pop lifecycle regressions."""
from copy import deepcopy
from pathlib import Path
import pytest
from app.domain.sequential.stack_pop_instruction import build_stack_pop_trace

SOURCE=(Path(__file__).resolve().parents[1]/"docs/tads_C/tad_pila.c").read_text(encoding="utf-8-sig")
def state(values):return {"kind":"stack","title":"Pila","items":[{"value":v} for v in values],"size":len(values),"empty":not values}

@pytest.mark.parametrize("values",[[7],[7,7],[-1,5],[-2147483648,2147483647]])
def test_pop_detaches_live_node_before_free_and_copies_num(values):
 before=state(values);after=state(values[1:]);saved=deepcopy(before)
 trace=build_stack_pop_trace(payload={},source_code=SOURCE,code_title="C",before_state=before,after_state=after,success=True,message="ok")
 steps={step["event_type"]:step for step in trace["steps"]}
 detached=steps["root_assigned"];freed=steps["node_free"]
 assert detached["state_after"]["items"]==after["items"]
 assert len(detached["pedagogy"]["heap_objects"])==len(values)
 assert detached["debug"]["aux"]["valid"] and detached["debug"]["num"]==values[0]
 assert len(freed["pedagogy"]["heap_objects"])==len(values)-1
 assert freed["debug"]["frees"]==1 and not freed["debug"]["aux"]["valid"]
 assert freed["debug"]["aux"]["value"] is None
 assert freed["debug"]["aux"]["historical_identity"]==detached["debug"]["aux"]["value"]
 for step in trace["steps"][:-1]:
  p=next(v for v in step["pedagogy"]["pointers"] if v["name"]=="p")
  assert p["type"]=="ptrPila *" and p["target"]=="&pila" and not p["changed"]
 assert trace["steps"][-1]["debug"]["result"]==values[0]
 assert trace["steps"][-1]["debug"]["root"]["alive"]
 assert trace["steps"][-1]["debug"]["call_stack"]==[]
 assert trace["final_state"]==after and before==saved
 assert all(step["console"]==[] for step in trace["steps"])
 for first,second in zip(trace["steps"],trace["steps"][1:]):assert first["state_after"]==second["state_snapshot"]

def test_pop_producer_does_not_invent_success_for_empty_api():
 with pytest.raises(AssertionError):build_stack_pop_trace(payload={},source_code=SOURCE,code_title="C",before_state=state([]),after_state=state([]),success=False,message="empty")
