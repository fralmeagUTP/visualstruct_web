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

function createHashHistoryEntry(subroutine, payloadText, resultText) {
  return {
    subroutine: subroutine || "Operacion",
    payload: payloadText || "-",
    result: resultText || "-",
  };
}

function renderHashHistory(history, container) {
  if (!container) {
    return;
  }
  if (!history.length) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
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
  const simStatus = hashById("hash-sim-status");

  if (!form || !operationSelect || !inputsContainer || !visualContainer) {
    return;
  }

  const operations = model.operations || [];
  let selected = operations[0] || null;
  let visualState = model.visual_state;
  const operationLabel = new Map(operations.map((op) => [op.name, op.label]));
  const actionHistory = [];
  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: hashById("op-pseudocode"),
      statusElement: simStatus,
      counterElement: hashById("hash-sim-counter"),
      renderState: (stateSnapshot) => {
        visualState = stateSnapshot;
        renderHashState(visualState, visualContainer);
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
    actionHistory.push(createHashHistoryEntry(subroutine, payloadText || "-", "Operacion aplicada."));
  });
  renderHashHistory(actionHistory, historyBox);
  renderHashState(visualState, visualContainer);

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

  function setSimulationButtonsEnabled() {
    const hasTrace = Boolean(tracePlayer && tracePlayer.hasTrace());
    const busy = pendingExecution;
    const canExecute = isCurrentSelectionValid();
    if (simPlayButton) {
      simPlayButton.disabled = busy || !canExecute;
    }
    if (simPrevButton) {
      simPrevButton.disabled = busy || !hasTrace;
    }
    if (simStepButton) {
      simStepButton.disabled = busy || !canExecute;
    }
  }

  function invalidateTrace(message) {
    traceSelectionKey = "";
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
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

  async function executeOperationAndLoadTrace(current, payload, selectionKey) {
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

      const hasExecutionTrace = Boolean(data.execution_trace && tracePlayer);
      if (hasExecutionTrace) {
        tracePlayer.loadTrace(data.execution_trace);
        traceSelectionKey = selectionKey;
      } else {
        traceSelectionKey = "";
      }
      const payloadText = summarizeHashPayload(payload);
      const subroutine = getHashSubroutineName(model, current.name, current.label);
      actionHistory.push(createHashHistoryEntry(subroutine, payloadText || "-", data.message));
      renderHashHistory(actionHistory, historyBox);

      if (data.visual_state) {
        visualState = data.visual_state;
        model.visual_state = data.visual_state;
        if (!hasExecutionTrace) {
          renderHashState(visualState, visualContainer);
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
    renderHashHistory(actionHistory, historyBox);
    if (data.visual_state) {
      visualState = data.visual_state;
      model.visual_state = data.visual_state;
      renderHashState(visualState, visualContainer);
    }
    invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
  });

  simPlayButton?.addEventListener("click", async () => {
    const ready = await ensureTraceForCurrentSelection();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.playFromStart();
  });

  simPrevButton?.addEventListener("click", () => {
    tracePlayer?.prev();
  });

  simStepButton?.addEventListener("click", async () => {
    const ready = await ensureTraceForCurrentSelection();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.step();
  });

}

document.addEventListener("DOMContentLoaded", () => {
  if (window.HASH_VIEW_MODEL) {
    initHashPage(window.HASH_VIEW_MODEL);
  }
});
