"""Apply reviewed inventory dispositions without editing historical artifacts."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


def inventory_identity(inventory: dict[str, Any]) -> str:
    """Bind the overlay to the exact set of original IDs, not a mutable count."""
    ids = sorted(item["id"] for item in inventory["items"])
    return hashlib.sha256(json.dumps(ids, ensure_ascii=False).encode()).hexdigest()


def apply_disposition_overlay(inventory: dict, bindings: dict, overlay: dict, *, project_root: Path) -> tuple[dict, dict, dict, list[str]]:
    """Return independent active copies and fail-closed disposition diagnostics.

    Retired widgets never receive PASS or executable coverage. The caller still
    validates every active binding with the ordinary executable gate.
    """
    active, assigned = deepcopy(inventory), deepcopy(bindings)
    errors: list[str] = []
    if not isinstance(overlay, dict) or overlay.get("schema") != "app-disposition-overlay/v1":
        return active, assigned, {}, ["Overlay inválido."]
    rows, additions = overlay.get("dispositions"), overlay.get("additions")
    if not isinstance(rows, list) or not isinstance(additions, list):
        return active, assigned, {}, ["Filas de overlay inválidas."]
    if overlay.get("original_identity") != inventory_identity(inventory):
        errors.append("Identidad original del overlay no coincide.")
    original = {item["id"]: item for item in inventory["items"]}
    seen: set[str] = set()
    retired: dict[str, dict] = {}
    root = project_root.resolve()
    def check_reference(reference: Any) -> bool:
        if not isinstance(reference, dict):
            return False
        try:
            path = (root / reference["path"]).resolve()
            path.relative_to(root)
            return hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
        except (KeyError, TypeError, ValueError, OSError):
            return False
    for row in rows:
        if not isinstance(row, dict):
            errors.append("Disposición inválida.")
            continue
        identifier = row.get("id")
        if identifier not in original or identifier in seen:
            errors.append(f"ID de disposición desconocido o duplicado: {identifier}")
            continue
        seen.add(identifier)
        status = row.get("status")
        if status not in {"RETIRED_AUTHORIZED", "RETIRED_DEPENDENCY", "ACTIVE_REPLACEMENT"}:
            errors.append(f"Estado de disposición inválido: {identifier}")
            continue
        if not check_reference(row.get("decision")):
            errors.append(f"Decisión ausente o cambiada: {identifier}")
        if status.startswith("RETIRED"):
            if original[identifier].get("category") != "control" or row.get("binding") is not None or row.get("result") != "NOT_PASS":
                errors.append(f"Retiro debe ser control sin binding ni PASS: {identifier}")
            retired[identifier] = row
        else:
            if not isinstance(row.get("binding"), dict) or not check_reference(row.get("evidence")):
                errors.append(f"Sustitución sin prueba/evidencia válida: {identifier}")
            else:
                assigned.setdefault("items", {})[identifier] = deepcopy(row["binding"])
    for identifier, row in retired.items():
        if row["status"] == "RETIRED_DEPENDENCY":
            dependency = retired.get(row.get("depends_on"))
            if dependency is None or dependency["status"] != "RETIRED_AUTHORIZED" or not check_reference(row.get("dependency_analysis")):
                errors.append(f"Dependencia de retiro inválida: {identifier}")
    active["items"] = [item for item in active["items"] if item["id"] not in retired]
    for identifier in retired:
        assigned.get("items", {}).pop(identifier, None)
    known = set(original)
    for addition in additions:
        if not isinstance(addition, dict) or not isinstance(addition.get("item"), dict):
            errors.append("Adición inválida.")
            continue
        item = addition["item"]
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.startswith("control:dynamic:") or identifier in known or item.get("category") != "control":
            errors.append(f"ID dinámico inválido o duplicado: {identifier}")
            continue
        known.add(identifier)
        if not isinstance(addition.get("binding"), dict) or not check_reference(addition.get("evidence")) or not check_reference(addition.get("decision")):
            errors.append(f"Adición sin decisión/prueba/evidencia válida: {identifier}")
            continue
        active["items"].append(deepcopy(item))
        assigned.setdefault("items", {})[identifier] = deepcopy(addition["binding"])
    counts: dict[str, int] = {}
    for item in active["items"]:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    active["items"].sort(key=lambda item: item["id"])
    active["summary"] = {"total": len(active["items"]), "by_category": counts}
    active_ids = {item["id"] for item in active["items"]}
    bound = active_ids.intersection(assigned.get("items", {}))
    summary = {"original": len(original), "retired_authorized_not_PASS": sum(row["status"] == "RETIRED_AUTHORIZED" for row in retired.values()), "retired_dependency_not_PASS": sum(row["status"] == "RETIRED_DEPENDENCY" for row in retired.values()), "added": len(active_ids - set(original)), "active": len(active_ids), "bound": len(bound), "pending": sorted(active_ids - bound), "new_executions": 0}
    expected = overlay.get("expected_summary")
    if expected != {key: summary[key] for key in ("original", "retired_authorized_not_PASS", "retired_dependency_not_PASS", "added", "active", "bound")}:
        errors.append("Contabilidad del overlay no coincide.")
    return active, assigned, summary, errors
