"use strict";

(function bootstrapInterpreterRuntime(globalScope) {
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

  function renderCode(codeElement, sourceCode, codeTitle) {
    if (!codeElement) {
      return;
    }
    const raw = String(sourceCode || "");
    codeElement.dataset.rawCode = raw;
    codeElement.dataset.codeTitle = String(codeTitle || "");
    const rows = raw.replaceAll("\r\n", "\n").split("\n");
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
    const defaultDelayMs = options && Number.isFinite(options.defaultDelayMs)
      ? Number(options.defaultDelayMs)
      : 170;
    const retainDoneLines = Boolean(options && options.retainDoneLines);

    let trace = null;
    let lines = [];
    let cursor = -1;
    let playing = false;
    let playToken = 0;

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
        await sleep(Math.max(20, delay));
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
    }

    async function step() {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para avanzar.");
        return false;
      }
      pause(true);
      if (cursor >= trace.steps.length - 1) {
        resetVisualLines();
        cursor = -1;
        const firstStep = trace.steps[0] || null;
        if (firstStep) {
          applyStateSnapshot(firstStep);
        }
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
      return true;
    }

    function hasTrace() {
      return Boolean(trace && Array.isArray(trace.steps) && trace.steps.length);
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
