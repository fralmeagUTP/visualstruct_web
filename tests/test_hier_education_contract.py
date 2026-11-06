"""Current educational decisions: real handlers/renderer and corruption negatives.

Node/JSDOM assertions do not claim browser rendering, viewport or screenshot PASS.
"""
from pathlib import Path
import json,shutil,subprocess
import pytest
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService as H

ROOT=Path(__file__).resolve().parents[1]

def test_historical_79_decisions_and_actual_handlers():
 run=subprocess.run(['node','qa/test_hier_prediction.js'],cwd=ROOT,capture_output=True,text=True,timeout=30)
 assert run.returncode==0,run.stdout+run.stderr
 assert 'PASS 79 real decisions' in run.stdout

@pytest.mark.parametrize('damage',[
 'two-hints','answer-seek','skip-seek','duplicate-score','permanent-practice-gate','keyboard-bypass','forged-evidence',
])
def test_prediction_oracle_rejects_contract_regressions(tmp_path,damage):
 source=(ROOT/'static/js/hierarchical.js').read_text()
 replacements={
  'two-hints':('hintLevel = Math.min(3, hintLevel + 1);','hintLevel = Math.min(2, hintLevel + 1);'),
  'answer-seek':('if (result.counted) { conceptualProgress.attempts','tracePlayer.seek(result.index); if (result.counted) { conceptualProgress.attempts'),
  'skip-seek':('const result = predictionController.skip(); if (!result) return;','const result = predictionController.skip(); if (!result) return; tracePlayer.seek(result.index);'),
  'duplicate-score':('if (result.counted) { conceptualProgress.attempts','if (true) { conceptualProgress.attempts'),
  'permanent-practice-gate':(' && !pendingDecision.scored',''),
  'keyboard-bypass':('await stepHierManually(false);','await tracePlayer.step();'),
  'forged-evidence':('evidence: `${target.substituted || target.source}','evidence: `FORGED'),
 }
 before,after=replacements[damage];assert before in source;source=source.replace(before,after)
 (tmp_path/'static/js').mkdir(parents=True);(tmp_path/'static/js/hierarchical.js').write_text(source)
 (tmp_path/'qa').mkdir()
 for name in ['test_hier_prediction.js','hier_prediction_harness.js','hier_prediction_fixtures.json']:shutil.copy2(ROOT/'qa'/name,tmp_path/'qa'/name)
 run=subprocess.run(['node','qa/test_hier_prediction.js'],cwd=tmp_path,capture_output=True,text=True,timeout=30)
 assert run.returncode!=0,damage+' was accepted'
 assert 'AssertionError' in run.stderr or 'Prediction must not seek' in run.stderr,run.stderr

@pytest.mark.parametrize('family',['abb','avl','red_black','binary_heap'])
def test_real_page_level_control_identity_and_narration(tmp_path,family):
 app=create_app()
 with app.test_client() as client:
  response=client.get('/hierarchical/'+family);assert response.status_code==200
 data=H.execute_operation(family,'insertar',{'value':7},[]);assert data['success']
 frame=data['execution_trace']['steps'][0]['pedagogy'];path=tmp_path/'page.json'
 path.write_text(json.dumps({'family':family,'html':response.get_data(as_text=True),'frame':frame}))
 run=subprocess.run(['node','qa/check_hier_education_dom.js',str(path)],cwd=ROOT,capture_output=True,text=True,timeout=30)
 assert run.returncode==0,run.stdout+run.stderr
 result=json.loads(run.stdout);assert result['levels']==3 and result['singleControl'] and result['identity']
