// Canonical-book presentation: return value, status and ownership are distinct.
function gGraphPhaseLabel(frame) {
  if(!frame?.book_instruction_model)return window.ContextualHelp?.phaseLabel(frame) || frame?.phase?.label || '—';
  return ({initial:'Estado inicial',caller_prepare:'Preparar argumentos',caller_receipt:'Recibir retorno',caller_prepare_release:'Preparar liberación',application_result:'Publicar resultado',api_publication:'Publicar resultado de la aplicación',api_rejection:'Rechazar solicitud antes de ejecutar C',enter:'Entrar en la función',parameter:'Recibir parámetro',scope_enter:'Entrar en el bloque',scope_exit:'Salir del bloque',declare:'Declarar variable',write:'Escribir un valor',condition:'Comprobar condición',operand:'Evaluar operando',allocate:'Reservar memoria',free:'Liberar memoria',call:'Llamar función',return:'Retornar',function_exit:'Volver al llamador',stdout:'Escribir en la consola',break:'Salir del bucle',continue:'Continuar el bucle'})[frame.instruction_event?.phase || frame.concept] || 'Instrucción C';
}
function gGraphTeachingFrame(frame) {
  if(!frame?.book_instruction_model)return frame;
  const projected={...frame,phase:{...frame.phase,label:gGraphPhaseLabel(frame)},variables:(frame.variables||[]).map(v=>({...v,value:v.value?.value_status==='indeterminate_after_free'?gTeachingValue(v.value):v.value,previous:v.previous?.value_status==='indeterminate_after_free'?gTeachingValue(v.previous):v.previous}))};
  const event=frame.instruction_event || {},value=event.value;
  if(value && typeof value==='object' && ['write','return'].includes(event.phase)){
    const text=event.phase==='write'?`Escribe ${event.name || 'el agregado'}: ${gTeachingValue(value)}.`:`Retorna el agregado: ${gTeachingValue(value)}. Las cabezas del caller se publican al recibir el retorno.`;
    projected.narration={...frame.narration,basic:text,intermediate:text};
  }
  return projected;
}
function gBookNoTraceMarkup(data) {
  return `<ul><li><strong>Resultado normal sin traza:</strong> la llamada C ya terminó; no hay instrucciones guardadas para avanzar o retroceder.</li><li><strong>Resultado registrado:</strong> ${gEscape(data.message || 'Consulta el resultado C y el estado final.')}</li><li><strong>Para estudiar los pasos:</strong> usa un grafo menor o una operación dentro del presupuesto de traza. El resultado actual no se convierte en pasos inventados.</li></ul>`;
}
function gBookStatusMarkup(record) {
  if (!record || record.source_contract !== 'graph-book/v1') return '';
  const states=['Correcto','No se pudo reservar memoria','No existe el elemento o la ruta','Peso negativo no permitido','Ciclo negativo alcanzable','Grafo desconectado','Argumento o simetría no válidos','Resultado fuera de rango'];
  const status=record.c_status;
  const text=Number.isInteger(status) ? `${record.c_status_name} (${status}): ${states[status] || 'estado registrado'}` : 'Esta función no entrega GrafoEstado.';
  const returned=record.c_return;
  const value=typeof returned==='object' ? gTeachingValue(returned) : String(returned ?? 'void');
  const ownership=record.ownership==='borrowed'?' Lista prestada del grafo: no se libera como resultado propio.':record.ownership==='owned'?(returned==='NULL'?' No hay nodos devueltos que liberar.':' Lista propia: el caller conserva el contenido y libera los nodos después de recibirlos.'):'';
  return `<p class="graph-book-status"><strong>Contrato C:</strong> ${gEscape(text)} <strong>Retorno C registrado:</strong> ${gEscape(value)}.${returned==='NULL' && status===0?' NULL con GRAFO_OK es un resultado vacío válido, no un error.':''}${ownership}</p>`;
}
function gBookFunctionLine(source, symbol) {
  if (!/^[A-Za-z_]\w*$/.test(symbol || '')) return -1;
  const pattern=new RegExp('^\\s*(?:static\\s+)?(?:void|int|long\\s+long|size_t|Grafo|ListaVertice|ListaArco)\\s*\\**\\s*'+symbol+'\\s*\\(');
  return String(source).replaceAll('\r\n','\n').split('\n').findIndex(line=>pattern.test(line));
}
function gFocusBookFunction(model, operationName) {
  const code=gById('op-pseudocode'), symbol=model.didactic?.operation_functions?.[operationName];
  if(!code || !symbol)return;
  const index=gBookFunctionLine(code.dataset.rawCode || code.textContent,symbol);
  enhanceGraphCodeNavigation(index);
  if(index>=0)window.CCodeNavigation?.revealLine(code,code.querySelector(`.code-line[data-line="${index}"]`));
}
function gDownloadGraphJson(value, filename) {
  const blob=new Blob([JSON.stringify(value,null,2)],{type:'application/json'}),link=document.createElement('a');
  link.href=URL.createObjectURL(blob);link.download=filename;link.click();URL.revokeObjectURL(link.href);
}
function gUpdateBookMainAvailability(model) {
  const link=gById('graph-download-main');if(!link)return;
  if(!link.dataset.downloadHref)link.dataset.downloadHref=link.getAttribute?.('href') || '';
  if(model.main_unavailable_reason){link.removeAttribute('href');link.setAttribute('aria-disabled','true');link.textContent='main.c no disponible: '+model.main_unavailable_reason;}
  else {if(link.dataset.downloadHref)link.setAttribute('href',link.dataset.downloadHref);link.removeAttribute('aria-disabled');link.textContent='Descargar main.c';}
}
function initSuspendedBookGraph(model) {
  const reason=model.main_unavailable_reason || model.visual_state?.suspension_reason || 'Historial de otro contrato C: estado suspendido, no vacío.';
  const controls=gById('graph-controls');
  document.querySelectorAll('.graph-workspace button, .graph-workspace input, .graph-workspace select').forEach(el=>{el.disabled=true;});
  renderGraphState(model.visual_state,gById('graph-visual-state'));
  const memory=gById('graph-live-memory');if(memory)memory.textContent='El estado anterior no se reconstruye con otro código C. Exporta el historial antes de restablecer.';
  const history=gById('action-history');if(history)history.innerHTML=`<li>${gEscape(reason)}</li>`;
  const main=gById('graph-download-main');if(main){main.removeAttribute('href');main.setAttribute('aria-disabled','true');main.textContent='main.c no disponible para este historial';}
  showGraphMessage(reason,false);
  const exportButton=gById('graph-export-summary');
  if(exportButton){exportButton.disabled=false;exportButton.textContent='Exportar historial original';exportButton.addEventListener('click',async()=>{
    exportButton.disabled=true;
    try{const response=await fetch(controls.dataset.historyUrl);if(!response.ok)throw new Error('No se pudo exportar el historial.');gDownloadGraphJson(await response.json(),'graph-history-original.json');}
    catch(error){showGraphMessage(error.message,false);}finally{exportButton.disabled=false;}
  });}
  const reset=gById('graph-reset-button');
  if(reset){reset.disabled=false;reset.addEventListener('click',async()=>{
    if(!window.confirm('¿Borrar el historial de esta sesión y empezar un grafo nuevo con el C del libro? Exporta primero si necesitas conservarlo.'))return;
    reset.disabled=true;
    try{const response=await fetch(controls.dataset.resetUrl,{method:'POST'}),data=await response.json();if(!response.ok || !data.success)throw new Error(data.message || 'No se pudo restablecer.');window.location.reload();}
    catch(error){showGraphMessage(error.message,false);reset.disabled=false;}
  });}
  updateGraphDidacticPanel(model,'create_graph');
}

// Numeric Graph only: exact versioned subtree references, reconstructed once.
// Shared frozen objects make replay read-only and avoid duplicated snapshots.
function gExpandGraphInstructionTrace(trace) {
  if (!trace || !trace.graph_snapshot_codec) return trace;
  if (trace.graph_snapshot_codec !== "graph-snapshot-pool/v1") throw new Error("Codec Graph no compatible");
  const objects = [];
  function decode(value) {
    if (value && typeof value === "object") {
      const keys = Object.keys(value), id = value.$graph_ref;
      if (Array.isArray(value) || keys.length !== 1 || keys[0] !== "$graph_ref" || !Number.isInteger(id) || id < 0 || id >= objects.length) throw new Error("Referencia Graph inválida");
      return objects[id];
    }
    return value;
  }
  for (const record of trace.graph_snapshot_pool) {
    if (!Array.isArray(record) || record.length !== 2 || ![0, 1].includes(record[0]) || !Array.isArray(record[1])) throw new Error("Registro Graph inválido");
    let value;
    if (record[0] === 0) {
      const keys = record[1].map(item => item[0]);
      if (keys.some(k => typeof k !== "string") || new Set(keys).size !== keys.length) throw new Error("Claves Graph inválidas");
      value = Object.fromEntries(record[1].map(([key, child]) => [key, decode(child)]));
    } else value = record[1].map(decode);
    objects.push(Object.freeze(value));
  }
  const {graph_snapshot_codec, graph_snapshot_pool, graph_snapshot_stats, ...expanded} = trace;
  expanded.steps = trace.steps.map(step => Object.freeze(Object.fromEntries(Object.entries(step).map(([key, value]) => [key, value && typeof value === "object" && !Array.isArray(value) && Object.prototype.hasOwnProperty.call(value, "$graph_ref") ? decode(value) : value]))));
  if (trace.numeric_C_memory) expanded.numeric_C_memory = decode(trace.numeric_C_memory);
  return expanded;
}

"use strict";

// Presentation only: identities and C field names remain exact; raw frames stay available.
function gTeachingValue(value) {
  if (value && typeof value === "object" && value.value_status === "indeterminate_after_free" && value.usable === false) return `valor indeterminado tras liberar; no utilizar (identidad histórica ${value.historical_identity})`;
  if (value === undefined) return "no registrado";
  if (value === null) return "sin valor";
  if (Array.isArray(value)) return value.length ? value.map(gTeachingValue).join(", ") : "vacío";
  if (typeof value === "object") return Object.entries(value).map(([key,item]) => `${key}: ${gTeachingValue(item)}`).join(" · ");
  return String(value);
}
function gGraphNodeFields(node) {
  if (node.fields !== undefined) return node.fields;
  if (node.items !== undefined) return node.items;
  const fields={value:node.kind==='queue'?'nro':'dato',next:node.kind==='queue'?'sgte':'sig',mark:'marcado',origin:'origen',target:'destino',weight:'costo'};
  return Object.fromEntries(Object.entries(node).filter(([key])=>!['id','kind','borrowed'].includes(key)).map(([key,value])=>[fields[key]||key,value]));
}
function gGraphNodeKind(kind) {
  return ({vertex:'vértice (NodoV)',arc:'arco (NodoA)',queue:'cola (NodoCola)',result:'resultado (NodoV)',successor:'sucesor (NodoV)'})[kind] || kind || 'reserva';
}
function gGraphMemoryMarkup(frame) {
  const st=frame.memory_display || frame.memory_state, nodes=st?.heap_nodes || frame.memory?.objects_after || [];
  const changed=new Set([...(frame.memory?.allocated||[]),...(frame.variables||[]).filter(v=>v.changed).map(v=>v.value)].map(v=>String(v?.id ?? v)));
  const source=[frame.source?.line_text,frame.condition?.source,frame.instruction_event?.statement].filter(Boolean).map(String).join("\n");
  const identifiers=new Set(source.match(/[A-Za-z_]\w*/g)||[]);
  const allVariables=frame.variables||[];
  const stack=frame.call_stack||[];
  const scopeRank=v=>{const index=stack.findIndex(f=>v.frame_id ? f.frame_id===v.frame_id : f.function===v.scope);return index;};
  const latest=new Map();
  for(const variable of allVariables)if(!latest.has(variable.name)||scopeRank(variable)>=scopeRank(latest.get(variable.name)))latest.set(variable.name,variable);
  const variables=[...latest.values()];
  const repeated=new Set(allVariables.filter((v,i)=>allVariables.findIndex(other=>other.name===v.name)!==i).map(v=>v.name));
  const referenced=variables.filter(v=>identifiers.has(v.name));
  const activeIds=new Set(referenced.flatMap(v=>typeof v.value==='object' && v.value ? Object.values(v.value) : [v.value]).map(String));
  const fieldValues=new Map(),activeFieldIds=new Set();
  for(const variable of referenced){
    if(!/^[A-Za-z_]\w*$/.test(variable.name)||!variable.value||typeof variable.value!=='object'||Array.isArray(variable.value))continue;
    const pattern=new RegExp('\\b'+variable.name+'\\s*(?:\\.|->)\\s*([A-Za-z_]\\w*)','g');
    const fields=[...new Set([...source.matchAll(pattern)].map(match=>match[1]))].filter(field=>Object.prototype.hasOwnProperty.call(variable.value,field));
    if(fields.length){fieldValues.set(variable,Object.fromEntries(fields.map(field=>[field,variable.value[field]])));fields.forEach(field=>{if(typeof variable.value[field]==='string')activeFieldIds.add(variable.value[field]);});}
  }
  const rank=n=>activeFieldIds.has(String(n.id))?3:activeIds.has(String(n.id))?2:changed.has(String(n.id))?1:0;
  const ordered=[...nodes].sort((a,b)=>rank(b)-rank(a));
  const vars=[...variables].filter(v=>identifiers.has(v.name)||v.changed||typeof v.value!=='object').sort((a,b)=>Number(identifiers.has(b.name))-Number(identifiers.has(a.name))||Number(Boolean(b.changed))-Number(Boolean(a.changed))).slice(0,6);
  return `<p class="graph-memory-context">${st?.graph ? `Cabezas C: ${gEscape(gTeachingValue(st.graph))}` : "Identidades simbólicas, no direcciones reales."}</p><div class="graph-live-variables">${vars.map(v=>`<span><code>${gEscape(v.name)}</code>${repeated.has(v.name)?` <small>(${gEscape(v.scope||v.frame_id||"ámbito actual")})</small>`:""} = ${gEscape(gTeachingValue(fieldValues.get(v) || v.value))}</span>`).join(" · ")}</div><div class="graph-live-cards">${ordered.map(n=>`<div class="graph-memory-card" data-graph-live-node="${gEscape(n.id)}"><strong>${gEscape(n.id)}</strong> <small>${gEscape(gGraphNodeKind(n.kind))}${n.borrowed ? " · prestado" : ""}</small><div>${gEscape(gTeachingValue(gGraphNodeFields(n)) )}</div></div>`).join("") || "Sin reservas registradas en este paso."}</div>`;
}
function initGraphClassroom() {
  const workspace=document.querySelector('.graph-primary-workspace'), row=document.querySelector('.graph-control-row');
  if(!workspace || !row)return;
  const toolbar=document.createElement('section');toolbar.className='graph-classroom-controls';toolbar.setAttribute('aria-label','Controlar ejecución');
  toolbar.appendChild(row);
  ['graph-step-metadata','graph-sim-status'].forEach(id=>{const el=gById(id);if(el)toolbar.appendChild(el);});
  workspace.before(toolbar);
}

function renderGraphPedagogy(frame,level){
  if(!frame)return;
  const summary=gById("graph-pedagogy-summary"),representation=gById("graph-representation-view"),aux=gById("graph-auxiliary-view"),traversal=gById("graph-traversal-view"),table=gById("graph-table-view"),relaxation=gById("graph-relaxation-view"),condition=gById("graph-condition-view"),invariant=gById("graph-invariant-view");
  if(summary)summary.innerHTML=`<strong>${gEscape(gGraphPhaseLabel(frame))}</strong>: ${gEscape(frame.narration?.[level]||frame.narration?.intermediate||"")}`;
  window.ContextualHelp?.frame("graph", gGraphTeachingFrame(frame), level);
  if(representation){const adjacency=frame.representation?.adjacency||{},degrees=frame.representation?.degrees||[];representation.innerHTML=`<p><strong>${frame.representation?.directed?"Arcos dirigidos (→)":"Aristas no dirigidas (—)"}</strong></p><ul>${Object.entries(adjacency).map(([vertex,items])=>`<li><code>${gEscape(vertex)}</code>: ${items.length?items.map((item)=>`${gEscape(item.vertex)}(${gEscape(item.weight)})`).join(", "):"∅"}</li>`).join("")}</ul><p>${degrees.map((item)=>frame.representation?.directed?`${gEscape(item.vertex)}: entrada ${item.in_degree}, salida ${item.out_degree}`:`${gEscape(item.vertex)}: grado ${item.degree}`).join(" · ")}</p><p>Reservados: ${frame.memory?.allocated?.length||0}; liberados: ${frame.memory?.freed?.length||0}; ${frame.book_instruction_model ? `referencias a reservas retiradas: ${frame.memory?.retired_references?.length||0}. No se certifica la ausencia de otros punteros inválidos` : `punteros colgantes: ${frame.memory?.dangling_references?.length||0}`}</p>`;}
  if(aux)aux.innerHTML=`<strong>${gEscape(frame.auxiliary?.kind||"—")}</strong><br>Contenido: <code>${gEscape(JSON.stringify(frame.auxiliary?.items||[]))}</code><br>Seleccionado: ${gEscape(frame.auxiliary?.selected??"—")} · Iteración: ${gEscape(frame.auxiliary?.iteration??"—")}`;
  if(traversal)traversal.innerHTML=`${frame.book_instruction_model?"Arcos de la lista C actual":"Árbol/bosque"}: <code>${gEscape(JSON.stringify(frame.traversal?.tree_edges||[]))}</code><br>Orden descubierto: <code>${gEscape(JSON.stringify(frame.traversal?.discovery_order||[]))}</code><br>Activo: ${gEscape(frame.traversal?.active??"—")}`;
  if(table)table.innerHTML=`<table><thead><tr><th>Vértice</th><th>Estado</th><th>Distancia</th><th>Predecesor</th><th>Iteración</th></tr></thead><tbody>${(frame.vertices||[]).map((item)=>`<tr><td>${gEscape(item.id)}</td><td>${gEscape(item.status)}</td><td>${gEscape(item.distance??(frame.book_instruction_model?"no alcanzado / no calculado":"∞"))}</td><td>${gEscape(item.predecessor??"—")}</td><td>${gEscape(frame.auxiliary?.iteration??"—")}</td></tr>`).join("")}</tbody></table>`;
  if(relaxation)relaxation.innerHTML=frame.relaxation?`<code>${gEscape(frame.relaxation.expression)}</code><br>${gEscape(frame.relaxation.old_distance??"∞")} &gt; ${gEscape(frame.relaxation.candidate??"∞")} ⇒ <strong>${frame.relaxation.success?"relajación exitosa":"sin cambio"}</strong><br>Nuevo valor: ${gEscape(frame.relaxation.new_distance??"∞")}; predecesor: ${gEscape(frame.relaxation.predecessor??"—")}`:"No se evalúa una relajación en este paso.";
  if(condition)condition.innerHTML=frame.condition?`<code>${gEscape(frame.condition.substituted)}</code> ⇒ <strong>${gEscape(frame.condition.result)}</strong><br>${gEscape(frame.condition.consequence)}`:`Arista activa: ${gEscape(frame.active_edge?`${frame.active_edge.from} → ${frame.active_edge.to} (peso ${frame.active_edge.weight})`:"—")}`;
  if(frame.memory_state && frame.vertex_operation){
    const st=frame.memory_display || frame.memory_state;
    if(representation)representation.innerHTML+=`<div data-graph-instruction-memory><h4>Memoria C por instrucción</h4><p data-graph-heads>${frame.instruction_event?.origin === "caller" ? "Cabezas del caller C (retira incidentes tras el retorno):" : "Cabezas C (arcos conservados por esta función):"} ${gEscape(JSON.stringify(st.graph))}</p>${(st.heap_nodes||[]).map(n=>`<div data-graph-memory-node="${gEscape(n.id)}" data-graph-memory-kind="${gEscape(n.kind)}"><strong>${gEscape(n.id)}</strong> ${gEscape(n.kind)} · ${n.borrowed?"prestado":"propio"}: <code>${gEscape(JSON.stringify(n.fields||n.items))}</code></div>`).join("")}<p data-graph-retired>Retiradas (sólo registro histórico): ${gEscape(JSON.stringify(st.retired_objects||[]))}</p></div>`;
    if(aux)aux.innerHTML+=`<div data-graph-variables>${(frame.variables||[]).map(v=>`<div data-graph-variable="${gEscape(v.name)}" data-graph-scope="${gEscape(v.scope)}">${gEscape(v.type)} ${gEscape(v.name)} (${gEscape(v.scope)}): ${gEscape(JSON.stringify(v.previous))} → ${gEscape(JSON.stringify(v.value))}</div>`).join("")}</div><div data-graph-frames>${(frame.call_stack||[]).map(f=>`<div data-graph-frame="${gEscape(f.frame_id)}">${gEscape(f.function)}: ${gEscape(f.scope_status)}</div>`).join("")}</div>`;
    if(traversal)traversal.innerHTML+=`<p data-graph-return>${frame.instruction_event?.origin === "caller" ? "Retorno C registrado (identidades retiradas no utilizables):" : "Retorno al caller:"} ${gEscape(JSON.stringify(st.returned))}</p>`;
  }else if(frame.memory_state && (frame.numeric_algorithm || frame.query_operation || frame.construction_operation)){
    const st=frame.memory_display || frame.memory_state;
    if(representation)representation.innerHTML+=`<div data-graph-instruction-memory><h4>Memoria C por instrucción</h4><p data-graph-heads>${frame.construction_operation ? "Cabezas del caller propietario:" : "Grafo prestado:"} ${gEscape(JSON.stringify(st.graph))}</p>${(st.heap_nodes||[]).map(n=>`<div data-graph-memory-node="${gEscape(n.id)}" data-graph-memory-kind="${gEscape(n.kind)}"><strong>${gEscape(n.id)}</strong> ${gEscape(n.kind)} · ${n.borrowed?"prestado":"propio"}: <code>${gEscape(JSON.stringify(n.fields||n.items))}</code></div>`).join("")}<p data-graph-retired>Retiradas (sólo registro histórico): ${gEscape(JSON.stringify(st.retired_objects||[]))}</p></div>`;
    if(aux)aux.innerHTML+=`<div data-graph-variables>${(frame.variables||[]).map(v=>`<div data-graph-variable="${gEscape(v.name)}" data-graph-scope="${gEscape(v.scope)}">${gEscape(v.type)} ${gEscape(v.name)} (${gEscape(v.scope)}): ${gEscape(JSON.stringify(v.previous))} → ${gEscape(JSON.stringify(v.value))}</div>`).join("")}</div><div data-graph-frames>${(frame.call_stack||[]).map(f=>`<div data-graph-frame="${gEscape(f.frame_id)}">${gEscape(f.function)}: ${gEscape(f.scope_status)}</div>`).join("")}</div>`;
    if(traversal)traversal.innerHTML+=`<p data-graph-return>Retorno al caller: ${gEscape(frame.query_operation ? JSON.stringify(st.returned) : frame.construction_operation ? JSON.stringify(st.returned) : st.returned)}</p>`;
  }else if(frame.memory_state){
    const st=frame.memory_display || frame.memory_state;
    if(representation)representation.innerHTML+=`<div data-bfs-memory><h4>Reservas y enlaces C (identidades simbólicas)</h4>${st.heap_nodes.map(n=>`<div data-bfs-node="${gEscape(n.id)}" data-bfs-kind="${gEscape(n.kind)}"><strong>${gEscape(n.id)}</strong> ${gEscape(JSON.stringify(n))}</div>`).join("")}<p>Retiradas: ${gEscape(JSON.stringify(st.freed_nodes))}</p></div>`;
    if(aux)aux.innerHTML+=`<p data-bfs-queue>${gEscape(JSON.stringify(st.queue))}</p><div data-bfs-variables>${frame.variables.map(v=>`<div data-bfs-variable="${gEscape(v.name)}" data-bfs-scope="${gEscape(v.scope)}">${gEscape(v.type)} ${gEscape(v.name)} (${gEscape(v.scope)}): ${gEscape(JSON.stringify(v.previous))} → ${gEscape(JSON.stringify(v.value))}</div>`).join("")}</div><div data-bfs-frames>${frame.call_stack.map(f=>`<div data-bfs-frame="${gEscape(f.frame_id)}">${gEscape(f.function)}: ${gEscape(f.scope_status)}</div>`).join("")}</div>`;
    if(st.head_storage && representation)representation.innerHTML+=`<p data-dfs-head-storage>${gEscape(JSON.stringify(st.head_storage))}</p>`;
    if(traversal)traversal.innerHTML+=`<p data-bfs-output>Recorrido publicado: ${gEscape(JSON.stringify(st.result_nodes.map(n=>n.value)))}</p><p>Retorno al caller: ${gEscape(st.published)}</p>`;
  }
  if(invariant)invariant.innerHTML=`<strong>${gEscape(frame.invariant?.symbol||"")} ${gEscape(frame.invariant?.name||"")}</strong><br>${gEscape(frame.invariant?.evidence||"")}`;
  const live=gById('graph-live-memory');if(live)live.innerHTML=gGraphMemoryMarkup(frame);
  // Preserve the complete original diagnostics, but do not make raw JSON the lesson.
  for(const [panel,title,content] of [
    [representation,'Representación y memoria técnica',gGraphMemoryMarkup(frame)],
    [aux,'Auxiliares y ámbitos técnicos',`<p>${gEscape(({adjacency:'Lista de adyacencia',queue:frame.book_instruction_model?'Cola de índices (Trabajo.prev)':'Cola',stack:'Pila',recursive_stack:'Pila recursiva',linear_scan:'Búsqueda lineal',edge_passes:'Pasadas por arcos',union_find:'Conjuntos disjuntos',priority_queue:'Cola de prioridad',none:'Sin auxiliar'}[frame.auxiliary?.kind] || 'Auxiliar actual'))}: ${gEscape(gTeachingValue(frame.auxiliary?.items||[]))}</p>`]
  ])if(panel)panel.innerHTML=content+`<details><summary>${title}</summary>${panel.innerHTML}</details>`;
  if(table)table.innerHTML=table.innerHTML.replace(/>undiscovered</g,'>No descubierto<').replace(/>frontier</g,'>Frontera<').replace(/>active</g,'>Activo<').replace(/>closed</g,'>Cerrado<');

}

function enhanceGraphCodeNavigation(activeLine=null){const code=gById("op-pseudocode"),list=gById("graph-function-list"),hide=gById("graph-hide-comments");if(!code||!list)return;const raw=String(code.dataset.rawCode||code.textContent||"");const rows=raw.replaceAll("\r\n","\n").split("\n"),functions=[];rows.forEach((row,index)=>{const match=row.match(/^\s*(?:static\s+)?(?:void|bool|int|double|size_t|Grafo|Lista\w*)\s*\**\s*([A-Za-z_]\w*)\s*\(/);if(match&&!['if','for','while','switch'].includes(match[1]))functions.push({name:match[1],line:index});});window.CCodeNavigation?.markComments(code, rows);const active=[...functions].reverse().find((item)=>Number.isInteger(activeLine)&&item.line<=activeLine)||functions[0];list.innerHTML=functions.length?functions.map((item)=>`<li><button type="button" class="${active?.line===item.line?'is-active':''}" data-line="${item.line}">${gEscape(item.name)}</button></li>`).join(""):'<li>Sin funciones detectadas</li>';list.querySelectorAll("button").forEach((button)=>button.addEventListener("click",()=>window.CCodeNavigation?.revealLine(code,code.querySelector(`.code-line[data-line="${button.dataset.line}"]`))));code.classList.toggle("hide-hier-comments",Boolean(hide?.checked));}

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
  if (!["run_bfs", "run_dfs", "run_dijkstra", "run_bellman_ford", "run_prim", "run_kruskal"].includes(entry.operation) && gBuildHistoryEntrySignature(last) === gBuildHistoryEntrySignature(entry)) {
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
  consoleEl.dataset.consoleCopy = safeLines.join("\n");
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
  if (/c[oó]digo c/i.test(String(codeTitle || ""))) {
    let state = { inBlockComment: false };
    return lines
      .map((line, index) => {
        const highlighted = highlightGraphCLine(line, state);
        state = highlighted.state;
        return `<span class="code-line" data-line="${index}">${highlighted.html || ""}</span>`;
      })
      .join("");
  }
  return lines
    .map((line, index) => `<span class="code-line" data-line="${index}">${gEscape(line) || ""}</span>`)
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
        input.step = field.step === undefined ? "any" : String(field.step);
        if (field.min !== undefined) input.min = String(field.min);
        if (field.max !== undefined) input.max = String(field.max);
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

// Geometry is presentation-only. Reciprocal arcs get separate lanes; loops stay visible.
function gGraphRoutes(positions, edges, nodeRadius=26) {
  const center=[...positions.values()].reduce((s,p)=>s+p.x,0)/(positions.size||1);
  const groups=new Map();
  edges.forEach((e,i)=>{const key=JSON.stringify([String(e.source),String(e.target)].sort());if(!groups.has(key))groups.set(key,[]);groups.get(key).push(i);});
  return edges.map((edge,index)=>{
    const a=positions.get(String(edge.source)),b=positions.get(String(edge.target));if(!a||!b)return null;
    const peers=groups.get(JSON.stringify([String(edge.source),String(edge.target)].sort()));
    if(String(edge.source)===String(edge.target)){
      const side=a.x>=center?1:-1,reach=82+peers.indexOf(index)*26;
      const p0={x:a.x+side*nodeRadius*.8,y:a.y-nodeRadius*.6},p3={x:a.x+side*nodeRadius*.8,y:a.y+nodeRadius*.6};
      const p1={x:a.x+side*reach,y:a.y-55},p2={x:a.x+side*reach,y:a.y+55};
      const point=t=>({x:(1-t)**3*p0.x+3*(1-t)**2*t*p1.x+3*(1-t)*t*t*p2.x+t**3*p3.x,y:(1-t)**3*p0.y+3*(1-t)**2*t*p1.y+3*(1-t)*t*t*p2.y+t**3*p3.y});
      return {edge,loop:true,point,control:[p0,p1,p2,p3],d:`M ${p0.x} ${p0.y} C ${p1.x} ${p1.y}, ${p2.x} ${p2.y}, ${p3.x} ${p3.y}`};
    }
    const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;
    // Canonical normal ensures both directions occupy distinct sides.
    const canonical=String(edge.source)<String(edge.target)?1:-1;
    const lane=peers.length>1?(peers.indexOf(index)-(peers.length-1)/2)*50:0;
    const c={x:(a.x+b.x)/2-dy/len*lane*canonical,y:(a.y+b.y)/2+dx/len*lane*canonical};
    const al=Math.hypot(c.x-a.x,c.y-a.y)||1,bl=Math.hypot(c.x-b.x,c.y-b.y)||1;
    const p0={x:a.x+(c.x-a.x)/al*nodeRadius,y:a.y+(c.y-a.y)/al*nodeRadius};
    const p2={x:b.x+(c.x-b.x)/bl*(nodeRadius+3),y:b.y+(c.y-b.y)/bl*(nodeRadius+3)};
    const point=t=>({x:(1-t)**2*p0.x+2*(1-t)*t*c.x+t*t*p2.x,y:(1-t)**2*p0.y+2*(1-t)*t*c.y+t*t*p2.y});
    return {edge,loop:false,point,control:[p0,c,p2],d:`M ${p0.x} ${p0.y} Q ${c.x} ${c.y} ${p2.x} ${p2.y}`};
  });
}
function gPlaceGraphWeightLabels(positions, edges, nodeRadius=26, routes=gGraphRoutes(positions,edges,nodeRadius)) {
  const nodes=[...positions.values()],placed=[];
  const overlaps=(a,b)=>a.left<b.right && a.right>b.left && a.top<b.bottom && a.bottom>b.top;
  const inside=(p,b)=>p.x>b.left&&p.x<b.right&&p.y>b.top&&p.y<b.bottom;
  const nodeBoxes=nodes.map(n=>({left:n.x-nodeRadius-8,right:n.x+nodeRadius+8,top:n.y-nodeRadius-8,bottom:n.y+nodeRadius+8}));
  routes.forEach((route,index)=>{
    if(!route)return;const edge=route.edge,width=Math.max(24,String(edge.weight).length*10+12),height=26;
    let best=null;
    for(const t of [.5,.38,.62,.26,.74,.17,.83]){
      const anchor=route.point(t),before=route.point(Math.max(0,t-.01)),after=route.point(Math.min(1,t+.01)),dx=after.x-before.x,dy=after.y-before.y,len=Math.hypot(dx,dy)||1;
      for(const offset of [0,18,-18,30,-30,44,-44,62,-62]){
        const x=anchor.x-dy/len*offset,y=anchor.y+dx/len*offset;
        const box={left:x-width/2,right:x+width/2,top:y-height/2,bottom:y+height/2};
        const conflicts=nodeBoxes.filter(b=>overlaps(box,b)).length+placed.filter(p=>overlaps(box,p.box)).length;
        let crossings=0;
        routes.forEach((other,j)=>{if(!other||j===index)return;for(let k=1;k<30;k++)if(inside(other.point(k/30),box)){crossings++;break;}});
        const score=conflicts*100000+crossings*600+Math.abs(offset)*2+Math.abs(t-.5)*30;
        if(!best||score<best.score)best={edge,x,y:y+5,box,midpoint:anchor,shifted:Math.abs(offset)>12,score};
      }
    }
    // Dense graphs can need an outer label; never knowingly overlap a node/label.
    if(best.score>=100000){
      const anchor=route.point(.5);
      search:for(let ring=1;ring<100;ring++)for(let k=0;k<16;k++){
        const x=anchor.x+ring*24*Math.cos(k*Math.PI/8),y=anchor.y+ring*24*Math.sin(k*Math.PI/8);
        const box={left:x-width/2,right:x+width/2,top:y-height/2,bottom:y+height/2};
        if(!nodeBoxes.some(b=>overlaps(box,b))&&!placed.some(p=>overlaps(box,p.box))){best={edge,x,y:y+5,box,midpoint:anchor,shifted:true,score:0};break search;}
      }
    }
    placed.push(best);
  });
  return placed;
}

function renderGraphSvg(state, simulation, traceDebug) {
  const nodes = Array.isArray(state.nodes) ? state.nodes : [];
  const edges = Array.isArray(state.edges) ? state.edges : [];

  if (!nodes.length) {
    return "<p class=\"viz-empty\">Grafo vacío. Crea vértices para iniciar.</p>";
  }

  const nodeRadius = 26;
  const positions = gAdaptiveGraphPositions(nodes, edges);
  const routes=gGraphRoutes(positions,edges,nodeRadius);
  const weightLabels=gPlaceGraphWeightLabels(positions,edges,nodeRadius,routes);
  const geometry=[...[...positions.values()].flatMap(p=>[{x:p.x-nodeRadius-20,y:p.y-nodeRadius-24},{x:p.x+nodeRadius+20,y:p.y+nodeRadius+20}]),...routes.filter(Boolean).flatMap(r=>r.control),...weightLabels.flatMap(p=>[{x:p.box.left,y:p.box.top},{x:p.box.right,y:p.box.bottom}])];
  const left=Math.min(...geometry.map(p=>p.x))-16,top=Math.min(...geometry.map(p=>p.y))-16;
  const width=Math.max(...geometry.map(p=>p.x))-left+16,height=Math.max(...geometry.map(p=>p.y))-top+16;
  const opName = state.last_operation && state.last_operation.name ? state.last_operation.name : "";
  const useSimulation = simulation && simulation.sourceOperation === opName;
  const highlights = traceDebug
    ? getTraceDebugHighlights(traceDebug)
    : useSimulation
      ? getSimulationHighlights(simulation)
      : getDefaultHighlights(state);

  let svg = "";
  svg += `<svg class="viz-graph-svg" data-layout="adaptive" width="${width}" height="${height}" viewBox="${left} ${top} ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;
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

    const edgeKey = `${String(edge.source)}->${String(edge.target)}`;
    const isTraversalEdge = highlights.traversalEdges.has(edgeKey);
    const isMstEdge = highlights.mstEdges.has(edgeKey);
    const markerAttr = state.directed ? "marker-end=\"url(#arrow-head)\"" : "";
    const edgeClass = isMstEdge
      ? "viz-graph-edge mst"
      : isTraversalEdge
        ? "viz-graph-edge traversal"
        : "viz-graph-edge";
    const route=routes[index];
    svg+=`<path data-graph-source="${gEscape(edge.source)}" data-graph-target="${gEscape(edge.target)}" ${route.loop?`data-graph-self-loop="${gEscape(edge.source)}"`:""} d="${route.d}" fill="none" class="${edgeClass}" ${markerAttr}><title>${gEscape(`${edge.source} → ${edge.target}: ${edge.weight}`)}</title></path>`;


  });

  for(const label of weightLabels)if(label.shifted)svg+=`<line x1="${label.midpoint.x}" y1="${label.midpoint.y}" x2="${label.x}" y2="${label.y-5}" stroke="#937057" stroke-width="1" stroke-dasharray="3 3" aria-hidden="true" />`;

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
    svg += `<circle data-node-id=\"${gEscape(nodeId)}\" cx=\"${pos.x}\" cy=\"${pos.y}\" r=\"${nodeRadius}\" class=\"${nodeClass}\" />`;
    svg += `<text x=\"${pos.x}\" y=\"${pos.y + 5}\" text-anchor=\"middle\" class=\"viz-graph-label\">${gEscape(node.label)}</text>`;
    if (highlights.traversalOrder.has(nodeId)) {
      svg += `<text x=\"${pos.x + 19}\" y=\"${pos.y - 18}\" text-anchor=\"middle\" class=\"viz-graph-order\">${gEscape(highlights.traversalOrder.get(nodeId))}</text>`;
    }
  });

  for(const label of weightLabels){
    const title=`Costo del arco ${label.edge.source} → ${label.edge.target}: ${label.edge.weight}`;
    svg+=`<g data-weight-source="${gEscape(label.edge.source)}" data-weight-target="${gEscape(label.edge.target)}"><title>${gEscape(title)}</title><rect x="${label.box.left}" y="${label.box.top}" width="${label.box.right-label.box.left}" height="${label.box.bottom-label.box.top}" rx="4" fill="white" fill-opacity=".94" /><text x="${label.x}" y="${label.y}" text-anchor="middle" class="viz-graph-weight">${gEscape(label.edge.weight)}</text></g>`;
  }

  svg += "</svg>";
  return svg;
}

function formatShortestPathResult(state, result, label) {
  const path = Array.isArray(result.path) ? result.path.map((item) => String(item)) : [];
  const edges = Array.isArray(result.path_arcs) ? result.path_arcs.map(([source,target,weight])=>({source:String(source),target:String(target),weight})) : (state.c_arcs || state.edges || []);

  if (!path.length || result.reachable === false) {
    return `<p><strong>${label}:</strong> No existe ruta entre inicio y destino.</p>`;
  }

  let html = `<p><strong>${label}:</strong> ${gEscape(path.join(" → "))}</p>`;
  html += "<div class=\"viz-path-steps\">";
  for (let index = 0; index < path.length - 1; index += 1) {
    const from = path[index];
    const to = path[index + 1];
    const weight = findEdgeWeight(edges, from, to, true);
    html += `<p>${gEscape(from)} - ${gEscape(to)} (peso ${gEscape(weight)})</p>`;
  }
  html += "</div>";

  const totalWeight = result.distance_to_destination;
  const totalText = totalWeight === null || totalWeight === undefined ? "No disponible" : totalWeight;
  html += `<p><strong>Peso total:</strong> ${gEscape(totalText)}</p>`;
  return html;
}

function formatGraphResult(state) {
  const record=state.last_result;
  if(record?.source_contract==='graph-book/v1'){
    const status=gBookStatusMarkup(record);
    if(record.c_status !== null && record.c_status !== undefined && record.c_status !== 0)return status+`<p>${gEscape(record.message || 'La función no produjo un resultado válido.')}</p>`;
    if(state.last_operation?.name==='edge_weight')return status+(record.c_return===1?`<p><strong>Costo escrito:</strong> ${gEscape(record.output)}</p>`:'<p>No existe el arco: retorno 0, salida no escrita. No se interpreta como costo cero.</p>');
    return status+formatGraphResultBody(state);
  }
  return formatGraphResultBody(state);
}
function formatGraphResultBody(state) {
  const operationName = state.last_operation && state.last_operation.name ? state.last_operation.name : "";
  const result = state.last_result ? state.last_result.result : null;

  if(operationName === "list_edges" && Array.isArray(result))return `<p><strong>Arcos prestados, en orden C:</strong></p><ul>${result.map(a=>`<li>${gEscape(a[0])} → ${gEscape(a[1])} (costo ${gEscape(a[2])})</li>`).join("") || "<li>Lista vacía</li>"}</ul>`;
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

  if(result === null || result === undefined)return '<p>Sin lista o valor adicional de resultado.</p>';
  return `<p><strong>Resultado:</strong> ${gEscape(gTeachingValue(result))}</p>`;
}

function gGraphPresentedResult(state, context = {}) {
  if(context.idle)return '<p>Sin ejecución actual. Prepara una operación.</p>';
  const recorded=state?.last_operation?.name;
  if(context.pending || (context.operation && recorded !== context.operation)) return '<p><strong>Resultado actual:</strong> pendiente de completar la operación.</p>';
  return state?.last_result?.result !== undefined ? formatGraphResult(state) : '';
}
function gMaintainGraphImageViewport(container, previous={left:0,top:0}) {
  if(window.ClassroomView) return; // Shared manual zoom owns image geometry in v1.
  const stage=container.querySelector('.viz-stage'),svg=stage?.querySelector('svg'),note=container.querySelector('.graph-image-pan-note');
  if(!stage || !svg)return;
  const box=svg.viewBox?.baseVal,rect=svg.getBoundingClientRect();
  if(!box || !box.width || !box.height)return;
  const scale=Math.min(rect.width/box.width,rect.height/box.height);
  const pan=scale<.9;
  stage.classList.toggle('graph-local-pan',pan);
  if(note)note.hidden=!pan;
  if(pan){
    // Never shrink glyphs to fit a dense graph. Only this image area scrolls.
    svg.style.width=`${Math.max(stage.clientWidth,box.width)}px`;
    svg.style.height=`${Math.max(stage.clientHeight,box.height)}px`;
    svg.style.minWidth=`${box.width}px`;svg.style.minHeight=`${box.height}px`;
    svg.style.maxHeight='none';svg.style.maxWidth='none';
    stage.setAttribute('tabindex','0');
    stage.setAttribute('aria-label','Imagen ampliada. Desplaza esta área para ver todos los nodos y pesos; el código permanece fijo.');
    stage.scrollLeft=previous.left;stage.scrollTop=previous.top;
  }
}

function renderGraphState(state, container, simulation, traceDebug, presentation = {}) {
  if (!state || !container) {
    return;
  }

  if(state.suspended){container.innerHTML=`<div role="status"><h4>Historial suspendido — no es un grafo vacío</h4><p>${gEscape(state.suspension_reason || "Este historial pertenece a otra versión del C.")}</p><p>Exporta el historial original o confirma Restablecer grafo para empezar con el libro.</p></div>`;return;}
  const oldStage=container.querySelector(".viz-stage");
  const imageViewport={left:oldStage?.scrollLeft||0,top:oldStage?.scrollTop||0};
  const metadata = state.metadata || {};
  const graphType = state.directed ? "Dirigido" : "No dirigido";
  const weighted = state.weighted ? "Si" : "No";

  let html = "";
  html += "<div class=\"viz-canvas\">";
  html += `<div class=\"viz-meta\"><strong>Grafo</strong> | Tipo: ${graphType} | Ponderado: ${weighted} | Vértices: ${metadata.vertices_count ?? 0} | Aristas: ${metadata.edges_count ?? 0}<span class="graph-image-pan-note" hidden> · Imagen ampliada: desplázala dentro del panel.</span></div>`;
  html += `<div class=\"viz-stage\"><div class="viz-stage-center">${renderGraphSvg(state.asymmetric_pairs?.length ? {...state,directed:true,edges:state.c_arcs||state.edges} : state, simulation, traceDebug)}</div></div>`;



  if(state.asymmetric_pairs?.length)html += '<p class="graph-policy">La política solicita un grafo no dirigido, pero existen arcos sin inversa del mismo peso. Se muestran los arcos reales; no se inventa simetría.</p>';
  html += `<div class="viz-traversals graph-current-result">${gGraphPresentedResult(state, presentation)}</div>`;
  if (traceDebug && traceDebug.note) {
    html += `<details class="viz-sim-note"><summary>Explicación de este paso</summary><p>${gEscape(String(traceDebug.note))}</p></details>`;
  }

  html += "</div>";
  container.innerHTML = html;
  gMaintainGraphImageViewport(container,imageViewport);
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
  window.ContextualHelp?.operation("graph", model, operationName);
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
  gFocusBookFunction(model, selectedOp);
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
  return didactic.operation_functions?.[operationName] || extractGraphSubroutineName(pseudoCode, fallback || operationName || "Operación");
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

function renderGraphHistory(history, container, didactic, mainCode) {
  if (!container) {
    return;
  }
  container.dataset.rawCode = "";
  if(window.GRAPH_VIEW_MODEL?.main_unavailable_reason){container.textContent=window.GRAPH_VIEW_MODEL.main_unavailable_reason;return;}
  if (!history.length && typeof mainCode !== "string") {
    container.innerHTML = "<li class=\"didactic-history-item empty\">Sin acciones ejecutadas.</li>";
    return;
  }
  const codeTitle = didactic && didactic.code_title ? String(didactic.code_title) : "";
  if (/c[oó]digo c/i.test(codeTitle)) {
    const code = String(mainCode || "");
    container.dataset.rawCode = code;
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

function graphCapacityError(controls, operationName, payload) {
  const limit = Number(controls.dataset.vertexLimit || 15);
  const nodes = window.GRAPH_VIEW_MODEL?.visual_state?.nodes || [];
  const ids = new Set(nodes.map(node => String(Number(node.id))));
  const message = `El limite educativo es de ${limit} vertices. No se modifico el grafo ni el historial.`;
  if (nodes.length > limit && (["insert_vertex", "insert_edge"].includes(operationName) || operationName.startsWith("run_"))) return message + " La sesion anterior conserva todos sus datos; elimina vertices o limpia el grafo para volver al limite.";
  if (operationName === "generate_random_graph" && Number(payload.vertices_count) > limit) return message;
  const fields = operationName === "insert_vertex" ? ["vertex"] : operationName === "insert_edge" ? ["origin", "target"] : [];
  if (fields.length) {
    const values = fields.map(field => Number(payload[field]));
    if (values.every(Number.isInteger)) {
      const added = [...new Set(values.map(String))].filter(id => !ids.has(id)).length;
      if (nodes.length + added > limit) return message;
    }
  }
  return "";
}

async function executeGraphOperation(controls, operationName, payload, executionMode = "step") {
  const capacityError = graphCapacityError(controls, operationName, payload);
  if (capacityError) {
    const error = new Error(capacityError);error.graphCapacityRejected = true;throw error;
  }
  const response = await fetch(controls.dataset.operateUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ operation: operationName, payload, execution_mode: executionMode }),
  });
  const data = await response.json();
  if(Array.isArray(data.history) && window.GRAPH_VIEW_MODEL)window.GRAPH_VIEW_MODEL.history=data.history;
  if (typeof data.main_c === "string" && window.GRAPH_VIEW_MODEL) {
    window.GRAPH_VIEW_MODEL.main_c = data.main_c;
    window.GRAPH_VIEW_MODEL.main_unavailable_reason=data.main_unavailable_reason || null;
    gUpdateBookMainAvailability(window.GRAPH_VIEW_MODEL);
    renderGraphHistory(data.history || [], gById("action-history"), window.GRAPH_VIEW_MODEL.didactic, data.main_c);
  }
  return data;
}

function initGraphPage(model) {
  gUpdateBookMainAvailability(model);
  if(model.suspended || model.visual_state?.suspended){initSuspendedBookGraph(model);return;}
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
  const simNext = gById("graph-sim-next");
  const stepNavigation = gById("graph-step-navigation");
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
    // Snapshot producers publish the complete console at this cursor. Event
    // producers publish only new fragments: repeated/blank output is valid C.
    if (trace.console_mode === "snapshot") {
      return Array.isArray(trace.steps[limit]?.console) ? trace.steps[limit].console.slice() : [];
    }
    const out = [];
    for (let i = 0; i <= limit; i += 1) {
      const step = trace.steps[i] || {};
      const emitted = Array.isArray(step.console) ? step.console : [];
      out.push(...emitted);
    }
    return out;
  }

  function refreshGraphPrintfConsole(cursor) {
    if(!pageState.consoleTrace && typeof pageState.consoleRawStdout=== "string" && printfConsole){printfConsole.dataset.consoleCopy=pageState.consoleRawStdout;printfConsole.textContent=pageState.consoleRawStdout || "(sin salida printf en esta ruta)";printfConsole.style.whiteSpace="pre-wrap";return;}
    const steps = pageState.consoleTrace?.steps;
    const step = Array.isArray(steps) && steps.length ? steps[Math.max(0, Math.min(cursor, steps.length - 1))] : null;
    const memory = cursor < 0 ? step?.state_snapshot : step?.pedagogy?.memory_state;
    if (typeof memory?.console_stdout === "string" && printfConsole) {
      printfConsole.dataset.consoleCopy = memory.console_stdout;
      printfConsole.textContent = memory.console_stdout || "(sin salida printf en esta ruta)";
      printfConsole.style.whiteSpace = "pre-wrap";
      return;
    }
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
  initGraphResponsiveWorkspace();initGraphClassroom();hideComments?.addEventListener("change",()=>enhanceGraphCodeNavigation(null));learningLevel?.addEventListener("change",()=>{renderGraphPedagogy(currentPedagogyFrame,learningLevel.value);writeGraphPresentation();});guidedExample?.addEventListener("change",()=>{const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample.value);if(exampleLesson)exampleLesson.textContent=example?example.lesson:"El ejemplo se construye mediante operaciones públicas y no cambia al reproducir.";});
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
  renderGraphHistory(pageState.actionHistory, historyBox, model.didactic, model.main_c);
  renderGraphState(pageState.graphState, visualState, pageState.simulation, null, {operation:getTargetSelection()?.operation?.name});
  const capacityPolicy = gById("graph-capacity-policy");
  if (capacityPolicy && pageState.graphState.nodes.length > Number(controls.dataset.vertexLimit)) capacityPolicy.textContent = "Sesion anterior: se conservan todos los vertices. Elimina vertices o limpia para volver al limite de 15; las inserciones y algoritmos estan bloqueados mientras lo supere.";

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
        renderGraphState(stateSnapshot, visualState, null, stepMeta ? stepMeta.debug : null, {pending:true});
        if(stepMeta?.pedagogy){currentPedagogyFrame=stepMeta.pedagogy;renderGraphPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");}
        updateGraphStepKind(stepMeta || null);
      },
      onCursorChange: (event) => {
        const cursor = event && Number.isInteger(event.cursor) ? event.cursor : -1;
        pageState.traceCursor = cursor;
        if(event?.trace?.book_instruction_model && pageState.bookFinalMessage){const done=cursor===event.trace.steps.length-1;showGraphMessage(done?pageState.bookFinalMessage.text:"Operación preparada: resultado pendiente hasta completar las llamadas C.",done?pageState.bookFinalMessage.success:true);}
        if(cursor<0 && event?.trace?.book_instruction_model){currentPedagogyFrame=event.trace.steps[0]?.pedagogy?.initial_frame || null;if(currentPedagogyFrame)renderGraphPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");gFocusBookFunction(model,event.trace.operation_name);}
        if((event?.trace?.bfs_instruction_model || event?.trace?.dfs_instruction_model) && pageState.bfsFinalMessage)showGraphMessage(cursor===event.trace.steps.length-1?pageState.bfsFinalMessage:`${event?.trace?.dfs_instruction_model ? "DFS" : "BFS"} preparado: resultado pendiente hasta completar la traza.`,true);
        if(event?.trace?.numeric_instruction_model && pageState.numericFinalMessage){const done=cursor===event.trace.steps.length-1;showGraphMessage(done?pageState.numericFinalMessage.text:"Algoritmo preparado: resultado pendiente hasta completar la traza.",done?pageState.numericFinalMessage.success:true);}
        if((event?.trace?.vertex_instruction_model || event?.trace?.neighbor_instruction_model || event?.trace?.construction_instruction_model) && pageState.vertexFinalMessage){const done=cursor===event.trace.steps.length-1;showGraphMessage(done?pageState.vertexFinalMessage.text:"Operación preparada: resultado pendiente hasta completar la traza.",done?pageState.vertexFinalMessage.success:true);}
        if(cursor<0 && (event?.trace?.vertex_instruction_model || event?.trace?.neighbor_instruction_model || event?.trace?.construction_instruction_model)){const first=event.trace.steps[0];currentPedagogyFrame=first.pedagogy.initial_frame;renderGraphPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");renderGraphState(first.state_snapshot,visualState,null,null);}
        if(cursor<0 && event?.trace?.numeric_instruction_model && event.trace.execution_started){const first=event.trace.steps[0];currentPedagogyFrame=first.pedagogy.initial_frame;renderGraphPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");renderGraphState(first.state_snapshot,visualState,null,{graph_memory:currentPedagogyFrame.memory_state,graph_progress:{mode:"path",nodes:[],edges:[]}});}
        if(cursor<0 && (event?.trace?.bfs_instruction_model || event?.trace?.dfs_instruction_model)){const first=event.trace.steps[0];currentPedagogyFrame=first.pedagogy.initial_frame;renderGraphPedagogy(currentPedagogyFrame,learningLevel?.value||"intermediate");renderGraphState(first.state_snapshot,visualState,null,{bfs_memory:currentPedagogyFrame.memory_state,graph_progress:{mode:"traversal",nodes:[],edges:[]}});}
        pageState.traceTotalSteps = event && event.trace && Array.isArray(event.trace.steps)
          ? event.trace.steps.length
          : 0;
        const resultPanel=visualState.querySelector('.graph-current-result');
        if(resultPanel)resultPanel.innerHTML=gGraphPresentedResult(event?.step?.state_after || pageState.graphState,{operation:event?.trace?.operation_name || getTargetSelection()?.operation?.name,pending:pageState.traceTotalSteps>0 && cursor<pageState.traceTotalSteps-1});
        refreshGraphPrintfConsole(cursor);
        const step=event?.step;
        if(step?.pedagogy && step.debug?.stage && simStatus && window.ContextualHelp)simStatus.textContent=simStatus.textContent.replace(` - ${step.debug.stage}`,` - ${gGraphPhaseLabel(step.pedagogy)}`);
        enhanceGraphCodeNavigation(Number.isInteger(step?.line_index)?step.line_index:null);if(cursor<0 && event?.trace?.book_instruction_model)gFocusBookFunction(model,event.trace.operation_name);writeGraphPresentation();
        if(progressSlider){progressSlider.max=String(Math.max(0,pageState.traceTotalSteps-1));progressSlider.value=String(Math.max(0,cursor));progressSlider.disabled=pageState.traceTotalSteps===0;}
        if(stepMetadata){const frame=(cursor<0 && (event?.trace?.neighbor_instruction_model || event?.trace?.construction_instruction_model) ? currentPedagogyFrame : step?.pedagogy)||{};const edge=frame.active_edge?`${frame.active_edge.from}→${frame.active_edge.to}`:"—";stepMetadata.textContent=`Función: ${(frame.numeric_algorithm || frame.query_operation || frame.construction_operation) ? frame.instruction_event?.function||(frame.query_operation ? "-" : "caller") : frame.call_stack?.[0]?.function||"—"} · Fase: ${gGraphPhaseLabel(frame)} · Vértice: ${frame.auxiliary?.selected??"—"} · Arista: ${edge}`;}
        const concealed=Boolean(practiceMode?.checked&&cursor>=0);if(practiceCover)practiceCover.hidden=!concealed;visualState.classList.toggle("graph-practice-hidden",concealed);
        if(announcer&&step?.pedagogy)announcer.textContent=`Paso ${cursor+1}. ${step.pedagogy.narration?.basic||step.pedagogy.phase?.label||""}`;
        if (cursor < 0) window.ContextualHelp?.frame("graph", null);
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
      simStep.disabled = false;
    }
    if (simNext) {
      simNext.disabled = busy || !stepMode || !hasTrace || atEnd || pageState.lockStepUntilInput;
    }
    if (stepNavigation) {
      stepNavigation.hidden = !stepMode;
    }
    if (simStep) {
      simStep.hidden = false;
    }
    if (speedSlider) {
      speedSlider.disabled = busy || !stepMode;
    }
    if (operationRunButton) {
      operationRunButton.disabled = busy || !canExecuteOperation;
    }
  }

  function invalidateTrace(message) {
    currentPedagogyFrame = null;
    const liveMemory = gById("graph-live-memory");
    if (liveMemory) liveMemory.textContent = "Prepara una traza para observar las reservas y los campos.";
    pageState.finalTraceDebug = null;
    pageState.traceSelectionKey = "";
    pageState.lastTraceOperation = "";
    pageState.traceCursor = -1;
    pageState.traceTotalSteps = 0;
    pageState.lockStepUntilInput = false;
    pageState.consoleTrace = null;
    pageState.consoleRawStdout = null;
    pageState.consoleFallbackMessage = "";
    tracePlayer?.clear(message || "Usa Reproducir o Siguiente paso para ejecutar.");
    const currentResult=visualState.querySelector('.graph-current-result');
    if(currentResult)currentResult.innerHTML=gGraphPresentedResult(pageState.graphState,{idle:true});
    // Al cambiar operación o entrada la navegación pertenece a la traza previa.
    // Restáurase explícitamente el único botón de entrada al modo paso a paso.
    if (stepNavigation) {
      stepNavigation.hidden = true;
    }
    if (simStep) {
      simStep.hidden = false;
    }
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
    const policy = gById("graph-capacity-policy");
    if (policy) policy.textContent = pageState.graphState.nodes.length > Number(controls.dataset.vertexLimit)
      ? "Sesion anterior: se conservan todos los vertices. Elimina vertices o limpia para volver al limite de 15; las inserciones y algoritmos estan bloqueados mientras lo supere."
      : "Limite educativo: 15 vertices. No se truncan grafos ni se cambia el C descargable.";
    renderGraphState(pageState.graphState, visualState, pageState.simulation, pageState.finalTraceDebug, {operation:pageState.lastTraceOperation || getTargetSelection()?.operation?.name,pending:pageState.traceTotalSteps>0 && pageState.traceCursor<pageState.traceTotalSteps-1});
    refreshSimulationStatus();
  }

  async function executeTargetAndLoadTrace(target, selectionKey, options) {
    if(pageState.pendingExecution)return null;
    pageState.pendingExecution = true;
    setSimulationButtonsState();
    if (createButton) {
      createButton.disabled = true;
    }

    try {
      const operationName = target.operation.name;
      const payload = target.payload || {};
      const data = await executeGraphOperation(controls, operationName, payload, options?.finalOnly ? "normal" : "step");
      if(data.preserve_session){showGraphMessage(data.message,false);return null;}
      if(Array.isArray(data.history))model.history=data.history;
      pageState.traceUnavailableReason=data.trace_unavailable_reason || "";
      pageState.consoleRawStdout=typeof data.console_stdout==="string"?data.console_stdout:null;
      if(!data.execution_trace){
        tracePlayer?.clear(pageState.traceUnavailableReason || "Sin traza disponible para esta ejecución.");
        pageState.consoleTrace=null;pageState.traceCursor=-1;pageState.traceTotalSteps=0;
        pageState.lastTraceOperation="";pageState.traceSelectionKey="";currentPedagogyFrame=null;
        const memory=gById("graph-live-memory");if(memory)memory.textContent=pageState.traceUnavailableReason || "Sin traza de memoria registrada.";
      }
      if (typeof data.main_c === "string") model.main_c = data.main_c;
      if (data.execution_trace?.graph_snapshot_codec) data.execution_trace = gExpandGraphInstructionTrace(data.execution_trace);
      pageState.bookFinalMessage = data.execution_trace?.book_instruction_model ? {text:data.message,success:Boolean(data.success)} : null;
      pageState.vertexFinalMessage = (data.execution_trace?.vertex_instruction_model || data.execution_trace?.neighbor_instruction_model || data.execution_trace?.construction_instruction_model) ? {text:data.message,success:Boolean(data.success)} : null;
      pageState.bfsFinalMessage = ["run_bfs", "run_dfs"].includes(operationName) && data.success ? data.message : null;
      pageState.numericFinalMessage = data.execution_trace?.numeric_instruction_model && data.execution_trace.execution_started ? {text:data.message,success:Boolean(data.success)} : null;
      if(pageState.bookFinalMessage && !options?.finalOnly)showGraphMessage("Operación preparada: resultado pendiente hasta completar las llamadas C.",true);
      else if(pageState.vertexFinalMessage && !options?.finalOnly)showGraphMessage("Operación preparada: resultado pendiente hasta completar la traza.",true);
      else if(pageState.numericFinalMessage && !options?.finalOnly)showGraphMessage("Algoritmo preparado: resultado pendiente hasta completar la traza.",true);
      else showGraphMessage(pageState.bfsFinalMessage && !options?.finalOnly ? `${operationName === "run_dfs" ? "DFS" : "BFS"} preparado: resultado pendiente hasta completar la traza.` : data.message, Boolean(data.success));
      updateGraphDidacticPanel(model, operationName);
      refreshDidacticNote(operationName, target.mode);
      if(options?.finalOnly && !data.execution_trace){
        const summary=gById('graph-pedagogy-summary');if(summary)summary.innerHTML=gBookNoTraceMarkup(data);
        const metadata=gById('graph-step-metadata');if(metadata)metadata.textContent='Resultado normal sin traza · llamada C terminada · no hay pasos guardados';
      }

      const payloadText = summarizeGraphPayload(payload);
      const label = operationLabel.get(operationName) || operationName;
      const subroutine = getGraphSubroutineName(model, operationName, label);
      if (data.execution_started || data.execution_trace?.execution_started || data.success) gPushUniqueHistoryEntry(
        pageState.actionHistory,
        createGraphHistoryEntry(
          subroutine,
          payloadText || "-",
          data.message,
          operationName,
          payload,
        ),
      );
      renderGraphHistory(pageState.actionHistory, historyBox, model.didactic, model.main_c);

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
          pageState.consoleFallbackMessage = "";
          const finalCursor = data.execution_trace.steps.length ? data.execution_trace.steps.length - 1 : -1;
          // Keep this actual execution for later replay. Enabling step mode
          // must not execute the query again or retain an older player trace.
          if (tracePlayer) {
            tracePlayer.loadTrace(data.execution_trace);
            pageState.lastTraceOperation = String(data.execution_trace.operation_name || "");
            pageState.traceSelectionKey = selectionKey;
            tracePlayer.seek(finalCursor);
          }
          refreshGraphPrintfConsole(finalCursor);
          if (finalCursor >= 0) {
            const finalStep = data.execution_trace.steps[finalCursor] || null;
            if (finalStep && finalStep.debug) {
              pageState.finalTraceDebug = finalStep.debug;
            }
          }
        } else {
          pageState.consoleTrace = null;
          pageState.consoleFallbackMessage = "";
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
            simStatus.textContent = pageState.traceUnavailableReason || "Modo normal: se aplicó el resultado final de las llamadas C.";
          }
        }
      }
      return data;
    } catch (_error) {
      if (_error.graphCapacityRejected) {showGraphMessage(_error.message, false);return null;}
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
  resetGraph?.addEventListener("click",async()=>{if(!window.confirm("¿Restablecer el grafo y borrar su historial de esta sesión?"))return;const response=await fetch(controls.dataset.resetUrl,{method:"POST"});const data=await response.json();pageState.actionHistory.length=0;model.main_c=data.main_c;model.main_unavailable_reason=data.main_unavailable_reason||null;gUpdateBookMainAvailability(model);model.history=data.history||[];renderGraphHistory(pageState.actionHistory,historyBox,model.didactic,model.main_c);if(data.visual_state){model.visual_state=data.visual_state;applyNewGraphState(data.visual_state);}invalidateTrace("Grafo restablecido.");showGraphMessage(data.message,Boolean(data.success));});
  loadExample?.addEventListener("click",async()=>{const example=(model.guided_examples||[]).find((item)=>item.id===guidedExample?.value);if(!example){showGraphMessage("Selecciona un ejemplo guiado.",false);return;}loadExample.disabled=true;try{const labelMap=new Map((example.vertices||[]).map((value,index)=>[String(value),index+1]));const resolve=(value)=>labelMap.get(String(value))??value;let data=await executeGraphOperation(controls,"create_graph",{directed:Boolean(example.directed)});if(!data.success)throw new Error(data.message);for(const vertex of example.vertices||[]){data=await executeGraphOperation(controls,"insert_vertex",{vertex:resolve(vertex)});if(!data.success)throw new Error(data.message);}for(const edge of example.edges||[]){data=await executeGraphOperation(controls,"insert_edge",{origin:resolve(edge[0]),target:resolve(edge[1]),weight:edge[2]});if(!data.success)throw new Error(data.message);}if(data.visual_state){model.visual_state=data.visual_state;applyNewGraphState(data.visual_state);}const mappedPayload={};Object.entries(example.payload||{}).forEach(([key,value])=>{mappedPayload[key]=resolve(value);});selectedAlgorithm=algorithmList.find((item)=>item.name===example.operation)||selectedAlgorithm;if(selectedAlgorithm){algorithmSelect.value=selectedAlgorithm.name;buildGraphInputs(selectedAlgorithm,algorithmInputs,"g-alg-field");selectedAlgorithm.inputs.forEach((field)=>{const input=gById(`g-alg-field-${field.name}`);if(input&&Object.prototype.hasOwnProperty.call(mappedPayload,field.name))input.value=mappedPayload[field.name];});setRunMode("algorithm");updateGraphDidacticPanel(model,selectedAlgorithm.name);}pageState.actionHistory.length=0;invalidateTrace("Ejemplo preparado. Reproduce la operación objetivo.");writeGraphPresentation();showGraphMessage(`Ejemplo preparado: ${example.lesson}`,true);}catch(error){showGraphMessage(error.message||"No se pudo preparar el ejemplo.",false);}finally{loadExample.disabled=false;}});

  createButton?.addEventListener("click", async () => {
    const payload={directed:modeSelect?modeSelect.value:"false"};
    const data=await executeTargetAndLoadTrace({mode:"operation",operation:{name:"create_graph"},payload},buildSelectionKey("operation","create_graph",payload),!isStepByStepEnabled()?{finalOnly:true}:undefined);
    if(!data)return;
    if(isStepByStepEnabled() && tracePlayer?.hasTrace())tracePlayer.reset();
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

  function comparisonCard(side){
    const summary=side?.summary||{},cost=summary.distance_to_destination??summary.total_weight;
    const label=({run_bfs:"BFS",run_dfs:"DFS",run_dijkstra:"Dijkstra",run_bellman_ford:"Bellman-Ford",run_prim:"Prim",run_kruskal:"Kruskal"})[side?.algorithm]||"Algoritmo";
    return `<article class="hier-compare-card"><h4>${gEscape(label)}</h4><p><strong>Estado C:</strong> ${gEscape(side?.c_status_name || "sin estado registrado")}</p><p><strong>Resultado:</strong> ${gEscape(gTeachingValue(summary.order||summary.path||summary.mst_edges||summary))}</p><p><strong>Costo:</strong> ${gEscape(cost ?? "no calculado")}</p><p>${gEscape(side?.message || "Sin certificación adicional de invariantes.")}</p></article>`;
  }
  function renderComparison(){if(!comparisonResult||!compareGrid)return;compareGrid.innerHTML=comparisonCard(comparisonResult.left)+comparisonCard(comparisonResult.right);if(compareInput)compareInput.textContent=`Entrada inmutable: ${comparisonResult.input.nodes.length} vértices, ${comparisonResult.input.edges.length} aristas. Concepto ${Number(compareProgress?.value||0)+1}/4.`;if(compareConclusion)compareConclusion.textContent=`${comparisonResult.conclusion} Estado auxiliar, costo, restricción e invariante se calculan sobre copias aisladas.`;}
  compareRun?.addEventListener("click",async()=>{const response=await fetch(controls.dataset.compareUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({kind:compareKind?.value,graph:model.visual_state,start:compareStart?.value,end:compareEnd?.value})});const data=await response.json();if(!response.ok||!data.success){if(compareConclusion)compareConclusion.textContent=data.message||"No se pudo comparar.";return;}comparisonResult=data;renderComparison();});
  compareProgress?.addEventListener("input",renderComparison);
  exportImage?.addEventListener("click", async () => {
    if (exportImage.disabled) return;
    const originalText = exportImage.textContent;
    exportImage.disabled = true;
    exportImage.setAttribute("aria-busy", "true");
    try {
      const exported = await window.InterpreterRuntime.exportVisualStateAsJpg({
        target: visualState, quality: .92, scale: 2,
        onProgress: (text) => { exportImage.textContent = text; },
      });
      window.InterpreterRuntime.downloadJpg(exported.dataUrl, exported.suggestedName);
      showGraphMessage("Captura JPG preparada; revisa las descargas del navegador.", true);
    } catch (error) { showGraphMessage(error.message || "No se pudo exportar la captura.", false); }
    finally {
      exportImage.disabled = false;
      exportImage.removeAttribute("aria-busy");
      exportImage.textContent = originalText;
    }
  });
  exportSummary?.addEventListener("click",()=>{const report={module:"graph",source_contract:model.source_contract,history:model.history||[],main_c:model.main_c,phase:activePhase,algorithm:selectedAlgorithm?.name||selectedOperation?.name,cursor:pageState.traceCursor,total_steps:pageState.traceTotalSteps,progress:{...conceptualProgress},frame:currentPedagogyFrame,comparison:comparisonResult};const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="graph-learning-summary.json";link.click();URL.revokeObjectURL(link.href);if(announcer)announcer.textContent="Resumen de aprendizaje exportado.";});
  document.addEventListener("keydown",(event)=>{if(!event.altKey)return;if(event.key==="ArrowRight"){event.preventDefault();simStep?.click();}else if(event.key==="ArrowLeft"){event.preventDefault();simPrev?.click();}else if(event.key==="Home"){event.preventDefault();homeButton?.click();}else if(event.key==="End"){event.preventDefault();endButton?.click();}else if(event.key.toLowerCase()==="p"){event.preventDefault();pauseButton?.click();}});

  simStep?.addEventListener("click", () => {
    stepToggle.checked = !stepToggle.checked;
    stepToggle.dispatchEvent(new Event("change"));
  });

  simNext?.addEventListener("click", async () => {
    if (!isStepByStepEnabled() || !tracePlayer?.hasTrace()) {
      return;
    }
    // Applying type owns its loaded creation trace until an input/selection
    // change invalidates it. Advancing must not dispatch the unrelated selector.
    const ready = pageState.lastTraceOperation === "create_graph" && tracePlayer.hasTrace()
      ? true : await ensureTraceForCurrentTarget();
    if (!ready || !tracePlayer || !tracePlayer.hasTrace()) {
      return;
    }
    const advanced = await tracePlayer.step();
    if (advanced && tracePlayer.isAtEnd()) {
      pageState.lockStepUntilInput = true;
    }
    setSimulationButtonsState();
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
    const target = resolveFastModeTarget();
    if (!target || !isTargetSelectionValid(target)) { showSimulationStatus("Completa las entradas para ejecutar."); return; }
    const key = buildSelectionKey(target.mode, target.operation.name, target.payload);
    await executeTargetAndLoadTrace(target, key, { finalOnly: !isStepByStepEnabled() });
    if (isStepByStepEnabled() && tracePlayer?.hasTrace()) tracePlayer.reset();
  });

  stepToggle?.addEventListener("change", () => {
    simStep.textContent = isStepByStepEnabled() ? "Cerrar paso a paso" : "Paso a paso";
    simStep.setAttribute("aria-pressed", String(isStepByStepEnabled()));
    tracePlayer?.pause(true);
    if (tracePlayer?.hasTrace()) tracePlayer.seek(isStepByStepEnabled() ? -1 : tracePlayer.getTotalSteps() - 1);
    setSimulationButtonsState();
  });
  if (stepToggle) { stepToggle.checked = false; stepToggle.hidden = true; }
  simPrev.textContent = "Paso anterior";
  simNext.textContent = "Siguiente paso";
  setSimulationButtonsState();

  updateStepModePanelVisibility();
  invalidateTrace("Usa Reproducir o Siguiente paso para ejecutar.");
  refreshGraphPrintfConsole(-1);
  refreshSimulationStatus();
  focusGraphSectionByHash();
}


// Presentation-only classroom v1; existing render targets retain their identity.
function graphMountClassroomView() {
  if (!window.ClassroomView) return;
  const root = document.querySelector(".graph-primary-workspace");
  if (!root) return;
  document.getElementById("graph-code-region")?.classList.add("classroom-code");
  document.getElementById("graph-code-region")?.classList.remove("didactic-technical");
  const history = document.getElementById("action-history");
  const consoleNode = document.getElementById("graph-printf-console");
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
  const view=window.ClassroomView.mount({root,visual:"#graph-visual-region",stage:"#graph-visual-state",code:"#op-pseudocode",memory:[".graph-live-memory-panel"],results,key:"graph"});
  // Graph-only auto framing. Any deliberate zoom/pan hands control to the reader.
  const stage=document.getElementById('graph-visual-state');
  let automatic=true,lastTopology='',scheduled=false;
  function fitGraph(force=false){
    scheduled=false;if(!automatic)return;
    const svg=stage.querySelector('svg');if(!svg)return;
    const key=JSON.stringify([...svg.querySelectorAll('circle')].map(n=>n.getAttribute('data-node-id')).concat([...svg.querySelectorAll('[data-graph-source]')].map(e=>e.getAttribute('data-graph-source')+'>'+e.getAttribute('data-graph-target'))).sort());
    if(!force&&key===lastTopology)return;lastTopology=key;
    const box=svg.getAttribute('viewBox').split(/\s+/).map(Number);
    const availableWidth=Math.max(1,stage.clientWidth-24),availableHeight=Math.max(1,stage.clientHeight-45);
    const readable=14/18;
    view.setZoom(Math.max(readable,Math.min(1,availableWidth/box[2],availableHeight/box[3])));
  }
  const queueFit=()=>{if(!scheduled){scheduled=true;requestAnimationFrame(()=>fitGraph());}};
  new MutationObserver(queueFit).observe(stage,{childList:true,subtree:true});
  window.addEventListener('resize',()=>{if(automatic)requestAnimationFrame(()=>fitGraph(true));});
  stage.addEventListener('wheel',()=>{automatic=false;},{passive:true});
  stage.addEventListener('pointerdown',()=>{automatic=false;},{passive:true});
  stage.addEventListener('keydown',()=>{automatic=false;});
  root.querySelector('.classroom-view-tools')?.addEventListener('click',event=>{
    const button=event.target.closest('button');if(!button)return;
    automatic=button.textContent==='Encajar vista';
    if(automatic)requestAnimationFrame(()=>fitGraph(true));
  });
  queueFit();

}

document.addEventListener("DOMContentLoaded", () => {
  if (window.GRAPH_VIEW_MODEL) {
    initGraphPage(window.GRAPH_VIEW_MODEL);
    graphMountClassroomView();
  }
});
