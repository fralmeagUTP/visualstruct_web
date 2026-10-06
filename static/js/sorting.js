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
        <div class="sorting-aux-items">${state.auxiliary_array.map((value) => `<span>${sEscape(state.algorithm === "mergesort" && value === null ? "sin inicializar" : value)}</span>`).join("")}</div>
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
  const auxiliary = Array.isArray(state.auxiliary_array) ? (algorithm === "mergesort" ? state.auxiliary_array : state.auxiliary_array.map(Number)) : [];
  const action = sEscape(state.trace_action || state.last_operation?.message || "Prepara la ejecución.");
  const cells = (values, className = "") => `<div class="sorting-strategy-cells ${className}">${values.map((value, index) => `<span><small>${index}</small>${sEscape(value)}</span>`).join("")}</div>`;
  let html = `<p>${action}</p>`;

  if (algorithm === "seleccion") {
    const candidate = state.selection_context ? state.selection_context.indice_menor : (comparing.length ? comparing[comparing.length - 1] : null);
    html += `<div class="sorting-cue-row"><strong>Prefijo confirmado:</strong> ${state.sorted_indices?.length ? `[0..${state.sorted_indices[state.sorted_indices.length - 1]}]` : "—"}<strong>Mínimo provisional:</strong> ${candidate === null ? "—" : `[${candidate}] = ${sEscape(items[candidate])}`}</div>`;
  } else if (algorithm === "insercion") {
    const insertion = state.insertion_context || {};
    const key = insertion.clave;
    const index = insertion.j;
    html += `<div class="sorting-cue-row"><strong>Clave:</strong> ${Number.isInteger(key) ? sEscape(key) : "—"}<strong>Índice j:</strong> ${Number.isInteger(index) ? `[${index}]` : "—"}</div>`;
  } else if (algorithm === "burbuja") {
    const bubble = state.bubble_context || {};
    const neighbors = Array.isArray(bubble.neighbors) ? bubble.neighbors : [];
    html += `<div class="sorting-cue-row"><strong>Pasada:</strong> ${Number.isInteger(bubble.pasada) ? bubble.pasada : "—"}<strong>j:</strong> ${Number.isInteger(bubble.j) ? bubble.j : "—"}<strong>hubo_intercambio:</strong> ${Number.isInteger(bubble.hubo_intercambio) ? bubble.hubo_intercambio : bubble.flag_declared ? "sin inicializar" : "—"}<strong>Vecinos:</strong> ${neighbors.length ? neighbors.map((index) => `[${index}]`).join(" / ") : "—"}</div>`;
  } else if (algorithm === "intercambio") {
    html += `<div class="sorting-cue-row"><strong>Pareja:</strong> ${comparing.length ? comparing.map((index) => `[${index}]`).join(" ↔ ") : "—"}<strong>Frontera:</strong> ${range ? `activo ${range[0]}..${range[1]}` : "—"}</div>`;
  } else if (algorithm === "shell") {
    const shell = state.shell_context || {};
    const gap = shell.intervalo;
    const group = Array.isArray(shell.group) ? shell.group : [];
    html += `<div class="sorting-cue-row"><strong>Intervalo:</strong> ${Number.isInteger(gap) ? gap : shell.gap_declared ? "sin inicializar" : "-"}<strong>i:</strong> ${Number.isInteger(shell.i) ? shell.i : shell.i_declared ? "sin inicializar" : "-"}<strong>j:</strong> ${Number.isInteger(shell.j) ? shell.j : "-"}<strong>Temporal:</strong> ${Number.isInteger(shell.temporal) ? sEscape(shell.temporal) : "-"}<strong>Grupo activo:</strong> ${group.length ? group.map((index) => `[${index}]`).join(" / ") : "-"}</div>`;
  } else if (algorithm === "quicksort") {
    const quick = state.quick_context || {};
    const value = (name) => Number.isInteger(quick[name]) ? sEscape(quick[name]) : "-";
    html += `<div class="sorting-cue-row"><strong>Primero:</strong> ${value("primero")}<strong>Ultimo:</strong> ${value("ultimo")}<strong>i:</strong> ${value("i")}<strong>j:</strong> ${value("j")}<strong>Pivote local:</strong> ${value("pivote")}<strong>Profundidad:</strong> ${quick.depth || 0}</div>`;
  } else if (algorithm === "mergesort") {
    const merge = state.merge_context || {};
    const value = (name) => Number.isInteger(merge[name]) ? sEscape(merge[name]) : "-";
    const mergeAux = Array.isArray(state.auxiliary_array) ? state.auxiliary_array : [];
    const auxCells = `<div class="sorting-strategy-cells is-auxiliary">${mergeAux.map((cell, index) => `<span data-aux-index="${index}" data-initialized="${cell !== null}"><small>${index}</small>${cell === null ? "sin inicializar" : sEscape(cell)}</span>`).join("")}</div>`;
    html += `<div class="sorting-cue-row"><strong>Izquierda:</strong> ${value("izquierda")}<strong>Medio:</strong> ${value("medio")}<strong>Derecha:</strong> ${value("derecha")}<strong>i:</strong> ${value("i")}<strong>j:</strong> ${value("j")}<strong>k:</strong> ${value("k")}<strong>Profundidad:</strong> ${merge.depth || 0}<strong>Reservas:</strong> ${merge.allocations || 0}<strong>Liberaciones:</strong> ${merge.frees || 0}</div>`;
    html += `<div class="sorting-recursion-view"><strong>Division/fusion activa</strong><span>${range ? `[${range[0]}..${range[1]}]` : "-"}</span>${merge.aux_live ? auxCells : `<span>${merge.aux_released ? "Auxiliar liberado; sin lectura." : merge.aux_declared ? "Puntero auxiliar sin inicializar." : "Sin reserva auxiliar activa."}</span>`}</div>`;
  } else if (algorithm === "heapsort") {
    const heap = state.heap_context || { heap_n: items.length, nodes: [], suffix: [] };
    const hv = (key) => heap[key] === null || heap[key] === undefined ? "-" : sEscape(heap[key]);
    html += `<div class="sorting-cue-row"><strong>n activo:</strong> ${hv("heap_n")}<strong>i:</strong> ${hv("i")}<strong>raiz:</strong> ${hv("raiz")}<strong>mayor:</strong> ${hv("mayor")}<strong>izquierdo:</strong> ${hv("izquierdo")}<strong>derecho:</strong> ${hv("derecho")}<strong>Profundidad:</strong> ${hv("depth")}<strong>Fase:</strong> ${hv("phase")}</div>`;
    html += `<div class="sorting-heap-view" data-heap-n="${heap.heap_n}">${heap.nodes.map((node) => `<div data-heap-index="${node.index}" data-children="${node.children.join(",")}"><strong>${sEscape(node.value)}</strong><small>[${node.index}] hijos: ${node.children.join(", ") || "-"}</small></div>`).join("")}</div>`;
    html += `<div class="sorting-sorted-suffix"><strong>Sufijo confirmado:</strong> ${heap.suffix.map((node) => `<span data-suffix-index="${node.index}">[${node.index}] ${sEscape(node.value)}</span>`).join(" ") || "-"}</div>`;
  } else if (["counting_sort", "binsort"].includes(algorithm) && state.counting_context) {
    const count = state.counting_context;
    const cv = (key) => {
      const active = key === "helper_i" ? count.helper_active : count.wrapper_active;
      const declared = key === "helper_i" ? count.helper_declared : count.declared;
      if (!active) return "fuera de alcance";
      if (!declared) return "sin declarar";
      return count[key] === null || count[key] === undefined ? "sin inicializar" : sEscape(count[key]);
    };
    html += `<div class="sorting-cue-row"><strong>Minimo:</strong> ${cv("minimo")}<strong>Maximo:</strong> ${cv("maximo")}<strong>Rango:</strong> ${cv("rango")}<strong>i:</strong> ${cv("i")}<strong>helper i:</strong> ${cv("helper_i")}<strong>indice:</strong> ${cv("indice")}</div>`;
    html += `<p data-count-live="${count.live}">${count.live ? "Conteo vivo: calloc inicializo todas las celdas en cero." : count.released ? "Conteo liberado; sin lectura de memoria." : "Sin reserva conteo activa."} Frecuencias escritas: ${count.filled}; consumidas: ${count.consumed}; escrituras: ${count.written}; decremento pendiente: ${count.pending_decrement}.</p>`;
    let buckets = count.buckets || [];
    if (count.count_state && !Array.isArray(state.auxiliary_array)) {
      const sparse = count.count_state;
      const active = count.phase === "fill" ? items[count.i] - count.minimo : count.i;
      const autoStart = Number.isInteger(active) && active >= 0 && active < sparse.length ? Math.floor(active / 64) * 64 : 0;
      const start = Math.max(0, Math.min(sparse.length-1, container.dataset.countWindowManual === "true" ? Number(container.dataset.countWindowStart) || 0 : autoStart));
      const nonzero = new Map(sparse.nonzero);
      buckets = Array.from({ length: Math.min(64,sparse.length-start) }, (_,offset)=>({index:start+offset,value:count.minimo+start+offset,count:nonzero.get(start+offset)||0}));
      html += `<p data-count-range="${sparse.length}">Ventana [${start}..${start+buckets.length-1}] de ${sparse.length} celdas. Las frecuencias no escritas valen cero.</p><label>Ir al indice de conteo <input data-count-window-index type="number" min="0" max="${sparse.length-1}" value="${start}"></label> <button type="button" data-count-window-follow>Seguir indice activo</button>`;
    }
    html += `<div class="sorting-buckets">${buckets.map((node) => `<div data-count-index="${node.index}" data-count-value="${node.value}"><strong>${sEscape(node.value)}</strong><span>${node.count}</span><small>frecuencia [${node.index}]</small></div>`).join("")}</div>`;
  } else if (algorithm === "counting_sort" || algorithm === "binsort") {
    const minimum = items.length ? Math.min(...items) : 0;
    html += `<div class="sorting-buckets">${auxiliary.map((count, index) => `<div><strong>${sEscape(minimum + index)}</strong><span>${sEscape(count)}</span><small>${algorithm === "binsort" ? "urna" : "frecuencia"}</small></div>`).join("") || (algorithm === "binsort" ? "Urnas aún no inicializadas." : "Frecuencias aún no inicializadas.")}</div>`;
  } else if (algorithm === "radixsort" && state.radix_context) {
    const radix = state.radix_context;
    html += '<p>Magnitudes uint32_t; máximo: ' + sEscape(radix.maximo ?? 'fuera de alcance') + '; exp: ' + sEscape(radix.exp ?? 'fuera de alcance') + '</p>';
    for (const [name, buffer] of Object.entries(radix.buffers)) {
      html += '<div class="sorting-radix-buffer" data-radix-buffer="' + name + '" data-live="' + buffer.live + '"><strong>' + sEscape(name) + ': uint32_t[' + buffer.capacity + '] — ' + sEscape(buffer.status) + '</strong><div>';
      if (buffer.live) html += (buffer.cells || []).map((value, index) => '<span data-radix-index="' + index + '" data-initialized="' + (value !== null) + '">[' + index + '] ' + sEscape(value === null ? 'sin inicializar' : value) + '</span>').join(' · ');
      else html += 'Reserva no disponible para lectura.';
      html += '</div></div>';
    }
    if (radix.counts) html += '<div data-radix-counts><strong>conteo: size_t[10]</strong> ' + radix.counts.map((value,index) => '[' + index + '] ' + sEscape(value)).join(' · ') + '</div>';
  } else {
    html += items.length ? cells(items) : "";
  }
  container.innerHTML = html;
  if (["counting_sort", "binsort"].includes(algorithm)) {
    container.onchange = (event) => {
      if (!event.target.matches("[data-count-window-index]")) return;
      container.dataset.countWindowManual = "true"; container.dataset.countWindowStart = event.target.value;
      renderSortingStrategy(state, container);
    };
    container.onclick = (event) => {
      if (!event.target.matches("[data-count-window-follow]")) return;
      container.dataset.countWindowManual = "false"; renderSortingStrategy(state, container);
    };
  }
}

function sHistoryFromSaved(entries) {
  const titles = { create_array: "Crear arreglo", generate_random_array: "Generar aleatorio", select_algorithm: "Seleccionar algoritmo", run: "Ejecutar" };
  return (Array.isArray(entries) ? entries : []).map((entry) => ({
    title: titles[entry.operation] || entry.operation,
    message: entry.operation === "run" ? `Ordenamiento ejecutado con ${entry.payload.algorithm_id}.` : JSON.stringify(entry.payload || {}),
  }));
}

function renderSortingHistory(entries, container, mainCode = "") {
  if (!container) {
    return;
  }
  const rows = entries.length
    ? entries.map((entry) => `<li><strong>${sEscape(entry.title)}</strong>: ${sEscape(entry.message)}</li>`).join("")
    : "<li>Sin acciones ejecutadas.</li>";
  const program = mainCode ? `<li class="didactic-main-item"><strong>Main reproducible</strong> · <a href="/help/source/sorting_array/main">Descargar main.c</a> · <a href="/help/source/sorting_array/source">C del TAD</a> · <a href="/help/source/sorting_array/header">Cabecera H</a><pre class="didactic-history-main">${sEscape(mainCode)}</pre><small>Compila main.c junto con tad_ordenamiento.c. Las llamadas calculan su salida; seleccion sin ejecución queda como comentario.</small></li>` : "";
  container.innerHTML = rows + program;
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
  const nextButton = sById("sorting-sim-next");
  const countingNavigation = sById("sorting-counting-navigation");
  const countingJump = sById("sorting-counting-jump");
  const stepNavigation = sById("sorting-step-navigation");
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

  let runPending = false;
  let trace = null;
  let history = sHistoryFromSaved(model.history);
  let consoleLines = [];
  let speedSetting = 0;
  let speedMultiplier = 1;
  let currentPedagogy = null;
  let currentAttemptState = null;
  let pendingPredictionIndex = null;
  let comparison = null;
  let practiceProgress = { attempts: 0, correct: 0, concepts: {} };
  try { practiceProgress = JSON.parse(window.sessionStorage.getItem("sorting-practice-progress") || "null") || practiceProgress; } catch (_error) { /* session-only fallback */ }

  const didacticOps = (model.didactic && model.didactic.operations) || {};

  function isStepByStepEnabled() {
    return !stepToggle || Boolean(stepToggle.checked);
  }

  function currentLearningLevel() {
    return "intermediate";
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
        ? variables.map((variable) => `<tr class="${variable.changed ? "is-changed" : ""}"><td>${sEscape(variable.name)}</td><td>${sEscape(variable.type)}</td><td>${sEscape(variable.initialized === false ? "sin inicializar" : variable.value)}</td><td>${sEscape(variable.meaning)}</td></tr>`).join("")
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
        ? `<strong>${sEscape(loop.kind)}</strong> · iteración ${sEscape(currentPedagogy.source?.function === "mezclar" && loop.iteration === null ? "sin contador ordinal" : loop.iteration)} · límites ${sEscape(JSON.stringify(loop.bounds))}${loop.exit ? " · salida del ciclo" : ""}`
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

  function renderCountingOutcome() {
    let badge = sById("sorting-counting-outcome");
    if (!badge) { badge=document.createElement("p");badge.id="sorting-counting-outcome";badge.setAttribute("role","status");status?.after(badge); }
    const failed = ["counting_sort", "binsort", "radixsort"].includes(trace?.operation_name) && trace.success === false;
    badge.hidden = !failed;
    if (failed) {
      badge.className="message error";
      badge.textContent=`${trace.error.label} Retorno C equivalente: ORDENAMIENTO_ERROR (0). Vista de la llamada fallida; estado aceptado e historial sin cambios.`;
      badge.dataset.simulated=String(Boolean(trace.error.simulated));
    }
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

  async function showPredictionForNext() {
    if (!practiceMode?.checked || !trace || !tracePlayer) return false;
    const nextIndex = tracePlayer.getCursor() + 1;
    const frame = (await tracePlayer.getStep(nextIndex))?.pedagogy;
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
    try { if (await showPredictionForNext()) return; }
    catch (error) { setMessage(error.message,false); return; }
    await tracePlayer?.step();
    setButtonsState();
  }

  async function answerPrediction(answer) {
    if (pendingPredictionIndex === null || !trace) return;
    const frame = (await tracePlayer.getStep(pendingPredictionIndex))?.pedagogy;
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
    ? window.CountingRuntime.createCompatiblePlayer({
      codeElement: codePanel,
      renderState: (state) => renderSortingVisualState(state, visualContainer),
      statusElement: status,
      counterElement: counter,
      retainDoneLines: true,
      onCursorChange: ({ cursor, step }) => {
        consoleLines = buildConsoleFromTrace(cursor);
        renderSortingConsole(consoleBox, consoleLines);
        const currentStep = step || (trace && Array.isArray(trace.steps) ? trace.steps[cursor] : null);
        if (currentStep?.state_after) {
          currentAttemptState = cursor < 0 ? currentStep.state_snapshot : currentStep.state_after;
          if (trace?.success !== false) model.visual_state = currentAttemptState;
        }
        renderCountingOutcome();
        if (trace?.trace_id) { try { window.sessionStorage.setItem("counting-cursor-"+trace.trace_id, String(cursor)); } catch (_error) { /* optional */ } }
        sEnhanceCodeNavigation(codePanel, functionList, hideComments, currentStep ? currentStep.line_index : null);
        renderPedagogy(currentStep ? currentStep.pedagogy : null);
        renderAnalysis(currentStep ? currentStep.state_after : model.visual_state);
        if (progress) {
          progress.max = String(window.CountingRuntime.total(trace));
          progress.value = String(Math.max(0, cursor + 1));
          progress.disabled = !trace;
        }
        if (progressLabel) {
          const phase = currentStep?.pedagogy?.phase?.label || "sin fase";
          const concept = currentStep?.pedagogy?.concept || "sin concepto";
          progressLabel.textContent = `Paso ${Math.max(0, cursor + 1)} · ${phase} · ${concept}`;
          if (announcer) announcer.textContent = `Paso ${Math.max(0, cursor + 1)}. ${phase}. ${concept}.`;
        }
        setButtonsState();
      },
    })
    : null;

  function setButtonsState() {
    const stepMode = isStepByStepEnabled();
    const hasTrace = Boolean(tracePlayer && tracePlayer.hasTrace());
    const atEnd = Boolean(tracePlayer && tracePlayer.isAtEnd());
    if (stepNavigation) stepNavigation.hidden = !stepMode;
    if (countingNavigation) countingNavigation.hidden = !stepMode || !hasTrace || !["counting_sort", "binsort", "radixsort"].includes(trace?.operation_name);
    if (countingJump) countingJump.max = String(tracePlayer?.getTotalSteps() || 0);
    if (stepButton) stepButton.hidden = false;
    if (speedSlider) {
      speedSlider.disabled = !stepMode;
    }
    if (prevButton) {
      prevButton.disabled = !stepMode || !hasTrace || tracePlayer.getCursor() < 0;
    }
    if (stepButton) {
      stepButton.disabled = false;
    }
    if (nextButton) nextButton.disabled = !stepMode || !hasTrace || atEnd;
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
      history = sHistoryFromSaved(data.history);
      model.main_c = data.main_c;
    renderSortingHistory(history, historyBox, model.main_c);
      tracePlayer?.clear("Arreglo creado. Ejecuta Reproducir.");
      renderSortingConsole(consoleBox, []);
      setButtonsState();
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
      history = sHistoryFromSaved(data.history);
      model.main_c = data.main_c;
    renderSortingHistory(history, historyBox, model.main_c);
      tracePlayer?.clear("Arreglo generado. Ejecuta Reproducir.");
      renderSortingConsole(consoleBox, []);
      setButtonsState();
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
    if (data.success) { history = sHistoryFromSaved(data.history); model.main_c = data.main_c;
      renderSortingHistory(history, historyBox, model.main_c); }
    trace = null;
    updateCodeByAlgorithm();
    tracePlayer?.clear("Algoritmo cambiado. Ejecuta Reproducir.");
    renderSortingConsole(consoleBox, []);
    setButtonsState();
  }

  async function runSorting(finalOnly, autoPlay = true) {
    if (runPending) return;
    runPending = true;
    try {
      const algorithmId = algorithmSelect ? algorithmSelect.value : "";
      const mode = finalOnly ? "fast" : "step_by_step";
      const data = await postJson(runUrl, { mode, algorithm_id: algorithmId });
      setMessage(data.message, Boolean(data.success));
      if (!data.success) {
        if (["counting_sort", "binsort", "radixsort"].includes(data.execution_trace?.operation_name) && tracePlayer) {
          model.visual_state = data.visual_state;
          model.main_c = data.main_c;
          trace = data.execution_trace;model.execution_trace=trace;
          try { window.sessionStorage.setItem("counting-step-mode-"+trace.trace_id,String(isStepByStepEnabled())); } catch (_error) { /* optional */ }
          tracePlayer.loadTrace(trace);
          if (finalOnly) await tracePlayer.seek(tracePlayer.getTotalSteps()-1);
          renderCountingOutcome();setButtonsState();
        }
        return;
      }
      history = sHistoryFromSaved(data.history);
      model.main_c = data.main_c;
    renderSortingHistory(history, historyBox, model.main_c);
      model.visual_state = data.visual_state;
      trace = data.execution_trace || null;
      model.execution_trace = trace;
      if (["counting_sort", "binsort", "radixsort"].includes(trace?.operation_name)) { try { window.sessionStorage.setItem("counting-step-mode-"+trace.trace_id,String(isStepByStepEnabled())); } catch (_error) { /* optional */ } }
      renderAnalysis(data.visual_state);
      if (finalOnly && ["intercambio", "seleccion", "insercion", "burbuja", "shell", "quicksort", "mergesort", "heapsort", "counting_sort", "binsort", "radixsort"].includes(algorithmId) && trace && tracePlayer) {
        tracePlayer.loadTrace(trace);
        await tracePlayer.seek(tracePlayer.getTotalSteps() - 1);
        setButtonsState();
        return;
      }
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
        setButtonsState();
        return;
      }
      tracePlayer.loadTrace(trace);
      sEnhanceCodeNavigation(codePanel, functionList, hideComments, null);
      if (autoPlay) await tracePlayer.playFromStart();
      setButtonsState();
    } finally {
      runPending = false;
    }
  }

  async function resetSorting() {
    if (!window.confirm("¿Restablecer los datos, el algoritmo y el historial de esta sesión?")) return;
    const data = await postJson(resetUrl, {});
    setMessage(data.message, Boolean(data.success));
    model.visual_state = data.visual_state;
    renderSortingVisualState(model.visual_state, visualContainer);
    history = [];
    model.main_c = data.main_c;
    renderSortingHistory(history, historyBox, model.main_c);
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

  let comparisonVersion = 0;
  async function renderComparisonCursor() {
    try {
    if (!comparison || !compareProgress) return;
    const cursor = Math.max(0, Number(compareProgress.value) - 1);
    const version = ++comparisonVersion;
    const ownedComparison = comparison;
    const leftTrace = ownedComparison.left.trace, rightTrace = ownedComparison.right.trace;
    const leftRaw = await window.CountingRuntime.frame(leftTrace, Math.min(cursor,window.CountingRuntime.total(leftTrace)-1));
    const concept = compareSync?.value === "concept" ? leftRaw?.pedagogy?.concept : null;
    const occurrence = concept ? (leftRaw.concept_occurrence || leftTrace.steps.slice(0,cursor+1).filter((step)=>step.pedagogy?.concept===concept).length) : 1;
    const leftStep = leftRaw;
    const rightStep = concept ? (await window.CountingRuntime.locate(rightTrace,concept,occurrence)) || await window.CountingRuntime.frame(rightTrace,Math.min(cursor,window.CountingRuntime.total(rightTrace)-1)) : await window.CountingRuntime.frame(rightTrace,Math.min(cursor,window.CountingRuntime.total(rightTrace)-1));
    if (version !== comparisonVersion || ownedComparison !== comparison) return;
    renderComparisonSide(comparison.left, leftStep, "sorting-compare-left-view", "sorting-compare-left-analysis", "sorting-compare-left-title");
    renderComparisonSide(comparison.right, rightStep, "sorting-compare-right-view", "sorting-compare-right-analysis", "sorting-compare-right-title");
    if (compareConclusion) {
      const leftMetrics = comparison.left.result.metrics;
      const rightMetrics = comparison.right.result.metrics;
      const fewer = leftMetrics.comparisons === rightMetrics.comparisons ? "Ambos realizaron igual número de comparaciones" : leftMetrics.comparisons < rightMetrics.comparisons ? `${comparison.left.algorithm} realizó menos comparaciones` : `${comparison.right.algorithm} realizó menos comparaciones`;
      compareConclusion.textContent = `${fewer} en esta entrada. Es una observación particular: una sola entrada no demuestra la complejidad general.`;
    }
    } catch (error) { setMessage(error.message,false); }
  }

  async function prepareComparison() {
    const frozenInput = manualInput?.value || (model.visual_state?.items || []).join(",");
    const data = await postJson(compareUrl, { values: frozenInput, left_algorithm: compareLeft?.value, right_algorithm: compareRight?.value });
    if (!data.success) { setMessage(data.message, false); return; }
    comparison = data;
    if (compareInput) compareInput.textContent = `Entrada inmutable: [${data.input.join(", ")}]`;
    compareProgress.disabled = false;
    compareProgress.min = "1";
    compareProgress.max = String(Math.max(window.CountingRuntime.total(data.left.trace), window.CountingRuntime.total(data.right.trace)));
    compareProgress.value = "1";
    renderComparisonCursor();
  }

  sById("sorting-counting-go")?.addEventListener("click", async () => { await tracePlayer?.seek(Number(countingJump.value)-1); setButtonsState(); });
  sById("sorting-counting-replay")?.addEventListener("click", async () => { await tracePlayer?.play(); setButtonsState(); });
  sById("sorting-counting-pause")?.addEventListener("click", () => { tracePlayer?.pause(); setButtonsState(); });
  createButton?.addEventListener("click", createArray);
  randomButton?.addEventListener("click", randomArray);
  algorithmSelect?.addEventListener("change", selectAlgorithm);
  playButton?.addEventListener("click", async () => {
    await runSorting(!isStepByStepEnabled(), false);
  });

  prepareButton?.addEventListener("click", async () => runSorting(false, false));
  pauseButton?.addEventListener("click", () => { tracePlayer?.pause(); setButtonsState(); });
  startButton?.addEventListener("click", () => { tracePlayer?.seek(-1); setButtonsState(); });
  endButton?.addEventListener("click", () => { if (tracePlayer) tracePlayer.seek(tracePlayer.getTotalSteps() - 1); setButtonsState(); });
  repeatButton?.addEventListener("click", async () => { if (!tracePlayer) return; await tracePlayer.seek(-1); await tracePlayer.play(); setButtonsState(); });
  restartExecutionButton?.addEventListener("click", () => { tracePlayer?.reset(); setButtonsState(); });
  stepButton?.addEventListener("click", () => {
    stepToggle.checked = !stepToggle.checked;
    stepToggle.dispatchEvent(new Event("change"));
  });

  nextButton?.addEventListener("click", async () => {
    if (!tracePlayer?.hasTrace()) return;
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
    if (["counting_sort", "binsort", "radixsort"].includes(trace?.operation_name)) { try { window.sessionStorage.setItem("counting-step-mode-"+trace.trace_id,String(isStepByStepEnabled())); } catch (_error) { /* optional */ } }
    stepButton.textContent = isStepByStepEnabled() ? "Cerrar paso a paso" : "Paso a paso";
    stepButton.setAttribute("aria-pressed", String(isStepByStepEnabled()));
    tracePlayer?.pause(true);
    if (tracePlayer?.hasTrace()) tracePlayer.seek(isStepByStepEnabled() ? -1 : tracePlayer.getTotalSteps() - 1);
    setButtonsState();
  });
  if (stepToggle) { stepToggle.checked = false; stepToggle.hidden = true; }
  prevButton.textContent = "Paso anterior";
  nextButton.textContent = "Siguiente paso";
  setButtonsState();
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
  exportSummary?.addEventListener("click", async () => {
    const summary = { schema: "sorting-learning-summary/v1", algorithm: algorithmSelect?.value, input: manualInput?.value, cursor: tracePlayer?.getCursor() ?? -1, total_steps: tracePlayer?.getTotalSteps() ?? 0, state: model.visual_state, theory: trace?.theory_profile || null, practice: practiceProgress, main_c: model.main_c };
    if (trace?.success === false) Object.assign(summary,{accepted_state:model.visual_state,attempt_state:currentAttemptState,success:false,error:trace.error,native_status:trace.native_status});
    if (window.CountingRuntime.isPaged(trace) || trace?.success === false && ["counting_sort", "binsort", "radixsort"].includes(trace?.operation_name)) {
      try {
        const response = await fetch(trace.export_url, { credentials:"same-origin", cache:"no-store" });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "No se pudo exportar Counting.");
        summary.counting_trace = data.compact_trace;
      } catch (error) { setMessage(error.message,false); return; }
    }
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
  renderSortingHistory(history, historyBox, model.main_c);
  renderSortingConsole(consoleBox, []);
  if (speedSlider) {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) speedSlider.value = "-2";
    setSpeed(speedSlider.value);
  }
  if (model.execution_trace) {
    trace = model.execution_trace;
    let savedCursor = -1;
    if (stepToggle) stepToggle.checked = model.execution_mode === "step_by_step";
    try {
      savedCursor = Number(window.sessionStorage.getItem("counting-cursor-"+trace.trace_id) ?? -1);
      const savedMode = window.sessionStorage.getItem("counting-step-mode-"+trace.trace_id);
      if (savedMode !== null && stepToggle) stepToggle.checked = savedMode === "true";
    } catch (_error) { /* optional */ }
    if (!isStepByStepEnabled()) savedCursor = window.CountingRuntime.total(trace)-1;
    tracePlayer?.loadTrace(trace);
    tracePlayer?.seek(savedCursor);
  }
  // Restored mode must expose the same caption and pressed state as a toggle.
  stepButton.textContent = isStepByStepEnabled() ? "Cerrar paso a paso" : "Paso a paso";
  stepButton.setAttribute("aria-pressed", String(isStepByStepEnabled()));
  setButtonsState();
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.SORTING_VIEW_MODEL) {
    initSortingPage(window.SORTING_VIEW_MODEL);
  }
});
