"""Bounded C-derived oracle: original empty capacity5 insert1->1 only."""
import re

def assert_fixed_capacity_source(source):
    executable=re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
    assert not re.search(r"\b(?:realloc|rehash)\s*\(", executable)
    insert=executable.split("bool th_insertar(",1)[1].split("bool th_buscar(",1)[0]
    assert not re.search(r"tabla->capacidad\s*=(?!=)",insert)
    assert "tabla->cantidad++;" in insert

def assert_hash_empty_insert(response):
    trace=response["execution_trace"];steps=trace["steps"]
    tokens="insert_entry insert_guard index_call index_entry index_guard raw_modulo negative_modulo_guard index_return index_assign actual_init search_test node_allocate node_null_guard node_key_write node_value_write node_next_write head_publish size_increment insert_return".split()
    lines=["bool th_insertar(TablaHash *tabla, int clave, int valor) {","    if (!tabla || !tabla->buckets || tabla->capacidad <= 0) return false;","    int indice = th_indice(tabla, clave);","int th_indice(const TablaHash *tabla, int clave) {","    if (!tabla || tabla->capacidad <= 0) return -1;","    int indice = clave % tabla->capacidad;","    if (indice < 0) {","    return indice;","    int indice = th_indice(tabla, clave);","    THNodo *actual = tabla->buckets[indice];","    while (actual != NULL) {","    THNodo *nuevo = (THNodo *)malloc(sizeof(THNodo));","    if (!nuevo) return false;","    nuevo->clave = clave;","    nuevo->valor = valor;","    nuevo->siguiente = tabla->buckets[indice];","    tabla->buckets[indice] = nuevo;","    tabla->cantidad++;","    return true;"]
    assert len(steps)==19
    assert [s["event_type"] for s in steps]==tokens
    assert [s["line_text"] for s in steps]==lines
    source=trace["source_code"].splitlines()
    for i,s in enumerate(steps):
        assert source[s["line_index"]]==lines[i]
        d=s["debug"]
        assert d["token"]==tokens[i]
        assert d["root"]["capacity"]==5 and d["root"]["size"]==int(i>=17)
        assert d["allocations"]==int(i>=11) and d["freed"]==[]
        assert d["count_writes"]==int(i>=17)
        assert d["key_writes"]==int(i>=13) and d["value_writes"]==int(i>=14)
        assert d["link_writes"]==(0 if i<15 else 1 if i==15 else 2)
        heap=d["heap"]
        assert len(heap)==int(i>=11)
        if heap:
            node=heap[0]
            assert node["initialized_mask"]==(0 if i<13 else 1 if i==13 else 3 if i==14 else 7)
            assert node["key"]==(1 if i>=13 else None)
            assert node["value"]==(1 if i>=14 else None) and node["next"] is None
        for field in ("state_snapshot","state_after"):
            state=s[field];assert state["metadata"]["capacity"]==5
            assert state["metadata"]["size"]==int(i>=18 or (field=="state_after" and i==17))
    assert trace["final_state"]==response["visual_state"]
