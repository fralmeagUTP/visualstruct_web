"""Pedagogical capture budget, not a limit or alteration of the canonical C TAD.

Measured streaming capture: 2,553 steps / 8.67 MB compact JSON / 149.7 MiB
peak process RSS for an eight-vertex sparse Dijkstra. Dense 15-vertex Kruskal
counts 255,403 events without snapshots: capturing that monolith is unsuitable.
4,000 emitted C/caller events is a conservative finite classroom boundary;
no accepted trace is sampled or truncated. The final API publication adds one
non-C step. Normal execution can still use the permitted 15-vertex graph.
"""
MAX_TRACE_EVENTS = 4000


def trace_budget_message():
    return (f"Esta operación supera {MAX_TRACE_EVENTS} eventos para la vista paso a paso. "
            "Usa un grafo de ejemplo más pequeño. Puedes ejecutar en modo normal "
            "para obtener el resultado completo, sin guardar una traza extensa.")


def normal_trace_notice():
    return (f"La operación se ejecutó en modo normal y su resultado está publicado. "
            f"No se guardó la traza porque supera {MAX_TRACE_EVENTS} eventos. "
            "Para observar cada paso, prepara un grafo más pequeño.")
