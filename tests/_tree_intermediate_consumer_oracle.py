"""Three fixed consumer contracts; physical anchors, not a new global tree interpreter."""
from _hierarchical_frame_oracle import _nodes, _memory_cards, _retire_objects, _memory_events
CASES={"abb":("abb","eliminar",2),"lr":("avl","insertar",20),"rl":("avl","insertar",20)}



def _assert_tree_public_projection(public, physical, structure):
    """Reconstruct only the scoped public tree from live physical C identities.

    A repeated identity ends a transient path; an ended lifetime is not read.
    RN reservations become drawable only once all five C fields are initialized.
    This does not demand final tree invariants during individual pointer stores.
    """
    raw=_nodes(physical); reached=set()
    def walk(identity):
        if identity not in raw or identity in reached:
            return None
        reached.add(identity); node=raw[identity]
        if structure=="red_black" and node["initialized"]!=31:
            return None
        left=walk(node["left"]); right=walk(node["right"])
        tree={"value":node["value"],"left":left,"right":right}
        if structure=="red_black": tree["color"]=node["color"]
        if structure=="avl":
            tree["balance_factor"]=node["balance_factor"]
            tree["height"]=1+max(left["height"] if left else 0,right["height"] if right else 0)
        return tree
    root=walk(physical["head"])
    def height(n):return 0 if n is None else 1+max(height(n["left"]),height(n["right"]))
    def traversal(n,order):
        if n is None:return []
        a=traversal(n["left"],order); b=traversal(n["right"],order); value=[n["value"]]
        return value+a+b if order=="preorden" else a+b+value if order=="postorden" else a+value+b
    assert public["root"]==root, "public root/topology/metadata disagree with live C memory"
    assert type(public["size"]) is int and public["size"]==len(reached)
    assert type(public["height"]) is int and public["height"]==height(root)
    empty=(physical["head"]=="NULL") if structure=="red_black" else not reached
    assert public["empty"] is empty
    if "head" in public:assert public["head"]==physical["head"]
    if "heap_nodes" in public:assert _nodes(public)==raw
    for name,count in [("reachable_count",len(reached)),("heap_count",len(raw)),("reserved_count",len(raw))]:
        if name in public:assert public[name]==count
    traversals=public["traversals"]
    if structure=="abb":assert traversals=={o:traversal(root,o) for o in ["inorden","preorden","postorden"]}
    elif "heap_nodes" in public:assert traversals=={}
    else:
        assert "inorden" in traversals
        for order,values in traversals.items():
            assert order in {"inorden","preorden","postorden"} and values==traversal(root,order)
    if "heap_nodes" in public:assert public["validation"] is None
def assert_tree_intermediate_consumer(body,case):
    assert case in CASES
    structure,operation,value=CASES[case]
    trace=body["execution_trace"]
    assert body["success"] is True and trace["structure_id"]==structure and trace["operation_name"]==operation and trace["payload"]=={"value":value}
    steps=trace["steps"];source=trace["source_code"].replace("\r\n","\n").split("\n")
    seed=steps[0]["state_snapshot"]["root"]
    if case=="abb":assert seed=={"value":2,"left":{"value":1,"left":None,"right":None},"right":{"value":3,"left":None,"right":None}}
    else:
        root_value,child_value,side=(30,10,"left") if case=="lr" else (10,30,"right")
        assert seed["value"]==root_value and seed[side]["value"]==child_value and seed[side]["left"] is None and seed[side]["right"] is None
        assert seed["height"]==2 and seed["balance_factor"]==(-1 if case=="lr" else 1)
    physical_before=steps[0]["state_snapshot"]
    retired={}
    for i,step in enumerate(steps):
        p=step["pedagogy"];event=p["instruction_event"];before=step["state_snapshot"];after=p["memory_state"]
        assert step["step_index"]==i and type(step["line_index"]) is int and source[step["line_index"]]==step["line_text"]
        assert p["source"]=={"line_index":step["line_index"],"line_text":step["line_text"]}
        if i:assert before==steps[i-1]["state_after"]
        _assert_tree_public_projection(before, physical_before, structure)
        _assert_tree_public_projection(after, after, structure)
        _assert_tree_public_projection(step["state_after"], after, structure)
        physical_before=after
        old,new=_nodes(before),_nodes(after)
        assert len({n["id"] for n in before["heap_nodes"]})==len(before["heap_nodes"])
        assert len({n["id"] for n in after["heap_nodes"]})==len(after["heap_nodes"])
        memory=p["memory"]
        _memory_cards(memory["objects_before"],old,retired)
        _retire_objects(retired,old,new)
        _memory_cards(memory["objects_after"],new,retired)
        _memory_events(memory["allocated_objects"],new.keys()-old.keys(),new)
        _memory_events(memory["freed_objects"],old.keys()-new.keys(),old)
        if event["phase"]=="call":assert new==old and after["head"]==before["head"], "call entry cannot execute deferred stores"
        for frame in after.get("tree_frames",[]):
            params=frame["parameters"]
            if frame["function"]==("abb_eliminar" if case=="abb" else "avl_insertar"):
                assert params.get("valor",params.get("x")) in ({2,3} if case=="abb" else {20})
                if case!="abb":assert params["raiz"]=="&raiz"
    _assert_tree_public_projection(body["visual_state"], physical_before, structure)
    assert trace["final_state"]==body["visual_state"]
    def anchor(text,phase):
        candidates=[s for s in steps if s["line_text"].strip()==text and s["pedagogy"]["instruction_event"]["phase"]==phase]
        assert len(candidates)==1
        return candidates[0]
    if case=="abb":
        copied=anchor("nodo->valor = temp->valor;","assignment")
        call=anchor("nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);","call")
        released=anchor("free(nodo);","free")
        linked=anchor("nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);","link")
        assert steps.index(copied)<steps.index(call)<steps.index(released)<steps.index(linked)
        a=_nodes(copied["state_snapshot"]);b=_nodes(copied["pedagogy"]["memory_state"])
        root_id=copied["state_snapshot"]["head"];successor=a[root_id]["right"]
        assert len(a)==3 and set(a)==set(b)
        assert a[root_id]["value"]==2 and b[root_id]["value"]==3 and b[successor]["value"]==3
        assert b[root_id]["right"]==successor
        assert released["pedagogy"]["memory"]["freed_objects"][0]["id"]==successor
        before_link=_nodes(linked["state_snapshot"]);after_link=_nodes(linked["pedagogy"]["memory_state"])
        assert len(before_link)==2 and successor not in before_link and before_link[root_id]["right"]==successor+" [valor indeterminado; identidad historica]"
        assert after_link[root_id]["right"]=="NULL" and after_link[root_id]["value"]==3
        assert body["visual_state"]["root"]=={"value":3,"left":{"value":1,"left":None,"right":None},"right":None}
        return copied["state_after"]["root"],linked["state_after"]["root"]
    text="avl_RSI(r, B);" if case=="lr" else "avl_RSD(r, B);"
    called=anchor(text,"call");completed=anchor(text,"after")
    second=anchor("avl_RSD(r, A);" if case=="lr" else "avl_RSI(r, A);","call")
    assert steps.index(called)<steps.index(completed)<steps.index(second)
    middle=completed["state_after"]["root"]
    side="left" if case=="lr" else "right"
    assert middle["value"]==(30 if case=="lr" else 10) and middle[side]["value"]==20
    assert middle[side][side]["value"]==(10 if case=="lr" else 30)
    assert middle["height"]==3 and middle["balance_factor"]==(-2 if case=="lr" else 2)
    assert middle[side]["height"]==2 and middle[side]["balance_factor"]==(-1 if case=="lr" else 1)
    assert middle[side][side]["height"]==1 and middle[side][side]["balance_factor"]==0
    raw=_nodes(completed["pedagogy"]["memory_state"])
    assert len(raw)==3 and {n["value"] for n in raw.values()}=={10,20,30}
    by_value={n["value"]:n for n in raw.values()}
    assert len(by_value)==len(raw)
    assert by_value[20][side]==by_value[10 if case=="lr" else 30]["id"]
    final=body["visual_state"]["root"]
    assert final["value"]==20 and final["left"]["value"]==10 and final["right"]["value"]==30 and final["height"]==2 and final["balance_factor"]==0
    return middle
