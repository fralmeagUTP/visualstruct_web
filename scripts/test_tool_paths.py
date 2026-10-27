"""Locate an existing testing tool without skipping checks or changing app config."""
from pathlib import Path
import os
import shutil

_LEGACY_WINDOWS_DOXYGEN = Path(r"C:\Users\fralm\Documents\Codex\2026-09-30\task-2\doxygen-tool\doxygen.exe")

def resolve_doxygen():
    found = shutil.which("doxygen")
    if found:
        return found
    # Preserve the already reviewed local Windows tool when it is not on PATH.
    if os.name == "nt" and _LEGACY_WINDOWS_DOXYGEN.is_file():
        return str(_LEGACY_WINDOWS_DOXYGEN)
    raise RuntimeError("Doxygen is required: install it on the test runner and put it on PATH")
