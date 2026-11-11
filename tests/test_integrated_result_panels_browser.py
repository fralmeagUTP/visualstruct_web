"""Presentation-only browser tests using production CSS/controller and long results.

This fixture does not replace live endpoint/algorithm end-to-end coverage.
"""
import os
import runpy
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('width', [1440, 800, 390])
def test_integrated_results_wrap_without_nested_scroll_and_preserve_practice(width, tmp_path):
    runpy.run_path(str(ROOT / 'qa_results/panel_layout_fixture.py'))
    html = Path('/tmp/visualstruct-panel-fixture.html').read_text()
    with pytest.importorskip('playwright.sync_api').sync_playwright() as pw:
        launch = {'executable_path': os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE']} if os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') else {}
        browser = pw.chromium.launch(**launch)
        page = browser.new_page(viewport={'width': width, 'height': 950})
        page.set_content(html, wait_until='load')
        result = page.locator('.classroom-inline-results')
        result.wait_for(state='visible')
        assert '30' in result.inner_text()
        assert page.locator('#stage .hier-current-result').count() == 0
        assert result.evaluate('(e)=>e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1')
        assert result.evaluate('(e)=>getComputedStyle(e).overflowY') == 'visible'
        console = page.locator('#console')
        assert 'Salida 34:' in console.inner_text()
        assert console.evaluate('(e)=>e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1')
        assert console.evaluate('(e)=>getComputedStyle(e).overflowY') == 'visible'
        assert page.locator('#code').evaluate('(e)=>getComputedStyle(e).overflowY') == 'auto'
        page.locator('#practice').click()
        assert not result.is_visible()
        page.locator('#practice').click()
        assert result.is_visible()
        page.get_by_role('button', name='+', exact=True).click()
        page.locator('#redraw').click()
        assert page.locator('.classroom-inline-results .hier-current-result').count() == 1
        assert '30' in result.inner_text()
        page.screenshot(path=str(tmp_path / f'results-{width}.png'), full_page=True)
        browser.close()
