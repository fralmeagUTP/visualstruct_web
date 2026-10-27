"use strict";

// Control temporal de UI: mantener oculta la linea de tiempo RN.
const H_SHOW_RN_TIMELINE = false;

function hById(id) {
  return document.getElementById(id);
}

function createHierPredictionController(getTrace, getCursor) {
  let trace = null, target = null, hintLevel = 0;
  const scored = new Set();
  function sync() {
    const nextTrace = getTrace();
    if (nextTrace !== trace) { trace = nextTrace; scored.clear(); target = null; hintLevel = 0; }
    for (let index = 0; index <= getCursor(); index += 1) {
      const frame = trace?.steps?.[index]?.pedagogy;
      if (frame && ["compare", "condition", "comparison"].includes(frame.concept) && typeof frame.condition?.result === "boolean") scored.add(index);
    }
    let next = null;
    for (let index = getCursor() + 1; index < (trace?.steps?.length || 0); index += 1) {
      const frame = trace.steps[index]?.pedagogy;
      // Only this frame's evaluated C condition is evidence. A branch/case
      // carried over on assignment frames does not create another decision.
      if (frame && ["compare", "condition", "comparison"].includes(frame.concept) && typeof frame.condition?.result === "boolean") {
        next = { index, source: String(frame.condition.source || frame.source?.line_text || "condición C"), answer: String(frame.condition.result) };
        break;
      }
    }
    if (target?.index !== next?.index) hintLevel = 0;
    target = next;
    return target ? { index: target.index, prompt: `Predecir próxima condición C (paso ${target.index + 1}): ¿es verdadera o falsa? ${target.source}`, options: [{value:"true",label:"Verdadero"},{value:"false",label:"Falso"}], scored: scored.has(target.index) } : null;
  }
  function answer(choice) {
    sync();
    if (!target || !["true","false"].includes(choice)) return null;
    const counted = !scored.has(target.index); scored.add(target.index);
    return { index: target.index, correct: choice === target.answer, counted, label: target.answer === "true" ? "Verdadero" : "Falso" };
  }
  function skip() { sync(); if (!target) return null; scored.add(target.index); return {index:target.index}; }
  function hint() {
    sync(); if (!target) return "No quedan decisiones con condición C registrada.";
    hintLevel = Math.min(2, hintLevel + 1);
    return hintLevel === 1 ? "Pista 1: identifica los operandos de la condición; consulta el estado previo, no el resultado futuro." : "Pista 2: evalúa los operadores y respeta el cortocircuito de && y ||; una comparación con NULL comprueba un puntero, no el contenido del nodo.";
  }
  return { sync, answer, skip, hint };
}

function renderHierComparisonShape(state, structure) {
  const root = structure === "binary_heap" ? heapArrayToTreeNode(state.array || []) : state.root;
  const levels = node => node ? 1 + Math.max(levels(node.left), levels(node.right)) : 0;
  const name = state.title || ({abb:"Árbol binario de búsqueda",avl:"Árbol AVL",red_black:"Árbol rojo-negro",binary_heap:"Montículo binario"})[structure] || "Estructura";
  const svg = drawTreeSvgFromNodes(flattenTree(root), {showBalanceFactor:structure === "avl",showNullLeaves:structure === "red_black"});
  return { name, height:levels(root), html:`<div class="hier-comparison-shape" role="img" aria-label="Forma de ${hEscape(name)}" data-comparison-root="${hEscape(root?.value ?? "NULL")}">${svg}</div>` };
}
function renderHierComparisonState(side, step) {
  const state = step?.state || side?.final_state || {};
  const shape = renderHierComparisonShape(state, side?.structure);
  const isHeap = side?.structure === "binary_heap", traversal = state.traversals?.inorden || [], array = state.array || [];
  const valid = step?.validation ?? side?.validation;
  return `<article class="hier-compare-card"><h4>${hEscape(shape.name)}</h4><p><strong>Paso:</strong> ${hEscape(step?.step ?? "final")} · insertado ${hEscape(step?.inserted ?? "—")}</p><p><strong>Altura (niveles):</strong> ${shape.height} · <strong>Tamaño:</strong> ${hEscape(state.size ?? side?.size ?? "—")}</p>${shape.html}<p><strong>${isHeap ? "Arreglo del heap (no orden total)" : "Orden de visita inorden"}:</strong> <code>${hEscape((isHeap ? array : traversal).join(" → ") || "vacío")}</code></p><p><strong>Invariante:</strong> ${valid === true ? "✓ válido" : valid === false ? "✗ inválido" : "sin verificación registrada"}</p></article>`;
}

function initHierResponsiveWorkspace() {
  const workspace = document.querySelector(".hier-primary-workspace");
  const tabs = Array.from(document.querySelectorAll("[data-hier-tab]"));
  if (!workspace || !tabs.length) return;
  let saved = "visual"; try { saved = sessionStorage.getItem("hier-active-tab") || "visual"; } catch (_error) { saved = "visual"; }
  const activate = (name) => { const value = name === "code" ? "code" : "visual"; workspace.dataset.activeTab = value; tabs.forEach((tab) => { const active = tab.dataset.hierTab === value; tab.classList.toggle("is-active", active); tab.setAttribute("aria-selected", String(active)); }); try { sessionStorage.setItem("hier-active-tab", value); } catch (_error) { /* optional */ } };
  tabs.forEach((tab) => tab.addEventListener("click", () => activate(tab.dataset.hierTab))); activate(saved);
}

function enhanceHierCodeNavigation(activeLine = null) {
  const code = hById("op-pseudocode"); const list = hById("hier-function-list"); const hide = hById("hier-hide-comments");
  if (!code || !list) return;
  const raw = String(code.dataset.rawCode || code.textContent || ""); const rows = raw.replaceAll("\r\n", "\n").split("\n"); const functions = [];
  const signature = /^\s*(?:static\s+)?(?:void|bool|char|int|size_t|AVL|RBT|ABBNodo|MonticuloBinario)\b(?:\s*\*+\s*|\s+)([A-Za-z_]\w*)\s*\(/;
  const comments = window.CCodeNavigation?.commentOnlyLines(raw) || [];
  rows.forEach((row,index) => {
    if (comments[index] || /^\s*(?:return|goto)\b/.test(row)) return;
    const match = row.match(signature);
    if (match && rows.slice(index).join("\n").match(/[;{}]/)?.[0] === "{" && !functions.some(item => item.name === match[1])) functions.push({name:match[1],line:index});
  });
  window.CCodeNavigation?.markComments(code, rows); code.classList.toggle("hide-hier-comments",Boolean(hide?.checked));
  const active=[...functions].reverse().find((item)=>Number.isInteger(activeLine)&&item.line<=activeLine)||functions[0]; list.innerHTML=functions.length?functions.map((item)=>`<li><button type="button" class="${active?.line===item.line?'is-active':''}" data-line="${item.line}">${hEscape(item.name)}</button></li>`).join(""):'<li>Sin funciones detectadas</li>'; list.querySelectorAll("button").forEach((button)=>button.addEventListener("click",()=>window.CCodeNavigation?.revealLine(code,code.querySelector(`.code-line[data-line="${button.dataset.line}"]`))));
}

function renderHierPedagogy(frame, level) {
  if (!frame) return;
  const summary=hById("hier-pedagogy-summary"), path=hById("hier-path-view"), stack=hById("hier-stack-view"), invariant=hById("hier-invariant-view"), variables=hById("hier-variables-view"), memory=hById("hier-memory-view"), relations=hById("hier-relations-view");
  if(summary)summary.innerHTML=`<strong>${hEscape(frame.phase?.label||frame.concept)}</strong>: ${hEscape(frame.narration?.[level]||frame.narration?.intermediate||"")}`;
  window.ContextualHelp?.frame("hier", frame, level);
  const condition=frame.condition; if(path)path.innerHTML=`Ruta: <code>${hEscape((frame.path?.keys||[]).join(" → ")||"—")}</code><br>Acción: <strong>${hEscape(window.ContextualHelp?.phaseLabel(frame)||frame.phase?.label||"—")}</strong>${condition?`<br><code>${hEscape(condition.substituted)}</code> ⇒ <strong>${hEscape(condition.result)}</strong> · rama ${hEscape(frame.executed_branch||"registrada")}`:""}${frame.adjustment?`<br>Ajuste: ${hEscape(frame.adjustment.message||frame.adjustment.type)}`:""}`;
  if (stack) {
    const live = frame.call_stack || [], completed = frame.completed_call_stack || [];
    const row = (call, historical) => `<div class="hier-stack-frame"><code>${hEscape(call.function)}</code> · ${historical ? "ámbito terminado (registro histórico)" : `profundidad ${hEscape(call.depth)}`}<br>raíz local registrada: ${hEscape(call.local_root_address||call.local_root||"NULL")}<br>retorno: ${hEscape(call.return ?? (historical ? "sin valor de retorno registrado" : "pendiente"))}${!historical && call.continuation ? ` · ${hEscape(call.continuation)}` : ""}</div>`;
    stack.innerHTML = live.length ? live.map(call => row(call, false)).join("") : "Sin llamadas activas en este paso.";
    if (completed.length) stack.innerHTML += `<details><summary>Marcos terminados (histórico): ${completed.length}</summary>${completed.map(call => row(call, true)).join("")}</details>`;
  }
  const proof = frame.invariant?.evidence_by_node_or_path || [];
  if (invariant) {
    const evidence = frame.invariant?.explanation || frame.invariant?.evidence || "";
    const brief = typeof evidence === "string" && !/^[\s]*[\[{]/.test(evidence) ? evidence : "La evidencia detallada está disponible en el registro técnico.";
    invariant.innerHTML = `<strong>${hEscape(frame.invariant?.symbol||"")} ${hEscape(frame.invariant?.name||"")}</strong><br>${hEscape(brief)}<details><summary>Registro técnico de la verificación</summary><pre>${hEscape(JSON.stringify({case:frame.case,evidence,proof},null,2))}</pre></details>`;
  }
  if(variables){variables.tabIndex=0;variables.setAttribute("role","region");variables.setAttribute("aria-label","Variables C: tabla desplazable horizontalmente con las flechas del teclado");}
  if(variables)variables.innerHTML=`<table><thead><tr><th>Tipo y variable</th><th>Anterior</th><th>Actual</th><th>Significado</th></tr></thead><tbody>${(frame.variables||[]).map((item)=>`<tr class="${item.changed?'is-changed':''}"><td><code>${hEscape(item.type)} ${hEscape(item.name)}</code>${item.scope?`<br><small>${hEscape(item.scope)}</small>`:""}</td><td>${hEscape(item.previous??"NULL")}</td><td>${hEscape(item.value??"NULL")}</td><td>${hEscape(item.meaning)}</td></tr>`).join("")}</tbody></table>`;
  if(memory){const mem=frame.memory||{};memory.innerHTML=`Evento: <strong>${hEscape(({none:"sin cambios de memoria",allocate:"reserva de memoria",allocation:"reserva de memoria",free:"liberación de memoria",link:"actualización de enlaces"})[mem.event] || mem.event || "sin cambios de memoria")}</strong><br>Reservados: ${hEscape((mem.allocated_objects||[]).map((item)=>item.address).join(", ")||"—")}<br>Liberados: ${hEscape((mem.freed_objects||[]).map((item)=>item.address).join(", ")||"—")}<br>Referencias colgantes: <strong>${(mem.dangling_references||[]).length}</strong>`;}
  if(memory && frame.memory && frame.memory.unusable_reference_records){
    const mem=frame.memory;memory.innerHTML=`Evento: <strong>${hEscape(mem.event)}</strong><br>Liberados (identidades historicas): ${hEscape((mem.freed_objects||[]).map(x=>x.address).join(', ')||'—')}<br>Referencias inutilizables registradas: <strong data-abb-unusable-count="${mem.unusable_reference_records.length}">${mem.unusable_reference_records.length}</strong><br>Son identidades guardadas; no se leen valores de punteros indeterminados.`;
  }
  if(relations){const arr=frame.array||{};relations.innerHTML=frame.structure==="binary_heap"?`A[i] activo: ${hEscape(arr.active_index??"—")} · padre: ${hEscape(arr.parent_index??"—")} · hijos: ${hEscape((arr.child_indices||[]).join(", ")||"—")}<br><strong>El heap no es un ABB ni un arreglo totalmente ordenado:</strong> solo garantiza prioridad padre-hijos.`:`Límites: ${hEscape(frame.path?.bounds?.lower||"-∞")} … ${hEscape(frame.path?.bounds?.upper||"+∞")} · sucesor: ${hEscape(frame.path?.successor??"—")}<br>Retorno: ${frame.return_propagation?.active?"activo":"sin retorno en esta instruccion"}<br>Reconexión del retorno: ${frame.return_propagation?.reconnects_subtree?"si":"no"}`;}
}

function hEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function hToCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\", "\\\\")
    .replaceAll('"', '\\"')
    .replaceAll("\r", "")
    .replaceAll("\n", "\\n");
}

function hDecodeCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\\\", "\u0000")
    .replaceAll("\\n", "\n")
    .replaceAll("\\t", "\t")
    .replaceAll('\\"', '"')
    .replaceAll("\\r", "")
    .replaceAll("\u0000", "\\");
}

function hExtractPrintfMessagesFromLine(lineText) {
  const source = String(lineText || "");
  const regex = /printf\s*\(\s*"((?:\\.|[^"\\])*)"/g;
  const messages = [];
  let match = regex.exec(source);
  while (match) {
    const decoded = hDecodeCStringLiteral(match[1]).replace(/\n+$/g, "").trim();
    if (decoded) {
      messages.push(decoded);
    }
    match = regex.exec(source);
  }
  return messages;
}

function hHasPrintfFormatSpecifier(text) {
  return /%[-+0-9.#hljztL]*[diuoxXfFeEgGaAcsp]/.test(String(text || ""));
}

function hIsOnlyPrintfSpecifier(text) {
  return /^%[-+0-9.#hljztL]*[diuoxXfFeEgGaAcsp]$/.test(String(text || "").trim());
}

function hNormalizeDidacticText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function hPushUniqueConsoleLine(lines, line) {
  const normalized = hNormalizeDidacticText(line);
  if (!normalized) {
    return;
  }
  if (lines.length && hNormalizeDidacticText(lines[lines.length - 1]) === normalized) {
    return;
  }
  lines.push(line);
}

function hBuildHistoryEntrySignature(entry) {
  if (!entry || typeof entry === "string") {
    return "";
  }
  const subroutine = hNormalizeDidacticText(entry.subroutine);
  const payload = hNormalizeDidacticText(entry.payload);
  const resultSource = Object.prototype.hasOwnProperty.call(entry, "finalResult")
    ? entry.finalResult
    : entry.result;
  const result = hNormalizeDidacticText(resultSource);
  const operation = hNormalizeDidacticText(entry.operation);
  return `${subroutine}|${payload}|${result}|${operation}`;
}

function hPushUniqueHistoryEntry(history, entry, options = {}) {
  if (!Array.isArray(history) || !entry) {
    return false;
  }
  const last = history.length ? history[history.length - 1] : null;
  if (!options.allowRepeated && hBuildHistoryEntrySignature(last) === hBuildHistoryEntrySignature(entry)) {
    return false;
  }
  history.push(entry);
  return true;
}

function hGetTraversalResultValuesFromTrace(trace) {
  const op = String(trace && trace.operation_name ? trace.operation_name : "").toLowerCase();
  if (!["inorden", "preorden", "postorden"].includes(op)) {
    return [];
  }
  const result = trace
    && trace.final_state
    && trace.final_state.last_result
    && Array.isArray(trace.final_state.last_result.result)
    ? trace.final_state.last_result.result
    : [];
  return result.map((value) => String(value));
}

function renderHierPrintfConsole(consoleEl, lines, fallbackText) {
  if (!consoleEl) {
    return;
  }
  const safeLines = Array.isArray(lines) ? lines : [];
  consoleEl.dataset.consoleCopy = safeLines.join("\n");
  const html = safeLines.length
    ? safeLines.map((line) => `<div class="console-line">${hEscape(line)}</div>`).join("")
    : `<div class="console-line muted">${hEscape(fallbackText || "(sin salida printf en esta ruta)")}</div>`;
  consoleEl.innerHTML = html;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

const H_C_KEYWORDS = new Set([
  "if", "else", "for", "while", "do", "switch", "case", "default", "break",
  "continue", "return", "sizeof", "typedef", "struct", "enum", "union",
  "static", "const", "volatile", "extern", "goto", "NULL", "true", "false",
]);

const H_C_TYPES = new Set([
  "void", "int", "bool", "float", "double", "char", "short", "long",
  "signed", "unsigned", "size_t",
]);

function hIsIdentStart(ch) {
  return /[A-Za-z_]/.test(ch);
}

function hIsIdentChar(ch) {
  return /[A-Za-z0-9_]/.test(ch);
}

function hNextNonSpaceChar(text, from) {
  let i = from;
  while (i < text.length && /\s/.test(text[i])) {
    i += 1;
  }
  return i < text.length ? text[i] : "";
}

function highlightHierCLine(line, state) {
  const text = String(line || "");
  const out = [];
  let i = 0;
  const inState = { inBlockComment: Boolean(state && state.inBlockComment) };

  if (/^\s*#/.test(text)) {
    return { html: `<span class="code-directive">${hEscape(text)}</span>`, state: inState };
  }

  while (i < text.length) {
    const ch = text[i];
    const next = i + 1 < text.length ? text[i + 1] : "";

    if (inState.inBlockComment) {
      const end = text.indexOf("*/", i);
      if (end === -1) {
        out.push(`<span class="code-comment">${hEscape(text.slice(i))}</span>`);
        i = text.length;
        break;
      }
      out.push(`<span class="code-comment">${hEscape(text.slice(i, end + 2))}</span>`);
      i = end + 2;
      inState.inBlockComment = false;
      continue;
    }

    if (ch === "/" && next === "/") {
      out.push(`<span class="code-comment">${hEscape(text.slice(i))}</span>`);
      i = text.length;
      break;
    }

    if (ch === "/" && next === "*") {
      const end = text.indexOf("*/", i + 2);
      if (end === -1) {
        out.push(`<span class="code-comment">${hEscape(text.slice(i))}</span>`);
        inState.inBlockComment = true;
        i = text.length;
      } else {
        out.push(`<span class="code-comment">${hEscape(text.slice(i, end + 2))}</span>`);
        i = end + 2;
      }
      continue;
    }

    if (ch === '"' || ch === "'") {
      const quote = ch;
      let j = i + 1;
      while (j < text.length) {
        if (text[j] === "\\" && j + 1 < text.length) {
          j += 2;
          continue;
        }
        if (text[j] === quote) {
          j += 1;
          break;
        }
        j += 1;
      }
      out.push(`<span class="code-string">${hEscape(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (/[0-9]/.test(ch)) {
      let j = i + 1;
      while (j < text.length && /[0-9A-Fa-fxXuUlL\.]/.test(text[j])) {
        j += 1;
      }
      out.push(`<span class="code-number">${hEscape(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (hIsIdentStart(ch)) {
      let j = i + 1;
      while (j < text.length && hIsIdentChar(text[j])) {
        j += 1;
      }
      const word = text.slice(i, j);
      let cls = "";
      if (H_C_TYPES.has(word)) {
        cls = "code-type";
      } else if (H_C_KEYWORDS.has(word)) {
        cls = "code-keyword";
      } else if (hNextNonSpaceChar(text, j) === "(") {
        cls = "code-function";
      }
      out.push(cls ? `<span class="${cls}">${hEscape(word)}</span>` : hEscape(word));
      i = j;
      continue;
    }

    if ("{}[]();,*".includes(ch)) {
      out.push(`<span class="code-punct">${hEscape(ch)}</span>`);
      i += 1;
      continue;
    }

    out.push(hEscape(ch));
    i += 1;
  }

  return { html: out.join(""), state: inState };
}

function buildHierHighlightedCodeHtml(raw, codeTitle) {
  const lines = String(raw || "").replaceAll("\r\n", "\n").split("\n");

  if (String(codeTitle || "").toLowerCase().includes("codigo c")) {
    let state = { inBlockComment: false };
    return lines
      .map((line, index) => {
        const highlighted = highlightHierCLine(line, state);
        state = highlighted.state;
        return `<span class="code-line" data-line="${index}">${highlighted.html || ""}</span>`;
      })
      .join("");
  }

  return lines
    .map((line, index) => `<span class="code-line" data-line="${index}">${hEscape(line) || ""}</span>`)
    .join("");
}

function renderHierDidacticCode(preElement, code, codeTitle) {
  const raw = String(code || "");
  preElement.dataset.rawCode = raw;
  preElement.dataset.codeTitle = String(codeTitle || "");
  preElement.innerHTML = buildHierHighlightedCodeHtml(raw, codeTitle);
}

function buildOperationInputs(operation, container) {
  container.innerHTML = "";
  if (!operation || !operation.inputs) {
    return;
  }

  operation.inputs.forEach((field) => {
    const wrap = document.createElement("div");
    const label = document.createElement("label");
    label.textContent = field.label;
    label.setAttribute("for", `h-field-${field.name}`);

    const input = document.createElement("input");
    input.id = `h-field-${field.name}`;
    input.name = field.name;
    input.type = field.type === "number" ? "number" : "text";
    input.required = field.required !== false;

    wrap.appendChild(label);
    wrap.appendChild(input);
    container.appendChild(wrap);
  });
}

function flattenTree(root) {
  if (!root) {
    return [];
  }

  const nodes = [];
  let cursor = 0;

  function walk(node, depth, parentKey) {
    if (!node) {
      return null;
    }

    const leftKey = walk(node.left, depth + 1, node.heap_index !== undefined ? `idx-${node.heap_index}` : String(node.value));
    const key = node.heap_index !== undefined ? `idx-${node.heap_index}` : String(node.value);
    const id = `n-${cursor}`;
    cursor += 1;

    const leftHeight = node.left && node.left.height !== undefined && node.left.height !== null ? Number(node.left.height) : 0;
    const rightHeight = node.right && node.right.height !== undefined && node.right.height !== null ? Number(node.right.height) : 0;
    // Contrato TAD C para AVL: FE = der - izq
    const inferredBalance = rightHeight - leftHeight;

    const currentNode = {
      id,
      key,
      value: node.value,
      x: cursor * 88,
      y: depth * 86 + 48,
      color: node.color || null,
      height: node.height ?? null,
      balanceFactor: node.balance_factor ?? inferredBalance,
      leftKey,
      rightKey: null,
      parentKey,
    };

    nodes.push(currentNode);
    currentNode.rightKey = walk(node.right, depth + 1, key);
    return key;
  }

  walk(root, 0, null);
  return nodes;
}

function rbBuildNodeIndex(root, parentKey = null, acc = new Map()) {
  if (!root) {
    return acc;
  }
  const key = String(root.value);
  acc.set(key, {
    key,
    value: root.value,
    color: String(root.color || "BLACK"),
    parentKey,
    leftKey: root.left ? String(root.left.value) : null,
    rightKey: root.right ? String(root.right.value) : null,
  });
  rbBuildNodeIndex(root.left, key, acc);
  rbBuildNodeIndex(root.right, key, acc);
  return acc;
}

function rbAnalyzeRules(root) {
  if (!root) {
    return {
      rootBlack: true,
      redRedPairs: [],
      blackHeightOk: true,
    };
  }

  const redRedPairs = [];

  function walk(node) {
    if (!node) {
      return { ok: true, blackHeight: 1, isRed: false };
    }

    const left = walk(node.left);
    const right = walk(node.right);
    const color = String(node.color || "BLACK");
    const isRed = color === "RED";

    if (isRed) {
      if (left.isRed) {
        redRedPairs.push(`${node.value}-${node.left.value}`);
      }
      if (right.isRed) {
        redRedPairs.push(`${node.value}-${node.right.value}`);
      }
    }

    const selfBlack = isRed ? 0 : 1;
    const blackHeight = Math.max(left.blackHeight, right.blackHeight) + selfBlack;
    const ok = left.ok && right.ok && left.blackHeight === right.blackHeight;
    return { ok, blackHeight, isRed };
  }

  const rootColor = String(root.color || "BLACK");
  const walked = walk(root);
  return {
    rootBlack: rootColor === "BLACK",
    redRedPairs,
    blackHeightOk: walked.ok,
  };
}

function rbDidacticDelta(stepMeta, compareState) {
  if (!stepMeta || !stepMeta.state_snapshot || !stepMeta.state_after) {
    return compareState;
  }
  const beforeRoot = stepMeta.state_snapshot.root || null;
  const afterRoot = stepMeta.state_after.root || null;
  if (!beforeRoot && !afterRoot) {
    return compareState;
  }

  const beforeMap = rbBuildNodeIndex(beforeRoot);
  const afterMap = rbBuildNodeIndex(afterRoot);
  const events = [];
  const recolored = [];
  const reparented = [];

  afterMap.forEach((afterNode, key) => {
    const beforeNode = beforeMap.get(key);
    if (beforeNode && beforeNode.color !== afterNode.color) {
      recolored.push(`${key}: ${beforeNode.color} -> ${afterNode.color}`);
    }
    if (beforeNode && beforeNode.parentKey !== afterNode.parentKey) {
      reparented.push(String(key));
    }
  });

  if (recolored.length) {
    events.push(`Recoloracion: ${recolored.join(", ")}.`);
  }
  if (reparented.length >= 2) {
    events.push(`Rotacion detectada (cambio estructural en: ${reparented.join(", ")}).`);
  }

  const beforeRules = rbAnalyzeRules(beforeRoot);
  const afterRules = rbAnalyzeRules(afterRoot);
  if (beforeRules.redRedPairs.length && !afterRules.redRedPairs.length) {
    events.push("Se resolvio conflicto rojo-rojo.");
  } else if (afterRules.redRedPairs.length) {
    events.push(`Conflicto rojo-rojo activo en: ${afterRules.redRedPairs.join(", ")}.`);
  }
  if (!afterRules.rootBlack) {
    events.push("Advertencia: la raiz debe ser negra.");
  }
  if (!afterRules.blackHeightOk) {
    events.push("Advertencia: altura negra inconsistente entre caminos.");
  }

  const next = compareState ? { ...compareState } : {};
  next.rnEvents = events;
  if (events.length) {
    next.rotationMessage = next.rotationMessage || events[0];
  }
  const active = Array.isArray(next.activeKeys) ? [...next.activeKeys] : [];
  recolored.forEach((item) => {
    const key = item.split(":", 1)[0].trim();
    if (key && !active.includes(key)) {
      active.push(key);
    }
  });
  next.activeKeys = active;
  return next;
}

function rbStageLabel(stage) {
  const value = String(stage || "").trim().toLowerCase();
  if (!value) {
    return "Ejecucion";
  }
  const labels = {
    search: "Busqueda",
    apply: "Aplicacion",
    pre_fixup: "Pre-fixup",
    fixup: "Fixup",
    post_fixup: "Post-fixup",
    result: "Resultado",
    start: "Inicio",
    progress: "Progreso",
    end: "Fin",
    single: "Paso unico",
  };
  return labels[value] || value;
}

function rbTimelineEntryFromStep(step) {
  const debug = step && typeof step.debug === "object" ? step.debug : null;
  const stage = rbStageLabel(debug && debug.stage ? debug.stage : step && step.phase ? step.phase : "");
  const baseNote = debug && debug.note ? String(debug.note).trim() : "";
  const lineText = step && step.line_text ? String(step.line_text).trim() : "";
  const entry = {
    stage,
    note: baseNote || (lineText ? `Linea C: ${lineText}` : "Paso del algoritmo."),
  };
  return entry;
}

function rbBuildTimelineFromTrace(trace) {
  if (!trace || !Array.isArray(trace.steps)) {
    return [];
  }
  return trace.steps.map((step) => rbTimelineEntryFromStep(step));
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function isHierExecutableLine(text, codeTitle) {
  const line = String(text || "").trim();
  if (!line) {
    return false;
  }
  if (line.startsWith("//") || line.startsWith("/*") || line.startsWith("*/")) {
    return false;
  }
  if (line === "*" || (line.startsWith("*") && line.length > 1 && /\s/.test(line[1]))) {
    return false;
  }
  if (line === "{" || line === "}") {
    return false;
  }
  if (String(codeTitle || "").toLowerCase().includes("codigo c") && line.startsWith("#")) {
    return false;
  }
  return true;
}

function hNextSignificantLine(lines, fromIndex) {
  for (let i = fromIndex; i < lines.length; i += 1) {
    const text = String(lines[i] || "").trim();
    if (!text) {
      continue;
    }
    if (text.startsWith("//") || text.startsWith("/*") || text.startsWith("*") || text.startsWith("*/")) {
      continue;
    }
    return i;
  }
  return -1;
}

function hFindMatchingBraceLine(lines, openLineIndex) {
  let depth = 0;
  for (let i = openLineIndex; i < lines.length; i += 1) {
    const line = String(lines[i] || "");
    for (let j = 0; j < line.length; j += 1) {
      const ch = line[j];
      if (ch === "{") {
        depth += 1;
      } else if (ch === "}") {
        depth -= 1;
        if (depth === 0) {
          return i;
        }
      }
    }
  }
  return -1;
}

function hResolveWhileLimit(condExpr, context) {
  const cond = String(condExpr || "").replace(/\s+/g, " ").trim();
  const size = Number(context?.sizeBefore || 0);
  const compareSteps = Number(context?.comparePath?.length || 0);

  if (cond.includes("actual != arbol->nil")) {
    return compareSteps > 0 ? compareSteps : Math.max(1, Math.min(10, size + 1));
  }
  if (cond.includes("actual != NULL")) {
    return compareSteps > 0 ? compareSteps : Math.max(1, Math.min(10, size + 1));
  }

  return Math.max(1, Math.min(8, size + 1));
}

function hEvalCondition(condExpr, context, runtime, whileMeta) {
  const cond = String(condExpr || "").replace(/\s+/g, " ").trim();
  const size = Number(context?.sizeBefore || 0);
  const compareSteps = Number(context?.comparePath?.length || 0);
  const compareFound = Boolean(context?.compareFound);
  const directions = Array.isArray(context?.compareDirections) ? context.compareDirections : [];
  const key = whileMeta?.key || "";
  const done = runtime.loopCounter[key] || 0;
  const limit = Number.isFinite(whileMeta?.limit) ? whileMeta.limit : null;
  const currentDirection = directions.length ? directions[Math.min(done, directions.length - 1)] : "";

  if (cond.includes("arbol == NULL")) {
    return false;
  }
  if (cond.includes("arbol != NULL")) {
    return true;
  }
  if (cond.includes("arbol->raiz == arbol->nil")) {
    return size === 0;
  }
  if (cond.includes("arbol->raiz != arbol->nil")) {
    return size > 0;
  }
  if (cond.includes("actual != arbol->nil") || cond.includes("actual != NULL")) {
    const loopsNeeded = limit !== null ? limit : Math.max(1, Math.min(10, size + 1));
    return done < loopsNeeded;
  }
  if (cond.includes("actual == arbol->nil") || cond.includes("actual == NULL")) {
    const loopsNeeded = limit !== null ? limit : Math.max(1, Math.min(10, size + 1));
    return done >= loopsNeeded;
  }
  if (cond.includes("valor == actual->valor")) {
    if (!compareFound || compareSteps <= 0) {
      return false;
    }
    return done === (compareSteps - 1);
  }
  if (cond.includes("valor < actual->valor")) {
    if (currentDirection) {
      return currentDirection === "left";
    }
    const target = Number(context?.payload?.value);
    if (Number.isFinite(target)) {
      return true;
    }
  }
  if (cond.includes("valor > actual->valor")) {
    if (currentDirection) {
      return currentDirection === "right";
    }
    const target = Number(context?.payload?.value);
    if (Number.isFinite(target)) {
      return true;
    }
  }

  if (whileMeta) {
    const safeLimit = limit !== null ? limit : Math.max(1, Math.min(8, size + 1));
    return done < safeLimit;
  }
  return true;
}

function buildHierExecutionPlan(rawCode, context) {
  const lines = String(rawCode || "").replaceAll("\r\n", "\n").split("\n");
  const executed = [];
  const skipped = new Set();
  const jumpAfterClose = {};
  const loopAtClose = {};
  const runtime = { loopCounter: {} };

  let i = 0;
  let guard = 0;
  while (i >= 0 && i < lines.length && guard < 3500) {
    guard += 1;
    const raw = String(lines[i] || "");
    const line = raw.trim();

    if (!line || line.startsWith("//") || line.startsWith("/*") || line.startsWith("*") || line.startsWith("*/")) {
      i += 1;
      continue;
    }

    executed.push(i);

    const ifMatch = line.match(/^if\s*\((.*)\)\s*\{?$/);
    if (ifMatch) {
      const cond = ifMatch[1] || "";
      const openIdx = raw.includes("{") ? i : hNextSignificantLine(lines, i + 1);
      const closeIdx = openIdx >= 0 ? hFindMatchingBraceLine(lines, openIdx) : -1;
      const truth = hEvalCondition(cond, context, runtime, null);

      if (!truth && closeIdx >= 0) {
        for (let k = i + 1; k <= closeIdx; k += 1) {
          skipped.add(k);
        }
        const elseIdx = hNextSignificantLine(lines, closeIdx + 1);
        if (elseIdx >= 0 && String(lines[elseIdx]).trim().startsWith("else")) {
          i = elseIdx;
        } else {
          i = closeIdx + 1;
        }
        continue;
      }

      if (truth && closeIdx >= 0) {
        const elseIdx = hNextSignificantLine(lines, closeIdx + 1);
        if (elseIdx >= 0 && String(lines[elseIdx]).trim().startsWith("else")) {
          const elseOpenIdx = String(lines[elseIdx]).includes("{") ? elseIdx : hNextSignificantLine(lines, elseIdx + 1);
          const elseCloseIdx = elseOpenIdx >= 0 ? hFindMatchingBraceLine(lines, elseOpenIdx) : -1;
          if (elseCloseIdx >= 0) {
            for (let k = elseIdx; k <= elseCloseIdx; k += 1) {
              skipped.add(k);
            }
            jumpAfterClose[closeIdx] = elseCloseIdx + 1;
          }
        }
      }
      i += 1;
      continue;
    }

    if (line.startsWith("else")) {
      i += 1;
      continue;
    }

    const whileMatch = line.match(/^while\s*\((.*)\)\s*\{?$/);
    if (whileMatch) {
      const cond = whileMatch[1] || "";
      const openIdx = raw.includes("{") ? i : hNextSignificantLine(lines, i + 1);
      const closeIdx = openIdx >= 0 ? hFindMatchingBraceLine(lines, openIdx) : -1;
      const key = `${i}:${closeIdx}`;
      const whileMeta = { key, limit: hResolveWhileLimit(cond, context) };
      const truth = hEvalCondition(cond, context, runtime, whileMeta);

      if (!truth && closeIdx >= 0) {
        for (let k = i + 1; k <= closeIdx; k += 1) {
          skipped.add(k);
        }
        i = closeIdx + 1;
        continue;
      }

      if (closeIdx >= 0) {
        loopAtClose[closeIdx] = { start: i, cond, key, limit: whileMeta.limit };
      }
      i += 1;
      continue;
    }

    if (line.startsWith("return ")) {
      break;
    }

    if (jumpAfterClose[i] !== undefined) {
      i = jumpAfterClose[i];
      continue;
    }

    if (line === "}" && loopAtClose[i]) {
      const meta = loopAtClose[i];
      runtime.loopCounter[meta.key] = (runtime.loopCounter[meta.key] || 0) + 1;
      const truth = hEvalCondition(meta.cond, context, runtime, meta);
      if (truth) {
        i = meta.start;
      } else {
        delete loopAtClose[i];
        i += 1;
      }
      continue;
    }

    i += 1;
  }

  return { executed, skipped };
}

async function simulateHierDidacticExecution(context) {
  const codeBox = hById("op-pseudocode");
  if (!codeBox) {
    return;
  }

  const codeTitle = codeBox.dataset.codeTitle || "";
  const rawCode = codeBox.dataset.rawCode || codeBox.textContent || "";
  const plan = buildHierExecutionPlan(rawCode, context || {});
  const lines = Array.from(codeBox.querySelectorAll(".code-line"));
  const steps = plan.executed
    .map((lineIndex) => lines[lineIndex])
    .filter((lineElement) => Boolean(lineElement))
    .filter((lineElement) => isHierExecutableLine(lineElement.textContent, codeTitle));

  if (!steps.length) {
    return;
  }

  lines.forEach((lineElement) => {
    lineElement.classList.remove("sim-active");
    lineElement.classList.remove("sim-done");
    lineElement.classList.remove("sim-skip");
  });
  plan.skipped.forEach((index) => {
    if (lines[index]) {
      lines[index].classList.add("sim-skip");
    }
  });

  const speed = Math.min(4, Math.max(0.25, Number(context?.playbackSpeed) || 1));
  const stepDelayMs = Math.max(20, Math.round(180 / speed));
  for (let i = 0; i < steps.length; i += 1) {
    const current = steps[i];
    current.classList.add("sim-active");
    if (i > 0) {
      steps[i - 1].classList.remove("sim-active");
      steps[i - 1].classList.add("sim-done");
    }
    window.CCodeNavigation?.revealLine(codeBox, current);
    await sleep(stepDelayMs);
  }

  const last = steps[steps.length - 1];
  last.classList.remove("sim-active");
  last.classList.add("sim-done");
  await sleep(Math.max(20, Math.round(120 / speed)));

  lines.forEach((lineElement) => {
    lineElement.classList.remove("sim-active");
  });
}

function isSearchLikeStructure(modelId) {
  return modelId === "abb" || modelId === "avl" || modelId === "red_black";
}

function normalizeCompareValue(rawValue) {
  if (rawValue === null || rawValue === undefined) {
    return null;
  }
  const text = String(rawValue).trim();
  if (!text) {
    return null;
  }
  const asNumber = Number(text);
  if (Number.isFinite(asNumber)) {
    return asNumber;
  }
  return text;
}

function buildComparisonPath(root, targetValue) {
  const pathKeys = [];
  const directions = [];
  let current = root;
  let found = false;

  while (current) {
    const key = String(current.value);
    pathKeys.push(key);
    if (targetValue === current.value) {
      directions.push("equal");
      found = true;
      break;
    }
    if (targetValue < current.value) {
      directions.push("left");
      current = current.left;
    } else {
      directions.push("right");
      current = current.right;
    }
  }

  return {
    pathKeys,
    found,
    directions,
  };
}

function getNodeHeightForInference(node) {
  if (!node) {
    return 0;
  }
  if (node.height !== null && node.height !== undefined) {
    return Number(node.height);
  }
  const leftHeight = getNodeHeightForInference(node.left);
  const rightHeight = getNodeHeightForInference(node.right);
  return 1 + Math.max(leftHeight, rightHeight);
}

function inferAvlInsertionRotation(root, insertedValue) {
  let detected = null;

  function walk(node) {
    if (!node) {
      return { height: 1, inserted: true };
    }

    if (insertedValue === node.value) {
      return { height: getNodeHeightForInference(node), inserted: false };
    }

    let leftHeight = getNodeHeightForInference(node.left);
    let rightHeight = getNodeHeightForInference(node.right);
    let inserted = false;

    if (insertedValue < node.value) {
      const leftResult = walk(node.left);
      inserted = leftResult.inserted;
      leftHeight = leftResult.height;
    } else {
      const rightResult = walk(node.right);
      inserted = rightResult.inserted;
      rightHeight = rightResult.height;
    }

    const balance = leftHeight - rightHeight;
    if (!detected && inserted && (balance > 1 || balance < -1)) {
      if (balance > 1) {
        const childValue = node.left ? node.left.value : insertedValue;
        detected = {
          type: insertedValue < childValue ? "LL" : "LR",
          pivot: String(node.value),
          child: String(childValue),
          inserted: String(insertedValue),
        };
      } else {
        const childValue = node.right ? node.right.value : insertedValue;
        detected = {
          type: insertedValue > childValue ? "RR" : "RL",
          pivot: String(node.value),
          child: String(childValue),
          inserted: String(insertedValue),
        };
      }
    }

    return {
      height: 1 + Math.max(leftHeight, rightHeight),
      inserted,
    };
  }

  walk(root);
  return detected;
}

function inferAvlDeletionRotation(root, deletedValue) {
  if (!root) {
    return null;
  }

  let detected = null;

  function infoFromNode(node) {
    if (!node) {
      return {
        height: 0,
        leftHeight: 0,
        rightHeight: 0,
        deleted: false,
      };
    }
    const leftHeight = getNodeHeightForInference(node.left);
    const rightHeight = getNodeHeightForInference(node.right);
    return {
      height: 1 + Math.max(leftHeight, rightHeight),
      leftHeight,
      rightHeight,
      deleted: false,
    };
  }

  function composeInfo(node, leftInfo, rightInfo, deleted) {
    const leftHeight = leftInfo.height;
    const rightHeight = rightInfo.height;
    const balance = leftHeight - rightHeight;

    if (!detected && deleted && (balance > 1 || balance < -1)) {
      if (balance > 1) {
        const childBalance = leftInfo.leftHeight - leftInfo.rightHeight;
        detected = {
          type: childBalance >= 0 ? "LL" : "LR",
          pivot: String(node.value),
          child: node.left ? String(node.left.value) : "",
          affected: String(deletedValue),
        };
      } else {
        const childBalance = rightInfo.leftHeight - rightInfo.rightHeight;
        detected = {
          type: childBalance <= 0 ? "RR" : "RL",
          pivot: String(node.value),
          child: node.right ? String(node.right.value) : "",
          affected: String(deletedValue),
        };
      }
    }

    return {
      height: 1 + Math.max(leftHeight, rightHeight),
      leftHeight,
      rightHeight,
      deleted,
    };
  }

  function deleteMin(node) {
    if (!node) {
      return {
        height: 0,
        leftHeight: 0,
        rightHeight: 0,
        deleted: false,
      };
    }

    if (!node.left) {
      const rightInfo = infoFromNode(node.right);
      return {
        height: rightInfo.height,
        leftHeight: rightInfo.leftHeight,
        rightHeight: rightInfo.rightHeight,
        deleted: true,
      };
    }

    const leftInfo = deleteMin(node.left);
    const rightInfo = infoFromNode(node.right);
    return composeInfo(node, leftInfo, rightInfo, leftInfo.deleted);
  }

  function walk(node) {
    if (!node) {
      return {
        height: 0,
        leftHeight: 0,
        rightHeight: 0,
        deleted: false,
      };
    }

    if (deletedValue < node.value) {
      const leftInfo = walk(node.left);
      if (!leftInfo.deleted) {
        return infoFromNode(node);
      }
      const rightInfo = infoFromNode(node.right);
      return composeInfo(node, leftInfo, rightInfo, true);
    }

    if (deletedValue > node.value) {
      const rightInfo = walk(node.right);
      if (!rightInfo.deleted) {
        return infoFromNode(node);
      }
      const leftInfo = infoFromNode(node.left);
      return composeInfo(node, leftInfo, rightInfo, true);
    }

    if (!node.left && !node.right) {
      return {
        height: 0,
        leftHeight: 0,
        rightHeight: 0,
        deleted: true,
      };
    }

    if (!node.left) {
      const rightInfo = infoFromNode(node.right);
      return {
        height: rightInfo.height,
        leftHeight: rightInfo.leftHeight,
        rightHeight: rightInfo.rightHeight,
        deleted: true,
      };
    }

    if (!node.right) {
      const leftInfo = infoFromNode(node.left);
      return {
        height: leftInfo.height,
        leftHeight: leftInfo.leftHeight,
        rightHeight: leftInfo.rightHeight,
        deleted: true,
      };
    }

    const leftInfo = infoFromNode(node.left);
    const rightInfo = deleteMin(node.right);
    return composeInfo(node, leftInfo, rightInfo, true);
  }

  walk(root);
  return detected;
}

function comparisonHighlight(compareState) {
  const highlights = {
    visitedKeys: new Set(),
    activeKeys: new Set(),
    unbalancedKeys: new Set(),
    rotationMessage: "",
  };

  if (!compareState) {
    return highlights;
  }

  if (Array.isArray(compareState.activeKeys)) {
    compareState.activeKeys.forEach((key) => {
      highlights.activeKeys.add(String(key));
    });
  }
  if (compareState.unbalancedKey !== undefined && compareState.unbalancedKey !== null) {
    highlights.unbalancedKeys.add(String(compareState.unbalancedKey));
  }
  if (compareState.rotationMessage) {
    highlights.rotationMessage = String(compareState.rotationMessage);
  }

  if (Array.isArray(compareState.pathKeys) && compareState.index >= 0) {
    const maxIndex = Math.min(compareState.index, compareState.pathKeys.length - 1);
    for (let i = 0; i <= maxIndex; i += 1) {
      const key = String(compareState.pathKeys[i]);
      highlights.visitedKeys.add(key);
      if (i === maxIndex) {
        highlights.activeKeys.add(key);
      }
    }
  }

  return highlights;
}

function getRotationNodeClass(nodeKey, rotationHint) {
  if (!rotationHint || !nodeKey) {
    return "";
  }

  const pivot = String(rotationHint.pivot || "");
  const child = String(rotationHint.child || "");
  const inserted = String(rotationHint.inserted || rotationHint.affected || "");
  const type = String(rotationHint.type || "");

  if (type === "LL") {
    if (nodeKey === pivot) {
      return " rot-cw";
    }
    if (nodeKey === child || nodeKey === inserted) {
      return " rot-ccw";
    }
  }
  if (type === "RR") {
    if (nodeKey === pivot) {
      return " rot-ccw";
    }
    if (nodeKey === child || nodeKey === inserted) {
      return " rot-cw";
    }
  }
  if (type === "LR") {
    if (nodeKey === pivot) {
      return " rot-cw";
    }
    if (nodeKey === child || nodeKey === inserted) {
      return " rot-ccw";
    }
  }
  if (type === "RL") {
    if (nodeKey === pivot) {
      return " rot-ccw";
    }
    if (nodeKey === child || nodeKey === inserted) {
      return " rot-cw";
    }
  }

  return "";
}

function rotationHintText(rotationHint) {
  if (!rotationHint) {
    return "";
  }
  const type = String(rotationHint.type || "");
  const pivot = String(rotationHint.pivot || "");
  const child = String(rotationHint.child || "");

  if (type === "LL") {
    return `Rotacion AVL LL: rotacion a la derecha en ${pivot}.`;
  }
  if (type === "RR") {
    return `Rotacion AVL RR: rotacion a la izquierda en ${pivot}.`;
  }
  if (type === "LR") {
    return `Rotacion AVL LR: izquierda en ${child} y luego derecha en ${pivot}.`;
  }
  if (type === "RL") {
    return `Rotacion AVL RL: derecha en ${child} y luego izquierda en ${pivot}.`;
  }
  return "Rotacion AVL detectada.";
}

function buildNullLeafVisuals(nodes, options = {}) {
  if (!options.showNullLeaves || !Array.isArray(nodes) || !nodes.length) {
    return [];
  }

  const nodeMap = new Map(nodes.map((node) => [node.key, node]));
  const nullLeaves = [];
  const baseDx = 44;
  const stepY = 86;

  nodes.forEach((node, index) => {
    const leftNode = node.leftKey && nodeMap.has(node.leftKey) ? nodeMap.get(node.leftKey) : null;
    const rightNode = node.rightKey && nodeMap.has(node.rightKey) ? nodeMap.get(node.rightKey) : null;
    const childY = node.y + stepY;

    if (!leftNode && (!options.rbtClearMemory || node.leftKey === "NULL")) {
      const dx = rightNode ? Math.max(baseDx, Math.abs(rightNode.x - node.x)) : baseDx;
      nullLeaves.push({
        key: `${node.key}-nil-left-${index}`,
        parentKey: node.key, side: "left",
        parentX: node.x,
        parentY: node.y,
        x: node.x - dx,
        y: childY,
      });
    }

    if (!rightNode && (!options.rbtClearMemory || node.rightKey === "NULL")) {
      const dx = leftNode ? Math.max(baseDx, Math.abs(node.x - leftNode.x)) : baseDx;
      nullLeaves.push({
        key: `${node.key}-nil-right-${index}`,
        parentKey: node.key, side: "right",
        parentX: node.x,
        parentY: node.y,
        x: node.x + dx,
        y: childY,
      });
    }
  });

  return nullLeaves;
}

function drawTreeSvgFromNodes(nodes, options = {}) {
  if (!nodes.length) {
    return "<p class=\"viz-empty\">Estructura vacia.</p>";
  }

  const nodeMap = new Map(nodes.map((node) => [node.key, node]));
  const nullLeaves = buildNullLeafVisuals(nodes, options);
  let minX = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = 0;
  nodes.forEach((node) => {
    minX = Math.min(minX, node.x);
    maxX = Math.max(maxX, node.x);
    maxY = Math.max(maxY, node.y);
  });
  nullLeaves.forEach((leaf) => {
    minX = Math.min(minX, leaf.x);
    maxX = Math.max(maxX, leaf.x);
    maxY = Math.max(maxY, leaf.y);
  });
  if (!Number.isFinite(minX)) {
    minX = 0;
  }
  const padX = 40;
  const offsetX = minX < padX ? (padX - minX) : 0;
  const svgWidth = maxX + offsetX + 90;
  const svgHeight = maxY + 70;

  const compare = comparisonHighlight(options.compareState);

  const minY = Math.min(...nodes.map(node => node.y), ...nullLeaves.map(leaf => leaf.y));
  const viewBox = options.fitBounds ? `${minX + offsetX - 35} ${minY - 35} ${maxX - minX + 70} ${maxY - minY + 80}` : `0 0 ${svgWidth} ${svgHeight}`;
  let svg = `<svg class="viz-tree-svg" width="${svgWidth}" height="${svgHeight}" viewBox="${viewBox}" xmlns="http://www.w3.org/2000/svg">`;

  nodes.forEach((node) => {
    if (node.leftKey && nodeMap.has(node.leftKey)) {
      const left = nodeMap.get(node.leftKey);
      svg += `<line x1="${node.x + offsetX}" y1="${node.y + 18}" x2="${left.x + offsetX}" y2="${left.y - 18}" class="viz-tree-edge"${options.avlInsertionMemory ? ` data-avl-svg-from="${node.id}" data-avl-svg-to="${node.leftKey}" data-avl-svg-side="left"` : ""}${options.rbtClearMemory ? ` data-rbt-svg-from="${node.id}" data-rbt-svg-to="${node.leftKey}" data-rbt-svg-side="left"` : ""} />`;
    }
    if (node.rightKey && nodeMap.has(node.rightKey)) {
      const right = nodeMap.get(node.rightKey);
      svg += `<line x1="${node.x + offsetX}" y1="${node.y + 18}" x2="${right.x + offsetX}" y2="${right.y - 18}" class="viz-tree-edge"${options.avlInsertionMemory ? ` data-avl-svg-from="${node.id}" data-avl-svg-to="${node.rightKey}" data-avl-svg-side="right"` : ""}${options.rbtClearMemory ? ` data-rbt-svg-from="${node.id}" data-rbt-svg-to="${node.rightKey}" data-rbt-svg-side="right"` : ""} />`;
    }
  });

  nullLeaves.forEach((leaf) => {
    svg += `<line x1="${leaf.parentX + offsetX}" y1="${leaf.parentY + 18}" x2="${leaf.x + offsetX}" y2="${leaf.y - 14}" class="viz-tree-edge"${options.rbtClearMemory ? ` data-rbt-svg-from="${leaf.parentKey}" data-rbt-svg-to="NULL" data-rbt-svg-side="${leaf.side}"` : ""} />`;
  });

  nodes.forEach((node) => {
    let nodeClass = "viz-tree-node";
    if (node.color === "RED") {
      nodeClass += " red";
    }
    if (node.color === "BLACK") {
      nodeClass += " black";
    }
    if (compare.visitedKeys.has(node.key)) {
      nodeClass += " sim-visited";
    }
    if (compare.activeKeys.has(node.key)) {
      nodeClass += " sim-active";
    }
    if (compare.unbalancedKeys.has(node.key)) {
      nodeClass += " sim-imbalanced";
    }
    nodeClass += getRotationNodeClass(node.key, options.rotationHint);

    svg += `<circle cx="${node.x + offsetX}" cy="${node.y}" r="24" class="${nodeClass}"${options.avlInsertionMemory ? ` data-avl-svg-node="${hEscape(node.id)}" data-avl-svg-status="${node.status}" data-avl-svg-parent="${hEscape(node.parentReference)}" data-avl-svg-fe="${hEscape(node.balanceFactor)}"${node.status==='detached'?' stroke-dasharray="4 3"':''}` : ""}${options.rbtClearMemory ? ` data-rbt-svg-node="${hEscape(node.id)}" data-rbt-svg-parent="${hEscape(node.parentReference)}" data-rbt-svg-color="${hEscape(node.color)}" data-rbt-svg-initialized="${node.initialized ?? 31}"${node.initialized!==undefined&&node.initialized!==31?' stroke-dasharray="4 3"':''}` : ""}${options.queryMemory ? ` data-heap-tree-index="${hEscape(node.key.replace("idx-", ""))}"` : ""}${options.insertMemory ? ` data-heap-tree-owner="${hEscape(options.memoryOwner)}"` : ""} />`;
    svg += `<text x="${node.x + offsetX}" y="${node.y + 6}" text-anchor="middle" class="viz-tree-text">${hEscape(node.value)}</text>`;

    if (options.rbtClearMemory && options.rbtInsertMemory) svg += `<text x="${node.x+offsetX}" y="${node.y+44}" text-anchor="middle" data-rbt-svg-reference="${node.id}">${hEscape(node.id)}; color:${hEscape(({BLACK:"negro",RED:"rojo"})[node.color] || node.color)}</text>`;
    if (options.avlInsertionMemory) svg += `<text x="${node.x+offsetX}" y="${node.y+44}" text-anchor="middle" data-avl-svg-reference="${node.id}">${node.id}; padre:${hEscape(node.parentReference)}</text>`;
    if (options.showBalanceFactor) {
      const feClass = node.balanceFactor >= -1 && node.balanceFactor <= 1 ? "viz-tree-fe ok" : "viz-tree-fe bad";
      svg += `<text x="${node.x + offsetX + 25}" y="${node.y - 18}" class="${feClass}">fe:${hEscape(node.balanceFactor)}</text>`;
    } else if (node.height !== null && node.height !== undefined) {
      svg += `<text x="${node.x + offsetX + 20}" y="${node.y - 18}" class="viz-tree-height">h:${hEscape(node.height)}</text>`;
    }
  });

  nullLeaves.forEach((leaf) => {
    svg += `<circle cx="${leaf.x + offsetX}" cy="${leaf.y}" r="16" class="viz-tree-node black nil" />`;
    svg += `<text x="${leaf.x + offsetX}" y="${leaf.y + 4}" text-anchor="middle" class="viz-tree-text nil">NULL</text>`;
  });

  svg += "</svg>";
  return svg;
}

function buildTransitionData(previousRoot, nextRoot) {
  const fromNodes = flattenTree(previousRoot);
  const toNodes = flattenTree(nextRoot);
  if (!fromNodes.length || !toNodes.length) {
    return null;
  }

  const fromMap = new Map(fromNodes.map((node) => [node.key, node]));
  const toMap = new Map(toNodes.map((node) => [node.key, node]));
  const keys = new Set([...fromMap.keys(), ...toMap.keys()]);

  const items = [];
  keys.forEach((key) => {
    const from = fromMap.get(key) || null;
    const to = toMap.get(key) || null;

    const startX = from ? from.x : (to ? to.x : 0);
    const startY = from ? from.y : (to ? to.y - 46 : 0);
    const endX = to ? to.x : (from ? from.x : 0);
    const endY = to ? to.y : (from ? from.y - 46 : 0);

    items.push({
      key,
      value: to ? to.value : from.value,
      colorFrom: from ? from.color : null,
      colorTo: to ? to.color : null,
      heightFrom: from ? from.height : null,
      heightTo: to ? to.height : null,
      balanceFrom: from ? from.balanceFactor : null,
      balanceTo: to ? to.balanceFactor : null,
      startX,
      startY,
      endX,
      endY,
      startOpacity: from ? 1 : 0,
      endOpacity: to ? 1 : 0,
      leftKey: to ? to.leftKey : null,
      rightKey: to ? to.rightKey : null,
      existsInTarget: Boolean(to),
    });
  });

  return {
    progress: 0,
    items,
  };
}

function renderTreeTransitionSvg(transitionData, options = {}) {
  const p = Math.max(0, Math.min(1, transitionData.progress));
  const interpolatedNodes = transitionData.items.map((item) => {
    const x = item.startX + (item.endX - item.startX) * p;
    const y = item.startY + (item.endY - item.startY) * p;
    const opacity = item.startOpacity + (item.endOpacity - item.startOpacity) * p;
    return {
      key: item.key,
      value: item.value,
      x,
      y,
      opacity,
      color: p < 0.5 ? item.colorFrom : item.colorTo,
      height: p < 0.5 ? item.heightFrom : item.heightTo,
      balanceFactor: p < 0.5 ? item.balanceFrom : item.balanceTo,
      leftKey: item.leftKey,
      rightKey: item.rightKey,
      existsInTarget: item.existsInTarget,
    };
  });

  if (!interpolatedNodes.length) {
    return "<p class=\"viz-empty\">Estructura vacia.</p>";
  }

  const nodeMap = new Map(interpolatedNodes.map((node) => [node.key, node]));
  const targetNodes = interpolatedNodes.filter((node) => node.existsInTarget);
  const nullLeaves = buildNullLeafVisuals(targetNodes, options);
  let minX = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = 0;
  interpolatedNodes.forEach((node) => {
    minX = Math.min(minX, node.x);
    maxX = Math.max(maxX, node.x);
    maxY = Math.max(maxY, node.y);
  });
  nullLeaves.forEach((leaf) => {
    minX = Math.min(minX, leaf.x);
    maxX = Math.max(maxX, leaf.x);
    maxY = Math.max(maxY, leaf.y);
  });
  if (!Number.isFinite(minX)) {
    minX = 0;
  }
  const padX = 40;
  const offsetX = minX < padX ? (padX - minX) : 0;
  const svgWidth = maxX + offsetX + 90;
  const svgHeight = maxY + 70;

  const compare = comparisonHighlight(options.compareState);

  let svg = `<svg class="viz-tree-svg" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">`;

  interpolatedNodes.forEach((node) => {
    if (!node.existsInTarget) {
      return;
    }
    if (node.leftKey && nodeMap.has(node.leftKey)) {
      const left = nodeMap.get(node.leftKey);
      svg += `<line x1="${node.x + offsetX}" y1="${node.y + 18}" x2="${left.x + offsetX}" y2="${left.y - 18}" class="viz-tree-edge" />`;
    }
    if (node.rightKey && nodeMap.has(node.rightKey)) {
      const right = nodeMap.get(node.rightKey);
      svg += `<line x1="${node.x + offsetX}" y1="${node.y + 18}" x2="${right.x + offsetX}" y2="${right.y - 18}" class="viz-tree-edge" />`;
    }
  });

  nullLeaves.forEach((leaf) => {
    svg += `<line x1="${leaf.parentX + offsetX}" y1="${leaf.parentY + 18}" x2="${leaf.x + offsetX}" y2="${leaf.y - 14}" class="viz-tree-edge" />`;
  });

  interpolatedNodes.forEach((node) => {
    let nodeClass = "viz-tree-node";
    if (node.color === "RED") {
      nodeClass += " red";
    }
    if (node.color === "BLACK") {
      nodeClass += " black";
    }
    if (compare.visitedKeys.has(node.key)) {
      nodeClass += " sim-visited";
    }
    if (compare.activeKeys.has(node.key)) {
      nodeClass += " sim-active";
    }
    if (compare.unbalancedKeys.has(node.key)) {
      nodeClass += " sim-imbalanced";
    }
    nodeClass += getRotationNodeClass(node.key, options.rotationHint);

    svg += `<circle cx="${node.x + offsetX}" cy="${node.y}" r="24" class="${nodeClass}"${options.queryMemory ? ` data-heap-tree-index="${hEscape(node.key.replace("idx-", ""))}"` : ""}${options.insertMemory ? ` data-heap-tree-owner="${hEscape(options.memoryOwner)}"` : ""} style="opacity:${node.opacity};" />`;
    svg += `<text x="${node.x + offsetX}" y="${node.y + 6}" text-anchor="middle" class="viz-tree-text" style="opacity:${node.opacity};">${hEscape(node.value)}</text>`;

    if (options.showBalanceFactor) {
      const feClass = node.balanceFactor >= -1 && node.balanceFactor <= 1 ? "viz-tree-fe ok" : "viz-tree-fe bad";
      svg += `<text x="${node.x + offsetX + 25}" y="${node.y - 18}" class="${feClass}" style="opacity:${node.opacity};">fe:${hEscape(node.balanceFactor)}</text>`;
    } else if (node.height !== null && node.height !== undefined) {
      svg += `<text x="${node.x + offsetX + 20}" y="${node.y - 18}" class="viz-tree-height" style="opacity:${node.opacity};">h:${hEscape(node.height)}</text>`;
    }
  });

  nullLeaves.forEach((leaf) => {
    svg += `<circle cx="${leaf.x + offsetX}" cy="${leaf.y}" r="16" class="viz-tree-node black nil" />`;
    svg += `<text x="${leaf.x + offsetX}" y="${leaf.y + 4}" text-anchor="middle" class="viz-tree-text nil">NULL</text>`;
  });

  svg += "</svg>";
  return svg;
}

function renderHeapArray(arrayValues) {
  if (!arrayValues || !arrayValues.length) {
    return "<p class=\"viz-empty\">Arreglo vacio.</p>";
  }
  const chips = arrayValues
    .map((value, index) => `<span class="viz-array-chip">[${index}] ${hEscape(value)}</span>`)
    .join(" ");
  return `<div class="viz-array-wrap">${chips}</div>`;
}

function renderHeapArrayFrame(arrayValues, frame) {
  if (!arrayValues || !arrayValues.length) {
    return "<p class=\"viz-empty\">Arreglo vacio.</p>";
  }

  const visited = new Set(frame && Array.isArray(frame.visitedIndices) ? frame.visitedIndices : []);
  const active = new Set(frame && Array.isArray(frame.activeIndices) ? frame.activeIndices : []);

  const chips = arrayValues
    .map((value, index) => {
      let className = "viz-array-chip";
      if (visited.has(index)) {
        className += " sim-visited";
      }
      if (active.has(index)) {
        className += " sim-active";
      }
      return `<span class="${className}"${frame?.queryMemory ? ` data-heap-source-index="${index}"` : ""}${frame?.insertMemory ? ` data-heap-source-owner="${hEscape(frame.memoryOwner)}"` : ""}>[${index}] ${hEscape(value)}</span>`;
    })
    .join(" ");

  return `<div class="viz-array-wrap">${chips}</div>`;
}

function heapArrayToTreeNode(arrayValues, index = 0) {
  if (!arrayValues || index >= arrayValues.length) {
    return null;
  }
  return {
    value: arrayValues[index],
    heap_index: index,
    left: heapArrayToTreeNode(arrayValues, 2 * index + 1),
    right: heapArrayToTreeNode(arrayValues, 2 * index + 2),
  };
}

function buildHeapInsertFrames(previousArray, value) {
  if (!Number.isFinite(value)) {
    return [];
  }

  const array = [...previousArray];
  const frames = [];
  const visited = new Set();
  array.push(value);
  let current = array.length - 1;

  visited.add(current);
  frames.push({
    array: [...array],
    activeIndices: [current],
    visitedIndices: [...visited],
    note: `Se inserta ${value} al final y comienza a subir.`,
  });

  while (current > 0) {
    const parent = Math.floor((current - 1) / 2);
    visited.add(parent);
    visited.add(current);
    if (array[parent] <= array[current]) {
      frames.push({
        array: [...array],
        activeIndices: [parent, current],
        visitedIndices: [...visited],
        note: `Comparacion final: ${array[parent]} <= ${array[current]}.`,
      });
      break;
    }
    const oldParent = array[parent];
    const oldCurrent = array[current];
    [array[parent], array[current]] = [array[current], array[parent]];
    frames.push({
      array: [...array],
      activeIndices: [parent, current],
      visitedIndices: [...visited],
      note: `Intercambio ${oldParent} <-> ${oldCurrent}.`,
    });
    current = parent;
  }

  return frames;
}

function buildHeapExtractFrames(previousArray) {
  const array = [...previousArray];
  if (!array.length) {
    return [];
  }

  const frames = [];
  const visited = new Set([0]);
  const extracted = array[0];

  if (array.length === 1) {
    frames.push({
      array: [],
      activeIndices: [],
      visitedIndices: [0],
      note: `Se extrae la raiz ${extracted}. El monticulo queda vacio.`,
    });
    return frames;
  }

  const last = array.pop();
  array[0] = last;
  frames.push({
    array: [...array],
    activeIndices: [0],
    visitedIndices: [0],
    note: `Se extrae la raiz ${extracted}. El ultimo valor ${last} sube a la raiz.`,
  });

  let current = 0;
  while (true) {
    const left = 2 * current + 1;
    const right = 2 * current + 2;
    let smallest = current;

    if (left < array.length && array[left] < array[smallest]) {
      smallest = left;
    }
    if (right < array.length && array[right] < array[smallest]) {
      smallest = right;
    }

    if (smallest === current) {
      frames.push({
        array: [...array],
        activeIndices: [current],
        visitedIndices: [...visited],
        note: "La propiedad de min-heap ya se cumple.",
      });
      break;
    }

    visited.add(smallest);
    const oldCurrent = array[current];
    const oldSmallest = array[smallest];
    [array[current], array[smallest]] = [array[smallest], array[current]];
    frames.push({
      array: [...array],
      activeIndices: [current, smallest],
      visitedIndices: [...visited],
      note: `Intercambio ${oldCurrent} <-> ${oldSmallest} para restaurar el heap.`,
    });
    current = smallest;
  }

  return frames;
}

function buildHeapOperationFrames(operationName, payload, previousArray) {
  if (!Array.isArray(previousArray)) {
    return [];
  }
  if (operationName === "insertar") {
    const rawValue = payload && payload.value !== undefined ? payload.value : null;
    const value = Number(rawValue);
    return buildHeapInsertFrames(previousArray, value);
  }
  if (operationName === "extraer_raiz") {
    return buildHeapExtractFrames(previousArray);
  }
  return [];
}

function formatHierResult(lastExecution) {
  if (!lastExecution || lastExecution.result === undefined) {
    return "";
  }

  const result = lastExecution.result;
  if (Array.isArray(result)) {
    return `<p><strong>Resultado:</strong> ${hEscape(result.join(" -> "))}</p>`;
  }
  if (typeof result === "boolean") {
    return `<p><strong>Resultado:</strong> ${result ? "Verdadero" : "Falso"}</p>`;
  }
  if (result === null) {
    return "";
  }
  return `<p><strong>Resultado:</strong> ${hEscape(JSON.stringify(result))}</p>`;
}

function layoutHierMemoryGraph(state) {
  const heap = state.heap_nodes || [], byId = new Map(heap.map(node => [node.id,node]));
  const visited = new Set(), active = new Set(); let safe = true;
  const incoming = new Map();
  for (const node of heap) for (const child of [node.left,node.right]) if (byId.has(child)) incoming.set(child,(incoming.get(child)||0)+1);
  if ([...incoming.values()].some(count => count > 1) || (state.head !== "NULL" && incoming.has(state.head))) safe = false;
  function validate(id) {
    if (id === "NULL") return;
    if (!byId.has(id) || active.has(id)) { safe = false; return; }
    if (visited.has(id)) return;
    visited.add(id); active.add(id);
    const node = byId.get(id); validate(node.left); validate(node.right); active.delete(id);
  }
  if (state.head !== "NULL") validate(state.head);
  const reachable = new Set(visited);
  for (const node of heap) if (!visited.has(node.id)) validate(node.id);
  const positions = new Map(); let slot = 0, maxDepth = 0;
  function place(id, depth) {
    if (id === "NULL") return;
    const node = byId.get(id); place(node.left,depth+1);
    positions.set(id,{x:48+(slot++)*88,y:42+depth*64});maxDepth=Math.max(maxDepth,depth);
    place(node.right,depth+1);
  }
  if (safe) {
    if (state.head !== "NULL") place(state.head,0);
    const detachedDepth=maxDepth+2;
    for (const node of heap) if (!positions.has(node.id) && !incoming.has(node.id)) place(node.id,detachedDepth);
  }
  const graph=heap.map((node,index)=>({...node,key:node.id,...(safe?positions.get(node.id):{x:48+(index%4)*120,y:42+Math.floor(index/4)*100}),leftKey:node.left,rightKey:node.right,parentReference:node.parent,balanceFactor:node.balance_factor}));
  return {graph,safe,detached:heap.filter(node=>!reachable.has(node.id)).map(node=>node.id),label:safe?(state.head === "NULL"?"Sin raíz publicada: reservas desconectadas.":"Árbol de enlaces observados; no certifica el invariante."):"Diagrama de memoria; no árbol válido todavía. Enlaces indeterminados o transitorios conservados."};
}

function renderHierState(
  modelId,
  state,
  container,
  lastExecution,
  transitionData,
  compareState,
  rotationVisualHint,
  rotationTextHint,
  heapFrame,
) {
  if (!state || !container) {
    return;
  }

  const memoryDetailsOpen = Boolean(container.querySelector?.(".hier-memory-call-detail")?.open);
  const treeOptions = {
    fitBounds: true,
    showBalanceFactor: modelId === "avl",
    showNullLeaves: modelId === "red_black",
    queryMemory: Boolean(state.heap_query_model),
    insertMemory: Boolean(state.heap_insert_model || state.heap_extract_model),
    memoryOwner: state.heap_data_reference,
    compareState,
    rotationHint: rotationVisualHint,
  };

  let html = `<div class="viz-canvas${modelId === "binary_heap" ? " heap-classroom-canvas" : ""}${(state.abb_traversal_model || state.abb_read_model) ? " abb-traversal-canvas" : ""}"><div class="viz-meta"><strong>${hEscape(state.title)}</strong> | Tamano: ${hEscape(state.size ?? 0)}</div>`;

  if ((state.abb_validate_model || state.avl_validate_model) && state.wrapper_result === null) html += "<p data-abb-validation-pending>Validacion pendiente: aun no retorna el llamador.</p>";
  if (state.rbt_validate_model) html += `<p data-rbt-validator-contract>${hEscape(state.validator_contract)}; resultado: ${state.wrapper_result === null ? "pendiente" : state.wrapper_result ? "correcto" : "incorrecto"}</p>`;
  if (state.avl_validate_model && typeof state.height_balance_result === "boolean") html += `<p data-avl-height-result>Equilibrio por alturas (C): ${state.height_balance_result ? "correcto" : "incorrecto"}. No comprueba orden ABB ni FE almacenado.</p>`;
  if (state.avl_validate_model && state.wrapper_result !== null) html += `<p data-avl-backend-validation>Validacion backend (orden y equilibrio): ${state.backend_validation ? "OK" : "ERROR"}</p>`;
  if (typeof state.validation === "boolean") {
    html += `<div class="viz-validation">${modelId === "red_black" ? "Validar reglas RN y enlaces" : "Validacion"}: ${state.validation ? "OK" : "ERROR"}</div>`;
  }
  if (modelId === "avl") {
    html += "<div class=\"viz-meta\">Regla AVL: cada nodo debe tener fe en {-1, 0, 1}.</div>";
    if (compareState && compareState.rotationMessage) {
      html += `<div class="viz-rotation-live">${hEscape(compareState.rotationMessage)}</div>`;
    }
    const rotationText = rotationHintText(rotationTextHint);
    if (rotationText) {
      html += `<div class="viz-rotation-note">${hEscape(rotationText)}</div>`;
    }
  }
  if (modelId === "red_black") {
    html += "<div class=\"viz-meta\">RN: raíz negra; rojos separados; altura negra igual.</div>";
    if (compareState && Array.isArray(compareState.rnEvents) && compareState.rnEvents.length) {
      html += "<div class=\"viz-sim-note\"><strong>Cambios por reglas RN:</strong><ul>";
      compareState.rnEvents.forEach((eventText) => {
        html += `<li>${hEscape(eventText)}</li>`;
      });
      html += "</ul></div>";
    }
    if (H_SHOW_RN_TIMELINE && compareState && Array.isArray(compareState.rnTimeline) && compareState.rnTimeline.length) {
      const currentIndex = Number.isInteger(compareState.rnTimelineIndex) ? compareState.rnTimelineIndex : -1;
      html += "<div class=\"viz-rn-timeline\"><strong>Linea de tiempo RN (paso a paso)</strong><ol>";
      compareState.rnTimeline.forEach((entry, idx) => {
        const stage = entry && entry.stage ? String(entry.stage) : "Ejecucion";
        const note = entry && entry.note ? String(entry.note) : "Paso del algoritmo.";
        const cls = idx === currentIndex ? " class=\"is-current\"" : "";
        html += `<li${cls}><span class=\"rn-stage\">${hEscape(stage)}:</span> ${hEscape(note)}</li>`;
      });
      html += "</ol></div>";
    }
  }

  if (state.heap_query_model) heapFrame = {queryMemory: true, insertMemory: Boolean(state.heap_insert_model || state.heap_extract_model), memoryOwner: state.heap_data_reference, array: state.array, visitedIndices: [], activeIndices: (state.heap_insert_model || state.heap_extract_model) ? state.heap_active_indices : Number.isInteger(state.active_copy_index) ? [state.active_copy_index] : []};
  if (modelId === "binary_heap" || state.kind === "heap") {
    const heapArray = heapFrame && Array.isArray(heapFrame.array) ? heapFrame.array : (state.array || []);
    const heapRoot = heapArrayToTreeNode(heapArray, 0);
    const heapCompareState = heapFrame ? {
      pathKeys: (heapFrame.visitedIndices || []).map((index) => `idx-${index}`),
      index: Math.max(0, (heapFrame.visitedIndices || []).length - 1),
      activeKeys: (heapFrame.activeIndices || []).map((index) => `idx-${index}`),
    } : treeOptions.compareState;
    const insertSuspended = Boolean(state.heap_insert_model && state.heap_data_reference.startsWith("indeterminado"));
    if (state.heap_extract_model) html += `<details class="hier-diagram-note"><summary>Arreglo y árbol: estado de esta instrucción</summary><p data-heap-extract-views>Ambas vistas siguen el prefijo logico de A1: cantidad C ${state.size}. La memoria conserva ${state.heap_written} celdas observadas, incluida la cola fuera de cantidad. Capacidad ${state.capacity}; extraer no libera ni reduce el buffer.</p></details>`;
    if (state.heap_insert_model) html += `<details class="hier-diagram-note"><summary>Arreglo y árbol: estado de esta instrucción</summary><p data-heap-insert-views>Ambas vistas siguen las celdas escritas de ${hEscape(state.heap_data_reference)}, no afirman cantidad futura. Cantidad C: ${state.size}; celdas escritas: ${state.heap_written}. ${state.heap_pending_index!==null?`<span data-heap-insert-pending="${state.heap_pending_index}">datos[${state.heap_pending_index}] escrito, aun fuera de cantidad hasta m-&gt;cantidad++.</span>`:""}</p></details>`;
    html += "<h4>Representacion en arreglo</h4>";
    html += insertSuspended ? "<p data-heap-drawing-suspended>Lectura de datos suspendida hasta publicar el nuevo buffer; no es un heap vacio.</p>" : renderHeapArrayFrame(heapArray, heapFrame);
    if (heapFrame && heapFrame.note) {
      html += `<p class="viz-sim-note">${hEscape(heapFrame.note)}</p>`;
    }
    html += "<h4>Representacion en arbol</h4>";
    html += insertSuspended ? "<p data-heap-drawing-suspended>Arbol suspendido: el puntero previo termino su vida; el temporal nuevo aparece en memoria.</p>" : transitionData
      ? renderTreeTransitionSvg(transitionData, { ...treeOptions, compareState: heapCompareState })
      : drawTreeSvgFromNodes(flattenTree(heapRoot), { ...treeOptions, compareState: heapCompareState });
  } else {
    if (state.rbt_clear_model || state.rbt_insert_model || state.rbt_delete_model || state.rbt_validation_graph) {
      const memoryGraph = layoutHierMemoryGraph(state); const graph = memoryGraph.graph;
      html += '<details class="hier-diagram-note"><summary>Reservas y enlaces observados; no certifica RN.</summary>' + (state.rbt_insert_model ? '<p data-rbt-insert-graph>Reservas vivas: '+hEscape(state.heap_count)+'; alcanzables en la proyeccion: '+hEscape(state.reachable_count)+'. Identidades y campos C escritos; sin inicializar no significa cero. Las rotaciones pueden tener enlaces/ciclos transitorios. NULL es un enlace realmente NULL, no una reserva NIL. No se certifica aqui un rojo-negro final.</p>' : '<p data-rbt-clear-graph>Reservas vivas y colores registrados. NULL representa solo un enlace realmente NULL; no es una reserva NIL. Los enlaces inutilizables conservan su identidad historica en las tarjetas. La proyeccion parcial no certifica un arbol rojo-negro completo.</p>') + '</details>';
      html += `<div class="hier-memory-projection">${hEscape(memoryGraph.label)}${memoryGraph.detached.length ? ` Reservas aparte: ${hEscape(memoryGraph.detached.join(", "))}.` : ""}</div>`;
      html += drawTreeSvgFromNodes(graph,{...treeOptions,showNullLeaves:false,rbtClearMemory:true,rbtInsertMemory:!!(state.rbt_insert_model||state.rbt_delete_model)});
    } else if (state.avl_insert_model || state.avl_delete_model) {
      const memoryGraph = layoutHierMemoryGraph(state); const graph = memoryGraph.graph;
      html += '<details class="hier-diagram-note"><summary>Reservas y enlaces observados; no certifica AVL.</summary>' + ('<p data-avl-insert-graph>Reservas vivas e identidades estables, incluso desconectadas. Enlaces y FE observados: la reconexion transitoria no certifica un AVL terminado.</p>') + '</details>';
      html += `<div class="hier-memory-projection">${hEscape(memoryGraph.label)}${memoryGraph.detached.length ? ` Reservas aparte: ${hEscape(memoryGraph.detached.join(", "))}.` : ""}</div>`;
      html += drawTreeSvgFromNodes(graph,{...treeOptions,showNullLeaves:false,avlInsertionMemory:true});
    } else html += transitionData
      ? renderTreeTransitionSvg(transitionData, treeOptions)
      : drawTreeSvgFromNodes(flattenTree(state.root), treeOptions);
  }

  const heapMemory = renderHeapQueryMemory(state);

  if (state.traversals) {
    html += "<details class=\"viz-traversals hier-traversal-summary\"><summary>Recorridos de la estructura</summary>";
    Object.keys(state.traversals).forEach((name) => {
      html += `<p><strong>${hEscape(name)}:</strong> ${hEscape(JSON.stringify(state.traversals[name]))}</p>`;
    });
    html += "</details>";
    const lastResult = state.rbt_read_model ? "" : state.avl_validate_model ? "" : (state.abb_validate_model || state.avl_validate_model) && state.wrapper_result === null ? "" : formatHierResult(lastExecution);
    if (lastResult) {
      html += lastResult;
    }
  }

  html += "</div>" + heapMemory;
  if (state.abb_insert_model || state.abb_traversal_model || state.abb_read_model) {
    const memoryNodes = state.heap_nodes || [];
    const liveIds = new Set(memoryNodes.map(node => node.id));
    const focusId = [...(state.tree_frames || [])].reverse().flatMap(frame => Object.values({...frame.parameters, ...frame.locals})).find(target => liveIds.has(target));
    const displayNodes = [...memoryNodes].sort((a, b) => Number(b.id === focusId) - Number(a.id === focusId));
    const fields = (node) => `<span>valor: <strong>${hEscape(node.value)}</strong></span> · <span>izquierdo: <code>${hEscape(node.left)}</code></span> · <span>derecho: <code>${hEscape(node.right)}</code></span>`;
    html += `<section class="abb-instruction-memory"><p data-abb-head="${hEscape(state.head)}"><strong>Raiz del llamador:</strong> ${hEscape(state.head)}</p><p>Identidades simbólicas, no direcciones reales.</p>`;
    const callerDetail = state.caller_frame ? state.caller_frame.description ? `<div data-abb-caller><code>${hEscape(state.caller_frame.function)}</code>: ${hEscape(state.caller_frame.description)}</div>` : `<div data-abb-caller><code>ejecutar_insercion</code>: arbol (ABBNodo **) → &amp;raiz; *arbol → ${hEscape(state.head)}</div>` : "";
    const frameDetails = (state.tree_frames || []).map((f,i,all) => `<div class="hier-stack-frame" data-abb-frame="${hEscape(f.id)}" data-abb-depth="${f.depth}"><strong>${hEscape(f.function)}#${hEscape(f.id)}</strong> · ${i===all.length-1?"activo":"suspendido"}<br>${Object.entries({...f.parameters,...f.locals}).map(([name,target])=>`<span data-abb-alias="${name}" data-abb-alias-frame="${f.id}" data-abb-alias-type="${(state.rbt_delete_model?['key','es_izq']:['valor','x','altIzq','altDer','bhIzq','bhDer','fe','hay_minimo','minimo','hay_maximo','maximo','tmp','feL','feR','dato','key','es_izq','tieneMin','minimo','tieneMax','maximo']).includes(name)?'int':state.rbt_delete_model&&name==='y_color_original'?'char':((state.avl_insert_model && ['raiz','r'].includes(name)) || (state.avl_delete_model && (name==='r' || (name==='raiz' && ['avl_eliminar','rebalancearTrasEliminar'].includes(f.function)))))?'AVL *':(state.rbt_insert_model||state.rbt_delete_model)&&['arbol','r','root'].includes(name)?'RBT *':state.rbt_read_model?'RBT':state.avl_read_model?'AVL':'ABBNodo *'}" data-abb-alias-target="${hEscape(target)}" data-abb-alias-usable="${(state.rbt_clear_model||state.rbt_delete_model) ? !String(target).includes("valor indeterminado") : !state.avl_delete_model || !(state.freed_nodes||[]).some(n=>n.id===target)}">${name} (${(state.rbt_delete_model?['key','es_izq']:['valor','x','altIzq','altDer','bhIzq','bhDer','fe','hay_minimo','minimo','hay_maximo','maximo','tmp','feL','feR','dato','key','es_izq','tieneMin','minimo','tieneMax','maximo']).includes(name)?'int':state.rbt_delete_model&&name==='y_color_original'?'char':((state.avl_insert_model && ['raiz','r'].includes(name)) || (state.avl_delete_model && (name==='r' || (name==='raiz' && ['avl_eliminar','rebalancearTrasEliminar'].includes(f.function)))))?'AVL *':(state.rbt_insert_model||state.rbt_delete_model)&&['arbol','r','root'].includes(name)?'RBT *':state.rbt_read_model?'RBT':state.avl_read_model?'AVL':'ABBNodo *'}) → ${hEscape(target)}${state.avl_delete_model && (state.freed_nodes||[]).some(n=>n.id===target)?" (vida terminada; no desreferenciar)":""}</span>`).join('<br>')}${f.expression?`<p data-abb-expression-frame="${f.id}">Operandos de expresión (no variables C): izquierdo = ${hEscape(f.expression.left)}; derecho = ${hEscape(f.expression.right)}. Orden elegido: ${hEscape(state.operand_evaluation_order)}; C permite otro orden.</p>`:''}</div>`).join('');
    const retiredNote = (state.abb_clear_model || state.abb_delete_model || state.avl_delete_model || state.rbt_delete_model) ? '<p>El SVG representa reservas vivas. Enlaces a reservas terminadas son identidades históricas inutilizables; esto no asigna NULL en C.</p>' : '';
    if (state.avl_extreme_model) html += `<p data-avl-output data-avl-output-initialized="${state.caller_output.initialized}" data-avl-output-value="${state.caller_output.initialized?hEscape(state.caller_output.value):'sin inicializar'}">salida (int del llamador): ${state.caller_output.initialized?hEscape(state.caller_output.value):'sin inicializar'}; no es una reserva AVL.</p>`;
    html += '<h4>Reservas vivas y sus enlaces</h4>' + displayNodes.map(node => `<div class="hier-stack-frame${node.id === focusId ? " is-current-memory" : ""}" data-abb-node="${node.id}" data-abb-status="${node.status}" data-abb-value="${hEscape(node.value)}" data-abb-left="${hEscape(node.left)}" data-abb-right="${hEscape(node.right)}"><strong>${node.id}</strong> · ${node.status==='linked'?'alcanzable desde la raiz':'desconectado, aun vivo'}<br>${fields(node)}${state.rbt_read_model?` | padre: <code>${hEscape(node.parent)}</code> | color: ${hEscape(({BLACK:"negro",RED:"rojo"})[node.color] || node.color)}`:state.avl_read_model?` · padre: <code>${hEscape(node.parent)}</code> · FE: ${hEscape(node.balance_factor)}`:""}</div>`).join('') + `<details class="hier-memory-call-detail"><summary>Pila de llamadas: ${(state.tree_frames || []).length} marco(s)</summary>${callerDetail}${frameDetails}${retiredNote}</details></section>`;
  }
  if(state.abb_clear_model || state.abb_delete_model || state.avl_delete_model || state.rbt_delete_model) html += `<details class="hier-retired-memory"><summary>Reservas terminadas: ${(state.freed_nodes || []).length} (histórico)</summary>`+(state.freed_nodes||[]).map(n=>`<div data-abb-retired-node="${n.id}" data-abb-retired-value="${n.value}">${hEscape(n.id)}: vida terminada. Valor registrado antes de free: ${hEscape(n.value)}. No es un objeto vivo ni un puntero utilizable.</div>`).join('') + "</details>";
  container.innerHTML = html;
  const memoryDetails = container.querySelector?.(".hier-memory-call-detail");
  if (memoryDetails) memoryDetails.open = memoryDetailsOpen;
}

function renderHeapClearMemory(state) {
  let html = `<section class="abb-instruction-memory" data-heap-clear-memory${state.heap_insert_model?" data-heap-insert-memory":""}><h4>Vida de memoria durante ${state.heap_insert_model?"Insertar":state.heap_extract_model?"Extraer raiz":"Limpiar"}</h4><p data-heap-clear-storage data-heap-count="${state.size}" data-heap-capacity="${state.capacity}" data-heap-reference="${hEscape(state.heap_data_reference)}">M1: datos ${hEscape(state.heap_data_reference)}; cantidad ${state.size}; capacidad ${state.capacity}. Identidades simbólicas; nunca leer un buffer liberado.</p>`;
  if (state.heap_extract_model) html += `<p data-heap-extract-output data-heap-output-initialized="${state.caller_output.initialized}" data-heap-output-value="${state.caller_output.initialized?hEscape(state.caller_output.value):'sin inicializar'}">R1 salida int: ${state.caller_output.initialized?hEscape(state.caller_output.value):'sin inicializar'}; independiente del bool. La memoria A1 permanece viva, incluyendo la cola fuera de cantidad.</p>`;
  const framesHtml = (state.query_frames || []).map((f,i,all) => `<div class="hier-stack-frame" data-heap-frame="${f.id}" data-heap-function="${hEscape(f.function)}"><strong>${hEscape(f.function)}</strong>: ${i===all.length-1?'activo':'suspendido'}<br>${Object.entries({...f.parameters,...f.locals}).map(([name,value])=>`<span data-heap-local="${name}" data-heap-local-frame="${f.id}" data-heap-local-value="${hEscape(value)}">${name}: ${hEscape(value)}</span>`).join('<br>')}</div>`).join('');
  for (const object of state.heap_allocations || []) {
    if (!object.live) continue;
    html += `<div data-heap-clear-allocation="${object.id}" data-heap-clear-capacity="${object.capacity}"><strong>${object.id}: buffer vivo, capacidad ${object.capacity}</strong><div class="viz-array-wrap">${object.cells.map(cell=>`<span class="viz-array-chip${state.heap_extract_model && (state.heap_active_indices || []).includes(cell.index)?' sim-active':''}" data-heap-clear-cell="${cell.index}" data-heap-clear-owner="${object.id}" data-heap-initialized="${cell.initialized===null?'desconocido':cell.initialized}" data-heap-value="${cell.initialized===true?hEscape(cell.value):cell.initialized===false?'sin inicializar':'no observado'}">[${cell.index}] ${cell.initialized===true?hEscape(cell.value):cell.initialized===false?'sin inicializar':'no observado'}</span>`).join(' ')}</div></div>`;
  }
  for (const object of state.heap_retired || []) html += `<div data-heap-clear-retired="${object.id}"><strong>${object.id}: vida terminada</strong><p>Registro previo a ${state.heap_insert_model?"realloc exitoso":"free"}; no es memoria accesible. No se evalua el puntero indeterminado.</p>${object.cells.filter(cell=>cell.initialized===true).map(cell=>`<span data-heap-clear-retired-index="${cell.index}" data-heap-retired-value="${hEscape(cell.value)}">[${cell.index}] ${hEscape(cell.value)}</span>`).join(' ')}</div>`;
  return html+`<details class="hier-memory-call-detail"><summary>Pila de llamadas: ${(state.query_frames || []).length} marco(s)</summary>${framesHtml}</details></section>`;
}

function renderHeapQueryMemory(state) {
  if (state.heap_clear_model || state.heap_insert_model || state.heap_extract_model) return renderHeapClearMemory(state);
  if (!state.heap_query_model) return "";
  let html = `<section class="abb-instruction-memory" data-heap-query-memory><h4>Memoria de la consulta</h4><p data-heap-storage="A1" data-heap-count="${state.size}" data-heap-capacity="${state.capacity}">M1: datos apunta a A1; cantidad ${state.size}; capacidad ${state.capacity}. A1 es el arreglo original; B1 es destino independiente. IDs simbólicos.</p>`;
  if (state.query_operation === "raiz" && state.caller_output) html += `<p data-heap-output data-heap-output-initialized="${state.caller_output.initialized}" data-heap-output-value="${state.caller_output.initialized?hEscape(state.caller_output.value):'sin inicializar'}">salida (int externo): ${state.caller_output.initialized?hEscape(state.caller_output.value):'sin inicializar'}; distinto del bool retornado.</p>`;
  const framesHtml = (state.query_frames || []).map((f,i,all) => `<div class="hier-stack-frame" data-heap-frame="${f.id}" data-heap-function="${hEscape(f.function)}"><strong>${hEscape(f.function)}</strong>: ${i===all.length-1?'activo':'suspendido'}<br>${Object.entries({...f.parameters,...f.locals}).map(([name,value])=>`<span data-heap-local="${name}" data-heap-local-frame="${f.id}" data-heap-local-value="${hEscape(value)}">${name}: ${hEscape(value)}</span>`).join('<br>')}</div>`).join('');
  if (state.destination) html += `<div data-heap-destination="B1" data-heap-destination-capacity="${state.destination.capacity}"><strong>B1: destino independiente vivo</strong><div class="viz-array-wrap">${state.destination.cells.map(cell=>`<span class="viz-array-chip${state.active_copy_index===cell.index?' sim-active':''}" data-heap-destination-index="${cell.index}" data-heap-initialized="${cell.initialized}" data-heap-value="${cell.initialized?hEscape(cell.value):'sin inicializar'}">[${cell.index}] ${cell.initialized?hEscape(cell.value):'sin inicializar'}</span>`).join(' ')}</div></div>`;
  if (state.retired_destination) html += `<div data-heap-retired="B1"><strong>B1: vida terminada</strong><p>Registros anteriores a free; no es memoria viva ni se leen punteros indeterminados.</p>${state.retired_destination.cells.map(cell=>`<span data-heap-retired-index="${cell.index}" data-heap-retired-value="${hEscape(cell.value)}">[${cell.index}] ${hEscape(cell.value)}</span>`).join(' ')}</div>`;
  return html+`<details class="hier-memory-call-detail"><summary>Pila de llamadas: ${(state.query_frames || []).length} marco(s)</summary>${framesHtml}</details></section>`;
}

function showHierMessage(text, success) {
  const box = hById("message-box");
  if (!box) {
    return;
  }
  box.textContent = text || "";
  box.className = success ? "message ok" : "message error";
}

function updateHierDidacticPanel(model, operationName) {
  window.ContextualHelp?.operation("hier", model, operationName);
  const recordBox = hById("tad-record");
  const pseudoTitle = hById("op-pseudocode-title");
  const pseudoBox = hById("op-pseudocode");
  if (!recordBox || !pseudoTitle || !pseudoBox) {
    return;
  }

  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const codeTitle = didactic.code_title || "Seudocodigo";
  const fallback = didactic.default_operation || "Contenido didactico no disponible para esta operacion.";
  const selectedOp = operationName || "";
  const selectedMeta = (model.operations || []).find((item) => item.name === selectedOp);
  const selectedLabel = selectedMeta ? selectedMeta.label : selectedOp;

  renderHierDidacticCode(recordBox, didactic.record || "Estructura no documentada.", codeTitle);
  pseudoTitle.textContent = selectedLabel ? `${codeTitle}: ${selectedLabel}` : codeTitle;
  if (model.id === "avl" && ["maximo", "inorden", "validar"].includes(selectedOp)) pseudoTitle.textContent += " — Auxiliar de la app; incluido en main.c";
  renderHierDidacticCode(pseudoBox, opMap[selectedOp] || fallback, codeTitle);
  enhanceHierCodeNavigation(null);
}

function summarizeHierPayload(payload) {
  if (!payload || typeof payload !== "object") {
    return "";
  }
  const parts = Object.entries(payload)
    .filter(([, value]) => String(value).trim() !== "")
    .map(([key, value]) => `${key}=${value}`);
  return parts.join(", ");
}

function extractHierSubroutineName(pseudoCode, fallback) {
  if (!pseudoCode) {
    return fallback;
  }
  const firstLine = String(pseudoCode).split("\n").find((line) => String(line).trim()) || "";
  const match = firstLine.match(/(?:SubProceso|Funcion|Procedimiento|Proceso)\s+([A-Za-z_][A-Za-z0-9_]*)/i);
  if (match && match[1]) {
    return match[1];
  }
  return fallback;
}

function getHierSubroutineName(model, operationName, fallback) {
  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const pseudoCode = opMap[operationName] || "";
  return extractHierSubroutineName(pseudoCode, fallback || operationName || "Operacion");
}

function createHierHistoryEntry(subroutine, payloadText, resultText, operationName, payloadRaw, options) {
  const opts = options && typeof options === "object" ? options : {};
  const normalizedResult = resultText || "-";
  return {
    subroutine: subroutine || "Operacion",
    payload: payloadText || "-",
    result: normalizedResult,
    finalResult: normalizedResult,
    pendingTrace: Boolean(opts.pendingTrace),
    success: opts.success !== false,
    operation: operationName || "",
    payloadRaw: payloadRaw && typeof payloadRaw === "object" ? { ...payloadRaw } : {},
  };
}

function getHierEntryVisibleResult(entry) {
  if (!entry || typeof entry === "string") {
    return "";
  }
  if (entry.pendingTrace) {
    return "";
  }
  const finalResult = Object.prototype.hasOwnProperty.call(entry, "finalResult")
    ? entry.finalResult
    : entry.result;
  return String(finalResult || "").trim();
}

function abbMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = Object.prototype.hasOwnProperty.call(payload, "value") ? String(payload.value).trim() : "";

  if (entry.operation === "insertar") {
    return `arbol = abb_insertar(arbol, ${value || "0"});`;
  }
  if (entry.operation === "eliminar") {
    return `arbol = abb_eliminar(arbol, ${value || "0"});`;
  }
  if (entry.operation === "buscar") {
    return `ABBNodo *encontrado_${index} = abb_buscar(arbol, ${value || "0"});`;
  }
  if (entry.operation === "minimo") {
    return `ABBNodo *minimo_${index} = abb_encontrarMinimo(arbol);`;
  }
  if (entry.operation === "maximo") {
    return `ABBNodo *maximo_${index} = abb_encontrarMaximo(arbol);`;
  }
  if (entry.operation === "altura") {
    return `int altura_${index} = abb_altura(arbol);`;
  }
  if (entry.operation === "contar_hojas") {
    return `int hojas_${index} = abb_contarHojas(arbol);`;
  }
  if (entry.operation === "inorden") {
    return "abb_inorden(arbol);";
  }
  if (entry.operation === "preorden") {
    return "abb_preorden(arbol);";
  }
  if (entry.operation === "postorden") {
    return "abb_postorden(arbol);";
  }
  if (entry.operation === "validar") {
    return `int valido_${index} = abb_validar_rango(arbol, 0, 0, 0, 0);`;
  }
  if (entry.operation === "limpiar") {
    return "abb_liberarArbol(arbol); arbol = NULL;";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function hAVLMainIntegerValue(entry) {
  // Preserve decimal integer semantics for leading zeros without Number rounding.
  return BigInt(String(entry?.payloadRaw?.value ?? "0").trim()).toString();
}

function avlMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = hAVLMainIntegerValue(entry);

  if (entry.operation === "insertar") {
    return `avl_insertar(&arbol, ${value || "0"});`;
  }
  if (entry.operation === "eliminar") {
    return `avl_eliminar(&arbol, ${value || "0"});`;
  }
  if (entry.operation === "buscar") {
    return `AVL encontrado_${index} = avl_buscar(arbol, ${value || "0"});`;
  }
  if (entry.operation === "minimo") {
    return `AVL minimo_${index} = avl_minimo(arbol);`;
  }
  if (entry.operation === "maximo") {
    return `AVL maximo_${index} = avl_maximo(arbol);`;
  }
  if (entry.operation === "altura") {
    return `int altura_${index} = avl_altura(arbol);`;
  }
  if (entry.operation === "inorden") {
    return "avl_inorden(arbol);";
  }
  if (entry.operation === "validar") {
    return `int valido_${index} = avl_validar_fes(arbol);`;
  }
  if (entry.operation === "limpiar") {
    return "avl_liberarAVL(arbol); arbol = NULL;";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function redBlackMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = hAVLMainIntegerValue(entry);

  if (entry.operation === "insertar") {
    return `rbt_insertar(&arbol, ${value || "0"});`;
  }
  if (entry.operation === "eliminar") {
    return `rbt_eliminar(&arbol, ${value || "0"});`;
  }
  if (entry.operation === "buscar") {
    return `RBT encontrado_${index} = rbt_buscar(arbol, ${value || "0"});`;
  }
  if (entry.operation === "inorden") {
    return "rbt_inorden(arbol);";
  }
  if (entry.operation === "altura") {
    return `int altura_${index} = rbt_altura(arbol);`;
  }
  if (entry.operation === "validar") {
    return `int valido_${index} = rbt_validar(arbol);`;
  }
  if (entry.operation === "limpiar") {
    return "rbt_liberar(arbol); arbol = NULL;";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function binaryHeapMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = hAVLMainIntegerValue(entry);

  if (entry.operation === "insertar") {
    return `bool ok_${index} = monticulo_insertar(&monticulo, ${value || "0"});`;
  }
  if (entry.operation === "extraer_raiz") {
    return `int extraido_${index}; bool ok_${index} = monticulo_extraer_raiz(&monticulo, &extraido_${index});`;
  }
  if (entry.operation === "raiz") {
    return `int raiz_${index}; bool ok_${index} = monticulo_raiz(&monticulo, &raiz_${index});`;
  }
  if (entry.operation === "a_lista") {
    return `int cantidad_${index} = monticulo_cantidad(&monticulo);
    int *buffer_${index} = cantidad_${index} > 0 ? malloc((size_t)cantidad_${index} * sizeof *buffer_${index}) : NULL;
    if (cantidad_${index} > 0 && buffer_${index} == NULL) { monticulo_destruir(&monticulo); return EXIT_FAILURE; }
    int usados_${index} = monticulo_copiar_valores(&monticulo, buffer_${index}, cantidad_${index});
    printf("A LISTA: [");
    for (int i_${index} = 0; i_${index} < usados_${index}; i_${index}++) printf("%s%d", i_${index} ? ", " : "", buffer_${index}[i_${index}]);
    printf("]\\n");
    free(buffer_${index});`;
  }
  if (entry.operation === "limpiar") {
    return "monticulo_destruir(&monticulo); monticulo_inicializar(&monticulo, MONTICULO_MIN, 16);";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function buildHierMainCode(modelId, history, didactic) {
  const lines = [];
  if (modelId === "abb") lines.push('#include <stdio.h>', '#include "tad_abb.h"', "");
  if (modelId === "abb" && history.some(entry => entry && entry.success !== false && ["contar_hojas", "validar"].includes(entry.operation))) {
    const source = didactic || window.HIER_VIEW_MODEL?.didactic || {};
    for (const op of ["contar_hojas", "validar"]) {
      if (!history.some(entry => entry && entry.success !== false && entry.operation === op)) continue;
      const helper = source.operations?.[op];
      if (!helper) throw new Error(`Falta el auxiliar canonico ABB de ${op}.`);
      lines.push(helper, "");
    }
    lines.push("/**", " * @brief Reproduce operaciones exitosas del historial ABB y calcula sus consultas.",
      " * @return 0 al terminar la secuencia de operaciones.",
      " * @note Compilar junto a tad_abb.c. Los auxiliares anteriores pertenecen a este",
      " * programa, no a la API publica del C/H descargado.", " */");
  }
  if (modelId === "avl") {
    const source = didactic || window.HIER_VIEW_MODEL?.didactic || {};
    lines.push('#include <stdio.h>', '#include <stddef.h>', '#include "tad_avl.h"', "");
    const definitions = [
      ["maximo", "Calcula el maximo mediante el auxiliar mostrado por la aplicacion.", "raiz", "Raiz consultada; NULL admitido.", "Alias prestado al maximo o NULL."],
      ["inorden", "Imprime el recorrido inorden ascendente del historial.", "nodo", "Raiz consultada; NULL admitido.", null],
      ["validar", "Comprueba equilibrio por alturas con el auxiliar mostrado.", "nodo", "Raiz consultada; NULL admitido.", "1 si todas las diferencias de alturas estan en el rango permitido; 0 en otro caso."],
    ];
    definitions.forEach(([op, brief, parameter, meaning, result]) => {
      if (!history.some(entry => entry && entry.success !== false && entry.operation === op)) return;
      const helper = source.operations?.[op];
      if (!helper) throw new Error(`Falta el auxiliar canonico AVL de ${op}.`);
      if (helper.trimStart().startsWith("/**")) { lines.push(helper, ""); return; }
      lines.push("/**", ` * @brief ${brief}`, ` * @param ${parameter} ${meaning}`);
      if (result) lines.push(` * @return ${result}`);
      lines.push(" * @note Auxiliar de este programa; no es una exportacion del C/H descargable.", " */", helper, "");
    });
    lines.push("/**", " * @brief Reproduce las operaciones exitosas del historial AVL y calcula sus consultas.",
      " * @return 0 al terminar la secuencia.",
      " * @note Compilar junto a tad_avl.c. Consultas fallidas no se ejecutan. El equilibrio",
      " * por alturas no certifica el FE almacenado; los auxiliares anteriores pertenecen a este main.", " */");
  }
  if (modelId === "red_black") {
    const source = didactic || window.HIER_VIEW_MODEL?.didactic || {};
    lines.push('#include <stdio.h>', '#include "tad_rojo_negro.h"', "");
    for (const op of ["inorden", "altura"]) {
      if (!history.some(entry => entry && entry.success !== false && entry.operation === op)) continue;
      const helper = source.operations?.[op];
      if (!helper) throw new Error(`Falta el auxiliar canonico Rojo-Negro de ${op}.`);
      lines.push(helper, "");
    }
    lines.push("/**", " * @brief Reproduce operaciones exitosas y calcula consultas del historial Rojo-Negro.",
      " * @return 0 al terminar.", " * @note Compilar junto a tad_rojo_negro.c. Auxiliares propios del main.",
      " * Validar llama al TAD publico: cinco reglas RN, orden estricto y enlaces nativos.",
      " * Al finalizar, el caller libera las reservas restantes y asigna NULL a su raiz.",
      " * Esta limpieza no agrega operaciones ni salida al historial del estudiante.", " */");
  }
  if (modelId === "binary_heap") {
    lines.push('#include <stdio.h>', '#include <stdlib.h>', '#include "tad_monticulo_binario.h"', "",
      "/**", " * @brief Reproduce el historial del monticulo y copia todos sus valores internos.",
      " * @return 0 al terminar; EXIT_FAILURE si falla la reserva para una copia.",
      " * @note A lista conserva el orden interno del heap; no ordena sus valores.", " */");
  }
  lines.push("int main(void) {");
  lines.push("    // Declaracion de la estructura");

  if (modelId === "abb") {
    lines.push("    ABBNodo *arbol = NULL;");
  } else if (modelId === "avl") {
    lines.push("    AVL arbol = NULL;");
    lines.push("    (void)arbol; // Permite un historial sin operaciones exitosas.");
  } else if (modelId === "red_black") {
    lines.push("    RBT arbol = NULL;");
    lines.push("    (void)arbol;");
  } else if (modelId === "binary_heap") {
    lines.push("    MonticuloBinario monticulo;");
    lines.push("    monticulo_inicializar(&monticulo, MONTICULO_MIN, 16);");
  } else {
    lines.push("    // Estructura jerarquica inicializada");
  }

  lines.push("");
  lines.push("    // Historial de ejecucion del usuario");
  history.forEach((entry, index) => {
    if (!entry || typeof entry === "string") {
      return;
    }
    if ((modelId === "abb" || modelId === "avl" || modelId === "red_black" || modelId === "binary_heap") && entry.success === false) {
      if (modelId !== "red_black") lines.push("    /* Operacion fallida en la interfaz: no forma parte de la reproduccion ejecutable. */");
      return;
    }
    let call = `${entry.subroutine || "Operacion"}();`;
    if (modelId === "abb") {
      call = abbMainCallForEntry(entry, index + 1);
    } else if (modelId === "avl") {
      call = avlMainCallForEntry(entry, index + 1);
    } else if (modelId === "red_black") {
      call = redBlackMainCallForEntry(entry, index + 1);
    } else if (modelId === "binary_heap") {
      call = binaryHeapMainCallForEntry(entry, index + 1);
    }
    if ((modelId === "avl" || modelId === "red_black") && entry.operation === "inorden") lines.push('    printf("INORDEN: ");');
    lines.push(`    ${call}`);
    if (modelId === "abb") {
      if (entry.operation === "buscar") {
        lines.push(`    printf("BUSCAR: %s\\n", encontrado_${index + 1} != NULL ? "encontrado" : "ausente");`);
        return;
      }
      if (["minimo", "maximo"].includes(entry.operation)) {
        const variable = `${entry.operation}_${index + 1}`;
        lines.push(`    if (${variable} != NULL) printf("${entry.operation.toUpperCase()}: %d\\n", ${variable}->valor);`);
        lines.push('    else puts("Arbol vacio.");');
        return;
      }
      if (entry.operation === "altura") {
        lines.push(`    printf("ALTURA: %d\\n", altura_${index + 1});`);
        return;
      }
      if (["inorden", "preorden", "postorden"].includes(entry.operation)) {
        lines.push('    printf("\\n");');
        return;
      }
      if (["insertar", "eliminar", "limpiar"].includes(entry.operation)) {
        lines.push(`    // Llamada registrada: ${entry.operation}; no se imprime un resultado precalculado.`);
        return;
      }
    }
    if (modelId === "abb" && entry.operation === "validar") {
      lines.push(`    printf("VALIDAR ABB: %s\\n", valido_${index + 1} ? "correcto" : "incorrecto");`);
      return;
    }
    if (modelId === "abb" && entry.operation === "contar_hojas") {
      lines.push(`    printf("Hojas actuales: %d\\n", hojas_${index + 1});`);
      return;
    }
    if (modelId === "avl") {
      const value = hAVLMainIntegerValue(entry);
      if (entry.operation === "insertar") {
        lines.push(`    printf("INSERTAR invocado: %d\\n", (int)(${value}));`);
        return;
      }
      if (entry.operation === "eliminar") {
        lines.push(`    printf("ELIMINAR invocado: %d\\n", (int)(${value}));`);
        return;
      }
      if (entry.operation === "buscar") lines.push(`    printf("BUSCAR ${hToCStringLiteral(value)}: %s\\n", encontrado_${index + 1} != NULL ? "encontrado" : "ausente");`);
      else if (entry.operation === "minimo") lines.push(`    printf("MINIMO: %d\\n", minimo_${index + 1}->nro);`);
      else if (entry.operation === "maximo") lines.push(`    printf("MAXIMO: %d\\n", maximo_${index + 1}->nro);`);
      else if (entry.operation === "altura") lines.push(`    printf("ALTURA: %d\\n", altura_${index + 1});`);
      else if (entry.operation === "inorden") lines.push('    printf("\\n");');
      else if (entry.operation === "validar") lines.push(`    printf("EQUILIBRIO POR ALTURAS: %s\\n", valido_${index + 1} ? "correcto" : "incorrecto");`);
      if (["buscar", "minimo", "maximo", "altura", "inorden", "validar"].includes(entry.operation)) return;
    }
    if (modelId === "binary_heap") {
      if (entry.operation === "a_lista") return;
      if (["raiz", "extraer_raiz"].includes(entry.operation)) {
        const variable = entry.operation === "raiz" ? "raiz" : "extraido";
        lines.push(`    if (ok_${index + 1}) printf("${entry.operation === "raiz" ? "RAIZ" : "EXTRAIDO"}: %d\\n", ${variable}_${index + 1});`);
        return;
      }
      if (entry.operation === "insertar") {
        const value = hAVLMainIntegerValue(entry);
        lines.push(`    if (!ok_${index + 1}) { monticulo_destruir(&monticulo); return EXIT_FAILURE; }`);
        lines.push(`    printf("INSERTAR: %d\\n", (int)(${value}));`);
        return;
      }
      if (entry.operation === "limpiar") {
        lines.push('    printf("LIMPIAR\\n");');
        return;
      }
    }
    if (modelId === "red_black") {
      const value = hAVLMainIntegerValue(entry);
      if (entry.operation === "buscar") lines.push(`    printf("BUSCAR %d: %s\\n", (int)(${value}), encontrado_${index + 1} != NULL ? "encontrado" : "ausente");`);
      else if (entry.operation === "altura") lines.push(`    printf("ALTURA: %d\\n", altura_${index + 1});`);
      else if (entry.operation === "inorden") lines.push('    printf("\\n");');
      else if (entry.operation === "validar") lines.push(`    printf("VALIDAR RN COMPLETO: %s\\n", valido_${index + 1} ? "correcto" : "incorrecto");`);
      else if (entry.operation === "eliminar") lines.push(`    printf("ELIMINAR invocado: %d\\n", (int)(${value}));`);
      else if (entry.operation === "limpiar") lines.push('    printf("LIMPIAR\\n");');
      return;
    }
    const visibleResult = getHierEntryVisibleResult(entry);
    if (visibleResult) {
      lines.push(`    printf("${hToCStringLiteral(visibleResult)}\\n");`);
      lines.push(`    // ${visibleResult}`);
    }
  });

  if (modelId === "abb") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    abb_liberarArbol(arbol); arbol = NULL;");
  } else if (modelId === "avl") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    avl_liberarAVL(arbol); arbol = NULL;");
  } else if (modelId === "red_black") {
    lines.push("    // Limpieza final del caller; no es otra operacion del historial.");
    lines.push("    rbt_liberar(arbol); arbol = NULL;");
  } else if (modelId === "binary_heap") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    monticulo_destruir(&monticulo);");
  }
  lines.push("    return 0;");
  lines.push("}");
  return lines.join("\n");
}

function renderHierHistory(history, container, modelId, didactic) {
  if (!container) {
    return;
  }
  container.dataset.rawCode = "";
  if (!history.length) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }

  const codeTitle = didactic && didactic.code_title ? String(didactic.code_title) : "";
  if (codeTitle.toLowerCase().includes("codigo c")) {
    const code = buildHierMainCode(modelId, history, didactic);
    container.dataset.rawCode = code;
    const codeHtml = buildHierHighlightedCodeHtml(code, codeTitle);
    container.innerHTML = (
      "<li class=\"didactic-history-item history-main-wrap\">" +
      "<div class=\"didactic-history-head\">Programa principal (main)</div>" +
      `<pre class="didactic-code didactic-history-main">${codeHtml}</pre>` +
      "</li>"
    );
    return;
  }

  container.innerHTML = history.map((item, index) => {
    if (typeof item === "string") {
      return (
        "<li class=\"didactic-history-item\">" +
        `<div class="didactic-history-head">Paso ${index + 1}: Historial</div>` +
        `<div class="didactic-history-line"><span class="k">Salida:</span> ${hEscape(item)}</div>` +
        "</li>"
      );
    }
    return (
      "<li class=\"didactic-history-item\">" +
      `<div class="didactic-history-head">Paso ${index + 1}: ${hEscape(item.subroutine || "Operacion")}</div>` +
      `<div class="didactic-history-line"><span class="k">Entrada:</span> ${hEscape(item.payload || "-")}</div>` +
      `<div class="didactic-history-line"><span class="k">Salida:</span> ${hEscape(getHierEntryVisibleResult(item) || "(en ejecucion)")}</div>` +
      "</li>"
    );
  }).join("");
}

function initHierSimplifiedWorkspace() {
  const prepareTitle = hById("hier-prepare-title");
  const visualTitle = hById("hier-visual-title");
  const codeTitle = hById("op-pseudocode-title");
  const controlTitle = hById("hier-control-title");
  const understandTitle = hById("hier-understand-title");
  const reflectTitle = hById("hier-reflect-title");
  const prepareStage = prepareTitle?.closest("section");
  const controlStage = controlTitle?.closest("section");
  const understandStage = understandTitle?.closest("section");
  const resultsStage = reflectTitle?.closest("section");

  // Preserve educational capabilities inside the current five stages.
  function moveLearningPanel(titleId, label) {
    const title = hById(titleId);
    const section = title?.closest("section");
    if (!section || !understandStage) return;
    section.classList.remove("hier-stage");
    const heading = document.createElement("h4");
    heading.id = titleId;
    heading.textContent = label;
    title.replaceWith(heading);
    const disclosure = document.createElement("details");
    disclosure.className = "hier-learning-disclosure";
    const summary = document.createElement("summary");
    summary.textContent = label;
    disclosure.append(summary, section);
    understandStage.append(disclosure);
  }
  moveLearningPanel("hier-predict-title", "Predecir");
  moveLearningPanel("hier-compare-title", "Comparar");
  const levelLabel = hById("hier-learning-level")?.closest("label");
  const codeToolbar = codeTitle?.closest("section")?.querySelector(".hier-code-toolbar");
  if (levelLabel && codeToolbar) codeToolbar.append(levelLabel);

  // The old position slider is an internal value only; navigation is manual.
  const comparePosition = hById("hier-compare-progress");
  if (comparePosition) {
    const label = comparePosition.closest("label");
    comparePosition.type = "hidden";
    comparePosition.setAttribute("aria-hidden", "true");
    comparePosition.setAttribute("tabindex", "-1");
    const controls = document.createElement("div");
    controls.className = "actions";
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", "Navegación manual de la comparación");
    for (const [id, text] of [["hier-compare-prev", "Paso anterior"], ["hier-compare-next", "Siguiente paso"]]) {
      const button = document.createElement("button");
      button.id = id; button.type = "button"; button.className = "btn secondary";
      button.textContent = text; button.disabled = true; controls.append(button);
    }
    const position = document.createElement("span");
    position.id = "hier-compare-position-label";
    position.setAttribute("aria-live", "polite");
    position.textContent = "Sin comparación preparada"; controls.append(position, comparePosition);
    label.replaceWith(controls);
  }

  if (prepareTitle) prepareTitle.innerHTML = "<span>1</span> Preparar y controlar ejecución";
  if (visualTitle) visualTitle.innerHTML = "<span>2</span> Visualizar y ejecutar";
  const codeHeading = codeTitle?.closest("section")?.querySelector(".hier-code-toolbar h3");
  if (codeHeading) codeHeading.innerHTML = "<span>3</span> Relacionar con código";
  if (understandTitle) understandTitle.innerHTML = "<span>4</span> Comprender";
  if (reflectTitle) reflectTitle.innerHTML = "<span>5</span> Resultados de ejecución";

  if (prepareStage && controlStage) {
    prepareStage.classList.add("hier-control-stage");
    const actions = controlStage.querySelector(".actions");
    const stepToggle = hById("hier-step-toggle");
    const counter = hById("hier-sim-counter");
    const status = hById("hier-sim-status");
    ["hier-prepare", "hier-sim-pause", "hier-sim-home", "hier-sim-end", "hier-sim-repeat", "hier-restart-execution"].forEach((id) => hById(id)?.remove());
    const executeButton = hById("hier-sim-play");
    const previousButton = hById("hier-sim-prev");
    const nextButton = hById("hier-sim-step");
    if (executeButton) executeButton.textContent = "Ejecutar operación";
    if (nextButton) nextButton.textContent = "Siguiente paso";
    if (previousButton) previousButton.textContent = "Paso anterior";
    if (actions && executeButton && previousButton && nextButton) {
      const stepModeButton = document.createElement("button");
      stepModeButton.id = "hier-step-mode";
      stepModeButton.type = "button";
      stepModeButton.className = "btn secondary hier-step-mode";
      stepModeButton.textContent = "Paso a paso";
      stepModeButton.setAttribute("aria-pressed", "false");
      const stepControls = document.createElement("div");
      stepControls.id = "hier-step-controls";
      stepControls.className = "hier-step-controls";
      stepControls.hidden = true;
      stepControls.append(previousButton, nextButton);
      executeButton.after(stepModeButton, stepControls);
    }
    if (stepToggle) {
      stepToggle.checked = false;
      stepToggle.hidden = true;
      stepToggle.classList.add("sr-only");
      stepToggle.setAttribute("tabindex", "-1");
      stepToggle.setAttribute("aria-hidden", "true");
    }
    const technical = controlStage.querySelector(".didactic-technical");
    const classroomControls = document.createElement("div");
    classroomControls.className = "hier-classroom-controls";
    classroomControls.setAttribute("role", "group");
    classroomControls.setAttribute("aria-label", "Controles de ejecución");
    classroomControls.append(actions, stepToggle, counter, status);
    const workspace = document.querySelector(".hier-primary-workspace");
    if (workspace) workspace.before(classroomControls);
    else prepareStage.append(classroomControls);
    technical?.remove();
    controlStage.remove();
  }

  function makeCollapsible(stage, title, contentId) {
    if (!stage || !title || hById(contentId)) return;
    const content = document.createElement("div");
    content.id = contentId;
    content.className = "hier-panel-content";
    content.hidden = true;
    Array.from(stage.children).forEach((child) => {
      if (child !== title) content.appendChild(child);
    });
    const heading = document.createElement("div");
    heading.className = "hier-panel-heading";
    const button = document.createElement("button");
    button.id = contentId.replace("-content", "-toggle");
    button.type = "button";
    button.className = "btn secondary hier-panel-toggle";
    button.textContent = "Mostrar";
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", contentId);
    button.addEventListener("click", () => {
      const visible = content.hidden;
      content.hidden = !visible;
      button.textContent = visible ? "Ocultar" : "Mostrar";
      button.setAttribute("aria-expanded", String(visible));
    });
    heading.append(title, button);
    stage.append(heading, content);
  }

  const tadDetails = resultsStage?.querySelector("details");
  if (tadDetails) {
    const tadPanel = document.createElement("section");
    tadPanel.className = "didactic-technical";
    const heading = document.createElement("h4");
    heading.textContent = "Estructura del TAD";
    tadPanel.append(heading, ...Array.from(tadDetails.children).filter((child) => child.tagName !== "SUMMARY"));
    tadDetails.replaceWith(tadPanel);
  }
  makeCollapsible(understandStage, understandTitle, "hier-understand-content");
  if (!window.ClassroomView) makeCollapsible(resultsStage, reflectTitle, "hier-results-content");
}

function initHierPage(model) {
  const form = hById("operation-form");
  const operationSelect = hById("operation-select");
  const inputsContainer = hById("operation-inputs");
  const resetButton = hById("reset-button");
  const visualContainer = hById("visual-state");
  const historyBox = hById("action-history");
  const simPlayButton = hById("hier-sim-play");
  const simPrevButton = hById("hier-sim-prev");
  const simStepButton = hById("hier-sim-step");
  const simStatus = hById("hier-sim-status");
  const stepToggle = hById("hier-step-toggle");
  const speedSlider = hById("hier-speed-slider");
  const speedValue = hById("hier-speed-value");
  const printfConsole = hById("hier-printf-console");
  window.ConsoleHistory?.bind(printfConsole, model.id || "sorting_array", model.history);
  const learningLevel = hById("hier-learning-level");
  const guidedExample = hById("hier-guided-example");
  const loadExampleButton = hById("hier-load-example");
  const exampleLesson = hById("hier-example-lesson");
  const restartExecutionButton = hById("hier-restart-execution");
  const hideComments = hById("hier-hide-comments");
  const prepareButton=hById("hier-prepare"), pauseButton=hById("hier-sim-pause"), homeButton=hById("hier-sim-home"), endButton=hById("hier-sim-end"), repeatButton=hById("hier-sim-repeat"), progressSlider=hById("hier-progress"), stepMetadata=hById("hier-step-metadata");
  const predictionSelect=hById("hier-prediction"), checkPrediction=hById("hier-check-prediction"), hintButton=hById("hier-hint"), skipPrediction=hById("hier-skip-prediction"), predictionFeedback=hById("hier-prediction-feedback"), practiceMode=hById("hier-practice-mode"), practiceCover=hById("hier-practice-cover"), progressSummary=hById("hier-progress-summary"), resetProgress=hById("hier-reset-progress");
  const compareSection=hById("hier-compare-title")?.closest("section"), compareKind=hById("hier-compare-kind"), compareValues=hById("hier-compare-values"), compareRun=hById("hier-compare-run"), compareProgress=hById("hier-compare-progress"), compareInput=hById("hier-compare-input"), compareGrid=hById("hier-compare-grid"), compareConclusion=hById("hier-compare-conclusion");
  const exportImage=hById("hier-export-image"), exportSummary=hById("hier-export-summary"), announcer=hById("hier-accessible-announcer");

  if (!form || !operationSelect || !inputsContainer || !visualContainer) {
    return;
  }

  initHierSimplifiedWorkspace();
  const stepModeButton = hById("hier-step-mode");
  const stepControls = hById("hier-step-controls");
  function syncStepModeUi() {
    const active = Boolean(stepToggle?.checked);
    if (stepControls) stepControls.hidden = !active;
    if (stepModeButton) {
      stepModeButton.textContent = active ? "Cerrar paso a paso" : "Paso a paso";
      stepModeButton.setAttribute("aria-pressed", String(active));
      stepModeButton.classList.toggle("is-active", active);
    }
  }
  stepModeButton?.addEventListener("click", () => {
    if (!stepToggle) return;
    stepToggle.checked = !stepToggle.checked;
    stepToggle.dispatchEvent(new Event("change"));
  });
  syncStepModeUi();

  const pageState = {
    modelId: model.id,
    visualState: model.visual_state,
    lastExecution: null,
    pendingExecution: null,
    rnTimeline: [],
    rnTimelineIndex: -1,
    traceAtEnd: false,
    compareState: null,
    rotationVisualHint: null,
    rotationTextHint: null,
    heapAnimation: {
      active: false,
      frame: null,
    },
    treeTransition: {
      active: false,
      data: null,
      rafId: null,
    },
  };

  const operations = model.operations || [];
  let playbackSpeed = 1;
  let playbackSpeedSetting = 0;
  let currentPedagogyFrame = null;
  let traceCursor = -1;
  const presentationKey = `hier-presentation:${model.id}`;
  const conceptualProgressKey=`hier-concept-progress:${model.id}`;
  function readConceptualProgress(){try{return JSON.parse(sessionStorage.getItem(conceptualProgressKey)||'{"attempts":0,"correct":0}') }catch(_error){return {attempts:0,correct:0};}}
  let conceptualProgress=readConceptualProgress(), hintLevel=0;
  let hierarchicalComparison=null;
  function renderConceptualProgress(){if(progressSummary)progressSummary.textContent=`Progreso conceptual de esta sesión: ${conceptualProgress.correct} aciertos de ${conceptualProgress.attempts} intentos.`;try{sessionStorage.setItem(conceptualProgressKey,JSON.stringify(conceptualProgress));}catch(_error){/* optional */}}
  const rnValidatorTraceKey = "visualstruct.rn.validar.trace.v3";
  let rnValidatorCache = null;
  function rnStable(value) {
    if (Array.isArray(value)) return value.map(rnStable);
    if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map(key => [key, rnStable(value[key])]));
    return value;
  }
  function rnDigest(value) { return JSON.stringify(rnStable(value)); }
  function clearRNValidatorCache() {
    if (model.id !== "red_black") return;
    rnValidatorCache = null;
    try { sessionStorage.removeItem(rnValidatorTraceKey); } catch (_error) { /* optional cache */ }
  }
  function writeRNValidatorCache() {
    if (!rnValidatorCache) return;
    try { sessionStorage.setItem(rnValidatorTraceKey, JSON.stringify(rnValidatorCache)); } catch (_error) { /* optional cache */ }
  }
  function readPresentation() { try { return JSON.parse(sessionStorage.getItem(presentationKey) || "{}"); } catch (_error) { return {}; } }
  function writePresentation(extra = {}) { const current=operations.find((op)=>op.name===operationSelect.value); try { sessionStorage.setItem(presentationKey,JSON.stringify({operation:operationSelect.value,payload:current?collectPayload(current):{},level:learningLevel?.value||"intermediate",cursor:traceCursor,...extra})); } catch(_error) { /* optional */ } }

  function speedSettingToMultiplier(setting) {
    return Math.pow(2, setting);
  }

  function setPlaybackSpeed(value) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
      return;
    }
    playbackSpeedSetting = Math.min(2, Math.max(-2, parsed));
    playbackSpeed = speedSettingToMultiplier(playbackSpeedSetting);
    if (speedValue) {
      const signed = playbackSpeedSetting >= 0
        ? `+${playbackSpeedSetting.toFixed(2)}x`
        : `${playbackSpeedSetting.toFixed(2)}x`;
      speedValue.textContent = `${signed} (${playbackSpeed.toFixed(2)}x real)`;
    }
    if (tracePlayer && typeof tracePlayer.setSpeed === "function") {
      tracePlayer.setSpeed(playbackSpeed);
    }
  }

  function scaledDelay(ms) {
    const base = Number(ms);
    if (!Number.isFinite(base)) {
      return 20;
    }
    return Math.max(20, Math.round(base / playbackSpeed));
  }
  let selected = operations[0] || null;
  const operationLabel = new Map(operations.map((op) => [op.name, op.label]));
  const actionHistory = [];
  const consoleState = {
    trace: null,
    resultMessage: null,
    fallbackMessage: "",
  };

  function finalizePendingHistoryEntry() {
    if (!actionHistory.length) {
      return false;
    }
    const last = actionHistory[actionHistory.length - 1];
    if (!last || typeof last === "string" || !last.pendingTrace) {
      return false;
    }
    last.pendingTrace = false;
    last.result = last.finalResult || last.result || "-";
    renderHierHistory(actionHistory, historyBox, pageState.modelId, model.didactic);
    return true;
  }

  function collectHierPrintfLines(trace, cursor) {
    if (!trace || !Array.isArray(trace.steps) || cursor < 0) {
      return [];
    }
    const limit = Math.min(cursor, trace.steps.length - 1);
    // Snapshot producers publish the complete console at this cursor. Event
    // producers publish only new fragments: repeated/blank output is valid C.
    if (trace.console_mode === "snapshot") {
      return Array.isArray(trace.steps[limit]?.console) ? trace.steps[limit].console.slice() : [];
    }
    const out = [];
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const emitted = Array.isArray(step.console) ? step.console : [];
      out.push(...emitted);
    }
    return out;
  }

  function refreshHierPrintfConsole(cursor) {
    const steps = consoleState.trace?.steps || [];
    const step = steps[Math.min(cursor, steps.length - 1)];
    const memory = cursor < 0 ? steps[0]?.state_snapshot : step?.pedagogy?.memory_state;
    const stdout = cursor < 0 ? "" : typeof step?.console_stdout === "string" ? step.console_stdout
      : typeof memory?.console_stdout === "string" ? memory.console_stdout
      : collectHierPrintfLines(consoleState.trace, cursor).join("\n");
    if (window.ConsoleHistory) window.ConsoleHistory.render(printfConsole, consoleState.trace, cursor, stdout);
    else renderHierPrintfConsole(printfConsole, collectHierPrintfLines(consoleState.trace, cursor), "(sin salida printf en esta ruta)");
  }

  operations.forEach((operation) => {
    const option = document.createElement("option");
    option.value = operation.name;
    option.textContent = operation.label;
    operationSelect.appendChild(option);
  });

  const savedPresentation = readPresentation();
  if (savedPresentation.operation) selected = operations.find((op)=>op.name===savedPresentation.operation) || selected;
  if (selected) operationSelect.value = selected.name;
  if (learningLevel) learningLevel.value = ["basic","intermediate","advanced"].includes(savedPresentation.level) ? savedPresentation.level : "intermediate";
  (model.guided_examples||[]).forEach((example)=>{ const option=document.createElement("option"); option.value=example.id; option.textContent=example.label; guidedExample?.appendChild(option); });

  buildOperationInputs(selected, inputsContainer);
  if(savedPresentation.payload&&selected)selected.inputs.forEach((field)=>{const input=hById(`h-field-${field.name}`);if(input&&Object.prototype.hasOwnProperty.call(savedPresentation.payload,field.name))input.value=savedPresentation.payload[field.name];});
  updateHierDidacticPanel(model, selected ? selected.name : "");
  (model.history || []).forEach((step) => {
    const opName = String(step.operation || "");
    const label = operationLabel.get(opName) || opName;
    const subroutine = getHierSubroutineName(model, opName, label);
    const payloadText = summarizeHierPayload(step.payload || {});
    hPushUniqueHistoryEntry(
      actionHistory,
      createHierHistoryEntry(
        subroutine,
        payloadText || "-",
        "Operacion aplicada.",
        opName,
        step.payload || {},
      ),
      { allowRepeated: model.id === "avl" || model.id === "binary_heap" || model.id === "red_black" || (model.id === "abb" && ["contar_hojas", "validar"].includes(step.operation)) },
    );
  });
  renderHierHistory(actionHistory, historyBox, pageState.modelId, model.didactic);
  let predictionController = null;
  let predictionTargetKey = "";
  let predictionTraceRef = null;
  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: hById("op-pseudocode"),
      statusElement: simStatus,
      counterElement: hById("hier-sim-counter"),
      renderState: (stateSnapshot, stepMeta) => {
        stopTreeTransition();
        stopHeapAnimation();
        const abbBefore = Boolean(stepMeta?.pedagogy?.memory_state?.abb_insert_model || stepMeta?.pedagogy?.memory_state?.abb_traversal_model || stepMeta?.pedagogy?.memory_state?.abb_read_model || stepMeta?.pedagogy?.memory_state?.heap_query_model) && stateSnapshot === stepMeta.state_snapshot;
    if ((stepMeta?.pedagogy?.memory_state?.abb_insert_model || stepMeta?.pedagogy?.memory_state?.abb_traversal_model || stepMeta?.pedagogy?.memory_state?.abb_read_model || stepMeta?.pedagogy?.memory_state?.heap_query_model) && !abbBefore) stateSnapshot = stepMeta.pedagogy.memory_state;
    pageState.visualState = stateSnapshot;
        if (
          stepMeta
          && stepMeta.debug
          && Array.isArray(stepMeta.debug.path_keys)
          && Number.isInteger(stepMeta.debug.path_index)
        ) {
          const activeKeys = Array.isArray(stepMeta.debug.active_keys)
            ? stepMeta.debug.active_keys.map((item) => String(item))
            : [];
          pageState.compareState = {
            pathKeys: stepMeta.debug.path_keys.map((item) => String(item)),
            index: Number(stepMeta.debug.path_index),
            activeKeys,
            unbalancedKey: (
              stepMeta.debug.unbalanced_key !== undefined && stepMeta.debug.unbalanced_key !== null
            ) ? String(stepMeta.debug.unbalanced_key) : null,
            rotationMessage: String(stepMeta.debug.rotation_message || "").trim(),
          };
        } else {
          pageState.compareState = null;
        }
        if (pageState.modelId === "red_black" && pageState.compareState) {
          pageState.compareState.rnTimeline = Array.isArray(pageState.rnTimeline)
            ? pageState.rnTimeline
            : [];
          pageState.compareState.rnTimelineIndex = Number.isInteger(stepMeta && stepMeta.step_index)
            ? Number(stepMeta.step_index)
            : -1;
        }
        pageState.rotationVisualHint = null;
        pageState.rotationTextHint = stepMeta?.pedagogy?.adjustment || null;
        if(stepMeta?.pedagogy){currentPedagogyFrame=abbBefore ? stepMeta.pedagogy.initial_frame : stepMeta.pedagogy;renderHierPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");}
        repaint();
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        traceCursor = cursor;
        if (model.id === "red_black" && rnValidatorCache && consoleState.trace?.operation_name === "validar" && traceSelectionKey === rnValidatorCache.selectionKey) {
          rnValidatorCache.cursor = cursor;
          writeRNValidatorCache();
        }
        const total = event && event.trace && Array.isArray(event.trace.steps)
          ? event.trace.steps.length
          : 0;
        pageState.traceAtEnd = total > 0 && cursor >= total - 1;
        if (consoleState.resultMessage) {
          showHierMessage(pageState.traceAtEnd ? consoleState.resultMessage.text : (consoleState.resultMessage.operation === "validar" ? "Validacion preparada: resultado pendiente hasta completar la traza." : consoleState.resultMessage.operation === "limpiar" ? "Limpieza preparada: resultado pendiente hasta completar la traza." : consoleState.resultMessage.operation === "insertar" ? "Insercion preparada: resultado pendiente hasta completar la traza." : consoleState.resultMessage.operation === "eliminar" ? "Eliminacion preparada: resultado pendiente hasta completar la traza." : consoleState.resultMessage.operation === "extraer_raiz" ? "Extraccion preparada: resultado pendiente hasta completar la traza." : "Consulta preparada: resultado pendiente hasta completar la traza."), pageState.traceAtEnd ? consoleState.resultMessage.success : true);
        }
        if (pageState.traceAtEnd) {
          if (pageState.pendingExecution) {
            pageState.lastExecution = pageState.pendingExecution;
            pageState.pendingExecution = null;
          }
          // Al finalizar la simulacion se limpia el resaltado didactico
          // para dejar el estado final del arbol en su color base.
          pageState.compareState = null;
          finalizePendingHistoryEntry();
        }
        if (pageState.modelId === "red_black") {
          pageState.rnTimelineIndex = cursor;
        }
        repaint();
        refreshHierPrintfConsole(cursor);
        const step=event?.step; enhanceHierCodeNavigation(Number.isInteger(step?.line_index)?step.line_index:null); writePresentation({cursor});
        if(progressSlider){progressSlider.max=String(Math.max(0,total-1));progressSlider.value=String(Math.max(0,cursor));progressSlider.disabled=total===0;}
        if (simStatus && cursor >= 0 && step?.pedagogy) simStatus.textContent = `Paso ${cursor + 1}/${total} · ${window.ContextualHelp?.phaseLabel(step.pedagogy) || "Ejecutar la instrucción"}`;
        const pedagogy=step?.pedagogy; const frameCall=pedagogy?.call_stack?.at(-1); if(stepMetadata)stepMetadata.textContent=`Función: ${frameCall?.function||"—"} · Profundidad: ${frameCall?.depth??"—"} · Fase: ${pedagogy?.phase?.label||"—"} · Concepto: ${pedagogy?.concept||"—"}`;
        syncPredictionUI();
        if (cursor < 0) window.ContextualHelp?.frame("hier", null);
        setSimulationButtonsEnabled();
      },
    })
    : null;
  if (speedSlider) {
    setPlaybackSpeed(speedSlider.value);
    speedSlider.addEventListener("input", () => {
      setPlaybackSpeed(speedSlider.value);
    });
  } else {
    setPlaybackSpeed(0);
  }
  initHierResponsiveWorkspace();
  hideComments?.addEventListener("change",()=>enhanceHierCodeNavigation(null));
  restartExecutionButton?.addEventListener("click",()=>{tracePlayer?.reset();setSimulationButtonsEnabled();});
  renderConceptualProgress();
  let pendingExecution = false;
  let traceSelectionKey = "";

  function stopTreeTransition() {
    if (pageState.treeTransition.rafId) {
      cancelAnimationFrame(pageState.treeTransition.rafId);
      pageState.treeTransition.rafId = null;
    }
    pageState.treeTransition.active = false;
    pageState.treeTransition.data = null;
  }

  function stopHeapAnimation() {
    pageState.heapAnimation.active = false;
    pageState.heapAnimation.frame = null;
  }

  function repaint() {
    if (visualContainer) {
      visualContainer.classList.toggle("sim-trace-complete", Boolean(pageState.traceAtEnd));
    }
    const transitionData = pageState.treeTransition.active ? pageState.treeTransition.data : null;
    renderHierState(
      pageState.modelId,
      pageState.visualState,
      visualContainer,
      pageState.lastExecution,
      transitionData,
      pageState.compareState,
      pageState.rotationVisualHint,
      pageState.rotationTextHint,
      pageState.heapAnimation.active ? pageState.heapAnimation.frame : null,
    );
  }

  function isCurrentSelectionValid() {
    const current = operations.find((op) => op.name === operationSelect.value);
    if (!current) {
      return false;
    }
    return current.inputs.every((field) => {
      const element = hById(`h-field-${field.name}`);
      if (!element) {
        return false;
      }
      if (field.required === false) {
        return true;
      }
      if (String(element.value || "").trim() === "") {
        return false;
      }
      return typeof element.checkValidity === "function" ? element.checkValidity() : true;
    });
  }

  function isStepByStepEnabled() {
    return !stepToggle || Boolean(stepToggle.checked);
  }

  function setSimulationButtonsEnabled() {
    if (window.MultipleInput?.lockActiveControls?.()) return;
    const stepMode = isStepByStepEnabled();
    const hasTrace = Boolean(tracePlayer && tracePlayer.hasTrace());
    const busy = pendingExecution;
    const canExecute = isCurrentSelectionValid();
    const cursor = tracePlayer && typeof tracePlayer.getCursor === "function"
      ? tracePlayer.getCursor()
      : -1;
    const total = tracePlayer && typeof tracePlayer.getTotalSteps === "function"
      ? tracePlayer.getTotalSteps()
      : 0;
    const atEnd = hasTrace && total > 0 && cursor >= total - 1;
    if (simPlayButton) {
      simPlayButton.disabled = busy || !canExecute;
    }
    if (simPrevButton) {
      simPrevButton.disabled = busy || !stepMode || !hasTrace || cursor < 0;
    }
    if (simStepButton) {
      simStepButton.disabled = busy || !stepMode || !canExecute || (hasTrace && atEnd);
    }
    if (speedSlider) {
      speedSlider.disabled = busy || !stepMode;
    }
  }

  function invalidateTrace(message) {
    finalizePendingHistoryEntry();
    traceSelectionKey = "";
    consoleState.trace = null;
    consoleState.resultMessage = null;
    consoleState.fallbackMessage = "";
    pageState.traceAtEnd = false;
    pageState.pendingExecution = null;
    pageState.rnTimeline = [];
    pageState.rnTimelineIndex = -1;
    tracePlayer?.clear(message || "Usa Ejecutar operación o activa Paso a paso.");
    repaint();
    refreshHierPrintfConsole(-1);
    setSimulationButtonsEnabled();
  }

  function collectPayload(current) {
    const payload = {};
    current.inputs.forEach((field) => {
      const element = hById(`h-field-${field.name}`);
      payload[field.name] = element ? element.value : "";
    });
    return payload;
  }

  function buildSelectionKey(current, payload) {
    return `${current.name}::${JSON.stringify(payload)}`;
  }

  function startTreeTransition(previousRoot, nextRoot, rotationHint) {
    const transitionData = buildTransitionData(previousRoot, nextRoot);
    if (!transitionData) {
      return;
    }

    stopTreeTransition();
    pageState.treeTransition.active = true;
    pageState.treeTransition.data = transitionData;
    pageState.rotationVisualHint = rotationHint || null;

    const duration = Math.max(180, scaledDelay(700));
    const startTs = performance.now();

    function tick(now) {
      if (!pageState.treeTransition.active || !pageState.treeTransition.data) {
        return;
      }

      const elapsed = now - startTs;
      const progress = Math.min(1, elapsed / duration);
      pageState.treeTransition.data.progress = progress;
      repaint();

      if (progress < 1) {
        pageState.treeTransition.rafId = requestAnimationFrame(tick);
      } else {
        stopTreeTransition();
        pageState.rotationVisualHint = null;
        repaint();
      }
    }

    pageState.treeTransition.rafId = requestAnimationFrame(tick);
  }

  function applyState(visualState, lastExecution) {
    const previousRoot = pageState.visualState ? pageState.visualState.root : null;
    const shouldAnimateRotations =
      (pageState.modelId === "avl" || pageState.modelId === "red_black")
      && lastExecution
      && (lastExecution.operation === "insertar" || lastExecution.operation === "eliminar");

    stopTreeTransition();
    stopHeapAnimation();

    pageState.visualState = visualState;
    pageState.lastExecution = lastExecution;
    pageState.compareState = null;
    pageState.rotationTextHint = lastExecution ? lastExecution.rotation_hint || null : null;
    pageState.rotationVisualHint = null;

    if (shouldAnimateRotations && previousRoot && visualState && visualState.root) {
      startTreeTransition(previousRoot, visualState.root, pageState.rotationTextHint);
    } else {
      repaint();
    }
  }

  async function animateComparison(pathKeys) {
    if (!pathKeys || !pathKeys.length) {
      return;
    }

    pageState.compareState = {
      pathKeys: [...pathKeys],
      index: -1,
    };
    repaint();

    for (let index = 0; index < pathKeys.length; index += 1) {
      pageState.compareState.index = index;
      repaint();
      await sleep(scaledDelay(380));
    }
  }

  async function animateHeapFrames(frames) {
    if (!frames || !frames.length) {
      return;
    }

    stopHeapAnimation();
    pageState.heapAnimation.active = true;

    for (let index = 0; index < frames.length; index += 1) {
      pageState.heapAnimation.frame = frames[index];
      repaint();
      await sleep(scaledDelay(340));
    }

    await sleep(scaledDelay(120));
    stopHeapAnimation();
    repaint();
  }

  repaint();
  refreshHierPrintfConsole(-1);
  invalidateTrace("Usa Ejecutar operación o activa Paso a paso.");

  operationSelect.addEventListener("change", () => {
    selected = operations.find((op) => op.name === operationSelect.value) || null;
    buildOperationInputs(selected, inputsContainer);
    updateHierDidacticPanel(model, selected ? selected.name : "");
    invalidateTrace("Operacion cambiada. Ejecuta nuevamente.");
    writePresentation({cursor:-1});
  });

  inputsContainer.addEventListener("input", () => {
    invalidateTrace("Entradas cambiadas. Ejecuta nuevamente.");
    writePresentation({cursor:-1});
  });

  learningLevel?.addEventListener("change",()=>{renderHierPedagogy(currentPedagogyFrame,learningLevel.value);writePresentation();});
  guidedExample?.addEventListener("change",()=>{const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample.value);if(exampleLesson)exampleLesson.textContent=example?example.lesson:"Los ejemplos construyen el estado mediante operaciones públicas reales.";});
  loadExampleButton?.addEventListener("click",async()=>{
    const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample?.value); if(!example){showHierMessage("Selecciona un ejemplo guiado.",false);return;}
    pendingExecution=true;setSimulationButtonsEnabled();loadExampleButton.disabled=true;
    try{
      const resetResponse=await fetch(form.dataset.resetUrl,{method:"POST"}); const resetData=await resetResponse.json(); let lastState=resetData.visual_state||null;
      for(const value of example.seed||[]){const response=await fetch(form.dataset.operateUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({operation:"insertar",payload:{value}})});const data=await response.json();if(!data.success)throw new Error(data.message||"No se pudo preparar el ejemplo.");lastState=data.visual_state;}
      if(lastState){model.visual_state=lastState;pageState.visualState=lastState;repaint();}
      selected=operations.find((op)=>op.name===example.operation)||selected;operationSelect.value=selected.name;buildOperationInputs(selected,inputsContainer);selected.inputs.forEach((field)=>{const input=hById(`h-field-${field.name}`);if(input&&Object.prototype.hasOwnProperty.call(example.payload||{},field.name))input.value=example.payload[field.name];});
      actionHistory.length=0;(example.seed||[]).forEach((value)=>hPushUniqueHistoryEntry(actionHistory,createHierHistoryEntry(getHierSubroutineName(model,"insertar","Insertar"),`value=${value}`,"Preparación del ejemplo.","insertar",{value}),{allowRepeated:model.id==="binary_heap"}));renderHierHistory(actionHistory,historyBox,pageState.modelId,model.didactic);updateHierDidacticPanel(model,selected.name);invalidateTrace("Ejemplo preparado. Reproduce la operación objetivo.");writePresentation({cursor:-1});showHierMessage(`Ejemplo preparado: ${example.lesson}`,true);window.MultipleInput?.stateChanged?.();
    }catch(error){showHierMessage(error.message||"No fue posible preparar el ejemplo.",false);}finally{pendingExecution=false;loadExampleButton.disabled=false;setSimulationButtonsEnabled();}
  });

  async function executeOperationAndLoadTrace(current, payload, selectionKey, options) {
    pendingExecution = true;
    setSimulationButtonsEnabled();
    if (resetButton) {
      resetButton.disabled = true;
    }

    let comparePath = [];
    let compareFound = false;
    let compareDirections = [];
    let rotationHint = null;
    let heapFrames = [];
    try {
      showHierMessage("Ejecutando subrutina...", true);
      const response = await (options?.multiple ? window.MultipleInput.fetchUnit : fetch)(form.dataset.operateUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: current.name, payload }),
      });
      const data = await response.json();
      if (data.execution_trace?.execution_started === false
          || data.execution_trace?.validation?.accepted === false) {
        // Host validation never entered C: keep the previous frame/history and
        // do not defer an error behind an empty trace or invent fallback steps.
        tracePlayer?.pause(true);
        showHierMessage(data.message, false);
        if (simStatus) simStatus.textContent = "La operacion no se ejecuto; el estado y la traza anterior permanecen sin cambios.";
        return options?.multiple ? data : null;
      }
      updateHierDidacticPanel(model, current.name);
      const finalOnly = Boolean(options && options.finalOnly);
      const hasExecutionTrace = Boolean(!finalOnly && data.execution_trace && tracePlayer);
      const deferQueryResult = hasExecutionTrace && ((pageState.modelId === "red_black" && ["buscar", "inorden", "altura", "validar", "limpiar", "insertar", "eliminar"].includes(current.name)) || (pageState.modelId === "abb" && current.name === "validar") || (pageState.modelId === "avl" && ["altura", "buscar", "inorden", "minimo", "maximo", "limpiar", "validar", "insertar", "eliminar"].includes(current.name)) || (pageState.modelId === "binary_heap" && ["raiz", "a_lista", "limpiar", "insertar", "extraer_raiz"].includes(current.name)));
      consoleState.resultMessage = deferQueryResult ? { text: data.message, operation: current.name, success: Boolean(data.success) } : null;
      showHierMessage(deferQueryResult ? (current.name === "validar" ? "Validacion preparada: resultado pendiente hasta completar la traza." : current.name === "limpiar" ? "Limpieza preparada: resultado pendiente hasta completar la traza." : current.name === "insertar" ? "Insercion preparada: resultado pendiente hasta completar la traza." : current.name === "eliminar" ? "Eliminacion preparada: resultado pendiente hasta completar la traza." : current.name === "extraer_raiz" ? "Extraccion preparada: resultado pendiente hasta completar la traza." : "Consulta preparada: resultado pendiente hasta completar la traza.") : data.message, deferQueryResult ? true : Boolean(data.success));
      window.ConsoleHistory?.setHistory(printfConsole, data.history);
      if (hasExecutionTrace) {
        consoleState.trace = data.execution_trace;
        consoleState.fallbackMessage = "";
        if (pageState.modelId === "red_black") {
          pageState.rnTimeline = rbBuildTimelineFromTrace(data.execution_trace);
          pageState.rnTimelineIndex = -1;
        }
        tracePlayer.loadTrace(data.execution_trace);
        const firstStep = data.execution_trace
          && Array.isArray(data.execution_trace.steps)
          && data.execution_trace.steps.length
          ? data.execution_trace.steps[0]
          : null;
        if (firstStep && firstStep.state_snapshot) {
          pageState.visualState = firstStep.state_snapshot;
          pageState.compareState = null;
          pageState.rotationVisualHint = null;
          pageState.rotationTextHint = null;
          pageState.traceAtEnd = false;
          repaint();
        }
        traceSelectionKey = selectionKey;
      } else {
        // API feedback is not stdout. Fast mode displays only the output
        // recorded by the executed C path, including an explicitly empty path.
        consoleState.trace = data.execution_trace || null;
        consoleState.fallbackMessage = "";
        const consoleCursor = finalOnly && Array.isArray(data.execution_trace?.steps)
          ? data.execution_trace.steps.length - 1 : -1;
        refreshHierPrintfConsole(consoleCursor);
        if (!finalOnly) {
          await simulateHierDidacticExecution({
            modelId: pageState.modelId,
            operation: current.name,
            payload,
            sizeBefore: Number(pageState?.visualState?.size || 0),
            comparePath,
            compareFound,
            compareDirections,
            success: Boolean(data.success),
            result: data.result,
            message: data.message,
            playbackSpeed,
          });
        }
        traceSelectionKey = "";
      }
      const payloadText = summarizeHierPayload(payload);
      const subroutine = getHierSubroutineName(model, current.name, current.label);
      hPushUniqueHistoryEntry(
        actionHistory,
        createHierHistoryEntry(
          subroutine,
          payloadText || "-",
          data.message,
          current.name,
          payload,
          { pendingTrace: hasExecutionTrace, success: Boolean(data.success) },
        ),
        { allowRepeated: pageState.modelId === "avl" || pageState.modelId === "binary_heap" || pageState.modelId === "red_black" || (pageState.modelId === "abb" && ["contar_hojas", "validar"].includes(current.name)) },
      );
      renderHierHistory(actionHistory, historyBox, pageState.modelId, model.didactic);
      if (data.visual_state) {
        model.visual_state = data.visual_state;
        let traceRotationHint = null;
        if (data.execution_trace && Array.isArray(data.execution_trace.steps)) {
          const stepWithRotation = data.execution_trace.steps.find(
            (step) => step && step.debug && step.debug.rotation_hint,
          );
          traceRotationHint = stepWithRotation && stepWithRotation.debug
            ? stepWithRotation.debug.rotation_hint
            : null;
        }
        const effectiveRotationHint = data.success ? traceRotationHint : null;
        const execution = {
          operation: current.name,
          result: data.result,
          rotation_hint: effectiveRotationHint,
        };
        if (hasExecutionTrace) {
          pageState.pendingExecution = execution;
          pageState.lastExecution = null;
          pageState.rotationTextHint = null;
          pageState.rotationVisualHint = null;
        }
        if (!hasExecutionTrace) {
          if (comparePath.length) {
            if (!finalOnly) {
              await animateComparison(comparePath);
            }
          }
          if (data.success && heapFrames.length) {
            if (!finalOnly) {
              await animateHeapFrames(heapFrames);
            }
          }
        }
        if (!hasExecutionTrace) {
          // A normal batch commits a complete final frame, not an unfinished rotation tween.
          applyState(data.visual_state, options?.multiple && finalOnly ? null : execution);
          if (simStatus && finalOnly) {
            simStatus.textContent = "Modo rapido: se aplico el resultado final de la operacion.";
          }
        }
      }
      if (model.id === "red_black" && data.success) {
        model.history = data.history;
        if (current.name === "validar" && hasExecutionTrace) {
          rnValidatorCache = { trace: data.execution_trace, history: rnDigest(data.history), state: rnDigest(data.visual_state), source: model.didactic?.operations?.validar, selectionKey, cursor: traceCursor, message: data.message, result: data.result };
          writeRNValidatorCache();
        } else clearRNValidatorCache();
      }
      if (!options?.multiple && data.success && current.mutates) window.MultipleInput?.stateChanged?.();
      return data;
    } catch (_error) {
      showHierMessage("No fue posible completar la operacion.", false);
      return null;
    } finally {
      pendingExecution = false;
      if (resetButton) {
        resetButton.disabled = false;
      }
      setSimulationButtonsEnabled();
    }
  }

  async function ensureTraceForCurrentSelection() {
    const current = operations.find((op) => op.name === operationSelect.value);
    if (!current) {
      showHierMessage("Debes seleccionar una operacion valida.", false);
      return null;
    }
    const payload = collectPayload(current);
    const selectionKey = buildSelectionKey(current, payload);
    if (tracePlayer && tracePlayer.hasTrace() && traceSelectionKey === selectionKey) {
      return { current, payload, selectionKey };
    }
    const data = await executeOperationAndLoadTrace(current, payload, selectionKey);
    if (!data) {
      return null;
    }
    return { current, payload, selectionKey };
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!isStepByStepEnabled()) {
      const current = operations.find((op) => op.name === operationSelect.value);
      if (!current) {
        return;
      }
      const payload = collectPayload(current);
      const selectionKey = buildSelectionKey(current, payload);
      await executeOperationAndLoadTrace(current, payload, selectionKey, { finalOnly: true });
      return;
    }
    const ready = await ensureTraceForCurrentSelection();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.playFromStart();
  });

  resetButton?.addEventListener("click", async () => {
    if(!window.confirm("¿Restablecer el TAD jerárquico y borrar su historial de esta sesión?"))return;
    stopTreeTransition();
    stopHeapAnimation();
    const response = await fetch(form.dataset.resetUrl, { method: "POST" });
    const data = await response.json();
    if (data.success) { clearRNValidatorCache(); window.ConsoleHistory?.reset(printfConsole); }
    showHierMessage(data.message, Boolean(data.success));
    updateHierDidacticPanel(model, selected ? selected.name : "");
    actionHistory.length = 0;
    renderHierHistory(actionHistory, historyBox, pageState.modelId, model.didactic);
    if (data.visual_state) {
      model.visual_state = data.visual_state;
      applyState(data.visual_state, null);
    }
    invalidateTrace("Usa Ejecutar operación o activa Paso a paso.");
    if (data.success) window.MultipleInput?.stateChanged?.();
  });

  simPlayButton?.addEventListener("click", async () => {
    const current = operations.find((op) => op.name === operationSelect.value);
    if (!current || !isCurrentSelectionValid()) { form.reportValidity?.(); return; }
    const payload = collectPayload(current);
    const selectionKey = buildSelectionKey(current, payload);
    const data = await executeOperationAndLoadTrace(current, payload, selectionKey, { finalOnly: !isStepByStepEnabled() });
    if (data && isStepByStepEnabled() && tracePlayer?.hasTrace()) tracePlayer.reset();
  });

  simPrevButton?.addEventListener("click", () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    tracePlayer?.prev();
  });

  simStepButton?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    const ready = await ensureTraceForCurrentSelection();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    const pendingDecision = predictionController?.sync();
    if (practiceMode?.checked && pendingDecision?.index === traceCursor + 1) {
      syncPredictionUI();
      if (predictionFeedback) predictionFeedback.textContent = "Antes de ejecutar esta condición, predice o continúa sin responder. El estado visible aún es el anterior.";
      const panel = predictionSelect?.closest("details"); if (panel) panel.open = true;
      return;
    }
    await tracePlayer.step();
  });

  prepareButton?.addEventListener("click",async()=>{const ready=await ensureTraceForCurrentSelection();if(ready){tracePlayer?.reset();showHierMessage("Ejecución preparada en el estado inicial.",true);}});
  pauseButton?.addEventListener("click",()=>tracePlayer?.pause());
  homeButton?.addEventListener("click",()=>tracePlayer?.seek(-1));
  endButton?.addEventListener("click",()=>tracePlayer?.seek(tracePlayer.getTotalSteps()-1));
  repeatButton?.addEventListener("click",async()=>{tracePlayer?.reset();await tracePlayer?.playFromStart();});
  progressSlider?.addEventListener("input",()=>tracePlayer?.seek(Number(progressSlider.value)));
  predictionController = createHierPredictionController(() => tracePlayer?.hasTrace() ? consoleState.trace : null, () => traceCursor);
  function syncPredictionUI() {
    if (!predictionController) return;
    const pending = predictionController.sync();
    const key = pending ? String(pending.index) : "none";
    if (key !== predictionTargetKey || predictionTraceRef !== consoleState.trace) {
      predictionTargetKey = key; predictionTraceRef = consoleState.trace;
      if (predictionSelect) predictionSelect.innerHTML = '<option value="">Elige una respuesta</option>' + (pending?.options || []).map(option => `<option value="${option.value}">${hEscape(option.label)}</option>`).join("");
      if (predictionFeedback) predictionFeedback.textContent = "";
    }
    if (predictionSelect) predictionSelect.disabled = !pending;
    if (checkPrediction) { checkPrediction.disabled = !pending; checkPrediction.textContent = "Comprobar y revelar decisión"; }
    if (hintButton) hintButton.disabled = !pending;
    if (skipPrediction) { skipPrediction.disabled = !pending; skipPrediction.textContent = "Revelar decisión sin responder"; }
    const prompt = hById("hier-prediction-prompt");
    if (prompt) prompt.textContent = pending?.prompt || "No hay una próxima decisión con condición C registrada. Ejecuta una operación en modo paso a paso o sigue navegando.";
    if (practiceCover) practiceCover.hidden = true;
    visualContainer.classList.remove("hier-practice-hidden");
  }
  practiceMode?.addEventListener("change", syncPredictionUI);
  checkPrediction?.addEventListener("click", () => {
    const result = predictionController.answer(predictionSelect?.value);
    if (!result) { if (predictionFeedback) predictionFeedback.textContent = "Selecciona una respuesta para la próxima decisión."; return; }
    if (result.counted) { conceptualProgress.attempts += 1; if (result.correct) conceptualProgress.correct += 1; renderConceptualProgress(); }
    tracePlayer.seek(result.index);
    if (predictionFeedback) predictionFeedback.textContent = `${result.correct ? "Correcto" : "No coincide"}: condición del paso ${result.index + 1} = ${result.label}. Decisión revelada.${result.counted ? "" : " Ya se registró este intento; no se puntúa de nuevo."}`;
  });
  hintButton?.addEventListener("click", () => { if (predictionFeedback) predictionFeedback.textContent = predictionController.hint(); });
  skipPrediction?.addEventListener("click", () => {
    const result = predictionController.skip(); if (!result) return;
    tracePlayer.seek(result.index);
    if (predictionFeedback) predictionFeedback.textContent = `Decisión del paso ${result.index + 1} revelada sin responder; no suma intentos.`;
  });
  resetProgress?.addEventListener("click", () => { conceptualProgress = {attempts:0,correct:0}; renderConceptualProgress(); if (predictionFeedback) predictionFeedback.textContent = "Progreso conceptual reiniciado."; });
  syncPredictionUI();
  function compareStateSummary(side,step){return renderHierComparisonState(side,step);}
  function renderHierComparison(){if(!hierarchicalComparison||!compareGrid)return;if(hierarchicalComparison.kind==="traversals"){compareGrid.innerHTML=renderHierComparisonShape(hierarchicalComparison.state || {}, "abb").html + hierarchicalComparison.traversals.map((item)=>`<article class="hier-compare-card"><h4>${hEscape(item.name)}</h4><p>${hEscape(item.stack_rule)}</p><p><strong>Orden de visita:</strong> <code>${hEscape(item.values.join(" → "))}</code></p></article>`).join("");}else{const cursor=Math.max(0,Number(compareProgress?.value||0));const leftStep=hierarchicalComparison.left.timeline[cursor]||hierarchicalComparison.left.timeline.at(-1);const rightStep=hierarchicalComparison.right.timeline[cursor]||hierarchicalComparison.right.timeline.at(-1);compareGrid.innerHTML=compareStateSummary(hierarchicalComparison.left,leftStep)+compareStateSummary(hierarchicalComparison.right,rightStep);}if(compareConclusion)compareConclusion.textContent=`${hierarchicalComparison.conclusion} Entrada, forma y estados de ambos lados se mantuvieron aislados.`;}
  compareRun?.addEventListener("click",async()=>{const values=String(compareValues?.value||"").split(/[,\s]+/).filter(Boolean).map(Number);try{const response=await fetch(compareSection?.dataset.compareUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({kind:compareKind?.value,values})});const data=await response.json();if(!response.ok||!data.success)throw new Error(data.message||"No se pudo comparar.");hierarchicalComparison=data;if(compareInput)compareInput.textContent=`Entrada inmutable: [${data.input.join(", ")}]`;if(compareProgress){const count=data.left?.timeline?.length||1;compareProgress.max=String(Math.max(0,count-1));compareProgress.value="0";compareProgress.disabled=data.kind==="traversals";}renderHierComparison();syncComparisonNavigation();if(announcer)announcer.textContent="Comparación jerárquica preparada.";}catch(error){if(compareConclusion)compareConclusion.textContent=error.message;}});
  function syncComparisonNavigation() {
    const previous = hById("hier-compare-prev"), next = hById("hier-compare-next");
    const available = Boolean(hierarchicalComparison && hierarchicalComparison.kind !== "traversals");
    const cursor = Number(compareProgress?.value || 0), last = Number(compareProgress?.max || 0);
    if (previous) previous.disabled = !available || cursor <= 0;
    if (next) next.disabled = !available || cursor >= last;
    const label = hById("hier-compare-position-label");
    if (label) label.textContent = available ? `Paso ${cursor + 1} de ${last + 1}` : "Sin pasos sincronizados";
  }
  hById("hier-compare-prev")?.addEventListener("click", () => {
    compareProgress.value = String(Math.max(0, Number(compareProgress.value) - 1));
    renderHierComparison(); syncComparisonNavigation();
  });
  hById("hier-compare-next")?.addEventListener("click", () => {
    compareProgress.value = String(Math.min(Number(compareProgress.max), Number(compareProgress.value) + 1));
    renderHierComparison(); syncComparisonNavigation();
  });
  compareProgress?.addEventListener("input", () => { renderHierComparison(); syncComparisonNavigation(); });
  compareKind?.addEventListener("change",()=>{hierarchicalComparison=null;if(compareProgress)compareProgress.disabled=true;syncComparisonNavigation();});
  exportImage?.addEventListener("click", async () => {
    if (exportImage.disabled) return;
    const originalText = exportImage.textContent;
    exportImage.disabled = true;
    exportImage.setAttribute("aria-busy", "true");
    try {
      const exported = await window.InterpreterRuntime.exportVisualStateAsJpg({
        target: hById("hier-visual-region"), quality: .9, scale: 1,
        onProgress: (text) => { exportImage.textContent = text; },
      });
      window.InterpreterRuntime.downloadJpg(exported.dataUrl, exported.suggestedName);
      showHierMessage("Captura JPG preparada; revisa las descargas del navegador.", true);
    } catch (error) { showHierMessage(error.message || "No se pudo exportar la captura.", false); }
    finally {
      exportImage.disabled = false;
      exportImage.removeAttribute("aria-busy");
      exportImage.textContent = originalText;
    }
  });
  exportSummary?.addEventListener("click",()=>{const current=operations.find((op)=>op.name===operationSelect.value);const summary={schema:"hierarchical-learning-summary/v1",structure:model.id,operation:operationSelect.value,payload:current?collectPayload(current):{},level:learningLevel?.value,cursor:tracePlayer?.getCursor()??-1,total_steps:tracePlayer?.getTotalSteps()??0,frame:currentPedagogyFrame,state:pageState.visualState,practice:conceptualProgress,comparison:hierarchicalComparison};const url=URL.createObjectURL(new Blob([JSON.stringify(summary,null,2)],{type:"application/json"}));const link=document.createElement("a");link.href=url;link.download=`${model.id}-resumen.json`;link.click();URL.revokeObjectURL(url);});
  document.addEventListener("keydown",async(event)=>{if(event.key===" " && event.target instanceof Element && event.target.closest("button, summary, a, [role=button]"))return;if(event.target instanceof Element && event.target.closest("#hier-variables-view"))return;if(event.target instanceof HTMLInputElement||event.target instanceof HTMLSelectElement||event.target instanceof HTMLTextAreaElement)return;if(event.key==="ArrowLeft"){event.preventDefault();tracePlayer?.prev();}else if(event.key==="ArrowRight"){event.preventDefault();await tracePlayer?.step();}else if(event.key==="Home"){event.preventDefault();tracePlayer?.seek(-1);}else if(event.key==="End"){event.preventDefault();tracePlayer?.seek(tracePlayer.getTotalSteps()-1);}else if(event.key===" "){event.preventDefault();tracePlayer?.pause();}});
  if(window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches&&speedSlider){speedSlider.value="-2";setPlaybackSpeed(speedSlider.value);}

  window.MultipleInput?.mount({
    model, form, player: tracePlayer, isBusy: () => pendingExecution,
    sync: setSimulationButtonsEnabled,
    select: (operation) => { operationSelect.value=operation; operationSelect.dispatchEvent(new Event("change")); },
    execute: (value, finalOnly) => {
      const current=operations.find(op=>op.name===operationSelect.value);
      const payload={value:String(value)};
      const field=document.getElementById("h-field-value"); if(field) field.value=String(value);
      return executeOperationAndLoadTrace(current,payload,buildSelectionKey(current,payload),{finalOnly,multiple:true});
    },
  });

  stepToggle?.addEventListener("change", () => {
    syncStepModeUi();
    tracePlayer?.pause(true);
    if (tracePlayer?.hasTrace()) tracePlayer.seek(isStepByStepEnabled() ? -1 : tracePlayer.getTotalSteps() - 1);
    setSimulationButtonsEnabled();
  });

  // A saved query restores its original frames; navigation never executes it again.
  if (model.id === "red_black" && selected?.name === "validar" && tracePlayer) {
    try {
      const saved = JSON.parse(sessionStorage.getItem(rnValidatorTraceKey) || "null");
      if (saved && saved.history === rnDigest(model.history) && saved.state === rnDigest(model.visual_state) && saved.source === model.didactic?.operations?.validar && saved.selectionKey === buildSelectionKey(selected, collectPayload(selected))) {
        const cursor = saved.cursor;
        rnValidatorCache = saved;
        traceSelectionKey = saved.selectionKey;
        consoleState.trace = saved.trace;
        consoleState.resultMessage = {text: saved.message, operation: "validar", success: true};
        pageState.rnTimeline = rbBuildTimelineFromTrace(saved.trace);
        pageState.pendingExecution = {operation: "validar", result: saved.result};
        tracePlayer.loadTrace(saved.trace);
        if (stepToggle) stepToggle.checked = true;
        syncStepModeUi();
        tracePlayer.seek(Number.isInteger(cursor) ? Math.max(-1, Math.min(cursor, saved.trace.steps.length-1)) : -1);
      } else if (saved) clearRNValidatorCache();
    } catch (_error) { clearRNValidatorCache(); }
  }


}


// Presentation-only classroom v1; existing render targets retain their identity.
function hierMountClassroomView() {
  if (!window.ClassroomView) return;
  const root = document.querySelector(".hier-primary-workspace");
  if (!root) return;
  document.getElementById("hier-code-region")?.classList.add("classroom-code");
  document.getElementById("hier-code-region")?.classList.remove("didactic-technical");
  const history = document.getElementById("action-history");
  const consoleNode = document.getElementById("hier-printf-console");
  const record = document.getElementById("tad-record");
  const results = [
    {label:"Consola C (printf)",panel:consoleNode?.closest("section"),code:consoleNode,getText:()=>consoleNode?.dataset.consoleCopy || ""},
    {label:"main.c del historial",panel:history?.parentElement,code:history,getText:()=>history?.dataset.rawCode || ""},
    {label:"Estructura del TAD",panel:record?.parentElement,code:record,getText:()=>record?.dataset.rawCode ?? record?.textContent ?? ""}
  ];
  results.forEach(entry=>{
    entry.panel?.classList.remove("didactic-technical");
    for(let node=entry.panel?.parentElement;node && node.tagName!=="ARTICLE";node=node.parentElement) {
      node.classList.remove("didactic-technical", "seq-pilot-collapsed");
      node.hidden = false;
      if(node.tagName==="DETAILS") node.open=true;
    }
  });
  window.ClassroomView.mount({root,visual:"#hier-visual-region",stage:"#visual-state",code:"#op-pseudocode",memory:[".abb-instruction-memory", ".hier-retired-memory"],results,key:"hierarchical"});
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.HIER_VIEW_MODEL) {
    initHierPage(window.HIER_VIEW_MODEL);
    hierMountClassroomView();
  }
});
