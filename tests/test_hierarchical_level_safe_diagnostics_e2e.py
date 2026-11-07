"""CI-only level-control captures: private loopback app and synthetic integer."""
from __future__ import annotations

import json
import sys
from urllib.parse import urlsplit

import pytest

from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app
from test_rbt_visual_safe_diagnostics_e2e import _capture_local_viewport
from test_hierarchical_education_restored_focal import (
    R,
    assert_level_location,
    assert_unchanged,
    education_snapshot,
    install_education_observer,
    reveal_education_code,
)

pytestmark = pytest.mark.e2e


def _abb_local_target(base):
    parsed = urlsplit(base)
    assert parsed.scheme == "http" and parsed.hostname == "127.0.0.1" and parsed.port
    assert parsed.username is None and parsed.password is None
    assert parsed.path in ("", "/") and not parsed.query and not parsed.fragment
    return base.rstrip("/") + "/hierarchical/abb"


def _assert_level_in_viewport(page):
    level = page.locator("#hier-learning-level")
    level.scroll_into_view_if_needed()
    box = level.bounding_box()
    viewport = page.viewport_size
    assert box and box["width"] > 0 and box["height"] > 0
    assert -1 <= box["x"] and box["x"] + box["width"] <= viewport["width"] + 1
    assert -1 <= box["y"] and box["y"] + box["height"] <= viewport["height"] + 1


@pytest.mark.parametrize("label,width,height", [
    ("desktop", 1366, 1000),
    ("narrow", 390, 844),
])
def test_level_code_location_safe_viewport_and_resize(controls40_page, label, width, height):
    page, context, base = controls40_page
    target = _abb_local_target(base)
    out = R / "visual-safe-diagnostics"
    out.mkdir(exist_ok=True)
    page.set_viewport_size({"width": width, "height": height})
    install_education_observer(page)
    errors, posts, external_requests = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: posts.append(request.url) if request.method == "POST" else None)

    # No outside origin is loaded into the private diagnostic page.
    origin = urlsplit(base)
    def local_only(route):
        requested = urlsplit(route.request.url)
        if (requested.scheme, requested.netloc) == (origin.scheme, origin.netloc):
            route.continue_()
        else:
            external_requests.append(True)
            route.abort()
    context.route("**/*", local_only)

    failure = None
    try:
        page.goto(target, wait_until="networkidle")
        _capture_local_viewport(page, target, out / f"level-{label}-initial-{width}x{height}.png")
        # The outer finally captures failure even if a public reveal is broken.
        reveal_education_code(page)
        page.locator("#hier-learning-level").scroll_into_view_if_needed()
        _capture_local_viewport(page, target, out / f"level-{label}-reveal-{width}x{height}.png")
        assert_level_location(page)
        _assert_level_in_viewport(page)

        # A real, small local trace makes value preservation a functional check.
        page.select_option("#operation-select", "insertar")
        page.locator("#h-field-value").fill("7")
        if not page.locator("#hier-step-toggle").is_checked():
            page.click("#hier-step-mode")
        with page.expect_response(lambda response: response.url == base + "/hierarchical/abb/operate" and response.request.method == "POST") as pending:
            page.click("#hier-sim-play")
        data = pending.value.json()
        assert data["success"]
        page.wait_for_function("()=>window.__eduTrace?.steps?.length>0")
        page.click("#hier-sim-step")
        assert page.evaluate("window.__eduPlayer.getCursor()") == 0
        before, count = education_snapshot(page), len(posts)
        trace_before = page.evaluate("JSON.stringify(window.__eduTrace)")
        assert count == 1
        level = page.locator("#hier-learning-level")
        level.select_option("advanced")
        level.scroll_into_view_if_needed()
        _capture_local_viewport(page, target, out / f"level-{label}-advanced-{width}x{height}.png")
        assert level.input_value() == "advanced"
        assert "Avanzado" in page.locator("#hier-level-guide").inner_text()
        assert_unchanged(page, before, posts, count)

        page.locator("#didactic-mode-switch").uncheck()
        assert not level.is_visible()
        assert level.input_value() == "advanced"
        assert_unchanged(page, before, posts, count)
        reveal_education_code(page)
        level.scroll_into_view_if_needed()
        _capture_local_viewport(page, target, out / f"level-{label}-reopened-{width}x{height}.png")
        assert_level_location(page)
        assert level.input_value() == "advanced"
        assert_unchanged(page, before, posts, count)

        alternate = {"width": 390, "height": 844} if width == 1366 else {"width": 1366, "height": 1000}
        for phase, viewport in [("resized", alternate), ("restored", {"width": width, "height": height})]:
            page.set_viewport_size(viewport)
            reveal_education_code(page)
            level.scroll_into_view_if_needed()
            _capture_local_viewport(page, target, out / f"level-{label}-{phase}-{viewport['width']}x{viewport['height']}.png")
            assert_level_location(page)
            _assert_level_in_viewport(page)
            assert level.input_value() == "advanced"
            assert "Avanzado" in page.locator("#hier-level-guide").inner_text()
            assert_unchanged(page, before, posts, count)
        assert page.evaluate("JSON.stringify(window.__eduTrace)") == trace_before
        assert not external_requests and not errors
        (out / f"level-{label}-result.json").write_text(json.dumps({
            "synthetic_data_only": True,
            "route": "/hierarchical/abb",
            "operation": "insertar",
            "value": 7,
            "viewport": {"width": width, "height": height},
            "alternate_viewport": alternate,
            "selected_level": "advanced",
            "level_and_two_guides_unique_in_code": True,
            "close_reopen_resize_preserved_value_and_trace": True,
            "main_operation_posts": count,
            "extra_posts": len(posts) - count,
            "external_requests": len(external_requests),
            "JS_errors": errors,
            "scope": "Viewport screenshots, public controls, desktop/narrow. Not a universal accessibility audit.",
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    except BaseException as exc:
        failure = exc
        raise
    finally:
        try:
            _capture_local_viewport(page, target, out / f"level-{label}-final.png")
        except BaseException as diagnostic_error:
            if failure is None:
                raise
            note = f"Viewport diagnostic unavailable: {type(diagnostic_error).__name__}: {diagnostic_error}"
            try:
                add_note = getattr(failure, "add_note", None)
                if callable(add_note):
                    add_note(note)
                else:
                    print(note, file=sys.stderr)  # Python 3.10.
            except Exception:
                pass  # Never replace the original UI failure with reporting.
