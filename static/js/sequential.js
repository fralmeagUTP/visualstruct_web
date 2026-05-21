"use strict";

function byId(id) {
  return document.getElementById(id);
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
  if (nodes.length < 2) {
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
  if (circular && items.length > 1) {
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
    if (baseItems.length) {
      frames.push(makePriorityQueueFrame(currentState, baseItems, { activeIndices: [0] }));
    } else {
      frames.push(makePriorityQueueFrame(currentState, baseItems, {}));
    }
    const nextItems = [...baseItems, { value, priority }];
    frames.push(makePriorityQueueFrame(currentState, nextItems, {
      activeIndices: [nextItems.length - 1],
      pendingIndices: [nextItems.length - 1],
    }));
    frames.push(makePriorityQueueFrame(currentState, nextItems, {
      activeIndices: [0],
      visitedIndices: nextItems.map((_, index) => index).slice(1),
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
    const remaining = baseItems.filter((_, idx) => idx !== minIndex);
    frames.push(makePriorityQueueFrame(currentState, remaining, {}));
    return frames;
  }

  if (operationName === "frente" && baseItems.length) {
    frames.push(makePriorityQueueFrame(currentState, baseItems, { activeIndices: [0] }));
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
  html += '<div class="viz-row-label front">FRONT</div><div class="viz-row">';
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
  html += '</div><div class="viz-row-tail"><span class="viz-row-label back">BACK</span></div>';
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
    inner += renderStack(state, hint);
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
  const simPlayButton = byId("seq-sim-play");
  const simPrevButton = byId("seq-sim-prev");
  const simStepButton = byId("seq-sim-step");
  const simStatus = byId("seq-sim-status");
  const stepToggle = byId("seq-step-toggle");
  const speedSlider = byId("seq-speed-slider");
  const speedValue = byId("seq-speed-value");
  const printfConsole = byId("seq-printf-console");

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
  function collectPrintfConsoleLines(trace, cursor) {
    if (!trace || !Array.isArray(trace.steps) || cursor < 0) {
      return [];
    }
    const limit = Math.min(cursor, trace.steps.length - 1);
    const out = [];
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const rawMessages = extractPrintfMessagesFromLine(step.line_text);
      rawMessages.forEach((msg) => {
        // Evita ruido visual de formatos printf no resueltos (ej. "%d", "%s").
        if (hasPrintfFormatSpecifier(msg)) {
          return;
        }
        pushUniqueConsoleLine(out, `[printf] ${msg}`);
      });
    }
    // Refleja el printf del main al finalizar la simulacion de la operacion.
    if (limit >= trace.steps.length - 1) {
      const finalMessage = String(trace.message || "").trim();
      if (finalMessage) {
        pushUniqueConsoleLine(out, `[printf] ${finalMessage}`);
      }
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
        const hasFrames = Array.isArray(visualTraceState.frames) && visualTraceState.frames.length > 0;
        if (hasFrames && stepMeta && Number.isInteger(stepMeta.step_index)) {
          const frameIndex = resolveFrameIndexForStep(
            model.id,
            visualTraceState.operationName,
            stepMeta.step_index,
            visualTraceState.totalSteps || 0,
            visualTraceState.frames,
            { lineText: stepMeta.line_text || "" },
          );
          if (frameIndex >= 0 && frameIndex < visualTraceState.frames.length) {
            const frame = visualTraceState.frames[frameIndex];
            renderVisualState(model.id, frame.state, visualContainer, {
              operation: visualTraceState.operationName,
              simulation: frame.simulation,
            });
            return;
          }
        }
        renderVisualState(model.id, stateSnapshot, visualContainer, null);
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        traceCursor = cursor;
        traceTotalSteps = event && event.trace && Array.isArray(event.trace.steps)
          ? event.trace.steps.length
          : 0;
        refreshPrintfConsole(cursor);
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

  visibleOperations.forEach((operation) => {
    const option = document.createElement("option");
    option.value = operation.name;
    option.textContent = operation.label;
    operationSelect.appendChild(option);
  });
  operationSelect.disabled = visibleOperations.length === 0;
  if (selected) {
    operationSelect.value = selected.name;
  }

  renderOperationInputs(selected, inputsContainer);
  updateDidacticPanel(model, selected ? selected.name : "");
  renderVisualState(model.id, model.visual_state, visualContainer, null);

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

  let pendingExecution = false;
  let traceSelectionKey = "";
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
    if (simPlayButton) {
      simPlayButton.disabled = busy || !canExecute;
    }
    if (simPrevButton) {
      simPrevButton.disabled = busy || !stepMode || !hasProgress;
    }
    if (simStepButton) {
      simStepButton.disabled = busy || !stepMode || !canExecute || (hasTrace && atEnd) || lockStepUntilInput;
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
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
    refreshPrintfConsole(-1);
    setSimulationButtonsEnabled();
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
        traceSelectionKey = selectionKey;
      } else {
        visualTraceState.operationName = "";
        visualTraceState.payload = {};
        visualTraceState.frames = [];
        visualTraceState.totalSteps = 0;
        consoleState.trace = null;
        consoleState.fallbackMessage = data.message || "(sin salida printf en esta ruta)";
        refreshPrintfConsole(-1);
        const allowFallbackPlayback = !(options && options.allowFallbackPlayback === false) && !finalOnly;
        if (allowFallbackPlayback) {
          const visualFrames = buildSequentialVisualFrames(
            model.id,
            model.visual_state,
            current.name,
            payload,
          );
          await simulateDidacticExecution({
            operation: current.name,
            payload,
            sizeBefore: Number(model?.visual_state?.size || 0),
            playbackSpeed,
            onStep: (stepIndex, totalSteps, stepMeta) => {
              if (!visualFrames.length) {
                return;
              }
              const frameIndex = resolveFrameIndexForStep(
                model.id,
                current.name,
                stepIndex,
                totalSteps,
                visualFrames,
                stepMeta,
              );
              if (frameIndex < 0) {
                return;
              }
              const frame = visualFrames[frameIndex];
              renderVisualState(model.id, frame.state, visualContainer, {
                operation: current.name,
                simulation: frame.simulation,
              });
            },
          });
        } else if (simStatus) {
          simStatus.textContent = "No hay traza paso a paso disponible para esta operacion.";
        }
        traceSelectionKey = "";
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
        if (!hasExecutionTrace) {
          renderVisualState(model.id, data.visual_state, visualContainer, {
            operation: current.name,
            payload,
            result: data.result,
            result_priority: data.result_priority,
          });
          if (simStatus && finalOnly) {
            simStatus.textContent = "Modo rapido: se aplico el resultado final de la operacion.";
          }
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

  async function ensureTraceForCurrentSelection(options) {
    const current = operationCatalog.get(operationSelect.value);
    if (!current) {
      showMessage("Debes seleccionar una operacion valida.", false);
      return null;
    }
    const payload = collectPayload(current);
    const selectionKey = buildSelectionKey(current, payload);
    if (tracePlayer && tracePlayer.hasTrace() && traceSelectionKey === selectionKey) {
      return { current, payload, selectionKey };
    }

    const data = await executeOperationAndLoadTrace(current, payload, selectionKey, options);
    if (!data) {
      return null;
    }
    return { current, payload, selectionKey };
  }

  invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");

  operationSelect.addEventListener("change", () => {
    selected = operationCatalog.get(operationSelect.value) || null;
    renderOperationInputs(selected, inputsContainer);
    updateDidacticPanel(model, selected ? selected.name : "");
    invalidateTrace("Operacion cambiada. Ejecuta nuevamente.");
  });

  inputsContainer.addEventListener("input", () => {
    invalidateTrace("Entradas cambiadas. Ejecuta nuevamente.");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!isStepByStepEnabled()) {
      const current = operationCatalog.get(operationSelect.value);
      if (!current) {
        return;
      }
      const payload = collectPayload(current);
      const selectionKey = buildSelectionKey(current, payload);
      await executeOperationAndLoadTrace(current, payload, selectionKey, {
        finalOnly: true,
        allowFallbackPlayback: false,
      });
      return;
    }
    const ready = await ensureTraceForCurrentSelection({ allowFallbackPlayback: true });
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.playFromStart();
  });

  resetButton?.addEventListener("click", async () => {
    const response = await fetch(form.dataset.resetUrl, { method: "POST" });
    const data = await response.json();
    showMessage(data.message, Boolean(data.success));
    updateDidacticPanel(model, selected ? selected.name : "");
    actionHistory.length = 0;
    renderActionHistory(actionHistory, historyBox, model.id, operationCatalog);
    if (data.visual_state) {
      model.visual_state = data.visual_state;
      renderVisualState(model.id, data.visual_state, visualContainer, null);
    }
    invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
    refreshPrintfConsole(-1);
  });

  simPlayButton?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      const current = operationCatalog.get(operationSelect.value);
      if (!current) {
        return;
      }
      const payload = collectPayload(current);
      const selectionKey = buildSelectionKey(current, payload);
      await executeOperationAndLoadTrace(current, payload, selectionKey, {
        finalOnly: true,
        allowFallbackPlayback: false,
      });
      return;
    }
    const ready = await ensureTraceForCurrentSelection({ allowFallbackPlayback: true });
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
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
    if (!isStepByStepEnabled()) {
      return;
    }
    const ready = await ensureTraceForCurrentSelection({ allowFallbackPlayback: false });
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    const advanced = await tracePlayer.step();
    if (advanced && tracePlayer.isAtEnd()) {
      lockStepUntilInput = true;
      setSimulationButtonsEnabled();
    }
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
  if (window.SEQ_VIEW_MODEL) {
    initStructurePage(window.SEQ_VIEW_MODEL);
  }
});
