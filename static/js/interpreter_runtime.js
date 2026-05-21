"use strict";

(function bootstrapInterpreterRuntime(globalScope) {
  const DIDACTIC_MODE_STORAGE_KEY = "didactic-mode";
  const DIDACTIC_MODE_VISUAL = "visual";
  const DIDACTIC_MODE_FULL = "full";

  function normalizeDidacticMode(rawMode) {
    return rawMode === DIDACTIC_MODE_FULL ? DIDACTIC_MODE_FULL : DIDACTIC_MODE_VISUAL;
  }

  function readDidacticMode() {
    try {
      return normalizeDidacticMode(window.localStorage.getItem(DIDACTIC_MODE_STORAGE_KEY));
    } catch (error) {
      return DIDACTIC_MODE_VISUAL;
    }
  }

  function persistDidacticMode(mode) {
    try {
      window.localStorage.setItem(DIDACTIC_MODE_STORAGE_KEY, normalizeDidacticMode(mode));
    } catch (error) {
      // Ignore localStorage failures (private mode or blocked storage).
    }
  }

  function applyDidacticMode(mode) {
    const nextMode = normalizeDidacticMode(mode);
    document.documentElement.setAttribute("data-didactic-mode", nextMode);
    const modeSwitch = document.getElementById("didactic-mode-switch");
    if (modeSwitch instanceof HTMLInputElement) {
      modeSwitch.checked = nextMode === DIDACTIC_MODE_FULL;
    }
    return nextMode;
  }

  function initDidacticModeSwitch() {
    const modeSwitch = document.getElementById("didactic-mode-switch");
    const mode = applyDidacticMode(readDidacticMode());
    persistDidacticMode(mode);
    if (!(modeSwitch instanceof HTMLInputElement)) {
      return;
    }
    modeSwitch.addEventListener("change", () => {
      const nextMode = modeSwitch.checked ? DIDACTIC_MODE_FULL : DIDACTIC_MODE_VISUAL;
      applyDidacticMode(nextMode);
      persistDidacticMode(nextMode);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDidacticModeSwitch, { once: true });
  } else {
    initDidacticModeSwitch();
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function sleep(ms) {
    return new Promise((resolve) => {
      window.setTimeout(resolve, ms);
    });
  }

  function ensureCodeLines(codeElement) {
    if (!codeElement) {
      return [];
    }
    let lines = Array.from(codeElement.querySelectorAll(".code-line"));
    if (lines.length) {
      return lines;
    }

    const raw = codeElement.dataset.rawCode || codeElement.textContent || "";
    const rows = String(raw).replaceAll("\r\n", "\n").split("\n");
    codeElement.innerHTML = rows
      .map((line, index) => `<span class="code-line" data-line="${index}">${escapeHtml(line) || "&nbsp;"}</span>`)
      .join("");
    lines = Array.from(codeElement.querySelectorAll(".code-line"));
    return lines;
  }

  function clearLineClasses(lines) {
    lines.forEach((line) => {
      line.classList.remove("sim-active");
      line.classList.remove("sim-done");
      line.classList.remove("sim-skip");
    });
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

  function renderCode(codeElement, sourceCode, codeTitle) {
    if (!codeElement) {
      return;
    }
    const raw = String(sourceCode || "");
    codeElement.dataset.rawCode = raw;
    codeElement.dataset.codeTitle = String(codeTitle || "");
    const rows = raw.replaceAll("\r\n", "\n").split("\n");
    if (String(codeTitle || "").toLowerCase().includes("codigo c")) {
      let state = { inBlockComment: false };
      codeElement.innerHTML = rows
        .map((line, index) => {
          const highlighted = highlightCLine(line, state);
          state = highlighted.state;
          return `<span class="code-line" data-line="${index}">${highlighted.html || "&nbsp;"}</span>`;
        })
        .join("");
      return;
    }
    codeElement.innerHTML = rows
      .map((line, index) => `<span class="code-line" data-line="${index}">${escapeHtml(line) || "&nbsp;"}</span>`)
      .join("");
  }

    function setStatus(statusElement, text) {
      if (!statusElement) {
        return;
      }
      statusElement.textContent = text || "";
    }

    function stepStatusText(step, currentIndex, totalSteps) {
      let status = `Paso ${currentIndex}/${totalSteps}`;
      const debug = step && typeof step.debug === "object" ? step.debug : null;
      if (!debug) {
        return status;
      }
      const stage = String(debug.stage || "").trim();
      const note = String(debug.note || "").trim();
      if (stage && note) {
        return `${status} - ${stage}: ${note}`;
      }
      if (stage) {
        return `${status} - ${stage}`;
      }
      if (note) {
        return `${status} - ${note}`;
      }
      return status;
    }

  function createTracePlayer(options) {
    const codeElement = options ? options.codeElement : null;
    const renderState = options ? options.renderState : null;
    const statusElement = options ? options.statusElement : null;
    const counterElement = options ? options.counterElement : null;
    const onCursorChange = options ? options.onCursorChange : null;
    const defaultDelayMs = options && Number.isFinite(options.defaultDelayMs)
      ? Number(options.defaultDelayMs)
      : 170;
    const retainDoneLines = Boolean(options && options.retainDoneLines);

    let trace = null;
    let lines = [];
    let cursor = -1;
    let playing = false;
    let playToken = 0;
    let speedMultiplier = 1;

    function normalizeSpeed(raw) {
      const parsed = Number(raw);
      if (!Number.isFinite(parsed)) {
        return 1;
      }
      return Math.min(4, Math.max(0.25, parsed));
    }

    function emitCursorChange(reason, step) {
      if (typeof onCursorChange !== "function") {
        return;
      }
      onCursorChange({
        reason: reason || "",
        trace,
        cursor,
        step: step || null,
      });
    }

    function setCounter(current, total) {
      if (!counterElement) {
        return;
      }
      const safeCurrent = Math.max(0, Number.isFinite(current) ? Number(current) : 0);
      const safeTotal = Math.max(0, Number.isFinite(total) ? Number(total) : 0);
      counterElement.textContent = `Paso: ${safeCurrent}/${safeTotal}`;
    }

    function resetVisualLines() {
      lines = ensureCodeLines(codeElement);
      clearLineClasses(lines);
    }

    function applyStateSnapshot(step) {
      if (typeof renderState === "function" && step && step.state_snapshot) {
        renderState(step.state_snapshot, step);
      }
    }

    function applyStateAfter(step) {
      if (typeof renderState === "function" && step && step.state_after) {
        renderState(step.state_after, step);
      }
    }

    function markPreviousAsDone(previousIndex) {
      if (!retainDoneLines) {
        return;
      }
      if (previousIndex < 0 || previousIndex >= (trace?.steps?.length || 0)) {
        return;
      }
      const prev = trace.steps[previousIndex] || {};
      const prevLineIndex = Number.isInteger(prev.line_index) ? prev.line_index : -1;
      const previousLine = prevLineIndex >= 0 ? lines[prevLineIndex] : null;
      if (previousLine) {
        previousLine.classList.remove("sim-active");
        previousLine.classList.add("sim-done");
      }
    }

    function activateCurrentLine(step) {
      const lineIndex = Number.isInteger(step.line_index) ? step.line_index : -1;
      lines.forEach((line) => {
        line.classList.remove("sim-active");
        if (!retainDoneLines) {
          line.classList.remove("sim-done");
        }
      });
      const currentLine = lineIndex >= 0 ? lines[lineIndex] : null;
      if (!currentLine) {
        return;
      }
      currentLine.classList.add("sim-active");
      currentLine.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }

    function finalizeLastLineIfNeeded() {
      if (!retainDoneLines) {
        return;
      }
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length || cursor < 0) {
        return;
      }
      const current = trace.steps[cursor] || {};
      const lineIndex = Number.isInteger(current.line_index) ? current.line_index : -1;
      const line = lineIndex >= 0 ? lines[lineIndex] : null;
      if (!line) {
        return;
      }
      line.classList.remove("sim-active");
      line.classList.add("sim-done");
    }

    function paintDoneLinesTo(indexInclusive) {
      if (!retainDoneLines || !trace || !Array.isArray(trace.steps)) {
        return;
      }
      for (let idx = 0; idx <= indexInclusive; idx += 1) {
        const step = trace.steps[idx] || {};
        const lineIndex = Number.isInteger(step.line_index) ? step.line_index : -1;
        const doneLine = lineIndex >= 0 ? lines[lineIndex] : null;
        if (doneLine) {
          doneLine.classList.add("sim-done");
        }
      }
    }

    async function _advanceOne(withDelay, token) {
      if (!trace || !Array.isArray(trace.steps) || cursor >= trace.steps.length - 1) {
        return false;
      }

      const previousIndex = cursor;
      const nextIndex = cursor + 1;
      const step = trace.steps[nextIndex] || {};
      markPreviousAsDone(previousIndex);
      activateCurrentLine(step);

      if (withDelay) {
        const delay = Number.isFinite(step.delay_ms) ? Number(step.delay_ms) : defaultDelayMs;
        const scaledDelay = Math.round(delay / speedMultiplier);
        await sleep(Math.max(12, scaledDelay));
        if (token !== playToken) {
          return false;
        }
      }
      applyStateAfter(step);
      cursor = nextIndex;
      setCounter(cursor + 1, trace.steps.length);
      setStatus(statusElement, stepStatusText(step, cursor + 1, trace.steps.length));

      if (cursor >= trace.steps.length - 1) {
        finalizeLastLineIfNeeded();
      }
      emitCursorChange("advance", step);
      return true;
    }

    async function _playLoop(fromStart) {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para reproducir.");
        return;
      }
      if (fromStart) {
        reset();
      }
      if (cursor >= trace.steps.length - 1) {
        reset();
      }
      playing = true;
      const token = ++playToken;

      while (playing && token === playToken && cursor < trace.steps.length - 1) {
        const advanced = await _advanceOne(true, token);
        if (!advanced) {
          break;
        }
      }
      if (token !== playToken) {
        return;
      }
      if (cursor >= trace.steps.length - 1) {
        playing = false;
        setStatus(statusElement, `Simulacion completada (${trace.steps.length} pasos).`);
      }
    }

    function loadTrace(newTrace) {
      trace = newTrace && Array.isArray(newTrace.steps) ? newTrace : null;
      playing = false;
      playToken += 1;

      if (!trace || !codeElement) {
        setCounter(0, 0);
        setStatus(statusElement, "No hay traza cargada.");
        return;
      }
      if (trace.source_code) {
        renderCode(codeElement, trace.source_code, trace.code_title || "");
      }
      resetVisualLines();
      cursor = -1;
      const firstStep = trace.steps[0] || null;
      if (firstStep) {
        applyStateSnapshot(firstStep);
      }
      setCounter(0, trace.steps.length);
      setStatus(statusElement, `Simulacion lista: ${trace.steps.length} pasos.`);
      emitCursorChange("load", firstStep);
    }

    function clear(message) {
      pause();
      trace = null;
      cursor = -1;
      if (codeElement) {
        const clearLines = ensureCodeLines(codeElement);
        clearLineClasses(clearLines);
      }
      setCounter(0, 0);
      setStatus(statusElement, message || "Ejecuta una operacion para generar la simulacion.");
      emitCursorChange("clear", null);
    }

    function pause(silent) {
      if (!trace) {
        return;
      }
      playing = false;
      playToken += 1;
      if (!silent) {
        setStatus(statusElement, "Simulacion pausada.");
      }
    }

    function reset() {
      if (!trace) {
        return;
      }
      pause();
      resetVisualLines();
      cursor = -1;
      const firstStep = trace.steps[0] || null;
      if (firstStep) {
        applyStateSnapshot(firstStep);
      }
      setCounter(0, trace.steps.length);
      setStatus(statusElement, `Simulacion reiniciada (${trace.steps.length} pasos).`);
      emitCursorChange("reset", firstStep);
    }

    async function step() {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para avanzar.");
        return false;
      }
      pause(true);
      if (cursor >= trace.steps.length - 1) {
        setStatus(statusElement, "Simulacion completada. Ingresa nuevos datos para continuar.");
        return false;
      }
      return _advanceOne(false, playToken);
    }

    function prev() {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para retroceder.");
        return false;
      }
      pause(true);
      if (cursor < 0) {
        setStatus(statusElement, "Ya estas en el inicio de la simulacion.");
        return false;
      }
      if (cursor === 0) {
        resetVisualLines();
        cursor = -1;
        const firstStep = trace.steps[0] || null;
        if (firstStep) {
          applyStateSnapshot(firstStep);
        }
        setCounter(0, trace.steps.length);
        setStatus(statusElement, `Paso 0/${trace.steps.length}`);
        emitCursorChange("prev_to_start", firstStep);
        return true;
      }

      const previousIndex = cursor - 1;
      const previousStep = trace.steps[previousIndex] || {};
      resetVisualLines();
      paintDoneLinesTo(previousIndex - 1);
      activateCurrentLine(previousStep);
      applyStateAfter(previousStep);
      cursor = previousIndex;
      setCounter(cursor + 1, trace.steps.length);
      setStatus(statusElement, stepStatusText(previousStep, cursor + 1, trace.steps.length));
      emitCursorChange("prev", previousStep);
      return true;
    }

    function hasTrace() {
      return Boolean(trace && Array.isArray(trace.steps) && trace.steps.length);
    }

    function setSpeed(multiplier) {
      speedMultiplier = normalizeSpeed(multiplier);
    }

    function getSpeed() {
      return speedMultiplier;
    }

    function getCursor() {
      return cursor;
    }

    function getTotalSteps() {
      return trace && Array.isArray(trace.steps) ? trace.steps.length : 0;
    }

    function isAtEnd() {
      const total = getTotalSteps();
      return total > 0 && cursor >= total - 1;
    }

    return {
      loadTrace,
      clear,
      pause,
      play: () => _playLoop(false),
      playFromStart: () => _playLoop(true),
      step,
      prev,
      reset,
      hasTrace,
      setSpeed,
      getSpeed,
      getCursor,
      getTotalSteps,
      isAtEnd,
    };
  }

  async function playExecutionTrace(options) {
    const trace = options && options.trace ? options.trace : null;
    const codeElement = options ? options.codeElement : null;
    const renderState = options ? options.renderState : null;
    if (!trace || !codeElement) {
      return;
    }
    const player = createTracePlayer({
      codeElement,
      renderState,
      statusElement: options ? options.statusElement : null,
      defaultDelayMs: options ? options.defaultDelayMs : null,
    });
    player.loadTrace(trace);
    await player.playFromStart();
  }

  globalScope.InterpreterRuntime = {
    ensureCodeLines,
    renderCode,
    createTracePlayer,
    playExecutionTrace,
  };
}(window));
