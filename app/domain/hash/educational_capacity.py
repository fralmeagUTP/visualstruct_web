"""Visualizer resource policy, not a restriction of the book's C TAD."""
from app.adapters.base_adapter import BaseAdapter

MAX_VISUAL_CAPACITY = 128
CAPACITY_MESSAGE = "El visualizador admite hasta 128 cubetas para mantener legibles y manejables las trazas. Este límite educativo no modifica el TAD C."

def oversized_history_capacity(history):
    """Inspect saved requests without allocating or replaying a table."""
    for step in history:
        if step.get("operation") != "create_table" or not isinstance(step.get("payload"), dict):
            continue
        try:
            capacity = BaseAdapter._require_int(step["payload"], "capacity", "capacidad")
        except (ValueError, TypeError):
            continue
        if capacity > MAX_VISUAL_CAPACITY:
            return capacity
    return None
