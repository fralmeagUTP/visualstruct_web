/* Execute the shipped renderer. This is DOM coverage, not a browser pass. */
'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const {JSDOM} = require('jsdom');
const dom = new JSDOM('<ol id="history"></ol>', {runScripts:'outside-only'});
try {
  for (const file of ['c_syntax_highlight.js','sequential.js'])
    vm.runInContext(fs.readFileSync(`static/js/${file}`, 'utf8'), dom.getInternalVMContext());
  const window = dom.window, container = window.document.getElementById('history');
  const rows = [];
  for (const [family, operation, fn, payload] of [
    ['linked_list','insertar_inicio','lista_insertar_inicio',{value:8}],
    ['circular_list','insertar_final','lcir_insertar_final',{value:8}],
    ['sublist','insertar_padre','sublista_insertar_padre',{parent:8}],
  ]) {
    const history = [window.createHistoryEntry(fn, '', '', operation, payload)];
    const catalog = new Map([[operation,{name:operation,inputs:Object.keys(payload).map(name=>({name}))}]]);
    window.renderActionHistory(history, container, family, catalog);
    const elements = [...container.querySelectorAll('.code-line')];
    rows.push({family, raw:container.dataset.rawCode, lines:elements.map(el=>el.textContent),
               indices:elements.map(el=>Number(el.dataset.line))});
  }
  process.stdout.write(JSON.stringify(rows));
} finally { dom.window.close(); }
