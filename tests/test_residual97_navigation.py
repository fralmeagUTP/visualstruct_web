"""Concrete current navigation and local C-download behavior for pending anchors."""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json
import pytest
from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app
R=Path(__file__).resolve().parents[1]
CASES=json.loads((Path(__file__).parent/'fixtures/residual97-navigation-v1.json').read_text(encoding='utf-8'))['cases']

def reveal_with_public_control(page,loc)->None:
 for _ in range(4):
  if loc.is_visible():return
  info=loc.evaluate("e=>{let p=e.parentElement;while(p){if(p.tagName==='DETAILS'&&!p.open)return {type:'details',id:p.id};if(p.hidden&&p.id)return {type:'hidden',id:p.id};p=p.parentElement;}return null;}")
  if not info:break
  if info['type']=='hidden':
   button=page.locator(f'button[aria-controls="{info["id"]}"]')
   if button.count()==1 and button.is_visible():button.click();continue
  else:
   # Open the closest closed disclosure via its real summary.
   summary=loc.locator('xpath=ancestor::details[not(@open)][1]/summary')
   if summary.is_visible():summary.click();continue
  break
 assert loc.is_visible(),'No reachable current public flow for this source anchor'

@pytest.mark.e2e
@pytest.mark.parametrize('row',CASES,ids=lambda row:row['family']+'::'+row['id'])
def test_residual97_actual_anchor_navigation_or_download(controls40_page,tmp_path:Path,row:dict)->None:
 page,context,base=controls40_page;page.goto(base+row['page'],wait_until='networkidle');loc=page.locator(row['selector']).nth(row['occurrence']);assert loc.count()==1,'Source anchor no longer rendered in current contract'
 reveal_with_public_control(page,loc)
 if row['download']:
  with page.expect_download() as download:loc.click()
  target=tmp_path/download.value.suggested_filename;download.value.save_as(target);content=target.read_bytes()
  if row['canonical_file']:assert hashlib.sha256(content).hexdigest()==row['expected_download_sha256']==hashlib.sha256((R/row['canonical_file']).read_bytes()).hexdigest()
  else:
   source=content.decode('utf-8-sig')
   for token in row['expected_main_tokens']:assert token in source
 else:
  loc.click();page.wait_for_url(base+row['expected_final_path'],wait_until='networkidle')
  assert urlsplit(page.url).path==row['expected_final_path']
  assert page.locator('main h2').first.inner_text().strip()==row['expected_heading']

from test_residual58_focal_cases import residual58_client,post_operation

def test_residual97_sorting_alias_serves_equivalent_workspace(residual58_client)->None:
 response=residual58_client.post('/api/ordenamiento/create-array',json={'values':[3,1]});assert response.status_code==200
 alias=residual58_client.get('/sorting/sorting_array');canonical=residual58_client.get('/sorting/visualizador')
 assert alias.status_code==200 and alias.data==canonical.data
 assert b'sorting-visual-state' in alias.data and b'3' in alias.data

def test_residual97_hierarchical_reset_removes_owned_tree(residual58_client)->None:
 for value in [7,3,9]:post_operation(residual58_client,'hierarchical','abb','insertar',{'value':value})
 reset=residual58_client.post('/hierarchical/abb/reset');assert reset.status_code==200
 assert post_operation(residual58_client,'hierarchical','abb','inorden')['result']==[]
 assert post_operation(residual58_client,'hierarchical','abb','altura')['result']==0


@pytest.mark.e2e
def test_review122_graph_main_download_keyboard_with_mouse_gap(controls40_page,tmp_path:Path)->None:
 page,context,base=controls40_page;page.goto(base+'/graph/graph',wait_until='networkidle')
 loc=page.locator('main a[href="/help/source/graph/main"].link')
 reveal_with_public_control(page,loc)
 # A real focus/Enter flow; the separate mouse-click regression remains failed.
 loc.focus();assert loc.evaluate('(e)=>document.activeElement===e')
 with page.expect_download() as downloaded:loc.press('Enter')
 target=tmp_path/'graph-main.c';downloaded.value.save_as(target);text=target.read_text(encoding='utf-8-sig')
 assert 'int main(' in text and 'free(g.a)' in text and 'free(g.v)' in text
