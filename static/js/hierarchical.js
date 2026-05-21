"use strict";

// Control temporal de UI: mantener oculta la linea de tiempo RN.
const H_SHOW_RN_TIMELINE = false;

function hById(id) {
  return document.getElementById(id);
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

function hPushUniqueHistoryEntry(history, entry) {
  if (!Array.isArray(history) || !entry) {
    return false;
  }
  const last = history.length ? history[history.length - 1] : null;
  if (hBuildHistoryEntrySignature(last) === hBuildHistoryEntrySignature(entry)) {
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
        return `<span class="code-line" data-line="${index}">${highlighted.html || "&nbsp;"}</span>`;
      })
      .join("");
  }

  return lines
    .map((line, index) => `<span class="code-line" data-line="${index}">${hEscape(line) || "&nbsp;"}</span>`)
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
    current.scrollIntoView({ block: "nearest", behavior: "smooth" });
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

    if (!leftNode) {
      const dx = rightNode ? Math.max(baseDx, Math.abs(rightNode.x - node.x)) : baseDx;
      nullLeaves.push({
        key: `${node.key}-nil-left-${index}`,
        parentX: node.x,
        parentY: node.y,
        x: node.x - dx,
        y: childY,
      });
    }

    if (!rightNode) {
      const dx = leftNode ? Math.max(baseDx, Math.abs(node.x - leftNode.x)) : baseDx;
      nullLeaves.push({
        key: `${node.key}-nil-right-${index}`,
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

  let svg = `<svg class="viz-tree-svg" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">`;

  nodes.forEach((node) => {
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

    svg += `<circle cx="${node.x + offsetX}" cy="${node.y}" r="24" class="${nodeClass}" />`;
    svg += `<text x="${node.x + offsetX}" y="${node.y + 6}" text-anchor="middle" class="viz-tree-text">${hEscape(node.value)}</text>`;

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

    svg += `<circle cx="${node.x + offsetX}" cy="${node.y}" r="24" class="${nodeClass}" style="opacity:${node.opacity};" />`;
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
      return `<span class="${className}">[${index}] ${hEscape(value)}</span>`;
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

  const treeOptions = {
    showBalanceFactor: modelId === "avl",
    showNullLeaves: modelId === "red_black",
    compareState,
    rotationHint: rotationVisualHint,
  };

  let html = `<div class="viz-canvas"><div class="viz-meta"><strong>${hEscape(state.title)}</strong> | Tamano: ${hEscape(state.size ?? 0)}</div>`;

  if (typeof state.validation === "boolean") {
    html += `<div class="viz-validation">Validacion: ${state.validation ? "OK" : "ERROR"}</div>`;
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
    html += "<div class=\"viz-meta\">Reglas RN: raiz negra, sin rojos consecutivos y misma altura negra en todos los caminos.</div>";
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

  if (modelId === "binary_heap" || state.kind === "heap") {
    const heapArray = heapFrame && Array.isArray(heapFrame.array) ? heapFrame.array : (state.array || []);
    const heapRoot = heapArrayToTreeNode(heapArray, 0);
    const heapCompareState = heapFrame ? {
      pathKeys: (heapFrame.visitedIndices || []).map((index) => `idx-${index}`),
      index: Math.max(0, (heapFrame.visitedIndices || []).length - 1),
      activeKeys: (heapFrame.activeIndices || []).map((index) => `idx-${index}`),
    } : treeOptions.compareState;
    html += "<h4>Representacion en arreglo</h4>";
    html += renderHeapArrayFrame(heapArray, heapFrame);
    if (heapFrame && heapFrame.note) {
      html += `<p class="viz-sim-note">${hEscape(heapFrame.note)}</p>`;
    }
    html += "<h4>Representacion en arbol</h4>";
    html += transitionData
      ? renderTreeTransitionSvg(transitionData, { ...treeOptions, compareState: heapCompareState })
      : drawTreeSvgFromNodes(flattenTree(heapRoot), { ...treeOptions, compareState: heapCompareState });
  } else {
    html += transitionData
      ? renderTreeTransitionSvg(transitionData, treeOptions)
      : drawTreeSvgFromNodes(flattenTree(state.root), treeOptions);
  }

  if (state.traversals) {
    html += "<div class=\"viz-traversals\">";
    Object.keys(state.traversals).forEach((name) => {
      html += `<p><strong>${hEscape(name)}:</strong> ${hEscape(JSON.stringify(state.traversals[name]))}</p>`;
    });
    const lastResult = formatHierResult(lastExecution);
    if (lastResult) {
      html += lastResult;
    }
    html += "</div>";
  }

  html += "</div>";
  container.innerHTML = html;
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
  renderHierDidacticCode(pseudoBox, opMap[selectedOp] || fallback, codeTitle);
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
    return `int niveles_${index} = abb_contarNiveles(arbol);`;
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
    return "/* El TAD nuevo no expone abb_es_valido(). */";
  }
  if (entry.operation === "limpiar") {
    return "abb_liberarArbol(arbol); arbol = NULL;";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function avlMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = Object.prototype.hasOwnProperty.call(payload, "value") ? String(payload.value).trim() : "";

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
    return "/* El TAD nuevo no expone avl_maximo(). */";
  }
  if (entry.operation === "altura") {
    return `int altura_${index} = avl_altura(arbol);`;
  }
  if (entry.operation === "inorden") {
    return "avl_verArbol(arbol, 0);";
  }
  if (entry.operation === "validar") {
    return "/* El TAD nuevo no expone avl_es_valido(). */";
  }
  if (entry.operation === "limpiar") {
    return "avl_liberarAVL(arbol); arbol = NULL;";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function redBlackMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = Object.prototype.hasOwnProperty.call(payload, "value") ? String(payload.value).trim() : "";

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
    return "rbt_verArbol(arbol, 0);";
  }
  if (entry.operation === "altura") {
    return "/* El TAD nuevo no expone rbt_altura(). */";
  }
  if (entry.operation === "validar") {
    return "/* El TAD nuevo no expone rbt_es_valido(). */";
  }
  if (entry.operation === "limpiar") {
    return "rbt_liberar(arbol); arbol = NULL;";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function binaryHeapMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const value = Object.prototype.hasOwnProperty.call(payload, "value") ? String(payload.value).trim() : "";

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
    return `int buffer_${index}[256]; int usados_${index} = monticulo_copiar_valores(&monticulo, buffer_${index}, 256);`;
  }
  if (entry.operation === "limpiar") {
    return "monticulo_destruir(&monticulo); monticulo_inicializar(&monticulo, MONTICULO_MIN, 10);";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function buildHierMainCode(modelId, history) {
  const lines = [];
  lines.push("int main(void) {");
  lines.push("    // Declaracion de la estructura");

  if (modelId === "abb") {
    lines.push("    ABBNodo *arbol = NULL;");
  } else if (modelId === "avl") {
    lines.push("    AVL arbol = NULL;");
  } else if (modelId === "red_black") {
    lines.push("    RBT arbol = NULL;");
  } else if (modelId === "binary_heap") {
    lines.push("    MonticuloBinario monticulo;");
    lines.push("    monticulo_inicializar(&monticulo, MONTICULO_MIN, 10);");
  } else {
    lines.push("    // Estructura jerarquica inicializada");
  }

  lines.push("");
  lines.push("    // Historial de ejecucion del usuario");
  history.forEach((entry, index) => {
    if (!entry || typeof entry === "string") {
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
    lines.push(`    ${call}`);
    const visibleResult = getHierEntryVisibleResult(entry);
    if (visibleResult) {
      lines.push(`    printf("${hToCStringLiteral(visibleResult)}\\n");`);
      lines.push(`    // ${visibleResult}`);
    }
  });

  if (modelId === "abb") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    // abb_liberarArbol(arbol);");
  } else if (modelId === "avl") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    // avl_liberarAVL(arbol);");
  } else if (modelId === "red_black") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    // rbt_liberar(arbol);");
  } else if (modelId === "binary_heap") {
    lines.push("    // Al finalizar el programa:");
    lines.push("    // monticulo_destruir(&monticulo);");
  }
  lines.push("    return 0;");
  lines.push("}");
  return lines.join("\n");
}

function renderHierHistory(history, container, modelId, didactic) {
  if (!container) {
    return;
  }
  if (!history.length) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }

  const codeTitle = didactic && didactic.code_title ? String(didactic.code_title) : "";
  if (codeTitle.toLowerCase().includes("codigo c")) {
    const code = buildHierMainCode(modelId, history);
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

  if (!form || !operationSelect || !inputsContainer || !visualContainer) {
    return;
  }

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
    const out = [];
    const traversalValues = hGetTraversalResultValuesFromTrace(trace);
    let traversalValueIndex = 0;
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const messages = hExtractPrintfMessagesFromLine(step.line_text);
      messages.forEach((msg) => {
        // En recorridos recursivos del ABB, traducir `printf("%d ", ...)`
        // a valores concretos visitados, evitando mostrar el literal "%d".
        if (hHasPrintfFormatSpecifier(msg)) {
          if (hIsOnlyPrintfSpecifier(msg) && traversalValueIndex < traversalValues.length) {
            hPushUniqueConsoleLine(out, `[printf] ${traversalValues[traversalValueIndex]}`);
            traversalValueIndex += 1;
            return;
          }
          // Si no podemos resolver el formato a un valor, omitimos ese ruido visual.
          return;
        }
        hPushUniqueConsoleLine(out, `[printf] ${msg}`);
      });
    }
    if (limit >= trace.steps.length - 1) {
      const finalMessage = String(trace.message || "").trim();
      if (finalMessage) {
        hPushUniqueConsoleLine(out, `[printf] ${finalMessage}`);
      }
    }
    return out;
  }

  function refreshHierPrintfConsole(cursor) {
    const lines = collectHierPrintfLines(consoleState.trace, cursor);
    renderHierPrintfConsole(
      printfConsole,
      lines,
      consoleState.fallbackMessage || "(sin salida printf en esta ruta)",
    );
  }

  operations.forEach((operation) => {
    const option = document.createElement("option");
    option.value = operation.name;
    option.textContent = operation.label;
    operationSelect.appendChild(option);
  });

  buildOperationInputs(selected, inputsContainer);
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
    );
  });
  renderHierHistory(actionHistory, historyBox, pageState.modelId, model.didactic);
  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: hById("op-pseudocode"),
      statusElement: simStatus,
      counterElement: hById("hier-sim-counter"),
      renderState: (stateSnapshot, stepMeta) => {
        stopTreeTransition();
        stopHeapAnimation();
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
          if (pageState.modelId === "red_black") {
            pageState.compareState = rbDidacticDelta(stepMeta, pageState.compareState);
          }
        } else {
          pageState.compareState = null;
          if (pageState.modelId === "red_black") {
            pageState.compareState = rbDidacticDelta(stepMeta, pageState.compareState);
          }
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
        pageState.rotationTextHint = (
          stepMeta
          && stepMeta.debug
          && stepMeta.debug.rotation_hint
        ) ? stepMeta.debug.rotation_hint : null;
        repaint();
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        const total = event && event.trace && Array.isArray(event.trace.steps)
          ? event.trace.steps.length
          : 0;
        pageState.traceAtEnd = total > 0 && cursor >= total - 1;
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
    consoleState.fallbackMessage = "";
    pageState.traceAtEnd = false;
    pageState.pendingExecution = null;
    pageState.rnTimeline = [];
    pageState.rnTimelineIndex = -1;
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
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
  invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");

  operationSelect.addEventListener("change", () => {
    selected = operations.find((op) => op.name === operationSelect.value) || null;
    buildOperationInputs(selected, inputsContainer);
    updateHierDidacticPanel(model, selected ? selected.name : "");
    invalidateTrace("Operacion cambiada. Ejecuta nuevamente.");
  });

  inputsContainer.addEventListener("input", () => {
    invalidateTrace("Entradas cambiadas. Ejecuta nuevamente.");
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
    if (
      isSearchLikeStructure(pageState.modelId)
      && (current.name === "insertar" || current.name === "eliminar" || current.name === "buscar")
    ) {
      const targetValue = normalizeCompareValue(payload.value);
      if (targetValue !== null) {
        const compareRoot = model.visual_state && model.visual_state.root ? model.visual_state.root : pageState.visualState.root;
        const compareResult = buildComparisonPath(compareRoot, targetValue);
        comparePath = compareResult.pathKeys;
        compareFound = Boolean(compareResult.found);
        compareDirections = Array.isArray(compareResult.directions) ? compareResult.directions : [];
        if (pageState.modelId === "avl" && current.name === "insertar") {
          rotationHint = inferAvlInsertionRotation(compareRoot, targetValue);
        }
        if (pageState.modelId === "avl" && current.name === "eliminar") {
          rotationHint = inferAvlDeletionRotation(compareRoot, targetValue);
        }
      }
    }
    if (pageState.modelId === "binary_heap") {
      heapFrames = buildHeapOperationFrames(
        current.name,
        payload,
        model.visual_state && Array.isArray(model.visual_state.array)
          ? model.visual_state.array
          : [],
      );
    }
    try {
      showHierMessage("Ejecutando subrutina...", true);
      const response = await fetch(form.dataset.operateUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: current.name, payload }),
      });
      const data = await response.json();
      showHierMessage(data.message, Boolean(data.success));
      updateHierDidacticPanel(model, current.name);
      const finalOnly = Boolean(options && options.finalOnly);
      const hasExecutionTrace = Boolean(!finalOnly && data.execution_trace && tracePlayer);
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
        consoleState.trace = null;
        consoleState.fallbackMessage = data.message || "(sin salida printf en esta ruta)";
        refreshHierPrintfConsole(-1);
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
          { pendingTrace: hasExecutionTrace },
        ),
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
        const effectiveRotationHint = data.success ? (traceRotationHint || rotationHint) : null;
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
          applyState(data.visual_state, execution);
          if (simStatus && finalOnly) {
            simStatus.textContent = "Modo rapido: se aplico el resultado final de la operacion.";
          }
        }
      }
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
    stopTreeTransition();
    stopHeapAnimation();
    const response = await fetch(form.dataset.resetUrl, { method: "POST" });
    const data = await response.json();
    showHierMessage(data.message, Boolean(data.success));
    updateHierDidacticPanel(model, selected ? selected.name : "");
    actionHistory.length = 0;
    renderHierHistory(actionHistory, historyBox, pageState.modelId, model.didactic);
    if (data.visual_state) {
      model.visual_state = data.visual_state;
      applyState(data.visual_state, null);
    }
    invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
  });

  simPlayButton?.addEventListener("click", async () => {
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
    await tracePlayer.step();
  });

  stepToggle?.addEventListener("change", () => {
    invalidateTrace(
      isStepByStepEnabled()
        ? "Modo paso a paso activado. Usa Reproducir o Siguiente paso."
        : "Modo rapido activado. Reproducir aplicara solo el resultado final.",
    );
  });

}

document.addEventListener("DOMContentLoaded", () => {
  if (window.HIER_VIEW_MODEL) {
    initHierPage(window.HIER_VIEW_MODEL);
  }
});
