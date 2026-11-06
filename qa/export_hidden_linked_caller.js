/* Exercise the shipped history renderer in a DOM, not a duplicate C generator.
 * This is a jsdom unit harness. Real browser/reload coverage lives in pytest e2e.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {JSDOM} = require(process.env.JSDOM_MODULE || 'jsdom');
const [root, htmlPath] = process.argv.slice(2);
const html = fs.readFileSync(htmlPath, 'utf8');
const modelMatch = html.match(/window\.SEQ_VIEW_MODEL\s*=\s*({[\s\S]*?});<\/script>/);
assert.ok(modelMatch, 'The actual HTTP page must embed its view model');
const model = JSON.parse(modelMatch[1]);
const dom = new JSDOM(html, {runScripts: 'outside-only', url: 'http://localhost/'});
const window = dom.window;
try {
  for (const file of ['c_syntax_highlight.js', 'sequential.js']) {
    vm.runInContext(fs.readFileSync(path.join(root, 'static/js', file), 'utf8'), dom.getInternalVMContext());
  }
  const catalog = new Map(model.operations.map(operation => [operation.name, operation]));
  const history = model.history.map(step => window.createHistoryEntry(
    window.getSubroutineName(model, step.operation, step.operation), '', '',
    step.operation, step.payload));
  const container = window.document.getElementById('action-history');
  window.renderActionHistory(history, container, model.id, catalog);
  const displayed = [...container.querySelectorAll('.code-line')].map(line => line.textContent).join('\n');
  // The renderer deliberately puts a space in otherwise empty display rows.
  assert.equal(displayed, container.dataset.rawCode.split('\n').map(line => line || ' ').join('\n'));
  process.stdout.write(JSON.stringify({code: displayed, operations: model.operations}));
} finally {
  window.close();
}
