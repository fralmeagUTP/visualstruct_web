from pathlib import Path
from copy import deepcopy
import json,pytest
from _linked_list_api_validation_consumer_oracle import assert_linked_list_mode_validation
ROOT=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-linked-list-canonical-consumer-low"
@pytest.fixture(scope="module")
def saved():return json.loads((ROOT/"linkedcanonical-before-call-20-insertar_elemento-wire.json").read_text(encoding="utf-8"))
def check(wire):assert_linked_list_mode_validation(wire["body"],wire["status"],{"position":"1","relative":"1","value":"1"})
def test_original_API_refusal_positive(saved):check(saved)
@pytest.mark.parametrize("fault",["status","success","started","accepted","stage","steps","payload","history","state","message","source","hidden","operation"])
def test_API_refusal_corruptions_rejected(saved,fault):
    w=deepcopy(saved);b=w["body"];t=b["execution_trace"]
    if fault=="status":w["status"]=200
    elif fault=="success":b["success"]=t["success"]=True
    elif fault=="started":t["execution_started"]=True
    elif fault=="accepted":t["validation"]["accepted"]=True
    elif fault=="stage":t["validation"]["stage"]="C"
    elif fault=="steps":t["steps"]=[{"line_text":"lista_insertar_elemento(&lista,1,1);"}]
    elif fault=="payload":t["payload"]["relative"]="0"
    elif fault=="history":b["history"]=[{"operation":"insertar_elemento","payload":t["payload"]}]
    elif fault=="state":
        for state in (b["visual_state"],t["final_state"]):state["items"]=[1];state["size"]=1;state["empty"]=False
    elif fault=="message":b["message"]=t["message"]=t["validation"]["message"]="different error"
    elif fault=="source":t["source_code"]+="\n"
    elif fault=="hidden":t["hidden_positional_instruction_model"]=False
    else:t["operation_name"]="insertar_posicion"
    with pytest.raises(AssertionError):check(w)
def test_original_positional_C_case_is_not_API_refusal():
    wire=json.loads((ROOT/"linkedcanonical-before-call-18-insertar_posicion-wire.json").read_text(encoding="utf-8"))
    body=wire["body"];trace=body["execution_trace"];assert wire["status"]==200 and body["success"] is True and trace["steps"]
    assert trace["final_state"]==body["visual_state"]
    for step in trace["steps"]:
        frame=step["pedagogy"];assert set(frame["narration"])=={"basic","intermediate","advanced"};assert frame["source"]["line_text"]==step["line_text"];assert frame["heap_transition"]["dangling_references"]==[]
    with pytest.raises(AssertionError):assert_linked_list_mode_validation(body,wire["status"],{"position":"1","relative":"1","value":"1"})

from _linked_list_api_validation_consumer_oracle import assert_linked_list_empty_validation,assert_hidden_delete_empty_branch
EMPTY_CALLS=[(26,"eliminar_inicio"),(28,"eliminar_final"),(30,"eliminar_posicion"),(32,"primero"),(34,"ultimo")]
def empty_wire(call,op):return json.loads((ROOT/("linkedcanonical-final-4-call-"+str(call)+"-"+op+"-wire.json")).read_text(encoding="utf-8"))
def check_empty(w):
    t=w["body"]["execution_trace"];assert_linked_list_empty_validation(w["body"],w["status"],t["payload"],t["operation_name"])
@pytest.mark.parametrize("call,op",EMPTY_CALLS)
def test_original_empty_API_cases_positive(call,op):check_empty(empty_wire(call,op))
@pytest.mark.parametrize("call,op",EMPTY_CALLS)
@pytest.mark.parametrize("fault",["started","steps","source","state_and_history"])
def test_empty_API_coordinated_corruptions_rejected(call,op,fault):
    w=empty_wire(call,op);b=w["body"];t=b["execution_trace"]
    if fault=="started":t["execution_started"]=True
    elif fault=="steps":t["steps"]=[{"line_text":"free(phantom);"}]
    elif fault=="source":t["source_code"]=t["source_code"].replace("return 0;","return 1;")
    else:
        for state in (b["visual_state"],t["final_state"]):state["size"]=1;state["items"]=[{"value":1}];state["empty"]=False
        b["history"]=[{"operation":op,"payload":t["payload"]}]
    with pytest.raises(AssertionError):check_empty(w)
def alias_body():return json.loads((ROOT/"linkedcanonical-final-4-call-22-eliminar_primero-wire.json").read_text(encoding="utf-8"))["body"]
def test_original_hidden_alias_empty_branch_positive():assert_hidden_delete_empty_branch(alias_body())
def test_hidden_alias_planner_reuses_C_empty_return():
    from app.services.execution_trace_service import ExecutionTraceService
    b=alias_body();t=b["execution_trace"];lines=t["source_code"].splitlines();plan=ExecutionTraceService._expand_linked_list_execution_indexes(operation_name="eliminar_primero",lines=lines,before_state=t["steps"][0]["state_snapshot"],after_state=b["visual_state"],payload={"value":"1"},success=True,message=b["message"])
    assert plan==[s["line_index"] for s in t["steps"]]
@pytest.mark.parametrize("fault",["lexical_advance","guard","phantom_heap","source"])
def test_hidden_alias_impossible_C_branch_rejected(fault):
    b=alias_body();t=b["execution_trace"];s=t["steps"]
    if fault=="lexical_advance":
        index=next(i for i,l in enumerate(t["source_code"].splitlines()) if l.strip()=="p = p->sgte;");fake=deepcopy(s[-1]);fake["line_index"]=index;fake["line_text"]=t["source_code"].splitlines()[index];s.append(fake)
    elif fault=="guard":s[1]["pedagogy"]["condition"]["result"]=False
    elif fault=="phantom_heap":s[2]["pedagogy"]["heap_transition"]["after"]=[{"id":"phantom"}]
    else:s[0]["line_index"]=s[1]["line_index"]
    with pytest.raises(AssertionError):assert_hidden_delete_empty_branch(b)
