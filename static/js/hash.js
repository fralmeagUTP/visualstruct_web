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

function hashPredictionExpected(state, operation, payload, kind) {
  const metadata = state?.metadata || {}, capacity = Number(metadata.capacity || 0), key = Number(payload?.key);
  const bucket = capacity > 0 && Number.isInteger(key) ? ((key % capacity) + capacity) % capacity : null;
  const chain = bucket === null ? [] : ((state?.buckets || []).find((item) => Number(item.index) === bucket)?.entries || []);
  const match = chain.findIndex((entry) => Number(entry.key) === key), found = match >= 0;
  const yesNo = (value) => value ? "si" : "no";
  if (kind === "bucket") return bucket === null ? "—" : String(bucket);
  if (kind === "collision") return yesNo(operation === "insert" && !found && chain.length > 0);
  if (kind === "comparisons") return String(found ? match + 1 : chain.length);
  if (kind === "link") return yesNo((operation === "insert" && !found) || (operation === "remove" && found));
  if (kind === "size") return String(Number(metadata.size || 0) + (operation === "insert" && !found ? 1 : operation === "remove" && found ? -1 : 0));
  if (kind === "malloc") return yesNo(operation === "insert" && !found && !payload?.simulate_allocation_failure);
  if (kind === "free") return yesNo((operation === "remove" && found) || operation === "clear" || operation === "destroy_table");
  return "";
}

function hashNormalizePrediction(value) {
  return String(value || "").trim().toLowerCase().replaceAll("sí", "si");
}

function hashTeachingValue(value) {
  if(value===undefined)return 'no registrado';
  if(value===null)return 'NULL';
  if(Array.isArray(value))return value.length?value.map(hashTeachingValue).join(', '):'vacío';
  if(typeof value==='object')return Object.entries(value).map(([k,v])=>`${k}: ${hashTeachingValue(v)}`).join(' · ');
  return String(value);
}
function hashVariableValue(variable) {
  if(variable.alive===false)return 'ámbito terminado; no leer almacenamiento';
  if(variable.valid===false && variable.historical_identity)return `puntero no utilizable; identidad histórica ${variable.historical_identity}`;
  if(variable.valid===false)return 'valor indeterminado; no utilizable';
  if(Number.isInteger(variable.initialized_prefix) && Number.isInteger(variable.capacity)){
    const prefix=variable.initialized_prefix;
    if(prefix===0)return `0 de ${variable.capacity} bytes inicializados`;
    const terminated=Array.isArray(variable.bytes) && variable.bytes.slice(0,prefix).includes(0);
    return `${prefix} de ${variable.capacity} bytes inicializados${terminated?'; texto terminado en \\0':''}${prefix<variable.capacity?'; resto indeterminado':''}`;
  }
  return variable.initialized===false?'sin inicializar':hashTeachingValue(variable.value);
}
function hashOutputCaption(frame) {
  const returnedFalse=frame.operation==='get' && frame.variables?.retorno===false && /return\s+false\s*;/.test(frame.source?.line_text||'');
  return returnedFalse?'Salida int (valor previo del llamador; th_buscar no lo escribió)':'Salida int';
}
function hashLiveMemoryMarkup(frame) {
  const mem=frame.memory||{}, vars=Object.entries(mem.variables||{});
  const tokens=new Set(String(frame.source?.line_text||'').match(/[A-Za-z_]\w*/g)||[]);
  const isReferenced=name=>tokens.has(name)||tokens.has(name.split('.').at(-1));
  const sorted=[...vars].sort(([a],[b])=>Number(isReferenced(b))-Number(isReferenced(a)));
  const active=new Set(sorted.filter(([name])=>isReferenced(name)).map(([,v])=>String(v.value)));
  const heap=[...(mem.heap||[])].sort((a,b)=>Number(active.has(String(b.id)))-Number(active.has(String(a.id))));
  const nodeHtml=n=>{const dead=n.alive===false, mask=Number(n.initialized_mask||0);return `<div class="hash-memory-card" data-hash-live-node="${hashEscape(n.id)}"><strong>${hashEscape(n.id)}</strong> · ${dead?'reserva liberada; no leer campos':n.fields_valid===false?'campos no legibles en este paso':`clave: ${mask&1?hashEscape(n.key):'sin inicializar'} · valor: ${mask&2?hashEscape(n.value):'sin inicializar'} · siguiente: ${mask&4?hashEscape(n.next??'NULL'):'sin inicializar'}`}</div>`;};
  return `<div class="hash-live-variables">${sorted.length?sorted.slice(0,6).map(([name,v])=>`<span><code>${hashEscape(name)}</code> = ${hashEscape(hashVariableValue(v))}</span>`).join(' · '):'Sin variables locales activas. Las reservas tienen su propia vida.'}</div><div class="hash-live-cards">${heap.filter(n=>n.alive!==false).map(nodeHtml).join('')||'Sin nodos vivos registrados.'}</div>${heap.some(n=>n.alive===false)?`<details><summary>Reservas liberadas: ${heap.filter(n=>n.alive===false).length}</summary>${heap.filter(n=>n.alive===false).map(nodeHtml).join('')}</details>`:''}${mem.output?`<p>${hashOutputCaption(frame)}: ${mem.output.alive===false?'ámbito terminado':mem.output.initialized?hashEscape(mem.output.value):'sin inicializar'}</p>`:''}`;
}
function decorateHashPedagogy(frame) {
  const live=hashById('hash-live-memory');if(live)live.innerHTML=hashLiveMemoryMarkup(frame);
  const pointers=hashById('hash-pointers-view'), memory=hashById('hash-memory-view'), chain=hashById('hash-chain-view');
  if(pointers){const raw=pointers.innerHTML;const vars=Object.entries(frame.memory?.variables||{});pointers.innerHTML=(vars.length?vars.map(([name,v])=>`<div><code>${hashEscape(name)}</code> = ${hashEscape(hashVariableValue(v))}</div>`).join(''):'<p>Sin variables locales activas; no significa que los nodos publicados sean NULL.</p>')+`<details><summary>Registro técnico de punteros y ámbitos</summary>${raw}</details>`;}
  if(memory)memory.innerHTML=hashLiveMemoryMarkup(frame)+`<details><summary>Registro técnico completo de memoria</summary>${memory.innerHTML}</details>`;
  if(chain){const raw=chain.innerHTML;chain.innerHTML=`<p>Bucket ${hashEscape(frame.chain?.bucket??'—')}. Comparaciones realizadas: ${(frame.chain?.examined||[]).length}.</p><p>Cadena actual: ${hashEscape(hashTeachingValue(frame.chain?.after||[]))}</p><details><summary>Cadena antes/después y evidencia</summary>${raw}</details>`;}
}
function initHashClassroom() {
  const workspace=document.querySelector('.hash-primary-workspace'),controls=document.querySelector('.hash-execution-controls');if(!workspace||!controls)return;
  const toolbar=document.createElement('section');toolbar.className='hash-classroom-controls';toolbar.setAttribute('aria-label','Controlar ejecución');toolbar.appendChild(controls);
  ['hash-sim-counter','hash-sim-detail','hash-sim-status'].forEach(id=>{const el=hashById(id);if(el)toolbar.appendChild(el);});workspace.before(toolbar);
}

function renderHashPedagogy(frame,level){if(!frame)return;const summary=hashById("hash-pedagogy-summary"),formula=hashById("hash-formula-view"),chain=hashById("hash-chain-view"),pointers=hashById("hash-pointers-view"),cost=hashById("hash-cost-view"),memory=hashById("hash-memory-view"),invariant=hashById("hash-invariant-view");if(summary)summary.innerHTML=`<strong>${hashEscape(frame.phase?.label||frame.concept)}</strong>: ${hashEscape(frame.narration?.[level]||frame.narration?.intermediate||"")}`;window.ContextualHelp?.frame("hash",frame,level);if(formula)formula.innerHTML=`Clave <strong>${hashEscape(frame.hash?.key??"—")}</strong> · capacidad <strong>${hashEscape(frame.hash?.capacity??"—")}</strong><br><code>${hashEscape(frame.hash?.expression||"sin cálculo")}</code><br>Residuo C: <strong>${hashEscape(frame.hash?.raw_remainder??"—")}</strong><br>${hashEscape(frame.hash?.normalization_expression||"")}<br>Bucket final: <strong>${hashEscape(frame.hash?.normalized_index??"—")}</strong>`;if(chain)chain.innerHTML=`Bucket ${hashEscape(frame.chain?.bucket??"—")} · caso: <strong>${hashEscape(frame.chain?.position_kind||"—")}</strong><br>Antes: <code>${hashEscape(JSON.stringify(frame.chain?.before||[]))}</code><br>Después: <code>${hashEscape(JSON.stringify(frame.chain?.after||[]))}</code><br>Comparaciones ejecutadas: ${hashEscape(JSON.stringify(frame.chain?.examined||[]))}`;if(pointers)pointers.innerHTML=Object.entries(frame.pointers||{}).map(([name,value])=>`<code>${hashEscape(name)}</code> = ${hashEscape(value)}`).join("<br>");if(cost)cost.innerHTML=`Hash: ${frame.cost?.hash_evaluations||0} · comparaciones: ${frame.cost?.comparisons||0} · nodos visitados: ${frame.cost?.nodes_visited||0}<br><small>${hashEscape(frame.cost?.unit||"")}</small><details><summary>Complejidad</summary>${hashEscape(frame.cost?.best_case||"")}<br>${hashEscape(frame.cost?.average_case||"")}<br>${hashEscape(frame.cost?.worst_case||"")}<br>${hashEscape(frame.cost?.depends_on||"")}</details>`;if(memory)memory.innerHTML=`Intento de malloc: ${frame.memory?.allocation_attempted?"sí":"no"} · comprobó NULL: ${frame.memory?.null_checked?"sí":"no"}<br>Fallo simulado: <strong>${frame.memory?.allocation_failed?"sí; estado intacto":"no"}</strong><br>Reservados: <code>${hashEscape(JSON.stringify(frame.memory?.allocated||[]))}</code><br>Campos inicializados: ${hashEscape((frame.memory?.initialized_fields||[]).join(", ")||"ninguno")}<br>Liberados: <code>${hashEscape(JSON.stringify(frame.memory?.freed||[]))}</code><br>Arreglo buckets liberado: ${frame.memory?.bucket_array_freed?"sí":"no"} · buckets = NULL: ${frame.memory?.bucket_array_is_null?"sí":"no"}<br>Enlaces cambiados: ${frame.memory?.links_changed?"sí":"no"}`;if(pointers && frame.memory?.variables)pointers.innerHTML += `<hr><strong>Variables tipadas / alcance</strong><pre>${hashEscape(JSON.stringify(frame.memory.variables,null,2))}</pre><p>Pila: ${hashEscape(JSON.stringify(frame.memory.call_stack||[]))}</p>`;if(memory && frame.memory?.heap)memory.innerHTML += `<hr><strong>Heap y máscaras de inicialización</strong><pre>${hashEscape(JSON.stringify(frame.memory.heap,null,2))}</pre><p>Buckets inicializados: ${hashEscape(JSON.stringify(frame.memory.bucket_initialization||[]))}</p>`;if(memory && frame.operation==="remove" && frame.memory?.bucket_array)memory.innerHTML += `<hr><strong>Arreglo de punteros THNodo *</strong><pre>${hashEscape(JSON.stringify(frame.memory.bucket_array,null,2))}</pre><p>Cantidad pendiente: ${frame.memory.count_write_pending?"sí; cantidad-- aún no ejecutado":"no"}</p><p>Puntero retirado: ${hashEscape(frame.memory.retired_pointer||"ninguno")}. Tras free no se inspecciona ni utiliza su valor; las referencias históricas son simbólicas.</p>`;if(memory && frame.memory?.output)memory.innerHTML += `<hr><strong>Almacenamiento de salida int</strong><pre>${hashEscape(JSON.stringify(frame.memory.output,null,2))}</pre><small>Valor indeterminado se muestra null; no se lee antes de escritura. alive=false indica alcance terminado.</small>`;if(memory && frame.memory?.buffer)memory.innerHTML += `<hr><strong>Buffer C char[] / bytes inicializados</strong><pre>${hashEscape(JSON.stringify(frame.memory.buffer,null,2))}</pre><small>La zona indeterminada no se lee. ${frame.operation === "stats" ? "Este texto C representa estadisticas con float y dos decimales; la API conserva su cociente y formato propios." : "Este texto C representa la tabla completa; el resultado API es una proyeccion independiente."}</small>`;if(memory && frame.stats_representation)memory.innerHTML += `<hr><strong>Representaciones C / API</strong><pre>${hashEscape(JSON.stringify(frame.stats_representation,null,2))}</pre><small>Las copias THEstadisticas y sus scopes son propios de cada llamada; padding y ABI no se inspeccionan.</small>`;if(memory && frame.lifecycle)memory.innerHTML += `<hr><strong>Vida de buckets / raiz C</strong><pre>${hashEscape(JSON.stringify(frame.memory.bucket_array,null,2))}</pre><p>Pointer raiz valido: ${frame.memory.root_bucket_pointer_valid?"si":"no; indeterminado"}. Cantidad pendiente: ${frame.memory.count_write_pending?"si":"no"}. Root TablaHash sigue vivo: ${frame.memory.root_stack_object_alive?"si":"no"}.</p>`;if(invariant)invariant.innerHTML=`<strong>${hashEscape(frame.invariant?.symbol||"")} ${hashEscape(frame.invariant?.name||"")}</strong><br>${hashEscape(frame.invariant?.evidence||"")}`;decorateHashPedagogy(frame);}

function initHashResponsiveWorkspace(){const workspace=document.querySelector(".hash-primary-workspace"),tabs=[...document.querySelectorAll("[data-hash-tab]")];if(!workspace||!tabs.length)return;let saved="visual";try{saved=sessionStorage.getItem("hash-active-tab")||"visual";}catch(_error){}const activate=(name)=>{const value=name==="code"?"code":"visual";workspace.dataset.activeTab=value;tabs.forEach((tab)=>{const active=tab.dataset.hashTab===value;tab.classList.toggle("is-active",active);tab.setAttribute("aria-selected",String(active));});try{sessionStorage.setItem("hash-active-tab",value);}catch(_error){}};tabs.forEach((tab)=>tab.addEventListener("click",()=>activate(tab.dataset.hashTab)));activate(saved);}

function enhanceHashCodeNavigation(activeLine){const code=hashById("op-pseudocode"),list=hashById("hash-function-list"),hide=hashById("hash-hide-comments");if(!code||!list)return;const source=code.dataset.rawCode||code.textContent||"";window.CCodeNavigation?.markComments(code,source);const functions=[];source.split("\n").forEach((line,index)=>{const match=line.match(/\b(th_[A-Za-z_]\w*)\s*\([^;]*\)\s*\{/);if(match)functions.push({name:match[1],line:index});});list.innerHTML=functions.map((item)=>`<li><button type="button" data-line="${item.line}">${hashEscape(item.name)}</button></li>`).join("");list.querySelectorAll("button").forEach((button)=>button.addEventListener("click",()=>{const lines=code.querySelectorAll(".code-line");window.CCodeNavigation?.revealLine(code,lines[Number(button.dataset.line)]);}));code.classList.toggle("hide-code-comments",Boolean(hide?.checked));if(Number.isInteger(activeLine))code.dataset.activeLine=String(activeLine);}

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
    history.push(entry);
  return true;
}

function renderHashPrintfConsole(consoleEl, lines, fallbackText) {
  if (!consoleEl) {
    return;
  }
  const safeLines = Array.isArray(lines) ? lines : [];
  consoleEl.dataset.consoleCopy = safeLines.join("\n");
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
    input.type = field.type === "number" ? "number" : field.type === "checkbox" ? "checkbox" : "text";
    input.required = field.required !== false;
    for (const bound of ["min", "max", "step"]) if (field[bound] !== undefined) input[bound] = String(field[bound]);

    wrap.appendChild(label);
    wrap.appendChild(input);
    container.appendChild(wrap);
  });
}

function renderHashEntries(entries, showAddresses, examinedKeys) {
  if (!Array.isArray(entries) || !entries.length) {
    return "<span class=\"hash-empty\">vacio</span>";
  }

  return entries
    .map((entry) => `<span class="hash-entry ${examinedKeys.has(Number(entry.key)) ? "is-examined" : ""}"><span class="hash-node-address">${showAddresses?hashEscape(entry.address||"—"):"nodo"}</span><span><code>clave</code> = ${hashEscape(entry.key)}</span><span><code>valor</code> = ${hashEscape(entry.value)}</span>${showAddresses?`<span><code>siguiente</code> = ${hashEscape(entry.next||"NULL")}</span>`:""}</span>`)
    .join("<span class=\"hash-sep\"> -> </span>");
}

function hashLoadFactorFormula(metadata) {
  if(Number(metadata.capacity)===0)return 'Capacidad 0: factor 0 por convención del TAD, sin dividir.';
  return `α = cantidad / capacidad = ${metadata.size??0} / ${metadata.capacity??'—'} = ${metadata.load_factor??'—'}`;
}
function hashBucketPointerLabel(lifecycle) {
  if(!lifecycle.root_bucket_pointer_valid)return 'Puntero buckets indeterminado tras free; no se lee.';
  if(lifecycle.root_bucket_pointer===null && lifecycle.bucket_array_alive===false)return 'buckets = NULL (sin arreglo).';
  return lifecycle.bucket_array_alive ? 'Puntero buckets al arreglo vivo.' : 'Puntero buckets registrado.';
}
function renderHashState(state, container, frame) {
  if (!state || !container) {
    return;
  }

  if(state.suspended){
    container.innerHTML=`<div class="hash-suspended" role="status"><h4>Estado histórico suspendido</h4><p>${hashEscape(state.suspension_reason || "Capacidad histórica superior al límite educativo de la aplicación.")}</p><p>Capacidad histórica: ${hashEscape(state.capacity ?? state.metadata?.capacity ?? "registrada en el historial")}. La tabla no se reconstruye ni se representa como vacía.</p><p>Conserva el historial y descarga main.c o el resumen antes de restablecer la tabla, si lo necesitas.</p></div>`;
    const minimap=hashById('hash-minimap');if(minimap)minimap.innerHTML='';
    const live=hashById('hash-live-memory');if(live)live.textContent='Memoria no reconstruida: estado histórico suspendido.';
    return;
  }
  const metadata = state.metadata || {};
  const allBuckets = Array.isArray(state.buckets) ? state.buckets : [];
  const filter = hashById("hash-bucket-filter")?.value || "all";
  const showAddresses = hashById("hash-show-addresses")?.checked !== false;
  const frameBucket = frame?.chain?.bucket;
  const activeBucket = frameBucket === null || frameBucket === undefined || frameBucket === ""
    ? null
    : Number(frameBucket);
  const examinedKeys = new Set((frame?.chain?.examined || []).map((key) => Number(key)));
  const buckets = filter === "occupied" ? allBuckets.filter((bucket)=>bucket.size>0 || (state.lifecycle && bucket.initialized===false)) : allBuckets;
  const minimap=hashById("hash-minimap");
  if(minimap)minimap.innerHTML=allBuckets.map((bucket)=>`<span class="hash-minimap-cell ${bucket.size?"is-occupied":""}" title="Bucket ${hashEscape(bucket.index)}: longitud ${hashEscape(bucket.size)}"><span class="sr-only">${hashEscape(bucket.index)}</span></span>`).join("");

  let html = "<div class=\"viz-canvas\"><div class=\"viz-stage\">";
  html += `<div class="viz-meta"><strong>${hashEscape(state.title || "Tabla Hash")}</strong></div>`;
  html += (
    `<div class="viz-meta">Tamano: ${hashEscape(metadata.size || 0)} | ` +
    `Capacidad: ${hashEscape(metadata.capacity || 0)} | ` +
    `Factor de carga: ${hashEscape(metadata.load_factor ?? 0)} | ` +
    `Ocupados: ${hashEscape(state.lifecycle && !state.lifecycle.chain_statistics_available ? "indeterminado" : metadata.occupied_buckets || 0)} | ` +
    `Colisiones Σ max(0, longitud−1): ${hashEscape(state.lifecycle && !state.lifecycle.chain_statistics_available ? "indeterminado" : metadata.collisions || 0)} | ` +
    `Cadena máxima: ${hashEscape(state.lifecycle && !state.lifecycle.chain_statistics_available ? "indeterminado" : metadata.max_chain_length || 0)}</div>`
  );
  html += `<div class="viz-meta hash-formulas"><code>${hashEscape(hashLoadFactorFormula(metadata))}</code></div>`;

  if(state.lifecycle)html += `<p class="viz-meta">${hashEscape(hashBucketPointerLabel(state.lifecycle))} ${state.lifecycle.count_write_pending ? "Cantidad C pendiente de su store final." : ""}</p>`;
  html += "<p class=\"hash-capacity-note\">Política de capacidad: fija; esta versión no ejecuta resize ni rehash.</p>";

  if (!buckets.length) {
    html += "<p class=\"viz-empty\">No hay buckets para mostrar.</p>";
  } else {
    html += "<div class=\"hash-buckets-wrap\">";
    buckets.forEach((bucket) => {
      const bucketClass = ["hash-bucket", bucket.collisions > 0 ? "has-collision" : "", Number.isInteger(activeBucket) && Number(bucket.index) === activeBucket ? "is-active-bucket" : ""].filter(Boolean).join(" ");
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
      html += `<div class="hash-bucket-body"><span class="hash-head-pointer">buckets[${hashEscape(bucket.index)}] →</span>${bucket.initialized === false && state.lifecycle ? '<span class="hash-empty">indeterminado tras free; no seguir chain</span>' : bucket.initialized === false ? '<span class="hash-empty">indeterminado; aún no inicializado</span>' : renderHashEntries(bucket.entries,showAddresses,examinedKeys)}${bucket.entries?.length?'<span class="hash-null">→ NULL</span>':""}</div>`;
      html += "</div>";
    });
    html += "</div>";
  }

  if (state.last_operation && state.last_operation.message) {
    html += `<p class="viz-meta"><strong>Ultima operacion:</strong> ${hashEscape(state.last_operation.message)}</p>`;
  }

  html += "</div></div>";
  container.innerHTML = html;
  const active=container.querySelector?.('.is-active-bucket');
  if(active && container.getBoundingClientRect){const bounds=container.getBoundingClientRect(),rect=active.getBoundingClientRect();if(rect.top<bounds.top||rect.bottom>bounds.bottom)container.scrollTop+=rect.top-bounds.top;}

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
  window.ContextualHelp?.operation("hash", model, operationName);
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
    return `th_destruir(&tabla); th_inicializar(&tabla, ${capacity || "17"});`;
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
  if (entry.operation === "destroy_table") {
    return "th_destruir(&tabla);";
  }
  return `${entry.subroutine || "Operacion"}();`;
}

function buildHashMainCode(history) {
  const lines = [];
  lines.push('#include "tad_tabla_hash.h"');
  lines.push("#include <stdio.h>");
  lines.push("");
  lines.push("int main(void) {");
  lines.push("    TablaHash tabla = {0};");
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
  lines.push("    th_destruir(&tabla);");
  lines.push("    return 0;");
  lines.push("}");
  return lines.join("\n");
}

function renderHashHistory(history, container, didactic, mainCode) {
  if (!container) {
    return;
  }
  container.dataset.rawCode = "";
  if (!history.length && !mainCode) {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }
  const codeTitle = didactic && didactic.code_title ? String(didactic.code_title) : "";
  if (codeTitle.toLowerCase().includes("codigo c")) {
    const code = mainCode || buildHashMainCode(history);
    container.dataset.rawCode = code;
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
  const simNextButton = hashById("hash-sim-next");
  const stepNavigation = hashById("hash-step-navigation");
  const simPauseButton = hashById("hash-sim-pause"),simStartButton=hashById("hash-sim-start"),simEndButton=hashById("hash-sim-end"),simRepeatButton=hashById("hash-sim-repeat"),simProgress=hashById("hash-sim-progress"),simDetail=hashById("hash-sim-detail");
  const stepToggle = hashById("hash-step-toggle");
  const simStatus = hashById("hash-sim-status");
  const printfConsole = hashById("hash-printf-console");
  const learningLevel=hashById("hash-learning-level"),guidedExample=hashById("hash-guided-example"),loadExample=hashById("hash-load-example"),exampleLesson=hashById("hash-example-lesson"),resetExecution=hashById("hash-reset-execution"),hideComments=hashById("hash-hide-comments"),bucketFilter=hashById("hash-bucket-filter"),showAddresses=hashById("hash-show-addresses");
  const predictionKind=hashById("hash-prediction-kind"),predictionAnswer=hashById("hash-prediction-answer"),predictionPrompt=hashById("hash-prediction-prompt"),predictionFeedback=hashById("hash-prediction-feedback"),predictionCheck=hashById("hash-check-prediction"),predictionHint=hashById("hash-prediction-hint"),predictionSkip=hashById("hash-skip-prediction"),practiceMode=hashById("hash-practice-mode"),resetProgress=hashById("hash-reset-progress");
  const compareControls=hashById("hash-compare-controls"),compareEntries=hashById("hash-compare-entries"),compareSuccessKey=hashById("hash-compare-success-key"),compareAbsentKey=hashById("hash-compare-absent-key"),compareRun=hashById("hash-compare-run"),compareProgress=hashById("hash-compare-progress"),compareInput=hashById("hash-compare-input"),compareGrid=hashById("hash-compare-grid"),compareConclusion=hashById("hash-compare-conclusion"),exportImage=hashById("hash-export-image"),exportSummary=hashById("hash-export-summary"),announcer=hashById("hash-accessible-announcer");

  if (!form || !operationSelect || !inputsContainer || !visualContainer) {
    return;
  }

  const operations = model.operations || [];
  let selected = operations[0] || null;
  let visualState = model.visual_state;
  const operationLabel = new Map(operations.map((op) => [op.name, op.label]));
  const actionHistory = [];
  let currentPedagogyFrame=null;
  let capacityComparison=null;
  const presentationKey="hash-presentation";
  const progressKey="hash-learning-progress";
  let conceptualProgress={correct:0,attempts:0,hints:0,skipped:0};
  try{conceptualProgress={...conceptualProgress,...JSON.parse(sessionStorage.getItem(progressKey)||"{}")} }catch(_error){}
  function saveConceptualProgress(){try{sessionStorage.setItem(progressKey,JSON.stringify(conceptualProgress));}catch(_error){}}
  function updatePredictionPrompt(){if(!predictionKind||!predictionPrompt)return;const current=operations.find((item)=>item.name===operationSelect.value)||selected;const payload=current?collectPayload(current):{};const labels={bucket:"¿Qué bucket final tendrá la clave?",collision:"¿Habrá colisión? (sí/no)",comparisons:"¿Cuántas comparaciones de clave se ejecutarán?",link:"¿Se modificará un enlace? (sí/no)",size:"¿Cuál será la cantidad final?",malloc:"¿Se reservará un nodo con malloc? (sí/no)",free:"¿Se liberará un nodo con free? (sí/no)"};predictionPrompt.textContent=labels[predictionKind.value]||"Formula una predicción.";if(predictionFeedback)predictionFeedback.textContent=`Progreso de sesión: ${conceptualProgress.correct}/${conceptualProgress.attempts} aciertos.`;return {current,payload};}
  try{const saved=JSON.parse(sessionStorage.getItem(presentationKey)||"{}");if(learningLevel&&saved.level)learningLevel.value=saved.level;}catch(_error){}
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
      const emitted = Array.isArray(step.console) ? step.console : [];
      emitted.forEach((line) => hashPushUniqueConsoleLine(out, line));
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
      renderState: (stateSnapshot,stepMeta) => {
        visualState = stateSnapshot;
        renderHashState(visualState, visualContainer, stateSnapshot === stepMeta?.state_snapshot ? null : stepMeta?.pedagogy);
        if(stateSnapshot === stepMeta?.state_snapshot){currentPedagogyFrame=null;["hash-live-memory","hash-formula-view","hash-chain-view","hash-pointers-view","hash-cost-view","hash-memory-view","hash-invariant-view"].forEach(id=>{const el=hashById(id);if(el)el.textContent="Antes de ejecutar: ninguna instrucción resaltada.";});}else if(stepMeta?.pedagogy){currentPedagogyFrame=stepMeta.pedagogy;renderHashPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");}
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        refreshHashPrintfConsole(cursor);
        const step=event?.step;
        if(step?.pedagogy && step.debug?.stage && simStatus && window.ContextualHelp)simStatus.textContent=simStatus.textContent.replace(` - ${step.debug.stage}`,` - ${window.ContextualHelp.phaseLabel(step.pedagogy)}`);
        enhanceHashCodeNavigation(Number.isInteger(step?.line_index)?step.line_index:null);try{sessionStorage.setItem(presentationKey,JSON.stringify({level:learningLevel?.value||"intermediate",cursor}));}catch(_error){}
        if(simProgress){const total=tracePlayer?.getTotalSteps?.()||0;simProgress.max=String(total);simProgress.value=String(Math.max(0,cursor+1));simProgress.disabled=!total;}
        if(simDetail){const frame=step?.pedagogy;simDetail.textContent=frame?`Función: ${frame.source?.function||"—"} · fase: ${window.ContextualHelp?.phaseLabel(frame)||frame.phase?.label||"—"} · bucket: ${frame.chain?.bucket??"—"} · nodo: ${frame.memory?.variables?.actual ? hashTeachingValue(frame.memory.variables.actual.value) : "sin local activo"}`:"Sin traza cargada.";}
        if (cursor < 0) window.ContextualHelp?.frame("hash", null);
        setSimulationButtonsEnabled();
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
  (model.guided_examples||[]).forEach((example)=>{if(!guidedExample)return;const option=document.createElement("option");option.value=example.id;option.textContent=example.label;guidedExample.appendChild(option);});

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
  renderHashHistory(actionHistory, historyBox, model.didactic, model.main_c);
  renderHashState(visualState, visualContainer);
  initHashResponsiveWorkspace();initHashClassroom();enhanceHashCodeNavigation(null);
  updatePredictionPrompt();
  refreshHashPrintfConsole(-1);

  function isCurrentSelectionValid() {
    const current = operations.find((item) => item.name === operationSelect.value);
    if (visualState?.suspended || !current) {
      return false;
    }
    return current.inputs.every((field) => {
      const element = hashById(`hash-field-${field.name}`);
      if (!element) {
        return false;
      }
      if (field.type === "checkbox" || field.required === false) {
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
    const cursor = tracePlayer?.getCursor?.() ?? -1;
    const total = tracePlayer?.getTotalSteps?.() ?? 0;
    if (stepNavigation) {
      stepNavigation.hidden = !stepMode;
    }
    if (simStepButton) {
      simStepButton.hidden = false;
    }
    if (simPlayButton) {
      simPlayButton.disabled = busy || !canExecute;
    }
    if (simPrevButton) {
      simPrevButton.disabled = busy || !stepMode || !hasTrace || cursor < 0;
    }
    if (simNextButton) {
      simNextButton.disabled = busy || !stepMode || !hasTrace || cursor >= total - 1;
    }
    if (simStepButton) {
      simStepButton.disabled = busy || Boolean(visualState?.suspended);
    }
  }

  function invalidateTrace(message) {
    currentPedagogyFrame=null;
    const memoryPanel=hashById("hash-live-memory");if(memoryPanel)memoryPanel.textContent=visualState?.suspended?"Memoria no reconstruida: estado histórico suspendido.":"Prepara una traza para observar la memoria C.";
    traceSelectionKey = "";
    consoleState.trace = null;
    consoleState.fallbackMessage = "";
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
    if (stepNavigation) {
      stepNavigation.hidden = true;
    }
    if (simStepButton) {
      simStepButton.hidden = false;
    }
    refreshHashPrintfConsole(-1);
    setSimulationButtonsEnabled();
  }

  function collectPayload(current) {
    const payload = {};
    current.inputs.forEach((field) => {
      const element = hashById(`hash-field-${field.name}`);
      payload[field.name] = element ? (field.type === "checkbox" ? element.checked : element.value) : "";
    });
    return payload;
  }

  function buildSelectionKey(current, payload) {
    return `${current.name}::${JSON.stringify(payload)}`;
  }

  async function executeOperationAndLoadTrace(current, payload, selectionKey, options) {
    if(pendingExecution)return null;
    if(visualState?.suspended){showHashMessage("Estado histórico suspendido: conserva el historial y restablece la tabla para continuar.",false);return null;}
    const capacityField=current.inputs?.find(field=>field.name==='capacity');
    if(current.name==='create_table' && capacityField && (!Number.isInteger(Number(payload.capacity)) || Number(payload.capacity)<Number(capacityField.min ?? 1) || Number(payload.capacity)>Number(capacityField.max ?? 128))){showHashMessage(`La capacidad educativa debe estar entre ${capacityField.min ?? 1} y ${capacityField.max ?? 128}; se conserva el estado anterior.`,false);return null;}

    if((current.name==="clear"||current.name==="destroy_table")&&!window.confirm(current.name==="clear"?"¿Vaciar todos los nodos conservando capacidad?":"¿Destruir nodos y arreglo de buckets?"))return null;
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
      const recordedSteps = Array.isArray(data.execution_trace?.steps) && data.execution_trace.steps.length > 0;
      if(data.preserve_session || ((!response.ok || !data.success) && !recordedSteps))return null;
      updateHashDidacticPanel(model, current.name);

      const finalOnly = Boolean(options && options.finalOnly);
      const hasExecutionTrace = Boolean(data.execution_trace && tracePlayer);
      if (hasExecutionTrace) {
        consoleState.trace = data.execution_trace;
        consoleState.fallbackMessage = "";
        tracePlayer.loadTrace(data.execution_trace);
        traceSelectionKey = selectionKey;
        if (finalOnly) tracePlayer.seek(tracePlayer.getTotalSteps() - 1);
      } else {
        consoleState.trace = null;
        consoleState.fallbackMessage = "(sin salida printf en esta ruta)";
        refreshHashPrintfConsole(-1);
        traceSelectionKey = "";
      }
      model.history = data.history || model.history;
      model.main_c = data.main_c || model.main_c;
      actionHistory.splice(0, actionHistory.length, ...(model.history || []).map(step =>
        createHashHistoryEntry(getHashSubroutineName(model, step.operation, step.operation), summarizeHashPayload(step.payload), "Operación confirmada", step.operation, step.payload)));
      renderHashHistory(actionHistory, historyBox, model.didactic, model.main_c);

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
  if (!visualState?.suspended && model.execution_trace && tracePlayer) {
    const restored = model.execution_trace;
    selected = operations.find(item => item.name === restored.operation_name) || selected;
    operationSelect.value = selected.name;
    buildHashOperationInputs(selected, inputsContainer);
    Object.entries(restored.payload || {}).forEach(([name, value]) => {
      const input = hashById(`hash-field-${name}`);
      if (input) { if (input.type === "checkbox") input.checked = Boolean(value); else input.value = value; }
    });
    updateHashDidacticPanel(model, selected.name);
    consoleState.trace = restored; consoleState.fallbackMessage = "";
    tracePlayer.loadTrace(restored);
    traceSelectionKey = buildSelectionKey(selected, collectPayload(selected));
    tracePlayer.seek(tracePlayer.getTotalSteps() - 1);
  }

  operationSelect.addEventListener("change", () => {
    selected = operations.find((item) => item.name === operationSelect.value) || null;
    buildHashOperationInputs(selected, inputsContainer);
    updateHashDidacticPanel(model, selected ? selected.name : "");
    enhanceHashCodeNavigation(null);
    invalidateTrace("Operacion cambiada. Ejecuta nuevamente.");
    updatePredictionPrompt();
  });

  learningLevel?.addEventListener("change",()=>{renderHashPedagogy(currentPedagogyFrame,learningLevel.value);try{sessionStorage.setItem(presentationKey,JSON.stringify({level:learningLevel.value,cursor:tracePlayer?.getCursor()??-1}));}catch(_error){}});
  hideComments?.addEventListener("change",()=>enhanceHashCodeNavigation(null));
  bucketFilter?.addEventListener("change",()=>renderHashState(visualState,visualContainer,currentPedagogyFrame));
  showAddresses?.addEventListener("change",()=>renderHashState(visualState,visualContainer,currentPedagogyFrame));
  resetExecution?.addEventListener("click",()=>tracePlayer?.reset());
  simPauseButton?.addEventListener("click",()=>tracePlayer?.pause());
  simStartButton?.addEventListener("click",()=>tracePlayer?.seek(-1));
  simEndButton?.addEventListener("click",()=>tracePlayer?.seek((tracePlayer?.getTotalSteps()||1)-1));
  simRepeatButton?.addEventListener("click",async()=>{if(tracePlayer?.hasTrace())await tracePlayer.playFromStart();});
  simProgress?.addEventListener("input",()=>tracePlayer?.seek(Number(simProgress.value||0)-1));
  predictionKind?.addEventListener("change",()=>updatePredictionPrompt());
  predictionCheck?.addEventListener("click",()=>{const context=updatePredictionPrompt();if(!context||!predictionAnswer)return;const expected=hashNormalizePrediction(hashPredictionExpected(visualState,context.current?.name,context.payload,predictionKind?.value));const actual=hashNormalizePrediction(predictionAnswer.value);conceptualProgress.attempts+=1;const correct=Boolean(actual)&&actual===expected;if(correct)conceptualProgress.correct+=1;saveConceptualProgress();if(predictionFeedback){predictionFeedback.className=correct?"message ok":"message error";predictionFeedback.textContent=correct?"Correcto. Tu predicción coincide con la ejecución C.":`Aún no. Revisa la capacidad, el bucket y la cadena; respuesta esperada: ${expected}.`;}});
  predictionHint?.addEventListener("click",()=>{const context=updatePredictionPrompt();if(!context)return;conceptualProgress.hints+=1;saveConceptualProgress();const expected=hashPredictionExpected(visualState,context.current?.name,context.payload,predictionKind?.value);if(predictionFeedback){predictionFeedback.className="message";predictionFeedback.textContent=`Pista ${conceptualProgress.hints}: usa clave % capacidad y observa la cadena correspondiente.${practiceMode?.checked?" En práctica no se muestra aún el resultado final.":` La respuesta tiene la forma: ${String(expected).replace(/./g,"•")}`}`;}});
  predictionSkip?.addEventListener("click",()=>{conceptualProgress.skipped+=1;saveConceptualProgress();if(predictionFeedback){predictionFeedback.className="message";predictionFeedback.textContent="Puedes continuar; la traza te mostrará la respuesta causal.";}});
  resetProgress?.addEventListener("click",()=>{conceptualProgress={correct:0,attempts:0,hints:0,skipped:0};saveConceptualProgress();updatePredictionPrompt();});
  function parseComparisonEntries(text){const pairs=String(text||"").split(",").map((part)=>part.trim()).filter(Boolean).map((part)=>part.split(":").map((value)=>Number(value.trim())));if(!pairs.length||pairs.some((pair)=>pair.length!==2||pair.some((value)=>!Number.isInteger(value))))throw new Error("Usa pares enteros con el formato clave:valor, separados por coma.");return pairs;}
  function renderCapacityComparison(){if(!capacityComparison||!compareGrid)return;const cursor=Math.max(0,Number(compareProgress?.value||0));compareGrid.innerHTML=capacityComparison.variants.map((variant)=>{const state=variant.snapshots[Math.min(cursor,variant.snapshots.length-1)],meta=state.metadata||{},active=variant.snapshots[Math.min(cursor,variant.snapshots.length-1)];const occupied=(active.buckets||[]).filter((bucket)=>bucket.size>0).map((bucket)=>`[${hashEscape(bucket.index)}] ${hashEscape(bucket.entries.map((entry)=>entry.key).join(" → ")||"∅")}`).join(" · ")||"sin buckets ocupados";return `<article class="hash-compare-card"><h4>Capacidad ${hashEscape(variant.capacity)}</h4><p><strong>Distribución:</strong> ${occupied}</p><p>Ocupados ${hashEscape(meta.occupied_buckets||0)} · colisiones ${hashEscape(meta.collisions||0)} · α=${hashEscape(meta.load_factor??0)} · cadena máx. ${hashEscape(meta.max_chain_length||0)}</p><p><strong>Exitosa:</strong> bucket ${hashEscape(variant.successful_lookup.bucket)}, ${hashEscape(variant.successful_lookup.comparisons)} comparaciones.</p><p><strong>Ausente:</strong> bucket ${hashEscape(variant.absent_lookup.bucket)}, ${hashEscape(variant.absent_lookup.comparisons)} comparaciones.</p></article>`;}).join("");if(compareInput)compareInput.textContent=`Entrada inmutable: ${capacityComparison.input.entries.map((pair)=>`${pair[0]}:${pair[1]}`).join(", ")} · inserción ${cursor}/${capacityComparison.input.entries.length}.`;if(compareConclusion)compareConclusion.textContent=capacityComparison.conclusion;}
  compareRun?.addEventListener("click",async()=>{try{const entries=parseComparisonEntries(compareEntries?.value);const response=await fetch(compareControls?.dataset.compareUrl||"",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({entries,success_key:compareSuccessKey?.value,absent_key:compareAbsentKey?.value})});const data=await response.json();if(!response.ok||!data.success)throw new Error(data.message||"No fue posible comparar.");capacityComparison=data;if(compareProgress){compareProgress.min="0";compareProgress.max=String(data.input.entries.length);compareProgress.value="0";compareProgress.disabled=false;}renderCapacityComparison();if(announcer)announcer.textContent="Comparación de capacidades preparada sobre copias aisladas.";}catch(error){if(compareConclusion)compareConclusion.textContent=error.message||"No fue posible comparar.";}});
  compareProgress?.addEventListener("input",renderCapacityComparison);
  exportImage?.addEventListener("click", async () => {
    if (exportImage.disabled) return;
    const originalText = exportImage.textContent;
    exportImage.disabled = true;
    exportImage.setAttribute("aria-busy", "true");
    try {
      const exported = await window.InterpreterRuntime.exportVisualStateAsJpg({
        target: visualContainer, quality: .92, scale: 2,
        onProgress: (text) => { exportImage.textContent = text; },
      });
      window.InterpreterRuntime.downloadJpg(exported.dataUrl, exported.suggestedName);
      showHashMessage("Captura JPG preparada; revisa las descargas del navegador.", true);
    } catch (error) { showHashMessage(error.message || "No se pudo exportar la captura.", false); }
    finally {
      exportImage.disabled = false;
      exportImage.removeAttribute("aria-busy");
      exportImage.textContent = originalText;
    }
  });
  exportSummary?.addEventListener("click",()=>{const summary={schema:"hash-learning-summary/v1",structure:model.id,operation:operationSelect.value,payload:(operations.find((item)=>item.name===operationSelect.value)?collectPayload(operations.find((item)=>item.name===operationSelect.value)):{}),level:learningLevel?.value,cursor:tracePlayer?.getCursor()??-1,total_steps:tracePlayer?.getTotalSteps()??0,frame:currentPedagogyFrame,state:visualState,history:model.history||[],main_c:model.main_c||"",progress:conceptualProgress,comparison:capacityComparison};const url=URL.createObjectURL(new Blob([JSON.stringify(summary,null,2)],{type:"application/json"}));const link=document.createElement("a");link.href=url;link.download="tabla-hash-resumen.json";link.click();URL.revokeObjectURL(url);if(announcer)announcer.textContent="Resumen de aprendizaje exportado.";});
  document.addEventListener("keydown",(event)=>{if(!event.altKey||["INPUT","TEXTAREA","SELECT"].includes(document.activeElement?.tagName))return;const actions={ArrowRight:()=>simStepButton?.click(),ArrowLeft:()=>simPrevButton?.click(),Home:()=>simStartButton?.click(),End:()=>simEndButton?.click(),p:()=>simPauseButton?.click(),P:()=>simPauseButton?.click()};const action=actions[event.key];if(action){event.preventDefault();action();}});
  loadExample?.addEventListener("click",async()=>{const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample?.value);if(!example){showHashMessage("Selecciona un ejemplo guiado.",false);return;}loadExample.disabled=true;try{let response=await fetch(form.dataset.operateUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({operation:"create_table",payload:{capacity:example.capacity}})});let data=await response.json();for(const [key,value] of example.entries||[]){response=await fetch(form.dataset.operateUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({operation:"insert",payload:{key,value}})});data=await response.json();}if(data.visual_state){visualState=data.visual_state;model.visual_state=data.visual_state;renderHashState(visualState,visualContainer);}selected=operations.find((item)=>item.name===example.operation)||selected;operationSelect.value=selected.name;buildHashOperationInputs(selected,inputsContainer);Object.entries(example.payload||{}).forEach(([name,value])=>{const input=hashById(`hash-field-${name}`);if(input){if(input.type==="checkbox")input.checked=Boolean(value);else input.value=value;}});updateHashDidacticPanel(model,selected.name);enhanceHashCodeNavigation(null);invalidateTrace("Ejemplo preparado; reproduce la operación objetivo.");updatePredictionPrompt();if(exampleLesson)exampleLesson.textContent=example.lesson;showHashMessage(`Ejemplo preparado: ${example.lesson}`,true);}finally{loadExample.disabled=false;}});

  inputsContainer.addEventListener("input", () => {
    if(!isCurrentSelectionValid())return;
    invalidateTrace("Entradas cambiadas. Ejecuta nuevamente.");
    updatePredictionPrompt();
  });
  inputsContainer.addEventListener("change", updatePredictionPrompt);

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
    await tracePlayer.play();
  });

  resetButton?.addEventListener("click", async () => {
    if(pendingExecution || !window.confirm("¿Restablecer la tabla y borrar el historial de esta sesión? Descarga main.c o el resumen antes si deseas conservarlo."))return;
    pendingExecution=true;resetButton.disabled=true;setSimulationButtonsEnabled();
    try {
      const response=await fetch(form.dataset.resetUrl,{method:"POST"});const data=await response.json();
      showHashMessage(data.message,Boolean(data.success));if(!response.ok||!data.success)return;
      updateHashDidacticPanel(model,selected?selected.name:"");
      model.history=data.history||[];model.main_c=data.main_c||"";
      actionHistory.length=0;renderHashHistory(actionHistory,historyBox,model.didactic,model.main_c);
      if(data.visual_state){visualState=data.visual_state;model.visual_state=data.visual_state;renderHashState(visualState,visualContainer);}
      invalidateTrace("Tabla restablecida. Prepara una operación.");
    }catch(error){showHashMessage("No se pudo confirmar el restablecimiento. Recarga para comprobar el estado de la sesión.",false);}
    finally{pendingExecution=false;resetButton.disabled=false;setSimulationButtonsEnabled();}
  });

  simPlayButton?.addEventListener("click", async () => {
    const current = operations.find((item) => item.name === operationSelect.value);
    if (!current || !isCurrentSelectionValid()) { form.reportValidity?.(); return; }
    const payload = collectPayload(current);
    const executed = await executeOperationAndLoadTrace(current, payload, buildSelectionKey(current, payload), { finalOnly: !isStepByStepEnabled() });
    if (executed && isStepByStepEnabled() && tracePlayer?.hasTrace() && !visualState?.suspended && isCurrentSelectionValid()) tracePlayer.reset();
  });

  simPrevButton?.addEventListener("click", () => {
    if (!isStepByStepEnabled()) {
      return;
    }
    tracePlayer?.prev();
  });

  simStepButton?.addEventListener("click", () => {
    stepToggle.checked = !stepToggle.checked;
    stepToggle.dispatchEvent(new Event("change"));
  });

  simNextButton?.addEventListener("click", async () => {
    if (!isStepByStepEnabled() || !tracePlayer?.hasTrace()) return;
    const ready = await ensureTraceForCurrentSelection();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    await tracePlayer.step();
    setSimulationButtonsEnabled();
  });

  stepToggle?.addEventListener("change", () => {
    simStepButton.textContent = isStepByStepEnabled() ? "Cerrar paso a paso" : "Paso a paso";
    simStepButton.setAttribute("aria-pressed", String(isStepByStepEnabled()));
    tracePlayer?.pause(true);
    if (tracePlayer?.hasTrace()) tracePlayer.seek(isStepByStepEnabled() ? -1 : tracePlayer.getTotalSteps() - 1);
    setSimulationButtonsEnabled();
  });
  if (stepToggle) { stepToggle.checked = false; stepToggle.hidden = true; }
  simPrevButton.textContent = "Paso anterior";
  simNextButton.textContent = "Siguiente paso";
  setSimulationButtonsEnabled();


}


// Presentation-only classroom v1; existing render targets retain their identity.
function hashMountClassroomView() {
  if (!window.ClassroomView) return;
  const root = document.querySelector(".hash-primary-workspace");
  if (!root) return;
  // Also upgrade an already cached server template without replacing control nodes.
  const viewToolbar = root.querySelector(".hash-view-toolbar");
  if (viewToolbar && !viewToolbar.closest(".hash-view-options")) {
    const options = document.createElement("details"), summary = document.createElement("summary");
    options.className = "hash-view-options"; summary.textContent = "Opciones de representación";
    viewToolbar.before(options); options.append(summary, viewToolbar);
  }
  root.querySelectorAll("#hash-visual-region > h4").forEach(heading => {
    if (heading.textContent.trim() === "Estado visual") heading.remove();
  });
  document.getElementById("hash-code-region")?.classList.add("classroom-code");
  document.getElementById("hash-code-region")?.classList.remove("didactic-technical");
  const history = document.getElementById("action-history");
  const consoleNode = document.getElementById("hash-printf-console");
  const record = document.getElementById("tad-record");
  const results = [
    {label:"Consola C (printf)",panel:consoleNode?.closest("section"),code:consoleNode,getText:()=>consoleNode?.dataset.consoleCopy || ""},
    {label:"main.c del historial",panel:history?.parentElement,code:history,getText:()=>history?.dataset.rawCode || ""},
    {label:"Estructura del TAD",panel:record?.parentElement,code:record,getText:()=>record?.dataset.rawCode ?? record?.textContent ?? ""}
  ];
  results.forEach(entry=>{
    entry.panel?.classList.remove("didactic-technical");
    for(let node=entry.panel?.parentElement;node && node.tagName!=="ARTICLE";node=node.parentElement) {
      node.classList.remove("didactic-technical", "seq-pilot-collapsed");
      node.hidden = false;
      if(node.tagName==="DETAILS") node.open=true;
    }
  });
  window.ClassroomView.mount({root,visual:"#hash-visual-region",stage:"#hash-visual-state",code:"#op-pseudocode",memory:[".hash-live-memory-panel"],results,key:"hash"});
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.HASH_VIEW_MODEL) {
    initHashPage(window.HASH_VIEW_MODEL);
    hashMountClassroomView();
  }
});
