"""Exact reviewed labels for the five-stage UI; no free-form suffix matching."""

from __future__ import annotations

STAGES = (
    "1 Preparar y controlar ejecución",
    "2 Visualizar y ejecutar",
    "3 Relacionar con código",
    "4 Comprender",
    "5 Resultados de ejecución",
)

# Keep each approved family description while retaining stage identity and order.
EXACT_PATH_VARIANTS = {
    "/hash/hash_table": (STAGES[0], "2 Visualizar y ejecutar: Tabla hash", *STAGES[2:]),
    "/sorting/visualizador": (*STAGES[:3], "4 Comprender el método", STAGES[4]),
}


def expected_stages(path: str) -> list[str]:
    """Return the exact five labels, allowing only the two reviewed route variants."""
    return list(EXACT_PATH_VARIANTS.get(path, STAGES))


def assert_stage_contract(actual: list[str], path: str) -> None:
    """Reject missing, duplicated, reordered or unrecognized stage labels."""
    assert actual == expected_stages(path), (path, actual)
