"use strict";

function renderGraphPedagogy(frame,level){
  if(!frame)return;
  const summary=gById("graph-pedagogy-summary"),representation=gById("graph-representation-view"),aux=gById("graph-auxiliary-view"),traversal=gById("graph-traversal-view"),table=gById("graph-table-view"),relaxation=gById("graph-relaxation-view"),condition=gById("graph-condition-view"),invariant=gById("graph-invariant-view");
  if(summary)summary.innerHTML=`<strong>${gEscape(frame.phase?.label||frame.concept)}</strong>: ${gEscape(frame.narration?.[level]||frame.narration?.intermediate||"")}`;
  if(representation){const adjacency=frame.representation?.adjacency||{},degrees=frame.representation?.degrees||[];representation.innerHTML=`<p><strong>${frame.representation?.directed?"Arcos dirigidos (→)":"Aristas no dirigidas (—)"}</strong></p><ul>${Object.entries(adjacency).map(([vertex,items])=>`<li><code>${gEscape(vertex)}</code>: ${items.length?items.map((item)=>`${gEscape(item.vertex)}(${gEscape(item.weight)})`).join(", "):"∅"}</li>`).join("")}</ul><p>${degrees.map((item)=>frame.representation?.directed?`${gEscape(item.vertex)}: entrada ${item.in_degree}, salida ${item.out_degree}`:`${gEscape(item.vertex)}: grado ${item.degree}`).join(" · ")}</p><p>Reservados: ${frame.memory?.allocated?.length||0}; liberados: ${frame.memory?.freed?.length||0}; punteros colgantes: ${frame.memory?.dangling_references?.length||0}</p>`;}
  if(aux)aux.innerHTML=`<strong>${gEscape(frame.auxiliary?.kind||"—")}</strong><br>Contenido: <code>${gEscape(JSON.stringify(frame.auxiliary?.items||[]))}</code><br>Seleccionado: ${gEscape(frame.auxiliary?.selected??"—")} · Iteración: ${gEscape(frame.auxiliary?.iteration??"—")}`;
  if(traversal)traversal.innerHTML=`Árbol/bosque: <code>${gEscape(JSON.stringify(frame.traversal?.tree_edges||[]))}</code><br>Orden descubierto: <code>${gEscape(JSON.stringify(frame.traversal?.discovery_order||[]))}</code><br>Activo: ${gEscape(frame.traversal?.active??"—")}`;
  if(table)table.innerHTML=`<table><thead><tr><th>Vértice</th><th>Estado</th><th>Distancia</th><th>Predecesor</th><th>Iteración</th></tr></thead><tbody>${(frame.vertices||[]).map((item)=>`<tr><td>${gEscape(item.id)}</td><td>${gEscape(item.status)}</td><td>${gEscape(item.distance??"∞")}</td><td>${gEscape(item.predecessor??"—")}</td><td>${gEscape(frame.auxiliary?.iteration??"—")}</td></tr>`).join("")}</tbody></table>`;
  if(relaxation)relaxation.innerHTML=frame.relaxation?`<code>${gEscape(frame.relaxation.expression)}</code><br>${gEscape(frame.relaxation.old_distance??"∞")} &gt; ${gEscape(frame.relaxation.candidate??"∞")} ⇒ <strong>${frame.relaxation.success?"relajación exitosa":"sin cambio"}</strong><br>Nuevo valor: ${gEscape(frame.relaxation.new_distance??"∞")}; predecesor: ${gEscape(frame.relaxation.predecessor??"—")}`:"No se evalúa una relajación en este paso.";
  if(condition)condition.innerHTML=frame.condition?`<code>${gEscape(frame.condition.substituted)}</code> ⇒ <strong>${gEscape(frame.condition.result)}</strong><br>${gEscape(frame.condition.consequence)}`:`Arista activa: ${gEscape(frame.active_edge?`${frame.active_edge.from} → ${frame.active_edge.to} (peso ${frame.active_edge.weight})`:"—")}`;
  if(invariant)invariant.innerHTML=`<strong>${gEscape(frame.invariant?.symbol||"")} ${gEscape(frame.invariant?.name||"")}</strong><br>${gEscape(frame.invariant?.evidence||"")}`;
}

function enhanceGraphCodeNavigation(activeLine=null){const code=gById("op-pseudocode"),list=gById("graph-function-list"),hide=gById("graph-hide-comments");if(!code||!list)return;const raw=String(code.dataset.rawCode||code.textContent||"");const rows=raw.replaceAll("\r\n","\n").split("\n"),functions=[];rows.forEach((row,index)=>{const match=row.match(/^\s*(?:static\s+)?(?:void|bool|int|double|size_t|Grafo|Lista\w*)\s*\**\s*([A-Za-z_]\w*)\s*\(/);if(match&&!['if','for','while','switch'].includes(match[1]))functions.push({name:match[1],line:index});});let block=false;code.querySelectorAll(".code-line").forEach((node,index)=>{const value=String(rows[index]||"").trim(),starts=value.startsWith("/*");node.classList.toggle("is-code-comment",block||starts||value.startsWith("//")||value.startsWith("*"));if(starts&&!value.includes("*/"))block=true;if(block&&value.includes("*/"))block=false;});const active=[...functions].reverse().find((item)=>Number.isInteger(activeLine)&&item.line<=activeLine)||functions[0];list.innerHTML=functions.length?functions.map((item)=>`<li><button type="button" class="${active?.line===item.line?'is-active':''}" data-line="${item.line}">${gEscape(item.name)}</button></li>`).join(""):'<li>Sin funciones detectadas</li>';list.querySelectorAll("button").forEach((button)=>button.addEventListener("click",()=>code.querySelector(`.code-line[data-line="${button.dataset.line}"]`)?.scrollIntoView({block:"center"})));code.classList.toggle("hide-hier-comments",Boolean(hide?.checked));}

function initGraphResponsiveWorkspace(){const workspace=document.querySelector(".graph-primary-workspace"),tabs=[...document.querySelectorAll("[data-graph-tab]")];if(!workspace||!tabs.length)return;let saved="visual";try{saved=sessionStorage.getItem("graph-active-tab")||"visual";}catch(_error){/* optional */}const activate=(name)=>{const value=name==="code"?"code":"visual";workspace.dataset.activeTab=value;tabs.forEach((tab)=>{const active=tab.dataset.graphTab===value;tab.classList.toggle("is-active",active);tab.setAttribute("aria-selected",String(active));});try{sessionStorage.setItem("graph-active-tab",value);}catch(_error){/* optional */}};tabs.forEach((tab)=>tab.addEventListener("click",()=>activate(tab.dataset.graphTab)));activate(saved);}

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

function gToCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\", "\\\\")
    .replaceAll('"', '\\"')
    .replaceAll("\r", "")
    .replaceAll("\n", "\\n");
}

function gDecodeCStringLiteral(text) {
  return String(text || "")
    .replaceAll("\\\\", "\u0000")
    .replaceAll("\\n", "\n")
    .replaceAll("\\t", "\t")
    .replaceAll('\\"', '"')
    .replaceAll("\\r", "")
    .replaceAll("\u0000", "\\");
}

function gExtractPrintfMessagesFromLine(lineText) {
  const source = String(lineText || "");
  const regex = /printf\s*\(\s*"((?:\\.|[^"\\])*)"/g;
  const messages = [];
  let match = regex.exec(source);
  while (match) {
    const decoded = gDecodeCStringLiteral(match[1]).replace(/\n+$/g, "").trim();
    if (decoded) {
      messages.push(decoded);
    }
    match = regex.exec(source);
  }
  return messages;
}

function gHasPrintfFormatSpecifier(text) {
  return /%[-+0-9.#hljztL]*[diuoxXfFeEgGaAcsp]/.test(String(text || ""));
}

function gNormalizeDidacticText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function gPushUniqueConsoleLine(lines, line) {
  const normalized = gNormalizeDidacticText(line);
  if (!normalized) {
    return;
  }
  if (lines.length && gNormalizeDidacticText(lines[lines.length - 1]) === normalized) {
    return;
  }
  lines.push(line);
}

function gBuildHistoryEntrySignature(entry) {
  if (!entry || typeof entry === "string") {
    return "";
  }
  const subroutine = gNormalizeDidacticText(entry.subroutine);
  const payload = gNormalizeDidacticText(entry.payload);
  const result = gNormalizeDidacticText(entry.result);
  const operation = gNormalizeDidacticText(entry.operation);
  return `${subroutine}|${payload}|${result}|${operation}`;
}

function gPushUniqueHistoryEntry(history, entry) {
  if (!Array.isArray(history) || !entry) {
    return false;
  }
  const last = history.length ? history[history.length - 1] : null;
  if (gBuildHistoryEntrySignature(last) === gBuildHistoryEntrySignature(entry)) {
    return false;
  }
  history.push(entry);
  return true;
}

function renderGraphPrintfConsole(consoleEl, lines, fallbackText) {
  if (!consoleEl) {
    return;
  }
  const safeLines = Array.isArray(lines) ? lines : [];
  const html = safeLines.length
    ? safeLines.map((line) => `<div class="console-line">${gEscape(line)}</div>`).join("")
    : `<div class="console-line muted">${gEscape(fallbackText || "(sin salida printf en esta ruta)")}</div>`;
  consoleEl.innerHTML = html;
  consoleEl.scrollTop = consoleEl.scrollHeight;
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
    return "<p class=\"viz-empty\">Grafo vacío. Crea vértices para iniciar.</p>";
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
    return formatShortestPathResult(state, result, "Ruta mínima (Dijkstra)");
  }

  if (operationName === "run_bellman_ford" && result && typeof result === "object") {
    if (result.has_negative_cycle) {
      return "<p><strong>Bellman-Ford:</strong> Se detectó ciclo negativo. No se garantiza ruta mínima.</p>";
    }
    return formatShortestPathResult(state, result, "Ruta mínima (Bellman-Ford)");
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

  if (operationName === "generate_random_graph" && result && typeof result === "object") {
    const verticesCount = result.vertices_count ?? "-";
    const edgesCount = result.edges_count ?? "-";
    const seed = result.seed ?? "-";
    return (
      "<p><strong>Resultado:</strong> Grafo aleatorio generado correctamente.</p>" +
      "<div class=\"viz-path-steps\">" +
      `<p>Vertices creados: ${gEscape(verticesCount)}</p>` +
      `<p>Aristas generadas: ${gEscape(edgesCount)}</p>` +
      `<p>Semilla usada: ${gEscape(seed)}</p>` +
      "</div>"
    );
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
  html += `<div class=\"viz-meta\"><strong>Grafo</strong> | Tipo: ${graphType} | Ponderado: ${weighted} | Vértices: ${metadata.vertices_count ?? 0} | Aristas: ${metadata.edges_count ?? 0}</div>`;
  html += `<div class=\"viz-stage\"><div class="viz-stage-center">${renderGraphSvg(state, simulation, traceDebug)}</div></div>`;

  if (state.last_result && state.last_result.result !== undefined) {
    html += `<div class=\"viz-traversals\">${formatGraphResult(state)}</div>`;
  }
  if (traceDebug && traceDebug.note) {
    html += `<p class="viz-sim-note">${gEscape(String(traceDebug.note))}</p>`;
  }

  html += "</div>";
  container.innerHTML = html;
  centerGraphViewport(container);
}

function centerGraphViewport(container) {
  if (!container) {
    return;
  }
  const stage = container.querySelector(".viz-stage");
  if (!stage) {
    return;
  }
  window.requestAnimationFrame(() => {
    const stageWidth = Math.max(stage.scrollWidth, stage.clientWidth);
    const maxLeft = Math.max(0, stageWidth - container.clientWidth);
    container.scrollLeft = Math.round(maxLeft / 2);
    container.scrollTop = 0;
  });
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
  const fallback = didactic.default_operation || "Seudocódigo no disponible para esta operación.";
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
  return extractGraphSubroutineName(pseudoCode, fallback || operationName || "Operación");
}

function createGraphHistoryEntry(subroutine, payloadText, resultText, operationName, payloadRaw) {
  return {
    subroutine: subroutine || "Operación",
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
    return `/* TAD nuevo: reinicio del grafo (dirigido=${directed ? "true" : "false"} didáctico). */ g = grafo_crear();`;
  }
  if (entry.operation === "insert_vertex") {
    return `g = grafo_insertar_vertice(g, ${vertex || "0"});`;
  }
  if (entry.operation === "remove_vertex") {
    return `g = grafo_eliminar_vertice(g, ${vertex || "0"});`;
  }
  if (entry.operation === "insert_edge") {
    return `g = grafo_insertar_arco(g, ${origin || "0"}, ${target || "0"}, ${weight || "1"});`;
  }
  if (entry.operation === "remove_edge") {
    return `g = grafo_eliminar_arco(g, ${origin || "0"}, ${target || "0"});`;
  }
  if (entry.operation === "exists_vertex") {
    return `int existe_${index} = grafo_existe_vertice(g, ${vertex || "0"});`;
  }
  if (entry.operation === "exists_edge") {
    return `int existe_${index} = grafo_existe_arco(g, ${origin || "0"}, ${target || "0"});`;
  }
  if (entry.operation === "neighbors") {
    return `ListaVertice vecinos_${index} = grafo_sucesores(g, ${vertex || "0"});`;
  }
  if (entry.operation === "edge_weight") {
    return `int peso_${index} = grafo_costo_arco(g, ${origin || "0"}, ${target || "0"});`;
  }
  if (entry.operation === "list_vertices") {
    return `ListaVertice vertices_${index} = grafo_vertices(g);`;
  }
  if (entry.operation === "list_edges") {
    return `ListaArco arcos_${index} = grafo_arcos(g);`;
  }
  if (entry.operation === "run_bfs") {
    return `ListaVertice rec_${index} = grafo_bfs(g, ${start || "0"});`;
  }
  if (entry.operation === "run_dfs") {
    return `ListaVertice rec_${index} = grafo_dfs(g, ${start || "0"});`;
  }
  if (entry.operation === "run_dijkstra") {
    return `ListaArco camino_${index} = grafo_dijkstra(g, ${start || "0"}, ${end || "0"});`;
  }
  if (entry.operation === "run_bellman_ford") {
    return `ListaArco camino_${index} = grafo_bellman_ford(g, ${start || "0"}, ${end || "0"});`;
  }
  if (entry.operation === "run_prim") {
    return `ListaArco mst_${index} = grafo_prim(g, ${start || "0"});`;
  }
  if (entry.operation === "run_kruskal") {
    return `ListaArco mst_${index} = grafo_kruskal(g);`;
  }
  if (entry.operation === "clear_graph") {
    return "g = grafo_crear();";
  }
  return `${entry.subroutine || "Operación"}();`;
}

function buildGraphMainCode(history) {
  const lines = [];
  lines.push("int main(void) {");
  lines.push("    Grafo g = grafo_crear();");
  lines.push("");
  lines.push("    // Historial de ejecucion del usuario");
  history.forEach((entry, index) => {
    if (!entry || typeof entry === "string") {
      return;
    }
    lines.push(`    ${graphMainCallForEntry(entry, index + 1)}`);
    if (entry.result) {
      lines.push(`    printf("${gToCStringLiteral(String(entry.result))}\\n");`);
      lines.push(`    // ${String(entry.result)}`);
    }
  });
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
      `<div class="didactic-history-head">Paso ${index + 1}: ${gEscape(item.subroutine || "Operación")}</div>` +
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

function classifyGraphStepKind(stepMeta) {
  if (!stepMeta || typeof stepMeta !== "object") {
    return "Acción actual: -";
  }
  const lineText = String(stepMeta.line_text || "").trim().toLowerCase();
  if (!lineText) {
    return "Acción actual: -";
  }

  if (
    lineText.startsWith("if ")
    || lineText.startsWith("if(")
    || lineText.startsWith("else if")
    || lineText.startsWith("while ")
    || lineText.startsWith("while(")
    || lineText.startsWith("for ")
    || lineText.startsWith("for(")
    || lineText.startsWith("switch ")
    || lineText.startsWith("switch(")
    || lineText.startsWith("case ")
  ) {
    return "Acción actual: Evaluando condición";
  }

  return "Acción actual: Aplicando cambio";
}

function updateGraphStepKind(stepMeta) {
  const element = gById("graph-sim-step-kind");
  if (!element) {
    return;
  }
  element.textContent = classifyGraphStepKind(stepMeta);
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
  const operationRunButton = gById("graph-op-run");
  const algorithmSelect = gById("graph-algorithm-select");
  const algorithmInputs = gById("graph-algorithm-inputs");
  const runModeSelect = gById("graph-run-mode");
  const simPlay = gById("graph-sim-play");
  const simPrev = gById("graph-sim-prev");
  const simStep = gById("graph-sim-step");
  const simStatus = gById("graph-sim-status");
  const stepToggle = gById("graph-step-toggle");
  const speedSlider = gById("graph-speed-slider");
  const speedValue = gById("graph-speed-value");
  const visualState = gById("graph-visual-state");
  const historyBox = gById("action-history");
  const printfConsole = gById("graph-printf-console");
  const didacticNote = gById("graph-didactic-note");
  const presetButtons = Array.from(document.querySelectorAll(".graph-preset-btn"));
  const learningLevel=gById("graph-learning-level"),guidedExample=gById("graph-guided-example"),loadExample=gById("graph-load-example"),exampleLesson=gById("graph-example-lesson"),restartExecution=gById("graph-restart-execution"),resetGraph=gById("graph-reset-button"),hideComments=gById("graph-hide-comments");
  const prepareButton=gById("graph-prepare"),pauseButton=gById("graph-sim-pause"),homeButton=gById("graph-sim-home"),endButton=gById("graph-sim-end"),repeatButton=gById("graph-sim-repeat"),progressSlider=gById("graph-progress"),stepMetadata=gById("graph-step-metadata");
  const predictionSelect=gById("graph-prediction"),checkPrediction=gById("graph-check-prediction"),hintButton=gById("graph-prediction-hint"),skipPrediction=gById("graph-skip-prediction"),predictionFeedback=gById("graph-prediction-feedback"),practiceMode=gById("graph-practice-mode"),practiceCover=gById("graph-practice-cover"),progressSummary=gById("graph-progress-summary"),resetProgress=gById("graph-reset-progress");
  const compareKind=gById("graph-compare-kind"),compareStart=gById("graph-compare-start"),compareEnd=gById("graph-compare-end"),compareRun=gById("graph-compare-run"),compareProgress=gById("graph-compare-progress"),compareInput=gById("graph-compare-input"),compareGrid=gById("graph-compare-grid"),compareConclusion=gById("graph-compare-conclusion");
  const exportImage=gById("graph-export-image"),exportSummary=gById("graph-export-summary"),announcer=gById("graph-accessible-announcer");
  const activePhase = String(controls?.dataset.activePhase || "construccion").trim() || "construccion";

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
    consoleTrace: null,
    consoleFallbackMessage: "",
    traceCursor: -1,
    traceTotalSteps: 0,
    lockStepUntilInput: false,
    finalTraceDebug: null,
  };

  let playbackSpeed = 1;
  let playbackSpeedSetting = 0;
  let currentPedagogyFrame=null;
  let comparisonResult=null;let hintLevel=0;
  const conceptualProgress={attempts:0,correct:0};
  const presentationKey=`graph-presentation:${activePhase}`;
  function readGraphPresentation(){try{return JSON.parse(sessionStorage.getItem(presentationKey)||"{}");}catch(_error){return {};}}
  function writeGraphPresentation(){try{sessionStorage.setItem(presentationKey,JSON.stringify({level:learningLevel?.value||"intermediate",cursor:pageState.traceCursor,phase:activePhase,operation:selectedOperation?.name,algorithm:selectedAlgorithm?.name}));}catch(_error){/* optional */}}

  function isStepByStepEnabled() {
    return !stepToggle || Boolean(stepToggle.checked);
  }

  function updateStepModePanelVisibility() {
    const stepMode = isStepByStepEnabled();
    const actionRow = simPrev ? simPrev.closest(".graph-sim-actions") : null;
    const speedPanel = speedSlider ? speedSlider.closest(".sim-speed-control") : null;
    const heading = actionRow ? actionRow.previousElementSibling : null;
    const counter = gById("graph-sim-counter");
    const stepKind = gById("graph-sim-step-kind");
    [heading, actionRow, speedPanel, counter, stepKind].forEach((element) => {
      if (!element) {
        return;
      }
      element.style.display = stepMode ? "" : "none";
    });
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

  function collectGraphPrintfLines(trace, cursor) {
    if (!trace || !Array.isArray(trace.steps) || cursor < 0) {
      return [];
    }
    const limit = Math.min(cursor, trace.steps.length - 1);
    const out = [];
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const emitted = Array.isArray(step.console) ? step.console : [];
      emitted.forEach((line) => gPushUniqueConsoleLine(out, line));
    }
    return out;
  }

  function refreshGraphPrintfConsole(cursor) {
    const lines = collectGraphPrintfLines(pageState.consoleTrace, cursor);
    renderGraphPrintfConsole(
      printfConsole,
      lines,
      pageState.consoleFallbackMessage || "(sin salida printf en esta ruta)",
    );
  }

  function parseJsonArray(rawValue) {
    if (!rawValue) {
      return [];
    }
    try {
      const parsed = JSON.parse(String(rawValue));
      return Array.isArray(parsed) ? parsed.map((item) => String(item)) : [];
    } catch (_error) {
      return [];
    }
  }

  const allowedOperations = new Set(parseJsonArray(controls.dataset.allowedOperations));
  const allowedAlgorithms = new Set(parseJsonArray(controls.dataset.allowedAlgorithms));
  const phaseRunMode = String(controls.dataset.phaseRunMode || "operation").trim().toLowerCase();
  const defaultAlgorithm = String(controls.dataset.defaultAlgorithm || "").trim();
  const didacticNotesByPhase =
    window.GRAPH_DIDACTIC_NOTES && typeof window.GRAPH_DIDACTIC_NOTES === "object"
      ? window.GRAPH_DIDACTIC_NOTES
      : {};
  const fallbackDidacticNote = didacticNote ? String(didacticNote.textContent || "").trim() : "";

  const allOperations = model.operations || [];
  const operationLabel = new Map(allOperations.map((op) => [op.name, op.label]));
  const operationList = allOperations.filter(
    (op) =>
      !op.name.startsWith("run_") &&
      op.name !== "create_graph" &&
      (allowedOperations.size === 0 || allowedOperations.has(op.name)),
  );
  const algorithmList = allOperations.filter(
    (op) => op.name.startsWith("run_") && (allowedAlgorithms.size === 0 || allowedAlgorithms.has(op.name)),
  );

  let selectedOperation = operationList[0] || null;
  let selectedAlgorithm = algorithmList.find((op) => op.name === defaultAlgorithm) || algorithmList[0] || null;
  const savedPresentation=readGraphPresentation();if(learningLevel)learningLevel.value=["basic","intermediate","advanced"].includes(savedPresentation.level)?savedPresentation.level:"intermediate";(model.guided_examples||[]).forEach((example)=>{const option=document.createElement("option");option.value=example.id;option.textContent=example.label;guidedExample?.appendChild(option);});
  initGraphResponsiveWorkspace();hideComments?.addEventListener("change",()=>enhanceGraphCodeNavigation(null));learningLevel?.addEventListener("change",()=>{renderGraphPedagogy(currentPedagogyFrame,learningLevel.value);writeGraphPresentation();});guidedExample?.addEventListener("change",()=>{const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample.value);if(exampleLesson)exampleLesson.textContent=example?example.lesson:"El ejemplo se construye mediante operaciones públicas y no cambia al reproducir.";});
  let activeRunMode = phaseRunMode === "algorithm" ? "algorithm" : "operation";

  function resolveDidacticNote(operationName, mode) {
    const phaseNotes = didacticNotesByPhase[activePhase] || {};
    const operationBucket = mode === "algorithm"
      ? (phaseNotes.algorithms || {})
      : (phaseNotes.operations || {});
    if (operationName && Object.prototype.hasOwnProperty.call(operationBucket, operationName)) {
      return String(operationBucket[operationName] || "").trim();
    }
    if (typeof phaseNotes.default === "string" && phaseNotes.default.trim()) {
      return phaseNotes.default.trim();
    }
    return fallbackDidacticNote;
  }

  function refreshDidacticNote(operationName, mode) {
    if (!didacticNote) {
      return;
    }
    didacticNote.textContent = resolveDidacticNote(operationName, mode);
  }

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

  operationSelect.disabled = operationList.length === 0;
  algorithmSelect.disabled = algorithmList.length === 0;

  buildGraphInputs(selectedOperation, operationInputs, "g-op-field");
  buildGraphInputs(selectedAlgorithm, algorithmInputs, "g-alg-field");
  if (activeRunMode === "algorithm") {
    updateGraphDidacticPanel(model, selectedAlgorithm ? selectedAlgorithm.name : "");
    refreshDidacticNote(selectedAlgorithm ? selectedAlgorithm.name : "", "algorithm");
  } else {
    updateGraphDidacticPanel(model, selectedOperation ? selectedOperation.name : "");
    refreshDidacticNote(selectedOperation ? selectedOperation.name : "", "operation");
  }
  (model.history || []).forEach((step) => {
    const opName = String(step.operation || "");
    const label = operationLabel.get(opName) || opName;
    const subroutine = getGraphSubroutineName(model, opName, label);
    const payloadText = summarizeGraphPayload(step.payload || {});
    gPushUniqueHistoryEntry(
      pageState.actionHistory,
      createGraphHistoryEntry(
        subroutine,
        payloadText || "-",
        "Operación aplicada.",
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
        pageState.simulation = null;
        renderGraphState(stateSnapshot, visualState, null, stepMeta ? stepMeta.debug : null);
        if(stepMeta?.pedagogy){currentPedagogyFrame=stepMeta.pedagogy;renderGraphPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");}
        updateGraphStepKind(stepMeta || null);
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        pageState.traceCursor = cursor;
        pageState.traceTotalSteps = event && event.trace && Array.isArray(event.trace.steps)
          ? event.trace.steps.length
          : 0;
        refreshGraphPrintfConsole(cursor);
        const step=event?.step;enhanceGraphCodeNavigation(Number.isInteger(step?.line_index)?step.line_index:null);writeGraphPresentation();
        if(progressSlider){progressSlider.max=String(Math.max(0,pageState.traceTotalSteps-1));progressSlider.value=String(Math.max(0,cursor));progressSlider.disabled=pageState.traceTotalSteps===0;}
        if(stepMetadata){const frame=step?.pedagogy||{};const edge=frame.active_edge?`${frame.active_edge.from}→${frame.active_edge.to}`:"—";stepMetadata.textContent=`Función: ${frame.call_stack?.[0]?.function||"—"} · Fase: ${frame.phase?.label||"—"} · Concepto: ${frame.concept||"—"} · Vértice: ${frame.auxiliary?.selected??"—"} · Arista: ${edge}`;}
        const concealed=Boolean(practiceMode?.checked&&cursor>=0);if(practiceCover)practiceCover.hidden=!concealed;visualState.classList.toggle("graph-practice-hidden",concealed);
        if(announcer&&step?.pedagogy)announcer.textContent=`Paso ${cursor+1}. ${step.pedagogy.narration?.basic||step.pedagogy.phase?.label||""}`;
        setSimulationButtonsState();
      },
      defaultDelayMs: 900,
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

  function getRunMode() {
    if (!runModeSelect) {
      return activeRunMode;
    }
    return runModeSelect.value === "algorithm" ? "algorithm" : "operation";
  }

  function setRunMode(mode) {
    activeRunMode = mode === "algorithm" ? "algorithm" : "operation";
    if (!runModeSelect) {
      return;
    }
    runModeSelect.value = activeRunMode;
  }

  setRunMode(activeRunMode);

  function setSimulationButtonsState() {
    updateStepModePanelVisibility();
    const stepMode = isStepByStepEnabled();
    const hasTrace = Boolean(tracePlayer && tracePlayer.hasTrace());
    const busy = Boolean(pageState.pendingExecution);
    const canExecute = stepMode
      ? canExecuteCurrentTarget()
      : isTargetSelectionValid(resolveFastModeTarget());
    const canExecuteOperation = canExecuteSelectedOperation();
    const cursor = tracePlayer && typeof tracePlayer.getCursor === "function"
      ? tracePlayer.getCursor()
      : pageState.traceCursor;
    const total = tracePlayer && typeof tracePlayer.getTotalSteps === "function"
      ? tracePlayer.getTotalSteps()
      : pageState.traceTotalSteps;
    const atEnd = hasTrace && total > 0 && cursor >= total - 1;
    const hasProgress = hasTrace && cursor >= 0;
    if (simPlay) {
      simPlay.disabled = busy || !canExecute;
    }
    if (simPrev) {
      simPrev.disabled = busy || !stepMode || !hasProgress;
    }
    if (simStep) {
      simStep.disabled = busy || !stepMode || !canExecute || atEnd || pageState.lockStepUntilInput;
    }
    if (speedSlider) {
      speedSlider.disabled = busy || !stepMode;
    }
    if (operationRunButton) {
      operationRunButton.disabled = busy || !canExecuteOperation;
    }
  }

  function invalidateTrace(message) {
    pageState.finalTraceDebug = null;
    pageState.traceSelectionKey = "";
    pageState.lastTraceOperation = "";
    pageState.traceCursor = -1;
    pageState.traceTotalSteps = 0;
    pageState.lockStepUntilInput = false;
    pageState.consoleTrace = null;
    pageState.consoleFallbackMessage = "";
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
    updateGraphStepKind(null);
    refreshGraphPrintfConsole(-1);
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

  function resolveFastModeTarget() {
    let target = getTargetSelection();
    if (isTargetSelectionValid(target)) {
      return target;
    }

    if (activePhase !== "construccion" && selectedAlgorithm) {
      const algorithmTarget = {
        mode: "algorithm",
        operation: selectedAlgorithm,
        payload: collectPayload(selectedAlgorithm, "g-alg-field"),
      };
      if (isTargetSelectionValid(algorithmTarget)) {
        return algorithmTarget;
      }
    }

    if (selectedOperation) {
      const operationTarget = {
        mode: "operation",
        operation: selectedOperation,
        payload: collectPayload(selectedOperation, "g-op-field"),
      };
      if (isTargetSelectionValid(operationTarget)) {
        return operationTarget;
      }
    }
    return target;
  }

  function canExecuteSelectedOperation() {
    if (!selectedOperation) {
      return false;
    }
    const target = {
      mode: "operation",
      operation: selectedOperation,
      payload: collectPayload(selectedOperation, "g-op-field"),
    };
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
      showSimulationStatus(`Simulación lista: ${pageState.simulation.steps.length} pasos. Pulsa Reproducir o Siguiente paso.`);
      return;
    }
    showSimulationStatus(describeSimulationStep(pageState.simulation));
  }

  function pickAlgorithm(algorithmName) {
    if (!algorithmName) {
      return;
    }
    const found = algorithmList.find((op) => op.name === algorithmName);
    if (!found) {
      return;
    }
    selectedAlgorithm = found;
    if (algorithmSelect) {
      algorithmSelect.value = found.name;
    }
    buildGraphInputs(selectedAlgorithm, algorithmInputs, "g-alg-field");
    updateGraphDidacticPanel(model, selectedAlgorithm.name);
    setRunMode("algorithm");
    refreshDidacticNote(selectedAlgorithm.name, "algorithm");
    invalidateTrace("Algoritmo cambiado. Ejecuta nuevamente.");
  }

  function focusGraphSectionByHash() {
    const hash = String(window.location.hash || "").replace("#", "").trim().toLowerCase();
    if (!hash) {
      return;
    }

    if (hash === "builder") {
      setRunMode("operation");
      const target = gById("builder");
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    if (hash === "traversals") {
      pickAlgorithm("run_bfs");
      const target = gById("traversals");
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    if (hash === "shortest-path") {
      pickAlgorithm("run_dijkstra");
      const target = gById("traversals");
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    if (hash === "mst") {
      pickAlgorithm("run_prim");
      const target = gById("traversals");
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function repaint() {
    renderGraphState(pageState.graphState, visualState, pageState.simulation, pageState.finalTraceDebug);
    refreshSimulationStatus();
  }

  async function executeTargetAndLoadTrace(target, selectionKey, options) {
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
      refreshDidacticNote(operationName, target.mode);

      const payloadText = summarizeGraphPayload(payload);
      const label = operationLabel.get(operationName) || operationName;
      const subroutine = getGraphSubroutineName(model, operationName, label);
      gPushUniqueHistoryEntry(
        pageState.actionHistory,
        createGraphHistoryEntry(
          subroutine,
          payloadText || "-",
          data.message,
          operationName,
          payload,
        ),
      );
      renderGraphHistory(pageState.actionHistory, historyBox, model.didactic);

      const finalOnly = Boolean(options && options.finalOnly);
      const hasExecutionTrace = Boolean(!finalOnly && data.execution_trace && tracePlayer);
      if (hasExecutionTrace) {
        pageState.finalTraceDebug = null;
        pageState.lockStepUntilInput = false;
        pageState.consoleTrace = data.execution_trace;
        pageState.consoleFallbackMessage = "";
        tracePlayer.loadTrace(data.execution_trace);
        pageState.lastTraceOperation = String(data.execution_trace.operation_name || "");
        pageState.traceSelectionKey = selectionKey;
      } else {
        pageState.lastTraceOperation = "";
        pageState.traceSelectionKey = "";
        pageState.finalTraceDebug = null;
        if (finalOnly && data.execution_trace && Array.isArray(data.execution_trace.steps)) {
          pageState.consoleTrace = data.execution_trace;
          pageState.consoleFallbackMessage = data.message || "(sin salida printf en esta ruta)";
          const finalCursor = data.execution_trace.steps.length ? data.execution_trace.steps.length - 1 : -1;
          refreshGraphPrintfConsole(finalCursor);
          if (finalCursor >= 0) {
            const finalStep = data.execution_trace.steps[finalCursor] || null;
            if (finalStep && finalStep.debug) {
              pageState.finalTraceDebug = finalStep.debug;
            }
          }
        } else {
          pageState.consoleTrace = null;
          pageState.consoleFallbackMessage = data.message || "(sin salida printf en esta ruta)";
          refreshGraphPrintfConsole(-1);
        }
      }

      const finalVisualState = finalOnly
        ? resolveFinalGraphStateFromTrace(data.execution_trace, data.visual_state)
        : data.visual_state;
      if (finalVisualState) {
        model.visual_state = finalVisualState;
        if (!hasExecutionTrace) {
          applyNewGraphState(finalVisualState);
          if (simStatus && finalOnly) {
            simStatus.textContent = "Modo rapido: se aplico el resultado final de la operacion.";
          }
        }
      }
      return data;
    } catch (_error) {
      showGraphMessage("No fue posible completar la operación.", false);
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
      showSimulationStatus("Selecciona una acción válida.");
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
    pageState.simulation = null;
    updateGraphStepKind(null);
    repaint();
    if (modeSelect) {
      modeSelect.value = newState.directed ? "true" : "false";
    }
  }

  function resolveFinalGraphStateFromTrace(executionTrace, fallbackState) {
    if (!executionTrace || !Array.isArray(executionTrace.steps) || !executionTrace.steps.length) {
      return fallbackState;
    }
    let traceState = null;
    for (let index = executionTrace.steps.length - 1; index >= 0; index -= 1) {
      const step = executionTrace.steps[index] || {};
      if (step && step.state_after) {
        traceState = step.state_after;
        break;
      }
      if (step && step.state_snapshot) {
        traceState = step.state_snapshot;
        break;
      }
    }
    if (!traceState) {
      return fallbackState;
    }

    const merged = { ...(traceState || {}) };
    const fallback = fallbackState && typeof fallbackState === "object" ? fallbackState : null;

    // Preserve algorithm outcome metadata so final fast render highlights
    // traversal/path/MST exactly like trace-complete mode.
    if (!merged.last_result && fallback && fallback.last_result) {
      merged.last_result = fallback.last_result;
    }
    if (!merged.last_operation && fallback && fallback.last_operation) {
      merged.last_operation = fallback.last_operation;
    }
    if (!merged.metadata && fallback && fallback.metadata) {
      merged.metadata = fallback.metadata;
    }
    if (merged.directed === undefined && fallback && fallback.directed !== undefined) {
      merged.directed = fallback.directed;
    }
    if (merged.weighted === undefined && fallback && fallback.weighted !== undefined) {
      merged.weighted = fallback.weighted;
    }

    return merged;
  }

  function stepForward() {
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      showSimulationStatus("No hay pasos disponibles para simular.");
      return false;
    }
    if (pageState.simulation.index >= pageState.simulation.steps.length - 1) {
      stopSimulationTimer(pageState.simulation);
      showSimulationStatus(`Simulación completada en ${pageState.simulation.steps.length} pasos.`);
      return false;
    }

    pageState.simulation.index += 1;
    repaint();
    return true;
  }

  function startSimulation() {
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      showSimulationStatus("No se puede iniciar: ejecuta un algoritmo para generar una simulación.");
      return;
    }

    stopSimulationTimer(pageState.simulation);
    pageState.simulation.running = true;

    const speed = speedSlider ? Number(speedSlider.value) : 900;
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
    showSimulationStatus("Simulación pausada.");
  }

  function resetSimulation() {
    if (!pageState.simulation || !pageState.simulation.steps.length) {
      showSimulationStatus("No hay simulación activa para reiniciar.");
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
    refreshDidacticNote(selectedOperation ? selectedOperation.name : "", "operation");
    invalidateTrace("Operación cambiada. Ejecuta nuevamente.");
  });

  algorithmSelect.addEventListener("change", () => {
    selectedAlgorithm = algorithmList.find((op) => op.name === algorithmSelect.value) || null;
    buildGraphInputs(selectedAlgorithm, algorithmInputs, "g-alg-field");
    updateGraphDidacticPanel(model, selectedAlgorithm ? selectedAlgorithm.name : "");
    setRunMode("algorithm");
    refreshDidacticNote(selectedAlgorithm ? selectedAlgorithm.name : "", "algorithm");
    invalidateTrace("Algoritmo cambiado. Ejecuta nuevamente.");
  });

  presetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const algorithmName = String(button.getAttribute("data-graph-algorithm") || "").trim();
      const anchor = String(button.getAttribute("data-graph-anchor") || "").trim();
      pickAlgorithm(algorithmName);
      if (anchor) {
        window.location.hash = anchor;
      }
    });
  });

  operationInputs?.addEventListener("input", () => {
    setRunMode("operation");
    invalidateTrace("Entradas de operación cambiadas. Ejecuta nuevamente.");
  });

  algorithmInputs?.addEventListener("input", () => {
    setRunMode("algorithm");
    invalidateTrace("Entradas de algoritmo cambiadas. Ejecuta nuevamente.");
  });

  runModeSelect?.addEventListener("change", () => {
    activeRunMode = runModeSelect.value === "algorithm" ? "algorithm" : "operation";
    if (activeRunMode === "algorithm") {
      refreshDidacticNote(selectedAlgorithm ? selectedAlgorithm.name : "", "algorithm");
    } else {
      refreshDidacticNote(selectedOperation ? selectedOperation.name : "", "operation");
    }
    invalidateTrace("Modo cambiado. Ejecuta nuevamente.");
  });

  restartExecution?.addEventListener("click",()=>{tracePlayer?.reset();setSimulationButtonsState();});
  resetGraph?.addEventListener("click",async()=>{if(!window.confirm("¿Restablecer el grafo y borrar su historial de esta sesión?"))return;const response=await fetch(controls.dataset.resetUrl,{method:"POST"});const data=await response.json();pageState.actionHistory.length=0;renderGraphHistory(pageState.actionHistory,historyBox,model.didactic);if(data.visual_state){model.visual_state=data.visual_state;applyNewGraphState(data.visual_state);}invalidateTrace("Grafo restablecido.");showGraphMessage(data.message,Boolean(data.success));});
  loadExample?.addEventListener("click",async()=>{const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample?.value);if(!example){showGraphMessage("Selecciona un ejemplo guiado.",false);return;}loadExample.disabled=true;try{const labelMap=new Map((example.vertices||[]).map((value,index)=>[String(value),index+1]));const resolve=(value)=>labelMap.get(String(value))??value;let data=await executeGraphOperation(controls,"create_graph",{directed:Boolean(example.directed)});if(!data.success)throw new Error(data.message);for(const vertex of example.vertices||[]){data=await executeGraphOperation(controls,"insert_vertex",{vertex:resolve(vertex)});if(!data.success)throw new Error(data.message);}for(const edge of example.edges||[]){data=await executeGraphOperation(controls,"insert_edge",{origin:resolve(edge[0]),target:resolve(edge[1]),weight:edge[2]});if(!data.success)throw new Error(data.message);}if(data.visual_state){model.visual_state=data.visual_state;applyNewGraphState(data.visual_state);}const mappedPayload={};Object.entries(example.payload||{}).forEach(([key,value])=>{mappedPayload[key]=resolve(value);});selectedAlgorithm=algorithmList.find((item)=>item.name===example.operation)||selectedAlgorithm;if(selectedAlgorithm){algorithmSelect.value=selectedAlgorithm.name;buildGraphInputs(selectedAlgorithm,algorithmInputs,"g-alg-field");selectedAlgorithm.inputs.forEach((field)=>{const input=gById(`g-alg-field-${field.name}`);if(input&&Object.prototype.hasOwnProperty.call(mappedPayload,field.name))input.value=mappedPayload[field.name];});setRunMode("algorithm");updateGraphDidacticPanel(model,selectedAlgorithm.name);}pageState.actionHistory.length=0;invalidateTrace("Ejemplo preparado. Reproduce la operación objetivo.");writeGraphPresentation();showGraphMessage(`Ejemplo preparado: ${example.lesson}`,true);}catch(error){showGraphMessage(error.message||"No se pudo preparar el ejemplo.",false);}finally{loadExample.disabled=false;}});

  createButton?.addEventListener("click", async () => {
    const directedValue = modeSelect ? modeSelect.value : "false";
      const data = await executeGraphOperation(controls, "create_graph", { directed: directedValue });
    showGraphMessage(data.message, Boolean(data.success));
    updateGraphDidacticPanel(model, "create_graph");
    refreshDidacticNote("create_graph", "operation");
    if (isStepByStepEnabled() && data.execution_trace && tracePlayer) {
      pageState.lockStepUntilInput = false;
      pageState.consoleTrace = data.execution_trace;
      pageState.consoleFallbackMessage = "";
      tracePlayer.loadTrace(data.execution_trace);
      pageState.lastTraceOperation = String(data.execution_trace.operation_name || "");
      pageState.traceSelectionKey = "";
    } else {
      pageState.consoleTrace = null;
      pageState.consoleFallbackMessage = data.message || "(sin salida printf en esta ruta)";
      refreshGraphPrintfConsole(-1);
    }
    const createSubroutine = getGraphSubroutineName(model, "create_graph", "Crear/Recrear grafo");
    gPushUniqueHistoryEntry(
      pageState.actionHistory,
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

  operationRunButton?.addEventListener("click", async () => {
    if (!selectedOperation) {
      showSimulationStatus("Selecciona una operación válida.");
      return;
    }
    setRunMode("operation");
    const target = {
      mode: "operation",
      operation: selectedOperation,
      payload: collectPayload(selectedOperation, "g-op-field"),
    };
    if (!isTargetSelectionValid(target)) {
      showSimulationStatus("Completa los campos de la operación.");
      setSimulationButtonsState();
      return;
    }
    const selectionKey = buildSelectionKey(target.mode, target.operation.name, target.payload);
    const data = await executeTargetAndLoadTrace(
      target,
      selectionKey,
      !isStepByStepEnabled() ? { finalOnly: true } : undefined,
    );
    if (!data || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.playFromStart();
  });

  function renderConceptualProgress(){if(progressSummary)progressSummary.textContent=`Progreso conceptual de esta sesión: ${conceptualProgress.correct} aciertos de ${conceptualProgress.attempts} intentos.`;}
  function revealPractice(){if(practiceCover)practiceCover.hidden=true;visualState.classList.remove("graph-practice-hidden");}
  function expectedGraphPrediction(frame){const concept=String(frame?.concept||"");const stage=String(frame?.case||"");if(concept==="extract"||stage==="extract_min")return "extract";if(concept==="discover"||stage==="visit")return "discover";if(stage==="update_distance")return "predecessor";if(concept==="relax"||stage==="relax_edge")return frame?.relaxation?.success===false?"none":"relax";if(concept==="accept"||["accept_edge","union","expand_mst"].includes(stage))return "accept";if(concept==="reject"||stage==="reject_edge")return "reject";if(concept==="negative_cycle"||stage==="detect_negative_cycle")return "negative_cycle";return "none";}
  checkPrediction?.addEventListener("click",()=>{if(!currentPedagogyFrame||!predictionSelect?.value){if(predictionFeedback)predictionFeedback.textContent="Prepara una traza y selecciona una predicción.";return;}const expected=expectedGraphPrediction(currentPedagogyFrame),correct=predictionSelect.value===expected;conceptualProgress.attempts+=1;if(correct)conceptualProgress.correct+=1;renderConceptualProgress();if(predictionFeedback)predictionFeedback.textContent=correct?"Correcto: coincide con la decisión ejecutada.":`Revisa el auxiliar, la condición y el invariante. Evidencia: ${expected}.`;hintLevel=0;revealPractice();});
  hintButton?.addEventListener("click",()=>{hintLevel=Math.min(3,hintLevel+1);const hints=["Observa qué estructura auxiliar cambia.",`El concepto del frame es «${currentPedagogyFrame?.concept||"aún no disponible"}».`,`La decisión esperada es ${expectedGraphPrediction(currentPedagogyFrame)}.`];if(predictionFeedback)predictionFeedback.textContent=hints[hintLevel-1];});
  skipPrediction?.addEventListener("click",()=>{revealPractice();if(predictionFeedback)predictionFeedback.textContent="Continuaste sin responder; no se registra intento.";});
  practiceMode?.addEventListener("change",()=>{const concealed=Boolean(practiceMode.checked&&pageState.traceCursor>=0);if(practiceCover)practiceCover.hidden=!concealed;visualState.classList.toggle("graph-practice-hidden",concealed);});
  resetProgress?.addEventListener("click",()=>{conceptualProgress.attempts=0;conceptualProgress.correct=0;renderConceptualProgress();if(predictionFeedback)predictionFeedback.textContent="Progreso conceptual reiniciado.";});
  prepareButton?.addEventListener("click",async()=>{const ready=await ensureTraceForCurrentTarget();if(ready)tracePlayer?.reset();});
  pauseButton?.addEventListener("click",()=>tracePlayer?.pause());
  homeButton?.addEventListener("click",()=>tracePlayer?.reset());
  endButton?.addEventListener("click",()=>{if(tracePlayer?.hasTrace())tracePlayer.seek(Math.max(0,tracePlayer.getTotalSteps()-1));});
  repeatButton?.addEventListener("click",async()=>{if(tracePlayer?.hasTrace())await tracePlayer.playFromStart();});
  progressSlider?.addEventListener("input",()=>{if(tracePlayer?.hasTrace())tracePlayer.seek(Number(progressSlider.value));});

  function comparisonCard(side){const summary=side?.summary||{};const constraint=side?.algorithm==="run_dijkstra"?"pesos no negativos":side?.algorithm?.includes("bellman")?"admite negativos":side?.algorithm?.includes("prim")||side?.algorithm?.includes("kruskal")?"grafo no dirigido":"componente alcanzable";return `<article class="hier-compare-card"><h4>${gEscape(side?.algorithm||"algoritmo")}</h4><p><strong>Auxiliar/estrategia:</strong> ${gEscape(summary.auxiliary||constraint)}</p><p><strong>Resultado:</strong> <code>${gEscape(JSON.stringify(summary.order||summary.path||summary.mst_edges||summary))}</code></p><p><strong>Costo:</strong> ${gEscape(summary.distance_to_destination??summary.total_weight??"según V+E")}</p><p><strong>Restricción:</strong> ${gEscape(constraint)}</p><p><strong>Invariante:</strong> ${summary.has_negative_cycle?"ciclo negativo detectado":"✓ conservado"}</p></article>`;}
  function renderComparison(){if(!comparisonResult||!compareGrid)return;compareGrid.innerHTML=comparisonCard(comparisonResult.left)+comparisonCard(comparisonResult.right);if(compareInput)compareInput.textContent=`Entrada inmutable: ${comparisonResult.input.nodes.length} vértices, ${comparisonResult.input.edges.length} aristas. Concepto ${Number(compareProgress?.value||0)+1}/4.`;if(compareConclusion)compareConclusion.textContent=`${comparisonResult.conclusion} Estado auxiliar, costo, restricción e invariante se calculan sobre copias aisladas.`;}
  compareRun?.addEventListener("click",async()=>{const response=await fetch(controls.dataset.compareUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({kind:compareKind?.value,graph:model.visual_state,start:compareStart?.value,end:compareEnd?.value})});const data=await response.json();if(!response.ok||!data.success){if(compareConclusion)compareConclusion.textContent=data.message||"No se pudo comparar.";return;}comparisonResult=data;renderComparison();});
  compareProgress?.addEventListener("input",renderComparison);
  exportImage?.addEventListener("click",async()=>{try{const result=await window.InterpreterRuntime.exportVisualStateAsJpg({target:visualState,quality:.92,scale:2});const link=document.createElement("a");link.href=result.dataUrl;link.download=result.suggestedName;link.click();if(announcer)announcer.textContent="Captura JPG exportada.";}catch(_error){if(announcer)announcer.textContent="No fue posible exportar la captura.";}});
  exportSummary?.addEventListener("click",()=>{const report={module:"graph",phase:activePhase,algorithm:selectedAlgorithm?.name||selectedOperation?.name,cursor:pageState.traceCursor,total_steps:pageState.traceTotalSteps,progress:{...conceptualProgress},frame:currentPedagogyFrame,comparison:comparisonResult};const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="graph-learning-summary.json";link.click();URL.revokeObjectURL(link.href);if(announcer)announcer.textContent="Resumen de aprendizaje exportado.";});
  document.addEventListener("keydown",(event)=>{if(!event.altKey)return;if(event.key==="ArrowRight"){event.preventDefault();simStep?.click();}else if(event.key==="ArrowLeft"){event.preventDefault();simPrev?.click();}else if(event.key==="Home"){event.preventDefault();homeButton?.click();}else if(event.key==="End"){event.preventDefault();endButton?.click();}else if(event.key.toLowerCase()==="p"){event.preventDefault();pauseButton?.click();}});

  simStep?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    const ready = await ensureTraceForCurrentTarget();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    const advanced = await tracePlayer.step();
    if (advanced && tracePlayer.isAtEnd()) {
      pageState.lockStepUntilInput = true;
      setSimulationButtonsState();
    }
  });

  simPrev?.addEventListener("click", () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    const moved = tracePlayer?.prev();
    if (moved) {
      pageState.lockStepUntilInput = false;
    }
    setSimulationButtonsState();
  });

  simPlay?.addEventListener("click", async () => {
    if (!isStepByStepEnabled()) {
      const target = resolveFastModeTarget();
      if (!target || !isTargetSelectionValid(target)) {
        showSimulationStatus("Completa las entradas para ejecutar.");
        setSimulationButtonsState();
        return;
      }
      const selectionKey = buildSelectionKey(target.mode, target.operation.name, target.payload);
      await executeTargetAndLoadTrace(target, selectionKey, { finalOnly: true });
      return;
    }
    const ready = await ensureTraceForCurrentTarget();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.playFromStart();
    if (tracePlayer.isAtEnd()) {
      pageState.lockStepUntilInput = true;
      setSimulationButtonsState();
    }
  });

  stepToggle?.addEventListener("change", () => {
    updateStepModePanelVisibility();
    invalidateTrace(
      isStepByStepEnabled()
        ? "Modo paso a paso activado. Usa Reproducir o Siguiente paso."
        : "Modo rapido activado. Reproducir aplicara solo el resultado final.",
    );
  });

  updateStepModePanelVisibility();
  invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
  refreshGraphPrintfConsole(-1);
  refreshSimulationStatus();
  focusGraphSectionByHash();
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.GRAPH_VIEW_MODEL) {
    initGraphPage(window.GRAPH_VIEW_MODEL);
  }
});
