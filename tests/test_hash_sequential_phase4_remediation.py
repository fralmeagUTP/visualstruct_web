import os
import subprocess
import sys

import pytest

from app.adapters.hash_table_adapter import HashTableAdapter
from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.domain.sequential.exceptions import EstructuraVaciaError
from app.services.c_code_service import CCodeService


def test_hash_integer_index_is_stable_across_processes():
    program = (
        "from app.domain.hash.tad_wrappers import TablaHash;"
        "t=TablaHash[int,str](17);print([t._indice(k) for k in (-18,-1,0,1,18)])"
    )
    outputs = []
    for seed in ("1", "999"):
        environment = os.environ.copy()
        environment["PYTHONHASHSEED"] = seed
        outputs.append(subprocess.check_output([sys.executable, "-c", program], text=True, env=environment).strip())
    assert outputs == ["[16, 16, 0, 1, 1]"] * 2


def test_hash_capacity_is_fixed_and_collision_chain_survives_update_remove():
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": 3})
    for key, value in ((-2, "a"), (1, "b"), (4, "c")):
        adapter.execute("insert", {"key": key, "value": value})
    assert adapter.table.capacidad() == 3
    assert adapter.to_visual_state()["metadata"]["collisions"] == 2
    adapter.execute("insert", {"key": 1, "value": "actualizado"})
    assert adapter.execute("get", {"key": 1})["result"] == "actualizado"
    assert adapter.execute("remove", {"key": -2})["result"] is True
    assert adapter.execute("contains", {"key": 4})["result"] is True


@pytest.mark.parametrize("key", ["texto", "1.5", True, None])
def test_hash_rejects_non_integer_keys(key):
    adapter = HashTableAdapter()
    with pytest.raises(ValueError):
        adapter.execute("insert", {"key": key, "value": "x"})
    assert adapter.table.tamano() == 0


def test_priority_queue_keeps_arrival_links_and_stable_priority_selection():
    adapter = PriorityQueueAdapter()
    for value, priority in ((10, 0), (20, -2147483648), (30, 0), (40, 2147483647), (50, -2147483648)):
        adapter.execute("encolar", {"value": value, "priority": priority})
    assert [(item["value"], item["priority"]) for item in adapter.to_visual_state()["items"]] == [
        (10, 0), (20, -2147483648), (30, 0), (40, 2147483647), (50, -2147483648)
    ]
    assert adapter.execute("frente", {})["result"] == 20
    assert [adapter.execute("desencolar", {})["result"] for _ in range(5)] == [20, 50, 10, 30, 40]
    with pytest.raises(EstructuraVaciaError):
        adapter.execute("frente", {})


def test_all_remediated_sequential_operations_map_to_real_c_functions():
    mappings = {
        "stack": ("cima", "pila_cima"),
        "queue": ("frente", "cola_frente"),
        "queue_final": ("final", "cola_final"),
        "priority_queue": ("frente", "cp_frente"),
    }
    for structure, (operation, function) in mappings.items():
        structure_id = "queue" if structure == "queue_final" else structure
        assert function in CCodeService.get_structure_data(structure_id)["operations"][operation]
    linked = CCodeService.get_structure_data("linked_list")["operations"]
    for operation in ("invertir", "primero", "ultimo", "eliminar_posicion"):
        assert f"lista_{operation}" in linked[operation]
