/* Only whole comment lines may be hidden; pointer dereferences are executable C. */
(function (scope) {
  "use strict";
  function commentOnlyLines(source) {
    let block = false, quote = null;
    return String(source || "").replaceAll("\r\n", "\n").split("\n").map(line => {
      let code = false, comment = block;
      for (let i = 0; i < line.length; i++) {
        const c = line[i], next = line[i + 1];
        if (block) {
          comment = true;
          if (c === "*" && next === "/") { block = false; i++; }
          continue;
        }
        if (quote) {
          code = true;
          if (c === "\\") { i++; continue; }
          if (c === quote) quote = null;
          continue;
        }
        if (c === "/" && next === "/") { comment = true; break; }
        if (c === "/" && next === "*") { comment = true; block = true; i++; continue; }
        if (c === '"' || c === "'") quote = c;
        if (!/\s/.test(c)) code = true;
      }
      // Valid C string/character literals cannot cross an unescaped newline.
      if (!line.endsWith("\\")) quote = null;
      return comment && !code;
    });
  }
  function markComments(code, rows) {
    const flags = commentOnlyLines(Array.isArray(rows) ? rows.join("\n") : rows);
    code?.querySelectorAll(".code-line").forEach((line, index) => line.classList.toggle("is-code-comment", Boolean(flags[index])));
    return flags;
  }
  function revealLine(panel, line) {
    if (!panel || !line || typeof panel.getBoundingClientRect !== "function" || typeof line.getBoundingClientRect !== "function") return;
    const box = panel.getBoundingClientRect(), item = line.getBoundingClientRect();
    const top = box.top + (panel.clientTop || 0), bottom = top + panel.clientHeight;
    if (item.top < top) panel.scrollTop += item.top - top;
    else if (item.bottom > bottom) panel.scrollTop += item.bottom - bottom;
  }
  scope.CCodeNavigation = { commentOnlyLines, markComments, revealLine };
}(window));
