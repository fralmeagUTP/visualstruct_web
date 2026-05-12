"use strict";

function gById(id) {
  return document.getElementById(id);
}

function gEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const G_C_KEYWORDS = new Set([
  "if", "else", "for", "while", "do", "switch", "case", "default", "break",
  "continue", "return", "sizeof", "typedef", "struct", "enum", "union",
  "static", "const", "volatile", "extern", "goto", "NULL", "true", "false",
]);

const G_C_TYPES = new Set([
  "void", "int", "bool", "float", "double", "char", "short", "long",
  "signed", "unsigned", "size_t",
]);

function gIsIdentStart(ch) {
  return /[A-Za-z_]/.test(ch);
}

function gIsIdentChar(ch) {
  return /[A-Za-z0-9_]/.test(ch);
}

function gNextNonSpaceChar(text, from) {
  let i = from;
  while (i < text.length && /\s/.test(text[i])) {
    i += 1;
  }
  return i < text.length ? text[i] : "";
}

function highlightGraphCLine(line, state) {
  const text = String(line || "");
  const out = [];
  let i = 0;
  const inState = { inBlockComment: Boolean(state && state.inBlockComment) };

  if (/^\s*#/.test(text)) {
    return { html: `<span class="code-directive">${gEscape(text)}</span>`, state: inState };
  }

  while (i < text.length) {
    const ch = text[i];
    const next = i + 1 < text.length ? text[i + 1] : "";

    if (inState.inBlockComment) {
      const end = text.indexOf("*/", i);
      if (end === -1) {
        out.push(`<span class="code-comment">${gEscape(text.slice(i))}</span>`);
        i = text.length;
        break;
      }
      out.push(`<span class="code-comment">${gEscape(text.slice(i, end + 2))}</span>`);
      i = end + 2;
      inState.inBlockComment = false;
      continue;
    }

    if (ch === "/" && next === "/") {
      out.push(`<span class="code-comment">${gEscape(text.slice(i))}</span>`);
      i = text.length;
      break;
    }

    if (ch === "/" && next === "*") {
      const end = text.indexOf("*/", i + 2);
      if (end === -1) {
        out.push(`<span class="code-comment">${gEscape(text.slice(i))}</span>`);
        inState.inBlockComment = true;
        i = text.length;
      } else {
        out.push(`<span class="code-comment">${gEscape(text.slice(i, end + 2))}</span>`);
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
      out.push(`<span class="code-string">${gEscape(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (/[0-9]/.test(ch)) {
      let j = i + 1;
      while (j < text.length && /[0-9A-Fa-fxXuUlL\.]/.test(text[j])) {
        j += 1;
      }
      out.push(`<span class="code-number">${gEscape(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (gIsIdentStart(ch)) {
      let j = i + 1;
      while (j < text.length && gIsIdentChar(text[j])) {
        j += 1;
      }
      const word = text.slice(i, j);
      let cls = "";
      if (G_C_TYPES.has(word)) {
        cls = "code-type";
      } else if (G_C_KEYWORDS.has(word)) {
        cls = "code-keyword";
      } else if (gNextNonSpaceChar(text, j) === "(") {
        cls = "code-function";
      }
      out.push(cls ? `<span class="${cls}">${gEscape(word)}</span>` : gEscape(word));
      i = j;
      continue;
    }

    if ("{}[]();,*".includes(ch)) {
      out.push(`<span class="code-punct">${gEscape(ch)}</span>`);
      i += 1;
      continue;
    }

    out.push(gEscape(ch));
    i += 1;
  }

  return { html: out.join(""), state: inState };
}

function buildGraphHighlightedCodeHtml(raw, codeTitle) {
  const lines = String(raw || "").replaceAll("\r\n", "\n").split("\n");
  if (String(codeTitle || "").toLowerCase().includes("codigo c")) {
    let state = { inBlockComment: false };
    return lines
      .map((line, index) => {
        const highlighted = highlightGraphCLine(line, state);
        state = highlighted.state;
        return `<span class="code-line" data-line="${index}">${highlighted.html || "&nbsp;"}</span>`;
      })
      .join("");
  }
  return lines
    .map((line, index) => `<span class="code-line" data-line="${index}">${gEscape(line) || "&nbsp;"}</span>`)
    .join("");
}

function renderGraphDidacticCode(preElement, code, codeTitle) {
  const raw = String(code || "");
  preElement.dataset.rawCode = raw;
  preElement.dataset.codeTitle = String(codeTitle || "");
  preElement.innerHTML = buildGraphHighlightedCodeHtml(raw, codeTitle);
}

function buildGraphInputs(operation, container, prefix) {
  container.innerHTML = "";
  if (!operation || !operation.inputs) {
    return;
  }

  operation.inputs.forEach((field) => {
    const wrap = document.createElement("div");
    const label = document.createElement("label");
    const inputId = `${prefix}-${field.name}`;

    label.textContent = field.label;
    label.setAttribute("for", inputId);

    let input;
    if (field.type === "select" && Array.isArray(field.options)) {
      input = document.createElement("select");
      field.options.forEach((opt) => {
        const option = document.createElement("option");
        option.value = opt.value;
        option.textContent = opt.label;
        input.appendChild(option);
      });
    } else {
      input = document.createElement("input");
      input.type = field.type === "number" ? "number" : "text";
      if (field.type === "number") {
        input.step = "any";
      }
    }

    input.id = inputId;
    input.name = field.name;
    input.required = field.required !== false;

    wrap.appendChild(label);
    wrap.appendChild(input);
    container.appendChild(wrap);
  });
}

function collectPayload(operation, prefix) {
  const payload = {};
  if (!operation || !operation.inputs) {
    return payload;
  }

  operation.inputs.forEach((field) => {
    const fieldInput = gById(`${prefix}-${field.name}`);
    payload[field.name] = fieldInput ? fieldInput.value : "";
  });
  return payload;
}

function addBidirectionalEdge(set, from, to) {
  set.add(`${from}->${to}`);
  set.add(`${to}->${from}`);
}

function findEdgeWeight(edges, from, to, directed) {
  const direct = edges.find((edge) => String(edge.source) === from && String(edge.target) === to);
  if (direct) {
    return direct.weight;
  }
  if (!directed) {
    const reverse = edges.find((edge) => String(edge.source) === to && String(edge.target) === from);
    if (reverse) {
      return reverse.weight;
    }
  }
  return "?";
}

function getDefaultHighlights(state) {
  const opName = state.last_operation && state.last_operation.name ? state.last_operation.name : "";
  const rawResult = state.last_result ? state.last_result.result : null;

  const highlights = {
    traversalNodes: new Set(),
    traversalOrder: new Map(),
    traversalEdges: new Set(),
    mstNodes: new Set(),
    mstEdges: new Set(),
  };

  if ((opName === "run_bfs" || opName === "run_dfs") && Array.isArray(rawResult)) {
    rawResult.forEach((value, index) => {
      const key = String(value);
      highlights.traversalNodes.add(key);
      highlights.traversalOrder.set(key, index + 1);
      if (index > 0) {
        addBidirectionalEdge(highlights.traversalEdges, String(rawResult[index - 1]), key);
      }
    });
  }

  if ((opName === "run_dijkstra" || opName === "run_bellman_ford") && rawResult && Array.isArray(rawResult.path)) {
    rawResult.path.forEach((value, index) => {
      const key = String(value);
      highlights.traversalNodes.add(key);
      highlights.traversalOrder.set(key, index + 1);
      if (index > 0) {
        addBidirectionalEdge(highlights.traversalEdges, String(rawResult.path[index - 1]), key);
      }
    });
  }

  if ((opName === "run_prim" || opName === "run_kruskal") && rawResult && Array.isArray(rawResult.mst_edges)) {
    rawResult.mst_edges.forEach((edge) => {
      if (!Array.isArray(edge) || edge.length < 2) {
        return;
      }
      const from = String(edge[0]);
      const to = String(edge[1]);
      highlights.mstNodes.add(from);
      highlights.mstNodes.add(to);
      addBidirectionalEdge(highlights.mstEdges, from, to);
    });
  }

  return highlights;
}

function getTraceDebugHighlights(traceDebug) {
  const highlights = {
    traversalNodes: new Set(),
    traversalOrder: new Map(),
    traversalEdges: new Set(),
    mstNodes: new Set(),
    mstEdges: new Set(),
  };
  if (!traceDebug || !traceDebug.graph_progress || typeof traceDebug.graph_progress !== "object") {
    return highlights;
  }

  const mode = String(traceDebug.graph_progress.mode || "");
  const nodes = Array.isArray(traceDebug.graph_progress.nodes) ? traceDebug.graph_progress.nodes : [];
  const edges = Array.isArray(traceDebug.graph_progress.edges) ? traceDebug.graph_progress.edges : [];

  if (mode === "mst") {
    nodes.forEach((node) => highlights.mstNodes.add(String(node)));
    edges.forEach((edge) => {
      if (!Array.isArray(edge) || edge.length < 2) {
        return;
      }
      addBidirectionalEdge(highlights.mstEdges, String(edge[0]), String(edge[1]));
    });
    return highlights;
  }

  nodes.forEach((node, index) => {
    const key = String(node);
    highlights.traversalNodes.add(key);
    if (!highlights.traversalOrder.has(key)) {
      highlights.traversalOrder.set(key, index + 1);
    }
  });
  edges.forEach((edge) => {
    if (!Array.isArray(edge) || edge.length < 2) {
      return;
    }
    addBidirectionalEdge(highlights.traversalEdges, String(edge[0]), String(edge[1]));
  });
  return highlights;
}

function buildSimulationFromState(state) {
  const opName = state.last_operation && state.last_operation.name ? state.last_operation.name : "";
  const result = state.last_result ? state.last_result.result : null;

  const simulation = {
    sourceOperation: opName,
    type: "",
    steps: [],
    index: -1,
    running: false,
    timer: null,
    speedMs: 900,
  };

  if ((opName === "run_bfs" || opName === "run_dfs") && Array.isArray(result)) {
    simulation.type = "traversal";
    result.forEach((value, index) => {
      const node = String(value);
      const step = {
        node,
        edge: index > 0 ? [String(result[index - 1]), node] : null,
        text: index === 0 ? `Inicio en ${node}` : `Avanzar a ${node}`,
      };
      simulation.steps.push(step);
    });
    return simulation;
  }

  if ((opName === "run_dijkstra" || opName === "run_bellman_ford") && result && Array.isArray(result.path)) {
    const path = result.path.map((value) => String(value));
    if (!path.length || result.reachable === false) {
      return simulation;
    }

    simulation.type = "shortest";
    simulation.steps.push({
      node: path[0],
      edge: null,
      text: `Inicio en ${path[0]}`,
    });

    for (let i = 1; i < path.length; i += 1) {
      const from = path[i - 1];
      const to = path[i];
      const weight = findEdgeWeight(state.edges || [], from, to, Boolean(state.directed));
      simulation.steps.push({
        node: to,
        edge: [from, to],
        text: `${from} - ${to} (peso ${weight})`,
      });
    }
    return simulation;
  }

  if ((opName === "run_prim" || opName === "run_kruskal") && result && Array.isArray(result.mst_edges)) {
    simulation.type = "mst";
    result.mst_edges.forEach((edge) => {
      if (!Array.isArray(edge) || edge.length < 3) {
        return;
      }
      simulation.steps.push({
        node: null,
        edge: [String(edge[0]), String(edge[1])],
        text: `${edge[0]} - ${edge[1]} (peso ${edge[2]})`,
      });
    });
    return simulation;
  }

  return simulation;
}

function getSimulationHighlights(simulation) {
  const highlights = {
    traversalNodes: new Set(),
    traversalOrder: new Map(),
    traversalEdges: new Set(),
    mstNodes: new Set(),
    mstEdges: new Set(),
  };

  if (!simulation || !Array.isArray(simulation.steps) || simulation.index < 0) {
    return highlights;
  }

  const maxIndex = Math.min(simulation.index, simulation.steps.length - 1);
  let orderCount = 0;

  for (let index = 0; index <= maxIndex; index += 1) {
    const step = simulation.steps[index];
    if (!step) {
      continue;
    }

    if ((simulation.type === "traversal" || simulation.type === "shortest") && step.node) {
      const node = String(step.node);
      highlights.traversalNodes.add(node);
      if (!highlights.traversalOrder.has(node)) {
        orderCount += 1;
        highlights.traversalOrder.set(node, orderCount);
      }
    }

    if ((simulation.type === "traversal" || simulation.type === "shortest") && Array.isArray(step.edge)) {
      addBidirectionalEdge(highlights.traversalEdges, String(step.edge[0]), String(step.edge[1]));
    }

    if (simulation.type === "mst" && Array.isArray(step.edge)) {
      const from = String(step.edge[0]);
      const to = String(step.edge[1]);
      highlights.mstNodes.add(from);
      highlights.mstNodes.add(to);
      addBidirectionalEdge(highlights.mstEdges, from, to);
    }
  }

  return highlights;
}

function renderGraphSvg(state, simulation, traceDebug) {
  const nodes = Array.isArray(state.nodes) ? state.nodes : [];
  const edges = Array.isArray(state.edges) ? state.edges : [];

  if (!nodes.length) {
    return "<p class=\"viz-empty\">Grafo vacio. Crea vertices para iniciar.</p>";
  }

  const nodeRadius = 26;
  const n = nodes.length;
  const width = Math.max(720, n * 140);
  const height = Math.max(360, n * 84);
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.max(90, Math.min(width, height) * 0.33);

  const positions = new Map();
  nodes.forEach((node, index) => {
    const angle = (2 * Math.PI * index) / n - Math.PI / 2;
    const x = cx + radius * Math.cos(angle);
    const y = cy + radius * Math.sin(angle);
    positions.set(String(node.id), { x, y, label: node.label });
  });

  const opName = state.last_operation && state.last_operation.name ? state.last_operation.name : "";
  const useSimulation = simulation && simulation.sourceOperation === opName;
  const highlights = traceDebug
    ? getTraceDebugHighlights(traceDebug)
    : useSimulation
      ? getSimulationHighlights(simulation)
      : getDefaultHighlights(state);

  let svg = "";
  svg += `<svg class=\"viz-graph-svg\" width=\"${width}\" height=\"${height}\" viewBox=\"0 0 ${width} ${height}\" xmlns=\"http://www.w3.org/2000/svg\">`;
  svg += "<defs>";
  svg += "<marker id=\"arrow-head\" markerWidth=\"10\" markerHeight=\"10\" refX=\"8\" refY=\"3\" orient=\"auto\" markerUnits=\"strokeWidth\">";
  svg += "<path d=\"M0,0 L0,6 L9,3 z\" class=\"viz-graph-arrowhead\" />";
  svg += "</marker>";
  svg += "</defs>";

  edges.forEach((edge, index) => {
    const source = positions.get(String(edge.source));
    const target = positions.get(String(edge.target));
    if (!source || !target) {
      return;
    }

    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const length = Math.hypot(dx, dy) || 1;
    const ux = dx / length;
    const uy = dy / length;

    const startX = source.x + ux * nodeRadius;
    const startY = source.y + uy * nodeRadius;
    const endX = target.x - ux * nodeRadius;
    const endY = target.y - uy * nodeRadius;

    const edgeKey = `${String(edge.source)}->${String(edge.target)}`;
    const isTraversalEdge = highlights.traversalEdges.has(edgeKey);
    const isMstEdge = highlights.mstEdges.has(edgeKey);
    const markerAttr = state.directed ? "marker-end=\"url(#arrow-head)\"" : "";
    const edgeClass = isMstEdge
      ? "viz-graph-edge mst"
      : isTraversalEdge
        ? "viz-graph-edge traversal"
        : "viz-graph-edge";
    svg += `<line x1=\"${startX}\" y1=\"${startY}\" x2=\"${endX}\" y2=\"${endY}\" class=\"${edgeClass}\" ${markerAttr} />`;

    const labelX = (startX + endX) / 2;
    const labelY = (startY + endY) / 2 - ((index % 2) * 8 + 8);
    svg += `<text x=\"${labelX}\" y=\"${labelY}\" text-anchor=\"middle\" class=\"viz-graph-weight\">${gEscape(edge.weight)}</text>`;
  });

  nodes.forEach((node) => {
    const pos = positions.get(String(node.id));
    if (!pos) {
      return;
    }

    const nodeId = String(node.id);
    const nodeClass = highlights.mstNodes.has(nodeId)
      ? "viz-graph-node mst"
      : highlights.traversalNodes.has(nodeId)
        ? "viz-graph-node traversal"
        : "viz-graph-node";
    svg += `<circle cx=\"${pos.x}\" cy=\"${pos.y}\" r=\"${nodeRadius}\" class=\"${nodeClass}\" />`;
    svg += `<text x=\"${pos.x}\" y=\"${pos.y + 5}\" text-anchor=\"middle\" class=\"viz-graph-label\">${gEscape(node.label)}</text>`;
    if (highlights.traversalOrder.has(nodeId)) {
      svg += `<text x=\"${pos.x + 19}\" y=\"${pos.y - 18}\" text-anchor=\"middle\" class=\"viz-graph-order\">${gEscape(highlights.traversalOrder.get(nodeId))}</text>`;
    }
  });

  svg += "</svg>";
  return svg;
}

function formatShortestPathResult(state, result, label) {
  const path = Array.isArray(result.path) ? result.path.map((item) => String(item)) : [];
  const edges = Array.isArray(state.edges) ? state.edges : [];

  if (!path.length || result.reachable === false) {
    return `<p><strong>${label}:</strong> No existe ruta entre inicio y destino.</p>`;
  }

  let html = `<p><strong>${label}:</strong></p>`;
  html += "<div class=\"viz-path-steps\">";
  for (let index = 0; index < path.length - 1; index += 1) {
    const from = path[index];
    const to = path[index + 1];
    const weight = findEdgeWeight(edges, from, to, Boolean(state.directed));
    html += `<p>${gEscape(from)} - ${gEscape(to)} (peso ${gEscape(weight)})</p>`;
  }
  html += "</div>";

  const totalWeight = result.distance_to_destination;
  const totalText = totalWeight === null || totalWeight === undefined ? "No disponible" : totalWeight;
  html += `<p><strong>Peso total:</strong> ${gEscape(totalText)}</p>`;
  return html;
}

function formatGraphResult(state) {
  const operationName = state.last_operation && state.last_operation.name ? state.last_operation.name : "";
  const result = state.last_result ? state.last_result.result : null;

  if (operationName === "run_dijkstra" && result && typeof result === "object") {
    return formatShortestPathResult(state, result, "Ruta minima (Dijkstra)");
  }

  if (operationName === "run_bellman_ford" && result && typeof result === "object") {
    if (result.has_negative_cycle) {
      return "<p><strong>Bellman-Ford:</strong> Se detecto ciclo negativo. No se garantiza ruta minima.</p>";
    }
    return formatShortestPathResult(state, result, "Ruta minima (Bellman-Ford)");
  }

  if ((operationName === "run_bfs" || operationName === "run_dfs") && Array.isArray(result)) {
    return `<p><strong>Recorrido:</strong> ${gEscape(result.join(" -> "))}</p>`;
  }

  if ((operationName === "run_prim" || operationName === "run_kruskal") && result && Array.isArray(result.mst_edges)) {
    const mstLabel = operationName === "run_prim" ? "MST por Prim" : "MST por Kruskal";
    let html = `<p><strong>${mstLabel}:</strong></p>`;
    html += "<div class=\"viz-path-steps\">";
    result.mst_edges.forEach((edge) => {
      if (!Array.isArray(edge) || edge.length < 3) {
        return;
      }
      html += `<p>${gEscape(edge[0])} - ${gEscape(edge[1])} (peso ${gEscape(edge[2])})</p>`;
    });
    html += "</div>";
    html += `<p><strong>Peso total:</strong> ${gEscape(result.total_weight)}</p>`;
    return html;
  }

  return `<p><strong>Resultado:</strong> ${gEscape(JSON.stringify(result))}</p>`;
}

function renderGraphState(state, container, simulation, traceDebug) {
  if (!state || !container) {
    return;
  }

  const metadata = state.metadata || {};
  const graphType = state.directed ? "Dirigido" : "No dirigido";
  const weighted = state.weighted ? "Si" : "No";

  let html = "";
  html += "<div class=\"viz-canvas\">";
  html += `<div class=\"viz-meta\"><strong>Grafo</strong> | Tipo: ${graphType} | Ponderado: ${weighted} | Vertices: ${metadata.vertices_count ?? 0} | Aristas: ${metadata.edges_count ?? 0}</div>`;
  html += `<div class=\"viz-stage\">${renderGraphSvg(state, simulation, traceDebug)}</div>`;

  if (state.last_result && state.last_result.result !== undefined) {
    html += `<div class=\"viz-traversals\">${formatGraphResult(state)}</div>`;
  }
  if (traceDebug && traceDebug.note) {
    html += `<p class="viz-sim-note">${gEscape(String(traceDebug.note))}</p>`;
  }

  html += "</div>";
  container.innerHTML = html;
}

function showGraphMessage(message, success) {
  const box = gById("graph-message-box");
  if (!box) {
    return;
  }
  box.textContent = message || "";
  box.className = success ? "message ok" : "message error";
}

function updateGraphDidacticPanel(model, operationName) {
  const recordBox = gById("tad-record");
  const pseudoTitle = gById("op-pseudocode-title");
  const pseudoBox = gById("op-pseudocode");
  if (!recordBox || !pseudoTitle || !pseudoBox) {
    return;
  }

  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const codeTitle = didactic.code_title || "Seudocodigo";
  const fallback = didactic.default_operation || "Seudocodigo no disponible para esta operacion.";
  const selectedOp = operationName || "";
  const selectedMeta = (model.operations || []).find((item) => item.name === selectedOp);
  const selectedLabel = selectedMeta ? selectedMeta.label : selectedOp;

  renderGraphDidacticCode(recordBox, didactic.record || "Estructura no documentada.", codeTitle);
  pseudoTitle.textContent = selectedLabel ? `${codeTitle}: ${selectedLabel}` : codeTitle;
  renderGraphDidacticCode(pseudoBox, opMap[selectedOp] || fallback, codeTitle);
}

function summarizeGraphPayload(payload) {
  if (!payload || typeof payload !== "object") {
    return "";
  }
  const parts = Object.entries(payload)
    .filter(([, value]) => String(value).trim() !== "")
    .map(([key, value]) => `${key}=${value}`);
  return parts.join(", ");
}

function extractGraphSubroutineName(pseudoCode, fallback) {
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

function getGraphSubroutineName(model, operationName, fallback) {
  const didactic = model && model.didactic ? model.didactic : {};
  const opMap = didactic.operations || {};
  const pseudoCode = opMap[operationName] || "";
  return extractGraphSubroutineName(pseudoCode, fallback || operationName || "Operacion");
}

function createGraphHistoryEntry(subroutine, payloadText, resultText, operationName, payloadRaw) {
  return {
    subroutine: subroutine || "Operacion",
    payload: payloadText || "-",
    result: resultText || "-",
    operation: operationName || "",
    payloadRaw: payloadRaw && typeof payloadRaw === "object" ? { ...payloadRaw } : {},
  };
}

function graphMainCallForEntry(entry, index) {
  const payload = entry && entry.payloadRaw && typeof entry.payloadRaw === "object" ? entry.payloadRaw : {};
  const directed = String(payload.directed || "").toLowerCase() === "true";
  const vertex = Object.prototype.hasOwnProperty.call(payload, "vertex") ? String(payload.vertex).trim() : "";
  const origin = Object.prototype.hasOwnProperty.call(payload, "origin") ? String(payload.origin).trim() : "";
  const target = Object.prototype.hasOwnProperty.call(payload, "target") ? String(payload.target).trim() : "";
  const weight = Object.prototype.hasOwnProperty.call(payload, "weight") ? String(payload.weight).trim() : "";
  const start = Object.prototype.hasOwnProperty.call(payload, "start") ? String(payload.start).trim() : "";
  const end = Object.prototype.hasOwnProperty.call(payload, "end") ? String(payload.end).trim() : "";

  if (entry.operation === "create_graph") {
    return `grafo_destruir(&grafo); dirigido = ${directed ? "true" : "false"}; grafo = grafo_crear(dirigido);`;
  }
  if (entry.operation === "insert_vertex") {
    return `GrafoEstado st_${index} = grafo_insertar_vertice(grafo, ${vertex || "0"});`;
  }
  if (entry.operation === "remove_vertex") {
    return `GrafoEstado st_${index} = grafo_eliminar_vertice(grafo, ${vertex || "0"});`;
  }
  if (entry.operation === "insert_edge") {
    return `GrafoEstado st_${index} = grafo_insertar_arista(grafo, ${origin || "0"}, ${target || "0"}, ${weight || "1"});`;
  }
  if (entry.operation === "remove_edge") {
    return `GrafoEstado st_${index} = grafo_eliminar_arista(grafo, ${origin || "0"}, ${target || "0"});`;
  }
  if (entry.operation === "exists_vertex") {
    return `bool existe_${index} = grafo_existe_vertice(grafo, ${vertex || "0"});`;
  }
  if (entry.operation === "exists_edge") {
    return `bool existe_${index} = grafo_existe_arista(grafo, ${origin || "0"}, ${target || "0"});`;
  }
  if (entry.operation === "neighbors") {
    return `int *vecinos_${index} = NULL; size_t cant_${index} = 0; GrafoEstado st_${index} = grafo_sucesores(grafo, ${vertex || "0"}, &vecinos_${index}, &cant_${index}); if (st_${index} == GRAFO_OK) { free(vecinos_${index}); }`;
  }
  if (entry.operation === "edge_weight") {
    return `int peso_${index} = 0; GrafoEstado st_${index} = grafo_obtener_peso(grafo, ${origin || "0"}, ${target || "0"}, &peso_${index});`;
  }
  if (entry.operation === "list_vertices") {
    return `int *vertices_${index} = NULL; size_t cant_${index} = 0; GrafoEstado st_${index} = grafo_obtener_vertices(grafo, &vertices_${index}, &cant_${index}); if (st_${index} == GRAFO_OK) { free(vertices_${index}); }`;
  }
  if (entry.operation === "list_edges") {
    return `GrafoArista *aristas_${index} = NULL; size_t cant_${index} = 0; GrafoEstado st_${index} = grafo_obtener_aristas(grafo, &aristas_${index}, &cant_${index}); if (st_${index} == GRAFO_OK) { free(aristas_${index}); }`;
  }
  if (entry.operation === "run_bfs") {
    return `GrafoRecorrido rec_${index} = grafo_bfs(grafo, ${start || "0"}); grafo_liberar_recorrido(&rec_${index});`;
  }
  if (entry.operation === "run_dfs") {
    return `GrafoRecorrido rec_${index} = grafo_dfs(grafo, ${start || "0"}); grafo_liberar_recorrido(&rec_${index});`;
  }
  if (entry.operation === "run_dijkstra") {
    return `GrafoCamino cam_${index} = grafo_dijkstra(grafo, ${start || "0"}, ${end || "0"}); grafo_liberar_camino(&cam_${index});`;
  }
  if (entry.operation === "run_bellman_ford") {
    return `GrafoCamino cam_${index} = grafo_bellman_ford(grafo, ${start || "0"}, ${end || "0"}); grafo_liberar_camino(&cam_${index});`;
  }
  if (entry.operation === "run_prim") {
    return `GrafoCamino mst_${index} = grafo_prim(grafo, ${start || "0"}); grafo_liberar_camino(&mst_${index});`;
  }
  if (entry.operation === "run_kruskal") {
    return `GrafoCamino mst_${index} = grafo_kruskal(grafo); grafo_liberar_camino(&mst_${index});`;
  }
  if (entry.operation === "clear_graph") {
    return "grafo_destruir(&grafo); grafo = grafo_crear(dirigido);";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function buildGraphMainCode(history) {
  const lines = [];
  lines.push("int main(void) {");
  lines.push("    bool dirigido = false;");
  lines.push("    Grafo *grafo = grafo_crear(dirigido);");
  lines.push("    if (grafo == NULL) { return 1; }");
  lines.push("");
  lines.push("    // Historial de ejecucion del usuario");
  history.forEach((entry, index) => {
    if (!entry || typeof entry === "string") {
      return;
    }
    lines.push(`    ${graphMainCallForEntry(entry, index + 1)}`);
    if (entry.result) {
      lines.push(`    // ${String(entry.result)}`);
    }
  });
  lines.push("    // Al finalizar el programa:");
  lines.push("    // grafo_destruir(&grafo);");
  lines.push("    return 0;");
  lines.push("}");
  return lines.join("\n");
}

function renderGraphHistory(history, container, didactic) {
  if (!container) {
    return;
  }
  if (!history.length) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }
  const codeTitle = didactic && didactic.code_title ? String(didactic.code_title) : "";
  if (codeTitle.toLowerCase().includes("codigo c")) {
    const code = buildGraphMainCode(history);
    const codeHtml = buildGraphHighlightedCodeHtml(code, codeTitle);
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
        `<div class="didactic-history-line"><span class="k">Salida:</span> ${gEscape(item)}</div>` +
        "</li>"
      );
    }
    return (
      "<li class=\"didactic-history-item\">" +
      `<div class="didactic-history-head">Paso ${index + 1}: ${gEscape(item.subroutine || "Operacion")}</div>` +
      `<div class="didactic-history-line"><span class="k">Entrada:</span> ${gEscape(item.payload || "-")}</div>` +
      `<div class="didactic-history-line"><span class="k">Salida:</span> ${gEscape(item.result || "-")}</div>` +
      "</li>"
    );
  }).join("");
}

function clearGraphMessage() {
  const box = gById("graph-message-box");
  if (!box) {
    return;
  }
  box.textContent = "";
  box.className = "message";
}

function showSimulationStatus(message) {
  const box = gById("graph-sim-status");
  if (!box) {
    return;
  }
  box.textContent = message || "";
}

function setSimulationControlsEnabled(enabled) {
  const play = gById("graph-sim-play");
  const prev = gById("graph-sim-prev");
  const step = gById("graph-sim-step");

  [play, prev, step].forEach((button) => {
    if (button) {
      button.disabled = !enabled;
    }
  });
}

function stopSimulationTimer(simulation) {
  if (simulation && simulation.timer) {
    clearInterval(simulation.timer);
    simulation.timer = null;
  }
  if (simulation) {
    simulation.running = false;
  }
}

function describeSimulationStep(simulation) {
  if (!simulation || simulation.index < 0 || simulation.index >= simulation.steps.length) {
    return "";
  }
  const step = simulation.steps[simulation.index];
  return `Paso ${simulation.index + 1}/${simulation.steps.length}: ${step.text}`;
}

async function executeGraphOperation(controls, operationName, payload) {
  const response = await fetch(controls.dataset.operateUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ operation: operationName, payload }),
  });
  return response.json();
}

function initGraphPage(model) {
  const controls = gById("graph-controls");
  const modeSelect = gById("graph-mode-select");
  const createButton = gById("graph-create-button");
  const operationSelect = gById("graph-operation-select");
  const operationInputs = gById("graph-operation-inputs");
  const algorithmSelect = gById("graph-algorithm-select");
  const algorithmInputs = gById("graph-algorithm-inputs");
  const runModeSelect = gById("graph-run-mode");
  const simSpeed = gById("graph-sim-speed");
  const simPlay = gById("graph-sim-play");
  const simPrev = gById("graph-sim-prev");
  const simStep = gById("graph-sim-step");
  const visualState = gById("graph-visual-state");
  const historyBox = gById("action-history");

  if (!controls || !visualState || !operationSelect || !algorithmSelect) {
    return;
  }

  const pageState = {
    graphState: model.visual_state,
    simulation: null,
    actionHistory: [],
    lastTraceOperation: "",
    pendingExecution: false,
    traceSelectionKey: "",
  };

  const allOperations = model.operations || [];
  const operationLabel = new Map(allOperations.map((op) => [op.name, op.label]));
  const operationList = allOperations.filter((op) => !op.name.startsWith("run_") && op.name !== "create_graph");
  const algorithmList = allOperations.filter((op) => op.name.startsWith("run_"));

  let selectedOperation = operationList[0] || null;
  let selectedAlgorithm = algorithmList[0] || null;

  operationList.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = item.label;
    operationSelect.appendChild(option);
  });

  algorithmList.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = item.label;
    algorithmSelect.appendChild(option);
  });

  buildGraphInputs(selectedOperation, operationInputs, "g-op-field");
  buildGraphInputs(selectedAlgorithm, algorithmInputs, "g-alg-field");
  updateGraphDidacticPanel(model, selectedOperation ? selectedOperation.name : "");
  (model.history || []).forEach((step) => {
    const opName = String(step.operation || "");
    const label = operationLabel.get(opName) || opName;
    const subroutine = getGraphSubroutineName(model, opName, label);
    const payloadText = summarizeGraphPayload(step.payload || {});
    pageState.actionHistory.push(
      createGraphHistoryEntry(
        subroutine,
        payloadText || "-",
        "Operacion aplicada.",
        opName,
        step.payload || {},
      ),
    );
  });
  renderGraphHistory(pageState.actionHistory, historyBox, model.didactic);
  renderGraphState(pageState.graphState, visualState, pageState.simulation);

  if (modeSelect) {
    modeSelect.value = pageState.graphState && pageState.graphState.directed ? "true" : "false";
  }
  const tracePlayer = window.InterpreterRuntime
    ? window.InterpreterRuntime.createTracePlayer({
      codeElement: gById("op-pseudocode"),
      statusElement: gById("graph-sim-status"),
      counterElement: gById("graph-sim-counter"),
      renderState: (stateSnapshot, stepMeta) => {
        pageState.graphState = stateSnapshot;
        pageState.simulation = buildSimulationFromState(stateSnapshot);
        renderGraphState(stateSnapshot, visualState, null, stepMeta ? stepMeta.debug : null);
      },
      defaultDelayMs: simSpeed ? Number(simSpeed.value) : 900,
    })
    : null;

  function getRunMode() {
    if (!runModeSelect) {
      return "operation";
    }
    return runModeSelect.value === "algorithm" ? "algorithm" : "operation";
  }

  function setRunMode(mode) {
    if (!runModeSelect) {
      return;
    }
    runModeSelect.value = mode === "algorithm" ? "algorithm" : "operation";
  }

  function setSimulationButtonsState() {
    const hasTrace = Boolean(tracePlayer && tracePlayer.hasTrace());
    const busy = Boolean(pageState.pendingExecution);
    const canExecute = canExecuteCurrentTarget();
    if (simPlay) {
      simPlay.disabled = busy || !canExecute;
    }
    if (simPrev) {
      simPrev.disabled = busy || !hasTrace;
    }
    if (simStep) {
      simStep.disabled = busy || !canExecute;
    }
  }

  function invalidateTrace(message) {
    pageState.traceSelectionKey = "";
    pageState.lastTraceOperation = "";
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
    setSimulationButtonsState();
  }

  function buildSelectionKey(mode, operationName, payload) {
    return `${mode}::${operationName}::${JSON.stringify(payload)}`;
  }

  function getTargetSelection() {
    const mode = getRunMode();
    if (mode === "algorithm") {
      if (!selectedAlgorithm) {
        return null;
      }
      return {
        mode,
        operation: selectedAlgorithm,
        payload: collectPayload(selectedAlgorithm, "g-alg-field"),
      };
    }
    if (!selectedOperation) {
      return null;
    }
    return {
      mode,
      operation: selectedOperation,
      payload: collectPayload(selectedOperation, "g-op-field"),
    };
  }

  function isTargetSelectionValid(target) {
    if (!target || !target.operation) {
      return false;
    }
    const prefix = target.mode === "algorithm" ? "g-alg-field" : "g-op-field";
    const fields = Array.isArray(target.operation.inputs) ? target.operation.inputs : [];
    return fields.every((field) => {
      const element = gById(`${prefix}-${field.name}`);
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

  function canExecuteCurrentTarget() {
    const target = getTargetSelection();
    return isTargetSelectionValid(target);
  }

  function refreshSimulationStatus() {
    if (tracePlayer && tracePlayer.hasTrace()) {
      setSimulationButtonsState();
      return;
    }
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      setSimulationButtonsState();
      showSimulationStatus("Usa Reproducir o Siguiente paso para ejecutar.");
      return;
    }
    setSimulationButtonsState();
    if (pageState.simulation.index < 0) {
      showSimulationStatus(`Simulacion lista: ${pageState.simulation.steps.length} pasos. Pulsa Reproducir o Siguiente paso.`);
      return;
    }
    showSimulationStatus(describeSimulationStep(pageState.simulation));
  }

  function repaint() {
    renderGraphState(pageState.graphState, visualState, pageState.simulation);
    refreshSimulationStatus();
  }

  async function executeTargetAndLoadTrace(target, selectionKey) {
    pageState.pendingExecution = true;
    setSimulationButtonsState();
    if (createButton) {
      createButton.disabled = true;
    }

    try {
      const operationName = target.operation.name;
      const payload = target.payload || {};
      const data = await executeGraphOperation(controls, operationName, payload);
      showGraphMessage(data.message, Boolean(data.success));
      updateGraphDidacticPanel(model, operationName);

      const payloadText = summarizeGraphPayload(payload);
      const label = operationLabel.get(operationName) || operationName;
      const subroutine = getGraphSubroutineName(model, operationName, label);
      pageState.actionHistory.push(
        createGraphHistoryEntry(
          subroutine,
          payloadText || "-",
          data.message,
          operationName,
          payload,
        ),
      );
      renderGraphHistory(pageState.actionHistory, historyBox, model.didactic);

      const hasExecutionTrace = Boolean(data.execution_trace && tracePlayer);
      if (hasExecutionTrace) {
        tracePlayer.loadTrace(data.execution_trace);
        pageState.lastTraceOperation = String(data.execution_trace.operation_name || "");
        pageState.traceSelectionKey = selectionKey;
      } else {
        pageState.lastTraceOperation = "";
        pageState.traceSelectionKey = "";
      }

      if (data.visual_state) {
        model.visual_state = data.visual_state;
        if (!hasExecutionTrace) {
          applyNewGraphState(data.visual_state);
        }
      }
      return data;
    } catch (_error) {
      showGraphMessage("No fue posible completar la operacion.", false);
      return null;
    } finally {
      pageState.pendingExecution = false;
      if (createButton) {
        createButton.disabled = false;
      }
      setSimulationButtonsState();
    }
  }

  async function ensureTraceForCurrentTarget() {
    const target = getTargetSelection();
    if (!target) {
      showSimulationStatus("Selecciona una accion valida.");
      return null;
    }
    const selectionKey = buildSelectionKey(target.mode, target.operation.name, target.payload);
    if (tracePlayer && tracePlayer.hasTrace() && pageState.traceSelectionKey === selectionKey) {
      return { target, selectionKey };
    }

    const data = await executeTargetAndLoadTrace(target, selectionKey);
    if (!data) {
      return null;
    }
    return { target, selectionKey };
  }

  function applyNewGraphState(newState) {
    stopSimulationTimer(pageState.simulation);
    pageState.graphState = newState;
    pageState.simulation = buildSimulationFromState(newState);
    repaint();
    if (modeSelect) {
      modeSelect.value = newState.directed ? "true" : "false";
    }
  }

  function stepForward() {
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      showSimulationStatus("No hay pasos disponibles para simular.");
      return false;
    }
    if (pageState.simulation.index >= pageState.simulation.steps.length - 1) {
      stopSimulationTimer(pageState.simulation);
      showSimulationStatus(`Simulacion completada en ${pageState.simulation.steps.length} pasos.`);
      return false;
    }

    pageState.simulation.index += 1;
    repaint();
    return true;
  }

  function startSimulation() {
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      showSimulationStatus("No se puede iniciar: ejecuta un algoritmo para generar una simulacion.");
      return;
    }

    stopSimulationTimer(pageState.simulation);
    pageState.simulation.running = true;

    const speed = simSpeed ? Number(simSpeed.value) : 900;
    pageState.simulation.speedMs = Number.isFinite(speed) && speed > 0 ? speed : 900;

    if (pageState.simulation.index >= pageState.simulation.steps.length - 1) {
      pageState.simulation.index = -1;
    }

    const advanced = stepForward();
    if (!advanced) {
      return;
    }

    pageState.simulation.timer = setInterval(() => {
      const moved = stepForward();
      if (!moved) {
        stopSimulationTimer(pageState.simulation);
      }
    }, pageState.simulation.speedMs);
  }

  function pauseSimulation() {
    if (!pageState.simulation) {
      return;
    }
    stopSimulationTimer(pageState.simulation);
    showSimulationStatus("Simulacion pausada.");
  }

  function resetSimulation() {
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      showSimulationStatus("No hay simulacion activa para reiniciar.");
      return;
    }
    stopSimulationTimer(pageState.simulation);
    pageState.simulation.index = -1;
    repaint();
  }

  operationSelect.addEventListener("change", () => {
    selectedOperation = operationList.find((op) => op.name === operationSelect.value) || null;
    buildGraphInputs(selectedOperation, operationInputs, "g-op-field");
    updateGraphDidacticPanel(model, selectedOperation ? selectedOperation.name : "");
    setRunMode("operation");
    invalidateTrace("Operacion cambiada. Ejecuta nuevamente.");
  });

  algorithmSelect.addEventListener("change", () => {
    selectedAlgorithm = algorithmList.find((op) => op.name === algorithmSelect.value) || null;
    buildGraphInputs(selectedAlgorithm, algorithmInputs, "g-alg-field");
    updateGraphDidacticPanel(model, selectedAlgorithm ? selectedAlgorithm.name : "");
    setRunMode("algorithm");
    invalidateTrace("Algoritmo cambiado. Ejecuta nuevamente.");
  });

  operationInputs?.addEventListener("input", () => {
    setRunMode("operation");
    invalidateTrace("Entradas de operacion cambiadas. Ejecuta nuevamente.");
  });

  algorithmInputs?.addEventListener("input", () => {
    setRunMode("algorithm");
    invalidateTrace("Entradas de algoritmo cambiadas. Ejecuta nuevamente.");
  });

  runModeSelect?.addEventListener("change", () => {
    invalidateTrace("Modo cambiado. Ejecuta nuevamente.");
  });

  createButton?.addEventListener("click", async () => {
    const directedValue = modeSelect ? modeSelect.value : "false";
    const data = await executeGraphOperation(controls, "create_graph", { directed: directedValue });
    showGraphMessage(data.message, Boolean(data.success));
    updateGraphDidacticPanel(model, "create_graph");
    if (data.execution_trace && tracePlayer) {
      tracePlayer.loadTrace(data.execution_trace);
      pageState.lastTraceOperation = String(data.execution_trace.operation_name || "");
      pageState.traceSelectionKey = "";
    }
    const createSubroutine = getGraphSubroutineName(model, "create_graph", "Crear/Recrear grafo");
    pageState.actionHistory.push(
      createGraphHistoryEntry(
        createSubroutine,
        `directed=${directedValue}`,
        data.message,
        "create_graph",
        { directed: directedValue },
      ),
    );
    renderGraphHistory(pageState.actionHistory, historyBox, model.didactic);
    if (data.visual_state) {
      model.visual_state = data.visual_state;
      applyNewGraphState(data.visual_state);
      showSimulationStatus("Tipo de grafo aplicado. Ahora construye el grafo.");
    }
    setSimulationButtonsState();
  });

  simStep?.addEventListener("click", async () => {
    const ready = await ensureTraceForCurrentTarget();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.step();
  });

  simPrev?.addEventListener("click", () => {
    tracePlayer?.prev();
  });

  simPlay?.addEventListener("click", async () => {
    const ready = await ensureTraceForCurrentTarget();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.playFromStart();
  });

  invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
  refreshSimulationStatus();
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.GRAPH_VIEW_MODEL) {
    initGraphPage(window.GRAPH_VIEW_MODEL);
  }
});
