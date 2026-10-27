/* Observed stdout only: this cache is not execution or reconstruction of C. */
(function () {
  "use strict";
  const states = new WeakMap();
  function publish(el, stdout, emptyText = "(sin salida printf en esta ruta)") {
    if (!el) return;
    const top = el.scrollTop, left = el.scrollLeft;
    const atEnd = el.scrollHeight - el.clientHeight - top <= 4;
    const text = String(stdout ?? "");
    el.dataset.consoleCopy = text;
    el.textContent = text || emptyText;
    el.style.whiteSpace = "pre";
    el.scrollTop = atEnd ? el.scrollHeight : top;
    el.scrollLeft = left;
  }
  function save(state) {
    try { sessionStorage.setItem(state.key, JSON.stringify({version: 2, history: state.history, base: state.base, current: state.current, emitted: state.emitted, furthestCursor: state.furthestCursor, token: state.token})); } catch (_) { /* optional cache */ }
  }
  function bind(el, key, history) {
    if (!el) return;
    const state = {key: "observed-stdout-v1:" + location.pathname + ":" + key, history: JSON.stringify(history || []), base: "", current: "", emitted: "", furthestCursor: -1, token: null, trace: null, restored: false};
    try {
      const cached = JSON.parse(sessionStorage.getItem(state.key) || "null");
      if (cached?.version === 2 && cached.history === state.history && typeof cached.base === "string" && typeof cached.current === "string" && typeof cached.emitted === "string" && Number.isInteger(cached.furthestCursor)) Object.assign(state, {base: cached.base, current: cached.current, emitted: cached.emitted, furthestCursor: cached.furthestCursor, token: cached.token, restored: true});
      else sessionStorage.removeItem(state.key);
    } catch (_) { /* optional cache */ }
    states.set(el, state);
    publish(el, state.base + state.current);
  }
  function setHistory(el, history) {
    const state = states.get(el);
    if (state && Array.isArray(history)) { state.history = JSON.stringify(history); state.restored = false; save(state); }
  }
  function render(el, trace, cursor, stdout) {
    const state = states.get(el);
    if (!state) { publish(el, stdout); return; }
    // Clearing the active visual trace must not erase the session transcript.
    if (trace) {
      if (state.trace !== trace) {
        const token = trace.trace_id || JSON.stringify(trace);
        if (!(state.restored && state.token === token)) { state.base += state.emitted; state.current = ""; state.emitted = ""; state.furthestCursor = -1; }
        state.restored = false;
        state.trace = trace; state.token = token;
      }
      state.current = typeof stdout === "string" ? stdout : "";
      // Rewind changes the view, not what this operation has already emitted.
      // A new operation archives only the furthest prefix actually observed.
      if (Number.isInteger(cursor) && cursor >= state.furthestCursor) {
        state.emitted = state.current;
        state.furthestCursor = cursor;
      }
    }
    publish(el, state.base + state.current);
    save(state);
  }
  function reset(el) {
    const state = states.get(el);
    if (state) { state.base = ""; state.current = ""; state.emitted = ""; state.furthestCursor = -1; state.token = null; state.trace = null; state.history = "[]"; save(state); }
    publish(el, "");
  }
  window.ConsoleHistory = {publish, bind, setHistory, render, reset};
})();
