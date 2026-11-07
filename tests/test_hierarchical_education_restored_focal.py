"""Four-family education contract reconciled by the 2026-11-06 decision."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from test_residual58_focal_cases import residual58_app
from test_controls40_real_flows import controls40_page

R = Path(__file__).resolve().parents[1]
FAMILIES = ["abb", "avl", "red_black", "binary_heap"]
EXAMPLES = {"abb": "search", "avl": "ll", "red_black": "black-parent", "binary_heap": "single"}


def install_education_observer(page):
    """Observe the real player, without revealing UI or replacing actions."""
    script = (R / "tests/_audit_hash_query_medium_browser.py").read_text(encoding="utf-8-sig")
    script = script.split('INJECT="""')[1].split('"""')[0]
    page.add_init_script(script.replace("localStorage.setItem('didactic-mode','full');", "").replace("__hash", "__edu"))


def open_summary(summary):
    summary.focus()
    if summary.locator("..").get_attribute("open") is None:
        summary.press("Space")
    assert summary.locator("..").get_attribute("open") is not None
    assert summary.evaluate("el => document.activeElement === el")


def reveal_education_code(page):
    """Only the public technical-mode switch and responsive Code tab."""
    switch = page.locator("#didactic-mode-switch")
    if not switch.is_checked():
        switch.check()
    code_tab = page.locator('[data-hier-tab="code"]')
    if code_tab.is_visible():
        code_tab.click()


def assert_level_location(page):
    for identifier in ["hier-learning-level", "hier-level-contract", "hier-level-guide"]:
        assert page.locator(f"#{identifier}").count() == 1
        assert page.locator(f"#hier-code-region #{identifier}").count() == 1
    level = page.locator("#hier-learning-level")
    assert level.is_visible()
    assert page.locator('label[for="hier-learning-level"]').count() == 1
    assert set((level.get_attribute("aria-describedby") or "").split()) == {"hier-level-contract", "hier-level-guide"}
    level.focus()
    assert level.evaluate("el => document.activeElement === el")


def open_panel(page, label):
    if page.locator("#hier-understand-toggle").get_attribute("aria-expanded") == "false":
        page.click("#hier-understand-toggle")
    summary = page.locator("details.hier-learning-disclosure > summary").filter(has_text=re.compile("^" + re.escape(label) + "$"))
    open_summary(summary)
    assert summary.locator('xpath=ancestor::section[@aria-labelledby="hier-understand-title"]').count() == 1


def education_snapshot(page):
    """Observed player state and code, not merely the cached initial model."""
    return page.evaluate("""() => ({
        cursor: window.__eduPlayer.getCursor(),
        rendered: window.__eduRendered,
        active: [...document.querySelectorAll('#op-pseudocode .sim-active')].map(e => e.dataset.line),
        code: document.querySelector('#op-pseudocode').textContent,
        history: document.querySelector('#action-history').textContent
    })""")


def assert_unchanged(page, before, posts, count):
    assert education_snapshot(page) == before
    assert len(posts) == count


def next_decision(trace, cursor):
    """Independent oracle from the HTTP trace, never the UI controller."""
    for index, step in enumerate(trace["steps"]):
        frame = step.get("pedagogy", {})
        condition = frame.get("condition") or {}
        if index > cursor and frame.get("concept") in {"compare", "condition", "comparison"} and type(condition.get("result")) is bool:
            return index, frame
    raise AssertionError("The selected public example must contain another evaluated C condition")


def assert_prediction_evidence(page, decision):
    index, frame = decision
    condition = frame["condition"]
    source = condition.get("source") or frame.get("source", {}).get("line_text")
    assert isinstance(source, str) and source
    prompt = page.locator("#hier-prediction-prompt").inner_text()
    assert f"paso {index + 1}" in prompt and source in prompt
    feedback = page.locator("#hier-prediction-feedback").inner_text()
    assert "futura" in feedback and "estado visible no cambia" in feedback
    assert f"paso {index + 1}" in feedback
    assert ("Verdadero" if condition["result"] else "Falso") in feedback
    assert (condition.get("substituted") or source) in feedback
    branch = frame.get("executed_branch") or condition.get("consequence")
    if branch:
        assert branch in feedback
    assert "cursor se conserva" in feedback


def assert_progress(page, correct, attempts):
    assert f"{correct} aciertos de {attempts} intentos" in page.locator("#hier-progress-summary").inner_text()


def assert_full_narration(page, narration):
    """Concise initial points may differ, but complete explanation is reachable."""
    panel = page.locator("#hier-pedagogy-summary")
    assert panel.is_visible()
    for summary in panel.locator("details > summary").all():
        open_summary(summary)
    visible = " ".join(panel.inner_text().split())
    # Labels can separate sentences, but selected-level content cannot vanish.
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", narration):
        if sentence.strip():
            assert " ".join(sentence.split()) in visible


def advance_to(page, index, posts, count):
    cursor = page.evaluate("window.__eduPlayer.getCursor()")
    assert cursor <= index
    for expected in range(cursor + 1, index + 1):
        page.click("#hier-sim-step")
        assert page.evaluate("window.__eduPlayer.getCursor()") == expected
        assert len(posts) == count


@pytest.mark.e2e
@pytest.mark.parametrize("family", FAMILIES)
def test_restored_education_real_functions_and_manual_navigation(controls40_page, tmp_path, family):
    page, context, base = controls40_page
    install_education_observer(page)
    errors, posts = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: posts.append(request.url) if request.method == "POST" else None)
    page.goto(base + "/hierarchical/" + family, wait_until="networkidle")
    reveal_education_code(page)
    assert_level_location(page)
    open_summary(page.locator("details.classroom-examples > summary"))
    assert page.locator("#hier-guided-example").is_visible()
    assert page.locator("#hier-guided-example").locator("xpath=ancestor::section[1]").get_attribute("aria-labelledby") == "hier-prepare-title"
    headings = page.locator("h3").evaluate_all(r"els=>els.map(e=>e.textContent.replace(/\s+/g,' ').trim()).filter(t=>/^[1-5] /.test(t))")
    assert headings == ["1 Preparar y controlar ejecución", "2 Visualizar y ejecutar", "3 Relacionar con código", "4 Comprender", "5 Resultados de ejecución"]
    assert page.locator("input[type=range]").count() == 0
    assert page.locator("#hier-sim-repeat").count() == 0

    examples = page.evaluate("window.HIER_VIEW_MODEL.guided_examples")
    example = next(item for item in examples if item["id"] == EXAMPLES[family])
    page.select_option("#hier-guided-example", example["id"])
    assert page.locator("#hier-example-lesson").inner_text() == example["lesson"]
    count = len(posts)
    page.click("#hier-load-example")
    page.wait_for_function("()=>document.querySelector('#message-box').textContent.startsWith('Ejemplo preparado:')")
    assert len(posts) - count == 1 + len(example.get("seed", []))
    assert page.locator("#operation-select").input_value() == example["operation"]
    for name, value in example.get("payload", {}).items():
        assert page.locator("#h-field-" + name).input_value() == str(value)
    if not page.locator("#hier-step-toggle").is_checked():
        page.click("#hier-step-mode")
    with page.expect_response(lambda response: response.url.endswith("/hierarchical/" + family + "/operate") and response.request.method == "POST") as pending:
        page.click("#hier-sim-play")
    data = pending.value.json()
    assert data["success"]
    page.wait_for_function("()=>window.__eduTrace?.steps?.length>0")
    trace, count = data["execution_trace"], len(posts)
    trace_before = page.evaluate("JSON.stringify(window.__eduTrace)")
    page.click("#hier-sim-step")
    assert page.evaluate("window.__eduPlayer.getCursor()") == 0
    initial = education_snapshot(page)

    open_panel(page, "Predecir")
    for level in ["basic", "advanced", "intermediate"]:
        page.select_option("#hier-learning-level", level)
        assert page.locator("#hier-learning-level").input_value() == level
        assert_full_narration(page, trace["steps"][0]["pedagogy"]["narration"][level])
        assert_unchanged(page, initial, posts, count)

    first = next_decision(trace, 0)
    assert page.locator("#hier-prediction option").evaluate_all("options=>options.map(o=>o.value).filter(Boolean)") == ["true", "false"]
    page.check("#hier-practice-mode")
    assert page.locator("#visual-state").is_visible()
    assert "hier-practice-hidden" not in (page.locator("#visual-state").get_attribute("class") or "")
    assert not page.locator("#hier-practice-cover").is_visible()
    assert_unchanged(page, initial, posts, count)
    hints = []
    for number in [1, 2, 3]:
        page.click("#hier-hint")
        hint = page.locator("#hier-prediction-feedback").inner_text()
        assert hint.startswith(f"Pista {number}:")
        hints.append(hint.split(":", 1)[1].strip())
        assert_progress(page, 0, 0)
        assert_unchanged(page, initial, posts, count)
    assert len(set(hints)) == 3
    page.click("#hier-hint")
    assert page.locator("#hier-prediction-feedback").inner_text().startswith("Pista 3:")
    assert_unchanged(page, initial, posts, count)
    page.select_option("#hier-prediction", str(first[1]["condition"]["result"]).lower())
    page.click("#hier-check-prediction")
    assert page.locator("#hier-prediction-feedback").inner_text().startswith("Correcto:")
    assert_prediction_evidence(page, first)
    assert_progress(page, 1, 1)
    assert_unchanged(page, initial, posts, count)
    page.click("#hier-check-prediction")
    assert_progress(page, 1, 1)
    assert_unchanged(page, initial, posts, count)

    # Resolving releases ordinary one-instruction navigation, not a jump.
    advance_to(page, first[0], posts, count)
    page.click("#hier-sim-prev")
    assert page.evaluate("window.__eduPlayer.getCursor()") == first[0] - 1
    before = education_snapshot(page)
    page.select_option("#hier-prediction", str(first[1]["condition"]["result"]).lower())
    page.click("#hier-check-prediction")
    assert_progress(page, 1, 1)
    assert_unchanged(page, before, posts, count)
    advance_to(page, first[0], posts, count)

    second = next_decision(trace, first[0])
    page.click("#hier-hint")
    assert page.locator("#hier-prediction-feedback").inner_text().startswith("Pista 1:")
    advance_to(page, second[0] - 1, posts, count)
    before = education_snapshot(page)
    page.click("#hier-sim-step")
    assert_unchanged(page, before, posts, count)
    page.locator("#hier-sim-step").focus()
    page.keyboard.press("ArrowRight")
    assert_unchanged(page, before, posts, count)
    assert page.locator("#visual-state").is_visible()
    assert "hier-practice-hidden" not in (page.locator("#visual-state").get_attribute("class") or "")
    page.click("#hier-skip-prediction")
    assert "sin responder" in page.locator("#hier-prediction-feedback").inner_text()
    assert_prediction_evidence(page, second)
    assert_progress(page, 1, 1)
    assert_unchanged(page, before, posts, count)
    page.locator("#hier-sim-step").focus()
    page.keyboard.press("ArrowRight")
    assert page.evaluate("window.__eduPlayer.getCursor()") == second[0]
    assert len(posts) == count
    page.click("#hier-sim-prev")
    before = education_snapshot(page)
    page.select_option("#hier-prediction", str(second[1]["condition"]["result"]).lower())
    page.click("#hier-check-prediction")
    assert_progress(page, 1, 1)  # An omitted decision is not a new attempt.
    assert_unchanged(page, before, posts, count)
    page.click("#hier-reset-progress")
    assert_progress(page, 0, 0)
    assert_unchanged(page, before, posts, count)
    page.click("#hier-check-prediction")
    assert_progress(page, 0, 0)  # Resetting metrics cannot unsee a decision.
    assert_unchanged(page, before, posts, count)
    page.uncheck("#hier-practice-mode")
    for _ in range(second[0] - 1):
        page.click("#hier-sim-prev")
    assert_unchanged(page, initial, posts, count)

    open_panel(page, "Comparar")
    model_before = page.evaluate("window.HIER_VIEW_MODEL.visual_state")
    kind = "abb-heap" if family == "binary_heap" else "avl-red-black" if family in ["avl", "red_black"] else "abb-avl"
    page.select_option("#hier-compare-kind", kind)
    page.fill("#hier-compare-values", "9, 3, 7")
    with page.expect_response(lambda response: "/hierarchical/compare" in response.url and response.request.method == "POST") as pending:
        page.click("#hier-compare-run")
    comparison = pending.value.json()
    assert comparison["success"] and comparison["input"] == [9, 3, 7]
    page.wait_for_function("()=>document.querySelector('#hier-compare-position-label').textContent.startsWith('Paso 1')")
    assert page.locator("#hier-compare-grid .hier-compare-card").count() == 2
    comparison_initial = page.locator("#hier-compare-grid").inner_text()
    page.click("#hier-compare-next")
    assert page.locator("#hier-compare-grid").inner_text() != comparison_initial
    page.click("#hier-compare-prev")
    assert page.locator("#hier-compare-grid").inner_text() == comparison_initial
    assert page.evaluate("window.HIER_VIEW_MODEL.visual_state") == model_before
    assert_unchanged(page, initial, posts, count + 1)
    assert page.locator("#hier-compare-progress").get_attribute("type") == "hidden"
    assert page.locator("input[type=range]").count() == 0

    page.click("#hier-sim-step")
    step_one = education_snapshot(page)
    assert step_one["cursor"] == 1
    page.click("#hier-sim-prev")
    assert_unchanged(page, initial, posts, count + 1)
    assert page.evaluate("window.__eduRendered") == trace["steps"][0]["state_after"]
    page.click("#hier-sim-step")
    assert_unchanged(page, step_one, posts, count + 1)
    assert page.evaluate("JSON.stringify(window.__eduTrace)") == trace_before
    assert not errors
    (tmp_path / "education-restored-proof.json").write_text(json.dumps({
        "family": family, "example": example["id"], "example_public_calls": 1 + len(example.get("seed", [])),
        "levels": ["basic", "advanced", "intermediate"], "level_location": "hier-code-region",
        "prediction": "future C true/false; hints1-3; answer/omit no seek; one score; skip no attempt; reset0",
        "practice": "prior state visible; pending decision blocks button/ArrowRight; resolved decision releases manual step",
        "condition_indices": [first[0], second[0]], "comparison_kind": kind, "comparison_input": [9, 3, 7],
        "comparison_manual_cached": True, "main_next_prev_cached": True, "five_stages": headings,
        "native_disclosures_keyboard_space": True, "sliders": 0, "JS_errors": errors,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
