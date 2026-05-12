"""Adapter for the priority queue TAD."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.sequential import ColaPrioridad


class PriorityQueueAdapter(BaseAdapter):
    """Adapt `ColaPrioridad` to the generic adapter contract."""

    def __init__(self) -> None:
        self._structure: ColaPrioridad[int] | None = None
        self._ordered_items: list[dict[str, int]] = []
        self._next_order = 0
        self.create()

    def create(self) -> None:
        self._structure = ColaPrioridad()
        self._ordered_items = []
        self._next_order = 0

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "encolar":
            valor = self._require_int(payload, "value", "valor")
            prioridad = self._require_int(payload, "priority", "prioridad")
            self._structure.encolar(valor, prioridad)
            self._ordered_items.append(
                {"value": valor, "priority": prioridad, "order": self._next_order}
            )
            self._next_order += 1
            return {
                "message": (
                    f"Se encolÃ³ '{valor}' con prioridad {prioridad} "
                    "(menor nÃºmero = mayor prioridad)."
                )
            }
        if operation_name == "desencolar":
            valor = self._structure.desencolar()
            removed_priority = self._remove_highest_priority_ordered_item(valor)
            return {
                "message": (
                    f"Se atendiÃ³ '{valor}' desde la cola de prioridad."
                    if removed_priority is None
                    else f"Se atendiÃ³ '{valor}' con prioridad {removed_priority}."
                ),
                "result": valor,
                "result_priority": removed_priority,
            }
        if operation_name == "frente":
            valor = self._structure.frente()
            priority = self._peek_highest_priority_value(valor)
            if priority is None:
                return {"message": f"El frente actual es '{valor}'.", "result": valor}
            return {
                "message": f"El frente actual es '{valor}' con prioridad {priority}.",
                "result": valor,
                "result_priority": priority,
            }
        if operation_name == "limpiar":
            self._structure.limpiar()
            self._ordered_items.clear()
            return {"message": "La cola de prioridad se limpiÃ³ correctamente."}
        raise ValueError(f"OperaciÃ³n no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        items = list(self._ordered_items)
        out_index = self._find_out_index(items)
        return {
            "kind": "priority",
            "title": "Cola de prioridad (orden de llegada)",
            "items": [{"value": item["value"], "priority": item["priority"]} for item in items],
            "size": self._structure.tamano(),
            "empty": self._structure.vacia(),
            "out_index": out_index,
        }

    def reset(self) -> None:
        self._structure.limpiar()
        self._ordered_items.clear()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "encolar",
                "label": "Encolar",
                "mutates": True,
                "inputs": [
                    {"name": "value", "label": "Valor", "type": "number"},
                    {"name": "priority", "label": "Prioridad", "type": "number"},
                ],
            },
            {"name": "desencolar", "label": "Desencolar", "mutates": True, "inputs": []},
            {
                "name": "frente",
                "label": "Ver frente",
                "mutates": False,
                "inputs": [],
                "hidden": True,
            },
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]

    @staticmethod
    def _find_out_index(items: list[dict[str, int]]) -> int:
        """Return index of next item to dequeue by (priority, order)."""
        if not items:
            return -1
        best_index = 0
        best_key = (items[0]["priority"], items[0]["order"])
        for index, item in enumerate(items[1:], start=1):
            key = (item["priority"], item["order"])
            if key < best_key:
                best_key = key
                best_index = index
        return best_index

    def _remove_highest_priority_ordered_item(self, expected_value: int) -> int | None:
        """Remove item selected by priority/order and return its priority."""
        if not self._ordered_items:
            return None
        index = self._find_out_index(self._ordered_items)
        if index < 0:
            return None
        item = self._ordered_items[index]
        if item["value"] == expected_value:
            self._ordered_items.pop(index)
            return item["priority"]

        # Fallback defensivo: remover primera coincidencia por valor.
        for fallback_index, candidate in enumerate(self._ordered_items):
            if candidate["value"] == expected_value:
                self._ordered_items.pop(fallback_index)
                return candidate["priority"]
        # Si no hay coincidencia, removemos el candidato calculado.
        self._ordered_items.pop(index)
        return item["priority"]

    def _peek_highest_priority_value(self, expected_value: int) -> int | None:
        """Get priority for next dequeue candidate."""
        if not self._ordered_items:
            return None
        index = self._find_out_index(self._ordered_items)
        if index < 0:
            return None
        candidate = self._ordered_items[index]
        if candidate["value"] != expected_value:
            return None
        return candidate["priority"]

