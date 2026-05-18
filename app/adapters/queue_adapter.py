"""Adapter for the queue TAD."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.sequential import Cola


class QueueAdapter(BaseAdapter):
    """Adapt `Cola` to the generic adapter contract."""

    def __init__(self) -> None:
        self._structure: Cola[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = Cola()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "encolar":
            valor = self._require_int(payload, "value", "valor")
            self._structure.encolar(valor)
            return {"message": f"Se encoló '{valor}' correctamente."}
        if operation_name == "desencolar":
            valor = self._structure.desencolar()
            return {"message": f"Se desencoló '{valor}' desde el frente.", "result": valor}
        if operation_name == "frente":
            valor = self._structure.frente()
            return {"message": f"El frente actual es '{valor}'.", "result": valor}
        if operation_name == "final":
            valor = self._structure.final()
            return {"message": f"El valor al final es '{valor}'.", "result": valor}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "La cola se limpió correctamente."}
        raise ValueError(f"Operación no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        items = self._structure.a_lista()
        return {
            "kind": "linear",
            "title": "Cola (frente a final)",
            "items": [{"value": value} for value in items],
            "size": self._structure.tamano(),
            "empty": self._structure.vacia(),
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "encolar",
                "label": "Encolar",
                "mutates": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {"name": "desencolar", "label": "Desencolar", "mutates": True, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]

