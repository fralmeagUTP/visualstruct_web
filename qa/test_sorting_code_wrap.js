'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('static/css/contextual_help.css','utf8');
const rule=css.match(/\.sorting-workspace #sorting-code,\s*\.sorting-workspace #sorting-code \.code-line\s*\{([^}]+)\}/);
assert.ok(rule,'wrapper and actual highlighted code lines must both wrap');
assert.match(rule[1],/white-space:\s*pre-wrap/);assert.match(rule[1],/overflow-wrap:\s*anywhere/);assert.match(rule[1],/word-break:\s*normal/);
assert.doesNotMatch(rule[1],/font-size|height|display:\s*none/);
assert.match(css,/height:\s*clamp\(420px, 62vh, 570px\)/,'fixed workspace height retained');
console.log('PASS scoped C soft wrap, unmodified font/height, fixed classroom workspace');
