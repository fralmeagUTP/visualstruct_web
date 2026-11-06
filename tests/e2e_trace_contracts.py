"""Exact current-trace stdout and publicly reachable auxiliary views for E2E."""
from __future__ import annotations


def trace_stdout(trace: dict, cursor: int) -> str:
    """Expected current-call bytes, not host feedback or deduplicated messages.

    Raw stdout snapshots are authoritative. Legacy event chunks have the
    documented line separator; snapshot chunks already represent the prefix.
    Session output from earlier calls must be asserted separately by the caller.
    """
    steps = trace["steps"]
    assert -1 <= cursor < len(steps)
    if cursor < 0:
        return ""
    step = steps[cursor]
    if "console_stdout" in step:
        assert isinstance(step["console_stdout"], str)
        return step["console_stdout"]
    mode = trace["console_mode"]
    assert mode in {"events", "snapshot"}, f"Unsupported stdout mode: {mode}"
    frames = [step] if mode == "snapshot" else steps[:cursor + 1]
    chunks = [chunk for frame in frames for chunk in frame["console"]]
    assert all(isinstance(chunk, str) for chunk in chunks)
    return "\n".join(chunks)


def reveal_public(page, locator) -> None:
    """Open ancestor disclosures/tabs using their public controls, never CSS.

    This does not reveal arbitrary hidden content or mutate application state.
    Unreachable content remains a failing accessibility assertion.
    """
    for _ in range(12):
        if locator.is_visible():
            return
        # Outermost hidden ancestor first, so its real control is reachable.
        barrier = locator.evaluate("""el => {
            const chain=[]; for(let p=el;p;p=p.parentElement) chain.unshift(p);
            for(const p of chain) {
                if(p.classList.contains('didactic-technical') && getComputedStyle(p).display==='none') return {kind:'technical'};
                if(p.tagName==='DETAILS' && !p.open) return {kind:'details', id:p.id};
                if(p.hidden && p.id) return {kind:'hidden', id:p.id};
            }
            return null;
        }""")
        assert barrier, "No public disclosure explains the hidden target"
        if barrier["kind"] == "technical":
            switch = page.locator("#didactic-mode-switch")
            assert switch.is_visible() and not switch.is_checked()
            switch.check()
        elif barrier["kind"] == "hidden":
            control = page.locator(f'[aria-controls="{barrier["id"]}"]')
            assert control.count() == 1 and control.is_visible()
            control.click()
        else:
            summary = locator.locator("xpath=ancestor-or-self::details[not(@open)]/summary").first
            assert summary.is_visible()
            summary.click()
    assert locator.is_visible(), "Public disclosure controls did not reveal the target"
