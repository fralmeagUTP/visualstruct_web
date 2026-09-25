"""Didactic help content for hash-table module."""

from __future__ import annotations

from typing import Any


class HashHelpService:
    """Serve educational texts for hash-table module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo de tablas hash",
        "description": (
            "Este modulo permite interpretar operaciones de tabla hash sobre codigo C real: "
            "insercion, consulta y eliminacion se reflejan en buckets, colisiones, punteros y memoria."
        ),
        "tips": [
            "Inicializa la tabla con capacidad valida antes de operar.",
            "Usa Reproducir para visualizar el flujo completo y Siguiente/Anterior paso para analizar cada linea.",
                "La capacidad es fija: monitorea cómo factor de carga y colisiones afectan las cadenas.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "hash_table": {
            "title": "Tabla Hash",
            "summary": (
                "Tabla hash de capacidad fija con claves y valores enteros, usando encadenamiento separado. "
                "La animacion sigue el indice hash, la normalizacion de negativos, las colisiones y la memoria."
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
                "La capacidad es fija: no hay resize ni rehash automático en el C interpretado.",
            ],
            "learning_guide": {
                "objective": "Explicar cómo el residuo C selecciona un bucket y cómo la cadena de punteros resuelve una colisión.",
                "strategy": "Calcular índice, normalizar negativos, recorrer actual/anterior y enlazar o liberar solo en la rama ejecutada.",
                "invariants": ["Cada clave está en el bucket normalizado por clave % capacidad.", "Las claves son únicas.", "cantidad coincide con los nodos alcanzables.", "Toda cadena termina en NULL y no tiene ciclos."],
                "memory": "Insertar una clave nueva reserva un THNodo con malloc; actualizar no reserva. Eliminar, vaciar y destruir liberan memoria con free.",
                "complexity": {"mejor": "Θ(1)", "promedio": "Θ(1 + α) con distribución aproximadamente uniforme", "peor": "Θ(n) si todas las claves colisionan"},
                "applications": ["Índices por identificador", "tablas de símbolos", "cachés con clave entera", "conteo y asociación de datos"],
                "common_errors": ["Confundir el módulo de Python con el residuo negativo de C.", "Suponer que la tabla se redimensiona automáticamente.", "Olvidar actualizar anterior al eliminar un nodo intermedio.", "Usar un nodo después de free."],
            },
            "glossary": {"Bucket": "Celda del arreglo que apunta a una cadena.", "Colisión": "Dos claves diferentes seleccionan el mismo bucket.", "Factor de carga α": "cantidad / capacidad.", "Encadenamiento separado": "Estrategia que conserva las colisiones en listas enlazadas.", "Residuo C": "Resultado de %, que puede ser negativo y se normaliza antes de indexar.", "NULL": "Puntero nulo que marca el final de una cadena.", "Capacidad fija": "Número de buckets que no cambia durante la vida de esta implementación."},
            "teacher_guide": ["Pida predecir el bucket antes de mostrar la traza.", "Use capacidad 1 como contraejemplo de distribución.", "Compare las mismas claves en 3, 7 y 17 sin cambiar la entrada.", "Solicite explicar anterior->siguiente antes de eliminar un nodo intermedio.", "Evalúe la justificación mediante la línea C y el invariante, no solo el resultado."],
            "keyboard": ["Alt+→: siguiente paso.", "Alt+←: paso anterior.", "Alt+Inicio: inicio.", "Alt+Fin: final.", "Alt+P: pausar."],
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
