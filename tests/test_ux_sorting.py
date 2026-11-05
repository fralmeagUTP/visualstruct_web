"""Presentation-only sorting UX regressions; C algorithms retain their contracts."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_single_narrative_by_drawing_and_eleven_predictions(client):
    html = client.get('/sorting/visualizador').get_data(as_text=True)
    assert html.count('id="sorting-pedagogy-narration"') == 1
    assert html.index('id="sorting-visual-region"') < html.index('id="sorting-pedagogy-narration"') < html.index('id="sorting-visual-state"')
    assert 'declarada, pero todavía sin un valor asignado' in html
    help_html = client.get('/help/sorting/sorting_array').get_data(as_text=True)
    assert help_html.count('Contrastar mi predicción') == 11
    assert help_html.count('<h4>Prueba y predice</h4>') == 11
    assert 'Preparar recorrido' in help_html


def test_narration_translates_without_mutating_source():
    script = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const context = {window: {}, document: {addEventListener() {}}};
vm.createContext(context); vm.runInContext(fs.readFileSync('static/js/sorting.js','utf8'), context);
for (const token of ['positive_null','sort_guard','valid_return','radix_entry','split_init','digit_frequency_write']) {
 const raw = token.replaceAll('_',' ');
 const frame = {phase:{id:token,goal:raw},source:{line_token:token},narration:{intermediate:raw+' Valores del modelo tras esta transición.'}};
 const before = JSON.stringify(frame), result = context.sStudentNarration(frame);
 assert(!result.includes(raw), result); assert.equal(JSON.stringify(frame),before);
}
assert.equal(context.sMemoryValue(null,{initialized:false}),'sin inicializar');
assert.equal(context.sConceptLabel('condition'),'Comprobar una condición');
assert(!context.sStudentNarration({phase:{goal:'Texto'},narration:{intermediate:'helper caller scope frame'}}).match(/helper|caller|scope|frame/));
'''
    result = subprocess.run(['node', '-e', script], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_prepared_caption_and_optional_technical_panels():
    source = (ROOT / 'static/js/sorting.js').read_text()
    assert 'stepMode ? "Preparar recorrido" : "Ejecutar operación"' in source
    assert 'cursor >= 0 && currentStep ? currentStep.pedagogy : null' in source
    assert 'classList.remove("didactic-technical")' not in source
    assert 'ContextualHelp?.frame("sorting"' not in source
    assert 'let html = "";' in source  # strategy does not duplicate trace_action


def test_real_traces_do_not_expose_raw_phase_labels():
    """Heap uses colon-prefixed conditions, unlike Radix's plain raw labels."""
    from app.adapters.sorting_adapter import SortingAdapter
    from app.services.sorting_structure_service import SortingStructureService

    frames = []
    for algorithm in SortingAdapter().get_supported_algorithms():
        result = SortingStructureService.execute_operation(
            structure_id='sorting_array', operation_name='run',
            payload={'algorithm_id': algorithm['id'], 'mode': 'step_by_step'},
            history=[{'operation': 'create_array', 'payload': {'values': [3, 1, 2]}}],
        )
        frames.extend(step['pedagogy'] for step in result['execution_trace']['steps'])
    script = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const c = {window: {}, document: {addEventListener() {}}};
vm.createContext(c); vm.runInContext(fs.readFileSync('static/js/sorting.js','utf8'), c);
const frames = JSON.parse(fs.readFileSync(0,'utf8'));
for (const frame of frames) {
 const before = JSON.stringify(frame), result = c.sStudentNarration(frame);
 assert(result.trim().length, 'Every real frame needs an explanation');
 assert(!/^(valid ptr|valid n|sort guard|swap a null|swap b null|swap guard|positive null|negative null)\b/i.test(result), result);
 assert(!result.includes('Los valores corresponden a esta transición'), result);
 assert.equal(JSON.stringify(frame), before);
}
'''
    result = subprocess.run(['node', '-e', script], cwd=ROOT, input=json.dumps(frames), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
