"""Resolve explicitly requested recorded test inputs to verified temporary copies.

This is a test-data reader, not a continuity gate or an agent control. It does
not replace historical evidence or certify a new execution.
"""
from __future__ import annotations
import atexit
import hashlib
import json
import os
from pathlib import Path
import tempfile
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "tests/fixtures/published-audit-inputs"
_extracted = None
_manifest = None
_registered = None
_verified_archive = False
_materialized = set()

def _extended(path: Path) -> Path:
    text = str(path.resolve())
    return Path(chr(92)*2 + "?" + chr(92) + text) if os.name == "nt" and len(text) >= 240 and not text.startswith(chr(92)*2 + "?") else path

def _catalog():
    global _manifest, _registered
    if _manifest is None:
        _manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
        _registered = set()
        for row in _manifest["files"]:
            relative = Path(row["path"].replace("\\", "/"))
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Escaping recorded input")
            _registered.add(relative.as_posix())
            _registered.update(parent.as_posix() for parent in relative.parents if parent.as_posix() != ".")
    return _manifest

def _recorded_root() -> Path:
    global _extracted, _verified_archive
    manifest = _catalog()
    archive = PACKAGE / "inputs.zip"
    if not _verified_archive:
        with archive.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256") if hasattr(hashlib, "file_digest") else None
            if digest is None:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(65536), b""): digest.update(chunk)
        if digest.hexdigest() != manifest["archive_sha256"]:
            raise ValueError("Recorded input archive changed")
        with zipfile.ZipFile(archive) as package:
            if set(package.namelist()) != {row["path"] for row in manifest["files"]}:
                raise ValueError("Recorded input manifest/archive mismatch")
        _verified_archive = True
    if _extracted is None:
        _extracted = Path(tempfile.mkdtemp(prefix="vs-inputs-"))
        cleanup_root = Path(chr(92)*2 + "?" + chr(92) + str(_extracted)) if os.name == "nt" else _extracted
        atexit.register(shutil.rmtree, cleanup_root)
    return _extracted


def _materialize(relative: str | None = None) -> Path:
    manifest = _catalog()
    root = _recorded_root()
    selected = [row for row in manifest["files"] if relative is None or row["path"] == relative or row["path"].startswith(relative.rstrip("/") + "/")]
    pending = [row for row in selected if row["path"] not in _materialized]
    if not pending:
        return root
    archive = PACKAGE / "inputs.zip"
    with zipfile.ZipFile(archive) as package:
        for row in pending:
            target = _extended(root / row["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(); size = 0
            with package.open(row["path"]) as source, target.open("wb") as output:
                for chunk in iter(lambda: source.read(65536), b""):
                    digest.update(chunk); size += len(chunk); output.write(chunk)
            if digest.hexdigest() != row["sha256"] or size != row["bytes"]:
                raise ValueError("Recorded input bytes changed: " + row["path"])
            _materialized.add(row["path"])
    return root


def recorded_input_root() -> Path:
    """Materialize the full declared input tree for consumers that need it."""
    return _materialize()

def audit_input_path(path: str | Path) -> Path:
    """Return a physical copy for a declared input, otherwise the actual path."""
    original = Path(str(path).replace("\\", "/"))
    try:
        relative = original.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return original
    for old, new in [
        ("openspec/changes/audit-local-quality-and-unified-controls/", "openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/"),
        ("openspec/changes/resolve-didactic-stack-c1-residuals/", "openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/")]:
        if relative.startswith(old): relative = new + relative[len(old):]
    _catalog()
    if relative in _registered:
        if original.is_dir() and "/evidence" not in relative and relative != "docs/tads_C":
            return original
        recorded = _extended(_materialize(relative) / relative)
        if "/evidence/" not in relative and original.is_file():
            current_bytes = original.read_bytes()
            recorded_bytes = recorded.read_bytes()
            if current_bytes.replace(b"\r\n", b"\n") != recorded_bytes.replace(b"\r\n", b"\n"):
                raise ValueError("Published source differs beyond Git line endings: " + relative)
        return recorded
    return original
