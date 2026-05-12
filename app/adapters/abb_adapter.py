"""Adapter for ABB hierarchical structure."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.hierarchical import ABB


class ABBAdapter(BaseAdapter):
    """Adapt `ABB` to the common visualizer contract."""

    def __init__(self) -> None:
        self._structure: ABB[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = ABB()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "insertar":
            value = self._require_int(payload, "value", "valor")
            self._structure.insertar(value)
            return {"message": f"Se insertó {value} en el ABB."}
        if operation_name == "eliminar":
            value = self._require_int(payload, "value", "valor")
            self._structure.eliminar(value)
            return {"message": f"Se eliminó {value} del ABB."}
        if operation_name == "buscar":
            value = self._require_int(payload, "value", "valor")
            found = self._structure.buscar(value)
            return {"message": f"Búsqueda de {value}: {'encontrado' if found else 'no encontrado'}.", "result": found}
        if operation_name == "minimo":
            result = self._structure.minimo()
            return {"message": f"Mínimo actual: {result}.", "result": result}
        if operation_name == "maximo":
            result = self._structure.maximo()
            return {"message": f"Máximo actual: {result}.", "result": result}
        if operation_name == "altura":
            result = self._structure.altura()
            return {"message": f"Altura actual: {result}.", "result": result}
        if operation_name == "contar_hojas":
            result = self._structure.contar_hojas()
            return {"message": f"Hojas actuales: {result}.", "result": result}
        if operation_name == "inorden":
            result = self._structure.inorden()
            return {"message": f"Recorrido inorden: {result}.", "result": result}
        if operation_name == "preorden":
            result = self._structure.preorden()
            return {"message": f"Recorrido preorden: {result}.", "result": result}
        if operation_name == "postorden":
            result = self._structure.postorden()
            return {"message": f"Recorrido postorden: {result}.", "result": result}
        if operation_name == "validar":
            result = self._structure.validar()
            return {"message": f"Validación ABB: {'correcta' if result else 'inválida'}.", "result": result}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "El ABB se limpió correctamente."}
        raise ValueError(f"Operación no soportada: {operation_name}.")

    def _to_node(self, node: Any) -> dict[str, Any] | None:
        if node is None:
            return None
        return {
            "value": node.dato,
            "left": self._to_node(node.izquierdo),
            "right": self._to_node(node.derecho),
        }

    def to_visual_state(self) -> dict[str, Any]:
        return {
            "kind": "binary_tree",
            "title": "Árbol Binario de Búsqueda (ABB)",
            "root": self._to_node(self._structure._raiz),
            "size": self._structure.tamano(),
            "empty": self._structure.vacio(),
            "height": self._structure.altura(),
            "validation": self._structure.validar(),
            "traversals": {
                "inorden": self._structure.inorden(),
                "preorden": self._structure.preorden(),
                "postorden": self._structure.postorden(),
            },
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {"name": "insertar", "label": "Insertar", "mutates": True, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "eliminar", "label": "Eliminar", "mutates": True, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "buscar", "label": "Buscar", "mutates": False, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "minimo", "label": "Mínimo", "mutates": False, "inputs": []},
            {"name": "maximo", "label": "Máximo", "mutates": False, "inputs": []},
            {"name": "altura", "label": "Altura", "mutates": False, "inputs": []},
            {"name": "contar_hojas", "label": "Contar hojas", "mutates": False, "inputs": []},
            {"name": "inorden", "label": "Inorden", "mutates": False, "inputs": []},
            {"name": "preorden", "label": "Preorden", "mutates": False, "inputs": []},
            {"name": "postorden", "label": "Postorden", "mutates": False, "inputs": []},
            {"name": "validar", "label": "Validar", "mutates": False, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]
