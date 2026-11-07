"""Exercise the actual CI capture function with doubles, without a browser."""
from pathlib import Path

import pytest

import test_hierarchical_level_safe_diagnostics_e2e as diagnostics


class RevealFailure(RuntimeError):
    # Exercise the supported Python 3.10 fallback even under Python 3.11+.
    add_note = None


class _Switch:
    def __init__(self, failure):
        self.failure = failure

    def is_checked(self):
        return False

    def check(self):
        raise self.failure


class _Page:
    def __init__(self, reveal_failure=None, redirected_url=None):
        self.url = "about:blank"
        self.reveal_failure = reveal_failure
        self.redirected_url = redirected_url
        self.captures = []

    def set_viewport_size(self, size):
        self.viewport_size = size

    def add_init_script(self, script):
        assert "__eduPlayer" in script

    def on(self, event, handler):
        pass

    def goto(self, target, wait_until):
        self.url = self.redirected_url or target

    def locator(self, selector):
        assert selector == "#didactic-mode-switch"
        return _Switch(self.reveal_failure)

    def screenshot(self, *, path, full_page):
        assert full_page is False
        self.captures.append(Path(path).name)
        if len(self.captures) > 1:
            raise RuntimeError("screenshot unavailable")


class _Context:
    def route(self, pattern, handler):
        assert pattern == "**/*"
        self.handler = handler


def test_level_capture_preserves_reveal_failure_when_final_capture_fails(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(diagnostics, "R", tmp_path)
    primary = RevealFailure("public code reveal failed")
    page = _Page(reveal_failure=primary)
    with pytest.raises(RevealFailure) as caught:
        diagnostics.test_level_code_location_safe_viewport_and_resize(
            (page, _Context(), "http://127.0.0.1:43123"), "desktop", 1366, 1000,
        )
    assert caught.value is primary
    assert page.captures == ["level-desktop-initial-1366x1000.png", "level-desktop-final.png"]
    assert "Viewport diagnostic unavailable: RuntimeError: screenshot unavailable" in capsys.readouterr().err


def test_level_capture_refuses_external_redirect(monkeypatch, tmp_path):
    monkeypatch.setattr(diagnostics, "R", tmp_path)
    page = _Page(redirected_url="https://example.invalid/unexpected")
    with pytest.raises(AssertionError, match="Refusing screenshot of unexpected destination"):
        diagnostics.test_level_code_location_safe_viewport_and_resize(
            (page, _Context(), "http://127.0.0.1:43123"), "narrow", 390, 844,
        )
    assert page.captures == []
