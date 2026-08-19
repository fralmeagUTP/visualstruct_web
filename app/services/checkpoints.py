"""Versioned, deterministic session checkpoint envelopes."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Any, Mapping

from app.adapters.base_adapter import BaseAdapter


CHECKPOINT_SCHEMA_VERSION = 1
_PAYLOAD_FIELDS = (
    "schema_version",
    "history_offset",
    "structure_id",
    "adapter_version",
    "state",
)
_CHECKPOINT_FIELDS = frozenset((*_PAYLOAD_FIELDS, "checksum"))


class CheckpointError(ValueError):
    """Base error for checkpoints that cannot be trusted or consumed."""


class CheckpointFormatError(CheckpointError):
    """Raised when the checkpoint is incomplete or not JSON-compatible."""


class CheckpointCompatibilityError(CheckpointError):
    """Raised when schema, structure, or adapter version is incompatible."""


class CheckpointChecksumError(CheckpointError):
    """Raised when checkpoint contents do not match their checksum."""


@dataclass(frozen=True, slots=True)
class SessionCheckpoint:
    """Validated checkpoint value object safe to pass to reconstruction code."""

    schema_version: int
    history_offset: int
    structure_id: str
    adapter_version: str
    state: dict[str, Any]
    checksum: str

    def to_dict(self) -> dict[str, Any]:
        """Return a detached JSON-serializable representation."""
        return {
            "schema_version": self.schema_version,
            "history_offset": self.history_offset,
            "structure_id": self.structure_id,
            "adapter_version": self.adapter_version,
            "state": deepcopy(self.state),
            "checksum": self.checksum,
        }


def _canonical_json(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as error:
        raise CheckpointFormatError(
            "El checkpoint contiene valores no compatibles con JSON."
        ) from error


def _calculate_checksum(payload: Mapping[str, Any]) -> str:
    encoded = _canonical_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def create_checkpoint(
    *,
    structure_id: str,
    history_offset: int,
    adapter: BaseAdapter,
) -> SessionCheckpoint:
    """Create a signed envelope from one checkpoint-capable adapter."""
    normalized_structure = structure_id.strip() if isinstance(structure_id, str) else ""
    if not normalized_structure:
        raise CheckpointFormatError("El identificador de estructura es obligatorio.")
    if type(history_offset) is not int or history_offset < 0:
        raise CheckpointFormatError("La posicion del historial debe ser un entero no negativo.")

    state = adapter.export_state()
    if not isinstance(state, dict):
        raise CheckpointFormatError("El adapter debe exportar el estado como un objeto JSON.")

    payload = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "history_offset": history_offset,
        "structure_id": normalized_structure,
        "adapter_version": adapter.adapter_version(),
        "state": deepcopy(state),
    }
    checksum = _calculate_checksum(payload)
    return SessionCheckpoint(**payload, checksum=checksum)


def validate_checkpoint(
    raw_checkpoint: Mapping[str, Any],
    *,
    expected_structure_id: str,
    expected_adapter_version: str,
) -> SessionCheckpoint:
    """Validate and detach an untrusted session checkpoint.

    Validation never mutates an adapter. Callers may import ``result.state``
    only after this function succeeds.
    """
    if not isinstance(raw_checkpoint, Mapping):
        raise CheckpointFormatError("El checkpoint debe ser un objeto JSON.")
    if set(raw_checkpoint) != _CHECKPOINT_FIELDS:
        missing = sorted(_CHECKPOINT_FIELDS - set(raw_checkpoint))
        extra = sorted(set(raw_checkpoint) - _CHECKPOINT_FIELDS)
        detail = []
        if missing:
            detail.append(f"faltan: {', '.join(missing)}")
        if extra:
            detail.append(f"sobran: {', '.join(extra)}")
        raise CheckpointFormatError(f"Campos de checkpoint invalidos ({'; '.join(detail)}).")

    schema_version = raw_checkpoint["schema_version"]
    history_offset = raw_checkpoint["history_offset"]
    structure_id = raw_checkpoint["structure_id"]
    adapter_version = raw_checkpoint["adapter_version"]
    state = raw_checkpoint["state"]
    checksum = raw_checkpoint["checksum"]

    if type(schema_version) is not int:
        raise CheckpointFormatError("La version de esquema debe ser un entero.")
    if schema_version != CHECKPOINT_SCHEMA_VERSION:
        raise CheckpointCompatibilityError(
            f"Version de checkpoint no soportada: {schema_version}."
        )
    if type(history_offset) is not int or history_offset < 0:
        raise CheckpointFormatError("La posicion del historial debe ser un entero no negativo.")
    if not isinstance(structure_id, str) or not structure_id:
        raise CheckpointFormatError("El identificador de estructura es invalido.")
    if structure_id != expected_structure_id:
        raise CheckpointCompatibilityError("El checkpoint pertenece a otra estructura.")
    if not isinstance(adapter_version, str) or not adapter_version:
        raise CheckpointFormatError("La version del adapter es invalida.")
    if adapter_version != expected_adapter_version:
        raise CheckpointCompatibilityError("La version del adapter no es compatible.")
    if not isinstance(state, dict):
        raise CheckpointFormatError("El estado del checkpoint debe ser un objeto JSON.")
    if (
        not isinstance(checksum, str)
        or len(checksum) != 64
        or any(character not in "0123456789abcdef" for character in checksum)
    ):
        raise CheckpointFormatError("El checksum SHA-256 tiene un formato invalido.")

    payload = {field: deepcopy(raw_checkpoint[field]) for field in _PAYLOAD_FIELDS}
    expected_checksum = _calculate_checksum(payload)
    if not hmac.compare_digest(checksum, expected_checksum):
        raise CheckpointChecksumError("El checksum del checkpoint no coincide con su contenido.")

    return SessionCheckpoint(**payload, checksum=checksum)
