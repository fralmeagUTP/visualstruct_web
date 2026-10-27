/* Concise, operation-scoped teaching notes. Detailed evidence remains available. */
(function (scope) {
  "use strict";
  const selected = new Map();
  const esc = (text) => String(text ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const rules = {
    stack: "El último valor que entra es el primero que sale (LIFO).",
    queue: "El primer valor que entra es el primero que sale (FIFO).",
    priority_queue: "Menor número significa mayor prioridad; si hay empate, sale primero quien llegó antes (FIFO).",
    linked_list: "Cada enlace debe conservar el orden de los nodos que siguen en la lista.",
    circular_list: "El último nodo enlaza con el primero; el recorrido debe detenerse al volver al inicio.",
    sublist: "Cada hijo pertenece a la sublista de un padre concreto.",
    abb: "Los valores menores van a la izquierda; los mayores, a la derecha.",
    avl: "Además del orden de búsqueda, las alturas de los hijos difieren como máximo en uno.",
    red_black: "El orden de búsqueda y las reglas de color se conservan tras cada operación completa.",
    binary_heap: "En este min-heap, cada padre es menor o igual que sus hijos; el arreglo no está totalmente ordenado.",
    hash_table: "La clave determina el bucket; las colisiones se recorren dentro de su cadena.",
    graph: "Los vértices y las aristas del grafo son distintos de las marcas temporales del algoritmo.",
    sorting_array: "Se conserva cada valor del arreglo; el resultado queda de menor a mayor."
  };
  const goals = {
    insertar: "Ubicar el valor y conectarlo donde corresponde.", eliminar: "Localizar el valor y reconectar la estructura sin perder los demás nodos.",
    buscar: "Seguir la ruta hasta encontrar el valor o confirmar que no está.",
    altura: "Calcular la altura a partir de los subárboles; no insertar ni eliminar nodos.",
    contar_hojas: "Contar únicamente los nodos que no tienen hijos.",
    minimo: "Localizar el menor valor sin modificar el árbol.", maximo: "Localizar el mayor valor sin modificar el árbol.",
    inorden: "Visitar izquierda, raíz y derecha, en ese orden.", preorden: "Visitar raíz, izquierda y derecha, en ese orden.", postorden: "Visitar izquierda, derecha y raíz, en ese orden.",
    apilar: "Crear un nodo y convertirlo en el nuevo tope.", desapilar: "Retirar el tope y conservar el enlace al siguiente nodo.",
    encolar: "Agregar un elemento respetando el orden de atención de esta cola.", desencolar: "Retirar el frente y actualizar los enlaces de la cola.",
    limpiar: "Liberar los nodos y dejar la estructura vacía.", clear: "Vaciar las cadenas de la tabla, conservando la tabla creada.", destroy_table: "Liberar la tabla y sus buckets.",
    insertar_inicio: "Enlazar el nuevo nodo antes del primero.", insertar_final: "Enlazar el nuevo nodo después del último.",
    insertar_padre: "Crear el nodo padre con su sublista vacía.", insertar_hijo: "Localizar el padre y agregar el hijo a su sublista.",
    eliminar_padre: "Retirar el padre y liberar también su sublista.", eliminar_hijo: "Retirar el hijo de la sublista del padre indicado.",
    invertir: "Invertir los enlaces sin perder la circularidad.", validar: "Comprobar las reglas de la estructura sin modificar sus datos.",
    insert: "Calcular el bucket y buscar la clave antes de insertar o actualizar su valor.", get: "Buscar la clave en su bucket y recuperar el valor si existe.", contains: "Comprobar si la clave está presente sin modificar la tabla.", remove: "Buscar la clave y retirar su nodo sin romper la cadena.",
    create_table: "Crear los buckets de una tabla vacía.",
    run_bfs: "Recorrer por niveles usando una cola.", run_dfs: "Profundizar por una ruta antes de retroceder.",
    run_dijkstra: "Elegir la distancia provisional menor y revisar sus aristas; requiere pesos no negativos.",
    run_bellman_ford: "Relajar las aristas y comprobar si existe un ciclo negativo alcanzable.",
    run_prim: "Ampliar el árbol con una arista de menor peso que llegue a un nuevo vértice.",
    run_kruskal: "Considerar aristas por peso y aceptar las que no formen ciclos.",
    insert_vertex: "Agregar el vértice sin crear aristas todavía.", remove_vertex: "Retirar el vértice y sus conexiones.",
    insert_edge: "Conectar origen y destino con el peso indicado.", remove_edge: "Retirar la conexión entre origen y destino.",
    create_graph: "Crear un grafo vacío del tipo elegido.", clear_graph: "Vaciar los vértices y las aristas del grafo.",
    extraer_raiz: "Retirar la raíz y restaurar la prioridad padre-hijos.", raiz: "Consultar la raíz sin retirarla.",
    frente: "Consultar el siguiente elemento que se atendería, sin retirarlo.",
    mostrar: "Recorrer la lista y mostrar sus valores en orden, sin cambiar los enlaces.",
    buscar_elemento: "Recorrer la lista y mostrar todas las posiciones del valor buscado.",
    buscar_posiciones: "Obtener todas las posiciones del valor; en la interfaz se cuentan desde uno.",
    eliminar_elemento: "Retirar la primera coincidencia del valor y reconectar sus vecinos.",
    eliminar_primero: "Retirar la primera coincidencia del valor, no necesariamente el primer nodo.",
    eliminar_repetidos: "Retirar todas las ocurrencias del valor indicado, incluida la primera.",
    eliminar_inicio: "Retirar el primer nodo y actualizar el inicio de la lista.",
    eliminar_final: "Retirar el último nodo y cerrar correctamente el enlace anterior.",
    eliminar_posicion: "Retirar el nodo de la posición indicada; la interfaz cuenta desde uno.",
    lista_insertar_elemento: "Posición 1: insertar al inicio. Posición mayor que 1: insertar después de ese nodo base.",
    insertar_posicion: "Insertar antes de la posición indicada; la posición 1 representa el inicio.",
    insertar_elemento: "En posición 1, insertar al inicio; en las demás, respetar el modo antes (-1) o después (0).",
    primero: "Consultar el primer valor sin retirar su nodo.",
    ultimo: "Recorrer hasta el último nodo y consultar su valor sin retirarlo.",
    hijos_de: "Localizar el padre y consultar únicamente los valores de su sublista.",
    a_lista: "Consultar el arreglo interno del montículo por niveles; no ordenarlo ni extraer elementos.",
    exists_vertex: "Comprobar si existe el vértice, sin modificar el grafo.",
    exists_edge: "Comprobar si existe la conexión entre origen y destino, respetando su dirección.",
    list_vertices: "Mostrar los vértices actuales sin modificar el grafo.",
    list_edges: "Mostrar las conexiones y sus pesos sin modificar el grafo.",
    neighbors: "Consultar los vecinos del vértice; en un grafo dirigido, seguir sus aristas salientes.",
    edge_weight: "Consultar el peso de la conexión indicada sin cambiarla.",
    generate_random_graph: "Preparar un grafo aleatorio con la cantidad de vértices indicada.",
    keys: "Recorrer los buckets y consultar todas las claves almacenadas.",
    values: "Recorrer los buckets y consultar los valores almacenados, sin modificar la tabla.",
    items: "Recorrer los buckets y consultar cada par clave-valor de la tabla.",
    stats: "Consultar capacidad, cantidad de entradas y ocupación de la tabla sin modificarla.",
    create_array: "Validar los enteros y reemplazar el arreglo con los datos ingresados.",
    generate_random_array: "Crear un arreglo aleatorio con el tamaño y los límites indicados.",
    select_algorithm: "Elegir el algoritmo que se aplicará; esta selección todavía no ordena el arreglo.",
    run: "Aplicar el algoritmo seleccionado y observar cómo transforma el arreglo.",
    step: "Consultar el paso anterior o siguiente de la ejecución de ordenamiento.",
    reset: "Restablecer el arreglo, la selección y el historial de ordenamiento.",
    intercambio: "Comparar pares y cambiar de lugar los que estén fuera de orden.", seleccion: "Elegir el menor elemento pendiente y colocarlo en su posición.",
    insercion: "Insertar cada valor en la parte que ya está ordenada.", burbuja: "Comparar vecinos y desplazar los mayores hacia el final.",
    shell: "Ordenar por saltos cada vez menores hasta llegar a uno.", quicksort: "Particionar alrededor de un pivote y ordenar las partes.",
    mergesort: "Dividir el arreglo y fusionar las partes ordenadas.", heapsort: "Construir un montículo y extraer su prioridad para ordenar.",
    counting_sort: "Contar las apariciones y reconstruir el arreglo por frecuencia.", binsort: "Delegar el ordenamiento por frecuencias en Counting sort.", radixsort: "Ordenar por dígitos, tratando por separado los valores negativos y no negativos."
  };
  const structureGoals = {
    priority_queue: {
      encolar: "Agregar al final en orden de llegada, sin ordenar físicamente los nodos por prioridad.",
      desencolar: "Recorrer la cola y retirar el nodo con el menor número de prioridad, aunque esté en medio; en empate, el primero que llegó.",
      frente: "Buscar el menor número de prioridad y consultar su valor sin retirarlo; en empate, elegir el primero que llegó."
    },
    binary_heap: {
      insertar: "Agregar al final del arreglo y subir el valor mientras sea menor que su padre.",
      extraer_raiz: "Retirar el mínimo, llevar el último valor a la raíz y bajarlo hasta restaurar el min-heap.",
      raiz: "Consultar el mínimo en la raíz, sin retirarlo.",
      limpiar: "Vaciar el montículo; no recorrerlo como una lista enlazada."
    },
    queue: { encolar: "Agregar un nodo al final; el frente conserva el próximo valor que saldrá." },
    circular_list: {
      insertar_inicio: "Insertar el nodo al inicio y conservar el enlace circular del último al primero.",
      insertar_final: "Insertar el nodo al final y enlazarlo de vuelta con el primero.",
      eliminar_inicio: "Retirar el primer nodo y reconectar el último con el nuevo inicio; si era el único, dejar la lista vacía."
    }
  };
  const panels = {
    hier: ["path", "stack", "invariant", "variables", "memory", "relations"],
    seq: ["condition", "variable", "pointer", "heap", "call"],
    graph: ["representation", "auxiliary", "traversal", "table", "relaxation", "condition", "invariant"],
    hash: ["formula", "chain", "pointers", "cost", "memory", "invariant"]
  };
  function sentences(value) {
    return String(value || "").split(/(?<=[.!?])\s+|\n+/).map(s => s.trim()).filter(Boolean);
  }
  function paint(prefix, points, detail, technical = false) {
    const target = document.getElementById(prefix === "sorting" ? "sorting-pedagogy-narration" : `${prefix}-pedagogy-summary`);
    if (!target) return;
    target.innerHTML = `<ul class="contextual-help-points">${points.map(([label, value]) => `<li><strong>${esc(label)}:</strong> ${esc(value)}</li>`).join("")}</ul>` + (detail ? `<details class="contextual-help-reference"><summary>${technical ? "Registro técnico de este paso" : "Explicación completa de este paso"}</summary><p>${esc(detail)}</p></details>` : "");
  }
  function showPanels(prefix, active) {
    (panels[prefix] || []).forEach(name => {
      const panel = document.getElementById(`${prefix}-${name}-view`);
      if (!panel) return;
      const container = panel.parentElement;
      if (container?.tagName === "SECTION") container.hidden = !active;
    });
  }
  function operation(prefix, model, name) {
    const meta = [...(model.operations || []), ...(model.algorithms || [])].find(item => (item.name || item.id) === name);
    const label = meta?.label || name || "Seleccionar operación";
    const structure = model.id || (prefix === "sorting" ? "sorting_array" : prefix);
    const goal = structureGoals[structure]?.[name] || goals[name] || `${label}: observar su resultado y los pasos necesarios en ${model.name || "la estructura"}.`;
    selected.set(prefix, { model, name });
    paint(prefix, [[label, goal], ["Regla a observar", rules[structure] || "Cada paso debe conservar los datos que la operación no modifica."], ["Ahora", "Prepara la operación y avanza con «Siguiente paso». Aún no hay instrucciones ejecutadas."]]);
    showPanels(prefix, false);
  }
  function phaseLabel(value) {
    const id = String(value?.phase?.id || "").toLowerCase();
    const label = String(value?.phase?.label || "");
    if (/initial|before_call/.test(id)) return "Antes de comenzar";
    if (/entry|enter/.test(id)) return "Entrar a la función";
    if (/(?:^|[-_])caller$/.test(id)) return "Continuar en la función llamadora";
    if (/return|exit|end/.test(id)) return "Terminar la función";
    const counter = String(value?.source?.line_text || "").match(/(?:->|\b)(cantidad|size|count|tamano|tamanio)\s*(?:\+\+|--|[+\-]=)/);
    if (counter) return "Actualizar la cantidad";
    const byConcept = { statement: "Ejecutar la instrucción C", parameter: "Recibir un parámetro", write: "Escribir un valor", declare: "Declarar una variable", operand: "Evaluar un operando", scope_enter: "Entrar en un bloque", scope_exit: "Terminar un bloque", "scope exit": "Terminar un bloque", break: "Salir del ciclo", api_publication: "Publicar el resultado en la aplicación", "api publication": "Publicar el resultado en la aplicación", api_projection: "Actualizar la vista de la aplicación", compare: "Evaluar una condición", condition: "Evaluar una condición", comparison: "Comparar valores", assignment: "Actualizar un valor", swap: "Intercambiar valores", call: "Llamar a una función", allocation: "Reservar memoria", allocate: "Reservar memoria", free: "Liberar memoria", link: "Conectar los nodos", loop: "Revisar el ciclo", output: "Mostrar un resultado", invariant: "Comprobar la propiedad de la estructura", phase: "Avanzar en el algoritmo" };
    // Token-derived English labels are identifiers, not learner-facing prose.
    if (label.toLowerCase() === "link" || value?.concept === "link") {
      const field = String(value?.source?.line_text || "").match(/->\s*([A-Za-z_]\w*)\s*=(?!=)/)?.[1];
      if (field) return /^(sgte|siguiente|next|ant|anterior|prev|izq|izquierda|izquierdo|der|derecha|derecho|hijo|padre)$/.test(field)
        ? "Actualizar un enlace" : "Actualizar un dato del nodo";
    }
    if (byConcept[label.toLowerCase()]) return byConcept[label.toLowerCase()];
    if (!label || label.toLowerCase() === id.replaceAll("_", " ") || /^(sort|swap|helper|loop|check|write|read|assign|copy|merge|partition|count|scan|alloc|free|return|entry)\b/i.test(label)) return byConcept[value?.concept] || "Ejecutar la instrucción";
    return label;
  }
  // Presentation-only metadata: retain the untouched frame in advanced views.
  function isModelMetadata(name) {
    return /(?:_model|_ids)$/.test(name) || ["heap_nodes", "heap_objects", "local_pointer_names", "state_changes", "scope_ended", "root_owner", "hidden_alias_memory"].includes(name);
  }
  function technicalNarration(text) {
    return /(?:\b\w+_model\b|\b\w+_ids\b|heap_nodes|heap_objects|local_pointer_names|conecta esta línea con)/i.test(text);
  }
  function stateSummary(value) {
    const state = value.memory_state;
    if (!state || typeof state !== "object") return "";
    if (Array.isArray(state.items)) {
      const values = state.items.map(item => typeof item === "object" ? item.value : item);
      if (values.every(item => item == null || typeof item !== "object")) return `Estado de la estructura: [${values.slice(0, 8).join(", ")}${values.length > 8 ? ", …" : ""}] (${values.length} elementos).`;
    }
    if (Number.isInteger(state.size)) return `La estructura tiene ${state.size} elementos.`;
    return "";
  }
  function frame(prefix, value, level) {
    if (!value) {
      const current = selected.get(prefix);
      if (current) operation(prefix, current.model, current.name);
      return;
    }
    const narration = value.narration?.[level] || value.narration?.basic || value.narration?.intermediate || "";
    const rawBits = sentences(narration);
    const bits = rawBits.filter(bit => !technicalNarration(bit));
    const condition = value.condition;
    const ended = value.memory_state?.scope_ended === true || (String(value.source?.line_text || "").trim() === "}" && value.concept === "return");
    const declaredNames = new Set([
      ...(value.scopes || []).flatMap(item => Array.isArray(item.variables) ? item.variables.map(variable => variable.name).filter(Boolean) : Object.keys(item.variables || {})),
      ...(value.call_stack || []).flatMap(item => Object.keys(item.parameters || {})),
      ...(String(value.source?.line_text || "").match(/[A-Za-z_]\w*/g) || [])
    ]);
    const changed = !ended && Array.isArray(value.variables) ? value.variables.filter(v => v.changed && (!isModelMetadata(String(v.name)) || declaredNames.has(v.name))) : [];
    const describe = (datum, item) => {
      if (prefix === "sorting" && scope.SortingMemoryFormat) return scope.SortingMemoryFormat.value(datum, item);
      if (Array.isArray(datum)) return `[${datum.slice(0, 6).join(", ")}${datum.length > 6 ? ", …" : ""}]`;
      if (datum && typeof datum === "object") return "estado compuesto (ver detalle técnico)";
      return String(datum ?? "sin valor");
    };
    const displayName = name => ({size: "Cantidad de elementos", empty: "Estructura vacía"})[name] || name;
    const goal = value.phase?.goal && !technicalNarration(value.phase.goal) ? value.phase.goal : "";
    const fallback = bits[0] || goal || "Observa la instrucción resaltada y su efecto en la estructura.";
    const change = ended ? `Termina el ámbito de esta función. ${stateSummary(value) || "Los datos de los locales dejan de estar disponibles; esto no implica liberar los nodos."}`
      : changed.length ? changed.slice(0, 2).map(v => `${displayName(v.name)}: ${v.previous == null ? "sin valor previo registrado" : describe(v.previous, {})} → ${describe(v.value, v)}`).join("; ") : fallback;
    const rawReason = condition?.consequence || bits[1];
    const reason = rawReason && !technicalNarration(rawReason) ? rawReason : "";
    const points = [["Paso actual", phaseLabel(value)], [changed.length ? "Cambio" : "Qué ocurre", change]];
    if (reason && reason !== change && !ended) points.push(["Por qué", reason]);
    paint(prefix, points, rawBits.length > 2 || changed.length || ended || technicalNarration(narration) ? narration : "", technicalNarration(narration));
    showPanels(prefix, true);
  }
  scope.ContextualHelp = { operation, frame, sentences, phaseLabel };
}(window));
