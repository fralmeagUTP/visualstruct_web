"""Adapter for Binary Heap hierarchical structure."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.hierarchical import MonticuloBinario


class BinaryHeapAdapter(BaseAdapter):
    """Adapt `MonticuloBinario` to the common visualizer contract."""

    def __init__(self) -> None:
        self._structure: MonticuloBinario[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = MonticuloBinario(min_heap=True)

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "insertar":
            value = self._require_int(payload, "value", "valor")
            self._structure.insertar(value)
            return {"message": f"Se insertó {value} en el montículo binario."}
        if operation_name == "extraer_raiz":
            result = self._structure.extraer_raiz()
            return {"message": f"Se extrajo la raíz {result}.", "result": result}
        if operation_name == "raiz":
            result = self._structure.raiz()
            return {"message": f"La raíz actual es {result}.", "result": result}
        if operation_name == "a_lista":
            result = self._structure.a_lista()
            return {"message": f"Arreglo interno: {result}.", "result": result}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "El montículo binario se limpió correctamente."}
        raise ValueError(f"Operación no soportada: {operation_name}.")

    def _to_tree_node(self, values: list[int], index: int) -> dict[str, Any] | None:
        if index >= len(values):
            return None
        return {
            "value": values[index],
            "left": self._to_tree_node(values, 2 * index + 1),
            "right": self._to_tree_node(values, 2 * index + 2),
        }

    def to_visual_state(self) -> dict[str, Any]:
        values = self._structure.a_lista()
        return {
            "kind": "heap",
            "title": "Montículo Binario (min-heap)",
            "array": values,
            "root": self._to_tree_node(values, 0),
            "size": self._structure.tamano(),
            "empty": self._structure.vacio(),
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {"name": "insertar", "label": "Insertar", "mutates": True, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "extraer_raiz", "label": "Extraer raíz", "mutates": True, "inputs": []},
            {"name": "raiz", "label": "Ver raíz", "mutates": False, "inputs": []},
            {"name": "a_lista", "label": "Ver arreglo", "mutates": False, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]
