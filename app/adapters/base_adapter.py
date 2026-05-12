"""Base adapter contract for sequential structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Common contract for every sequential structure adapter."""

    @abstractmethod
    def create(self) -> None:
        """Create or recreate the underlying structure instance."""

    @abstractmethod
    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one operation and return a didactic result payload."""

    @abstractmethod
    def to_visual_state(self) -> dict[str, Any]:
        """Return a serializable state for the visual layer."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the structure to an empty state."""

    @abstractmethod
    def get_supported_operations(self) -> list[dict[str, Any]]:
        """Return operation metadata for the dynamic panel."""

    @staticmethod
    def _require_text(payload: dict[str, Any], key: str, label: str) -> str:
        """Return a required trimmed text field."""
        value = payload.get(key)
        if value is None:
            raise ValueError(f"El campo '{label}' es obligatorio.")
        text = str(value).strip()
        if not text:
            raise ValueError(f"El campo '{label}' es obligatorio.")
        return text

    @staticmethod
    def _require_int(payload: dict[str, Any], key: str, label: str) -> int:
        """Return a required integer field."""
        text = BaseAdapter._require_text(payload=payload, key=key, label=label)
        try:
            return int(text)
        except ValueError as error:
            raise ValueError(f"El campo '{label}' debe ser un número entero.") from error
