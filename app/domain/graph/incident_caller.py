"""One literal C caller fragment translating the existing API incident-arc contract."""
from __future__ import annotations


def incident_vertex_literal(vertex: int) -> str:
    """Keep the existing Graph main int32 literal contract, including INT_MIN."""
    value = int(vertex)
    if not -2147483648 <= value <= 2147483647:
        raise ValueError("El main C requiere vértices y argumentos int32.")
    return "(-2147483647 - 1)" if value == -2147483648 else str(value)


def incident_caller_lines(vertex: int, indent: str = "    ") -> list[str]:
    """Own arcs remain caller-owned; unlink each incident once after vertex C returns."""
    value = incident_vertex_literal(vertex)
    return [indent + line for line in [
        "{",
        "    ListaArco *enlace = &g.a;",
        "    while (*enlace != NULL) {",
        "        ListaArco actual = *enlace;",
        f"        if (actual->origen == {value} || actual->destino == {value}) {{",
        "            *enlace = actual->sig;",
        "            free(actual);",
        "        } else {",
        "            enlace = &actual->sig;",
        "        }",
        "    }",
        "}",
    ]]
