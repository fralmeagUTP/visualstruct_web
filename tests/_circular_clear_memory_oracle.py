"""Independent fixed-case store model for native lcir_destruir([1,2,3])."""
from copy import deepcopy
PREFIX=["void lcir_destruir(ListaCircular *lista) {","LCirNodo *actual;","LCirNodo *next;","if (lista == NULL || lista->cabeza == NULL) {","actual = lista->cabeza;","if (lista->cabeza == lista->cola) {"]
LOOP=["while (actual != lista->cola) {","next = actual->sgte;","lista->cabeza = next;","lista->cola->sgte = lista->cabeza;","if (lista->cantidad > 0) {","lista->cantidad--;","free(actual);","actual = next;"]
LINES=PREFIX+LOOP*2+["while (actual != lista->cola) {","lista->cabeza = NULL;","lista->cola = NULL;","lista->cantidad = 0;","free(actual);","}"]

from _circular_insert_memory_oracle import _assert_sequence_projection, _assert_sequence_memory_projection

def assert_circular_clear_memory(body):
    trace=body["execution_trace"]
    assert trace["structure_id"]=="circular_list" and trace["operation_name"]=="limpiar" and trace["payload"]=={}
    assert body["success"] is True
    steps=trace["steps"]
    assert len(steps)==28 and [s["line_text"].strip() for s in steps]==LINES
    initial=steps[0]["state_snapshot"]
    assert initial["items"]==[{"value":1},{"value":2},{"value":3}] and type(initial["size"]) is int and initial["size"]==3 and initial["empty"] is False
    cards=steps[0]["pedagogy"]["heap_objects"]
    assert len(cards)==3 and len({n["id"] for n in cards})==3 and len({n["address"] for n in cards})==3
    ids=[n["id"] for n in cards]
    nodes={identity:{"valor":i+1,"sgte":ids[(i+1)%3]} for i,identity in enumerate(ids)}
    head,tail,quantity=ids[0],ids[2],3
    actual=following=None
    source=trace["source_code"].replace("\r\n","\n").split("\n")
    expected_values=[1,2,3]; expected_size=3
    previous_heap=None;freed_ids=[]
    for i,(step,line) in enumerate(zip(steps,LINES)):
        assert step["step_index"]==i and source[step["line_index"]].strip()==line
        if i:assert step["state_snapshot"]==steps[i-1]["state_after"]
        if i>=23:assert step["line_index"]==max(j for j,l in enumerate(source) if l.strip()==line)
        _assert_sequence_projection(step["state_snapshot"], expected_values, expected_size)
        freed=None;condition=None
        if line=="if (lista == NULL || lista->cabeza == NULL) {":condition=False
        elif line=="actual = lista->cabeza;":actual=head
        elif line=="if (lista->cabeza == lista->cola) {":condition=head==tail
        elif line=="while (actual != lista->cola) {":condition=actual!=tail
        elif line=="next = actual->sgte;":following=nodes[actual]["sgte"]
        elif line=="lista->cabeza = next;":head=following
        elif line=="lista->cola->sgte = lista->cabeza;":nodes[tail]["sgte"]=head
        elif line=="if (lista->cantidad > 0) {":condition=quantity>0
        elif line=="lista->cantidad--;":quantity-=1
        elif line=="free(actual);":
            assert actual in nodes
            freed=(actual,deepcopy(nodes.pop(actual)));freed_ids.append(actual)
            if following==actual:following="indeterminado (liberado)"
            actual="indeterminado (liberado)"
        elif line=="actual = next;":actual=following
        elif line=="lista->cabeza = NULL;":head=None
        elif line=="lista->cola = NULL;":tail=None
        elif line=="lista->cantidad = 0;":quantity=0
        elif line=="}":actual=following=None
        reachable=[];pointer=head
        while pointer is not None and pointer not in reachable:
            assert pointer in nodes
            reachable.append(pointer);pointer=nodes[pointer]["sgte"]
        f=step["pedagogy"];m=f["memory_state"];heap=f["heap_objects"]
        assert len(heap)==len(nodes) and len({n["id"] for n in heap})==len(heap) and len({n["address"] for n in heap})==len(heap)
        objects={n["id"]:n for n in heap}
        assert set(objects)==set(nodes)
        for identity,fields in nodes.items():
            n=objects[identity]
            assert n["fields"]==fields and n["status"]==("linked" if identity in reachable else "detached")
            assert n["allocated"] is True and n["freed"] is False
        transition=f["heap_transition"]
        assert transition["after"]==heap
        assert len({n["id"] for n in transition["before"]})==len(transition["before"])
        if previous_heap is not None:assert transition["before"]==previous_heap
        previous_heap=heap
        if freed:
            assert len(transition["freed"])==1
            retired=transition["freed"][0]
            assert retired["id"]==freed[0] and retired["fields"]==freed[1]
            assert retired["allocated"] is False and retired["freed"] is True and retired["status"]=="freed"
        else:assert transition["freed"]==[]
        assert m["cabeza"]==(head or "NULL") and m["cola"]==(tail or "NULL") and m["cantidad"]==quantity
        expected_values=[nodes[n]["valor"] for n in reachable]; expected_size=quantity
        _assert_sequence_projection(m, expected_values, expected_size, reachable)
        _assert_sequence_memory_projection(m, m, heap)
        if i<27:_assert_sequence_memory_projection(step["state_after"], m, heap)
        _assert_sequence_projection(step["state_after"], expected_values, expected_size, reachable if i<27 else None)
        assert m["items"]==[{"value":nodes[n]["valor"]} for n in reachable]
        assert m.get("actual")==actual and m.get("next")==following and m["lista"]=="&lc"
        calls=f["call_stack"]
        assert len(calls)==1 and calls[0]["function"]=="lcir_destruir" and calls[0]["parameters"]=={"lista":"&lc"}
        pointers=f["pointers"]
        assert len({p["name"] for p in pointers})==len(pointers)
        root=next(p for p in pointers if p["name"]=="lista")
        assert root["type"]=="ListaCircular *" and root["target"]==("fuera de ámbito" if i==27 else "&lc")
        if condition is not None:assert f["condition"]["result"] is condition
    _assert_sequence_projection(body["visual_state"], expected_values, expected_size)
    assert freed_ids==ids and body["visual_state"]["items"]==[] and body["visual_state"]["size"]==0 and trace["final_state"]==body["visual_state"]
