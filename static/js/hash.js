"use strict";

function hashById(id) {
  return document.getElementById(id);
}

function hashEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function hashToCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\", "\\\\")
    .replaceAll('"', '\\"')
    .replaceAll("\r", "")
    .replaceAll("\n", "\\n");
}

function hashDecodeCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\\\", "\u0000")
    .replaceAll("\\n", "\n")
    .replaceAll("\\t", "\t")
    .replaceAll('\\"', '"')
    .replaceAll("\\r", "")
    .replaceAll("\u0000", "\\");
}

function hashExtractPrintfMessagesFromLine(lineText) {
  const source = String(lineText || "");
  const regex = /printf\s*\(\s*"((?:\\.|[^"\\])*)"/g;
  const messages = [];
  let match = regex.exec(source);
  while (match) {
    const decoded = hashDecodeCStringLiteral(match[1]).replace(/\n+$/g, "").trim();
    if (decoded) {
      messages.push(decoded);
    }
    match = regex.exec(source);
  }
  return messages;
}

function hashHasPrintfFormatSpecifier(text) {
  return /%[-+0-9.#hljztL]*[diuoxXfFeEgGaAcsp]/.test(String(text || ""));
}

function hashNormalizeDidacticText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function hashPushUniqueConsoleLine(lines, line) {
  const normalized = hashNormalizeDidacticText(line);
  if (!normalized) {
    return;
  }
  if (lines.length && hashNormalizeDidacticText(lines[lines.length - 1]) === normalized) {
    return;
  }
  lines.push(line);
}

function hashBuildHistoryEntrySignature(entry) {
  if (!entry || typeof entry === "string") {
    return "";
  }
  const subroutine = hashNormalizeDidacticText(entry.subroutine);
  const payload = hashNormalizeDidacticText(entry.payload);
  const result = hashNormalizeDidacticText(entry.result);
  const operation = hashNormalizeDidacticText(entry.operation);
  return `${subroutine}|${payload}|${result}|${operation}`;
}

function hashPushUniqueHistoryEntry(history, entry) {
  if (!Array.isArray(history) || !entry) {
    return false;
  }
  const last = history.length ? history[history.length - 1] : null;
  if (hashBuildHistoryEntrySignature(last) === hashBuildHistoryEntrySignature(entry)) {
    return false;
  }
  history.push(entry);
  return true;
}

function renderHashPrintfConsole(consoleEl, lines, fallbackText) {
  if (!consoleEl) {
    return;
  }
  const safeLines = Array.isArray(lines) ? lines : [];
  const html = safeLines.length
    ? safeLines.map((line) => `<div class="console-line">${hashEscape(line)}</div>`).join("")
    : `<div class="console-line muted">${hashEscape(fallbackText || "(sin salida printf en esta ruta)")}</div>`;
  consoleEl.innerHTML = html;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function buildHashOperationInputs(operation, container) {
  container.innerHTML = "";
  if (!operation || !operation.inputs) {
    return;
  }

  operation.inputs.forEach((field) => {
    const wrap = document.createElement("div");
    const label = document.createElement("label");
    label.textContent = field.label;
    label.setAttribute("for", `hash-field-${field.name}`);

    const input = document.createElement("input");
    input.id = `hash-field-${field.name}`;
    input.name = field.name;
    input.type = field.type === "number" ? "number" : "text";
    input.required = field.required !== false;

    wrap.appendChild(label);
    wrap.appendChild(input);
    container.appendChild(wrap);
  });
}

function renderHashEntries(entries) {
  if (!Array.isArray(entries) || !entries.length) {
    return "<span class=\"hash-empty\">vacio</span>";
  }

  return entries
    .map((entry) => `<span class="hash-entry">(${hashEscape(entry.key)}: ${hashEscape(entry.value)})</span>`)
    .join("<span class=\"hash-sep\"> -> </span>");
}

function renderHashState(state, container) {
  if (!state || !container) {
    return;
  }

  const metadata = state.metadata || {};
  const buckets = Array.isArray(state.buckets) ? state.buckets : [];
  const resizeEvent = metadata.resize_event;

  let html = "<div class=\"viz-canvas\"><div class=\"viz-stage\">";
  html += `<div class="viz-meta"><strong>${hashEscape(state.title || "Tabla Hash")}</strong></div>`;
  html += (
    `<div class="viz-meta">Tamano: ${hashEscape(metadata.size || 0)} | ` +
    `Capacidad: ${hashEscape(metadata.capacity || 0)} | ` +
    `Factor de carga: ${hashEscape(metadata.load_factor ?? 0)} | ` +
    `Colisiones: ${hashEscape(metadata.collisions || 0)}</div>`
  );

  if (resizeEvent) {
    html += (
      "<p class=\"hash-resize-note\">Redimensionamiento detectado: " +
      `${hashEscape(resizeEvent.old_capacity)} -> ${hashEscape(resizeEvent.new_capacity)}.</p>`
    );
  }

  if (!buckets.length) {
    html += "<p class=\"viz-empty\">No hay buckets para mostrar.</p>";
  } else {
    html += "<div class=\"hash-buckets-wrap\">";
    buckets.forEach((bucket) => {
      const bucketClass = bucket.collisions > 0 ? "hash-bucket has-collision" : "hash-bucket";
      const collisionBadge = bucket.collisions > 0
        ? `<span class="hash-collision-badge">colisiones: ${hashEscape(bucket.collisions)}</span>`
        : "";
      html += `<div class="${bucketClass}">`;
      html += (
        `<div class="hash-bucket-head">` +
        `<span class="hash-bucket-index">[${hashEscape(bucket.index)}]</span>` +
        `<span class="hash-bucket-size">n=${hashEscape(bucket.size)}</span>` +
        `${collisionBadge}</div>`
      );
      html += `<div class="hash-bucket-body">${renderHashEntries(bucket.entries)}</div>`;
      html += "</div>";
    });
    html += "</div>";
  }

  if (state.last_operation && state.last_operation.message) {
    html += `<p class="viz-meta"><strong>Ultima operacion:</strong> ${hashEscape(state.last_operation.message)}</p>`;
  }

  html += "</div></div>";
  container.innerHTML = html;
}

function showHashMessage(text, success) {
  const box = hashById("hash-message-box");
  if (!box) {
    return;
  }
  box.textContent = text || "";
  box.className = success ? "message ok" : "message error";
}

function updateHashDidacticPanel(model, operationName) {
  const recordBox = hashById("tad-record");
  const pseudoTitle = hashById("op-pseudocode-title");
  const pseudoBox = hashById("op-pseudocode");
  if (!recordBox || !pseudoTitle || !pseudoBox) {
    return;
  }

  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const fallback = didactic.default_operation || "Seudocodigo no disponible para esta operacion.";
  const codeTitle = didactic.code_title || "Seudocodigo";
  const selectedOp = operationName || "";
  const selectedMeta = (model.operations || []).find((item) => item.name === selectedOp);
  const selectedLabel = selectedMeta ? selectedMeta.label : selectedOp;

  if (window.InterpreterRuntime) {
    window.InterpreterRuntime.renderCode(
      recordBox,
      didactic.record || "Estructura no documentada.",
      didactic.code_title || "Seudocodigo",
    );
  } else {
    recordBox.textContent = didactic.record || "Estructura no documentada.";
  }
  pseudoTitle.textContent = selectedLabel ? `${codeTitle}: ${selectedLabel}` : codeTitle;
  if (window.InterpreterRuntime) {
    window.InterpreterRuntime.renderCode(
      pseudoBox,
      opMap[selectedOp] || fallback,
      codeTitle,
    );
  } else {
    pseudoBox.textContent = opMap[selectedOp] || fallback;
  }
}

function summarizeHashPayload(payload) {
  if (!payload || typeof payload !== "object") {
    return "";
  }
  const parts = Object.entries(payload)
    .filter(([, value]) => String(value).trim() !== "")
    .map(([key, value]) => `${key}=${value}`);
  return parts.join(", ");
}

function extractHashSubroutineName(pseudoCode, fallback) {
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

function getHashSubroutineName(model, operationName, fallback) {
  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const pseudoCode = opMap[operationName] || "";
  return extractHashSubroutineName(pseudoCode, fallback || operationName || "Operacion");
}

function createHashHistoryEntry(subroutine, payloadText, resultText, operationName, payloadRaw) {
  return {
    subroutine: subroutine || "Operacion",
    payload: payloadText || "-",
    result: resultText || "-",
    operation: operationName || "",
    payloadRaw: payloadRaw && typeof payloadRaw === "object" ? { ...payloadRaw } : {},
  };
}

function hashMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const key = Object.prototype.hasOwnProperty.call(payload, "key") ? String(payload.key).trim() : "";
  const value = Object.prototype.hasOwnProperty.call(payload, "value") ? String(payload.value).trim() : "";
  const capacity = Object.prototype.hasOwnProperty.call(payload, "capacity") ? String(payload.capacity).trim() : "";

  if (entry.operation === "create_table") {
    return `th_inicializar(&tabla, ${capacity || "17"});`;
  }
  if (entry.operation === "insert") {
    return `bool ok_${index} = th_insertar(&tabla, ${key || "0"}, ${value || "0"});`;
  }
  if (entry.operation === "get") {
    return `int valor_${index} = 0; bool ok_${index} = th_buscar(&tabla, ${key || "0"}, &valor_${index});`;
  }
  if (entry.operation === "contains") {
    return `bool existe_${index} = th_contiene(&tabla, ${key || "0"});`;
  }
  if (entry.operation === "remove") {
    return `bool eliminado_${index} = th_eliminar(&tabla, ${key || "0"});`;
  }
  if (entry.operation === "keys" || entry.operation === "values" || entry.operation === "items") {
    return `char buffer_${index}[2048]; th_formatear(&tabla, buffer_${index}, sizeof(buffer_${index}));`;
  }
  if (entry.operation === "stats") {
    return `THEstadisticas stats_${index} = th_estadisticas(&tabla);`;
  }
  if (entry.operation === "clear") {
    return "th_vaciar(&tabla);";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function buildHashMainCode(history) {
  const lines = [];
  lines.push("int main(void) {");
  lines.push("    TablaHash tabla;");
  lines.push("    th_inicializar(&tabla, 17);");
  lines.push("");
  lines.push("    // Historial de ejecucion del usuario");
  history.forEach((entry, index) => {
    if (!entry || typeof entry === "string") {
      return;
    }
    lines.push(`    ${hashMainCallForEntry(entry, index + 1)}`);
    lines.push(`    printf("${hashToCStringLiteral(entry.result || "Operacion aplicada.")}\\n");`);
    lines.push(`    // ${entry.result || "Operacion aplicada."}`);
  });
  lines.push("    // Al finalizar el programa:");
  lines.push("    // th_destruir(&tabla);");
  lines.push("    return 0;");
  lines.push("}");
  return lines.join("\n");
}

function renderHashHistory(history, container, didactic) {
  if (!container) {
    return;
  }
  if (!history.length) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }
  const codeTitle = didactic && didactic.code_title ? String(didactic.code_title) : "";
  if (codeTitle.toLowerCase().includes("codigo c")) {
    const code = buildHashMainCode(history);
    const tmp = document.createElement("pre");
    if (window.InterpreterRuntime) {
      window.InterpreterRuntime.renderCode(tmp, code, codeTitle);
      container.innerHTML = (
        "<li class=\"didactic-history-item history-main-wrap\">" +
        "<div class=\"didactic-history-head\">Programa principal (main)</div>" +
        `<pre class="didactic-code didactic-history-main">${tmp.innerHTML}</pre>` +
        "</li>"
      );
      return;
    }
    container.innerHTML = (
      "<li class=\"didactic-history-item history-main-wrap\">" +
      "<div class=\"didactic-history-head\">Programa principal (main)</div>" +
      `<pre class="didactic-code didactic-history-main">${hashEscape(code)}</pre>` +
      "</li>"
    );
    return;
  }
  container.innerHTML = history.map((item, index) => {
    if (typeof item === "string") {
      return (
        "<li class=\"didactic-history-item\">" +
        `<div class="didactic-history-head">Paso ${index + 1}: Historial</div>` +
        `<div class="didactic-history-line"><span class="k">Salida:</span> ${hashEscape(item)}</div>` +
        "</li>"
      );
    }
    return (
      "<li class=\"didactic-history-item\">" +
      `<div class="didactic-history-head">Paso ${index + 1}: ${hashEscape(item.subroutine || "Operacion")}</div>` +
      `<div class="didactic-history-line"><span class="k">Entrada:</span> ${hashEscape(item.payload || "-")}</div>` +
      `<div class="didactic-history-line"><span class="k">Salida:</span> ${hashEscape(item.result || "-")}</div>` +
      "</li>"
    );
  }).join("");
}

function initHashPage(model) {
  const form = hashById("hash-operation-form");
  const operationSelect = hashById("hash-operation-select");
  const inputsContainer = hashById("hash-operation-inputs");
  const resetButton = hashById("hash-reset-button");
  const visualContainer = hashById("hash-visual-state");
  const historyBox = hashById("action-history");
  const simPlayButton = hashById("hash-sim-play");
  const simPrevButton = hashById("hash-sim-prev");
  const simStepButton = hashById("hash-sim-step");
  const stepToggle = hashById("hash-step-toggle");
  const simStatus = hashById("hash-sim-status");
  const printfConsole = hashById("hash-printf-console");

  if (!form || !operationSelect || !inputsContainer || !visualContainer) {
    return;
  }

  const operations = model.operations || [];
  let selected = operations[0] || null;
  let visualState = model.visual_state;
  const operationLabel = new Map(operations.map((op) => [op.name, op.label]));
  const actionHistory = [];
  const consoleState = {
    trace: null,
    fallbackMessage: "",
  };
  function collectHashPrintfLines(trace, cursor) {
    if (!trace || !Array.isArray(trace.steps) || cursor < 0) {
      return [];
    }
    const limit = Math.min(cursor, trace.steps.length - 1);
    const out = [];
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const messages = hashExtractPrintfMessagesFromLine(step.line_text);
      messages.forEach((msg) => {
        // Evita mostrar literales de formato sin resolver (ej. "%d", "%s").
        if (hashHasPrintfFormatSpecifier(msg)) {
          return;
        }
        hashPushUniqueConsoleLine(out, `[printf] ${msg}`);
      });
    }
    if (limit >= trace.steps.length - 1) {
      const finalMessage = String(trace.message || "").trim();
      if (finalMessage) {
        hashPushUniqueConsoleLine(out, `[printf] ${finalMessage}`);
      }
    }
    return out;
  }
  function refreshHashPrintfConsole(cursor) {
    const lines = collectHashPrintfLines(consoleState.trace, cursor);
    renderHashPrintfConsole(printfConsole, lines, consoleState.fallbackMessage || "(sin salida printf en esta ruta)");
  }
  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: hashById("op-pseudocode"),
      statusElement: simStatus,
      counterElement: hashById("hash-sim-counter"),
      renderState: (stateSnapshot) => {
        visualState = stateSnapshot;
        renderHashState(visualState, visualContainer);
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        refreshHashPrintfConsole(cursor);
      },
    })
    : null;
  let pendingExecution = false;
  let traceSelectionKey = "";

  operations.forEach((operation) => {
    const option = document.createElement("option");
    option.value = operation.name;
    option.textContent = operation.label;
    operationSelect.appendChild(option);
  });

  buildHashOperationInputs(selected, inputsContainer);
  updateHashDidacticPanel(model, selected ? selected.name : "");
  (model.history || []).forEach((step) => {
    const opName = String(step.operation || "");
    const label = operationLabel.get(opName) || opName;
    const subroutine = getHashSubroutineName(model, opName, label);
    const payloadText = summarizeHashPayload(step.payload || {});
    hashPushUniqueHistoryEntry(
      actionHistory,
      createHashHistoryEntry(subroutine, payloadText || "-", "Operacion aplicada.", opName, step.payload || {}),
    );
  });
  renderHashHistory(actionHistory, historyBox, model.didactic);
  renderHashState(visualState, visualContainer);
  refreshHashPrintfConsole(-1);

  function isCurrentSelectionValid() {
    const current = operations.find((item) => item.name === operationSelect.value);
    if (!current) {
      return false;
    }
    return current.inputs.every((field) => {
      const element = hashById(`hash-field-${field.name}`);
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
    if (simPlayButton) {
      simPlayButton.disabled = busy || !canExecute;
    }
    if (simPrevButton) {
      simPrevButton.disabled = busy || !stepMode || !hasTrace;
    }
    if (simStepButton) {
      simStepButton.disabled = busy || !stepMode || !canExecute;
    }
  }

  function invalidateTrace(message) {
    traceSelectionKey = "";
    consoleState.trace = null;
    consoleState.fallbackMessage = "";
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
    refreshHashPrintfConsole(-1);
    setSimulationButtonsEnabled();
  }

  function collectPayload(current) {
    const payload = {};
    current.inputs.forEach((field) => {
      const element = hashById(`hash-field-${field.name}`);
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
    if (resetButton) {
      resetButton.disabled = true;
    }
    try {
      showHashMessage("Ejecutando subrutina...", true);
      const response = await fetch(form.dataset.operateUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: current.name, payload }),
      });
      const data = await response.json();
      showHashMessage(data.message, Boolean(data.success));
      updateHashDidacticPanel(model, current.name);

      const finalOnly = Boolean(options && options.finalOnly);
      const hasExecutionTrace = Boolean(!finalOnly && data.execution_trace && tracePlayer);
      if (hasExecutionTrace) {
        consoleState.trace = data.execution_trace;
        consoleState.fallbackMessage = "";
        tracePlayer.loadTrace(data.execution_trace);
        traceSelectionKey = selectionKey;
      } else {
        consoleState.trace = null;
        consoleState.fallbackMessage = data.message || "(sin salida printf en esta ruta)";
        refreshHashPrintfConsole(-1);
        traceSelectionKey = "";
      }
      const payloadText = summarizeHashPayload(payload);
      const subroutine = getHashSubroutineName(model, current.name, current.label);
      hashPushUniqueHistoryEntry(
        actionHistory,
        createHashHistoryEntry(subroutine, payloadText || "-", data.message, current.name, payload),
      );
      renderHashHistory(actionHistory, historyBox, model.didactic);

      if (data.visual_state) {
        visualState = data.visual_state;
        model.visual_state = data.visual_state;
        if (!hasExecutionTrace) {
          renderHashState(visualState, visualContainer);
          if (simStatus && finalOnly) {
            simStatus.textContent = "Modo rapido: se aplico el resultado final de la operacion.";
          }
        }
      }
      return data;
    } catch (_error) {
      showHashMessage("No fue posible completar la operacion.", false);
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
    const current = operations.find((item) => item.name === operationSelect.value);
    if (!current) {
      showHashMessage("Debes seleccionar una operacion valida.", false);
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

  invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");

  operationSelect.addEventListener("change", () => {
    selected = operations.find((item) => item.name === operationSelect.value) || null;
    buildHashOperationInputs(selected, inputsContainer);
    updateHashDidacticPanel(model, selected ? selected.name : "");
    invalidateTrace("Operacion cambiada. Ejecuta nuevamente.");
  });

  inputsContainer.addEventListener("input", () => {
    invalidateTrace("Entradas cambiadas. Ejecuta nuevamente.");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!isStepByStepEnabled()) {
      const current = operations.find((item) => item.name === operationSelect.value);
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
    const response = await fetch(form.dataset.resetUrl, { method: "POST" });
    const data = await response.json();
    showHashMessage(data.message, Boolean(data.success));
    updateHashDidacticPanel(model, selected ? selected.name : "");
    actionHistory.length = 0;
    renderHashHistory(actionHistory, historyBox, model.didactic);
    if (data.visual_state) {
      visualState = data.visual_state;
      model.visual_state = data.visual_state;
      renderHashState(visualState, visualContainer);
    }
    invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
  });

  simPlayButton?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      const current = operations.find((item) => item.name === operationSelect.value);
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
  if (window.HASH_VIEW_MODEL) {
    initHashPage(window.HASH_VIEW_MODEL);
  }
});
