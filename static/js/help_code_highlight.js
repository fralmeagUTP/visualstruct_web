"use strict";

function helpEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const HELP_C_KEYWORDS = new Set([
  "if", "else", "for", "while", "do", "switch", "case", "default", "break",
  "continue", "return", "sizeof", "typedef", "struct", "enum", "union",
  "static", "const", "volatile", "extern", "goto", "NULL", "true", "false",
]);

const HELP_C_TYPES = new Set([
  "void", "int", "bool", "float", "double", "char", "short", "long",
  "signed", "unsigned", "size_t",
]);

function isHelpIdentStart(ch) {
  return /[A-Za-z_]/.test(ch);
}

function isHelpIdentChar(ch) {
  return /[A-Za-z0-9_]/.test(ch);
}

function nextNonSpaceChar(text, from) {
  let i = from;
  while (i < text.length && /\s/.test(text[i])) {
    i += 1;
  }
  return i < text.length ? text[i] : "";
}

function highlightHelpCLine(line, state) {
  const text = String(line || "");
  const out = [];
  let i = 0;
  const inState = { inBlockComment: Boolean(state && state.inBlockComment) };

  if (/^\s*#/.test(text)) {
    return { html: `<span class="code-directive">${helpEscape(text)}</span>`, state: inState };
  }

  while (i < text.length) {
    const ch = text[i];
    const next = i + 1 < text.length ? text[i + 1] : "";

    if (inState.inBlockComment) {
      const end = text.indexOf("*/", i);
      if (end === -1) {
        out.push(`<span class="code-comment">${helpEscape(text.slice(i))}</span>`);
        i = text.length;
        break;
      }
      out.push(`<span class="code-comment">${helpEscape(text.slice(i, end + 2))}</span>`);
      i = end + 2;
      inState.inBlockComment = false;
      continue;
    }

    if (ch === "/" && next === "/") {
      out.push(`<span class="code-comment">${helpEscape(text.slice(i))}</span>`);
      i = text.length;
      break;
    }

    if (ch === "/" && next === "*") {
      const end = text.indexOf("*/", i + 2);
      if (end === -1) {
        out.push(`<span class="code-comment">${helpEscape(text.slice(i))}</span>`);
        inState.inBlockComment = true;
        i = text.length;
      } else {
        out.push(`<span class="code-comment">${helpEscape(text.slice(i, end + 2))}</span>`);
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
      out.push(`<span class="code-string">${helpEscape(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (/[0-9]/.test(ch)) {
      let j = i + 1;
      while (j < text.length && /[0-9A-Fa-fxXuUlL\.]/.test(text[j])) {
        j += 1;
      }
      out.push(`<span class="code-number">${helpEscape(text.slice(i, j))}</span>`);
      i = j;
      continue;
    }

    if (isHelpIdentStart(ch)) {
      let j = i + 1;
      while (j < text.length && isHelpIdentChar(text[j])) {
        j += 1;
      }
      const word = text.slice(i, j);
      let cls = "";
      if (HELP_C_TYPES.has(word)) {
        cls = "code-type";
      } else if (HELP_C_KEYWORDS.has(word)) {
        cls = "code-keyword";
      } else if (nextNonSpaceChar(text, j) === "(") {
        cls = "code-function";
      }
      out.push(cls ? `<span class="${cls}">${helpEscape(word)}</span>` : helpEscape(word));
      i = j;
      continue;
    }

    if ("{}[]();,*".includes(ch)) {
      out.push(`<span class="code-punct">${helpEscape(ch)}</span>`);
      i += 1;
      continue;
    }

    out.push(helpEscape(ch));
    i += 1;
  }

  return { html: out.join(""), state: inState };
}

function highlightHelpCodeBlock(preElement) {
  if (!preElement) {
    return;
  }
  if (preElement.querySelector(".code-line")) {
    return;
  }

  const raw = String(preElement.textContent || "");
  const lines = raw.replaceAll("\r\n", "\n").split("\n");
  let state = { inBlockComment: false };
  const html = lines
    .map((line, index) => {
      const highlighted = highlightHelpCLine(line, state);
      state = highlighted.state;
      return `<span class="code-line" data-line="${index}">${highlighted.html || "&nbsp;"}</span>`;
    })
    .join("");
  preElement.innerHTML = html;
}

document.addEventListener("DOMContentLoaded", () => {
  const blocks = Array.from(document.querySelectorAll("pre.didactic-code"));
  blocks.forEach((block) => highlightHelpCodeBlock(block));
});

