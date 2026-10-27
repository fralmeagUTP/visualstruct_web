/* One presentation-only C reader for initial and dynamically replaced source.
 * Never parse source as HTML; retain source rows, navigation classes and rawCode.
 */
(function (scope) {
  "use strict";
  const selector = "pre.didactic-code, pre.didactic-history-main, code";
  const keywords = new Set("if else for while do switch case default break continue return sizeof typedef struct enum union static const volatile extern goto NULL true false restrict inline _Atomic _Static_assert".split(" "));
  const types = new Set("void int bool float double char short long signed unsigned size_t ptrdiff_t FILE Grafo GrafoEstado ListaVertice ListaArco NodoV NodoA Pila Cola Lista Arbol AVL TablaHash OrdenamientoEstado".split(" "));
  const remembered = new WeakMap();

  function tokenize(source, previous = {}) {
    const tokens = [], text = String(source), state = {inBlockComment: Boolean(previous.inBlockComment)};
    const emit = (text, kind = "") => { if (text) tokens.push({text, kind}); };
    let i = 0;
    while (i < text.length) {
      if (state.inBlockComment) {
        const end = text.indexOf("*/", i), stop = end < 0 ? text.length : end + 2;
        emit(text.slice(i, stop), "comment"); i = stop; state.inBlockComment = end < 0; continue;
      }
      const rest = text.slice(i), ch = text[i];
      if (rest.startsWith("/*")) { state.inBlockComment = true; continue; }
      if (rest.startsWith("//")) { const end = rest.search(/[\r\n]/), stop = end < 0 ? text.length : i + end; emit(text.slice(i, stop), "comment"); i = stop; continue; }
      if (ch === "#" && /^\s*$/.test(text.slice(text.lastIndexOf("\n", i - 1) + 1, i))) {
        const end = rest.search(/[\r\n]/), stop = end < 0 ? text.length : i + end;
        emit(text.slice(i, stop), "directive"); i = stop; continue;
      }
      if (ch === '"' || ch === "'") {
        let end = i + 1;
        while (end < text.length) { if (text[end] === "\\") { end += 2; continue; } if (text[end++] === ch) break; }
        emit(text.slice(i, end), "string"); i = end; continue;
      }
      const number = rest.match(/^(?:0[xX][\da-fA-F]+(?:\.[\da-fA-F]*)?(?:[pP][+-]?\d+)?|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)[uUlLfF]*/);
      if (number) { emit(number[0], "number"); i += number[0].length; continue; }
      const identifier = rest.match(/^[A-Za-z_]\w*/);
      if (identifier) {
        const word = identifier[0], next = text.slice(i + word.length).trimStart()[0];
        const kind = types.has(word) ? "type" : keywords.has(word) ? "keyword" : next === "(" ? "function" : "identifier";
        emit(word, kind); i += word.length; continue;
      }
      emit(ch, "{}[]();,.".includes(ch) ? "punct" : "+-*/%=!<>&|^~?:".includes(ch) ? "operator" : ""); i++;
    }
    return {tokens, state};
  }

  function readerFor(node) {
    const element = node?.nodeType === 1 ? node : node?.parentElement;
    const reader = element?.closest?.(selector);
    if (!reader || reader.closest(".console-screen, .console-line, [data-no-syntax]")) return null;
    // A PRE owns its rows/embedded CODE; never highlight the same source twice.
    return reader.closest("pre.didactic-code, pre.didactic-history-main") || reader;
  }

  function snapshot(units) { return units.map(node => ({node, first: node.firstChild, text: node.textContent})); }
  function unchanged(old, current) {
    return old?.length === current.length && current.every((row, i) => old[i].node === row.node && old[i].first === row.first && old[i].text === row.text);
  }
  function highlightBlock(block) {
    if (!block?.isConnected) return;
    const lines = Array.from(block.querySelectorAll(".code-line"));
    const units = lines.length ? lines : [block.children.length === 1 && block.firstElementChild.tagName === "CODE" ? block.firstElementChild : block];
    const before = snapshot(units);
    if (unchanged(remembered.get(block), before)) return;
    const x = block.scrollLeft, y = block.scrollTop;
    let state = {inBlockComment: false};
    before.forEach(({node, text}) => {
      const result = tokenize(text, state); state = result.state;
      const fragment = document.createDocumentFragment();
      for (const token of result.tokens) {
        if (!token.kind) fragment.append(document.createTextNode(token.text));
        else { const span = document.createElement("span"); span.className = "code-" + token.kind; span.textContent = token.text; fragment.append(span); }
      }
      node.replaceChildren(fragment);
    });
    block.dataset.cSyntax = "c";
    block.scrollLeft = x; block.scrollTop = y;
    remembered.set(block, snapshot(units));
  }

  function collect(root, pending) {
    const own = readerFor(root); if (own) pending.add(own);
    root?.querySelectorAll?.(selector).forEach(node => { const block = readerFor(node); if (block) pending.add(block); });
  }
  function start() {
    const initial = new Set(); collect(document, initial); initial.forEach(highlightBlock);
    new MutationObserver(records => {
      const pending = new Set();
      for (const record of records) {
        const block = readerFor(record.target); if (block) pending.add(block);
        record.addedNodes.forEach(node => { if (node.nodeType === 1) collect(node, pending); });
      }
      pending.forEach(highlightBlock);
    }).observe(document.body, {childList: true, characterData: true, subtree: true});
  }
  scope.CSyntax = {tokenize, highlightBlock};
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true});
  else start();
}(window));
