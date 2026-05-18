"""Didactic help content for hash-table module."""

from __future__ import annotations

from typing import Any


class HashHelpService:
    """Serve educational texts for hash-table module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo de tablas hash",
        "description": (
            "Este modulo permite interpretar operaciones de tabla hash sobre codigo C real: "
            "insercion, consulta y eliminacion se reflejan en buckets, colisiones y "
            "eventos de redimensionamiento durante la simulacion."
        ),
        "tips": [
            "Inicializa la tabla con capacidad valida antes de operar.",
            "Usa Reproducir para visualizar el flujo completo y Siguiente/Anterior paso para analizar cada linea.",
            "Monitorea factor de carga, colisiones por bucket y rehash cuando cambie la capacidad.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "hash_table": {
            "title": "Tabla Hash",
            "summary": (
                "Tabla hash con encadenamiento separado por buckets y redimensionamiento automatico "
                "cuando el factor de carga supera el umbral. En la animacion sigue el calculo del "
                "indice hash, el manejo de colisiones y el rehash de claves tras cambios de capacidad."
            ),
            "supported_operations": [
                "create_table",
                "insert",
                "get",
                "contains",
                "remove",
                "keys",
                "values",
                "items",
                "stats",
                "clear",
            ],
            "pending_operations": [
                "El TAD no expone tecnicas alternativas de hashing (lineal/cuadratico/doble hash).",
                "La visualizacion de buckets usa atributos internos del TAD de forma temporal.",
            ],
        }
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return didactic help for hash module."""
        return HashHelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for one hash structure."""
        return HashHelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        )
