/* Finite DOM-observer contracts; no browser, server, or simulated E2E pass. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

test('approved console exposes exact raw bytes and a separate empty placeholder', () => {
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('static/js/console-history.js', 'utf8'), context);
  const el = {dataset: {}, style: {}, textContent: '', scrollTop: 0, scrollLeft: 0, scrollHeight: 0, clientHeight: 0};
  for (const stdout of ['', '7 7\n', '\n\n', ' áéñ \n áéñ \n']) {
    context.window.ConsoleHistory.publish(el, stdout);
    assert.equal(el.dataset.consoleCopy, stdout);
    assert.equal(el.textContent, stdout || '(sin salida printf en esta ruta)');
  }
});

test('renderer colors accented and unaccented C titles immediately without altering source', () => {
  const context = {window: {}, document: {readyState: 'loading', addEventListener() {}}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('static/js/interpreter_runtime.js', 'utf8'), context);
  const source = 'int value = 7;\nreturn value;\n';
  for (const title of ['Código C: título con acento', 'Codigo C']) {
    const el = {dataset: {}, innerHTML: '', querySelectorAll() { return []; }, scrollTop: 0};
    context.window.InterpreterRuntime.renderCode(el, source, title);
    assert.match(el.innerHTML, /class="code-(?:type|keyword)"/);
    assert.equal(el.dataset.rawCode, source);
  }
});

test('shipped sequential collectors retain repeated and blank output at each cursor', () => {
  const source=fs.readFileSync('static/js/sequential.js','utf8');
  const start=source.indexOf('  function collectPrintfConsoleLines(');
  const end=source.indexOf('  function refreshPrintfConsole(',start);
  assert.ok(start>0 && end>start);
  const context={};vm.createContext(context);vm.runInContext(source.slice(start,end),context);
  const trace={console_mode:'events',steps:[{console:[' same \n']},{console:[' same \n','']},{console:['last']}]};
  const expected=['',' same \n',' same \n\n same \n\n',' same \n\n same \n\n\nlast'];
  for(let cursor=-1;cursor<3;cursor++)
    assert.equal(context.collectPrintfConsoleLines(trace,cursor).join('\n'),expected[cursor+1]);
  trace.console_mode='snapshot';
  assert.equal(context.collectPrintfConsoleLines(trace,1).join('\n'),' same \n\n');
  trace.steps[1].console_stdout=' 7\n7\n';
  assert.equal(context.collectPrintfStdout(trace,1),' 7\n7\n');
});
