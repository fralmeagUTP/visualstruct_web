from __future__ import annotations

from pathlib import Path


def test_legacy_graph_file_was_removed() -> None:
    root = Path(__file__).resolve().parents[1]
    graph_dir = root / "app" / "domain" / "graph"
    assert not (graph_dir / "grafo.py").exists(), "Legacy file should not exist: grafo.py"
    assert not (graph_dir / "lista_enlazada.py").exists(), "Legacy file should not exist: lista_enlazada.py"
    assert not (graph_dir / "monticulo_binario.py").exists(), "Legacy file should not exist: monticulo_binario.py"


def test_app_does_not_import_legacy_graph_module() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"
    absolute_legacy_imports = [
        "app.domain.graph.grafo",
        "app.domain.graph.lista_enlazada",
        "app.domain.graph.monticulo_binario",
    ]
    relative_legacy_imports = [
        "from .grafo import",
        "from .lista_enlazada import",
        "from .monticulo_binario import",
    ]

    offenders: list[str] = []
    for path in app_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for fragment in absolute_legacy_imports:
            if fragment in text:
                offenders.append(f"{path.relative_to(root)} -> {fragment}")
        if path.parent.name == "graph":
            for fragment in relative_legacy_imports:
                if fragment in text:
                    offenders.append(f"{path.relative_to(root)} -> {fragment}")
    assert not offenders, "Found legacy graph imports:\n" + "\n".join(offenders)
