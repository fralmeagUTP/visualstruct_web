"""Real complete classroom downloads plus the historical raw-panel pixel oracle."""
import base64
import hashlib
import json
import os
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
from PIL import Image, ImageChops
from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app
from scripts.published_test_inputs import audit_input_path


def _image_evidence(path):
    with Image.open(path) as image:
        assert image.format == "JPEG"
        extrema = image.convert("RGB").getextrema()
        assert any(low != high for low, high in extrema), extrema
        return list(image.size)


def _assert_complete_geometry(size, width, height, live_width, bounds):
    assert size == [round(width * 2), round(height * 2)]
    assert width >= live_width and height > 19
    visible = [box for box in bounds if box["width"] > 0 and box["height"] > 0 and box["painted"]]
    assert visible, "Export must contain measured, visible content"
    for required in ("sorting-visual-state", "sorting-pedagogy-narration", "sorting-live-memory"):
        assert any(box.get("id") == required for box in visible), required
        assert any(text["owner"] == required and text["painted"] and text["fontSize"] > 0
                   and text["width"] > 0 and text["height"] > 0
                   for box in bounds for text in box["text"]), required
    assert any(text["text"] == "Identificadores simbólicos; no son direcciones reales."
               and text["painted"] and text["fontSize"] > 0 and text["width"] > 0 and text["height"] > 0
               for box in bounds for text in box["text"]), "Memory terminal must be rendered"
    assert all(box["left"] >= -1 and box["top"] >= -1 and
               box["right"] <= width + 1 and box["bottom"] <= height + 1
               for box in visible + [text for box in bounds for text in box["text"]
                                     if text["painted"] and text["width"] > 0 and text["height"] > 0]), bounds


@pytest.mark.e2e
def test_empty_and_nonempty_sorting_export(tmp_path, controls40_page):
    _, fixture_context, private_url = controls40_page
    root = Path(__file__).resolve().parents[1]
    out = Path(os.environ.get("JPEG_FOCAL_OUT", str(tmp_path)))
    out.mkdir(parents=True, exist_ok=True)
    before = audit_input_path(root / "openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-jpeg-hidden-list-traces-low/interpreter_runtime.before.js").read_text(encoding="utf-8")
    browser = fixture_context.browser
    assert browser is not None
    rows = []
    for label in ["empty-current", "nonempty-before", "nonempty-current"]:
        context = browser.new_context(viewport={"width": 1366, "height": 1000}, accept_downloads=True)
        page = context.new_page()
        errors, posts = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: posts.append(request.url) if request.method == "POST" else None)
        if label.endswith("before"):
            page.route("**/static/js/interpreter_runtime.js*", lambda route: route.fulfill(status=200, content_type="application/javascript", body=before))
        page.goto(private_url + "/sorting/visualizador", wait_until="networkidle")
        page.locator("#didactic-mode-switch").check()
        if label.startswith("nonempty"):
            page.locator("#sorting-manual-values").fill("7, 2, 9")
            page.locator("#sorting-create-array").click()
            page.wait_for_function("document.querySelector('#sorting-visual-state').textContent.includes('9')")
        page.add_script_tag(content=(Path(__file__).with_name("export_dom_probe.js")).read_text())
        n = len(posts)
        if label.endswith("current"):
            # Exercise the real UI and inspect the serialized export, not just a
            # non-white pixel. The full region includes narration and memory.
            page.evaluate("""() => {
                const original = XMLSerializer.prototype.serializeToString;
                XMLSerializer.prototype.serializeToString = function(node) {
                    const value = original.call(this, node);
                    window.__exportMarkup = value;
                    const probe = node.cloneNode(true);
                    const stage = document.createElement('div');
                    stage.style.cssText = 'position:fixed;left:-100000px;top:0;pointer-events:none';
                    stage.append(probe); document.body.append(stage);
                    try {
                        window.__exportBounds = extractExportEvidence(probe);
                    } finally { stage.remove(); }
                    return value;
                };
            }""")
            page.select_option("#export-jpg-scale", "2")
            live_width = page.locator("#sorting-visual-region").evaluate("e => e.getBoundingClientRect().width")
            with page.expect_download() as got:
                page.click("#export-visual-jpg-btn")
            complete = out / (label + "-complete.jpg")
            got.value.save_as(complete)
            size = _image_evidence(complete)
            markup = page.evaluate("window.__exportMarkup")
            xml = ET.fromstring(markup)
            nodes = {node.attrib.get("id"): node for node in xml.iter() if node.attrib.get("id")}
            assert "sorting-visual-region" in nodes
            assert "sorting-live-memory" in nodes
            assert "sorting-pedagogy-narration" in nodes
            assert "classroom-view-tools" not in markup
            text = " ".join(xml.itertext())
            assert "Identificadores simbólicos; no son direcciones reales." in text
            assert ("Arreglo vacío" in text) if label.startswith("empty") else all(str(value) in text for value in [7, 2, 9])
            dimensions = {key.strip(): value.strip() for part in xml.attrib["style"].split(";") if ":" in part for key, value in [part.split(":", 1)]}
            width = float(dimensions["width"].strip().removesuffix("px"))
            height = float(dimensions["height"].strip().removesuffix("px"))
            bounds = page.evaluate("window.__exportBounds")
            _assert_complete_geometry(size, width, height, live_width, bounds)
            rows.append({"label": label, "complete_size": size, "region_width": live_width})
            (out / (label + "-complete.xml")).write_text(markup, encoding="utf-8")
        # Equivalent historical scope: the raw visual node outside the classroom.
        # Retain the live node width and actual rendered children,
        # and inline their live styles. No complete-region guarantee is bypassed:
        # that separate UI path was tested above on the untouched classroom.
        result = page.evaluate("""async () => {
            const source = document.querySelector('#sorting-visual-state');
            const clone = source.cloneNode(true);
            const originals = [source, ...source.querySelectorAll('*')];
            const copies = [clone, ...clone.querySelectorAll('*')];
            originals.forEach((node, i) => {
                const style = getComputedStyle(node);
                for (const property of style) copies[i].style.setProperty(property, style.getPropertyValue(property));
            });
            clone.style.width = `${source.getBoundingClientRect().width}px`;
            clone.style.height = 'auto';
            clone.style.maxHeight = 'none';
            clone.style.overflow = 'visible';
            clone.style.zoom = '1';
            clone.style.position = 'static';
            source.id = 'live-sorting-state';
            document.body.append(clone);
            try {
                const liveWidth = source.getBoundingClientRect().width;
                const box = clone.getBoundingClientRect();
                const evidence = extractExportEvidence(clone);
                const exported = await InterpreterRuntime.exportVisualStateAsJpg({target: clone, scale: 2, quality: .92});
                return {...exported, independent: {liveWidth, width: box.width, height: box.height, evidence}};
            } finally { clone.remove(); source.id = 'sorting-visual-state'; }
        }""")
        raw = out / (label + ".jpg")
        raw.write_bytes(base64.b64decode(result["dataUrl"].split(",", 1)[1]))
        raw_size = _image_evidence(raw)
        measured = result["independent"]
        assert abs(measured["width"] - measured["liveWidth"]) <= 1
        assert raw_size == [math.floor(measured["width"] + .5) * 2,
                            math.floor(measured["height"] + .5) * 2]
        if label.startswith("empty"):
            paragraphs = [text for box in measured["evidence"] for text in box["text"]
                          if "Arreglo vacío" in text["text"]]
            assert paragraphs and all(text["painted"] and text["fontSize"] > 0
                                      and text["width"] > 0 and text["height"] > 0 for text in paragraphs)
            assert all(text["left"] >= -1 and text["top"] >= -1 and
                       text["right"] <= measured["width"] + 1 and
                       text["bottom"] <= measured["height"] + 1 for text in paragraphs)
            assert raw_size[1] >= max(text["height"] for text in paragraphs) * 2
            # The serializer hook also measures the actual empty export clone,
            # catching margin-induced clipping after the independent source anchor.
            exported_bounds = page.evaluate("window.__exportBounds")
            exported_paragraphs = [text for box in exported_bounds for text in box["text"]
                                   if "Arreglo vacío" in text["text"]]
            assert exported_paragraphs
            assert all(text["painted"] and text["fontSize"] > 0 and text["width"] > 0
                       and text["height"] > 0 and text["left"] >= -1 and text["top"] >= -1
                       and text["right"] <= raw_size[0] / 2 + 1
                       and text["bottom"] <= raw_size[1] / 2 + 1 for text in exported_paragraphs)
        assert len(posts) == n and not errors
        rows.append({"label": label, "raw_size": raw_size, "export_POSTs": len(posts) - n, "errors": errors})
        context.close()
    with Image.open(out / "nonempty-before.jpg") as old, Image.open(out / "nonempty-current.jpg") as current:
        assert old.size == current.size
        assert ImageChops.difference(old.convert("RGB"), current.convert("RGB")).getbbox() is None
    (out / "JPEG-regression-report.json").write_text(json.dumps({"rows": rows, "nonempty_pixels_identical": True, "current_runtime_sha256": hashlib.sha256(audit_input_path(root / "static/js/interpreter_runtime.js").read_bytes()).hexdigest()}, indent=2), encoding="utf-8")
