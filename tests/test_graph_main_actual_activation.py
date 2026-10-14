"""MainGraph downloads remain reachable with actual pointer and keyboard actions."""
from pathlib import Path
import pytest
from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app

@pytest.mark.parametrize('activation',['click','keyboard'])
def test_graph_main_actual_activation(controls40_page,tmp_path:Path,activation:str)->None:
 page,context,base=controls40_page;page.goto(base+'/graph/graph',wait_until='networkidle');loc=page.locator('main a[href="/help/source/graph/main"].link')
 from test_residual97_navigation import reveal_with_public_control
 reveal_with_public_control(page,loc)
 assert loc.is_visible()
 with page.expect_download() as got:
  if activation=='click':loc.click()
  else:loc.focus();assert loc.evaluate('(e)=>document.activeElement===e');loc.press('Enter')
 path=tmp_path/'main.c';got.value.save_as(path);source=path.read_text(encoding='utf-8-sig');assert 'int main(' in source and 'free(g.a)' in source and 'free(g.v)' in source
