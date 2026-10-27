"""Exact native printf chunks and emission location for two Lista consumers."""
from __future__ import annotations

def assert_lista_console(steps: list[dict], operation: str) -> None:
    lines = [s["line_text"].strip() for s in steps]
    if operation == "buscar_elemento":
        target = 'printf("\\n Encontrado en la posicion %d\\n", i);'
        expected = ["\n Encontrado en la posicion 1\n", "\n Encontrado en la posicion 3\n"]
        assert lines.count("if (!encontrado) {") == 1
        assert not any("Numero no encontrado" in line for line in lines)
    else:
        assert operation == "eliminar_repetidos"
        target = 'printf("\\n\\n Valores eliminados..\\n");'
        expected = ["\n\n Valores eliminados..\n"]
    indices = [i for i, line in enumerate(lines) if line == target]
    assert len(indices) == len(expected)
    assert [chunk for s in steps for chunk in s.get("console", [])] == expected
    for i, chunk in zip(indices, expected):
        assert steps[i].get("console") == [chunk]
    assert all(not s.get("console") for i, s in enumerate(steps) if i not in indices)
    assert lines[-1] == "}" and not steps[-1].get("console")
    if operation == "buscar_elemento":
        assert indices[-1] < lines.index("if (!encontrado) {") < len(lines) - 1
    else:
        frees = [i for i, line in enumerate(lines) if line == "free(temp);"]
        assert len(frees) == 3 and max(frees) < indices[0] < len(lines) - 1
