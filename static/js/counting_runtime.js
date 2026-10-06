/* Counting-only paged replay. Ordinary trace players retain their original contract. */
(function (scope) {
  "use strict";
  const providers = new WeakMap();
  const isPaged = (trace) => trace?.schema === "counting-paged-trace/v1";
  const total = (trace) => isPaged(trace) ? trace.step_count : (trace?.steps?.length || 0);
  function provider(trace) {
    if (providers.has(trace)) return providers.get(trace);
    const pages = new Map();
    let pending = Promise.resolve();
    const seed = new Map((trace.initial_page?.steps || []).map((s) => [s.step_index, s]));
    function remember(start, steps) {
      pages.delete(start); pages.set(start, steps);
      while (pages.size > 4) pages.delete(pages.keys().next().value);
    }
    async function request(query) {
      const response = await fetch(`${trace.manifest.page_url}?${new URLSearchParams(query)}`, { credentials: "same-origin", cache: "no-store" });
      const data = await response.json();
      if (!response.ok || !data.success || data.trace_id !== trace.trace_id) throw new Error(data.message || "La pagina de Counting no esta disponible.");
      return data;
    }
    async function get(index) {
      if (index < 0 || index >= total(trace)) return null;
      if (seed.has(index)) return seed.get(index);
      const start = Math.floor(index / 64) * 64;
      if (pages.has(start)) return pages.get(start)[index-start];
      // Serialize and recheck: rapid seeks share at most one in-flight GET per trace.
      const task = pending.catch(() => {}).then(async () => {
        if (!pages.has(start)) { const data = await request({ start, limit: 64 }); remember(start, data.steps); }
        return pages.get(start)[index-start];
      });
      pending = task;
      return task;
    }
    const api = { get, locate: async (concept, occurrence) => (await request({ concept, occurrence, limit: 1 })).steps[0], cacheSize: () => pages.size };
    providers.set(trace, api); return api;
  }
  async function frame(trace, index) { return isPaged(trace) ? provider(trace).get(index) : trace?.steps?.[index] || null; }
  async function locate(trace, concept, occurrence) {
    if (isPaged(trace)) return provider(trace).locate(concept, occurrence);
    const matches = (trace?.steps || []).filter((s) => s.pedagogy?.concept === concept);
    return matches[Math.min(Math.max(occurrence-1, 0), matches.length-1)] || null;
  }
  function createPagedPlayer(options) {
    let trace = null, cursor = -1, desired = -1, navigation = 0, playToken = 0, speed = 1;
    const code = options.codeElement, status = options.statusElement, counter = options.counterElement;
    function report(message) { if (status) status.textContent = message; }
    function count() { if (counter) counter.textContent = `Paso: ${Math.max(0,cursor+1)}/${total(trace)}`; }
    function paint(step, initial, reason) {
      const lines = scope.InterpreterRuntime.ensureCodeLines(code);
      lines.forEach((line) => { line.classList.remove("sim-active", "sim-done"); });
      if (options.retainDoneLines && !initial) (step.done_lines || []).forEach((index) => lines[index]?.classList.add("sim-done"));
      if (!initial && Number.isInteger(step.line_index)) {
        lines[step.line_index]?.classList.add("sim-active");
        lines[step.line_index]?.scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
      options.renderState?.(initial ? step.state_snapshot : step.state_after, step);
      count(); report(`Paso ${Math.max(0,cursor+1)}/${total(trace)} - ${step.debug?.note || "Counting"}`);
      options.onCursorChange?.({ reason, trace, cursor, step });
    }
    function pause(silent) { playToken++; if (!silent) report("Simulacion pausada."); }
    function reset() {
      pause(true); navigation++; cursor = desired = -1;
      const first = trace?.initial_page?.steps?.[0]; if (first) paint(first, true, "reset");
    }
    function loadTrace(value) {
      pause(true); navigation++; trace = value; cursor = desired = -1;
      if (trace?.source_code) scope.InterpreterRuntime.renderCode(code, trace.source_code, trace.code_title);
      const first = trace?.initial_page?.steps?.[0]; if (first) paint(first, true, "load"); else count();
    }
    async function move(target, reason, playbackToken) {
      const version = ++navigation, ownTrace = trace;
      desired = target;
      try {
        const step = await frame(ownTrace, Math.max(0,target));
        if (version !== navigation || ownTrace !== trace || (playbackToken !== undefined && playbackToken !== playToken)) return false;
        if (!step) return false;
        cursor = target; paint(step, target < 0, reason); return true;
      } catch (error) { if (version === navigation && ownTrace === trace) { desired = cursor; pause(true); report(error.message); } return false; }
    }
    function seek(target) {
      pause(true);
      const parsed = Number(target);
      const index = Number.isFinite(parsed) ? Math.max(-1, Math.min(Math.trunc(parsed), total(trace)-1)) : cursor;
      return move(index, "seek");
    }
    async function step() {
      pause(true); if (desired >= total(trace)-1) return false;
      return move(desired+1, "advance");
    }
    function prev() { return seek(desired-1); }
    async function play() {
      if (!trace) return;
      if (cursor >= total(trace)-1) reset();
      const token = ++playToken;
      while (trace && token === playToken && cursor < total(trace)-1) {
        if (!(await move(cursor+1, "advance", token))) break;
        await new Promise((resolve) => setTimeout(resolve, Math.max(12,160/speed)));
      }
    }
    function clear(message) { pause(true); navigation++; trace = null; cursor = desired = -1; count(); report(message || "No hay traza cargada."); options.onCursorChange?.({ reason:"clear", trace:null, cursor, step:null }); }
    return { loadTrace, seek, step, prev, reset, clear, pause, play, playFromStart:async()=>{reset();await play();}, hasTrace:()=>Boolean(trace), getCursor:()=>cursor, getTotalSteps:()=>total(trace), isAtEnd:()=>Boolean(trace)&&cursor>=total(trace)-1, setSpeed:(value)=>{speed=Math.min(4,Math.max(0.25,Number(value)||1));}, getSpeed:()=>speed };
  }
  function createCompatiblePlayer(options) {
    const legacy = scope.InterpreterRuntime.createTracePlayer(options);
    const paged = createPagedPlayer(options);
    let active = legacy, trace = null;
    const api = { loadTrace(value) { active.pause(true); trace=value; active=isPaged(value)?paged:legacy; active.loadTrace(value); }, getStep:(index)=>frame(trace,index) };
    for (const name of ["seek","step","prev","reset","clear","pause","play","playFromStart","hasTrace","getCursor","getTotalSteps","isAtEnd","setSpeed","getSpeed"]) api[name]=(...args)=>active[name](...args);
    return api;
  }
  scope.CountingRuntime = { isPaged, total, frame, locate, createCompatiblePlayer, cachePages:(trace)=>isPaged(trace)?provider(trace).cacheSize():0 };
}(window));
