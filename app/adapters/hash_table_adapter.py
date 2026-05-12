"""Adapter for hash-table structure."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.hash import TablaHash


class HashTableAdapter(BaseAdapter):
    """Adapt ``TablaHash`` to the common visualizer contract."""

    def __init__(self) -> None:
        self._table: TablaHash[str, str] | None = None
        self._last_operation: dict[str, Any] = {}
        self._last_result: dict[str, Any] | None = None
        self._last_resize_event: dict[str, Any] | None = None
        self.create()

    @property
    def table(self) -> TablaHash[str, str]:
        """Return a non-null table instance."""
        if self._table is None:
            self.create()
        return self._table  # type: ignore[return-value]

    def _record_last_operation(self, name: str, status: str, message: str) -> None:
        """Persist operation outcome for didactic feedback."""
        self._last_operation = {
            "name": name,
            "status": status,
            "message": message,
        }

    def create(self) -> None:
        """Create a new hash table with default capacity."""
        self._table = TablaHash(capacidad=17)
        self._last_result = None
        self._last_resize_event = None
        self._record_last_operation(
            name="create_table",
            status="success",
            message="Tabla hash creada correctamente con capacidad 17.",
        )

    @staticmethod
    def _parse_capacity(payload: dict[str, Any]) -> int:
        """Validate capacity from payload."""
        capacidad = BaseAdapter._require_int(payload, "capacity", "capacidad")
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        return capacidad

    @staticmethod
    def _require_key(payload: dict[str, Any]) -> str:
        """Validate key field."""
        return BaseAdapter._require_text(payload, "key", "clave")

    @staticmethod
    def _require_value(payload: dict[str, Any]) -> str:
        """Validate value field."""
        return BaseAdapter._require_text(payload, "value", "valor")

    def _set_result(self, name: str, result: dict[str, Any]) -> dict[str, Any]:
        """Persist successful operation result."""
        self._last_result = result
        self._record_last_operation(
            name=name,
            status="success",
            message=result.get("message", "Operacion ejecutada correctamente."),
        )
        return result

    def record_failed_operation(self, name: str, message: str) -> None:
        """Persist failed operation for visual state."""
        self._record_last_operation(name=name, status="error", message=message)

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one hash-table operation."""
        if operation_name == "create_table":
            capacidad = self._parse_capacity(payload)
            self._table = TablaHash(capacidad=capacidad)
            self._last_resize_event = None
            self._last_result = None
            return self._set_result(
                operation_name,
                {"message": f"Tabla hash creada con capacidad {capacidad}."},
            )

        if operation_name == "insert":
            key = self._require_key(payload)
            value = self._require_value(payload)
            existed_before = self.table.contiene(key)
            old_capacity = self.table.capacidad()

            self.table.insertar(key, value)

            new_capacity = self.table.capacidad()
            resized = new_capacity != old_capacity
            if resized:
                self._last_resize_event = {
                    "old_capacity": old_capacity,
                    "new_capacity": new_capacity,
                    "reason": "factor_carga_superior_a_0_75",
                }
            else:
                self._last_resize_event = None

            message = (
                f"Se actualizo la clave '{key}' con el nuevo valor."
                if existed_before
                else f"Se inserto la clave '{key}' en la tabla hash."
            )
            if resized:
                message += f" Se redimensiono de {old_capacity} a {new_capacity}."

            return self._set_result(
                operation_name,
                {
                    "message": message,
                    "result": {
                        "updated": existed_before,
                        "resized": resized,
                        "old_capacity": old_capacity,
                        "new_capacity": new_capacity,
                    },
                },
            )

        if operation_name == "get":
            key = self._require_key(payload)
            result = self.table.buscar(key)
            if result is None:
                message = f"La clave '{key}' no existe."
            else:
                message = f"Valor encontrado para '{key}': {result}."
            return self._set_result(operation_name, {"message": message, "result": result})

        if operation_name == "contains":
            key = self._require_key(payload)
            result = self.table.contiene(key)
            message = f"Clave '{key}': {'existe' if result else 'no existe'}."
            return self._set_result(operation_name, {"message": message, "result": result})

        if operation_name == "remove":
            key = self._require_key(payload)
            removed = self.table.eliminar(key)
            if removed:
                message = f"Se elimino la clave '{key}'."
            else:
                message = f"La clave '{key}' no existe; no hubo cambios."
            self._last_resize_event = None
            return self._set_result(operation_name, {"message": message, "result": removed})

        if operation_name == "keys":
            result = self.table.claves()
            return self._set_result(operation_name, {"message": f"Claves: {result}.", "result": result})

        if operation_name == "values":
            result = self.table.valores()
            return self._set_result(operation_name, {"message": f"Valores: {result}.", "result": result})

        if operation_name == "items":
            result = self.table.items()
            return self._set_result(operation_name, {"message": f"Items: {result}.", "result": result})

        if operation_name == "stats":
            result = {
                "size": self.table.tamano(),
                "capacity": self.table.capacidad(),
                "load_factor": self.table.factor_carga(),
            }
            return self._set_result(
                operation_name,
                {
                    "message": (
                        "Tamano: "
                        f"{result['size']}, Capacidad: {result['capacity']}, "
                        f"Factor de carga: {result['load_factor']:.3f}."
                    ),
                    "result": result,
                },
            )

        if operation_name == "clear":
            self.table.limpiar()
            self._last_resize_event = None
            return self._set_result(operation_name, {"message": "Tabla hash limpiada correctamente."})

        raise ValueError(f"Operacion no soportada: {operation_name}.")

    def _buckets_visual_snapshot(self) -> list[dict[str, Any]]:
        """Return serializable bucket list.

        Technical note:
        This method inspects ``TablaHash._buckets`` as a temporary decision
        to support didactic visualization of collisions until a public snapshot
        method exists in the TAD.
        """
        buckets: list[dict[str, Any]] = []
        internal_buckets = getattr(self.table, "_buckets")
        for index, bucket in enumerate(internal_buckets):
            entries = [{"key": entry.clave, "value": entry.valor} for entry in bucket]
            buckets.append(
                {
                    "index": index,
                    "entries": entries,
                    "size": len(entries),
                    "collisions": max(0, len(entries) - 1),
                }
            )
        return buckets

    def to_visual_state(self) -> dict[str, Any]:
        """Serialize hash-table state for frontend rendering."""
        buckets = self._buckets_visual_snapshot()
        total_collisions = sum(bucket["collisions"] for bucket in buckets)
        metadata = {
            "size": self.table.tamano(),
            "capacity": self.table.capacidad(),
            "load_factor": round(self.table.factor_carga(), 6),
            "collisions": total_collisions,
            "is_empty": self.table.tamano() == 0,
            "resized": self._last_resize_event is not None,
            "resize_event": self._last_resize_event,
        }
        return {
            "structure": "hash_table",
            "title": "Tabla Hash (encadenamiento separado)",
            "buckets": buckets,
            "metadata": metadata,
            "last_operation": self._last_operation,
            "last_result": self._last_result,
        }

    def reset(self) -> None:
        """Reset the hash table while keeping current capacity."""
        current_capacity = self.table.capacidad()
        self._table = TablaHash(capacidad=current_capacity)
        self._last_result = None
        self._last_resize_event = None
        self._record_last_operation(
            name="reset",
            status="success",
            message="Estado reiniciado correctamente.",
        )

    def get_supported_operations(self) -> list[dict[str, Any]]:
        """Return dynamic operation metadata for the panel."""
        return [
            {
                "name": "create_table",
                "label": "Crear tabla",
                "mutates": True,
                "inputs": [{"name": "capacity", "label": "Capacidad", "type": "number"}],
            },
            {
                "name": "insert",
                "label": "Insertar/Actualizar clave-valor",
                "mutates": True,
                "inputs": [
                    {"name": "key", "label": "Clave", "type": "text"},
                    {"name": "value", "label": "Valor", "type": "text"},
                ],
            },
            {
                "name": "get",
                "label": "Buscar clave",
                "mutates": False,
                "inputs": [{"name": "key", "label": "Clave", "type": "text"}],
            },
            {
                "name": "contains",
                "label": "Verificar existencia de clave",
                "mutates": False,
                "inputs": [{"name": "key", "label": "Clave", "type": "text"}],
            },
            {
                "name": "remove",
                "label": "Eliminar clave",
                "mutates": True,
                "inputs": [{"name": "key", "label": "Clave", "type": "text"}],
            },
            {"name": "keys", "label": "Listar claves", "mutates": False, "inputs": []},
            {"name": "values", "label": "Listar valores", "mutates": False, "inputs": []},
            {"name": "items", "label": "Listar items", "mutates": False, "inputs": []},
            {"name": "stats", "label": "Tamano/capacidad/factor", "mutates": False, "inputs": []},
            {"name": "clear", "label": "Limpiar tabla", "mutates": True, "inputs": []},
        ]
