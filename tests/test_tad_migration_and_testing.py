"""Pruebas de integracion para la migracion a TAD nuevos."""

from __future__ import annotations

from pathlib import Path

from app.domain.hierarchical import MonticuloBinario as HMonticulo
from app.domain.sequential import MonticuloBinario as SMonticulo
from app.services.c_code_service import CCodeService


def test_docs_tads_c_contains_only_new_tad_c_and_h_files() -> None:
    """La carpeta docs/tads_C debe contener solo archivos .c/.h con prefijo tad_."""
    base = Path(__file__).resolve().parents[1] / "docs" / "tads_C"
    c_h_files = sorted(path.name for path in base.iterdir() if path.suffix in {".c", ".h"})

    expected = sorted(
        [
            "tad_abb.c",
            "tad_abb.h",
            "tad_avl.c",
            "tad_avl.h",
            "tad_cola.c",
            "tad_cola.h",
            "tad_cola_prioridad.c",
            "tad_cola_prioridad.h",
            "tad_grafo.c",
            "tad_grafo.h",
            "tad_lista.c",
            "tad_lista.h",
            "tad_lista_circular.c",
            "tad_lista_circular.h",
            "tad_monticulo_binario.c",
            "tad_monticulo_binario.h",
            "tad_pila.c",
            "tad_pila.h",
            "tad_rojo_negro.c",
            "tad_rojo_negro.h",
            "tad_sublista.c",
            "tad_sublista.h",
            "tad_tabla_hash.c",
            "tad_tabla_hash.h",
        ]
    )
    assert c_h_files == expected
    assert all(name.startswith("tad_") for name in c_h_files)


def test_c_code_service_uses_new_tad_file_naming_in_default_messages() -> None:
    """El contenido didactico C debe referenciar archivos tad_*.c."""
    structures = [
        "linked_list",
        "stack",
        "queue",
        "priority_queue",
        "circular_list",
        "sublist",
        "abb",
        "avl",
        "red_black",
        "binary_heap",
        "graph",
        "hash_table",
    ]
    for structure_id in structures:
        data = CCodeService.get_structure_data(structure_id)
        assert data is not None
        assert "docs/tads_C/tad_" in data["default_operation"]


def test_sequential_heap_supports_tad_mode_and_generic_priority_mode() -> None:
    """Monticulo secuencial debe operar en modo TAD (int) y modo generico (prioridad)."""
    min_heap = SMonticulo[int]()
    assert getattr(min_heap, "_use_tad") is True
    for value in [5, 1, 3]:
        min_heap.insertar(value)
    assert min_heap.raiz() == 1
    assert min_heap.extraer_raiz() == 1

    custom_heap = SMonticulo[dict[str, int]](prioridad=lambda item: item["p"], min_heap=True)
    assert getattr(custom_heap, "_use_tad") is False
    custom_heap.insertar({"v": 10, "p": 4})
    custom_heap.insertar({"v": 20, "p": 1})
    assert custom_heap.extraer_raiz()["v"] == 20


def test_hierarchical_heap_supports_tad_mode_and_generic_priority_mode() -> None:
    """Monticulo jerarquico debe operar en modo TAD (int) y modo generico (prioridad)."""
    max_heap = HMonticulo[int](min_heap=False)
    assert getattr(max_heap, "_use_tad") is True
    for value in [5, 1, 3]:
        max_heap.insertar(value)
    assert max_heap.raiz() == 5
    assert max_heap.extraer_raiz() == 5

    custom_heap = HMonticulo[dict[str, int]](prioridad=lambda item: item["p"], min_heap=True)
    assert getattr(custom_heap, "_use_tad") is False
    custom_heap.insertar({"v": 10, "p": 4})
    custom_heap.insertar({"v": 20, "p": 1})
    assert custom_heap.extraer_raiz()["v"] == 20
