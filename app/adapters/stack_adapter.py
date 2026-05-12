"""Adapter for the stack TAD."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.sequential import Pila


class StackAdapter(BaseAdapter):
    """Adapt `Pila` to the generic adapter contract."""

    def __init__(self) -> None:
        self._structure: Pila[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = Pila()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "apilar":
            valor = self._require_int(payload, "value", "valor")
            self._structure.apilar(valor)
            return {"message": f"Se apilÃ³ '{valor}' correctamente."}
        if operation_name == "desapilar":
            valor = self._structure.desapilar()
            return {"message": f"Se desapilÃ³ '{valor}' desde el tope.", "result": valor}
        if operation_name == "cima":
            valor = self._structure.cima()
            return {"message": f"La cima actual es '{valor}'.", "result": valor}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "La pila se limpiÃ³ correctamente."}
        raise ValueError(f"OperaciÃ³n no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        items = self._structure.a_lista()
        return {
            "kind": "linear",
            "title": "Pila (tope a fondo)",
            "items": [{"value": value} for value in items],
            "size": self._structure.tamano(),
            "empty": self._structure.vacia(),
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "apilar",
                "label": "Apilar",
                "mutates": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {"name": "desapilar", "label": "Desapilar", "mutates": True, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]

