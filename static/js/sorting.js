"use strict";

function sById(id) {
  return document.getElementById(id);
}

function sEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function sNormalizeDidacticText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function sPushUniqueConsoleLine(lines, line) {
  const normalized = sNormalizeDidacticText(line);
  if (!normalized) {
    return;
  }
  if (lines.length && sNormalizeDidacticText(lines[lines.length - 1]) === normalized) {
    return;
  }
  lines.push(line);
}

function sBuildHistoryEntrySignature(entry) {
  if (!entry || typeof entry !== "object") {
    return "";
  }
  const title = sNormalizeDidacticText(entry.title);
  const message = sNormalizeDidacticText(entry.message);
  return `${title}|${message}`;
}

function sPushUniqueHistoryEntry(history, entry) {
  if (!Array.isArray(history) || !entry) {
    return false;
  }
  const last = history.length ? history[history.length - 1] : null;
  if (sBuildHistoryEntrySignature(last) === sBuildHistoryEntrySignature(entry)) {
    return false;
  }
  history.push(entry);
  return true;
}

function renderSortingVisualState(state, container) {
  if (!container || !state) {
    return;
  }
  const items = Array.isArray(state.items) ? state.items : [];
  if (!items.length) {
    container.innerHTML = '<p class="muted">Arreglo vacio. Crea o genera datos para iniciar.</p>';
    return;
  }
  const comparing = new Set((state.comparing_indices || []).map((x) => Number(x)));
  const swapping = new Set((state.swapping_indices || []).map((x) => Number(x)));
  const sorted = new Set((state.sorted_indices || []).map((x) => Number(x)));
  const activeRange = Array.isArray(state.active_range) ? state.active_range : null;
  const pivot = Number.isInteger(state.pivot_index) ? Number(state.pivot_index) : null;
  const maxAbs = Math.max(...items.map((value) => Math.abs(Number(value) || 0)), 1);

  const bars = items
    .map((value, index) => {
      const numeric = Number(value) || 0;
      const width = Math.max(8, Math.round((Math.abs(numeric) / maxAbs) * 100));
      const classes = ["sorting-item"];
      if (comparing.has(index)) classes.push("is-comparing");
      if (swapping.has(index)) classes.push("is-swapping");
      if (sorted.has(index)) classes.push("is-sorted");
      if (pivot === index) classes.push("is-pivot");
      if (activeRange && (index < activeRange[0] || index > activeRange[1])) classes.push("is-out-range");
      return `
        <div class="${classes.join(" ")}">
          <div class="sorting-item-label">[${index}] ${sEscape(value)}</div>
          <div class="sorting-item-bar" style="width:${width}%"></div>
        </div>
      `;
    })
    .join("");

  const aux = Array.isArray(state.auxiliary_array)
    ? `
      <div class="sorting-aux">
        <h5>Arreglo auxiliar</h5>
        <div class="sorting-aux-items">${state.auxiliary_array.map((value) => `<span>${sEscape(value)}</span>`).join("")}</div>
      </div>
    `
    : "";

  const metrics = state.metrics || {};
  const metricsHtml = `
    <div class="sorting-metrics">
      <span>Comparaciones: <strong>${metrics.comparisons || 0}</strong></span>
      <span>Intercambios: <strong>${metrics.swaps || 0}</strong></span>
      <span>Movimientos: <strong>${metrics.moves || 0}</strong></span>
      <span>Pasos: <strong>${metrics.steps || 0}</strong></span>
    </div>
  `;

  container.innerHTML = `<div class="sorting-items">${bars}</div>${aux}${metricsHtml}`;
}

function renderSortingHistory(entries, container) {
  if (!container) {
    return;
  }
  if (!entries.length) {
    container.innerHTML = "<li>Sin acciones ejecutadas.</li>";
    return;
  }
  container.innerHTML = entries
    .map((entry) => `<li><strong>${sEscape(entry.title)}</strong>: ${sEscape(entry.message)}</li>`)
    .join("");
}

function renderSortingConsole(consoleEl, lines) {
  if (!consoleEl) {
    return;
  }
  if (!lines.length) {
    consoleEl.innerHTML = '<div class="console-line muted">(sin salida printf en esta ruta)</div>';
    return;
  }
  consoleEl.innerHTML = lines.map((line) => `<div class="console-line">${sEscape(line)}</div>`).join("");
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function speedSettingToMultiplier(setting) {
  return Math.pow(2, setting);
}

function initSortingPage(model) {
  const controls = sById("sorting-controls");
  if (!controls) {
    return;
  }

  const createUrl = controls.dataset.createUrl;
  const randomUrl = controls.dataset.randomUrl;
  const algorithmUrl = controls.dataset.algorithmUrl;
  const runUrl = controls.dataset.runUrl;
  const resetUrl = controls.dataset.resetUrl;

  const manualInput = sById("sorting-manual-values");
  const randomSize = sById("sorting-random-size");
  const randomMin = sById("sorting-random-min");
  const randomMax = sById("sorting-random-max");
  const algorithmSelect = sById("sorting-algorithm");
  const messageBox = sById("sorting-message-box");
  const visualContainer = sById("sorting-visual-state");
  const codeTitle = sById("sorting-code-title");
  const codePanel = sById("sorting-code");
  const historyBox = sById("sorting-action-history");
  const consoleBox = sById("sorting-printf-console");
  const status = sById("sorting-sim-status");
  const counter = sById("sorting-sim-counter");
  const stepToggle = sById("sorting-step-toggle");
  const playButton = sById("sorting-sim-play");
  const stepButton = sById("sorting-sim-step");
  const prevButton = sById("sorting-sim-prev");
  const speedSlider = sById("sorting-speed-slider");
  const speedValue = sById("sorting-speed-value");

  const createButton = sById("sorting-create-array");
  const randomButton = sById("sorting-random-array");
  const resetButton = sById("sorting-reset");

  let trace = null;
  let history = [];
  let consoleLines = [];
  let speedSetting = 0;
  let speedMultiplier = 1;

  const didacticOps = (model.didactic && model.didactic.operations) || {};

  function isStepByStepEnabled() {
    return !stepToggle || Boolean(stepToggle.checked);
  }

  function setMessage(text, success) {
    if (!messageBox) {
      return;
    }
    messageBox.textContent = text || "";
    messageBox.className = success ? "message success" : "message error";
  }

  function updateCodeByAlgorithm() {
    const algorithmId = algorithmSelect ? algorithmSelect.value : "";
    const current = (model.algorithms || []).find((item) => item.id === algorithmId);
    const label = current ? current.label : algorithmId;
    if (codeTitle) {
      codeTitle.textContent = `Codigo C: ${label}`;
    }
    const code = didacticOps[algorithmId] || model.didactic.default_operation || "Contenido no disponible.";
    if (window.InterpreterRuntime && codePanel) {
      window.InterpreterRuntime.renderCode(codePanel, code, "Codigo C");
    } else if (codePanel) {
      codePanel.textContent = code;
    }
  }

  function buildConsoleFromTrace(stepIndex) {
    if (!trace || !Array.isArray(trace.steps) || stepIndex < 0) {
      return [];
    }
    const lines = [];
    for (let idx = 0; idx <= Math.min(stepIndex, trace.steps.length - 1); idx += 1) {
      const step = trace.steps[idx] || {};
      const debug = step.debug && step.debug.note ? step.debug.note : step.line_text;
      if (debug && String(debug).trim()) {
        sPushUniqueConsoleLine(lines, `[printf] ${String(debug).trim()}`);
      }
    }
    return lines.slice(-8);
  }

  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: codePanel,
      renderState: (state) => renderSortingVisualState(state, visualContainer),
      statusElement: status,
      counterElement: counter,
      retainDoneLines: true,
      onCursorChange: ({ cursor }) => {
        consoleLines = buildConsoleFromTrace(cursor);
        renderSortingConsole(consoleBox, consoleLines);
      },
    })
    : null;

  function setButtonsState() {
    const stepMode = isStepByStepEnabled();
    if (speedSlider) {
      speedSlider.disabled = !stepMode;
    }
    if (prevButton) {
      prevButton.disabled = !stepMode || !tracePlayer || tracePlayer.getCursor() < 0;
    }
    if (stepButton) {
      const atEnd = tracePlayer && tracePlayer.isAtEnd();
      stepButton.disabled = !stepMode || !tracePlayer || !tracePlayer.hasTrace() || atEnd;
    }
  }

  function setSpeed(value) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
      return;
    }
    speedSetting = Math.max(-2, Math.min(2, parsed));
    speedMultiplier = speedSettingToMultiplier(speedSetting);
    if (speedValue) {
      const sign = speedSetting >= 0 ? "+" : "";
      speedValue.textContent = `${sign}${speedSetting.toFixed(2)}x (${speedMultiplier.toFixed(2)}x real)`;
    }
    tracePlayer?.setSpeed(speedMultiplier);
  }

  async function postJson(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
    });
    return response.json();
  }

  async function createArray() {
    const data = await postJson(createUrl, { values: manualInput ? manualInput.value : "" });
    setMessage(data.message, Boolean(data.success));
    if (data.success) {
      model.visual_state = data.visual_state;
      renderSortingVisualState(model.visual_state, visualContainer);
      sPushUniqueHistoryEntry(history, { title: "Crear arreglo", message: data.message });
      renderSortingHistory(history, historyBox);
      tracePlayer?.clear("Arreglo creado. Ejecuta Reproducir.");
      renderSortingConsole(consoleBox, []);
    }
  }

  async function randomArray() {
    const data = await postJson(randomUrl, {
      size: randomSize ? randomSize.value : "",
      min_value: randomMin ? randomMin.value : "",
      max_value: randomMax ? randomMax.value : "",
    });
    setMessage(data.message, Boolean(data.success));
    if (data.success) {
      model.visual_state = data.visual_state;
      renderSortingVisualState(model.visual_state, visualContainer);
      sPushUniqueHistoryEntry(history, { title: "Generar aleatorio", message: data.message });
      renderSortingHistory(history, historyBox);
      tracePlayer?.clear("Arreglo generado. Ejecuta Reproducir.");
      renderSortingConsole(consoleBox, []);
    }
  }

  async function selectAlgorithm() {
    const algorithmId = algorithmSelect ? algorithmSelect.value : "";
    const data = await postJson(algorithmUrl, { algorithm_id: algorithmId });
    setMessage(data.message, Boolean(data.success));
    updateCodeByAlgorithm();
    tracePlayer?.clear("Algoritmo cambiado. Ejecuta Reproducir.");
    renderSortingConsole(consoleBox, []);
  }

  async function runSorting(finalOnly) {
    const algorithmId = algorithmSelect ? algorithmSelect.value : "";
    const mode = finalOnly ? "fast" : "step_by_step";
    const data = await postJson(runUrl, { mode, algorithm_id: algorithmId });
    setMessage(data.message, Boolean(data.success));
    if (!data.success) {
      return;
    }
    sPushUniqueHistoryEntry(history, { title: "Ejecutar", message: data.message });
    renderSortingHistory(history, historyBox);
    model.visual_state = data.visual_state;
    if (finalOnly) {
      trace = null;
      tracePlayer?.clear("Modo rapido: se aplico el resultado final.");
      renderSortingVisualState(data.visual_state, visualContainer);
      renderSortingConsole(consoleBox, [`[printf] ${data.message}`]);
      setButtonsState();
      return;
    }
    trace = data.execution_trace || null;
    if (!trace || !tracePlayer) {
      renderSortingVisualState(data.visual_state, visualContainer);
      renderSortingConsole(consoleBox, [`[printf] ${data.message}`]);
      return;
    }
    tracePlayer.loadTrace(trace);
    await tracePlayer.playFromStart();
    setButtonsState();
  }

  async function resetSorting() {
    const data = await postJson(resetUrl, {});
    setMessage(data.message, Boolean(data.success));
    model.visual_state = data.visual_state;
    renderSortingVisualState(model.visual_state, visualContainer);
    history = [];
    renderSortingHistory(history, historyBox);
    trace = null;
    tracePlayer?.clear("Usa Reproducir para ejecutar.");
    renderSortingConsole(consoleBox, []);
    setButtonsState();
  }

  function fillAlgorithmSelect() {
    if (!algorithmSelect) {
      return;
    }
    const options = Array.isArray(model.algorithms) ? model.algorithms : [];
    algorithmSelect.innerHTML = options
      .map((item) => `<option value="${sEscape(item.id)}">${sEscape(item.label)}</option>`)
      .join("");
    const selected = model.visual_state && model.visual_state.algorithm ? String(model.visual_state.algorithm) : "burbuja";
    algorithmSelect.value = selected;
  }

  createButton?.addEventListener("click", createArray);
  randomButton?.addEventListener("click", randomArray);
  algorithmSelect?.addEventListener("change", selectAlgorithm);
  playButton?.addEventListener("click", async () => {
    await runSorting(!(stepToggle && stepToggle.checked));
  });
  stepButton?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    if (!tracePlayer || !tracePlayer.hasTrace()) {
      await runSorting(false);
      return;
    }
    await tracePlayer.step();
    setButtonsState();
  });
  prevButton?.addEventListener("click", () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    tracePlayer?.prev();
    setButtonsState();
  });
  stepToggle?.addEventListener("change", () => {
    tracePlayer?.clear(
      stepToggle.checked
        ? "Modo paso a paso activado. Usa Reproducir o Siguiente paso."
        : "Modo rapido activado. Reproducir aplicara solo el resultado final.",
    );
    setButtonsState();
  });
  resetButton?.addEventListener("click", resetSorting);
  speedSlider?.addEventListener("input", () => setSpeed(speedSlider.value));

  fillAlgorithmSelect();
  updateCodeByAlgorithm();
  renderSortingVisualState(model.visual_state, visualContainer);
  renderSortingHistory(history, historyBox);
  renderSortingConsole(consoleBox, []);
  if (speedSlider) {
    setSpeed(speedSlider.value);
  }
  setButtonsState();
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.SORTING_VIEW_MODEL) {
    initSortingPage(window.SORTING_VIEW_MODEL);
  }
});
