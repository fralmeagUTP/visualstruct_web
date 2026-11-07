"""Observers for the approved raw-stdout console and self-contained C main.

Presentation placeholders are not C output. Missing metadata or a visible/raw
mismatch must fail instead of being normalized to an empty successful result.
"""
from __future__ import annotations


def console_stdout(page, selector: str) -> str:
    """Return exact copied stdout and require its visible rendering to agree."""
    console = page.locator(selector)
    raw = console.get_attribute("data-console-copy")
    assert raw is not None, f"Raw stdout metadata missing from {selector}"
    assert console.text_content() == (raw or "(sin salida printf en esta ruta)")
    return raw


def main_source(page, selector: str = ".didactic-history-main") -> str:
    """Read rendered code rows exactly, including spaces and empty lines."""
    block = page.locator(selector)
    lines = block.locator(".code-line").all_text_contents()
    assert lines, "Displayed main must contain source rows"
    assert block.locator(".code-line").evaluate_all("xs => xs.map(x => Number(x.dataset.line))") == list(range(len(lines)))
    source = "\n".join(lines)
    assert "\u00a0" not in source, "Copied C must not contain nonbreaking spaces"
    raw = block.evaluate("el => el.closest('[data-raw-code]')?.dataset.rawCode")
    assert raw is not None, "Copied C metadata is missing"
    raw_lines = raw.split("\n")
    assert len(lines) == len(raw_lines), "Displayed source has missing or extra rows"
    # Sequential history gives empty display rows one layout space. Only an
    # actually empty copied row admits that sentinel; no strip/normalization of
    # nonempty lines, indentation, or trailing spaces is allowed.
    assert all(shown == copied or (copied == "" and shown == " ")
               for shown, copied in zip(lines, raw_lines)), "Displayed source differs from copied C"
    assert "\u00a0" not in raw, "Copied C must not contain nonbreaking spaces"
    return raw


def observe_before_cleanup(main: str, cleanup: str, observation: str) -> str:
    """Insert a native state observation before the caller's final cleanup.

    Keep every displayed byte and the final cleanup. Earlier history operations
    may also clear the same structure, so only the last standalone cleanup line
    is selected, and the terminal return must remain after it.
    """
    lines = main.splitlines(keepends=True)
    candidates = [i for i, line in enumerate(lines) if cleanup in line and not line.lstrip().startswith("//")]
    assert candidates, "The displayed caller must release its owned state"
    index = candidates[-1]
    assert any("return 0;" in line for line in lines[index + 1:]), "Cleanup must precede the caller return"
    return "".join(lines[:index]) + "    " + observation + "\n" + "".join(lines[index:])
