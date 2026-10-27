/* Convenience queue only. Every mutation remains an existing, unitary TAD call. */
(function (root) {
  'use strict';
  const operations = Object.freeze({stack:'apilar', queue:'encolar', linked_list:'insertar_final', circular_list:'insertar_final', abb:'insertar', avl:'insertar', red_black:'insertar', binary_heap:'insertar'});
  const unique = new Set(['abb','avl','red_black']);
  function parse(text, structure, existing = []) {
    const parts = String(text).split(',');
    const errors = [], values = [], seen = new Set(existing.map(Number));
    if (parts.length > 50) errors.push('Máximo 50 valores por lote; divide la lista.');
    parts.forEach((raw, index) => {
      const token = raw.trim(), position = index + 1;
      if (!token) { errors.push(`Posición ${position}: falta un valor${index === parts.length - 1 && parts.length > 1 ? ' (coma final)' : ''}.`); return; }
      if (!/^[+-]?\d+$/.test(token)) { errors.push(`Posición ${position}: «${token}» no es un entero decimal.`); return; }
      const value = Number(token);
      if (!Number.isSafeInteger(value) || value < -2147483648 || value > 2147483647) { errors.push(`Posición ${position}: fuera del rango int32.`); return; }
      if (unique.has(structure) && seen.has(value)) errors.push(`Posición ${position}: ${value} está repetido en la lista o ya existe en el árbol; este TAD no admite duplicados.`);
      seen.add(value); values.push(value);
    });
    return {values, errors, valid: errors.length === 0};
  }
  // No polling and no mutation retry. Each next() is an explicit transition.
  function createQueue(adapter, notify = () => {}) {
    const s = {phase:'idle', values:[], index:0, confirmed:0, mode:'normal', stopRequested:false, playing:false, message:''};
    let busy = false, playGeneration = 0, batchGeneration = 0;
    const active = () => ['request','trace','uncertain'].includes(s.phase);
    const emit = () => notify({...s, values:s.values.slice(), busy, active:active()});
    function finish(phase, message) { s.phase=phase; s.playing=false; s.message=message; emit(); }
    function finishTrace() { adapter.player?.pause(true); if (s.mode === 'step' && adapter.player?.hasTrace()) adapter.player.seek(adapter.player.getTotalSteps()-1); }
    async function send(generation = batchGeneration) {
      if (generation !== batchGeneration || busy || s.stopRequested || s.index >= s.values.length) return;
      busy=true; s.phase='request'; s.message='Esperando confirmación del servidor…'; emit();
      let data;
      try { data=await adapter.execute(s.values[s.index], s.mode === 'normal'); } catch (_) { data=null; }
      busy=false;
      if (!data || typeof data.success !== 'boolean') {
        finish('uncertain', `Respuesta incierta para el valor ${s.index+1} (${s.values[s.index]}). Confirmados: ${s.confirmed}. No se reintentará; se descartaron los pendientes. Recarga para consultar estado e historial antes de decidir qué falta.`); return;
      }
      if (!data.success) {
        if (data.execution_trace?.execution_started === true) finishTrace();
        finish('failed', `Se detuvo en el valor ${s.index+1}: ${data.message || 'operación rechazada'}. Confirmados: ${s.confirmed}; pendientes descartados. No se deshace lo anterior.`); return;
      }
      s.confirmed++;
      if (s.stopRequested) { finishTrace(); finish('stopped', `Detenido: ${s.confirmed} operaciones confirmadas; ${s.values.length-s.confirmed} pendientes descartadas. La operación aceptada se conserva.`); return; }
      if (s.mode === 'step' && adapter.player?.getTotalSteps() > 0) {
        adapter.player.reset(); s.phase='trace'; s.message='Operación ya aceptada. Navega su traza; al finalizar, confirma Siguiente valor.'; emit();
      } else {
        s.index++;
        if (s.index === s.values.length) finish('done', `Completado: ${s.confirmed} de ${s.values.length} operaciones confirmadas, en el orden indicado.`);
        else { s.phase='trace'; emit(); await new Promise(resolve => setTimeout(resolve, 0)); if (generation === batchGeneration && !s.stopRequested) await send(generation); }
      }
    }
    return {
      state: () => ({...s, busy, active:active()}),
      async start(values, mode) {
        if (active() || busy || !values.length) return;
        Object.assign(s,{values:values.slice(), index:0, confirmed:0, mode, stopRequested:false, playing:false, message:''});
        batchGeneration++; adapter.player?.pause(true); await send(batchGeneration);
      },
      async next() {
        if (busy || s.phase !== 'trace' || s.mode !== 'step' || s.playing) return;
        if (!adapter.player.isAtEnd()) { busy=true; emit(); await adapter.player.step(); busy=false; if(s.stopRequested) { finishTrace(); finish('stopped', `Detenido: ${s.confirmed} operaciones confirmadas; ${s.values.length-s.confirmed} pendientes descartadas.`); } else emit(); return; }
        s.index++;
        if (s.index === s.values.length) finish('done', `Completado: ${s.confirmed} de ${s.values.length} operaciones confirmadas.`);
        else await send();
      },
      prev() { if (busy || s.phase !== 'trace' || s.mode !== 'step' || s.playing) return; adapter.player.prev(); emit(); },
      async play() {
        if (busy || s.phase !== 'trace' || s.mode !== 'step' || s.playing || adapter.player.isAtEnd()) return;
        const generation=++playGeneration; s.playing=true; emit(); await adapter.player.play(); if(generation===playGeneration) { s.playing=false; emit(); }
      },
      pause() { playGeneration++; adapter.player?.pause(true); s.playing=false; emit(); },
      stop() {
        if (!active() || s.phase === 'uncertain') return;
        playGeneration++; s.stopRequested=true; s.playing=false; adapter.player?.pause(true);
        if (busy) { s.message='Deteniendo después de la operación en curso; no se enviarán más valores.'; emit(); return; }
        finishTrace(); finish('stopped', `Detenido: ${s.confirmed} operaciones confirmadas; ${s.values.length-s.confirmed} pendientes descartadas. La operación aceptada se conserva.`);
      },
    };
  }
  async function fetchUnit(url, options) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    try {
      const response=await fetch(url, {...options, signal:controller.signal});
      // Read body within the same timeout. A broken response is always uncertain.
      const data=await response.json();
      if (!response.ok && typeof data.success !== 'boolean') throw new Error('Respuesta incierta');
      return {json:async()=>data};
    } finally { clearTimeout(timer); }
  }
  function mount(adapter) {
    const operation = operations[adapter.model.id];
    if (!operation || !adapter.player) return null;
    const panel=document.createElement('details'); panel.id='multiple-input'; panel.className='multiple-input';
    panel.innerHTML=`<summary>Agregar varios</summary><p id="multiple-rule"></p>
      <label for="multiple-values">Valores separados por comas (máximo 50)</label>
      <input id="multiple-values" type="text" placeholder="50,25,75,12,37" autocomplete="off" aria-describedby="multiple-preview multiple-rule">
      <p id="multiple-preview" role="status"></p>
      <div class="actions"><button id="multiple-load" class="btn" type="button">Cargar valores</button><button id="multiple-step" class="btn secondary" type="button">Agregar paso a paso</button></div>
      <div id="multiple-controls" hidden class="actions"><button id="multiple-prev" class="btn secondary" type="button">Paso anterior</button><button id="multiple-next" class="btn" type="button">Siguiente paso</button><button id="multiple-play" class="btn" type="button">Reproducir traza</button><button id="multiple-pause" class="btn secondary" type="button">Pausar</button><button id="multiple-stop" class="btn secondary" type="button">Detener lote</button></div>
      <p id="multiple-status" role="status" aria-live="polite"></p><button id="multiple-reconcile" type="button" class="btn secondary" hidden>Recargar estado e historial (sin reintentar)</button>
      <small>Una llamada al TAD por valor. Detener conserva la operación ya aceptada y descarta pendientes; no deshace el lote. No uses otra pestaña de esta sesión para modificar el mismo TAD durante la carga.</small>`;
    adapter.form.insertAdjacentElement('afterend', panel);
    const el=id=>panel.querySelector('#multiple-'+id), input=el('values');
    el('rule').textContent = (operation==='insertar_final' ? 'Se agrega al final, en el orden escrito. ' : operation==='apilar' ? 'Se apila en el orden escrito; el último queda en el tope. ' : operation==='encolar' ? 'Se encola en el orden escrito. ' : 'Se inserta en el orden escrito. ') + (unique.has(adapter.model.id) ? 'Este árbol no admite duplicados.' : 'Este TAD permite valores repetidos.');
    let locked=false, submittedInput=false;
    const disabledBefore=new Map();
    function lock(value) {
      if (value===locked) return; locked=value;
      if (value) {
        document.querySelectorAll('button,input,select,textarea').forEach(node=>{if(!panel.contains(node)){disabledBefore.set(node,node.disabled);node.disabled=true;}});
      } else { disabledBefore.forEach((disabled,node)=>{node.disabled=disabled;}); disabledBefore.clear(); adapter.sync?.(); }
    }
    root.MultipleInput.lockActiveControls=()=>{
      if(!locked) return false;
      document.querySelectorAll('button,input,select,textarea').forEach(node=>{
        if(!panel.contains(node)) {
          if(!disabledBefore.has(node)) disabledBefore.set(node,node.disabled);
          node.disabled=true;
        }
      });
      return true;
    };
    function preview() {
      const parsed=parse(input.value,adapter.model.id,adapter.model.visual_state?.traversals?.inorden||[]);
      el('preview').textContent=parsed.valid ? `${parsed.values.length} valores · Orden: ${parsed.values.join(' → ')}` : parsed.errors.join(' ');
      el('load').disabled=locked || submittedInput || !parsed.valid || adapter.isBusy(); el('step').disabled=el('load').disabled;
      input.setAttribute('aria-invalid',String(!parsed.valid)); return parsed;
    }
    root.MultipleInput.stateChanged=()=>{
      if(locked) return;
      if(queue.state().phase==='idle') { preview(); return; }
      submittedInput=false; el('status').textContent='La estructura cambió después del lote; revisa el estado y el historial actuales.'; preview();
    };
    const queue=createQueue(adapter,s=>{
      lock(s.active); input.disabled=s.active; el('load').disabled=s.active; el('step').disabled=s.active;
      el('controls').hidden=!s.active || s.phase==='uncertain';
      const trace=s.phase==='trace' && s.mode==='step';
      ['prev','next','play'].forEach(id=>{el(id).disabled=!trace||s.busy||s.playing;});
      el('prev').disabled ||= adapter.player.getCursor()<0;
      el('play').disabled ||= adapter.player.isAtEnd(); el('pause').disabled=!s.playing;
      el('stop').disabled=s.stopRequested;
      el('next').textContent=adapter.player.isAtEnd() ? (s.index===s.values.length-1 ? 'Finalizar lote' : 'Siguiente valor') : 'Siguiente paso';
      el('reconcile').hidden=s.phase!=='uncertain';
      el('status').textContent=`${s.active ? `Valor ${Math.min(s.index+1,s.values.length)} de ${s.values.length} · ${s.values[s.index]} · ` : ''}${s.message}`;
      if (!s.active) {
        if(submittedInput) {
          el('preview').textContent=`${s.values.length} valores · Orden solicitado: ${s.values.join(' → ')}`;
          el('load').disabled=true; el('step').disabled=true; input.setAttribute('aria-invalid','false');
        } else preview();
        el('status').textContent += ' Edita la lista para preparar otro lote.';
      }
    });
    function guard(event) {
      if (!locked) return;
      if (panel.contains(event.target)) {
        // Local buttons keep native Enter/Space, but must not reach the old global trace shortcuts.
        if(event.type==='keydown' && !event.target.matches('input,textarea')) {
          event.stopImmediatePropagation();
          if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) event.preventDefault();
        }
        return;
      }
      if (event.type==='keydown' && !['ArrowLeft','ArrowRight','Home','End',' ','Enter'].includes(event.key)) return;
      if (event.type==='click' && !event.target.closest('button,a,input,select,summary')) return;
      event.preventDefault(); event.stopImmediatePropagation();
    }
    ['click','submit','change','input','keydown'].forEach(type=>document.addEventListener(type,guard,true));
    window.addEventListener('beforeunload',event=>{if(locked){event.preventDefault();event.returnValue='';}});
    input.addEventListener('input',()=>{submittedInput=false;preview();});
    async function start(mode) {
      if (queue.state().active || submittedInput || adapter.isBusy()) return;
      const parsed=preview(); if(!parsed.valid) return;
      // Select the actual operation before the lock, so existing C/source UI stays honest.
      adapter.select(operation); submittedInput=true;
      await queue.start(parsed.values,mode);
    }
    el('load').addEventListener('click',()=>start('normal')); el('step').addEventListener('click',()=>start('step'));
    for(const id of ['prev','next','play','pause','stop']) el(id).addEventListener('click',()=>queue[id]());
    el('reconcile').addEventListener('click',()=>{
      try { window.sessionStorage.setItem('multiple-reconcile:'+adapter.model.id,JSON.stringify(queue.state())); } catch (_) { /* optional reminder */ }
      locked=false;window.location.reload();
    });
    try {
      const key='multiple-reconcile:'+adapter.model.id;
      const prior=JSON.parse(window.sessionStorage.getItem(key)||'null');
      if(prior) {
        window.sessionStorage.removeItem(key); panel.open=true;
        setTimeout(()=>{
          if(adapter.player.hasTrace()) adapter.player.seek(adapter.player.getTotalSteps()-1);
          el('status').textContent=`Estado e historial consultados de nuevo al servidor, sin repetir operaciones. La respuesta del valor ${prior.index+1} (${prior.values[prior.index]}) fue incierta: contrasta el historial y la estructura antes de introducir únicamente lo que falte.`;
          adapter.sync?.();
        },0);
      }
    } catch (_) { /* storage is optional */ }
    preview(); return queue;
  }
  root.MultipleInput={parse,createQueue,mount,fetchUnit,operations};
  if(typeof module!=='undefined' && module.exports) module.exports=root.MultipleInput;
})(typeof window!=='undefined'?window:globalThis);
