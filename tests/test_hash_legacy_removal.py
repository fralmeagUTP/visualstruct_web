from __future__ import annotations

from pathlib import Path


def test_legacy_hash_files_were_removed() -> None:
    root = Path(__file__).resolve().parents[1]
    hash_dir = root / "app" / "domain" / "hash"
    assert not (hash_dir / "lista_enlazada.py").exists(), "Legacy file should not exist: lista_enlazada.py"
    assert not (hash_dir / "tabla_hash.py").exists(), "Legacy file should not exist: tabla_hash.py"


def test_app_does_not_import_legacy_hash_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"
    absolute_legacy_imports = [
        "app.domain.hash.lista_enlazada",
        "app.domain.hash.tabla_hash",
    ]
    relative_legacy_imports = [
        "from .lista_enlazada import",
        "from .tabla_hash import",
    ]

    offenders: list[str] = []
    for path in app_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for fragment in absolute_legacy_imports:
            if fragment in text:
                offenders.append(f"{path.relative_to(root)} -> {fragment}")
        if path.parent.name == "hash":
            for fragment in relative_legacy_imports:
                if fragment in text:
                    offenders.append(f"{path.relative_to(root)} -> {fragment}")
    assert not offenders, "Found legacy hash imports:\n" + "\n".join(offenders)
