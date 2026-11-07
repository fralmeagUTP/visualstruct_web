"""Independent expected student text for the finite Intercambio/Selección audits."""
from __future__ import annotations


def expected_instruction_narration(action: str) -> str:
    """Keep the instruction explanation while translating its technical prose."""
    # These algorithms supply full explanations, not raw phase/token labels.
    return (action.replace('al caller', 'a la función que llamó')
            .replace('caller suspendido', 'función que llamó suspendida')
            .replace('del helper', 'de la función auxiliar')
            .replace('scope', 'ámbito de la variable').strip())
