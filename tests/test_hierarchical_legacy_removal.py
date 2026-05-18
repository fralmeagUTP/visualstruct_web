from __future__ import annotations

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


def test_app_does_not_import_legacy_hierarchical_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"
    absolute_legacy_imports = [
        "app.domain.hierarchical.abb",
        "app.domain.hierarchical.avl",
        "app.domain.hierarchical.rojo_negro",
        "app.domain.hierarchical.monticulo_binario",
    ]
    relative_legacy_imports = [
        "from .abb import",
        "from .avl import",
        "from .rojo_negro import",
        "from .monticulo_binario import",
    ]

    offenders: list[str] = []
    for path in app_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for fragment in absolute_legacy_imports:
            if fragment in text:
                offenders.append(f"{path.relative_to(root)} -> {fragment}")
        if path.parent.name == "hierarchical":
            for fragment in relative_legacy_imports:
                if fragment in text:
                    offenders.append(f"{path.relative_to(root)} -> {fragment}")
    assert not offenders, "Found legacy hierarchical imports:\n" + "\n".join(offenders)
