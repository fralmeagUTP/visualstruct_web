"""Adapter for Red-Black hierarchical structure."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.hierarchical import ColorRN, RojoNegro


class RedBlackAdapter(BaseAdapter):
    """Adapt `RojoNegro` to the common visualizer contract."""

    def __init__(self) -> None:
        self._structure: RojoNegro[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = RojoNegro()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "insertar":
            value = self._require_int(payload, "value", "valor")
            self._structure.insertar(value)
            return {
                "message": f"Se insertó {value} en el Rojo-Negro.",
                "console": ["El numero ha sido insertado"],
            }
        if operation_name == "eliminar":
            value = self._require_int(payload, "value", "valor")
            self._structure.eliminar(value)
            return {"message": f"Se eliminó {value} del Rojo-Negro."}
        if operation_name == "buscar":
            value = self._require_int(payload, "value", "valor")
            found = self._structure.buscar(value)
            return {"message": f"Búsqueda de {value}: {'encontrado' if found else 'no encontrado'}.", "result": found}
        if operation_name == "inorden":
            result = self._structure.inorden()
            return {"message": f"Recorrido inorden: {result}.", "result": result}
        if operation_name == "altura":
            result = self._structure.altura()
            return {"message": f"Altura actual: {result}.", "result": result}
        if operation_name == "validar":
            result = self._structure.validar()
            return {"message": f"Validación Rojo-Negro: {'correcta' if result else 'inválida'}.", "result": result}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "El Rojo-Negro se limpió correctamente."}
        raise ValueError(f"Operación no soportada: {operation_name}.")

    def _to_node(self, node: Any) -> dict[str, Any] | None:
        nil = self._structure._nil
        if node is nil:
            return None
        return {
            "value": node.dato,
            "color": "RED" if node.color == ColorRN.ROJO else "BLACK",
            "left": self._to_node(node.izquierdo),
            "right": self._to_node(node.derecho),
        }

    def to_visual_state(self) -> dict[str, Any]:
        return {
            "kind": "binary_tree",
            "title": "Árbol Rojo-Negro",
            "root": self._to_node(self._structure._raiz),
            "size": self._structure.tamano(),
            "empty": self._structure.vacio(),
            "height": self._structure.altura(),
            "validation": self._structure.validar(),
            "traversals": {"inorden": self._structure.inorden()},
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {"name": "insertar", "label": "Insertar", "mutates": True, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "eliminar", "label": "Eliminar", "mutates": True, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "buscar", "label": "Buscar", "mutates": False, "inputs": [{"name": "value", "label": "Valor", "type": "number"}]},
            {"name": "inorden", "label": "Inorden", "mutates": False, "inputs": []},
            {"name": "altura", "label": "Altura", "mutates": False, "inputs": []},
            {"name": "validar", "label": "Validar", "mutates": False, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]
