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
  container.setAttribute("role", "img");
  container.setAttribute("aria-label", `Arreglo del algoritmo ${state.algorithm || "sin seleccionar"}: ${items.join(", ") || "vacío"}`);
  const strategyContainer = sById("sorting-strategy-view");
  if (!items.length) {
    container.innerHTML = '<p class="muted">Arreglo vacio. Crea o genera datos para iniciar.</p>';
    renderSortingStrategy(state, strategyContainer);
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
      const width = numeric === 0 ? 0 : Math.max(5, Math.round((Math.abs(numeric) / maxAbs) * 48));
      const classes = ["sorting-item"];
      if (comparing.has(index)) classes.push("is-comparing");
      if (swapping.has(index)) classes.push("is-swapping");
      if (sorted.has(index)) classes.push("is-sorted");
      if (pivot === index) classes.push("is-pivot");
      if (activeRange && (index < activeRange[0] || index > activeRange[1])) classes.push("is-out-range");
      const symbols = [comparing.has(index) ? "C" : "", swapping.has(index) ? "I" : "", pivot === index ? "P" : "", sorted.has(index) ? "✓" : ""].filter(Boolean);
      const sideClass = numeric < 0 ? "is-negative" : numeric > 0 ? "is-positive" : "is-zero";
      return `
        <div class="${classes.join(" ")}" aria-label="Índice ${index}, valor ${sEscape(value)}${symbols.length ? `, estado ${symbols.join(" ")}` : ""}">
          <div class="sorting-item-label">[${index}] ${sEscape(value)}</div><div class="sorting-state-symbols" aria-hidden="true">${symbols.map((symbol) => `<span class="sorting-state-symbol">${symbol}</span>`).join("")}</div>
          <div class="sorting-zero-track"><span class="sorting-zero-axis" aria-hidden="true"></span><div class="sorting-item-bar ${sideClass}" style="width:${width}%"></div></div>
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

  const temporaries = state.temporaries && typeof state.temporaries === "object"
    ? Object.entries(state.temporaries)
    : [];
  const temporariesHtml = temporaries.length
    ? `<div class="sorting-aux"><h5>Variables temporales</h5><div class="sorting-aux-items">${temporaries.map(([name, value]) => `<span>${sEscape(name)} = ${sEscape(value)}</span>`).join("")}</div></div>`
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

  container.innerHTML = `<div class="sorting-items">${bars}</div>${temporariesHtml}${aux}${metricsHtml}`;
  renderSortingStrategy(state, strategyContainer);
}

function renderSortingStrategy(state, container) {
  if (!container || !state) return;
  const algorithm = String(state.algorithm || "");
  const token = String(state.trace_token || "");
  const items = Array.isArray(state.items) ? state.items.map(Number) : [];
  const comparing = Array.isArray(state.comparing_indices) ? state.comparing_indices.map(Number) : [];
  const range = Array.isArray(state.active_range) ? state.active_range.map(Number) : null;
  const auxiliary = Array.isArray(state.auxiliary_array) ? state.auxiliary_array.map(Number) : [];
  const action = sEscape(state.trace_action || state.last_operation?.message || "Prepara la ejecución.");
  const cells = (values, className = "") => `<div class="sorting-strategy-cells ${className}">${values.map((value, index) => `<span><small>${index}</small>${sEscape(value)}</span>`).join("")}</div>`;
  let html = `<p>${action}</p>`;

  if (algorithm === "seleccion") {
    const candidate = comparing.length ? comparing[comparing.length - 1] : null;
    html += `<div class="sorting-cue-row"><strong>Prefijo confirmado:</strong> ${range ? `[0..${Math.max(0, range[0] - 1)}]` : "—"}<strong>Mínimo provisional:</strong> ${candidate === null ? "—" : `[${candidate}] = ${sEscape(items[candidate])}`}</div>`;
  } else if (algorithm === "insercion") {
    const keyMatch = String(state.trace_action || "").match(/(?:clave|Insertar clave) (-?\d+)/i);
    const hole = state.swapping_indices?.[0] ?? comparing[1];
    html += `<div class="sorting-cue-row"><strong>Clave:</strong> ${keyMatch ? sEscape(keyMatch[1]) : "—"}<strong>Hueco:</strong> ${Number.isInteger(hole) ? `[${hole}]` : "—"}</div>`;
  } else if (algorithm === "burbuja" || algorithm === "intercambio") {
    html += `<div class="sorting-cue-row"><strong>Pareja:</strong> ${comparing.length ? comparing.map((index) => `[${index}]`).join(" ↔ ") : "—"}<strong>Frontera:</strong> ${range ? `activo ${range[0]}..${range[1]}` : "—"}</div>`;
  } else if (algorithm === "shell") {
    const gapMatch = String(state.trace_action || "").match(/(?:gap\)?|Intervalo actual \(gap\)):\s*(\d+)/i);
    const gap = gapMatch ? Number(gapMatch[1]) : null;
    html += `<div class="sorting-cue-row"><strong>Intervalo (gap):</strong> ${gap ?? "consulta la fase"}<strong>Grupo activo:</strong> ${comparing.length ? comparing.map((index) => `[${index}]`).join(" · ") : "—"}</div>`;
  } else if (algorithm === "quicksort") {
    const pivot = Number.isInteger(state.pivot_index) ? state.pivot_index : null;
    html += `<div class="sorting-partition"><span>Menores / rango izquierdo</span><strong>P ${pivot === null ? "—" : `[${pivot}] = ${sEscape(items[pivot])}`}</strong><span>Mayores / rango derecho</span></div><p>Subproblema activo: ${range ? `[${range[0]}..${range[1]}]` : "—"}</p>`;
  } else if (algorithm === "mergesort") {
    html += `<div class="sorting-recursion-view"><strong>División/fusión activa</strong><span>${range ? `[${range[0]}..${range[1]}]` : "—"}</span>${auxiliary.length ? cells(auxiliary, "is-auxiliary") : "<span>Aún sin auxiliar.</span>"}</div>`;
  } else if (algorithm === "heapsort") {
    html += `<div class="sorting-heap-view">${items.map((value, index) => `<div><strong>${sEscape(value)}</strong><small>[${index}] hijos: ${2 * index + 1 < items.length ? 2 * index + 1 : "—"}, ${2 * index + 2 < items.length ? 2 * index + 2 : "—"}</small></div>`).join("")}</div>`;
  } else if (algorithm === "counting_sort" || algorithm === "binsort") {
    const minimum = items.length ? Math.min(...items) : 0;
    html += `<div class="sorting-buckets">${auxiliary.map((count, index) => `<div><strong>${sEscape(minimum + index)}</strong><span>${sEscape(count)}</span><small>${algorithm === "binsort" ? "urna" : "frecuencia"}</small></div>`).join("") || (algorithm === "binsort" ? "Urnas aún no inicializadas." : "Frecuencias aún no inicializadas.")}</div>`;
  } else if (algorithm === "radixsort") {
    const expMatch = String(state.trace_action || "").match(/exp=(\d+)/);
    const exp = expMatch ? Number(expMatch[1]) : 1;
    const source = auxiliary.length ? auxiliary : items;
    html += `<p><strong>Dígito activo:</strong> ${exp === 1 ? "unidades" : exp === 10 ? "decenas" : `posición ${exp}`} · el signo se procesa por grupos separados.</p><div class="sorting-buckets">${Array.from({ length: 10 }, (_, digit) => { const values = source.filter((value) => Math.floor(Math.abs(value) / exp) % 10 === digit); return `<div><strong>${digit}</strong><span>${values.length ? values.map(sEscape).join(", ") : "∅"}</span><small>bucket</small></div>`; }).join("")}</div>`;
  } else {
    html += items.length ? cells(items) : "";
  }
  container.innerHTML = html;
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

function sEnhanceCodeNavigation(codePanel, functionList, hideComments, activeLine) {
  if (!codePanel) return;
  const raw = String(codePanel.dataset.rawCode || codePanel.textContent || "");
  const rows = raw.replaceAll("\r\n", "\n").split("\n");
  const functions = [];
  const signature = /^\s*(?:static\s+)?(?:void|bool|int|size_t|uint32_t|OrdenamientoResultado)\s+\**([A-Za-z_]\w*)\s*\(/;
  rows.forEach((row, index) => {
    const match = row.match(signature);
    if (match) functions.push({ name: match[1], line: index });
  });

  let inBlockComment = false;
  Array.from(codePanel.querySelectorAll(".code-line")).forEach((lineEl, index) => {
    const trimmed = String(rows[index] || "").trim();
    const startsBlock = trimmed.startsWith("/*");
    const isComment = inBlockComment || startsBlock || trimmed.startsWith("//") || trimmed.startsWith("*");
    lineEl.classList.toggle("is-code-comment", isComment);
    if (startsBlock && !trimmed.includes("*/")) inBlockComment = true;
    if (inBlockComment && trimmed.includes("*/")) inBlockComment = false;
  });
  codePanel.classList.toggle("hide-code-comments", Boolean(hideComments && hideComments.checked));

  if (!functionList) return;
  functionList.innerHTML = functions.length
    ? functions.map((item) => `<li><button type="button" class="sorting-function-link" data-code-line="${item.line}">${sEscape(item.name)}</button></li>`).join("")
    : "<li class=\"muted\">Sin funciones detectadas</li>";
  const active = [...functions].reverse().find((item) => Number.isInteger(activeLine) && item.line <= activeLine) || functions[0];
  functionList.querySelectorAll(".sorting-function-link").forEach((button) => {
    button.classList.toggle("is-active", Boolean(active && Number(button.dataset.codeLine) === active.line));
    button.addEventListener("click", () => {
      const target = codePanel.querySelector(`.code-line[data-line="${button.dataset.codeLine}"]`);
      target?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
}

function sInitResponsiveWorkspace() {
  const workspace = document.querySelector(".sorting-primary-workspace");
  const tabs = Array.from(document.querySelectorAll("[data-sorting-tab]"));
  if (!workspace || !tabs.length) return;
  let saved = "visual";
  try { saved = window.sessionStorage.getItem("sorting-active-tab") || "visual"; } catch (_error) { saved = "visual"; }
  const activate = (name) => {
    const selected = name === "code" ? "code" : "visual";
    workspace.dataset.activeTab = selected;
    tabs.forEach((tab) => {
      const active = tab.dataset.sortingTab === selected;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", String(active));
    });
    try { window.sessionStorage.setItem("sorting-active-tab", selected); } catch (_error) { /* storage is optional */ }
  };
  tabs.forEach((tab) => tab.addEventListener("click", () => activate(tab.dataset.sortingTab)));
  activate(saved);
}

const SORTING_GUIDED_EXAMPLES = {
  normal: { values: [7, 2, 9, 4, 1, 6, 3], explanation: "Caso mixto para reconocer las fases principales." },
  ordered: { values: [1, 2, 3, 4, 5, 6, 7], explanation: "Permite observar qué trabajo evita o mantiene el algoritmo." },
  reverse: { values: [7, 6, 5, 4, 3, 2, 1], explanation: "Fuerza numerosos movimientos en varios métodos." },
  duplicates: { values: [4, 2, 4, 1, 2, 4, 1], explanation: "Ayuda a estudiar igualdad y estabilidad." },
  signed: { values: [-5, 3, 0, -2, 7, -1, 3], explanation: "Comprueba orden, signo, cero y valores repetidos." },
};

function sResolveGuidedExample(kind, algorithmId) {
  if (SORTING_GUIDED_EXAMPLES[kind]) return SORTING_GUIDED_EXAMPLES[kind];
  const divideAndConquer = [4, 2, 6, 1, 3, 5, 7];
  if (kind === "best") {
    return algorithmId === "quicksort"
      ? { values: divideAndConquer, explanation: "Distribuye los pivotes de QuickSort de forma aproximadamente equilibrada." }
      : { values: [1, 2, 3, 4, 5, 6, 7], explanation: "Entrada orientativa de mejor caso; contrasta las métricas observadas." };
  }
  return algorithmId === "quicksort"
    ? { values: [1, 2, 3, 4, 5, 6, 7], explanation: "Caso adverso orientativo para algunas estrategias de pivote; verifica la implementación mostrada." }
    : { values: [7, 6, 5, 4, 3, 2, 1], explanation: "Entrada orientativa de peor caso; contrasta comparaciones y movimientos." };
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
  const compareUrl = controls.dataset.compareUrl;
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
  const prepareButton = sById("sorting-sim-prepare");
  const pauseButton = sById("sorting-sim-pause");
  const startButton = sById("sorting-sim-start");
  const endButton = sById("sorting-sim-end");
  const repeatButton = sById("sorting-sim-repeat");
  const restartExecutionButton = sById("sorting-restart-execution");
  const progress = sById("sorting-progress");
  const progressLabel = sById("sorting-progress-label");
  const functionList = sById("sorting-function-list");
  const hideComments = sById("sorting-hide-comments");
  const learningShell = document.querySelector(".sorting-learning-shell");
  const learningLevel = sById("sorting-learning-level");
  const guidedExample = sById("sorting-guided-example");
  const loadExampleButton = sById("sorting-load-example");
  const exampleExplanation = sById("sorting-example-explanation");
  const pedagogyPhase = sById("sorting-pedagogy-phase");
  const pedagogyObjective = sById("sorting-pedagogy-objective");
  const pedagogyNarration = sById("sorting-pedagogy-narration");
  const conditionView = sById("sorting-condition-view");
  const variableTable = sById("sorting-variable-table");
  const callStack = sById("sorting-call-stack");
  const loopView = sById("sorting-loop-view");
  const pointerView = sById("sorting-pointer-view");
  const invariantText = sById("sorting-invariant-text");
  const observedMetrics = sById("sorting-observed-metrics");
  const theoryProfile = sById("sorting-theory-profile");
  const practiceMode = sById("sorting-practice-mode");
  const predictionCard = sById("sorting-prediction-card");
  const predictionPrompt = sById("sorting-prediction-prompt");
  const predictionFeedback = sById("sorting-prediction-feedback");
  const hintOne = sById("sorting-hint-one");
  const hintTwo = sById("sorting-hint-two");
  const predictionSkip = sById("sorting-prediction-skip");
  const conceptProgress = sById("sorting-concept-progress");
  const progressReset = sById("sorting-progress-reset");
  const compareLeft = sById("sorting-compare-left");
  const compareRight = sById("sorting-compare-right");
  const compareSync = sById("sorting-compare-sync");
  const compareRun = sById("sorting-compare-run");
  const compareProgress = sById("sorting-compare-progress");
  const compareInput = sById("sorting-compare-input");
  const compareConclusion = sById("sorting-compare-conclusion");
  const announcer = sById("sorting-accessible-announcer");
  const exportImage = sById("sorting-export-image");
  const exportSummary = sById("sorting-export-summary");

  const createButton = sById("sorting-create-array");
  const randomButton = sById("sorting-random-array");
  const resetButton = sById("sorting-reset");

  let trace = null;
  let history = [];
  let consoleLines = [];
  let speedSetting = 0;
  let speedMultiplier = 1;
  let currentPedagogy = null;
  let pendingPredictionIndex = null;
  let comparison = null;
  let practiceProgress = { attempts: 0, correct: 0, concepts: {} };
  try { practiceProgress = JSON.parse(window.sessionStorage.getItem("sorting-practice-progress") || "null") || practiceProgress; } catch (_error) { /* session-only fallback */ }

  const didacticOps = (model.didactic && model.didactic.operations) || {};

  function isStepByStepEnabled() {
    return !stepToggle || Boolean(stepToggle.checked);
  }

  function currentLearningLevel() {
    const value = learningLevel ? learningLevel.value : "intermediate";
    return ["basic", "intermediate", "advanced"].includes(value) ? value : "intermediate";
  }

  function renderPedagogy(frame) {
    currentPedagogy = frame && typeof frame === "object" ? frame : null;
    if (!currentPedagogy) {
      if (pedagogyPhase) pedagogyPhase.textContent = "Preparación";
      if (pedagogyObjective) pedagogyObjective.textContent = "Selecciona datos y un algoritmo para comenzar.";
      if (pedagogyNarration) pedagogyNarration.textContent = "La explicación de cada paso aparecerá aquí.";
      if (conditionView) { conditionView.textContent = "Sin condición evaluada."; conditionView.className = "sorting-condition-view"; }
      if (variableTable) variableTable.innerHTML = '<tr><td colspan="4">Sin frame activo.</td></tr>';
      if (callStack) callStack.innerHTML = "<li>Sin llamadas activas.</li>";
      if (loopView) loopView.textContent = "Sin ciclo activo.";
      if (pointerView) pointerView.textContent = "Sin punteros activos.";
      if (invariantText) invariantText.textContent = "Se mostrará al preparar la ejecución.";
      return;
    }
    const level = currentLearningLevel();
    const phase = currentPedagogy.phase || {};
    const narration = currentPedagogy.narration || {};
    if (pedagogyPhase) pedagogyPhase.textContent = `${phase.label || "Ejecución"} · ${currentPedagogy.concept || "paso"}`;
    if (pedagogyObjective) pedagogyObjective.textContent = phase.goal || "Comprender el cambio de estado.";
    if (pedagogyNarration) pedagogyNarration.textContent = narration[level] || narration.intermediate || "";
    const condition = currentPedagogy.condition;
    if (conditionView) {
      conditionView.className = `sorting-condition-view${condition && condition.result === true ? " is-true" : condition && condition.result === false ? " is-false" : ""}`;
      conditionView.innerHTML = condition
        ? `<strong>${sEscape(condition.expression)}</strong> → ${condition.result === true ? "VERDADERO" : condition.result === false ? "FALSO" : "resultado pendiente"}<br><span>${sEscape(condition.consequence || "")}</span>`
        : "Sin condición evaluada en este frame.";
    }
    const variables = Array.isArray(currentPedagogy.variables) ? currentPedagogy.variables : [];
    if (variableTable) {
      variableTable.innerHTML = variables.length
        ? variables.map((variable) => `<tr class="${variable.changed ? "is-changed" : ""}"><td>${sEscape(variable.name)}</td><td>${sEscape(variable.type)}</td><td>${sEscape(variable.value)}</td><td>${sEscape(variable.meaning)}</td></tr>`).join("")
        : '<tr><td colspan="4">Este frame no modifica variables escalares.</td></tr>';
    }
    const stack = Array.isArray(currentPedagogy.call_stack) ? currentPedagogy.call_stack : [];
    if (callStack) {
      callStack.innerHTML = stack.length
        ? stack.map((call) => `<li><strong>${sEscape(call.function)}</strong>(${sEscape(JSON.stringify(call.parameters || {}))})<br><small>${sEscape(call.continuation || "")}</small></li>`).join("")
        : "<li>Sin llamadas activas.</li>";
    }
    const loop = currentPedagogy.loop;
    if (loopView) {
      loopView.innerHTML = loop
        ? `<strong>${sEscape(loop.kind)}</strong> · iteración ${sEscape(loop.iteration)} · límites ${sEscape(JSON.stringify(loop.bounds))}${loop.exit ? " · salida del ciclo" : ""}`
        : "Sin ciclo activo en este frame.";
    }
    const pointers = Array.isArray(currentPedagogy.pointers) ? currentPedagogy.pointers : [];
    if (pointerView) {
      pointerView.innerHTML = pointers.length
        ? pointers.map((pointer) => `<div><strong>${sEscape(pointer.name)}</strong> → ${sEscape(pointer.target)} = ${sEscape(pointer.value)}</div>`).join("")
        : "Sin punteros activos en este frame.";
    }
    if (invariantText) invariantText.textContent = currentPedagogy.invariant?.text || "Invariante no disponible.";
  }

  function renderAnalysis(state) {
    const metrics = state && state.metrics ? state.metrics : {};
    if (observedMetrics) observedMetrics.innerHTML = `<div class="sorting-theory-grid"><span>Comparaciones<br><strong>${sEscape(metrics.comparisons || 0)}</strong></span><span>Intercambios<br><strong>${sEscape(metrics.swaps || 0)}</strong></span><span>Movimientos<br><strong>${sEscape(metrics.moves || 0)}</strong></span></div>`;
    const theory = trace && trace.theory_profile ? trace.theory_profile : null;
    if (theoryProfile && theory) theoryProfile.innerHTML = `<div class="sorting-theory-grid"><span>Mejor<br><strong>${sEscape(theory.best)}</strong></span><span>Promedio<br><strong>${sEscape(theory.average)}</strong></span><span>Peor<br><strong>${sEscape(theory.worst)}</strong></span><span>Memoria<br><strong>${sEscape(theory.memory)}</strong></span><span>Estable<br><strong>${theory.stable ? "Sí" : "No"}</strong></span><span>In-place<br><strong>${theory.in_place ? "Sí" : "No"}</strong></span></div>`;
  }

  function applyLearningLevel() {
    const level = currentLearningLevel();
    if (learningShell) learningShell.dataset.learningLevel = level;
    try { window.sessionStorage.setItem("sorting-learning-level", level); } catch (_error) { /* optional */ }
    renderPedagogy(currentPedagogy);
  }

  function savePracticeProgress() {
    if (conceptProgress) conceptProgress.textContent = `${practiceProgress.attempts} intentos · ${practiceProgress.correct} aciertos`;
    try { window.sessionStorage.setItem("sorting-practice-progress", JSON.stringify(practiceProgress)); } catch (_error) { /* session-only */ }
  }

  function predictionExpected(frame) {
    if (frame?.condition && typeof frame.condition.result === "boolean") return frame.condition.result;
    const token = String(frame?.source?.line_token || "");
    return token.includes("swap") || frame?.concept === "phase" || frame?.concept === "call";
  }

  function showPredictionForNext() {
    if (!practiceMode?.checked || !trace || !tracePlayer) return false;
    const nextIndex = tracePlayer.getCursor() + 1;
    const frame = trace.steps?.[nextIndex]?.pedagogy;
    if (!frame || !["condition", "comparison", "branch", "call", "phase"].includes(frame.concept)) return false;
    pendingPredictionIndex = nextIndex;
    predictionCard.hidden = false;
    const expression = frame.condition?.expression;
    predictionPrompt.textContent = expression ? `¿La condición «${expression}» será verdadera?` : `¿Este paso producirá la acción «${frame.phase?.label || frame.concept}»?`;
    hintOne.textContent = frame.invariant?.text || "Observa el rango activo y los elementos señalados.";
    hintTwo.textContent = frame.condition?.consequence || frame.narration?.intermediate || "Relaciona el estado actual con la línea C resaltada.";
    predictionFeedback.textContent = "El resultado permanece oculto hasta responder o continuar.";
    return true;
  }

  async function advanceWithPractice() {
    if (showPredictionForNext()) return;
    await tracePlayer?.step();
    setButtonsState();
  }

  async function answerPrediction(answer) {
    if (pendingPredictionIndex === null || !trace) return;
    const frame = trace.steps[pendingPredictionIndex]?.pedagogy;
    const expected = predictionExpected(frame);
    const correct = Boolean(answer) === expected;
    practiceProgress.attempts += 1;
    if (correct) practiceProgress.correct += 1;
    const concept = frame?.concept || "otro";
    practiceProgress.concepts[concept] = (practiceProgress.concepts[concept] || 0) + (correct ? 1 : 0);
    savePracticeProgress();
    predictionFeedback.textContent = correct ? "Correcto. Ahora observa cómo el frame confirma tu predicción." : `No coincide. ${frame?.condition?.consequence || frame?.narration?.intermediate || "Revisa el cambio mostrado."}`;
    pendingPredictionIndex = null;
    await tracePlayer.step();
    predictionCard.hidden = true;
    setButtonsState();
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
    sEnhanceCodeNavigation(codePanel, functionList, hideComments, null);
  }

  function buildConsoleFromTrace(stepIndex) {
    if (!trace || !Array.isArray(trace.steps) || stepIndex < 0) {
      return [];
    }
    const lines = [];
    for (let idx = 0; idx <= Math.min(stepIndex, trace.steps.length - 1); idx += 1) {
      const step = trace.steps[idx] || {};
      const events = step.debug && Array.isArray(step.debug.console_events)
        ? step.debug.console_events
        : [];
      for (const event of events) {
        if (event && String(event).trim()) {
          sPushUniqueConsoleLine(lines, `[printf] ${String(event).trim()}`);
        }
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
      onCursorChange: ({ cursor, step }) => {
        consoleLines = buildConsoleFromTrace(cursor);
        renderSortingConsole(consoleBox, consoleLines);
        const currentStep = step || (trace && Array.isArray(trace.steps) ? trace.steps[cursor] : null);
        if (currentStep?.state_after) model.visual_state = currentStep.state_after;
        sEnhanceCodeNavigation(codePanel, functionList, hideComments, currentStep ? currentStep.line_index : null);
        renderPedagogy(currentStep ? currentStep.pedagogy : null);
        renderAnalysis(currentStep ? currentStep.state_after : model.visual_state);
        if (progress) {
          progress.max = String(trace && Array.isArray(trace.steps) ? trace.steps.length : 0);
          progress.value = String(Math.max(0, cursor + 1));
          progress.disabled = !trace;
        }
        if (progressLabel) {
          const phase = currentStep?.pedagogy?.phase?.label || "sin fase";
          const concept = currentStep?.pedagogy?.concept || "sin concepto";
          progressLabel.textContent = `Paso ${Math.max(0, cursor + 1)} · ${phase} · ${concept}`;
          if (announcer) announcer.textContent = `Paso ${Math.max(0, cursor + 1)}. ${phase}. ${concept}.`;
        }
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
    if (pauseButton) pauseButton.disabled = !stepMode || !tracePlayer || !tracePlayer.hasTrace();
    if (startButton) startButton.disabled = !stepMode || !tracePlayer || !tracePlayer.hasTrace();
    if (endButton) endButton.disabled = !stepMode || !tracePlayer || !tracePlayer.hasTrace();
    if (repeatButton) repeatButton.disabled = !stepMode || !tracePlayer || !tracePlayer.hasTrace();
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
      trace = null;
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
      trace = null;
      model.visual_state = data.visual_state;
      renderSortingVisualState(model.visual_state, visualContainer);
      sPushUniqueHistoryEntry(history, { title: "Generar aleatorio", message: data.message });
      renderSortingHistory(history, historyBox);
      tracePlayer?.clear("Arreglo generado. Ejecuta Reproducir.");
      renderSortingConsole(consoleBox, []);
    }
  }

  async function loadGuidedExample() {
    const kind = guidedExample ? guidedExample.value : "normal";
    const algorithmId = algorithmSelect ? algorithmSelect.value : "burbuja";
    const example = sResolveGuidedExample(kind, algorithmId);
    if (manualInput) manualInput.value = example.values.join(", ");
    if (exampleExplanation) exampleExplanation.textContent = example.explanation;
    await createArray();
  }

  async function selectAlgorithm() {
    const algorithmId = algorithmSelect ? algorithmSelect.value : "";
    const data = await postJson(algorithmUrl, { algorithm_id: algorithmId });
    setMessage(data.message, Boolean(data.success));
    trace = null;
    updateCodeByAlgorithm();
    tracePlayer?.clear("Algoritmo cambiado. Ejecuta Reproducir.");
    renderSortingConsole(consoleBox, []);
  }

  async function runSorting(finalOnly, autoPlay = true) {
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
    trace = data.execution_trace || null;
    renderAnalysis(data.visual_state);
    if (finalOnly) {
      trace = null;
      tracePlayer?.clear("Modo rapido: se aplico el resultado final.");
      renderSortingVisualState(data.visual_state, visualContainer);
      renderSortingConsole(consoleBox, []);
      setButtonsState();
      return;
    }
    if (!trace || !tracePlayer) {
      renderSortingVisualState(data.visual_state, visualContainer);
      renderSortingConsole(consoleBox, []);
      return;
    }
    tracePlayer.loadTrace(trace);
    sEnhanceCodeNavigation(codePanel, functionList, hideComments, null);
    if (autoPlay) await tracePlayer.playFromStart();
    setButtonsState();
  }

  async function resetSorting() {
    if (!window.confirm("¿Restablecer los datos, el algoritmo y el historial de esta sesión?")) return;
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
    if (compareLeft && compareRight) {
      compareLeft.innerHTML = algorithmSelect.innerHTML;
      compareRight.innerHTML = algorithmSelect.innerHTML;
      compareLeft.value = "burbuja";
      compareRight.value = "insercion";
    }
  }

  function comparisonStep(side, cursor, concept, occurrence = 1) {
    const steps = side?.trace?.steps || [];
    if (!steps.length) return null;
    if (concept) {
      const matches = steps.filter((step) => step.pedagogy?.concept === concept);
      return matches[Math.min(Math.max(occurrence - 1, 0), matches.length - 1)] || steps[Math.min(cursor, steps.length - 1)];
    }
    return steps[Math.min(cursor, steps.length - 1)];
  }

  function renderComparisonSide(side, step, viewId, analysisId, titleId) {
    const state = step?.state_after || side?.trace?.final_state || {};
    const items = Array.isArray(state.items) ? state.items : [];
    const view = sById(viewId);
    const analysis = sById(analysisId);
    const title = sById(titleId);
    if (title) title.textContent = side.algorithm;
    if (view) view.innerHTML = `<div class="sorting-compare-array">${items.map((value) => `<span>${sEscape(value)}</span>`).join("")}</div><p>${sEscape(step?.pedagogy?.phase?.label || "Resultado")}</p>`;
    const metrics = state.metrics || side.result?.metrics || {};
    const theory = side.trace?.theory_profile || {};
    if (analysis) analysis.innerHTML = `<div class="sorting-compare-analysis"><strong>Observado:</strong> ${metrics.comparisons || 0} comparaciones, ${metrics.swaps || 0} intercambios, ${metrics.moves || 0} movimientos.<br><strong>Teoría:</strong> mejor ${sEscape(theory.best)}, promedio ${sEscape(theory.average)}, peor ${sEscape(theory.worst)}, memoria ${sEscape(theory.memory)}, estable ${theory.stable ? "sí" : "no"}, in-place ${theory.in_place ? "sí" : "no"}.</div>`;
  }

  function renderComparisonCursor() {
    if (!comparison || !compareProgress) return;
    const cursor = Math.max(0, Number(compareProgress.value) - 1);
    const leftRaw = comparison.left.trace.steps[Math.min(cursor, comparison.left.trace.steps.length - 1)];
    const concept = compareSync?.value === "concept" ? leftRaw?.pedagogy?.concept : null;
    const occurrence = concept ? comparison.left.trace.steps.slice(0, cursor + 1).filter((step) => step.pedagogy?.concept === concept).length : 1;
    const leftStep = concept ? leftRaw : comparisonStep(comparison.left, cursor, null);
    const rightStep = comparisonStep(comparison.right, cursor, concept, occurrence);
    renderComparisonSide(comparison.left, leftStep, "sorting-compare-left-view", "sorting-compare-left-analysis", "sorting-compare-left-title");
    renderComparisonSide(comparison.right, rightStep, "sorting-compare-right-view", "sorting-compare-right-analysis", "sorting-compare-right-title");
    if (compareConclusion) {
      const leftMetrics = comparison.left.result.metrics;
      const rightMetrics = comparison.right.result.metrics;
      const fewer = leftMetrics.comparisons === rightMetrics.comparisons ? "Ambos realizaron igual número de comparaciones" : leftMetrics.comparisons < rightMetrics.comparisons ? `${comparison.left.algorithm} realizó menos comparaciones` : `${comparison.right.algorithm} realizó menos comparaciones`;
      compareConclusion.textContent = `${fewer} en esta entrada. Es una observación particular: una sola entrada no demuestra la complejidad general.`;
    }
  }

  async function prepareComparison() {
    const frozenInput = manualInput?.value || (model.visual_state?.items || []).join(",");
    const data = await postJson(compareUrl, { values: frozenInput, left_algorithm: compareLeft?.value, right_algorithm: compareRight?.value });
    if (!data.success) { setMessage(data.message, false); return; }
    comparison = data;
    if (compareInput) compareInput.textContent = `Entrada inmutable: [${data.input.join(", ")}]`;
    compareProgress.disabled = false;
    compareProgress.min = "1";
    compareProgress.max = String(Math.max(data.left.trace.steps.length, data.right.trace.steps.length));
    compareProgress.value = "1";
    renderComparisonCursor();
  }

  createButton?.addEventListener("click", createArray);
  randomButton?.addEventListener("click", randomArray);
  algorithmSelect?.addEventListener("change", selectAlgorithm);
  playButton?.addEventListener("click", async () => {
    if (!(stepToggle && stepToggle.checked)) {
      await runSorting(true);
    } else if (practiceMode?.checked) {
      if (!tracePlayer?.hasTrace()) await runSorting(false, false);
      await advanceWithPractice();
    } else if (tracePlayer?.hasTrace()) {
      await tracePlayer.play();
      setButtonsState();
    } else {
      await runSorting(false, true);
    }
  });
  prepareButton?.addEventListener("click", async () => runSorting(false, false));
  pauseButton?.addEventListener("click", () => { tracePlayer?.pause(); setButtonsState(); });
  startButton?.addEventListener("click", () => { tracePlayer?.seek(-1); setButtonsState(); });
  endButton?.addEventListener("click", () => { if (tracePlayer) tracePlayer.seek(tracePlayer.getTotalSteps() - 1); setButtonsState(); });
  repeatButton?.addEventListener("click", async () => { if (!tracePlayer) return; tracePlayer.seek(-1); await tracePlayer.play(); setButtonsState(); });
  restartExecutionButton?.addEventListener("click", () => { tracePlayer?.reset(); setButtonsState(); });
  stepButton?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    if (!tracePlayer || !tracePlayer.hasTrace()) {
      await runSorting(false);
      return;
    }
    await advanceWithPractice();
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
  progress?.addEventListener("input", () => { tracePlayer?.seek(Number(progress.value) - 1); setButtonsState(); });
  document.querySelectorAll("[data-prediction]").forEach((button) => button.addEventListener("click", () => answerPrediction(button.dataset.prediction === "true")));
  predictionSkip?.addEventListener("click", async () => { pendingPredictionIndex = null; predictionCard.hidden = true; await tracePlayer?.step(); setButtonsState(); });
  progressReset?.addEventListener("click", () => { practiceProgress = { attempts: 0, correct: 0, concepts: {} }; savePracticeProgress(); });
  practiceMode?.addEventListener("change", () => { if (!practiceMode.checked) { pendingPredictionIndex = null; predictionCard.hidden = true; } });
  compareRun?.addEventListener("click", prepareComparison);
  compareProgress?.addEventListener("input", renderComparisonCursor);
  compareSync?.addEventListener("change", renderComparisonCursor);
  exportImage?.addEventListener("click", async () => {
    try {
      const exported = await window.InterpreterRuntime.exportVisualStateAsJpg({ target: sById("sorting-visual-region"), quality: 0.9, scale: 1 });
      const link = document.createElement("a"); link.href = exported.dataUrl; link.download = exported.suggestedName; link.click();
    } catch (error) { setMessage(error.message || "No se pudo exportar la captura.", false); }
  });
  exportSummary?.addEventListener("click", () => {
    const summary = { schema: "sorting-learning-summary/v1", algorithm: algorithmSelect?.value, input: manualInput?.value, cursor: tracePlayer?.getCursor() ?? -1, total_steps: tracePlayer?.getTotalSteps() ?? 0, state: model.visual_state, theory: trace?.theory_profile || null, practice: practiceProgress };
    const url = URL.createObjectURL(new Blob([JSON.stringify(summary, null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = `ordenamiento-${summary.algorithm || "resumen"}.json`; link.click(); URL.revokeObjectURL(url);
  });
  document.addEventListener("keydown", async (event) => {
    if (!event.altKey || event.ctrlKey || event.metaKey) return;
    const key = event.key.toLowerCase();
    if (key === "arrowright") { event.preventDefault(); await advanceWithPractice(); }
    else if (key === "arrowleft") { event.preventDefault(); tracePlayer?.prev(); }
    else if (key === "home") { event.preventDefault(); tracePlayer?.seek(-1); }
    else if (key === "end") { event.preventDefault(); if (tracePlayer) tracePlayer.seek(tracePlayer.getTotalSteps() - 1); }
    else if (key === "p") { event.preventDefault(); tracePlayer?.pause(); }
    else if (key === "r") { event.preventDefault(); if (tracePlayer?.isAtEnd()) tracePlayer.seek(-1); await tracePlayer?.play(); }
    setButtonsState();
  });
  hideComments?.addEventListener("change", () => sEnhanceCodeNavigation(codePanel, functionList, hideComments, null));
  learningLevel?.addEventListener("change", applyLearningLevel);
  guidedExample?.addEventListener("change", () => {
    const example = sResolveGuidedExample(guidedExample.value, algorithmSelect ? algorithmSelect.value : "burbuja");
    if (exampleExplanation) exampleExplanation.textContent = example.explanation;
  });
  loadExampleButton?.addEventListener("click", loadGuidedExample);

  sInitResponsiveWorkspace();
  if (learningLevel) {
    try { learningLevel.value = window.sessionStorage.getItem("sorting-learning-level") || "intermediate"; } catch (_error) { learningLevel.value = "intermediate"; }
  }
  applyLearningLevel();
  savePracticeProgress();
  fillAlgorithmSelect();
  updateCodeByAlgorithm();
  renderSortingVisualState(model.visual_state, visualContainer);
  renderSortingHistory(history, historyBox);
  renderSortingConsole(consoleBox, []);
  if (speedSlider) {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) speedSlider.value = "-2";
    setSpeed(speedSlider.value);
  }
  setButtonsState();
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.SORTING_VIEW_MODEL) {
    initSortingPage(window.SORTING_VIEW_MODEL);
  }
});
