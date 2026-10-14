"""Current hierarchical cached-trace navigation, without resurrecting retired buttons."""
import re
from playwright.sync_api import expect
from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app

def test_review17_hierarchical_keyboard_and_manual_reset_use_cached_trace(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/hierarchical/abb',wait_until='networkidle')
 page.select_option('#operation-select','insertar');page.locator('[name="value"]').fill('7');page.click('#hier-step-mode')
 with page.expect_response(lambda r:r.url.endswith('/hierarchical/abb/operate') and r.request.method=='POST'):page.click('#hier-sim-play')
 expect(page.locator('#hier-sim-counter')).to_have_text(re.compile(r'Paso: 0/'))
 posts=[];page.on('request',lambda request:posts.append(request.url) if request.method=='POST' else None)
 page.locator('#hier-sim-counter').click();page.keyboard.press('End')
 final=page.locator('#hier-sim-counter').inner_text();assert not final.startswith('Paso: 0/')
 page.keyboard.press('Home');expect(page.locator('#hier-sim-counter')).to_have_text(re.compile(r'Paso: 0/'))
 page.keyboard.press('ArrowRight');expect(page.locator('#hier-sim-counter')).to_have_text(re.compile(r'Paso: 1/'))
 page.keyboard.press('Space');paused=page.locator('#hier-sim-counter').inner_text();page.wait_for_timeout(200);assert page.locator('#hier-sim-counter').inner_text()==paused
 page.click('#hier-step-mode');assert page.locator('#hier-sim-counter').inner_text()==final
 page.click('#hier-step-mode');expect(page.locator('#hier-sim-counter')).to_have_text(re.compile(r'Paso: 0/'))
 assert not posts
