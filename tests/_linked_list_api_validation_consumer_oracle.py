"""Exact hidden linked_list relative1 API refusal; no fictitious C execution."""
import hashlib
SOURCE_SHA="60243e196fe9a3627fc3aec328fa6b5e63bc42437aa1a953b47dbf01c76385ff"
MESSAGE="El modo de insercion debe ser -1 (antes) o 0 (despues)."
def assert_linked_list_mode_validation(body,status,payload):
    assert status==400 and body.get("success") is False
    assert payload=={"position":"1","relative":"1","value":"1"}
    trace=body.get("execution_trace");assert isinstance(trace,dict)
    assert trace.get("structure_id")=="linked_list" and trace.get("operation_name")=="insertar_elemento"
    assert trace.get("payload")==payload
    assert trace.get("success") is False and trace.get("execution_started") is False
    assert trace.get("validation")=={"stage":"API","accepted":False,"message":MESSAGE}
    assert trace.get("steps")==[] and trace.get("hidden_positional_instruction_model") is True
    assert body.get("message")==trace.get("message")==MESSAGE
    assert trace.get("caller_translation")=="Existing positional compatibility caller; separate from unchanged TAD C."
    assert hashlib.sha256(trace["source_code"].encode()).hexdigest()==SOURCE_SHA
    empty={"empty":True,"items":[],"kind":"linear","size":0,"title":"Lista enlazada"}
    assert body.get("history")==[] and body.get("visual_state")==trace.get("final_state")==empty

EMPTY_SPEC={'eliminar_inicio': {'flag': 'hidden_terminal_instruction_model', 'function': 'lista_eliminar_inicio', 'body_sha256': 'c2aff4347c9092b6fea7eb780057dc14a0f8767961d0168ef7991cb1cdb89590'}, 'eliminar_final': {'flag': 'hidden_terminal_instruction_model', 'function': 'lista_eliminar_final', 'body_sha256': '4e2eb2570ba43d590124edfc34b55edc8bac88422d3b754e55c05c200492dbed'}, 'eliminar_posicion': {'flag': 'hidden_positional_instruction_model', 'function': 'lista_eliminar_posicion', 'body_sha256': 'd71dda2acab92323aa094281ab1510edcc128eee98ab024701f832cfcf3fbb67'}, 'primero': {'flag': 'hidden_terminal_instruction_model', 'function': 'lista_primero', 'body_sha256': '382394394c74e1a820522b0ab9e202c04fa85554e1459d8841627f602bcb5350'}, 'ultimo': {'flag': 'linked_last_instruction_model', 'function': 'lista_ultimo', 'body_sha256': 'a39a4fb2454630be774bfa17a53941a64b3a85ac2fe5b29af59ad01666f881b5'}}
EMPTY_MESSAGE="No se puede ejecutar la operaci\u00f3n porque la estructura est\u00e1 vac\u00eda."
def assert_linked_list_empty_validation(body,status,payload,operation):
    import re
    assert operation in EMPTY_SPEC;spec=EMPTY_SPEC[operation]
    assert payload==({"position":"1"} if operation=="eliminar_posicion" else {})
    assert status==400 and body.get("success") is False
    t=body.get("execution_trace");assert isinstance(t,dict)
    assert t.get("structure_id")=="linked_list" and t.get("operation_name")==operation and t.get("payload")==payload
    assert t.get("success") is False and t.get("execution_started") is False and t.get("steps")==[]
    expected_message="La posici\u00f3n ingresada es inv\u00e1lida para el estado actual." if operation=="eliminar_posicion" else EMPTY_MESSAGE
    assert t.get(spec["flag"]) is True and t.get("validation")=={"stage":"API","accepted":False,"message":expected_message}
    assert body.get("message")==t.get("message")==expected_message
    empty={"empty":True,"items":[],"kind":"linear","size":0,"title":"Lista enlazada"}
    assert body.get("history")==[] and body.get("visual_state")==t.get("final_state")==empty
    source=t["source_code"];token="int "+spec["function"]+"(";assert token in source;start=source.index(token);cbody=source[start:source.index("\n}",start)+2]
    digest=hashlib.sha256(" ".join(re.sub(r"/\*.*?\*/|//[^\n]*","",cbody,flags=re.S).split()).encode()).hexdigest()
    assert digest==spec["body_sha256"]

def assert_hidden_delete_empty_branch(body):
    t=body["execution_trace"];assert body["success"] is True and t["operation_name"]=="eliminar_primero" and t["payload"]=={"value":"1"}
    assert hashlib.sha256(t["source_code"].encode()).hexdigest()=="e94a40f8c2420a2752cf6aa22fcbe156696380e6a253ef63972c1380d1615ad1"
    steps=t["steps"];expected=['void lista_eliminar_elemento(Tlista *lista, int valor) {','if (lista == NULL || *lista == NULL) {','printf(" Valor no encontrado o lista vacia.\\n");','return;']
    assert len(steps)==4 and [s["line_text"].strip() for s in steps]==expected
    source=t["source_code"].splitlines()
    for i,s in enumerate(steps):
        assert s["step_index"]==i and type(s["line_index"]) is int and 0<=s["line_index"]<len(source) and s["line_text"]==source[s["line_index"]]
        assert s["state_snapshot"]["items"]==s["state_after"]["items"]==[]
        assert s["state_snapshot"]["size"]==s["state_after"]["size"]==0
        frame=s["pedagogy"];assert set(frame["narration"])=={"basic","intermediate","advanced"}
        assert frame["heap_transition"]["before"]==frame["heap_transition"]["after"]==[]
        assert frame["heap_transition"]["freed"]==frame["heap_transition"]["dangling_references"]==[]
        if i:assert s["state_snapshot"]==steps[i-1]["state_after"]
    assert steps[1]["pedagogy"]["condition"]["result"] is True
    assert t["final_state"]==body["visual_state"] and body["history"]==[{"operation":"eliminar_primero","payload":{"value":"1"}}]
