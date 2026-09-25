"use strict";

function byId(id) {
  return document.getElementById(id);
}

function initSequentialResponsiveWorkspace() {
  const workspace = document.querySelector(".sequential-primary-workspace");
  const tabs = Array.from(document.querySelectorAll("[data-seq-tab]"));
  if (!workspace || !tabs.length) return;
  const storageKey = document.querySelector(".is-stack-pilot") ? "sequential-stack-workspace-tab-v2" : "sequential-active-tab";
  let saved = "visual";
  try { saved = window.sessionStorage.getItem(storageKey) || "visual"; } catch (_error) { saved = "visual"; }
  const activate = (name) => {
    const selected = name === "code" ? "code" : "visual";
    workspace.dataset.activeTab = selected;
    tabs.forEach((tab) => { const active = tab.dataset.seqTab === selected; tab.classList.toggle("is-active", active); tab.setAttribute("aria-selected", String(active)); });
    try { window.sessionStorage.setItem(storageKey, selected); } catch (_error) { /* optional */ }
  };
  tabs.forEach((tab) => tab.addEventListener("click", () => activate(tab.dataset.seqTab)));
  activate(saved);
}

function enhanceSequentialCodeNavigation(activeLine = null) {
  const code = byId("op-pseudocode");
  const list = byId("seq-function-list");
  const hide = byId("seq-hide-comments");
  if (!code || !list) return;
  const raw = String(code.dataset.rawCode || code.textContent || "");
  const rows = raw.replaceAll("\r\n", "\n").split("\n");
  const functions = [];
  const signature = /^\s*(?:static\s+)?(?:void|bool|int|size_t|ptr\w+|[A-Za-z_]\w*)\s+\**([A-Za-z_]\w*)\s*\(/;
  rows.forEach((row, index) => { const match = row.match(signature); if (match && !["if", "while", "for", "switch"].includes(match[1])) functions.push({ name: match[1], line: index }); });
  let inBlock = false;
  code.querySelectorAll(".code-line").forEach((line, index) => {
    const value = String(rows[index] || "").trim();
    const starts = value.startsWith("/*");
    line.classList.toggle("is-code-comment", inBlock || starts || value.startsWith("//") || value.startsWith("*"));
    if (starts && !value.includes("*/")) inBlock = true;
    if (inBlock && value.includes("*/")) inBlock = false;
  });
  code.classList.toggle("hide-code-comments", Boolean(hide?.checked));
  const active = [...functions].reverse().find((item) => Number.isInteger(activeLine) && item.line <= activeLine) || functions[0];
  list.innerHTML = functions.length ? functions.map((item) => `<li><button type="button" class="seq-function-link${active?.line === item.line ? " is-active" : ""}" data-line="${item.line}">${escapeHtml(item.name)}</button></li>`).join("") : '<li class="muted">Sin funciones detectadas</li>';
  list.querySelectorAll(".seq-function-link").forEach((button) => button.addEventListener("click", () => code.querySelector(`.code-line[data-line="${button.dataset.line}"]`)?.scrollIntoView({ block: "center" })));
}

function renderOperationInputs(operation, container) {
  container.innerHTML = "";
  if (!operation || !operation.inputs) {
    return;
  }

  operation.inputs.forEach((field) => {
    const wrapper = document.createElement("div");
    const label = document.createElement("label");
    label.setAttribute("for", `field-${field.name}`);
    label.textContent = field.label;

    const input = document.createElement("input");
    input.id = `field-${field.name}`;
    input.name = field.name;
    input.type = field.type === "number" ? "number" : "text";
    input.required = true;
    if (field.type === "number" && Object.prototype.hasOwnProperty.call(field, "min")) {
      input.min = String(field.min);
    }

    wrapper.appendChild(label);
    wrapper.appendChild(input);
    container.appendChild(wrapper);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function sequentialValue(value) {
  if (value === null || typeof value === "undefined") return "NULL";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function renderSequentialPedagogyFrame(frame, level) {
  const summary = byId("seq-pedagogy-summary");
  const conditionView = byId("seq-condition-view");
  const variableView = byId("seq-variable-view");
  const pointerView = byId("seq-pointer-view");
  const heapView = byId("seq-heap-view");
  const callView = byId("seq-call-view");
  if (!frame) return;
  const narration = frame.narration?.[level] || frame.narration?.intermediate || "";
  if (summary) summary.innerHTML = `<strong>${escapeHtml(frame.phase?.label || frame.concept)}</strong>: ${escapeHtml(narration)}<br><small>Invariante: ${escapeHtml(frame.invariant?.text || "")}</small>`;
  if (conditionView) {
    const condition = frame.condition;
    const loop = frame.loop;
    conditionView.innerHTML = condition
      ? `<code>${escapeHtml(condition.source)}</code><br>Sustitución: <code>${escapeHtml(condition.substituted)}</code><br>Resultado: <strong>${escapeHtml(sequentialValue(condition.result))}</strong><br>${escapeHtml(condition.consequence)}${loop?.active ? `<br>Ciclo: ${escapeHtml(loop.exit || "continúa")}` : ""}`
      : "Sin condición en este frame.";
  }
  const table = (headers, rows) => `<table class="seq-data-table"><thead><tr>${headers.map((item) => `<th>${escapeHtml(item)}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table>`;
  if (variableView) {
    const rows = (frame.variables || []).map((item) => `<tr><td><code>${escapeHtml(item.type)}</code></td><td>${escapeHtml(item.name)}</td><td>${escapeHtml(item.meaning)}</td><td>${escapeHtml(sequentialValue(item.previous))}</td><td>${escapeHtml(sequentialValue(item.value))}${item.changed ? " Δ" : ""}</td></tr>`);
    variableView.innerHTML = rows.length ? table(["Tipo", "Nombre", "Significado", "Anterior", "Actual"], rows) : "Sin variables.";
  }
  if (pointerView) {
    const rows = (frame.pointers || []).map((item) => `<tr><td><code>${escapeHtml(item.name)}</code></td><td>${escapeHtml(sequentialValue(item.previous_target))}</td><td>${escapeHtml(sequentialValue(item.target))}</td><td>${item.changed ? "reasignado" : escapeHtml(item.alias || "estable")}</td></tr>`);
    pointerView.innerHTML = rows.length ? table(["Puntero", "Destino anterior", "Destino nuevo", "Relación"], rows) : "Sin punteros activos en esta línea.";
  }
  if (heapView) {
    const transition = frame.heap_transition || {};
    const live = (transition.after || frame.heap_objects || []).map((item) => `<span class="seq-memory-object"><code>${escapeHtml(item.address || item.id)}</code> ${escapeHtml(sequentialValue(item.fields))} · ${escapeHtml(item.status || "linked")}</span>`);
    const freed = (transition.freed || []).map((item) => `<span class="seq-memory-object is-freed"><code>${escapeHtml(item.address || item.id)}</code> liberado</span>`);
    heapView.innerHTML = `<strong>Evento: ${escapeHtml(transition.kind || "stable")}</strong><div>${[...live, ...freed].join("") || "No hay objetos alcanzables."}</div>`;
  }
  if (callView) {
    const rows = (frame.call_stack || []).map((item) => `<tr><td><code>${escapeHtml(item.function)}</code></td><td>${escapeHtml(sequentialValue(item.parameters))}</td><td>${escapeHtml(sequentialValue(item.return))}</td><td>${escapeHtml(item.continuation)}</td></tr>`);
    callView.innerHTML = rows.length ? table(["Función", "Parámetros", "Retorno", "Continuación"], rows) : "Sin llamadas.";
  }
}

function toCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\", "\\\\")
    .replaceAll('"', '\\"')
    .replaceAll("\r", "")
    .replaceAll("\n", "\\n");
}

function decodeCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\\\", "\u0000")
    .replaceAll("\\n", "\n")
    .replaceAll("\\t", "\t")
    .replaceAll('\\"', '"')
    .replaceAll("\\r", "")
    .replaceAll("\u0000", "\\");
}

function extractPrintfMessagesFromLine(lineText) {
  const source = String(lineText || "");
  const regex = /printf\s*\(\s*"((?:\\.|[^"\\])*)"/g;
  const messages = [];
  let match = regex.exec(source);
  while (match) {
    const decoded = decodeCStringLiteral(match[1]).replace(/\n+$/g, "").trim();
    if (decoded) {
      messages.push(decoded);
    }
    match = regex.exec(source);
  }
  return messages;
}

function hasPrintfFormatSpecifier(text) {
  return /%[-+0-9.#hljztL]*[diuoxXfFeEgGaAcsp]/.test(String(text || ""));
}

function normalizeDidacticText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function pushUniqueConsoleLine(lines, line) {
  const normalized = normalizeDidacticText(line);
  if (!normalized) {
    return;
  }
  if (lines.length && normalizeDidacticText(lines[lines.length - 1]) === normalized) {
    return;
  }
  lines.push(line);
}

function buildHistoryEntrySignature(entry) {
  if (!entry || typeof entry === "string") {
    return "";
  }
  const subroutine = normalizeDidacticText(entry.subroutine);
  const payload = normalizeDidacticText(entry.payload);
  const result = normalizeDidacticText(entry.result);
  const operation = normalizeDidacticText(entry.operation);
  return `${subroutine}|${payload}|${result}|${operation}`;
}

function pushUniqueHistoryEntry(history, entry) {
  if (!Array.isArray(history) || !entry) {
    return false;
  }
  const last = history.length ? history[history.length - 1] : null;
  if (buildHistoryEntrySignature(last) === buildHistoryEntrySignature(entry)) {
    return false;
  }
  history.push(entry);
  return true;
}

function renderPrintfConsole(consoleEl, lines, fallbackText) {
  if (!consoleEl) {
    return;
  }
  const safeLines = Array.isArray(lines) ? lines : [];
  const hasOutput = safeLines.length > 0;
  const rows = hasOutput
    ? safeLines.map((line) => `<div class="console-line">${escapeHtml(line)}</div>`).join("")
    : `<div class="console-line muted">${escapeHtml(fallbackText || "(sin salida printf en esta ruta)")}</div>`;
  consoleEl.innerHTML = rows;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

const C_KEYWORDS = new Set([
  "if", "else", "for", "while", "do", "switch", "case", "default", "break",
  "continue", "return", "sizeof", "typedef", "struct", "enum", "union",
  "static", "const", "volatile", "extern", "goto", "NULL", "true", "false",
]);

const C_TYPES = new Set([
  "void", "int", "bool", "float", "double", "char", "short", "long",
  "signed", "unsigned", "size_t",
]);

function isIdentStart(ch) {
  return /[A-Za-z_]/.test(ch);
}

function isIdentChar(ch) {
  return /[A-Za-z0-9_]/.test(ch);
}

function nextNonSpaceChar(text, from) {
  let i = from;
  while (i < text.length && /\s/.test(text[i])) {
    i += 1;
  }
  return i < text.length ? text[i] : "";
}

function highlightCLine(line, state) {
  const text = String(line || "");
  const out = [];
  let i = 0;
  const inState = { inBlockComment: Boolean(state && state.inBlockComment) };

  if (/^\s*#/.test(text)) {
    return { html: `<span class="code-directive">${escapeHtml(text)}</span>`, state: inState };
  }

  while (i < text.length) {
    const ch = text[i];
    const next = i + 1 < text.length ? text[i + 1] : "";

    if (inState.inBlockComment) {
      const end = text.indexOf("*/", i);
      if (end === -1) {
        out.push(`<span class="code-comment">${escapeHtml(text.slice(i))}</span>`);
        i = text.length;
        break;
      }
      out.push(`<span class="code-comment">${escapeHtml(text.slice(i, end + 2))}</span>`);
      i = end + 2;
      inState.inBlockComment = false;
      continue;
    }

    if (ch === "/" && next === "/") {
      out.push(`<span class="code-comment">${escapeHtml(text.slice(i))}</span>`);
      i = text.length;
      break;
    }

    if (ch === "/" && next === "*") {
      const end = text.indexOf("*/", i + 2);
      if (end === -1) {
        out.push(`<span class="code-comment">${escapeHtml(text.slice(i))}</span>`);
        inState.inBlockComment = true;
        i = text.length;
      } else {
        out.push(`<span class="code-comment">${escapeHtml(text.slice(i, end + 2))}</span>`);
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
      out.push(`<span class="code-string">${escapeHtml(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (/[0-9]/.test(ch)) {
      let j = i + 1;
      while (j < text.length && /[0-9A-Fa-fxXuUlL\.]/.test(text[j])) {
        j += 1;
      }
      out.push(`<span class="code-number">${escapeHtml(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (isIdentStart(ch)) {
      let j = i + 1;
      while (j < text.length && isIdentChar(text[j])) {
        j += 1;
      }
      const word = text.slice(i, j);
      let cls = "";
      if (C_TYPES.has(word)) {
        cls = "code-type";
      } else if (C_KEYWORDS.has(word)) {
        cls = "code-keyword";
      } else if (nextNonSpaceChar(text, j) === "(") {
        cls = "code-function";
      }
      out.push(cls ? `<span class="${cls}">${escapeHtml(word)}</span>` : escapeHtml(word));
      i = j;
      continue;
    }

    if (
      (ch === "-" && next === ">") ||
      (ch === "=" && next === "=") ||
      (ch === "!" && next === "=") ||
      (ch === "<" && next === "=") ||
      (ch === ">" && next === "=") ||
      (ch === "&" && next === "&") ||
      (ch === "|" && next === "|")
    ) {
      out.push(`<span class="code-operator">${escapeHtml(ch + next)}</span>`);
      i += 2;
      continue;
    }

    if ("{}[]();,*".includes(ch)) {
      out.push(`<span class="code-punct">${escapeHtml(ch)}</span>`);
      i += 1;
      continue;
    }

    out.push(escapeHtml(ch));
    i += 1;
  }

  return { html: out.join(""), state: inState };
}

function renderDidacticCode(preElement, code, codeTitle) {
  const raw = String(code || "");
  preElement.dataset.rawCode = raw;
  preElement.dataset.codeTitle = String(codeTitle || "");
  const lines = raw.replaceAll("\r\n", "\n").split("\n");

  if (String(codeTitle || "").toLowerCase().includes("codigo c")) {
    let state = { inBlockComment: false };
    const html = lines
      .map((line, index) => {
        const highlighted = highlightCLine(line, state);
        state = highlighted.state;
        return `<span class="code-line" data-line="${index}">${highlighted.html || "&nbsp;"}</span>`;
      })
      .join("");
    preElement.innerHTML = html;
    return;
  }
  preElement.innerHTML = lines
    .map((line, index) => `<span class="code-line" data-line="${index}">${escapeHtml(line) || "&nbsp;"}</span>`)
    .join("");
}

function sleep(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function isExecutableLine(text, codeTitle) {
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

function nextSignificantLine(lines, fromIndex) {
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

function findMatchingBraceLine(lines, openLineIndex) {
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

function evalCondition(condExpr, context, runtime, whileMeta) {
  const cond = String(condExpr || "").replace(/\s+/g, " ").trim();
  const size = Number(context?.sizeBefore || 0);
  const position = Number(context?.payload?.position || 0);
  const key = whileMeta?.key || "";
  const done = runtime.loopCounter[key] || 0;
  const limit = Number.isFinite(whileMeta?.limit) ? whileMeta.limit : null;

  if (cond.includes("lista == NULL")) {
    return false;
  }
  if (cond.includes("lista != NULL")) {
    return true;
  }
  if (cond.includes("q == NULL")) {
    return false;
  }
  if (cond.includes("lista->cabeza == NULL")) {
    return size === 0;
  }
  if (cond.includes("lista->cabeza != NULL")) {
    return size > 0;
  }
  if (cond.includes("aux != NULL")) {
    if (limit !== null) {
      return done < limit;
    }
    return done < Math.max(0, size);
  }
  if (cond.includes("t->sgte != NULL")) {
    const loopsNeeded = limit !== null ? limit : Math.max(0, size - 1);
    return done < loopsNeeded;
  }
  if (cond.includes("actual != NULL") && cond.includes("i < pos - 1")) {
    const byPos = Math.max(0, position - 2);
    const bySize = Math.max(0, size - 1);
    const loopsNeeded = limit !== null ? limit : Math.min(byPos, bySize);
    return done < loopsNeeded;
  }

  if (whileMeta) {
    const safeLimit = limit !== null ? limit : Math.max(1, Math.min(8, size + 1));
    return done < safeLimit;
  }

  return true;
}

function resolveWhileLimit(condExpr, context) {
  const cond = String(condExpr || "").replace(/\s+/g, " ").trim();
  const size = Number(context?.sizeBefore || 0);
  const position = Number(context?.payload?.position || 0);

  if (cond.includes("t->sgte != NULL")) {
    return Math.max(0, size - 1);
  }
  if (cond.includes("aux != NULL")) {
    return Math.max(0, size);
  }
  if (cond.includes("actual != NULL") && cond.includes("i < pos - 1")) {
    const byPos = Math.max(0, position - 2);
    const bySize = Math.max(0, size - 1);
    return Math.min(byPos, bySize);
  }

  return Math.max(1, Math.min(8, size + 1));
}

function buildExecutionPlan(rawCode, context) {
  const lines = String(rawCode || "").replaceAll("\r\n", "\n").split("\n");
  const executed = [];
  const skipped = new Set();
  const jumpAfterClose = {};
  const loopAtClose = {};
  const runtime = { loopCounter: {} };

  let i = 0;
  let guard = 0;
  while (i >= 0 && i < lines.length && guard < 3000) {
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
      const openIdx = raw.includes("{") ? i : nextSignificantLine(lines, i + 1);
      const closeIdx = openIdx >= 0 ? findMatchingBraceLine(lines, openIdx) : -1;
      const truth = evalCondition(cond, context, runtime, null);

      if (!truth && closeIdx >= 0) {
        for (let k = i + 1; k <= closeIdx; k += 1) {
          skipped.add(k);
        }
        const elseIdx = nextSignificantLine(lines, closeIdx + 1);
        if (elseIdx >= 0 && String(lines[elseIdx]).trim().startsWith("else")) {
          i = elseIdx;
        } else {
          i = closeIdx + 1;
        }
        continue;
      }

      if (truth && closeIdx >= 0) {
        const elseIdx = nextSignificantLine(lines, closeIdx + 1);
        if (elseIdx >= 0 && String(lines[elseIdx]).trim().startsWith("else")) {
          const elseOpenIdx = String(lines[elseIdx]).includes("{") ? elseIdx : nextSignificantLine(lines, elseIdx + 1);
          const elseCloseIdx = elseOpenIdx >= 0 ? findMatchingBraceLine(lines, elseOpenIdx) : -1;
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
      const openIdx = raw.includes("{") ? i : nextSignificantLine(lines, i + 1);
      const closeIdx = openIdx >= 0 ? findMatchingBraceLine(lines, openIdx) : -1;
      const key = `${i}:${closeIdx}`;
      const whileMeta = { key, limit: resolveWhileLimit(cond, context) };
      const truth = evalCondition(cond, context, runtime, whileMeta);
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
      const truth = evalCondition(meta.cond, context, runtime, meta);
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

async function simulateDidacticExecution(context) {
  const codeBox = byId("op-pseudocode");
  if (!codeBox) {
    return;
  }

  const codeTitle = codeBox.dataset.codeTitle || "";
  const rawCode = codeBox.dataset.rawCode || codeBox.textContent || "";
  const plan = buildExecutionPlan(rawCode, context || {});
  const lines = Array.from(codeBox.querySelectorAll(".code-line"));
  const steps = plan.executed
    .map((lineIndex) => lines[lineIndex])
    .filter((lineElement) => Boolean(lineElement))
    .filter((lineElement) => isExecutableLine(lineElement.textContent, codeTitle));

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
  const stepDelayMs = Math.max(20, Math.round(190 / speed));
  for (let i = 0; i < steps.length; i += 1) {
    if (typeof context?.onStep === "function") {
      context.onStep(i, steps.length, {
        lineText: steps[i].textContent || "",
        lineIndex: Number(steps[i].dataset.line || -1),
      });
    }
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
  await sleep(120);

  lines.forEach((lineElement) => {
    lineElement.classList.remove("sim-active");
  });
}

function nodeBox(content, options = {}) {
  const cls = options.className ? ` ${options.className}` : "";
  return `<div class="viz-node${cls}">${content}</div>`;
}

function drawCircularLoop(visualContainer) {
  const wrap = visualContainer.querySelector(".circular-wrap");
  if (!wrap) {
    return;
  }

  const row = wrap.querySelector(".viz-row");
  if (!row) {
    return;
  }

  const nodes = row.querySelectorAll(".viz-node");
  if (nodes.length < 1) {
    return;
  }

  const previous = wrap.querySelector(".viz-loop-svg");
  if (previous) {
    previous.remove();
  }

  const first = nodes[0];
  const last = nodes[nodes.length - 1];
  const wrapRect = wrap.getBoundingClientRect();
  const rowRect = row.getBoundingClientRect();
  const firstRect = first.getBoundingClientRect();
  const lastRect = last.getBoundingClientRect();

  const headX = firstRect.left - wrapRect.left + 12;
  const tailX = lastRect.right - wrapRect.left - 12;
  const downY = rowRect.top - wrapRect.top + 2;
  const topY = Math.max(30, downY - 24);

  const headLabel = wrap.querySelector(".viz-pointer.head");
  const tailLabel = wrap.querySelector(".viz-pointer.tail");
  if (headLabel) {
    headLabel.style.left = `${Math.max(6, headX - 10)}px`;
    headLabel.style.top = `${Math.max(2, topY - 24)}px`;
  }
  if (tailLabel) {
    tailLabel.style.left = `${tailX + 8}px`;
    tailLabel.style.top = `${Math.max(2, topY - 24)}px`;
  }

  const width = Math.max(wrap.scrollWidth, tailX + 14);
  const height = Math.max(wrap.scrollHeight, downY + 8);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "viz-loop-svg");
  svg.setAttribute("width", String(Math.ceil(width)));
  svg.setAttribute("height", String(Math.ceil(height)));
  svg.setAttribute("viewBox", `0 0 ${Math.ceil(width)} ${Math.ceil(height)}`);

  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
  marker.setAttribute("id", "viz-loop-arrow");
  marker.setAttribute("markerWidth", "12");
  marker.setAttribute("markerHeight", "10");
  marker.setAttribute("refX", "9");
  marker.setAttribute("refY", "5");
  marker.setAttribute("orient", "auto");
  marker.setAttribute("markerUnits", "strokeWidth");
  const arrowPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  arrowPath.setAttribute("d", "M 0 0 L 9 5 L 0 10 z");
  arrowPath.setAttribute("class", "viz-loop-arrow-head");
  marker.appendChild(arrowPath);
  defs.appendChild(marker);
  svg.appendChild(defs);

  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute(
    "d",
    `M ${tailX} ${downY} L ${tailX} ${topY} L ${headX} ${topY} L ${headX} ${downY}`,
  );
  path.setAttribute("class", "viz-loop-path");
  path.setAttribute("marker-end", "url(#viz-loop-arrow)");
  svg.appendChild(path);
  wrap.appendChild(svg);
}

function renderLinearWithHeadTail(state, circular, hint) {
  const items = state.items || [];
  const simulation = hint && hint.simulation ? hint.simulation : null;
  const hasTempNode = Boolean(
    simulation
    && (
      (simulation.tempNodeValue !== undefined && simulation.tempNodeValue !== null)
      || (simulation.tempDetachedValue !== undefined && simulation.tempDetachedValue !== null)
    ),
  );
  if (!items.length && !hasTempNode) {
    return '<p class="viz-empty">Estructura vacia.</p>';
  }

  const activeIndices = new Set(simulation && simulation.activeIndices ? simulation.activeIndices : []);
  const visitedIndices = new Set(simulation && simulation.visitedIndices ? simulation.visitedIndices : []);
  const pendingIndices = new Set(simulation && simulation.pendingIndices ? simulation.pendingIndices : []);
  const commitIndices = new Set(simulation && simulation.commitIndices ? simulation.commitIndices : []);
  const suppressDefaultBadges = Boolean(simulation && simulation.suppressDefaultBadges);

  let html = `<div class="viz-row-wrap${circular ? " circular-wrap" : ""}">`;
  if (simulation && simulation.opLabel) {
    html += `<div class="viz-op-label">${escapeHtml(simulation.opLabel)}</div>`;
  }
  if (circular) {
    html += '<span class="viz-pointer head">HEAD</span>';
    html += '<span class="viz-pointer tail">COLA</span>';
  } else {
    html += '<div class="viz-row-label head">HEAD</div>';
  }
  html += '<div class="viz-row">';

  items.forEach((item, index) => {
    const value = escapeHtml(item.value);
    const isHead = index === 0;
    const isTail = index === items.length - 1;

    const badges = [];
    if (isHead && !circular) {
      badges.push('<span class="viz-badge ok">N</span>');
    }
    if (!suppressDefaultBadges && hint && hint.operation === "insertar_final" && isTail) {
      badges.push('<span class="viz-badge new">NEW</span>');
    }
    const simClasses = [];
    if (activeIndices.has(index)) {
      simClasses.push("sim-active");
    } else if (visitedIndices.has(index)) {
      simClasses.push("sim-visited");
    }
    if (pendingIndices.has(index)) {
      simClasses.push("sim-pending");
    }
    if (commitIndices.has(index)) {
      simClasses.push("sim-commit");
    }
    html += `<div class="viz-node${isHead ? " is-head" : ""}${simClasses.length ? ` ${simClasses.join(" ")}` : ""}">${value}${badges.join("")}</div>`;
    if (!isTail) {
      html += '<div class="viz-arrow">&rarr;</div>';
    }
  });

  if (!circular && items.length) {
    html += '<div class="viz-arrow">&rarr;</div><div class="viz-row-label null">NULL</div>';
  } else if (!circular && !items.length) {
    html += '<div class="viz-row-label null">NULL</div>';
  }
  html += "</div>";
  if (circular && items.length > 0) {
    html += '<div class="viz-loop-host"></div>';
  }
  if (hasTempNode) {
    html += '<div class="viz-temp-node-wrap">';
    if (simulation.tempNodeValue !== undefined && simulation.tempNodeValue !== null) {
      html += `<div class="viz-temp-node-title">${escapeHtml(simulation.tempNodeTitle || "nodo aux")}</div>`;
      html += nodeBox(escapeHtml(simulation.tempNodeValue), { className: "sim-pending" });
      if (Number.isInteger(simulation.tempLinkTargetIndex)) {
        const targetText = simulation.tempLinkTargetIndex >= 0
          ? `ENLACE -> nodo[${simulation.tempLinkTargetIndex}]`
          : "ENLACE -> NULL";
        html += `<div class="viz-temp-link">${escapeHtml(targetText)}</div>`;
      }
    }
    if (simulation.tempDetachedValue !== undefined && simulation.tempDetachedValue !== null) {
      html += `<div class="viz-temp-node-title">${escapeHtml(simulation.tempDetachedTitle || "nodo removido")}</div>`;
      html += nodeBox(escapeHtml(simulation.tempDetachedValue), { className: "sim-active sim-detached" });
    }
    if (simulation.tempActionLabel) {
      html += `<div class="viz-temp-note">${escapeHtml(simulation.tempActionLabel)}</div>`;
    }
    html += "</div>";
  }
  html += "</div>";
  return html;
}

function toIntOrNull(value) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed)) {
    return null;
  }
  return parsed;
}

function cloneValues(state) {
  return (state.items || []).map((item) => item.value);
}

function makeLinkedListFrame(baseState, values, simulation) {
  return {
    state: {
      ...baseState,
      items: values.map((value) => ({ value })),
      size: values.length,
      empty: values.length === 0,
    },
    simulation: {
      suppressDefaultBadges: true,
      ...(simulation || {}),
    },
  };
}

function makeStackFrame(baseState, values, simulation) {
  return {
    state: {
      ...baseState,
      items: values.map((value) => ({ value })),
      size: values.length,
      empty: values.length === 0,
    },
    simulation: {
      suppressDefaultBadges: true,
      ...(simulation || {}),
    },
  };
}

function makeQueueFrame(baseState, values, simulation) {
  return {
    state: {
      ...baseState,
      items: values.map((value) => ({ value })),
      size: values.length,
      empty: values.length === 0,
    },
    simulation: {
      suppressDefaultBadges: true,
      ...(simulation || {}),
    },
  };
}

function makePriorityQueueFrame(baseState, items, simulation) {
  return {
    state: {
      ...baseState,
      items: items.map((item) => ({ value: item.value, priority: item.priority })),
      size: items.length,
      empty: items.length === 0,
    },
    simulation: {
      suppressDefaultBadges: true,
      ...(simulation || {}),
    },
  };
}

function buildLinkedListSimulationFrames(currentState, operationName, payload) {
  const baseValues = cloneValues(currentState);
  const frames = [];

  if (operationName === "insertar_inicio") {
    const value = toIntOrNull(payload.value);
    if (value === null) {
      return frames;
    }
    const nextValues = [value, ...baseValues];
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      activeIndices: baseValues.length ? [0] : [],
      opLabel: "Estado inicial",
    }));
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempNodeValue: value,
      opLabel: `1) Se crea nodo aux con valor ${value}`,
    }));
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempNodeValue: value,
      tempLinkTargetIndex: baseValues.length ? 0 : -1,
      activeIndices: baseValues.length ? [0] : [],
      opLabel: "2) aux->sgte = *l",
    }));
    frames.push(makeLinkedListFrame(currentState, nextValues, {
      activeIndices: [0],
      pendingIndices: [0],
      commitIndices: [0],
      opLabel: "3) *l = aux (actualiza HEAD)",
    }));
    frames.push(makeLinkedListFrame(currentState, nextValues, {
      activeIndices: [0],
      opLabel: "Nodo insertado al inicio",
    }));
    return frames;
  }

  if (operationName === "insertar_final") {
    const value = toIntOrNull(payload.value);
    if (value === null) {
      return frames;
    }
    if (!baseValues.length) {
      frames.push(makeLinkedListFrame(currentState, baseValues, { opLabel: "Estado inicial (lista vacia)" }));
      frames.push(makeLinkedListFrame(currentState, baseValues, {
        tempNodeValue: value,
        opLabel: `1) Se crea nodo aux con valor ${value}`,
      }));
      frames.push(makeLinkedListFrame(currentState, [value], {
        activeIndices: [0],
        pendingIndices: [0],
        commitIndices: [0],
        opLabel: "2) *l = aux",
      }));
      return frames;
    }
    const visited = [];
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      activeIndices: [0],
      opLabel: "Estado inicial",
    }));
    for (let i = 0; i < baseValues.length; i += 1) {
      visited.push(i);
      frames.push(makeLinkedListFrame(currentState, baseValues, {
        activeIndices: [i],
        visitedIndices: visited.slice(0, -1),
        opLabel: `Buscando nodo final (paso ${i + 1})`,
      }));
    }
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempNodeValue: value,
      opLabel: `1) Se crea nodo aux con valor ${value}`,
      visitedIndices: baseValues.map((_, i) => i),
    }));
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempNodeValue: value,
      tempLinkTargetIndex: baseValues.length - 1,
      activeIndices: [baseValues.length - 1],
      visitedIndices: baseValues.slice(0, -1).map((_, i) => i),
      opLabel: "2) ultimo->sgte = aux",
    }));
    const nextValues = [...baseValues, value];
    frames.push(makeLinkedListFrame(currentState, nextValues, {
      activeIndices: [nextValues.length - 1],
      pendingIndices: [nextValues.length - 1],
      commitIndices: [nextValues.length - 1],
      visitedIndices: baseValues.map((_, i) => i),
      opLabel: "Nodo insertado al final",
    }));
    return frames;
  }

  if (
    operationName === "lista_insertar_elemento"
    || operationName === "insertar_elemento"
    || operationName === "insertar_posicion"
  ) {
    const value = toIntOrNull(payload.value);
    const posUi = toIntOrNull(payload.position);
    if (value === null || posUi === null) {
      return frames;
    }
    const idx = Math.max(0, Math.min(baseValues.length, posUi - 1));
    const visited = [];
    for (let i = 0; i < idx; i += 1) {
      visited.push(i);
      frames.push(makeLinkedListFrame(currentState, baseValues, { activeIndices: [i], visitedIndices: visited.slice(0, -1) }));
    }
    const nextValues = baseValues.slice();
    nextValues.splice(idx, 0, value);
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempNodeValue: value,
      opLabel: `1) Se crea nodo aux con valor ${value}`,
      visitedIndices: visited,
    }));
    frames.push(makeLinkedListFrame(currentState, nextValues, {
      activeIndices: [idx],
      pendingIndices: [idx],
      commitIndices: [idx],
      visitedIndices: visited,
      opLabel: "2) Reasignacion de enlaces en la posicion objetivo",
    }));
    return frames;
  }

  if (operationName === "limpiar") {
    if (!baseValues.length) {
      return frames;
    }
    for (let i = 0; i < baseValues.length; i += 1) {
      const remaining = baseValues.slice(i);
      frames.push(makeLinkedListFrame(currentState, remaining, { activeIndices: [0] }));
    }
    frames.push(makeLinkedListFrame(currentState, [], {}));
    return frames;
  }

  if (operationName === "eliminar_inicio" && baseValues.length) {
    const removed = baseValues[0];
    const remaining = baseValues.slice(1);
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      activeIndices: [0],
      pendingIndices: [0],
      opLabel: "Estado inicial",
    }));
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempDetachedValue: removed,
      tempDetachedTitle: "aux = *l",
      activeIndices: [0],
      opLabel: "1) aux = *l",
    }));
    frames.push(makeLinkedListFrame(currentState, remaining, {
      commitIndices: remaining.length ? [0] : [],
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      opLabel: "2) *l = aux->sgte",
    }));
    frames.push(makeLinkedListFrame(currentState, remaining, {
      opLabel: "3) free(aux)",
      tempActionLabel: "Memoria del nodo removido liberada.",
    }));
    return frames;
  }

  if (operationName === "eliminar_final" && baseValues.length) {
    if (baseValues.length === 1) {
      const removed = baseValues[0];
      frames.push(makeLinkedListFrame(currentState, baseValues, {
        activeIndices: [0],
        opLabel: "Estado inicial",
      }));
      frames.push(makeLinkedListFrame(currentState, [], {
        tempDetachedValue: removed,
        tempDetachedTitle: "nodo removido",
        opLabel: "1) *l = NULL",
      }));
      frames.push(makeLinkedListFrame(currentState, [], {
        opLabel: "2) free(aux)",
        tempActionLabel: "Memoria del nodo removido liberada.",
      }));
      return frames;
    }
    const visited = [];
    for (let i = 0; i < baseValues.length; i += 1) {
      visited.push(i);
      frames.push(makeLinkedListFrame(currentState, baseValues, {
        activeIndices: [i],
        visitedIndices: visited.slice(0, -1),
        opLabel: `Buscando ultimo nodo (paso ${i + 1})`,
      }));
    }
    const removed = baseValues[baseValues.length - 1];
    const remaining = baseValues.slice(0, -1);
    frames.push(makeLinkedListFrame(currentState, baseValues, {
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      activeIndices: [baseValues.length - 2],
      opLabel: "1) prev->sgte = NULL",
    }));
    frames.push(makeLinkedListFrame(currentState, remaining, {
      activeIndices: [remaining.length - 1],
      commitIndices: [remaining.length - 1],
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      opLabel: "2) Reasignacion del ultimo enlace",
    }));
    frames.push(makeLinkedListFrame(currentState, remaining, {
      opLabel: "3) free(aux)",
      tempActionLabel: "Memoria del nodo removido liberada.",
    }));
    return frames;
  }

  if ((operationName === "buscar_elemento" || operationName === "buscar_posiciones") && baseValues.length) {
    const visited = [];
    for (let i = 0; i < baseValues.length; i += 1) {
      visited.push(i);
      frames.push(makeLinkedListFrame(currentState, baseValues, { activeIndices: [i], visitedIndices: visited.slice(0, -1) }));
    }
    return frames;
  }

  if (operationName === "eliminar_elemento" && baseValues.length) {
    const value = toIntOrNull(payload.value);
    if (value === null) {
      return frames;
    }
    const index = baseValues.findIndex((item) => Number(item) === Number(value));
    const visited = [];
    for (let i = 0; i < baseValues.length; i += 1) {
      visited.push(i);
      frames.push(makeLinkedListFrame(currentState, baseValues, {
        activeIndices: [i],
        visitedIndices: visited.slice(0, -1),
        opLabel: `Buscando valor ${value}`,
      }));
      if (i === index) {
        break;
      }
    }
    if (index >= 0) {
      const remaining = baseValues.slice(0, index).concat(baseValues.slice(index + 1));
      frames.push(makeLinkedListFrame(currentState, remaining, {
        commitIndices: index < remaining.length ? [index] : [],
        tempDetachedValue: value,
        tempDetachedTitle: "nodo removido",
        opLabel: "Reasignacion de enlaces (nodo removido)",
      }));
      frames.push(makeLinkedListFrame(currentState, remaining, {
        commitIndices: index < remaining.length ? [index] : [],
        opLabel: "Estado final tras free(p)",
      }));
    }
    return frames;
  }

  if (operationName === "eliminar_repetidos" && baseValues.length) {
    const value = toIntOrNull(payload.value);
    if (value === null) {
      return frames;
    }
    const visited = [];
    for (let i = 0; i < baseValues.length; i += 1) {
      visited.push(i);
      frames.push(makeLinkedListFrame(currentState, baseValues, {
        activeIndices: [i],
        visitedIndices: visited.slice(0, -1),
        opLabel: `Buscando repeticiones de ${value}`,
      }));
    }
    const remaining = baseValues.filter((item) => Number(item) !== Number(value));
    frames.push(makeLinkedListFrame(currentState, remaining, {
      tempDetachedValue: value,
      tempDetachedTitle: "valor eliminado",
      opLabel: "Eliminacion de todas las ocurrencias",
    }));
    return frames;
  }

  return frames;
}

function buildStackSimulationFrames(currentState, operationName, payload) {
  const baseValues = cloneValues(currentState);
  const frames = [];

  if (operationName === "apilar") {
    const value = toIntOrNull(payload.value);
    if (value === null) {
      return frames;
    }
    const nextValues = [value, ...baseValues];
    frames.push(makeStackFrame(currentState, baseValues, {
      activeIndices: baseValues.length ? [0] : [],
      opLabel: "Estado inicial",
    }));
    frames.push(makeStackFrame(currentState, baseValues, {
      tempNodeValue: value,
      opLabel: `1) Se crea nodo aux con valor ${value}`,
    }));
    frames.push(makeStackFrame(currentState, baseValues, {
      tempNodeValue: value,
      tempLinkTargetIndex: baseValues.length ? 0 : -1,
      activeIndices: baseValues.length ? [0] : [],
      opLabel: "2) aux->sgte = *p",
    }));
    frames.push(makeStackFrame(currentState, nextValues, {
      activeIndices: [0],
      pendingIndices: [0],
      commitIndices: [0],
      tempNodeValue: value,
      tempNodeTitle: "aux (integrado)",
      tempActionLabel: "El nodo temporal ahora forma parte de la pila.",
      opLabel: "3) *p = aux (actualiza TOPE)",
    }));
    frames.push(makeStackFrame(currentState, nextValues, {
      activeIndices: [0],
      commitIndices: [0],
      opLabel: "Estado final: nodo insertado en el TOPE",
    }));
    return frames;
  }

  if (operationName === "desapilar" && baseValues.length) {
    const removed = baseValues[0];
    const remaining = baseValues.slice(1);
    frames.push(makeStackFrame(currentState, baseValues, {
      activeIndices: [0],
      pendingIndices: [0],
      opLabel: "Estado inicial",
    }));
    frames.push(makeStackFrame(currentState, baseValues, {
      activeIndices: [0],
      tempDetachedValue: removed,
      tempDetachedTitle: "aux = *p",
      opLabel: "1) aux = *p",
    }));
    frames.push(makeStackFrame(currentState, remaining, {
      commitIndices: remaining.length ? [0] : [],
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      opLabel: "2) *p = aux->sgte",
    }));
    frames.push(makeStackFrame(currentState, remaining, {
      tempActionLabel: "3) free(aux)",
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      opLabel: "Memoria del nodo removido liberada",
    }));
    frames.push(makeStackFrame(currentState, remaining, {
      activeIndices: remaining.length ? [0] : [],
      commitIndices: remaining.length ? [0] : [],
      opLabel: "Estado final tras desapilar",
    }));
    return frames;
  }

  if (operationName === "cima" && baseValues.length) {
    frames.push(makeStackFrame(currentState, baseValues, { activeIndices: [0] }));
    return frames;
  }

  if (operationName === "limpiar") {
    if (!baseValues.length) {
      return frames;
    }
    for (let i = 0; i < baseValues.length; i += 1) {
      const remaining = baseValues.slice(i);
      frames.push(makeStackFrame(currentState, remaining, { activeIndices: [0] }));
    }
    frames.push(makeStackFrame(currentState, [], {}));
    return frames;
  }

  return frames;
}

function buildCircularListSimulationFrames(currentState, operationName, payload) {
  const values = cloneValues(currentState); const frames = [];
  const frame = (next, simulation) => frames.push(makeLinkedListFrame(currentState, next, { suppressDefaultBadges: true, ...(simulation || {}) }));
  const value = toIntOrNull(payload.value);
  if (operationName === "insertar_inicio" && value !== null) { frame(values, { opLabel: "HEAD actual" }); frame(values, { tempNodeValue: value, tempNodeTitle: "aux creado", opLabel: "aux->sgte = HEAD" }); frame([value, ...values], { activeIndices: [0], commitIndices: [0], opLabel: "HEAD = aux; TAIL->sgte = HEAD" }); }
  else if (operationName === "insertar_final" && value !== null) { frame(values, { activeIndices: values.length ? [values.length - 1] : [], opLabel: "TAIL actual" }); frame(values, { tempNodeValue: value, tempNodeTitle: "aux creado", opLabel: "aux->sgte = HEAD" }); frame([...values, value], { activeIndices: [values.length], commitIndices: [values.length], opLabel: "TAIL = aux; cierre circular" }); }
  else if (operationName === "eliminar_inicio" && values.length) { frame(values, { activeIndices: [0], tempDetachedValue: values[0], tempDetachedTitle: "aux = HEAD", opLabel: "aux = HEAD" }); frame(values.slice(1), { tempDetachedValue: values[0], tempActionLabel: "HEAD = aux->sgte; free(aux)", opLabel: "HEAD avanza y TAIL conserva el ciclo" }); }
  else if (operationName === "eliminar_primero" && values.length && value !== null) { const index = values.findIndex((item) => Number(item) === value); if (index >= 0) { frame(values, { activeIndices: [index], opLabel: `recorrido hasta ${value}` }); frame(values.filter((_, i) => i !== index), { tempDetachedValue: values[index], tempActionLabel: "enlace reasignado; free(aux)", opLabel: "nodo desconectado" }); } }
  else if (operationName === "buscar_posiciones" && values.length) values.forEach((_, i) => frame(values, { activeIndices: [i], visitedIndices: values.slice(0, i).map((_, j) => j), opLabel: "recorrido circular" }));
  else if (operationName === "invertir" && values.length) { frame(values, { opLabel: "invertir enlaces sgte" }); frame([...values].reverse(), { commitIndices: values.map((_, i) => i), opLabel: "HEAD y TAIL actualizados; ciclo restaurado" }); }
  else if (operationName === "limpiar" && values.length) { values.forEach((_, i) => frame(values.slice(i), { tempDetachedValue: values[i], opLabel: "desconectar y liberar nodo" })); frame([], { opLabel: "HEAD = TAIL = NULL" }); }
  return frames;
}

function buildSublistSimulationFrames(currentState, operationName, payload) {
  const original = structuredClone(currentState.items || []); const frames = [];
  const frame = (items, simulation = {}) => frames.push({ state: { ...currentState, items: structuredClone(items), size: items.length, empty: !items.length }, simulation: { suppressDefaultBadges: true, ...simulation } });
  const parent = toIntOrNull(payload.parent); const child = toIntOrNull(payload.child);
  if (operationName === "insertar_padre" && parent !== null) { frame(original, { opLabel: "buscar final de padres" }); frame([...original, { parent, children: [] }], { tempNodeValue: parent, commitIndices: [original.length], opLabel: "enlazar nuevo padre" }); }
  else if (operationName === "insertar_hijo" && parent !== null && child !== null) { const next = structuredClone(original); const index = next.findIndex((item) => Number(item.parent) === parent); frame(original, { activeIndices: index >= 0 ? [index] : [], opLabel: "localizar padre" }); if (index >= 0) { next[index].children = [...(next[index].children || []), child]; frame(next, { activeIndices: [index], tempNodeValue: child, opLabel: "enlazar hijo en la rama" }); } }
  else if (operationName === "eliminar_padre" && parent !== null) { const index = original.findIndex((item) => Number(item.parent) === parent); if (index >= 0) { frame(original, { activeIndices: [index], tempDetachedValue: parent, opLabel: "aislar padre y sus hijos" }); frame(original.filter((_, i) => i !== index), { tempDetachedValue: parent, tempActionLabel: "free de rama padre-hijos", opLabel: "rama liberada" }); } }
  else if (operationName === "eliminar_hijo" && parent !== null && child !== null) { const next = structuredClone(original); const index = next.findIndex((item) => Number(item.parent) === parent); frame(original, { activeIndices: index >= 0 ? [index] : [], opLabel: "localizar rama padre" }); if (index >= 0) { const childIndex = (next[index].children || []).findIndex((item) => Number(item) === child); if (childIndex >= 0) { next[index].children.splice(childIndex, 1); frame(next, { activeIndices: [index], tempDetachedValue: child, tempActionLabel: "enlace hijo reasignado; free", opLabel: "primera coincidencia de hijo desconectada" }); } } }
  else if (operationName === "hijos_de" && parent !== null) { const parentIndex = original.findIndex((item) => Number(item.parent) === parent); const limit = parentIndex >= 0 ? parentIndex + 1 : original.length; for (let index = 0; index < limit; index += 1) frame(original, { activeIndices: [index], visitedIndices: Array.from({ length: index }, (_, visited) => visited), opLabel: `comparar padre ${original[index].parent}` }); }
  else if (operationName === "limpiar" && original.length) { original.forEach((item, index) => frame(original.slice(index), { tempDetachedValue: item.parent, opLabel: "liberar rama" })); frame([], { opLabel: "HEAD = NULL" }); }
  return frames;
}

function buildQueueSimulationFrames(currentState, operationName, payload) {
  const baseValues = cloneValues(currentState);
  const frames = [];

  if (operationName === "encolar") {
    const value = toIntOrNull(payload.value);
    if (value === null) {
      return frames;
    }
    const nextValues = [...baseValues, value];
    if (baseValues.length) {
      frames.push(makeQueueFrame(currentState, baseValues, {
        activeIndices: [baseValues.length - 1],
        opLabel: "Estado inicial (ATRAS actual)",
      }));
    } else {
      frames.push(makeQueueFrame(currentState, baseValues, {
        opLabel: "Estado inicial (cola vacia)",
      }));
    }
    frames.push(makeQueueFrame(currentState, baseValues, {
      tempNodeValue: value,
      opLabel: `1) Se crea nodo aux con valor ${value}`,
    }));
    if (baseValues.length) {
      frames.push(makeQueueFrame(currentState, baseValues, {
        tempNodeValue: value,
        tempLinkTargetIndex: baseValues.length - 1,
        activeIndices: [baseValues.length - 1],
        opLabel: "2) q->atras->sgte = aux",
      }));
    } else {
      frames.push(makeQueueFrame(currentState, nextValues, {
        activeIndices: [0],
        pendingIndices: [0],
        commitIndices: [0],
        tempNodeValue: value,
        tempNodeTitle: "aux (integrado)",
        opLabel: "2) q->delante = aux",
      }));
      frames.push(makeQueueFrame(currentState, nextValues, {
        activeIndices: [0],
        commitIndices: [0],
        opLabel: "3) q->atras = aux",
      }));
      frames.push(makeQueueFrame(currentState, nextValues, {
        activeIndices: [0],
        commitIndices: [0],
        opLabel: "Estado final: primer nodo encolado",
      }));
      return frames;
    }
    frames.push(makeQueueFrame(currentState, nextValues, {
      activeIndices: [baseValues.length],
      pendingIndices: [baseValues.length],
      commitIndices: [baseValues.length],
      tempNodeValue: value,
      tempNodeTitle: "aux (integrado)",
      opLabel: "3) q->atras = aux",
    }));
    frames.push(makeQueueFrame(currentState, nextValues, {
      activeIndices: [baseValues.length],
      commitIndices: [baseValues.length],
      opLabel: "Estado final: nodo agregado al final de la cola",
    }));
    return frames;
  }

  if (operationName === "desencolar" && baseValues.length) {
    const removed = baseValues[0];
    const remaining = baseValues.slice(1);
    frames.push(makeQueueFrame(currentState, baseValues, {
      activeIndices: [0],
      pendingIndices: [0],
      opLabel: "Estado inicial",
    }));
    frames.push(makeQueueFrame(currentState, baseValues, {
      activeIndices: [0],
      tempDetachedValue: removed,
      tempDetachedTitle: "aux = q->delante",
      opLabel: "1) aux = q->delante",
    }));
    frames.push(makeQueueFrame(currentState, remaining, {
      commitIndices: remaining.length ? [0] : [],
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      opLabel: "2) q->delante = aux->sgte",
    }));
    frames.push(makeQueueFrame(currentState, remaining, {
      tempActionLabel: "3) free(aux)",
      tempDetachedValue: removed,
      tempDetachedTitle: "nodo removido",
      opLabel: "Memoria del nodo removido liberada",
    }));
    frames.push(makeQueueFrame(currentState, remaining, {
      activeIndices: remaining.length ? [0] : [],
      commitIndices: remaining.length ? [0] : [],
      opLabel: "Estado final tras desencolar",
    }));
    return frames;
  }

  if (operationName === "frente" && baseValues.length) {
    frames.push(makeQueueFrame(currentState, baseValues, { activeIndices: [0] }));
    return frames;
  }

  if (operationName === "final" && baseValues.length) {
    frames.push(makeQueueFrame(currentState, baseValues, { activeIndices: [baseValues.length - 1] }));
    return frames;
  }

  if (operationName === "limpiar") {
    if (!baseValues.length) {
      return frames;
    }
    for (let i = 0; i < baseValues.length; i += 1) {
      const remaining = baseValues.slice(i);
      frames.push(makeQueueFrame(currentState, remaining, { activeIndices: [0] }));
    }
    frames.push(makeQueueFrame(currentState, [], {}));
    return frames;
  }

  return frames;
}

function buildPriorityQueueSimulationFrames(currentState, operationName, payload) {
  const baseItems = (currentState.items || []).map((item) => ({
    value: item.value,
    priority: item.priority,
  }));
  const frames = [];

  if (operationName === "encolar") {
    const value = toIntOrNull(payload.value);
    const priority = toIntOrNull(payload.priority);
    if (value === null || priority === null) {
      return frames;
    }
    frames.push(makePriorityQueueFrame(currentState, baseItems, {
      activeIndices: baseItems.length ? [baseItems.length - 1] : [],
      opLabel: baseItems.length ? "Estado inicial (última llegada)" : "Estado inicial (cola vacía)",
    }));
    const nextItems = [...baseItems, { value, priority }];
    frames.push(makePriorityQueueFrame(currentState, baseItems, {
      tempNodeValue: value,
      tempNodePriority: priority,
      opLabel: "aux = malloc; aux->sgte = NULL",
    }));
    frames.push(makePriorityQueueFrame(currentState, nextItems, {
      activeIndices: [nextItems.length - 1],
      pendingIndices: [nextItems.length - 1],
      commitIndices: [nextItems.length - 1],
      tempNodeValue: value,
      tempNodePriority: priority,
      tempNodeTitle: "aux (integrado)",
      opLabel: "enlace de llegada actualizado",
    }));
    const selectedIndex = nextItems.reduce((best, item, index) => (
      Number(item.priority) < Number(nextItems[best].priority) ? index : best
    ), 0);
    frames.push(makePriorityQueueFrame(currentState, nextItems, {
      activeIndices: [selectedIndex],
      visitedIndices: nextItems.map((_, index) => index).filter((index) => index !== selectedIndex),
      opLabel: "La selección respeta prioridad y llegada",
    }));
    return frames;
  }

  if (operationName === "desencolar" && baseItems.length) {
    let minIndex = 0;
    for (let i = 1; i < baseItems.length; i += 1) {
      if (Number(baseItems[i].priority) < Number(baseItems[minIndex].priority)) {
        minIndex = i;
      }
    }
    const visited = [];
    for (let i = 0; i < baseItems.length; i += 1) {
      visited.push(i);
      frames.push(makePriorityQueueFrame(currentState, baseItems, {
        activeIndices: [i],
        visitedIndices: visited.slice(0, -1),
      }));
    }
    const removed = baseItems[minIndex];
    frames.push(makePriorityQueueFrame(currentState, baseItems, {
      activeIndices: [minIndex],
      visitedIndices: visited.filter((index) => index !== minIndex),
      tempDetachedValue: removed.value,
      tempDetachedPriority: removed.priority,
      tempDetachedTitle: "objetivo seleccionado",
      opLabel: "desconectar objetivo de la cadena",
    }));
    const remaining = baseItems.filter((_, idx) => idx !== minIndex);
    frames.push(makePriorityQueueFrame(currentState, remaining, {
      tempDetachedValue: removed.value,
      tempDetachedPriority: removed.priority,
      tempDetachedTitle: "objetivo retirado",
      tempActionLabel: "free(objetivo)",
      opLabel: "Liberar sólo el candidato seleccionado",
    }));
    frames.push(makePriorityQueueFrame(currentState, remaining, {
      activeIndices: remaining.length ? [remaining.reduce((best, item, index) => (
        Number(item.priority) < Number(remaining[best].priority) ? index : best
      ), 0)] : [],
      opLabel: "Estado final tras desencolar",
    }));
    return frames;
  }

  if (operationName === "frente" && baseItems.length) {
    const candidate = baseItems.reduce((best, item, index) => (
      Number(item.priority) < Number(baseItems[best].priority) ? index : best
    ), 0);
    frames.push(makePriorityQueueFrame(currentState, baseItems, {
      activeIndices: [candidate],
      visitedIndices: baseItems.map((_, index) => index).filter((index) => index !== candidate),
      opLabel: "Consulta: candidato de mayor prioridad",
    }));
    return frames;
  }

  if (operationName === "limpiar") {
    if (!baseItems.length) {
      return frames;
    }
    for (let i = 0; i < baseItems.length; i += 1) {
      const remaining = baseItems.slice(i);
      frames.push(makePriorityQueueFrame(currentState, remaining, { activeIndices: [0] }));
    }
    frames.push(makePriorityQueueFrame(currentState, [], {}));
    return frames;
  }

  return frames;
}

function resolveStackFrameByLine(operationName, lineText, frames) {
  const line = String(lineText || "").toLowerCase();
  if (!frames.length) {
    return -1;
  }

  if (operationName === "apilar") {
    if (line.includes("*p = aux")) {
      return Math.min(3, frames.length - 1);
    }
    if (line.includes("aux->sgte = *p")) {
      return Math.min(2, frames.length - 1);
    }
    if (line.includes("if (aux == null)") || line.includes("if (aux==null)")) {
      return Math.min(1, frames.length - 1);
    }
    if (line.includes("aux->nro") || line.includes("malloc")) {
      return Math.min(1, frames.length - 1);
    }
    // Fallback al mapeo proporcional por paso para no volver al estado inicial
    // en lineas de cierre (p. ej. "}") al final de la traza.
    return -1;
  }

  if (operationName === "desapilar") {
    if (line.includes("free(aux)") || line.includes("*p = aux->sgte")) {
      return line.includes("free(aux)")
        ? Math.min(3, frames.length - 1)
        : Math.min(2, frames.length - 1);
    }
    if (line.includes("int num = aux->nro") || line.includes("aux = *p")) {
      return Math.min(1, frames.length - 1);
    }
    return -1;
  }

  if (operationName === "cima") {
    return 0;
  }

  if (operationName === "limpiar") {
    return -1;
  }

  return -1;
}

function resolveQueueFrameByLine(operationName, lineText, frames) {
  const line = String(lineText || "").toLowerCase();
  if (!frames.length) {
    return 0;
  }

  if (operationName === "encolar") {
    if (line.includes("q->atras = aux")) {
      return Math.min(3, frames.length - 1);
    }
    if (
      line.includes("q->atras->sgte = aux")
      || line.includes("q->delante = aux")
    ) {
      return Math.min(2, frames.length - 1);
    }
    if (
      line.includes("if (aux == null)")
      || line.includes("if (aux==null)")
      || line.includes("if (q->delante == null)")
      || line.includes("if (q->delante==null)")
      || line === "else {"
      || line === "else"
    ) {
      return Math.min(1, frames.length - 1);
    }
    if (
      line.includes("aux->sgte = null")
      || line.includes("aux->nro")
      || line.includes("malloc")
    ) {
      return Math.min(1, frames.length - 1);
    }
    return -1;
  }

  if (operationName === "desencolar") {
    if (line.includes("free(aux)") || line.includes("q->delante = aux->sgte")) {
      return line.includes("free(aux)")
        ? Math.min(3, frames.length - 1)
        : Math.min(2, frames.length - 1);
    }
    if (line.includes("int num = aux->nro") || line.includes("aux = q->delante")) {
      return Math.min(1, frames.length - 1);
    }
    return -1;
  }

  if (operationName === "frente") {
    return 0;
  }
  if (operationName === "final") {
    return 0;
  }
  if (operationName === "limpiar") {
    return -1;
  }
  return -1;
}

function resolvePriorityQueueFrameByLine(operationName, lineText, frames) {
  const line = String(lineText || "").toLowerCase();
  if (!frames.length) {
    return 0;
  }

  if (operationName === "encolar") {
    if (line.includes("cola->atras = nuevo")) {
      return Math.min(2, frames.length - 1);
    }
    if (
      line.includes("nuevo->prioridad")
      || line.includes("nuevo->valor")
      || line.includes("nuevo->sgte = null")
      || line.includes("malloc")
      || line.includes("cola->atras->sgte = nuevo")
    ) {
      return Math.min(1, frames.length - 1);
    }
    return -1;
  }

  if (operationName === "desencolar") {
    if (line.includes("free(objetivo)") || line.includes("objetivoprev->sgte = objetivo->sgte") || line.includes("cola->delante = objetivo->sgte")) {
      return Math.min(frames.length - 1, Math.max(0, frames.length - 1));
    }
    if (line.includes("while (actual != null)") || line.includes("actual = actual->sgte") || line.includes("actual->prioridad < objetivo->prioridad")) {
      return Math.min(Math.max(1, frames.length - 2), frames.length - 1);
    }
    return -1;
  }

  if (operationName === "frente") {
    return 0;
  }
  if (operationName === "limpiar") {
    return -1;
  }
  return -1;
}

function resolveLinkedListFrameByLine(operationName, lineText, frames) {
  const line = String(lineText || "").toLowerCase();
  if (!frames.length) {
    return -1;
  }

  if (operationName === "eliminar_elemento") {
    if (line.includes("free(")) {
      return Math.max(0, frames.length - 1);
    }
    if (
      line.includes("ant->sgte = p->sgte")
      || line.includes("*lista = p->sgte")
      || line.includes("*l = aux->sgte")
    ) {
      return Math.max(0, frames.length - 2);
    }
    return -1;
  }

  return -1;
}

function resolveFrameIndexForStep(modelId, operationName, stepIndex, totalSteps, frames, stepMeta) {
  if (!frames.length) {
    return -1;
  }
  if (
    (modelId === "linked_list" || modelId === "stack" || modelId === "queue" || modelId === "priority_queue")
    && totalSteps > 0
    && stepIndex >= totalSteps - 1
  ) {
    return frames.length - 1;
  }
  if (modelId === "linked_list") {
    const mapped = resolveLinkedListFrameByLine(operationName, stepMeta?.lineText || "", frames);
    if (mapped >= 0) {
      return mapped;
    }
  }
  if (modelId === "stack") {
    const mapped = resolveStackFrameByLine(operationName, stepMeta?.lineText || "", frames);
    if (mapped >= 0) {
      return mapped;
    }
  }
  if (modelId === "queue") {
    const mapped = resolveQueueFrameByLine(operationName, stepMeta?.lineText || "", frames);
    if (mapped >= 0) {
      return mapped;
    }
  }
  if (modelId === "priority_queue") {
    const mapped = resolvePriorityQueueFrameByLine(operationName, stepMeta?.lineText || "", frames);
    if (mapped >= 0) {
      return mapped;
    }
  }
  const ratio = totalSteps <= 1 ? 1 : stepIndex / (totalSteps - 1);
  return Math.min(
    frames.length - 1,
    Math.max(0, Math.floor(ratio * frames.length)),
  );
}

function buildSequentialVisualFrames(modelId, visualState, operationName, payload) {
  if (modelId === "linked_list") {
    return buildLinkedListSimulationFrames(visualState, operationName, payload);
  }
  if (modelId === "stack") {
    return buildStackSimulationFrames(visualState, operationName, payload);
  }
  if (modelId === "queue") {
    return buildQueueSimulationFrames(visualState, operationName, payload);
  }
  if (modelId === "priority_queue") {
    return buildPriorityQueueSimulationFrames(visualState, operationName, payload);
  }
  if (modelId === "circular_list") return buildCircularListSimulationFrames(visualState, operationName, payload);
  if (modelId === "sublist") return buildSublistSimulationFrames(visualState, operationName, payload);
  return [];
}

function renderQueue(state, hint) {
  const items = state.items || [];
  const simulation = hint && hint.simulation ? hint.simulation : null;
  const hasTempNode = simulation && simulation.tempNodeValue !== undefined && simulation.tempNodeValue !== null;
  const hasDetachedNode = simulation && simulation.tempDetachedValue !== undefined && simulation.tempDetachedValue !== null;
  if (!items.length && !hasTempNode && !hasDetachedNode) {
    return '<p class="viz-empty">Cola vacia.</p>';
  }

  const activeIndices = new Set(simulation && simulation.activeIndices ? simulation.activeIndices : []);
  const visitedIndices = new Set(simulation && simulation.visitedIndices ? simulation.visitedIndices : []);
  const pendingIndices = new Set(simulation && simulation.pendingIndices ? simulation.pendingIndices : []);
  const commitIndices = new Set(simulation && simulation.commitIndices ? simulation.commitIndices : []);
  const suppressDefaultBadges = Boolean(simulation && simulation.suppressDefaultBadges);
  const tempNodeValue = hasTempNode ? simulation.tempNodeValue : null;
  const tempLinkTargetIndex =
    simulation && Number.isInteger(simulation.tempLinkTargetIndex) ? simulation.tempLinkTargetIndex : null;

  let html = '<div class="viz-row-wrap queue-wrap">';
  if (simulation && simulation.opLabel) {
    html += `<div class="viz-op-label">${escapeHtml(simulation.opLabel)}</div>`;
  }
  html += '<div class="viz-row-label front">DELANTE</div><div class="viz-row">';
  items.forEach((item, index) => {
    const isFront = index === 0;
    const isBack = index === items.length - 1;
    const simClasses = [];
    if (activeIndices.has(index)) {
      simClasses.push("sim-active");
    } else if (visitedIndices.has(index)) {
      simClasses.push("sim-visited");
    }
    if (pendingIndices.has(index)) {
      simClasses.push("sim-pending");
    }
    if (commitIndices.has(index)) {
      simClasses.push("sim-commit");
    }
    let className = simClasses.join(" ");
    if (isFront || isBack) {
      className = `${className ? `${className} ` : ""}is-end`;
    }
    let badge = "";
    if (!suppressDefaultBadges && hint && hint.operation === "encolar" && isBack) {
      badge = '<span class="viz-badge new">NEW</span>';
    }
    html += nodeBox(escapeHtml(item.value) + badge, { className });
    if (!isBack) {
      html += '<div class="viz-arrow">&rarr;</div>';
    }
  });
  if (!items.length) {
    html += '<div class="viz-row-label null">NULL</div>';
  }
  html += '</div><div class="viz-row-tail"><span class="viz-row-label back">ATRÁS</span></div>';
  if (hasTempNode || hasDetachedNode || (simulation && simulation.tempActionLabel)) {
    html += '<div class="viz-temp-node-wrap">';
    if (hasTempNode) {
      html += `<div class="viz-temp-node-title">${escapeHtml(simulation.tempNodeTitle || "nodo aux")}</div>`;
      html += nodeBox(escapeHtml(tempNodeValue), { className: "sim-pending" });
      if (tempLinkTargetIndex !== null) {
        const targetText =
          tempLinkTargetIndex >= 0 && tempLinkTargetIndex < items.length
            ? `ENLACE -> nodo[${tempLinkTargetIndex}]`
            : "ENLACE -> NULL";
        html += `<div class="viz-temp-link">${escapeHtml(targetText)}</div>`;
      }
    }
    if (hasDetachedNode) {
      html += `<div class="viz-temp-node-title">${escapeHtml(simulation.tempDetachedTitle || "nodo removido")}</div>`;
      html += nodeBox(escapeHtml(simulation.tempDetachedValue), { className: "sim-active sim-detached" });
    }
    if (simulation && simulation.tempActionLabel) {
      html += `<div class="viz-temp-note">${escapeHtml(simulation.tempActionLabel)}</div>`;
    }
    html += "</div>";
  }
  if (hint && hint.operation === "desencolar" && hint.result) {
    html += `<div class="viz-out">OUT: ${escapeHtml(hint.result)}</div>`;
  }
  html += "</div>";
  return html;
}

function renderPriorityQueue(state, hint) {
  const items = state.items || [];
  if (!items.length) {
    return '<p class="viz-empty">Cola de prioridad vacia.</p>';
  }

  const simulation = hint && hint.simulation ? hint.simulation : null;
  const activeIndices = new Set(simulation && simulation.activeIndices ? simulation.activeIndices : []);
  const visitedIndices = new Set(simulation && simulation.visitedIndices ? simulation.visitedIndices : []);
  const pendingIndices = new Set(simulation && simulation.pendingIndices ? simulation.pendingIndices : []);
  const suppressDefaultBadges = Boolean(simulation && simulation.suppressDefaultBadges);

  const outIndexFromState = Number.isInteger(state.out_index) ? state.out_index : -1;
  let outIndex = outIndexFromState;
  if (outIndex < 0 || outIndex >= items.length) {
    outIndex = 0;
    for (let i = 1; i < items.length; i += 1) {
      if (Number(items[i].priority) < Number(items[outIndex].priority)) {
        outIndex = i;
      }
    }
  }

  let html = '<div class="viz-row">';
  items.forEach((item, index) => {
    const content = `V:${escapeHtml(item.value)}<br>P:${escapeHtml(item.priority)}`;
    const simClasses = [];
    if (activeIndices.has(index)) {
      simClasses.push("sim-active");
    } else if (visitedIndices.has(index)) {
      simClasses.push("sim-visited");
    }
    if (pendingIndices.has(index)) {
      simClasses.push("sim-pending");
    }
    let className = simClasses.join(" ");
    let badge = "";
    if (index === outIndex) {
      className = `${className ? `${className} ` : ""}is-out`;
      if (!suppressDefaultBadges) {
        badge = '<span class="viz-badge out">OUT</span>';
      }
    }
    html += nodeBox(content + badge, { className });
    if (index < items.length - 1) {
      html += '<div class="viz-arrow">&rarr;</div>';
    }
  });
  html += "</div>";
  if (hint && hint.operation === "desencolar" && hint.result) {
    if (hint.result_priority !== undefined && hint.result_priority !== null && String(hint.result_priority) !== "") {
      html += `<div class="viz-out">Atendido: ${escapeHtml(hint.result)} (P:${escapeHtml(hint.result_priority)})</div>`;
    } else {
      html += `<div class="viz-out">Atendido: ${escapeHtml(hint.result)}</div>`;
    }
  }
  return html;
}

function renderStack(state, hint) {
  const items = state.items || [];
  const simulation = hint && hint.simulation ? hint.simulation : null;
  const hasTempNode = simulation && simulation.tempNodeValue !== undefined && simulation.tempNodeValue !== null;
  const hasDetachedNode = simulation && simulation.tempDetachedValue !== undefined && simulation.tempDetachedValue !== null;
  if (!items.length && !hasTempNode && !hasDetachedNode) {
    return '<p class="viz-empty">Pila vacia.</p>';
  }

  const activeIndices = new Set(simulation && simulation.activeIndices ? simulation.activeIndices : []);
  const visitedIndices = new Set(simulation && simulation.visitedIndices ? simulation.visitedIndices : []);
  const pendingIndices = new Set(simulation && simulation.pendingIndices ? simulation.pendingIndices : []);
  const commitIndices = new Set(simulation && simulation.commitIndices ? simulation.commitIndices : []);
  const suppressDefaultBadges = Boolean(simulation && simulation.suppressDefaultBadges);
  const tempNodeValue = hasTempNode ? simulation.tempNodeValue : null;
  const tempLinkTargetIndex =
    simulation && Number.isInteger(simulation.tempLinkTargetIndex) ? simulation.tempLinkTargetIndex : null;

  let html = '<div class="viz-stack-wrap">';
  if (simulation && simulation.opLabel) {
    html += `<div class="viz-op-label">${escapeHtml(simulation.opLabel)}</div>`;
  }
  html += '<div class="viz-row-label top">TOPE</div><div class="viz-stack">';
  items.forEach((item, index) => {
    const isTop = index === 0;
    const value = escapeHtml(item.value);
    const simClasses = [];
    if (activeIndices.has(index)) {
      simClasses.push("sim-active");
    } else if (visitedIndices.has(index)) {
      simClasses.push("sim-visited");
    }
    if (pendingIndices.has(index)) {
      simClasses.push("sim-pending");
    }
    if (commitIndices.has(index)) {
      simClasses.push("sim-commit");
    }
    const className = `${isTop ? "is-top" : ""}${simClasses.length ? ` ${simClasses.join(" ")}` : ""}`.trim();
    let badge = "";
    if (!suppressDefaultBadges && isTop && hint && hint.operation === "apilar") {
      badge = '<span class="viz-badge new">NEW</span>';
    }
    html += `<div class="viz-stack-node-row">${nodeBox(value + badge, { className })}</div>`;
    if (index < items.length - 1) {
      html += '<div class="viz-stack-down">&darr;</div>';
    }
  });
  html += '<div class="viz-stack-down">&darr;</div><div class="viz-stack-null">NULL</div>';
  html += "</div>";
  if (hasTempNode || hasDetachedNode || (simulation && simulation.tempActionLabel)) {
    html += '<div class="viz-temp-node-wrap">';
    if (hasTempNode) {
      html += `<div class="viz-temp-node-title">${escapeHtml(simulation.tempNodeTitle || "nodo aux")}</div>`;
      html += nodeBox(escapeHtml(tempNodeValue), { className: "sim-pending" });
      if (tempLinkTargetIndex !== null) {
        const targetText =
          tempLinkTargetIndex >= 0 && tempLinkTargetIndex < items.length
            ? "ENLACE -> TOPE"
            : "ENLACE -> NULL";
        html += `<div class="viz-temp-link">${escapeHtml(targetText)}</div>`;
      }
    }
    if (hasDetachedNode) {
      html += `<div class="viz-temp-node-title">${escapeHtml(simulation.tempDetachedTitle || "nodo removido")}</div>`;
      html += nodeBox(escapeHtml(simulation.tempDetachedValue), { className: "sim-active sim-detached" });
    }
    if (simulation && simulation.tempActionLabel) {
      html += `<div class="viz-temp-note">${escapeHtml(simulation.tempActionLabel)}</div>`;
    }
    html += "</div>";
  }
  if (hint && hint.operation === "desapilar" && hint.result) {
    html += `<div class="viz-out">OUT: ${escapeHtml(hint.result)}</div>`;
  }
  html += "</div>";
  return html;
}

function renderLinkedStack(state, hint) {
  const items = state.items || [];
  const simulation = hint && hint.simulation ? hint.simulation : null;
  const activeIndices = new Set(simulation?.activeIndices || []);
  const visitedIndices = new Set(simulation?.visitedIndices || []);
  const pendingIndices = new Set(simulation?.pendingIndices || []);
  const commitIndices = new Set(simulation?.commitIndices || []);
  const tempNodeValue = simulation?.tempNodeValue;
  const detachedValue = simulation?.tempDetachedValue;
  const hasTempNode = tempNodeValue !== undefined && tempNodeValue !== null;
  const hasDetachedNode = detachedValue !== undefined && detachedValue !== null;
  const tempIsIntegrated = String(simulation?.tempNodeTitle || "").includes("integrado");
  const nodeName = (index) => `N${index + 1}`;
  const nodeClasses = (index) => {
    const classes = [];
    if (index === 0) classes.push("is-top");
    if (activeIndices.has(index)) classes.push("sim-active");
    else if (visitedIndices.has(index)) classes.push("sim-visited");
    if (pendingIndices.has(index)) classes.push("sim-pending");
    if (commitIndices.has(index)) classes.push("sim-commit");
    return classes.join(" ");
  };
  const nodeMarkup = (value, index, classes = "", nextLabel) => {
    const next = nextLabel === undefined
      ? (index + 1 < items.length ? nodeName(index + 1) : "NULL")
      : nextLabel;
    return `<article class="stack-linked-node ${classes}"><div class="stack-linked-node-id">${escapeHtml(nodeName(index))}</div><div class="stack-linked-field"><span>DATO</span><strong>${escapeHtml(value)}</strong></div><div class="stack-linked-field stack-linked-next"><span>sgte</span><strong>→ ${escapeHtml(next)}</strong></div></article>`;
  };

  let html = '<div class="stack-linked-wrap">';
  if (simulation?.opLabel) {
    html += `<p class="stack-linked-operation">${escapeHtml(simulation.opLabel)}</p>`;
  }
  html += '<div class="stack-linked-pointer"><strong>Pila</strong><span aria-hidden="true">↓</span><code>';
  html += items.length ? nodeName(0) : "NULL";
  html += '</code></div>';

  if (!items.length) {
    html += '<div class="stack-linked-null">Pila → NULL</div>';
  } else {
    html += '<div class="stack-linked-chain">';
    items.forEach((item, index) => {
      html += nodeMarkup(item.value, index, nodeClasses(index));
      html += index + 1 < items.length
        ? '<div class="stack-linked-arrow" aria-hidden="true">↓</div>'
        : '<div class="stack-linked-arrow stack-linked-null-arrow" aria-hidden="true">↓&nbsp; NULL</div>';
    });
    html += '</div>';
  }

  if (hasTempNode && !tempIsIntegrated) {
    const target = Number.isInteger(simulation?.tempLinkTargetIndex) && simulation.tempLinkTargetIndex >= 0
      ? nodeName(simulation.tempLinkTargetIndex)
      : "NULL";
    html += `<aside class="stack-linked-aux"><p><strong>aux</strong> · ${escapeHtml(simulation?.tempNodeTitle || "nodo temporal")}</p>${nodeMarkup(tempNodeValue, items.length, "sim-pending", target)}</aside>`;
  }
  if (hasDetachedNode) {
    const next = items.length ? nodeName(0) : "NULL";
    html += `<aside class="stack-linked-aux is-detached"><p><strong>aux</strong> · ${escapeHtml(simulation?.tempDetachedTitle || "nodo retirado")}</p>${nodeMarkup(detachedValue, items.length, "sim-detached", next)}${simulation?.tempActionLabel ? `<small>${escapeHtml(simulation.tempActionLabel)}</small>` : ""}</aside>`;
  } else if (simulation?.tempActionLabel) {
    html += `<p class="stack-linked-note">${escapeHtml(simulation.tempActionLabel)}</p>`;
  }
  if (hint?.operation === "desapilar" && hint.result !== undefined && hint.result !== null) {
    html += `<p class="viz-out">OUT: ${escapeHtml(hint.result)}</p>`;
  }
  html += '</div>';
  return html;
}

function renderStructuralSequential(structureId, state, hint) {
  const items = state.items || [];
  const sim = hint?.simulation || {};
  const active = new Set(sim.activeIndices || []);
  const valueField = structureId === "queue" || structureId === "linked_list" || structureId === "circular_list" ? "NRO" : "DATO";
  const node = (value, index, extra = "") => `<article class="stack-linked-node ${active.has(index) ? "sim-active" : ""} ${extra}"><div class="stack-linked-node-id">N${index + 1}</div><div class="stack-linked-field"><span>${valueField}</span><strong>${escapeHtml(value)}</strong></div><div class="stack-linked-field stack-linked-next"><span>sgte</span><strong>→ ${escapeHtml(index + 1 < items.length ? `N${index + 2}` : (structureId === "circular_list" && items.length ? "HEAD" : "NULL"))}</strong></div></article>`;
  if (structureId === "sublist") {
    const parents = items.map((item, parentIndex) => {
      const children = Array.isArray(item.children) ? item.children : [];
      const parentRef = `P${parentIndex + 1}`;
      const nextParent = parentIndex + 1 < items.length ? `P${parentIndex + 2}` : "NULL";
      const childrenMarkup = children.length
        ? children.map((child, childIndex) => {
          const childRef = `H${parentIndex + 1}.${childIndex + 1}`;
          const nextChild = childIndex + 1 < children.length ? `H${parentIndex + 1}.${childIndex + 2}` : "NULL";
          return `<div class="stack-sublist-child-entry"><article class="stack-linked-node stack-sublist-child ${active.has(parentIndex) ? "sim-active" : ""}"><div class="stack-linked-node-id">${childRef}</div><div class="stack-linked-field"><span>HIJO</span><strong>${escapeHtml(child)}</strong></div><div class="stack-linked-field stack-linked-next"><span>sgte</span><strong>→ ${nextChild}</strong></div></article>${childIndex + 1 < children.length ? '<div class="stack-sublist-child-link" aria-hidden="true"><span>→</span><small>sgte</small></div>' : '<div class="stack-sublist-child-null"><span>→</span><small>NULL</small></div>'}</div>`;
        }).join("")
        : '<div class="stack-sublist-empty">hijos → NULL</div>';

      return `<section class="stack-sublist-parent ${active.has(parentIndex) ? "sim-active" : ""}"><div class="stack-sublist-parent-head"><span class="stack-sublist-parent-label">${parentRef}</span><article class="stack-linked-node stack-sublist-parent-node"><div class="stack-linked-field"><span>PADRE</span><strong>${escapeHtml(item.parent)}</strong></div><div class="stack-linked-field stack-linked-next"><span>sgte padre</span><strong>→ ${nextParent}</strong></div></article></div><div class="stack-sublist-children" aria-label="Sublista de hijos del padre ${escapeHtml(item.parent)}"><div class="stack-sublist-children-label"><span>hijos</span><strong>→ ${children.length ? `H${parentIndex + 1}.1` : "NULL"}</strong></div>${childrenMarkup}</div></section>`;
    }).join('<div class="stack-sublist-parent-link" aria-hidden="true"><span>↓</span><small>siguiente padre</small></div>');
    const transient = sim.tempNodeValue !== undefined
      ? `<aside class="stack-linked-aux"><p><strong>aux</strong> · hijo temporal</p><div class="stack-linked-node stack-sublist-child"><div class="stack-linked-node-id">aux</div><div class="stack-linked-field"><span>HIJO</span><strong>${escapeHtml(sim.tempNodeValue)}</strong></div><div class="stack-linked-field"><span>sgte</span><strong>→ ${sim.tempLinkTargetIndex >= 0 ? `H?.${sim.tempLinkTargetIndex + 1}` : "NULL"}</strong></div></div></aside>`
      : sim.tempDetachedValue !== undefined
        ? `<aside class="stack-linked-aux is-detached"><p><strong>aux</strong> · hijo retirado ${escapeHtml(sim.tempDetachedValue)}</p><small>${escapeHtml(sim.tempActionLabel || "desconectar y liberar")}</small></aside>`
        : "";
    return `<div class="stack-linked-wrap stack-sublist-wrap">${sim.opLabel ? `<p class="stack-linked-operation">${escapeHtml(sim.opLabel)}</p>` : ""}<div class="stack-linked-pointer"><strong>HEAD</strong><span>↓</span><code>${items.length ? "P1" : "NULL"}</code></div><div class="stack-sublist-parents">${parents || '<div class="stack-linked-null">HEAD → NULL</div>'}</div>${transient}</div>`;
  }
  const labels = structureId === "queue" || structureId === "priority_queue" ? `<div class="stack-linked-pointer"><strong>delante</strong><span>→</span><code>${items.length ? "N1" : "NULL"}</code></div><div class="stack-linked-pointer"><strong>atrás</strong><span>→</span><code>${items.length ? `N${items.length}` : "NULL"}</code></div>` : `<div class="stack-linked-pointer"><strong>HEAD</strong><span>→</span><code>${items.length ? "N1" : "NULL"}</code></div>${structureId === "linked_list" && sim.activeIndices?.length ? `<div class="stack-linked-pointer"><strong>actual</strong><span>→</span><code>N${sim.activeIndices[0] + 1}</code></div>${sim.activeIndices[0] > 0 ? `<div class="stack-linked-pointer"><strong>anterior</strong><span>→</span><code>N${sim.activeIndices[0]}</code></div>` : ""}` : ""}${structureId === "circular_list" ? `<div class="stack-linked-note">TAIL → HEAD (circular)</div>` : ""}`;
  const priority = structureId === "priority_queue";
  const chain = items.map((item, i) => priority ? `<article class="stack-linked-node stack-priority-node ${active.has(i) ? "sim-active" : ""}"><div class="stack-linked-node-id">N${i + 1}</div><div class="stack-linked-field"><span>VALOR</span><strong>${escapeHtml(item.value)}</strong></div><div class="stack-linked-field"><span>PRIORIDAD</span><strong>${escapeHtml(item.priority)}</strong></div><div class="stack-linked-field stack-linked-next"><span>sgte</span><strong>→ ${i + 1 < items.length ? `N${i + 2}` : "NULL"}</strong></div></article>` : node(item.value, i)).join('<div class="stack-linked-arrow">↓</div>');
  const priorityFields = structureId === "priority_queue" && sim.tempNodePriority !== undefined
    ? `<div class="stack-linked-field"><span>PRIORIDAD</span><strong>${escapeHtml(sim.tempNodePriority)}</strong></div>` : "";
  const detachedPriority = structureId === "priority_queue" && sim.tempDetachedPriority !== undefined
    ? ` · prioridad ${escapeHtml(sim.tempDetachedPriority)}` : "";
  const transientNodeClass = structureId === "priority_queue" ? " stack-priority-node" : "";
  const transient = sim.tempNodeValue !== undefined ? `<aside class="stack-linked-aux"><p><strong>aux</strong> · nodo temporal</p><div class="stack-linked-node${transientNodeClass}"><div class="stack-linked-field"><span>${valueField}</span><strong>${escapeHtml(sim.tempNodeValue)}</strong></div>${priorityFields}<div class="stack-linked-field"><span>enlace</span><strong>→ ${sim.tempLinkTargetIndex >= 0 ? `N${sim.tempLinkTargetIndex + 1}` : "NULL"}</strong></div></div></aside>` : sim.tempDetachedValue !== undefined ? `<aside class="stack-linked-aux is-detached"><p><strong>aux</strong> · nodo retirado ${escapeHtml(sim.tempDetachedValue)}${detachedPriority}</p><small>${escapeHtml(sim.tempActionLabel || "desconectar y liberar")}</small></aside>` : "";
  return `<div class="stack-linked-wrap">${sim.opLabel ? `<p class="stack-linked-operation">${escapeHtml(sim.opLabel)}</p>` : ""}${labels}<div class="stack-linked-chain">${chain || '<div class="stack-linked-null">NULL</div>'}</div>${transient}</div>`;
}

function renderSublist(state) {
  const items = state.items || [];
  if (!items.length) {
    return '<p class="viz-empty">No hay padres en la sublista.</p>';
  }

  const nodeW = 96;
  const nodeH = 42;
  const rowGap = 24;
  const startX = 10;
  const startY = 36;
  const subStartX = 130;
  const arrowGap = 20;
  const nullGap = 44;
  const fontNode = 24;
  const fontLabel = 18;

  let maxX = subStartX + 80;

  items.forEach((item) => {
    const childCount = (item.children || []).length;
    if (childCount > 0) {
      const right =
        subStartX +
        childCount * nodeW +
        (childCount - 1) * arrowGap +
        arrowGap +
        nullGap;
      maxX = Math.max(maxX, right);
    } else {
      maxX = Math.max(maxX, subStartX + 190);
    }
  });

  const width = Math.max(520, maxX + 20);
  const height = startY + items.length * (nodeH + rowGap) + 26;

  let svg = `<svg class="viz-sub-svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;
  svg += `<text x="${startX}" y="${startY - 10}" class="viz-svg-label">HEAD</text>`;

  items.forEach((item, index) => {
    const y = startY + index * (nodeH + rowGap);
    const parent = escapeHtml(item.parent);
    const children = item.children || [];
    const hasChildren = children.length > 0;

    svg += `<rect x="${startX}" y="${y}" width="${nodeW}" height="${nodeH}" rx="6" ry="6" class="viz-svg-node${hasChildren ? " has-children" : ""}" />`;
    svg += `<text x="${startX + 14}" y="${y + fontNode}" class="viz-svg-node-text">${parent}</text>`;

    if (index < items.length - 1) {
      const downX = startX + nodeW / 2;
      const downY = y + nodeH + 14;
      svg += `<text x="${downX}" y="${downY}" text-anchor="middle" class="viz-svg-arrow">↓</text>`;
    } else {
      const nullX = startX + nodeW / 2;
      const nullY = y + nodeH + 24;
      svg += `<text x="${nullX}" y="${nullY}" text-anchor="middle" class="viz-svg-null">NULL</text>`;
    }

    svg += `<text x="${startX + nodeW + 8}" y="${y + fontLabel}" class="viz-svg-arrow">→</text>`;

    if (children.length > 0) {
      let childX = subStartX;
      children.forEach((child, childIndex) => {
        const childValue = escapeHtml(child);
        svg += `<rect x="${childX}" y="${y}" width="${nodeW}" height="${nodeH}" rx="6" ry="6" class="viz-svg-node" />`;
        svg += `<text x="${childX + 14}" y="${y + fontNode}" class="viz-svg-node-text">${childValue}</text>`;

        if (childIndex < children.length - 1) {
          svg += `<text x="${childX + nodeW + 8}" y="${y + fontLabel}" class="viz-svg-arrow">→</text>`;
          childX += nodeW + arrowGap;
        } else {
          const nullX = childX + nodeW + 14;
          svg += `<text x="${nullX}" y="${y + fontLabel}" class="viz-svg-arrow">→</text>`;
          svg += `<text x="${nullX + 18}" y="${y + fontLabel}" class="viz-svg-null">NULL</text>`;
        }
      });
    } else {
      const textX = subStartX;
      svg += `<text x="${textX}" y="${y + fontLabel}" class="viz-svg-empty">(sin hijos)</text>`;
      svg += `<text x="${textX + 122}" y="${y + fontLabel}" class="viz-svg-arrow">→</text>`;
      svg += `<text x="${textX + 142}" y="${y + fontLabel}" class="viz-svg-null">NULL</text>`;
    }
  });

  svg += "</svg>";
  return `<div class="viz-sub-svg-wrap">${svg}</div>`;
}

function renderVisualState(structureId, state, container, hint) {
  if (!state || !container) {
    return;
  }

  let inner = `<div class="viz-meta"><strong>${escapeHtml(state.title || "Estado")}</strong> | Tamano: ${escapeHtml(state.size ?? 0)}</div>`;

  if (structureId === "stack") {
    inner += container.dataset.stackVisualMode === "linked"
      ? renderLinkedStack(state, hint)
      : renderStack(state, hint);
  } else if (container.dataset.stackVisualMode === "linked" || container.dataset.structuralVisualMode === "nodes") {
    inner += renderStructuralSequential(structureId, state, hint);
  } else if (structureId === "queue") {
    inner += renderQueue(state, hint);
  } else if (structureId === "priority_queue") {
    inner += renderPriorityQueue(state, hint);
  } else if (structureId === "linked_list") {
    inner += renderLinearWithHeadTail(state, false, hint);
  } else if (structureId === "circular_list") {
    inner += renderLinearWithHeadTail(state, true, hint);
  } else if (structureId === "sublist") {
    inner += renderSublist(state);
  } else {
    inner += '<p class="viz-empty">Tipo de visualizacion no soportado.</p>';
  }

  container.innerHTML = `<div class="viz-canvas"><div class="viz-stage">${inner}</div></div>`;
  if (structureId === "circular_list") {
    requestAnimationFrame(() => {
      drawCircularLoop(container);
    });
  }
}

function appendSequentialSemanticOverlay(structureId, state, container, frame) {
  if (!container || !frame) return;
  const items = Array.isArray(state?.items) ? state.items : [];
  const chips = [];
  const pointerNames = (frame.pointers || []).filter((item) => item.changed || item.target !== null).map((item) => item.name);
  if (structureId === "stack") {
    chips.push(`TOP → ${items.length ? sequentialValue(items[0].value) : "NULL"}`, "Regla: LIFO");
    if (pointerNames.includes("aux")) chips.push("auxiliar activo");
    if (frame.concept === "free") chips.push("nodo desconectado → free");
  } else if (structureId === "queue") {
    chips.push(`DELANTE → ${items.length ? sequentialValue(items[0].value) : "NULL"}`, `ATRÁS → ${items.length ? sequentialValue(items[items.length - 1].value) : "NULL"}`, "Regla: FIFO");
    chips.push(items.length === 0 ? "estado vacío" : items.length === 1 ? "estado unitario" : "estado múltiple");
  } else if (structureId === "priority_queue") {
    const priorities = items.map((item) => String(item.priority));
    const tie = priorities.some((value, index) => priorities.indexOf(value) !== index);
    chips.push("enlaces: orden de llegada", "selección: prioridad mínima");
    if (frame.concept === "condition") chips.push("candidato evaluado en el recorrido");
    if (Number.isInteger(state.out_index) && state.out_index >= 0) chips.push(`seleccionado: llegada #${state.out_index + 1}`);
    if (tie) chips.push("empate → gana quien llegó antes");
  } else if (structureId === "linked_list") {
    chips.push(`HEAD → ${items.length ? sequentialValue(items[0].value) : "NULL"}`, "cadena alcanzable → NULL");
    pointerNames.filter((name) => ["actual", "anterior", "p", "q", "t"].includes(name)).forEach((name) => chips.push(`${name} visible`));
    if (frame.concept === "link") chips.push("enlace anterior → enlace nuevo");
  } else if (structureId === "circular_list") {
    chips.push(`HEAD → ${items.length ? sequentialValue(items[0].value) : "NULL"}`, items.length ? "TAIL.next → HEAD ↻" : "cierre vacío");
    if (frame.loop?.active) chips.push("salida: volver al inicio");
  } else if (structureId === "sublist") {
    chips.push("propiedad: padre → hijos", "ramas no activas: sin cambios");
    if (frame.variables?.some((item) => item.name === "parent")) chips.push(`rama activa: padre ${sequentialValue(frame.variables.find((item) => item.name === "parent")?.value)}`);
  }
  const strip = document.createElement("div");
  strip.className = "seq-semantic-strip";
  strip.innerHTML = chips.map((chip) => `<span class="seq-semantic-chip">${escapeHtml(chip)}</span>`).join("") + `<span class="seq-invariant-status">✓ Invariante: ${escapeHtml(frame.invariant?.text || "verificado")}</span>`;
  container.querySelector(".viz-canvas")?.appendChild(strip);
}

const SEQUENTIAL_COMPARISONS = Object.freeze({
  "stack-queue": { left: "Pila", right: "Cola", steps: [["Entrada común", "10, 20, 30", "10, 20, 30"], ["Extremo de extracción", "TOP = 30", "FRONT = 10"], ["Resultado", "sale 30 (LIFO)", "sale 10 (FIFO)"]], conclusion: "Con las mismas inserciones, la pila retira el último elemento y la cola retira el primero." },
  "queue-priority": { left: "Cola", right: "Cola de prioridad", steps: [["Llegada inmutable", "10(P3), 20(P1), 30(P2)", "10(P3), 20(P1), 30(P2)"], ["Selección", "FRONT = 10", "candidato = 20(P1)"], ["Resultado", "sale 10 por llegada", "sale 20 por prioridad"]], conclusion: "La cola física conserva llegada en ambos lados; solo la política de selección cambia." },
  "linear-circular": { left: "Lista lineal", right: "Lista circular", steps: [["Nodos", "10 → 20 → 30", "10 → 20 → 30"], ["Último enlace", "30 → NULL", "30 → HEAD"], ["Terminación", "actual == NULL", "actual == HEAD otra vez"]], conclusion: "La circularidad cambia el último enlace y obliga a terminar al volver al inicio." },
  "list-sublist": { left: "Lista", right: "Sublista", steps: [["Datos", "P1 → P2", "P1(h11) → P2(h21)"], ["Cambio aislado", "insertar tras P1", "insertar h12 en P1"], ["Resultado", "cambia cadena principal", "P2 y sus hijos no cambian"]], conclusion: "La sublista añade propiedad padre-hijo y protege las ramas no seleccionadas." },
});

function renderSequentialComparison(kind, cursor, grid, conclusion) {
  const source = SEQUENTIAL_COMPARISONS[kind] || SEQUENTIAL_COMPARISONS["stack-queue"];
  // Las dos vistas reciben copias profundas; ninguna puede mutar la secuencia base congelada.
  const left = structuredClone(source.steps); const right = structuredClone(source.steps);
  const index = Math.max(0, Math.min(Number(cursor) || 0, source.steps.length - 1));
  const row = source.steps[index];
  grid.innerHTML = `<article class="seq-compare-card"><h4>${escapeHtml(source.left)}</h4><p><strong>${escapeHtml(row[0])}</strong></p><p class="seq-compare-sequence">${escapeHtml(left[index][1])}</p></article><article class="seq-compare-card"><h4>${escapeHtml(source.right)}</h4><p><strong>${escapeHtml(row[0])}</strong></p><p class="seq-compare-sequence">${escapeHtml(right[index][2])}</p></article>`;
  conclusion.textContent = `Conclusión guiada: ${source.conclusion}`;
}

function showMessage(text, success) {
  const box = byId("message-box");
  if (!box) {
    return;
  }
  const hasPrintfConsole = Boolean(byId("seq-printf-console"));
  if (success && hasPrintfConsole) {
    box.textContent = "";
    box.className = "message";
    return;
  }
  box.textContent = text || "";
  box.className = success ? "message ok" : "message error";
}

function updateDidacticPanel(model, operationName) {
  const recordBox = byId("tad-record");
  const pseudoTitle = byId("op-pseudocode-title");
  const pseudoBox = byId("op-pseudocode");
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

  renderDidacticCode(recordBox, didactic.record || "Estructura no documentada.", codeTitle);
  pseudoTitle.textContent = selectedLabel ? `${codeTitle}: ${selectedLabel}` : codeTitle;
  renderDidacticCode(pseudoBox, opMap[selectedOp] || fallback, codeTitle);
  enhanceSequentialCodeNavigation(null);
}

function summarizePayload(payload) {
  if (!payload || typeof payload !== "object") {
    return "";
  }
  const parts = Object.entries(payload)
    .filter(([, value]) => String(value).trim() !== "")
    .map(([key, value]) => `${key}=${value}`);
  return parts.join(", ");
}

function extractSubroutineName(pseudoCode, fallback) {
  if (!pseudoCode) {
    return fallback;
  }
  const lines = String(pseudoCode).split("\n");
  const pseudoLine = lines.find((line) => {
    const trimmed = String(line).trim();
    return /^(SubProceso|Funcion|Procedimiento|Proceso)\s+/i.test(trimmed);
  });
  if (pseudoLine) {
    const pseudoMatch = pseudoLine.trim().match(/(?:SubProceso|Funcion|Procedimiento|Proceso)\s+([A-Za-z_][A-Za-z0-9_]*)/i);
    if (pseudoMatch && pseudoMatch[1]) {
      return pseudoMatch[1];
    }
  }

  for (let i = 0; i < lines.length; i += 1) {
    const trimmed = String(lines[i]).trim();
    if (!trimmed) {
      continue;
    }
    if (
      trimmed.startsWith("/*") ||
      trimmed.startsWith("*") ||
      trimmed.startsWith("//") ||
      trimmed.startsWith("@")
    ) {
      continue;
    }
    if (/^(if|while|for|switch|return)\b/.test(trimmed)) {
      continue;
    }
    const cMatch = trimmed.match(
      /^(?:static\s+)?[A-Za-z_][A-Za-z0-9_\s\*]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*\{?\s*$/,
    );
    if (cMatch && cMatch[1]) {
      return cMatch[1];
    }
  }
  return fallback;
}

function getSubroutineName(model, operationName, fallback) {
  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const pseudoCode = opMap[operationName] || "";
  return extractSubroutineName(pseudoCode, fallback || operationName || "Operacion");
}

function createHistoryEntry(subroutine, payloadText, resultText, operationName, payloadMap) {
  return {
    subroutine: subroutine || "Operacion",
    payload: payloadText || "-",
    result: resultText || "-",
    operation: operationName || "",
    payloadMap: payloadMap && typeof payloadMap === "object" ? { ...payloadMap } : {},
  };
}

function buildOrderedArgs(item, operationCatalog, structureId) {
  const payloadMap = item && item.payloadMap && typeof item.payloadMap === "object"
    ? item.payloadMap
    : {};
  const opName = item && item.operation ? item.operation : "";
  const operation = operationCatalog && opName ? operationCatalog.get(opName) : null;
  const used = new Set();
  const args = [];

  if (operation && Array.isArray(operation.inputs)) {
    operation.inputs.forEach((inputField) => {
      const key = inputField.name;
      const value = payloadMap[key];
      if (value === undefined || value === null || String(value).trim() === "") {
        return;
      }
      used.add(key);
      args.push(String(value).trim());
    });
  }

  Object.keys(payloadMap).forEach((key) => {
    if (used.has(key)) {
      return;
    }
    const value = payloadMap[key];
    if (value === undefined || value === null || String(value).trim() === "") {
      return;
    }
    args.push(String(value).trim());
  });

  if (!args.length && item && item.payload && item.payload !== "-") {
    const parsed = String(item.payload)
      .split(",")
      .map((part) => part.trim())
      .filter((part) => part.length > 0)
      .map((part) => {
        const pieces = part.split("=");
        if (pieces.length === 2) {
          return pieces[1].trim();
        }
        return part;
      });
    if (parsed.length) {
      args.push(...parsed);
    }
  }

  const tadArg = getMainStructureArgument(structureId);
  if (tadArg) {
    args.unshift(tadArg);
  }
  return args;
}

function buildMainDeclarationLines(structureId) {
  const mappings = {
    stack: ["ptrPila pila = NULL;"],
    queue: ["struct Cola cola = { .delante = NULL, .atras = NULL };"],
    priority_queue: ["ColaPrioridad cp;", "cp_inicializar(&cp);"],
    linked_list: ["Tlista lista = NULL;"],
    circular_list: ["ListaCircular lc;", "lcir_inicializar(&lc);"],
    sublist: ["Nodo *sublista = NULL;", "sublista_inicializar(&sublista);"],
  };
  return mappings[structureId] || ["// Declarar e inicializar el TAD seleccionado"];
}

function getMainStructureArgument(structureId) {
  const mappings = {
    stack: "&pila",
    queue: "&cola",
    priority_queue: "&cp",
    linked_list: "&lista",
    circular_list: "&lc",
    sublist: "&sublista",
  };
  return mappings[structureId] || "";
}

function renderActionHistory(history, container, structureId, operationCatalog) {
  if (!container) {
    return;
  }
  if (!history.length) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }
  const declarations = buildMainDeclarationLines(structureId);
  const codeLines = [
    "int main(void) {",
    "    // Declaracion de la estructura",
    ...declarations.map((line) => `    ${line}`),
    "",
    "    // Historial de ejecucion del usuario",
  ];

  history.forEach((item, index) => {
    if (typeof item === "string") {
      codeLines.push(`    // Paso ${index + 1}: ${item}`);
      return;
    }
    const fn = (item.subroutine || "Operacion").replace(/\s+/g, "");
    const args = buildOrderedArgs(item, operationCatalog, structureId).join(", ");
    const call = `${fn}(${args});`;
    codeLines.push(`    ${call}`);
    codeLines.push(`    printf("${toCStringLiteral(item.result || "Operacion aplicada.")}\\n");`);
    codeLines.push(`    // ${item.result || "Operacion aplicada."}`);
  });

  codeLines.push("    return 0;");
  codeLines.push("}");

  let hlState = { inBlockComment: false };
  const codeHtml = codeLines
    .map((line, index) => {
      const highlighted = highlightCLine(line, hlState);
      hlState = highlighted.state;
      return `<span class="code-line" data-line="${index}">${highlighted.html || "&nbsp;"}</span>`;
    })
    .join("");

  container.innerHTML = (
    "<li class=\"didactic-history-item history-main-wrap\">" +
    "<div class=\"didactic-history-head\">Programa principal (main)</div>" +
    `<pre class="didactic-code didactic-history-main">${codeHtml}</pre>` +
    "</li>"
  );
}

function initStructurePage(model) {
  const form = byId("operation-form");
  const operationSelect = byId("operation-select");
  const inputsContainer = byId("operation-inputs");
  const resetButton = byId("reset-button");
  const visualContainer = byId("visual-state");
  const historyBox = byId("action-history");
  const simExecuteButton = byId("seq-sim-execute");
  const simPlayButton = byId("seq-sim-play");
  const simPrepareButton = byId("seq-sim-prepare");
  const simPauseButton = byId("seq-sim-pause");
  const simStartButton = byId("seq-sim-start");
  const simPrevButton = byId("seq-sim-prev");
  const simStepButton = byId("seq-sim-step");
  const simEndButton = byId("seq-sim-end");
  const simRepeatButton = byId("seq-sim-repeat");
  const simStatus = byId("seq-sim-status");
  const stepToggle = byId("seq-step-toggle");
  const speedSlider = byId("seq-speed-slider");
  const speedValue = byId("seq-speed-value");
  const printfConsole = byId("seq-printf-console");
  const restartExecutionButton = byId("seq-restart-execution");
  const hideComments = byId("seq-hide-comments");
  const pedagogySummary = byId("seq-pedagogy-summary");
  // Las estructuras secuenciales usan siempre explicaciones de nivel intermedio.
  const learningLevel = null;
  const progressSlider = byId("seq-progress-slider");
  const progressDetail = byId("seq-progress-detail");
  const predictionsEnabled = byId("seq-predictions-enabled");
  const practiceMode = byId("seq-practice-mode");
  const predictionPanel = byId("seq-prediction-panel");
  const predictionQuestion = byId("seq-prediction-question");
  const predictionChoices = byId("seq-prediction-choices");
  const predictionFeedback = byId("seq-prediction-feedback");
  const predictionHint = byId("seq-prediction-hint");
  const predictionSkip = byId("seq-prediction-skip");
  const conceptProgressBox = byId("seq-concept-progress");
  const resetLearningButton = byId("seq-reset-learning");
  const compareKind = byId("seq-compare-kind");
  const compareRun = byId("seq-compare-run");
  const compareProgress = byId("seq-compare-progress");
  const compareGrid = byId("seq-compare-grid");
  const compareConclusion = byId("seq-compare-conclusion");
  const exportImageButton = byId("seq-export-image");
  const exportSummaryButton = byId("seq-export-summary");

  if (!form || !operationSelect || !inputsContainer || !visualContainer) {
    return;
  }

  const operations = model.operations || [];
  const visibleOperations = operations.filter(
    (op) => !op.hidden && !(model.id === "priority_queue" && op.name === "frente"),
  );
  let selected = visibleOperations[0] || operations[0] || null;
  const operationLabel = new Map(operations.map((op) => [op.name, op.label]));
  const operationCatalog = new Map(operations.map((op) => [op.name, op]));
  const actionHistory = [];
  const consoleState = {
    trace: null,
    fallbackMessage: "",
  };
  const visualTraceState = {
    operationName: "",
    payload: {},
    frames: [],
    totalSteps: 0,
  };
  const lastVisualRender = {
    state: model.visual_state,
    hint: null,
  };
  function renderCurrentVisual(state, hint) {
    lastVisualRender.state = state;
    lastVisualRender.hint = hint;
    renderVisualState(model.id, state, visualContainer, hint);
  }
  let playbackSpeed = 1;
  let playbackSpeedSetting = 0;
  let currentPedagogyFrame = null;
  let predictionPendingIndex = -1;
  let predictionHintLevel = 0;
  const presentationKey = `sequential-presentation:${model.id}`;
  const learningProgressKey = `sequential-learning-progress:${model.id}`;
  function readLearningProgress() { try { return JSON.parse(window.sessionStorage.getItem(learningProgressKey) || '{"attempts":0,"correct":0,"concepts":{}}'); } catch (_error) { return { attempts: 0, correct: 0, concepts: {} }; } }
  let learningProgress = readLearningProgress();
  function renderLearningProgress() { if (conceptProgressBox) conceptProgressBox.textContent = `Progreso conceptual de esta sesión: ${learningProgress.correct}/${learningProgress.attempts} predicciones correctas · ${Object.keys(learningProgress.concepts || {}).length} conceptos practicados.`; }
  function saveLearningProgress() { try { window.sessionStorage.setItem(learningProgressKey, JSON.stringify(learningProgress)); } catch (_error) { /* optional */ } renderLearningProgress(); }
  function readPresentation() {
    try { return JSON.parse(window.sessionStorage.getItem(presentationKey) || "{}"); } catch (_error) { return {}; }
  }
  function writePresentation(extra = {}) {
    const current = operationCatalog.get(operationSelect.value);
    const payload = current ? collectPayload(current) : {};
    try { window.sessionStorage.setItem(presentationKey, JSON.stringify({ operation: operationSelect.value, payload, level: learningLevel?.value || "intermediate", cursor: traceCursor, ...extra })); } catch (_error) { /* optional */ }
  }

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
  function collectPrintfConsoleLines(trace, cursor) {
    if (!trace || !Array.isArray(trace.steps) || cursor < 0) {
      return [];
    }
    const limit = Math.min(cursor, trace.steps.length - 1);
    const out = [];
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const emitted = Array.isArray(step.console) ? step.console : [];
      emitted.forEach((line) => pushUniqueConsoleLine(out, line));
    }
    return out;
  }
  function refreshPrintfConsole(cursor) {
    const lines = collectPrintfConsoleLines(consoleState.trace, cursor);
    const fallback = consoleState.fallbackMessage || "(sin salida printf en esta ruta)";
    renderPrintfConsole(printfConsole, lines, fallback);
  }
  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: byId("op-pseudocode"),
      statusElement: simStatus,
      counterElement: byId("seq-sim-counter"),
      renderState: (stateSnapshot, stepMeta) => {
        // El backend conserva el estado canónico; la vista enlazada añade solo
        // metadatos temporales de la traza (aux, sgte y liberación) para enseñar
        // la misma transición que ejecuta el código C.
        const runtimeCursor = tracePlayer?.getCursor?.() ?? -1;
        const stepIndex = Math.max(0, runtimeCursor + 1);
        const frameIndex = (visualContainer.dataset.stackVisualMode === "linked" || visualContainer.dataset.structuralVisualMode === "nodes")
          ? resolveFrameIndexForStep(
            model.id,
            visualTraceState.operationName,
            stepIndex,
            visualTraceState.totalSteps,
            visualTraceState.frames,
            stepMeta,
          )
          : -1;
        // El último paso siempre vuelve al snapshot canónico del intérprete.
        // Así, paso a paso, «Ejecutar operación» desde un cursor intermedio y
        // el modo rápido terminan en exactamente el mismo estado del TAD.
        const isFinalTraceStep = visualTraceState.totalSteps > 0
          && stepIndex >= visualTraceState.totalSteps - 1;
        const visualFrame = !isFinalTraceStep && frameIndex >= 0
          ? visualTraceState.frames[frameIndex]
          : null;
        renderCurrentVisual(
          visualFrame?.state || stateSnapshot,
          visualFrame ? {
            operation: visualTraceState.operationName,
            payload: visualTraceState.payload,
            simulation: visualFrame.simulation,
          } : null,
        );
        appendSequentialSemanticOverlay(model.id, stateSnapshot, visualContainer, stepMeta?.pedagogy);
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        traceCursor = cursor;
        traceTotalSteps = event && event.trace && Array.isArray(event.trace.steps)
          ? event.trace.steps.length
          : 0;
        refreshPrintfConsole(cursor);
        const step = event && event.step ? event.step : null;
        enhanceSequentialCodeNavigation(step && Number.isInteger(step.line_index) ? step.line_index : null);
        if (step && step.pedagogy) { currentPedagogyFrame = step.pedagogy; renderSequentialPedagogyFrame(currentPedagogyFrame, learningLevel?.value || "intermediate"); }
        if (progressSlider) { progressSlider.max = String(traceTotalSteps); progressSlider.value = String(Math.max(0, cursor + 1)); progressSlider.disabled = traceTotalSteps === 0; }
        if (progressDetail) progressDetail.textContent = `Paso ${Math.max(0, cursor + 1)} · ${step?.pedagogy?.call_stack?.[0]?.function || "sin función"} · ${step?.pedagogy?.phase?.label || "sin fase"} · ${step?.pedagogy?.concept || "sin concepto"}`;
        writePresentation({ cursor });
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
  initSequentialResponsiveWorkspace();
  renderLearningProgress();
  hideComments?.addEventListener("change", () => enhanceSequentialCodeNavigation(null));
  restartExecutionButton?.addEventListener("click", () => { tracePlayer?.reset(); setSimulationButtonsEnabled(); });

  visibleOperations.forEach((operation) => {
    const option = document.createElement("option");
    option.value = operation.name;
    option.textContent = operation.label;
    operationSelect.appendChild(option);
  });
  operationSelect.disabled = visibleOperations.length === 0;
  const savedPresentation = readPresentation();
  if (savedPresentation.operation && operationCatalog.has(savedPresentation.operation)) selected = operationCatalog.get(savedPresentation.operation);
  if (selected) {
    operationSelect.value = selected.name;
  }

  if (learningLevel) learningLevel.value = ["basic", "intermediate", "advanced"].includes(savedPresentation.level) ? savedPresentation.level : "intermediate";
  renderOperationInputs(selected, inputsContainer);
  if (savedPresentation.payload && selected) selected.inputs.forEach((field) => { const input = byId(`field-${field.name}`); if (input && Object.prototype.hasOwnProperty.call(savedPresentation.payload, field.name)) input.value = savedPresentation.payload[field.name]; });
  updateDidacticPanel(model, selected ? selected.name : "");
  renderCurrentVisual(model.visual_state, null);

  (model.history || []).forEach((step) => {
    const opName = String(step.operation || "");
    const label = operationLabel.get(opName) || opName;
    const subroutine = getSubroutineName(model, opName, label);
    const payloadText = summarizePayload(step.payload || {});
    pushUniqueHistoryEntry(
      actionHistory,
      createHistoryEntry(
        subroutine,
        payloadText || "-",
        "Operacion aplicada.",
        opName,
        step.payload || {},
      ),
    );
  });
  renderActionHistory(actionHistory, historyBox, model.id, operationCatalog);
  refreshPrintfConsole(-1);

  function initStackPilotPanels() {
    const currentViewButton = byId("stack-view-current");
    const linkedViewButton = byId("stack-view-linked");
    // La preferencia es de presentación por TAD; no debe mezclarse entre pantallas
    // ni formar parte del historial de operaciones.
    const stackViewStorageKey = `sequential-structural-visual-mode:${model.id}`;
    const setStackVisualMode = (mode) => {
      const linked = mode === "linked";
      visualContainer.dataset.stackVisualMode = linked ? "linked" : "current";
      currentViewButton?.classList.toggle("is-active", !linked);
      linkedViewButton?.classList.toggle("is-active", linked);
      currentViewButton?.setAttribute("aria-pressed", String(!linked));
      linkedViewButton?.setAttribute("aria-pressed", String(linked));
      try { window.sessionStorage.setItem(stackViewStorageKey, linked ? "linked" : "current"); } catch (_error) { /* optional */ }
      renderCurrentVisual(lastVisualRender.state, lastVisualRender.hint);
    };
    let savedVisualMode = "current";
    try { savedVisualMode = window.sessionStorage.getItem(stackViewStorageKey) || "current"; } catch (_error) { /* optional */ }
    setStackVisualMode(savedVisualMode);
    currentViewButton?.addEventListener("click", () => setStackVisualMode("current"));
    linkedViewButton?.addEventListener("click", () => setStackVisualMode("linked"));
    const predictionStage = document.querySelector(".is-stack-pilot > .seq-predict");
    const predictionOptIn = byId("seq-predictions-enabled");
    if (predictionOptIn) predictionOptIn.checked = false;
    predictionStage?.remove();
    document.querySelector(".is-stack-pilot > .seq-compare")?.remove();
    const prepareStage = document.querySelector(".is-stack-pilot > .seq-prepare");
    const executeStage = document.querySelector(".is-stack-pilot > .seq-execute");
    if (prepareStage && executeStage && executeStage.parentElement !== prepareStage) {
      prepareStage.appendChild(executeStage);
    }
    const actionGroup = document.querySelector(".seq-execute .actions");
    const technicalControls = document.querySelector(".seq-execute > .didactic-technical");
    if (actionGroup && !actionGroup.querySelector(".seq-pilot-step-toggle")) {
      ["seq-sim-prepare", "seq-sim-play", "seq-sim-pause", "seq-sim-start", "seq-sim-end", "seq-sim-repeat", "seq-restart-execution", "reset-button"].forEach((id) => byId(id)?.remove());
      technicalControls?.remove();
      const stepToggleButton = document.createElement("button");
      stepToggleButton.type = "button";
      stepToggleButton.className = "btn secondary seq-pilot-step-toggle";
      stepToggleButton.textContent = "Paso a paso";
      const stepNavigation = document.createElement("div");
      stepNavigation.className = "seq-pilot-step-navigation";
      stepNavigation.hidden = true;
      stepNavigation.append(byId("seq-sim-prev"), byId("seq-sim-step"));
      stepToggleButton.setAttribute("aria-expanded", "false");
      stepToggleButton.addEventListener("click", () => {
        const expanded = stepNavigation.hidden;
        stepNavigation.hidden = !expanded;
        stepToggleButton.setAttribute("aria-expanded", String(expanded));
        stepToggleButton.textContent = expanded ? "Cerrar paso a paso" : "Paso a paso";
      });
      const traceStatus = document.createElement("div");
      traceStatus.className = "seq-pilot-trace-status";
      ["seq-progress-detail", "seq-sim-counter", "seq-sim-status"].forEach((id) => {
        const item = byId(id);
        if (item) traceStatus.appendChild(item);
      });
      actionGroup.append(stepToggleButton, stepNavigation, traceStatus);
    }
    const storageKey = "sequential-stack-pilot-panels-v2";
    let saved = {};
    try { saved = JSON.parse(window.sessionStorage.getItem(storageKey) || "{}"); } catch (_error) { saved = {}; }
    [
      ["seq-predict-title", "seq-predict", "Predecir"],
      ["seq-understand-title", "seq-understand", "Comprender"],
      ["seq-compare-title", "seq-compare", "Comparar"],
      ["seq-reflect-title", "seq-reflect", "Resultados de la ejecución"],
    ].forEach(([headingId, sectionClass, label]) => {
      const heading = byId(headingId);
      const section = heading?.closest(`.${sectionClass}`);
      if (!heading || !section || heading.querySelector(".seq-pilot-toggle")) return;
      section.id = `stack-pilot-${sectionClass}`;
      section.classList.add("seq-pilot-panel");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "seq-pilot-toggle";
      button.setAttribute("aria-controls", section.id);
      const setExpanded = (expanded) => {
        section.classList.toggle("seq-pilot-collapsed", !expanded);
        button.setAttribute("aria-expanded", String(expanded));
        button.textContent = expanded ? "Ocultar" : "Mostrar";
        saved[sectionClass] = expanded;
        try { window.sessionStorage.setItem(storageKey, JSON.stringify(saved)); } catch (_error) { /* optional */ }
      };
      button.setAttribute("aria-label", `Mostrar u ocultar ${label}`);
      button.addEventListener("click", () => setExpanded(section.classList.contains("seq-pilot-collapsed")));
      heading.appendChild(button);
      setExpanded(saved[sectionClass] === true);
    });
  }

  initStackPilotPanels();

  function initSiblingSequentialViews() {
    if (model.id === "stack") return;
    const current = byId("seq-view-current"); const structural = byId("seq-view-structural");
    const modeKey = `sequential-structural-mode:${model.id}`;
    const setMode = (mode) => {
      const nodes = mode === "nodes";
      visualContainer.dataset.structuralVisualMode = nodes ? "nodes" : "current";
      current?.classList.toggle("is-active", !nodes); structural?.classList.toggle("is-active", nodes);
      current?.setAttribute("aria-pressed", String(!nodes)); structural?.setAttribute("aria-pressed", String(nodes));
      try { sessionStorage.setItem(modeKey, nodes ? "nodes" : "current"); } catch (_error) { /* optional */ }
      renderCurrentVisual(lastVisualRender.state, lastVisualRender.hint);
    };
    try { setMode(sessionStorage.getItem(modeKey) || "current"); } catch (_error) { setMode("current"); }
    current?.addEventListener("click", () => setMode("current")); structural?.addEventListener("click", () => setMode("nodes"));
    const heading = byId("seq-reflect-title"); const section = heading?.closest(".seq-reflect");
    if (heading && section && !heading.querySelector(".seq-pilot-toggle")) {
      const button = document.createElement("button"); button.type = "button"; button.className = "seq-pilot-toggle";
      const apply = (expanded) => { section.classList.toggle("seq-pilot-collapsed", !expanded); button.textContent = expanded ? "Ocultar" : "Mostrar"; button.setAttribute("aria-expanded", String(expanded)); };
      button.addEventListener("click", () => apply(section.classList.contains("seq-pilot-collapsed"))); heading.appendChild(button); apply(false);
    }
  }
  initSiblingSequentialViews();

  let pendingExecution = false;
  let traceSelectionKey = "";
  let traceExecutionRevision = 0;
  let traceCursor = -1;
  let traceTotalSteps = 0;
  let lockStepUntilInput = false;

  function isStepByStepEnabled() {
    return !stepToggle || Boolean(stepToggle.checked);
  }

  function isCurrentSelectionValid() {
    const current = operations.find((item) => item.name === operationSelect.value);
    if (!current) {
      return false;
    }
    return current.inputs.every((field) => {
      const element = byId(`field-${field.name}`);
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

  function setSimulationButtonsEnabled() {
    const stepMode = isStepByStepEnabled();
    const hasTrace = Boolean(tracePlayer && tracePlayer.hasTrace());
    const busy = pendingExecution;
    const canExecute = isCurrentSelectionValid();
    const runtimeCursor = tracePlayer && typeof tracePlayer.getCursor === "function"
      ? tracePlayer.getCursor()
      : traceCursor;
    const runtimeTotalSteps = tracePlayer && typeof tracePlayer.getTotalSteps === "function"
      ? tracePlayer.getTotalSteps()
      : traceTotalSteps;
    const hasProgress = hasTrace && runtimeCursor >= 0;
    const atEnd = hasTrace && runtimeTotalSteps > 0 && runtimeCursor >= runtimeTotalSteps - 1;
    if (simExecuteButton) simExecuteButton.disabled = busy || !canExecute;
    if (simPlayButton) simPlayButton.disabled = busy || !stepMode || !hasTrace || predictionPendingIndex >= 0;
    [simPauseButton, simStartButton, simEndButton, simRepeatButton, restartExecutionButton].forEach((button) => { if (button) button.disabled = busy || !stepMode || !hasTrace; });
    if (simPrepareButton) simPrepareButton.disabled = busy || !stepMode || !hasTrace;
    if (simPrevButton) {
      simPrevButton.disabled = busy || !stepMode || !hasProgress;
    }
    if (simStepButton) {
      simStepButton.disabled = busy || !stepMode || !hasTrace || atEnd || lockStepUntilInput || predictionPendingIndex >= 0;
    }
    if (speedSlider) {
      speedSlider.disabled = busy || !stepMode;
    }
  }

  function invalidateTrace(message) {
    traceSelectionKey = "";
    traceCursor = -1;
    traceTotalSteps = 0;
    lockStepUntilInput = false;
    consoleState.trace = null;
    consoleState.fallbackMessage = "";
    visualTraceState.operationName = "";
    visualTraceState.payload = {};
    visualTraceState.frames = [];
    visualTraceState.totalSteps = 0;
    tracePlayer?.clear(message || "Ejecuta una operación para crear una traza; después podrás preparar o reproducir.");
    predictionPendingIndex = -1; if (predictionPanel) predictionPanel.hidden = true;
    refreshPrintfConsole(-1);
    setSimulationButtonsEnabled();
  }

  function predictionForStep(step) {
    const frame = step?.pedagogy;
    if (!frame) return null;
    const pointerChanged = (frame.pointers || []).some((item) => item.changed);
    const extremeChanged = (frame.state_changes || []).some((item) => ["empty", "size", "items"].includes(item));
    if (!["condition", "link", "free"].includes(frame.concept) && !pointerChanged && !extremeChanged) return null;
    if (frame.concept === "condition") return { question: `¿La condición «${frame.condition?.substituted || frame.condition?.source}» resulta verdadera?`, expected: frame.condition?.result === true, hint: ["Observa los valores sustituidos.", "Compara ambos operandos de la condición.", `La ruta registrada ${frame.condition?.result ? "entra" : "no entra"} al cuerpo.`] };
    const changes = (frame.state_changes || []).length > 0 || pointerChanged || frame.concept === "free";
    const label = frame.concept === "free" ? "liberará y hará inalcanzable un nodo" : frame.concept === "link" ? "reasignará un enlace" : "cambiará un extremo o el tamaño";
    return { question: `¿Esta instrucción ${label}?`, expected: changes, hint: ["Compara el estado anterior con el siguiente frame.", `Concepto actual: ${frame.concept}.`, changes ? "Sí existe una transición registrada." : "El estado observable permanece estable."] };
  }

  async function advancePendingPrediction(answered) {
    if (predictionPendingIndex < 0) return;
    predictionPendingIndex = -1; predictionHintLevel = 0;
    if (predictionPanel && !answered) predictionPanel.hidden = true;
    if (answered) predictionChoices?.querySelectorAll("button").forEach((button) => { button.disabled = true; });
    const advanced = await tracePlayer?.step();
    visualContainer.classList.remove("seq-practice-hidden");
    if (advanced && tracePlayer.isAtEnd()) lockStepUntilInput = true;
    if (!answered && simStatus) simStatus.textContent = "Continuaste sin responder; revisa la explicación del frame.";
    setSimulationButtonsEnabled();
  }

  function requestPrediction(step, index) {
    const prompt = predictionForStep(step);
    if (!prompt || !predictionsEnabled?.checked) return false;
    // Predecir acompaña la traza, pero no debe interrumpir su avance.
    predictionPendingIndex = -1; predictionHintLevel = 0;
    const predictionStage = predictionPanel?.closest(".seq-predict");
    if (predictionStage?.classList.contains("seq-pilot-collapsed")) {
      predictionStage.classList.remove("seq-pilot-collapsed");
      const toggle = predictionStage.querySelector(".seq-pilot-toggle");
      if (toggle) { toggle.setAttribute("aria-expanded", "true"); toggle.textContent = "Ocultar"; }
      try {
        const savedPanels = JSON.parse(window.sessionStorage.getItem("sequential-stack-pilot-panels-v2") || "{}");
        savedPanels.seqPredict = true;
        window.sessionStorage.setItem("sequential-stack-pilot-panels-v2", JSON.stringify(savedPanels));
      } catch (_error) { /* optional storage */ }
    }
    predictionPanel.hidden = false; predictionQuestion.textContent = prompt.question; predictionFeedback.textContent = "Selecciona una respuesta o continúa sin responder.";
    predictionChoices.innerHTML = '<button class="btn" type="button" data-answer="true">Sí</button><button class="btn secondary" type="button" data-answer="false">No</button>';
    if (practiceMode?.checked) visualContainer.classList.add("seq-practice-hidden");
    predictionChoices.querySelectorAll("[data-answer]").forEach((button) => button.addEventListener("click", () => {
      const answer = button.dataset.answer === "true"; const correct = answer === prompt.expected;
      learningProgress.attempts += 1; if (correct) learningProgress.correct += 1; learningProgress.concepts[step.pedagogy.concept] = (learningProgress.concepts[step.pedagogy.concept] || 0) + 1; saveLearningProgress();
      predictionFeedback.textContent = correct ? "Correcto. Continúa la traza para observar el efecto real." : `No coincide. ${prompt.hint[2]}`;
      predictionChoices.querySelectorAll("button").forEach((choice) => { choice.disabled = true; });
    }));
    predictionHint.onclick = () => { predictionFeedback.textContent = prompt.hint[Math.min(predictionHintLevel, prompt.hint.length - 1)]; predictionHintLevel += 1; };
    return false;
  }

  function collectPayload(current) {
    const payload = {};
    current.inputs.forEach((field) => {
      const element = byId(`field-${field.name}`);
      payload[field.name] = element ? element.value : "";
    });
    return payload;
  }

  function buildSelectionKey(current, payload) {
    return `${current.name}::${JSON.stringify(payload)}`;
  }

  function hasPreparedTraceForCurrentSelection() {
    const current = operationCatalog.get(operationSelect.value);
    if (!current || !tracePlayer?.hasTrace()) return false;
    const selectionKey = buildSelectionKey(current, collectPayload(current));
    return traceSelectionKey.startsWith(`${selectionKey}::execution:`);
  }

  function requirePreparedTrace() {
    if (!isStepByStepEnabled()) {
      if (simStatus) simStatus.textContent = "Activa el modo paso a paso y ejecuta una operación para preparar una traza.";
      return false;
    }
    if (!hasPreparedTraceForCurrentSelection()) {
      if (simStatus) simStatus.textContent = "No hay una traza preparada para estos datos. Ejecuta la operación primero.";
      return false;
    }
    return true;
  }

  async function executeOperationAndLoadTrace(current, payload, selectionKey, options) {
    pendingExecution = true;
    setSimulationButtonsEnabled();
    const resetButtonLocal = byId("reset-button");
    if (resetButtonLocal) {
      resetButtonLocal.disabled = true;
    }

    try {
      updateDidacticPanel(model, current.name);
      showMessage("Ejecutando subrutina...", true);
      const response = await fetch(form.dataset.operateUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: current.name, payload }),
      });
      const data = await response.json();
      showMessage(data.message, Boolean(data.success));
      updateDidacticPanel(model, current.name);

      if (!data.success) {
        if (simStatus) simStatus.textContent = "La operación no se ejecutó; el TAD y la traza anterior permanecen sin cambios.";
        return data;
      }

      const finalOnly = Boolean(options && options.finalOnly);
      const hasExecutionTrace = Boolean(!finalOnly && data.execution_trace && tracePlayer);
      if (hasExecutionTrace) {
        lockStepUntilInput = false;
        visualTraceState.operationName = current.name;
        visualTraceState.payload = { ...payload };
        visualTraceState.frames = buildSequentialVisualFrames(
          model.id,
          model.visual_state,
          current.name,
          payload,
        );
        visualTraceState.totalSteps = Array.isArray(data.execution_trace.steps)
          ? data.execution_trace.steps.length
          : 0;
        consoleState.trace = data.execution_trace;
        consoleState.fallbackMessage = "";
        tracePlayer.loadTrace(data.execution_trace);
        traceExecutionRevision += 1;
        traceSelectionKey = `${selectionKey}::execution:${traceExecutionRevision}`;
      } else {
        visualTraceState.operationName = "";
        visualTraceState.payload = {};
        visualTraceState.frames = [];
        visualTraceState.totalSteps = 0;
        consoleState.trace = null;
        consoleState.fallbackMessage = data.message || "(sin salida printf en esta ruta)";
        refreshPrintfConsole(-1);
        if (simStatus && !finalOnly) {
          simStatus.textContent = "No hay traza paso a paso disponible para esta operacion.";
        }
        traceSelectionKey = "";
        tracePlayer?.clear(finalOnly
          ? "Modo rápido: se aplicó el resultado final de la operación."
          : "No hay una traza disponible para esta operación.");
      }

      const payloadText = summarizePayload(payload);
      const subroutine = getSubroutineName(model, current.name, current.label);
      pushUniqueHistoryEntry(
        actionHistory,
        createHistoryEntry(
          subroutine,
          payloadText || "-",
          data.message,
          current.name,
          payload,
        ),
      );
      renderActionHistory(actionHistory, historyBox, model.id, operationCatalog);
      if (data.visual_state) {
        model.visual_state = data.visual_state;
        // Executing a real operation must leave the canonical final state visible.
        // The trace is loaded for later playback; its initial snapshot is rendered
        // only when the learner explicitly prepares, replays, or navigates it.
        renderCurrentVisual(data.visual_state, {
          operation: current.name,
          payload,
          result: data.result,
          result_priority: data.result_priority,
        });
        if (simStatus && finalOnly) {
          simStatus.textContent = "Modo rápido: se aplicó el resultado final de la operación.";
        }
      }
      return data;
    } catch (_error) {
      showMessage("No fue posible completar la operacion.", false);
      return null;
    } finally {
      pendingExecution = false;
      if (resetButtonLocal) {
        resetButtonLocal.disabled = false;
      }
      setSimulationButtonsEnabled();
    }
  }

  async function executeNewOperation() {
    const current = operationCatalog.get(operationSelect.value);
    if (!current) {
      showMessage("Debes seleccionar una operacion valida.", false);
      return null;
    }
    if (!isCurrentSelectionValid()) {
      form.reportValidity?.();
      showMessage("Completa los datos requeridos antes de ejecutar.", false);
      return null;
    }
    const payload = collectPayload(current);
    const selectionKey = buildSelectionKey(current, payload);
    tracePlayer?.pause(true);
    const data = await executeOperationAndLoadTrace(current, payload, selectionKey, {
      finalOnly: !isStepByStepEnabled(),
    });
    if (!data) {
      return null;
    }
    if (data.success && simStatus && isStepByStepEnabled()) {
      simStatus.textContent = "Traza lista: pulsa «Siguiente paso» para recorrer el código instrucción por instrucción.";
    }
    return data;
  }

  async function executeOrFinishCurrentTrace() {
    const hasActiveTrace = hasPreparedTraceForCurrentSelection()
      && tracePlayer
      && tracePlayer.getCursor() >= 0
      && !tracePlayer.isAtEnd();
    if (hasActiveTrace) {
      tracePlayer.seek(tracePlayer.getTotalSteps() - 1);
      lockStepUntilInput = true;
      if (simStatus) simStatus.textContent = "Ejecución completada desde la instrucción actual.";
      setSimulationButtonsEnabled();
      return null;
    }
    return executeNewOperation();
  }

  invalidateTrace("Ejecuta una operación para crear una traza; después podrás preparar o reproducir.");

  operationSelect.addEventListener("change", () => {
    selected = operationCatalog.get(operationSelect.value) || null;
    renderOperationInputs(selected, inputsContainer);
    updateDidacticPanel(model, selected ? selected.name : "");
    invalidateTrace("Operación cambiada. Ejecuta una nueva operación para crear su traza.");
    writePresentation({ cursor: -1 });
  });

  inputsContainer.addEventListener("input", () => {
    invalidateTrace("Entradas cambiadas. Ejecuta una nueva operación para crear su traza.");
    writePresentation({ cursor: -1 });
  });

  learningLevel?.addEventListener("change", () => {
    renderSequentialPedagogyFrame(currentPedagogyFrame, learningLevel.value);
    writePresentation();
  });

  form.addEventListener("submit", async (event) => { event.preventDefault(); await executeNewOperation(); });

  simExecuteButton?.addEventListener("click", executeOrFinishCurrentTrace);

  resetButton?.addEventListener("click", async () => {
    if (!window.confirm("¿Restablecer el TAD y borrar su historial de esta sesión?")) {
      return;
    }
    const response = await fetch(form.dataset.resetUrl, { method: "POST" });
    const data = await response.json();
    showMessage(data.message, Boolean(data.success));
    updateDidacticPanel(model, selected ? selected.name : "");
    actionHistory.length = 0;
    renderActionHistory(actionHistory, historyBox, model.id, operationCatalog);
    if (data.visual_state) {
      model.visual_state = data.visual_state;
      renderCurrentVisual(data.visual_state, null);
    }
    invalidateTrace("TAD restablecido. Ejecuta una operación para crear una traza.");
    refreshPrintfConsole(-1);
  });

  simPrepareButton?.addEventListener("click", () => {
    if (!requirePreparedTrace()) return;
    tracePlayer.seek(-1);
    lockStepUntilInput = false;
    if (simStatus) simStatus.textContent = "Traza preparada. Predice o inicia la reproducción.";
    setSimulationButtonsEnabled();
  });

  simPauseButton?.addEventListener("click", () => { tracePlayer?.pause(); setSimulationButtonsEnabled(); });
  simStartButton?.addEventListener("click", () => { tracePlayer?.seek(-1); lockStepUntilInput = false; setSimulationButtonsEnabled(); });
  simEndButton?.addEventListener("click", () => {
    if (!requirePreparedTrace()) return;
    tracePlayer.seek(tracePlayer.getTotalSteps() - 1); lockStepUntilInput = true; setSimulationButtonsEnabled();
  });
  simRepeatButton?.addEventListener("click", async () => { if (!requirePreparedTrace()) return; lockStepUntilInput = false; await tracePlayer.playFromStart(); setSimulationButtonsEnabled(); });
  progressSlider?.addEventListener("input", () => { if (tracePlayer?.hasTrace()) { tracePlayer.seek(Number(progressSlider.value) - 1); lockStepUntilInput = tracePlayer.isAtEnd(); setSimulationButtonsEnabled(); } });
  predictionSkip?.addEventListener("click", () => { if (predictionPanel) predictionPanel.hidden = true; visualContainer.classList.remove("seq-practice-hidden"); });
  resetLearningButton?.addEventListener("click", () => { learningProgress = { attempts: 0, correct: 0, concepts: {} }; saveLearningProgress(); });
  practiceMode?.addEventListener("change", () => { if (!practiceMode.checked) visualContainer.classList.remove("seq-practice-hidden"); });
  const refreshComparison = () => renderSequentialComparison(compareKind?.value, compareProgress?.value, compareGrid, compareConclusion);
  compareRun?.addEventListener("click", refreshComparison);
  compareProgress?.addEventListener("input", refreshComparison);
  compareKind?.addEventListener("change", () => { if (compareProgress) compareProgress.value = "0"; refreshComparison(); });
  exportImageButton?.addEventListener("click", async () => {
    try { const exported = await window.InterpreterRuntime.exportVisualStateAsJpg({ target: visualContainer, quality: 0.9, scale: 1 }); const link = document.createElement("a"); link.href = exported.dataUrl; link.download = exported.suggestedName; link.click(); }
    catch (error) { showMessage(error.message || "No se pudo exportar la captura.", false); }
  });
  exportSummaryButton?.addEventListener("click", () => {
    const current = operationCatalog.get(operationSelect.value);
    const summary = { schema: "sequential-learning-summary/v1", structure: model.id, operation: operationSelect.value, payload: current ? collectPayload(current) : {}, level: learningLevel?.value, cursor: tracePlayer?.getCursor() ?? -1, total_steps: tracePlayer?.getTotalSteps() ?? 0, frame: currentPedagogyFrame, state: model.visual_state, practice: learningProgress, comparison: compareKind?.value };
    const url = URL.createObjectURL(new Blob([JSON.stringify(summary, null, 2)], { type: "application/json" })); const link = document.createElement("a"); link.href = url; link.download = `${model.id}-resumen.json`; link.click(); URL.revokeObjectURL(url);
  });
  document.addEventListener("keydown", async (event) => {
    if (!event.altKey || event.ctrlKey || event.metaKey || ["INPUT", "SELECT", "TEXTAREA"].includes(event.target?.tagName)) return;
    const key = event.key.toLowerCase();
    if (key === "arrowright") { event.preventDefault(); simStepButton?.click(); }
    else if (key === "arrowleft") { event.preventDefault(); tracePlayer?.prev(); }
    else if (key === "home") { event.preventDefault(); tracePlayer?.seek(-1); }
    else if (key === "end") { event.preventDefault(); if (tracePlayer?.hasTrace()) tracePlayer.seek(tracePlayer.getTotalSteps() - 1); }
    else if (key === "p") { event.preventDefault(); tracePlayer?.pause(); }
    else if (key === "r") { event.preventDefault(); if (tracePlayer?.hasTrace()) await tracePlayer.playFromStart(); }
    setSimulationButtonsEnabled();
  });

  simPlayButton?.addEventListener("click", async () => {
    if (!requirePreparedTrace()) return;
    await tracePlayer.playFromStart();
  });

  simPrevButton?.addEventListener("click", () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    const moved = tracePlayer?.prev();
    if (moved) {
      lockStepUntilInput = false;
    }
    setSimulationButtonsEnabled();
  });

  simStepButton?.addEventListener("click", async () => {
    if (!requirePreparedTrace()) return;
    const nextIndex = tracePlayer.getCursor() + 1;
    const nextStep = consoleState.trace?.steps?.[nextIndex];
    if (requestPrediction(nextStep, nextIndex)) { setSimulationButtonsEnabled(); return; }
    const advanced = await tracePlayer.step();
    if (advanced && tracePlayer.isAtEnd()) {
      lockStepUntilInput = true;
      setSimulationButtonsEnabled();
    }
  });

  stepToggle?.addEventListener("change", () => {
    invalidateTrace(
      isStepByStepEnabled()
        ? "Modo paso a paso activado. Ejecuta una operación para crear una traza."
        : "Modo rápido activado. Ejecutar operación aplicará solo el resultado final.",
    );
  });

}

document.addEventListener("DOMContentLoaded", () => {
  if (window.SEQ_VIEW_MODEL) {
    initStructurePage(window.SEQ_VIEW_MODEL);
  }
});
