"""Focal actual export regression; explicit live preview required, private cookies."""
import hashlib,json,os
from pathlib import Path
import pytest
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright

@pytest.mark.skipif(not os.environ.get("JPEG_FOCAL_URL"),reason="requires explicit owned preview URL")
def test_empty_and_nonempty_sorting_export(tmp_path):
    root=Path(__file__).resolve().parents[1]
    out=Path(os.environ.get("JPEG_FOCAL_OUT",str(tmp_path)));out.mkdir(parents=True,exist_ok=True)
    before=(root/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-jpeg-hidden-list-traces-low/interpreter_runtime.before.js").read_text(encoding="utf-8")
    rows=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        for label in ["empty-current","nonempty-before","nonempty-current"]:
            context=browser.new_context(viewport={"width":1366,"height":1000},accept_downloads=True)
            page=context.new_page();errors=[];posts=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.on("request",lambda r:posts.append(r.url) if r.method=="POST" else None)
            if label.endswith("before"):
                page.route("**/static/js/interpreter_runtime.js*",lambda r:r.fulfill(status=200,content_type="application/javascript",body=before))
            page.goto(os.environ["JPEG_FOCAL_URL"]+"/sorting/visualizador",wait_until="networkidle")
            page.locator("#didactic-mode-switch").check()
            if label.startswith("nonempty"):
                page.locator("#sorting-manual-values").fill("7, 2, 9")
                page.locator("#sorting-create-array").click()
                page.wait_for_function("document.querySelector('#sorting-visual-state').textContent.includes('9')")
            page.select_option("#export-jpg-scale","2")
            geometry=page.locator("#sorting-visual-state").evaluate("e=>({text:e.textContent,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})")
            n=len(posts)
            with page.expect_download() as got:page.click("#export-visual-jpg-btn")
            dest=out/(label+".jpg");got.value.save_as(dest)
            with Image.open(dest) as im:
                extrema=im.convert("RGB").getextrema();size=list(im.size)
            assert any(a!=b for a,b in extrema),(label,extrema)
            assert len(posts)==n and not errors
            if label.startswith("empty"):
                assert size==[996,38] and "Arreglo vacio" in geometry["text"]
            rows.append({"label":label,"size":size,"RGB_extrema":extrema,"DOM":geometry,"POSTs":posts,"export_POSTs":len(posts)-n,"errors":errors})
            context.close()
        browser.close()
    with Image.open(out/"nonempty-before.jpg") as a,Image.open(out/"nonempty-current.jpg") as b:
        assert a.size==b.size and ImageChops.difference(a.convert("RGB"),b.convert("RGB")).getbbox() is None
    (out/"JPEG-regression-report.json").write_text(json.dumps({"rows":rows,"nonempty_pixels_identical":True,"current_runtime_sha256":hashlib.sha256((root/"static/js/interpreter_runtime.js").read_bytes()).hexdigest()},indent=2),encoding="utf-8")
