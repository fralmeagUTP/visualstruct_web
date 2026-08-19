"""Base adapter contract for sequential structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class AdapterStateError(ValueError):
    """Base error raised when an adapter state cannot be imported."""


class AdapterStateVersionError(AdapterStateError):
    """Raised when serialized state targets another adapter version."""


class BaseAdapter(ABC):
    """Common contract for every sequential structure adapter."""

    STATE_VERSION: ClassVar[str] = "1"

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

    def export_state(self) -> dict[str, Any]:
        """Export the adapter-owned payload used by a session checkpoint.

        Implementations must return data accepted by ``import_state`` and made
        exclusively of JSON-compatible values. Visual state is deliberately
        not used as the persistence contract because presentation fields may
        evolve independently.
        """
        raise NotImplementedError(
            f"{type(self).__name__} no implementa exportacion de estado."
        )

    def import_state(self, state: dict[str, Any]) -> None:
        """Replace current state atomically from an exported payload.

        Implementations must validate the complete payload before mutating the
        adapter and raise ``AdapterStateError`` for malformed input.
        """
        raise NotImplementedError(
            f"{type(self).__name__} no implementa importacion de estado."
        )

    @classmethod
    def adapter_version(cls) -> str:
        """Return the stable version used for checkpoint compatibility."""
        return cls.STATE_VERSION

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
