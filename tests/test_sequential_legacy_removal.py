from __future__ import annotations

from pathlib import Path


def test_legacy_sequential_files_were_removed() -> None:
    root = Path(__file__).resolve().parents[1]
    seq_dir = root / "app" / "domain" / "sequential"
    legacy = {
        "cola.py",
        "cola_prioridad.py",
        "lista_circular.py",
        "lista_enlazada.py",
        "monticulo_binario.py",
        "pila.py",
        "sublista.py",
    }
    for name in legacy:
        assert not (seq_dir / name).exists(), f"Legacy file should not exist: {name}"


def test_app_does_not_import_legacy_sequential_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"
    absolute_legacy_imports = [
        "app.domain.sequential.cola",
        "app.domain.sequential.cola_prioridad",
        "app.domain.sequential.lista_circular",
        "app.domain.sequential.lista_enlazada",
        "app.domain.sequential.monticulo_binario",
        "app.domain.sequential.pila",
        "app.domain.sequential.sublista",
    ]
    relative_legacy_imports = [
        "from .cola import",
        "from .cola_prioridad import",
        "from .lista_circular import",
        "from .lista_enlazada import",
        "from .monticulo_binario import",
        "from .pila import",
        "from .sublista import",
    ]

    offenders: list[str] = []
    for path in app_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for fragment in absolute_legacy_imports:
            if fragment in text:
                offenders.append(f"{path.relative_to(root)} -> {fragment}")
        if path.parent.name == "sequential":
            for fragment in relative_legacy_imports:
                if fragment in text:
                    offenders.append(f"{path.relative_to(root)} -> {fragment}")
    assert not offenders, "Found legacy sequential imports:\n" + "\n".join(offenders)
