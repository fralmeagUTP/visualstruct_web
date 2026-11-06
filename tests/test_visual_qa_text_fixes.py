"""Focused presentation regressions found in cloud visual QA."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from app.domain.graph.book_trace import _text


@pytest.mark.parametrize('description, expected', [
    ('grafo_bfs: GRAFO_OK.', 'grafo_bfs: GRAFO_OK.'),
    ('grafo_bfs: GRAFO_OK', 'grafo_bfs: GRAFO_OK.'),
    ('grafo_bfs: GRAFO_OK.  ', 'grafo_bfs: GRAFO_OK.'),
    (None, 'application_boundary.'),
])
def test_graph_boundary_has_single_terminal_period_without_mutation(description, expected):
    event = {'phase': 'application_boundary', 'description': description, 'C_executed': False}
    memory = {'external': {}}
    original = deepcopy((event, memory))
    assert _text(event, memory) == f'Frontera de la aplicación: {expected} No es una instrucción del TAD.'
    assert (event, memory) == original


def test_sorting_student_narration_translates_caller_grammar_without_mutation():
    source = Path(__file__).resolve().parents[1] / 'static/js/sorting.js'
    # Load the real presentation function, stopping before browser initialization.
    script = r'''
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[1], 'utf8');
const context = {};
vm.createContext(context);
vm.runInContext(source.slice(0, source.indexOf('function sPushUniqueConsoleLine')), context);
for (const [input, expected] of [
  ['Retorno void al caller; retirar locales, sin printf propio del TAD.',
   'Retorno void a la función que llamó; retirar locales, sin printf propio del TAD.'],
  ['Retorno void al caller; el TAD no ejecuta printf.',
   'Retorno void a la función que llamó; el TAD no ejecuta printf.'],
  ['Retornar ORDENAMIENTO_OK; retirar locales del wrapper y confirmar el resultado final.',
   'Retornar ORDENAMIENTO_OK; retirar locales de la función principal y confirmar el resultado final.'],
  ['Retornar ORDENAMIENTO_OK (1) y retirar parámetros/locales del wrapper.',
   'Retornar ORDENAMIENTO_OK (1) y retirar parámetros/locales de la función principal.'],
  ['Retirar scope del helper; caller recursivo suspendido.',
   'Retirar ámbito de la variable de la función auxiliar; función que llamó recursiva suspendida.'],
  ['Contexto: caller.', 'Contexto: función que llamó.'],
  ['Un caller_index no es caller.', 'Un caller_index no es función que llamó.'],
  ['Solo se evalúa la condición.', 'Solo se evalúa la condición.'],
]) {
  const frame = {source: {line_token: 'sort_return'}, phase: {goal: 'return'}, narration: {intermediate: input}};
  const original = JSON.stringify(frame);
  assert.equal(context.sStudentNarration(frame), expected);
  assert.equal(JSON.stringify(frame), original);
}
for (const [role, label] of Object.entries({caller: 'función que llamó', wrapper: 'función principal', helper: 'función auxiliar'})) {
  for (const [article, prefix] of Object.entries({al: 'a la', del: 'de la', el: 'la', un: 'una'})) {
    for (const [suffix, translatedSuffix] of [['', ''], [' recursivo', ' recursiva'], [' suspendido', ' suspendida'], [' recursivo suspendido', ' recursiva suspendida']]) {
      const narration = `${article} ${role}${suffix}`;
      const expected = `${prefix} ${label}${translatedSuffix}`;
      const frame = {phase: {goal: 'narration'}, narration: {intermediate: narration}};
      assert.equal(context.sStudentNarration(frame), expected);
      frame.narration.intermediate = narration[0].toUpperCase() + narration.slice(1);
      assert.equal(context.sStudentNarration(frame), expected[0].toUpperCase() + expected.slice(1));
    }
  }
}
for (const token of ['caller_index', 'wrapper_active', 'helper_n']) {
  assert.equal(context.sStudentNarration({phase: {goal: 'narration'}, narration: {intermediate: token}}), token);
}
'''
    subprocess.run(['node', '-e', script, str(source)], check=True, capture_output=True, text=True)
