"""Test-only C observation of private return diagnostics, not a public API shim.

The original downloadable C is compiled separately. This derivative records the
actual local diagnostic immediately after evaluating each public return value.
No branch, allocation or graph mutation is added or replaced.
"""
import re


def instrument_private_diagnostics(source):
    pattern = re.compile(r'^(Grafo|ListaVertice|ListaArco) (grafo_\w+)\([^{}]*\) \{', re.M)
    patches = []
    for match in pattern.finditer(source):
        start = match.end()
        depth = 1
        cursor = start
        while depth:
            depth += (source[cursor] == '{') - (source[cursor] == '}')
            cursor += 1
        body = source[start:cursor-1]
        if 'GrafoEstado diagnostico = GRAFO_OK;' not in body:
            continue
        typ = match[1]
        body = re.sub(r'\breturn\s+([^;]+);',
                      lambda ret: '{ '+typ+' qa_result = '+ret[1]+'; qa_status = diagnostico; return qa_result; }', body)
        patches.append((start, cursor-1, body))
    assert len(patches) == 10
    for start, end, body in reversed(patches):
        source = source[:start]+body+source[end:]
    return 'int qa_status = 0;\n'+source


def write_observed_graph(source_path, output_path):
    """Write QA-only derivative. Caller must also compile original source."""
    from pathlib import Path
    source = Path(source_path).read_text(encoding="utf-8-sig")
    Path(output_path).write_text(instrument_private_diagnostics(source), encoding="utf-8")
    return Path(output_path)


if __name__ == "__main__":
    import sys
    write_observed_graph(sys.argv[1], sys.argv[2])
