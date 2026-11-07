"""Unit checks for exact E2E stdout observers, including rejecting bad views."""
from __future__ import annotations

import pytest

from e2e_contract_helpers import console_stdout, main_source, observe_before_cleanup


class Console:
    def __init__(self, raw: str | None, visible: str) -> None:
        self.raw = raw
        self.visible = visible

    def get_attribute(self, name: str) -> str | None:
        assert name == "data-console-copy"
        return self.raw

    def text_content(self) -> str:
        return self.visible


class Page:
    def __init__(self, raw: str | None, visible: str) -> None:
        self.console = Console(raw, visible)

    def locator(self, selector: str) -> Console:
        assert selector == "#hier-printf-console"
        return self.console


@pytest.mark.parametrize("stdout", ["", "7 7\n", "\n\n", " áéñ \n áéñ \n"])
def test_stdout_observer_keeps_exact_bytes_and_empty_placeholder(stdout: str) -> None:
    visible = stdout or "(sin salida printf en esta ruta)"
    assert console_stdout(Page(stdout, visible), "#hier-printf-console") == stdout


@pytest.mark.parametrize("raw,visible", [
    (None, "(sin salida printf en esta ruta)"),
    ("", "invented output"),
    ("7 7\n", "7\n"),
    (" áéñ \n", "áéñ"),
])
def test_stdout_observer_rejects_missing_metadata_or_mismatched_view(raw, visible) -> None:
    with pytest.raises(AssertionError):
        console_stdout(Page(raw, visible), "#hier-printf-console")


def test_native_observation_preserves_history_cleanup_and_return() -> None:
    main = "int main(void) {\n    lista_limpiar(&lista);\n    lista_insertar_final(&lista, 7);\n    /* release ownership */ lista_limpiar(&lista);\n    return 0;\n}\n"
    result = observe_before_cleanup(main, "lista_limpiar(&lista);", 'puts("observe");')
    assert result.replace('    puts("observe");\n', "") == main
    assert result.index('puts("observe");') > result.index('lista_insertar_final(&lista, 7);')
    assert result.index('puts("observe");') < result.rindex('lista_limpiar(&lista);')


@pytest.mark.parametrize("main", [
    "int main(void) { return 0; }\n",
    "int main(void) {\n    // lista_limpiar(&lista);\n    return 0;\n}\n",
    "int main(void) {\n    return 0;\n    lista_limpiar(&lista);\n}\n",
])
def test_native_observation_requires_executed_final_cleanup(main: str) -> None:
    with pytest.raises(AssertionError):
        observe_before_cleanup(main, "lista_limpiar(&lista);", 'puts("observe");')


class MainRows:
    def __init__(self, lines, indices):
        self.lines, self.indices = lines, indices

    def all_text_contents(self):
        return self.lines

    def evaluate_all(self, expression):
        return self.indices


class MainBlock:
    def __init__(self, lines, raw, indices):
        self.rows, self.raw = MainRows(lines, indices), raw

    def locator(self, selector):
        assert selector == ".code-line"
        return self.rows

    def evaluate(self, expression):
        return self.raw


class MainPage:
    def __init__(self, lines, raw, indices):
        self.block = MainBlock(lines, raw, indices)

    def locator(self, selector):
        assert selector == ".didactic-history-main"
        return self.block


def test_main_observer_requires_rendered_and_copyable_source_equivalence():
    lines = ['#include <stdio.h>', '', 'int main(void) {', '    return 0;', '}']
    source = "\n".join(lines)
    assert main_source(MainPage(lines, source, list(range(5)))) == source


@pytest.mark.parametrize("lines,raw,indices", [
    (["line"], "other", [0]),
    (["  "], "", [0]),
    ([""], " ", [0]),
    (["    return 0;"], "   return 0;", [0]),
    (["value"], "value ", [0]),
    (["line"], None, [0]),
    (["line"], "line", [1]),
    (["\u00a0"], "\u00a0", [0]),
    ([], "", []),
])
def test_main_observer_rejects_missing_modified_or_reordered_source(lines, raw, indices):
    with pytest.raises(AssertionError):
        main_source(MainPage(lines, raw, indices))


def test_main_observer_reads_shipped_history_renderer_and_exact_copy_source():
    import json
    import subprocess
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(["node", "qa/emit_e2e_main_rows.js"], cwd=root,
                            capture_output=True, text=True, check=True)
    records = json.loads(result.stdout)
    assert {row["family"] for row in records} == {"linked_list", "circular_list", "sublist"}
    for record in records:
        lines, raw, indices = record["lines"], record["raw"], record["indices"]
        assert "" in raw.split("\n") and " " in lines
        # Reproduce the previous observer's failure on the real renderer.
        assert "\n".join(lines) != raw
        assert main_source(MainPage(lines, raw, indices)) == raw
        broken = list(lines)
        index = next(i for i, line in enumerate(lines) if line.startswith("    "))
        broken[index] = broken[index][1:]
        with pytest.raises(AssertionError):
            main_source(MainPage(broken, raw, indices))
