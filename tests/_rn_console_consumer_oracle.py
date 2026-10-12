"""Only original empty-RN insert10 stdout consumer; no new RN cases."""
import hashlib
SOURCE_SHA="fd594753ddf270f85da25157cf0e2e729f3e55e42edec07aa2baf1a6b806c741"
TEXT="\tEl numero ha sido insertado\n"
PHASES="caller_enter enter condition local local operand condition condition allocate condition initialize initialize initialize initialize condition link call enter condition recolor return resume printf return caller".split()
def assert_empty_rn_console(body):
    trace=body["execution_trace"];steps=trace["steps"];source=trace["source_code"]
    assert hashlib.sha256(source.encode()).hexdigest()==SOURCE_SHA
    assert len(steps)==25
    assert [s["pedagogy"]["instruction_event"]["phase"] for s in steps]==PHASES
    lines=source.splitlines()
    for i,s in enumerate(steps):
        assert type(s["line_index"]) is int and lines[s["line_index"]]==s["line_text"]
        p=s["pedagogy"];assert p["source"]["line_index"]==s["line_index"] and p["source"]["line_text"]==s["line_text"]
        assert s["console"]==([TEXT] if i==22 else [])
        memory=p["memory_state"]
        assert memory["console_stdout"]==(TEXT if i>=22 else "")
    stdout=steps[22];old=stdout["state_snapshot"];new=stdout["state_after"]
    assert stdout["line_text"].strip()=='printf("\\tEl numero ha sido insertado\\n");'
    assert stdout["pedagogy"]["instruction_event"]["frame_id"]=="F1"
    assert old["console_stdout"]=="" and new=={**old,"console_stdout":TEXT}
    frame=old["tree_frames"][-1]
    assert frame=={"id":"F1","function":"rbt_insertar","depth":0,"parameters":{"arbol":"&raiz","dato":10},"locals":{"padre":"NULL","actual":"N1"}}
    assert old["head"]=="N1" and old["heap_nodes"]==[{"id":"N1","value":10,"left":"NULL","right":"NULL","parent":"NULL","color":"BLACK","initialized":31,"status":"linked"}]
    assert steps[19]["line_text"].strip()=="n->rbt_color = NEGRO;"
    assert steps[20]["pedagogy"]["instruction_event"]["return"]=="void"
    assert steps[21]["line_text"].strip()=="rbt_insercion_caso1(actual, arbol);"
    assert steps[23]["pedagogy"]["instruction_event"]["return"]=="void"
    assert trace["final_state"]==body["visual_state"]
    final=body["visual_state"];assert final["size"]==1 and final["validation"] is True
    assert final["root"]=={"value":10,"color":"BLACK","left":None,"right":None}
