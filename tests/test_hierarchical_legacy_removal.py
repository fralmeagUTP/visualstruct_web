from __future__ import annotations

import ast
from importlib.util import resolve_name

import pytest


from pathlib import Path


def test_legacy_hierarchical_files_were_removed() -> None:
    root = Path(__file__).resolve().parents[1]
    hier_dir = root / "app" / "domain" / "hierarchical"
    legacy = {
        "abb.py",
        "avl.py",
        "rojo_negro.py",
        "monticulo_binario.py",
    }
    for name in legacy:
        assert not (hier_dir / name).exists(), f"Legacy file should not exist: {name}"


LEGACY_MODULES = frozenset({
    "app.domain.hierarchical.abb",
    "app.domain.hierarchical.avl",
    "app.domain.hierarchical.rojo_negro",
    "app.domain.hierarchical.monticulo_binario",
})


def _legacy_imports(source: str, *, module: str, is_package: bool = False) -> list[str]:
    """Find exact retired module imports, including relative/from-package forms."""
    package = module if is_package else module.rpartition(".")[0]
    candidates: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            candidates.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                base = resolve_name("." * node.level + base, package)
            candidates.append(base)
            candidates.extend(f"{base}.{alias.name}" for alias in node.names)
    return [name for name in candidates
            if any(name == retired or name.startswith(retired + ".")
                   for retired in LEGACY_MODULES)]


def test_app_does_not_import_legacy_hierarchical_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []
    for path in (root / "app").rglob("*.py"):
        parts = path.relative_to(root).with_suffix("").parts
        is_package = parts[-1] == "__init__"
        module = ".".join(parts[:-1] if is_package else parts)
        for imported in _legacy_imports(path.read_text(encoding="utf-8-sig"),
                                        module=module, is_package=is_package):
            offenders.append(f"{path.relative_to(root)} -> {imported}")
    assert not offenders, "Found legacy hierarchical imports:\n" + "\n".join(offenders)


@pytest.mark.parametrize("source,module,is_package", [
    ("import app.domain.hierarchical.abb", "app.services.example", False),
    ("from app.domain.hierarchical.avl import Nodo", "app.services.example", False),
    ("from app.domain.hierarchical import rojo_negro", "app.services.example", False),
    ("from .abb import Nodo", "app.domain.hierarchical.example", False),
    ("from ..hierarchical import monticulo_binario", "app.domain.sequential.example", False),
    ("from .avl import Nodo", "app.domain.hierarchical", True),
    ("import app.domain.hierarchical.abb.child", "app.services.example", False),
])
def test_legacy_detector_rejects_real_imports(source, module, is_package):
    assert _legacy_imports(source, module=module, is_package=is_package)


@pytest.mark.parametrize("source", [
    "import app.domain.hierarchical.abb_instruction",
    "from app.domain.hierarchical.avl_insert_instruction import build",
    "from .abb_instruction import build",
    "from app.domain.hierarchical import abb_instruction",
    "# from .abb import Nodo\ntext = 'app.domain.hierarchical.abb'",
])
def test_legacy_detector_accepts_instruction_modules_and_nonimports(source):
    assert _legacy_imports(source, module="app.domain.hierarchical.example") == []
