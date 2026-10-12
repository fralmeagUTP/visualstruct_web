"""Fixed RN consumer fixtures; authentic memory and causal C stores, not a general interpreter."""
from copy import deepcopy
import hashlib
import re
from _hierarchical_frame_oracle import _nodes, _memory_cards, _retire_objects, _memory_events
from _tree_intermediate_consumer_oracle import _assert_tree_public_projection
FIELDS = {"nro":"value", "izq":"left", "der":"right", "padre":"parent", "rbt_color":"color"}
SOURCE = {"rotation":"846e2f6b7ab2cb8c6322e01cc2281fb6f3afff7030da331099d69664cbbc6092", "delete":"493de87438979e3ab41bf32fd75c16d18d283ac655412d277b08d35f3f033be2"}

def _env(state):
    frames=state["tree_frames"]
    assert frames, "physical write requires C scope"
    return {**frames[-1]["parameters"], **frames[-1]["locals"]}

def _read(expr,state):
    expr=expr.strip()
    if expr in {"NULL","ROJO","NEGRO"}:return {"NULL":"NULL","ROJO":"RED","NEGRO":"BLACK"}[expr]
    if expr.startswith("colorOf("):
        ident=_read(expr[8:-1],state)
        return "BLACK" if ident=="NULL" else _nodes(state)[ident]["color"]
    parts=expr.split("->")
    value=state["head"] if parts[0]=="(*arbol)" else _env(state)[parts[0]]
    for field in parts[1:]:
        assert value in _nodes(state), "C read requires live identity"
        value=_nodes(state)[value][FIELDS[field]]
        assert value != "sin inicializar"
    return value

def _physical_store(before,after,text,phase):
    old,actual=_nodes(before),_nodes(after);expected=deepcopy(old);head=before["head"]
    if phase=="allocate":
        assert text=="actual = malloc(sizeof(struct nodoRBT));" and len(actual.keys()-old.keys())==1
        ident=next(iter(actual.keys()-old.keys()))
        expected[ident]={"id":ident, **{f:"sin inicializar" for f in FIELDS.values()}, "initialized":0}
    elif phase=="free":
        assert text=="free(z);";ident=_read("z",before);assert ident in expected;del expected[ident]
    elif phase in {"initialize","link","recolor"}:
        statement=re.sub(r"^if \((?:v|w|w_izq|w_der|x|\*arbol)\)\s*", "", text)
        assert statement.endswith(";") and "=" in statement
        parts=[x.strip() for x in statement[:-1].split("=")];value=_read(parts[-1],before)
        for lhs in parts[:-1]:
            if lhs in {"*r","*arbol","*root"}:
                assert _env(before)[lhs[1:]]=="&raiz";head=value
            else:
                alias,field=lhs.rsplit("->",1);ident=_read(alias,before);assert ident in expected
                expected[ident][FIELDS[field]]=value
                expected[ident]["initialized"]|={"nro":1,"izq":2,"der":4,"padre":8,"rbt_color":16}[field]
    assert actual==expected, (text,"unexplained physical store")
    assert after["head"]==head, (text,"unexplained root store")

def assert_rbt_consumer(body,case):
    assert case in {"rotation","delete_int","delete_text"}
    kind="rotation" if case=="rotation" else "delete"
    trace=body["execution_trace"];value=1 if kind=="rotation" else (3 if case=="delete_int" else "3")
    assert body["success"] is True and trace["structure_id"]=="red_black"
    assert trace["operation_name"]==("insertar" if kind=="rotation" else "eliminar") and trace["payload"]=={"value":value}
    assert hashlib.sha256(trace["source_code"].encode()).hexdigest()==SOURCE[kind]
    steps=trace["steps"];source=trace["source_code"].replace("\r\n","\n").split("\n")
    initial=_nodes(steps[0]["state_snapshot"])
    seeds=([10,5] if kind=="rotation" else [7,3,18,10,8,11,22,26])
    assert steps[0]["state_snapshot"]["head"]=="N1" and [n["value"] for n in initial.values()]==seeds
    topology=([(10,"N2","NULL","NULL","BLACK"),(5,"NULL","NULL","N1","RED")] if kind=="rotation" else [(7,"N2","N3","NULL","BLACK"),(3,"NULL","NULL","N1","BLACK"),(18,"N4","N7","N1","RED"),(10,"N5","N6","N3","BLACK"),(8,"NULL","NULL","N4","RED"),(11,"NULL","NULL","N4","RED"),(22,"NULL","N8","N3","BLACK"),(26,"NULL","NULL","N7","RED")])
    assert initial=={f"N{i}":dict(id=f"N{i}",value=v,left=l,right=r,parent=p,color=c,initialized=31) for i,(v,l,r,p,c) in enumerate(topology,1)}
    physical_before=steps[0]["state_snapshot"]
    retired={}
    for i,s in enumerate(steps):
        p=s["pedagogy"];event=p["instruction_event"];before=s["state_snapshot"];after=p["memory_state"]
        assert s["step_index"]==i and type(s["line_index"]) is int and source[s["line_index"]]==s["line_text"]
        assert p["source"]=={"line_index":s["line_index"],"line_text":s["line_text"]}
        if i:assert before==steps[i-1]["state_after"]
        _assert_tree_public_projection(before, physical_before, "red_black")
        _assert_tree_public_projection(after, after, "red_black")
        _assert_tree_public_projection(s["state_after"], after, "red_black")
        physical_before=after
        old,new=_nodes(before),_nodes(after);mem=p["memory"]
        _memory_cards(mem["objects_before"],old,retired);_retire_objects(retired,old,new);_memory_cards(mem["objects_after"],new,retired)
        _memory_events(mem["allocated_objects"],new.keys()-old.keys(),new);_memory_events(mem["freed_objects"],old.keys()-new.keys(),old)
        _physical_store(before,after,event.get("statement",s["line_text"]).strip(),event["phase"])
        for f in after.get("tree_frames",[]):
            if f["function"]==("rbt_insertar" if kind=="rotation" else "rbt_eliminar"):
                assert f["parameters"]=={"arbol":"&raiz",("dato" if kind=="rotation" else "key"):(1 if kind=="rotation" else 3)}
    _assert_tree_public_projection(body["visual_state"], physical_before, "red_black")
    assert trace["final_state"]==body["visual_state"]
    def anchor(text,phase):
        found=[s for s in steps if s["line_text"].strip()==text and s["pedagogy"]["instruction_event"]["phase"]==phase]
        assert len(found)==1,(text,phase,"unique physical anchor required")
        return found[0]
    if kind=="rotation":
        called=anchor("rbt_rotar_dcha(arbol, a);","call");resumed=anchor("rbt_rotar_dcha(arbol, a);","resume")
        assert called["state_after"]["root"]["value"]==10
        assert _nodes(called["state_snapshot"])==_nodes(called["pedagogy"]["memory_state"])
        publish=anchor("*r = B;","link");attach=anchor("B->der = A;","link");parent=anchor("B->padre = padre;","link")
        assert steps.index(called)<steps.index(publish)<steps.index(attach)<steps.index(parent)<steps.index(resumed)
        assert publish["pedagogy"]["memory_state"]["head"]=="N2" and publish["state_after"]["size"]==2
        assert len(_nodes(publish["pedagogy"]["memory_state"]))==3
        assert attach["state_after"]["size"]==3
        assert _nodes(parent["pedagogy"]["memory_state"])["N2"]["parent"]=="NULL"
        assert resumed["state_after"]["root"]=={"value":5,"color":"BLACK","left":{"value":1,"color":"RED","left":None,"right":None},"right":{"value":10,"color":"RED","left":None,"right":None}}
        assert body["visual_state"]["root"]==resumed["state_after"]["root"] and body["visual_state"]["size"]==3
        return resumed
    loop=[s["pedagogy"]["instruction_event"] for s in steps if s["line_text"].strip()=="while (z != NULL && z->nro != key) {"]
    assert [(e["phase"],e["expression"],e["condition"]) for e in loop]==[("operand","z != NULL",True),("operand","z->nro != key",True),("condition","z != NULL && z->nro != key",True),("operand","z != NULL",True),("operand","z->nro != key",False),("condition","z != NULL && z->nro != key",False)]
    assert "x = z->izq;" not in [s["line_text"].strip() for s in steps]
    branch=anchor("if (z->izq == NULL) {","condition");assert branch["pedagogy"]["instruction_event"]["condition"] is True
    replacement=anchor("x = z->der;","local");assert _env(replacement["pedagogy"]["memory_state"])["x"]=="NULL"
    detached=anchor("u->padre->izq = v;","link");released=anchor("free(z);","free");fix=anchor("arreglarEliminacion(arbol, x, x_parent);","call")
    assert steps.index(replacement)<steps.index(detached)<steps.index(released)<steps.index(fix)
    assert detached["state_snapshot"]["size"]==8 and detached["state_after"]["size"]==7
    assert len(_nodes(detached["pedagogy"]["memory_state"]))==8 and _nodes(detached["pedagogy"]["memory_state"])["N2"]["value"]==3
    assert released["state_snapshot"]["size"]==released["state_after"]["size"]==7
    assert released["pedagogy"]["memory"]["freed_objects"][0]["id"]=="N2"
    locals_=_env(fix["pedagogy"]["memory_state"])
    assert locals_=={"arbol":"&raiz","key":3,"z":"N2 [valor indeterminado; identidad historica]","y":"N2 [valor indeterminado; identidad historica]","y_color_original":"n","x":"NULL","x_parent":"N1"}
    enter=anchor("static void arreglarEliminacion(RBT *root, RBT x, RBT x_parent) {","enter")
    assert enter["pedagogy"]["memory_state"]["tree_frames"][-1]["parameters"]=={"root":"&raiz","x":"NULL","x_parent":"N1"}
    assert "w" not in enter["pedagogy"]["memory_state"]["tree_frames"][-1]["locals"]
    sibling=[s for s in steps if s["pedagogy"]["instruction_event"]["phase"]=="local" and s["line_text"].strip().startswith("RBT w =")]
    assert len(sibling)==1 and _env(sibling[0]["pedagogy"]["memory_state"])["w"]=="N3"
    assert body["visual_state"]["size"]==7 and body["visual_state"]["root"]["value"]==18
    assert body["visual_state"]["traversals"]["inorden"]==[7,8,10,11,18,22,26]
    return released
