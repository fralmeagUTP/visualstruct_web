"use strict";

(function bootstrapInterpreterRuntime(globalScope) {
  const DIDACTIC_MODE_STORAGE_KEY = "didactic-mode";
  const DIDACTIC_MODE_VISUAL = "visual";
  const DIDACTIC_MODE_FULL = "full";
  const EXPORT_JPG_TARGET_IDS = [
    "graph-visual-state",
    "sorting-visual-state",
    "hash-visual-state",
    "visual-state",
  ];
  const EXPORT_JPG_MIN_QUALITY = 0.5;
  const EXPORT_JPG_MAX_QUALITY = 1;
  const EXPORT_JPG_MIN_SCALE = 1;
  const EXPORT_JPG_MAX_SCALE = 3;

  function normalizeDidacticMode(rawMode) {
    return rawMode === DIDACTIC_MODE_FULL ? DIDACTIC_MODE_FULL : DIDACTIC_MODE_VISUAL;
  }

  function readDidacticMode() {
    try {
      return normalizeDidacticMode(window.localStorage.getItem(DIDACTIC_MODE_STORAGE_KEY));
    } catch (error) {
      return DIDACTIC_MODE_VISUAL;
    }
  }

  function persistDidacticMode(mode) {
    try {
      window.localStorage.setItem(DIDACTIC_MODE_STORAGE_KEY, normalizeDidacticMode(mode));
    } catch (error) {
      // Ignore localStorage failures (private mode or blocked storage).
    }
  }

  function applyDidacticMode(mode) {
    const nextMode = normalizeDidacticMode(mode);
    document.documentElement.setAttribute("data-didactic-mode", nextMode);
    const modeSwitch = document.getElementById("didactic-mode-switch");
    if (modeSwitch instanceof HTMLInputElement) {
      modeSwitch.checked = nextMode === DIDACTIC_MODE_FULL;
    }
    return nextMode;
  }

  function initDidacticModeSwitch() {
    const modeSwitch = document.getElementById("didactic-mode-switch");
    const mode = applyDidacticMode(readDidacticMode());
    persistDidacticMode(mode);
    if (!(modeSwitch instanceof HTMLInputElement)) {
      return;
    }
    modeSwitch.addEventListener("change", () => {
      const nextMode = modeSwitch.checked ? DIDACTIC_MODE_FULL : DIDACTIC_MODE_VISUAL;
      applyDidacticMode(nextMode);
      persistDidacticMode(nextMode);
    });
  }

  function isElementVisible(element) {
    if (!element) {
      return false;
    }
    const style = window.getComputedStyle(element);
    if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) {
      return false;
    }
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function resolveVisualExportTarget() {
    for (let i = 0; i < EXPORT_JPG_TARGET_IDS.length; i += 1) {
      const candidate = document.getElementById(EXPORT_JPG_TARGET_IDS[i]);
      if (candidate && isElementVisible(candidate)) {
        return candidate;
      }
    }
    return null;
  }

  function setExportControlsVisibility(visible) {
    const exportControls = document.getElementById("export-jpg-controls");
    if (!(exportControls instanceof HTMLElement)) {
      return;
    }
    exportControls.style.display = visible ? "inline-flex" : "none";
  }

  function refreshExportControlsVisibility() {
    const target = resolveVisualExportTarget();
    setExportControlsVisibility(Boolean(target));
  }

  function resolveExportDimensions(target) {
    const rect = target.getBoundingClientRect();
    const width = Math.max(
      1,
      Math.round(
        Math.max(
          rect.width || 0,
          target.scrollWidth || 0,
          target.clientWidth || 0,
          target.offsetWidth || 0,
        ),
      ),
    );
    const height = Math.max(
      1,
      Math.round(
        Math.max(
          rect.height || 0,
          target.scrollHeight || 0,
          target.clientHeight || 0,
          target.offsetHeight || 0,
        ),
      ),
    );
    return { width, height };
  }

  function applyInlineComputedStyles(sourceRoot, clonedRoot) {
    if (!sourceRoot || !clonedRoot) {
      return;
    }
    const sourceNodes = [sourceRoot, ...Array.from(sourceRoot.querySelectorAll("*"))];
    const clonedNodes = [clonedRoot, ...Array.from(clonedRoot.querySelectorAll("*"))];
    const count = Math.min(sourceNodes.length, clonedNodes.length);
    for (let i = 0; i < count; i += 1) {
      const sourceNode = sourceNodes[i];
      const clonedNode = clonedNodes[i];
      if (!(sourceNode instanceof Element) || !(clonedNode instanceof Element)) {
        continue;
      }
      const computed = window.getComputedStyle(sourceNode);
      let styleText = "";
      for (let j = 0; j < computed.length; j += 1) {
        const prop = computed[j];
        styleText += `${prop}:${computed.getPropertyValue(prop)};`;
      }
      clonedNode.setAttribute("style", styleText);
    }
  }

  function replaceClonedCanvasWithImages(sourceRoot, clonedRoot) {
    const sourceCanvasList = Array.from(sourceRoot.querySelectorAll("canvas"));
    const clonedCanvasList = Array.from(clonedRoot.querySelectorAll("canvas"));
    const count = Math.min(sourceCanvasList.length, clonedCanvasList.length);
    for (let i = 0; i < count; i += 1) {
      const sourceCanvas = sourceCanvasList[i];
      const clonedCanvas = clonedCanvasList[i];
      if (!(sourceCanvas instanceof HTMLCanvasElement) || !(clonedCanvas instanceof HTMLCanvasElement)) {
        continue;
      }
      let imageUrl = "";
      try {
        imageUrl = sourceCanvas.toDataURL("image/png");
      } catch (error) {
        imageUrl = "";
      }
      if (!imageUrl) {
        continue;
      }
      const img = document.createElement("img");
      img.src = imageUrl;
      img.alt = "";
      img.width = sourceCanvas.width || sourceCanvas.clientWidth || 0;
      img.height = sourceCanvas.height || sourceCanvas.clientHeight || 0;
      img.style.width = `${sourceCanvas.clientWidth}px`;
      img.style.height = `${sourceCanvas.clientHeight}px`;
      clonedCanvas.replaceWith(img);
    }
  }

  function toSvgForeignObjectMarkup(contentHtml, width, height) {
    return (
      `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">` +
      `<foreignObject x="0" y="0" width="100%" height="100%">` +
      `<div xmlns="http://www.w3.org/1999/xhtml">${contentHtml}</div>` +
      "</foreignObject></svg>"
    );
  }

  function normalizeExportQuality(rawValue) {
    const parsed = Number(rawValue);
    if (!Number.isFinite(parsed)) {
      return 0.92;
    }
    return Math.min(EXPORT_JPG_MAX_QUALITY, Math.max(EXPORT_JPG_MIN_QUALITY, parsed));
  }

  function normalizeExportScale(rawValue) {
    const parsed = Number(rawValue);
    if (!Number.isFinite(parsed)) {
      return 2;
    }
    return Math.min(EXPORT_JPG_MAX_SCALE, Math.max(EXPORT_JPG_MIN_SCALE, Math.round(parsed)));
  }

  function drawImageToJpegDataUrl(image, width, height, quality, scale) {
    const canvas = document.createElement("canvas");
    const targetScale = normalizeExportScale(scale);
    canvas.width = Math.max(1, Math.round(width * targetScale));
    canvas.height = Math.max(1, Math.round(height * targetScale));
    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("No se pudo crear contexto 2D.");
    }
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", normalizeExportQuality(quality));
  }

  function loadImageFromSource(src) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      let settled = false;
      const finish = (error) => {
        if (settled) return;
        settled = true;
        window.clearTimeout(timer);
        image.onload = null;
        image.onerror = null;
        if (error) { image.src = ""; reject(error); }
        else resolve(image);
      };
      const timer = window.setTimeout(() => finish(new Error("La imagen SVG no termino de cargar en 5 segundos.")), 5000);
      image.onload = () => finish();
      image.onerror = () => finish(new Error("No se pudo cargar la imagen SVG intermedia."));
      image.src = src;
      // Decode is also observable when an engine does not deliver a load event.
      if (typeof image.decode === "function") image.decode().then(() => finish(), () => {});
    });
  }

  async function renderSvgMarkupToJpegDataUrl(svgMarkup, width, height, quality, scale, onProgress) {
    const blob = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
    const objectUrl = URL.createObjectURL(blob);
    const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgMarkup)}`;
    // Chromium can taint a canvas for a blob SVG containing foreignObject.
    // A self-contained data URL preserves its origin-clean rasterization path.
    const sources = [dataUrl, objectUrl];
    let lastError = null;
    try {
      for (let index = 0; index < sources.length; index += 1) {
        try {
          onProgress?.(`Cargando imagen ${index + 1}/2...`);
          const image = await loadImageFromSource(sources[index]);
          onProgress?.("Creando JPG...");
          return drawImageToJpegDataUrl(image, width, height, quality, scale);
        } catch (error) {
          lastError = error;
        }
      }
      throw lastError || new Error("No se pudo rasterizar la visualizacion.");
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  function prepareClassroomExportClone(cloned) {
    // Full evidence export is independent of the live zoom, pan and folded memory.
    cloned.querySelectorAll(".classroom-view-tools, .classroom-code-actions, .hash-view-options").forEach(node => node.remove());
    Array.from(cloned.querySelectorAll("details.classroom-memory, details.classroom-memory details")).reverse().forEach(node => {
      node.open = true;
      // Chromium can defer a formerly closed details content box. Export a static
      // expanded block, rather than measuring/serializing a disclosure widget.
      if (node.replaceWith && node.attributes) {
        const block = document.createElement("div");
        for (const attr of Array.from(node.attributes)) if (attr.name !== "open") block.setAttribute(attr.name, attr.value);
        while (node.firstChild) block.appendChild(node.firstChild);
        node.replaceWith(block);
      }
    });
    [cloned, ...Array.from(cloned.querySelectorAll("*"))].forEach(node => {
      if (node.style) node.style.zoom = "1";
    });
  }

  function expandHierarchicalExportClone(cloned, originalWidth) {
    // Only the detached export copy loses the classroom's scroll/flex budget.
    const nodes = [cloned, ...Array.from(cloned.querySelectorAll("*"))];
    let contentWidth = originalWidth;
    for (const node of nodes) {
      if (node instanceof HTMLElement) {
        // Data-bearing bar dimensions are not viewport constraints.
        if (node.matches?.(".sorting-item-bar, .sorting-zero-track, .sorting-zero-axis, .sorting-state-symbol")) continue;
        node.style.height = "auto";
        node.style.maxHeight = "none";
        node.style.maxWidth = "none";
        node.style.width = "auto";
        node.style.flex = "0 0 auto";
        node.style.overflow = "visible";
        node.style.overflowX = "visible";
        node.style.overflowY = "visible";
        node.style.gridTemplateRows = "none";
        if (node.style.setProperty) {
          for (const [property,value] of Object.entries({height:"auto","max-height":"none","max-width":"none",width:"auto",flex:"0 0 auto",overflow:"visible","overflow-x":"visible","overflow-y":"visible"})) node.style.setProperty(property,value,"important");
        }
      } else if (node.tagName?.toLowerCase() === "svg") {
        const box = String(node.getAttribute("viewBox") || "").trim().split(/[ ,]+/).map(Number);
        if (box.length === 4 && box.every(Number.isFinite) && box[2] > 0 && box[3] > 0) {
          // Preserve coordinates and aspect ratio, not the compact viewport crop.
          node.style.width = `${box[2]}px`;
          node.style.height = `${box[3]}px`;
          node.style.minWidth = "0";
          node.style.maxWidth = "none";
          node.style.maxHeight = "none";
          node.style.flex = "0 0 auto";
          node.style.overflow = "visible";
          contentWidth = Math.max(contentWidth, box[2] + 48);
        }
      }
    }
    cloned.style.display = "block";
    cloned.style.margin = "0";
    cloned.style.width = `${Math.ceil(contentWidth)}px`;
    const stage = document.createElement("div");
    stage.style.cssText = "position:fixed;left:0;top:0;transform:translateX(-200%);visibility:hidden;pointer-events:none;z-index:-1;";
    stage.style.width = cloned.style.width;
    stage.setAttribute("aria-hidden", "true");
    stage.appendChild(cloned);
    try {
      document.body.appendChild(stage);
      const origin = cloned.getBoundingClientRect();
      let width = Math.max(contentWidth, cloned.scrollWidth, origin.width);
      let height = Math.max(cloned.scrollHeight, origin.height);
      for (const node of nodes) {
        const bounds = node.getBoundingClientRect();
        if (bounds.width === 0 && bounds.height === 0) continue; // Closed details/hidden rows.
        width = Math.max(width, bounds.right - origin.left);
        height = Math.max(height, bounds.bottom - origin.top);
      }
      return { width: Math.max(1, Math.ceil(width)), height: Math.max(1, Math.ceil(height)) };
    } finally {
      cloned.remove();
      stage.remove();
    }
  }

  function resolveCompleteVisualExportTarget(target) {
    // Graph/Hash current memory is a sibling of the drawing/result, not inside it.
    // Both the panel action and the global export must capture the same region.
    if (target?.id === "visual-state" && target.closest?.(".classroom-workspace")) {
      return target.closest?.("#hier-visual-region, #seq-visual-region") || target;
    }
    if (target?.id === "sorting-visual-state" && target.closest?.(".classroom-workspace")) {
      return target.closest?.("#sorting-visual-region") || target;
    }
    if (target?.id === "graph-visual-state") {
      return target.closest?.("#graph-visual-region") || target;
    }
    if (target?.id === "hash-visual-state") {
      return target.closest?.("#hash-visual-region") || target;
    }
    return target;
  }

  async function exportVisualStateAsJpg(options) {
    const target = resolveCompleteVisualExportTarget(options && options.target ? options.target : resolveVisualExportTarget());
    if (!target) {
      throw new Error("No hay un panel visual disponible para exportar.");
    }

    const onProgress = typeof options?.onProgress === "function" ? options.onProgress : null;
    onProgress?.("Preparando captura...");
    let { width, height } = resolveExportDimensions(target);

    const cloned = target.cloneNode(true);
    if (!(cloned instanceof HTMLElement)) {
      throw new Error("No se pudo clonar el panel visual.");
    }

    applyInlineComputedStyles(target, cloned);
    // The empty Sorting paragraph's top margin collapses outside its source
    // target. The clipped foreignObject wrapper must preserve its text origin.
    if (target.id === "sorting-visual-state" && target.children.length === 1 &&
        target.firstElementChild?.matches("p.muted")) {
      cloned.firstElementChild.style.marginTop = "0px";
    }
    replaceClonedCanvasWithImages(target, cloned);
    prepareClassroomExportClone(cloned);
    if (target.id === "hash-visual-region") cloned.querySelector?.(".hash-view-toolbar")?.remove();
    if (target.id === "hier-visual-region" || target.closest?.("#hier-visual-region") || target.id === "graph-visual-region" || target.id === "hash-visual-region" || target.closest?.(".classroom-workspace")) {
      ({ width, height } = expandHierarchicalExportClone(cloned, width));
    }

    // Importante: anular clipping del contenedor original (scroll/max-height)
    // para capturar el contenido completo de la visualizacion.
    cloned.style.margin = "0";
    cloned.style.width = `${width}px`;
    cloned.style.height = `${height}px`;
    cloned.style.maxWidth = "none";
    cloned.style.maxHeight = "none";
    cloned.style.overflow = "visible";
    cloned.style.overflowX = "visible";
    cloned.style.overflowY = "visible";
    cloned.style.boxSizing = "border-box";

    const wrapper = document.createElement("div");
    wrapper.style.background = "#ffffff";
    wrapper.style.width = `${width}px`;
    wrapper.style.height = `${height}px`;
    wrapper.style.padding = "0";
    wrapper.style.margin = "0";
    wrapper.style.overflow = "hidden";
    wrapper.appendChild(cloned);

    const markup = toSvgForeignObjectMarkup(new XMLSerializer().serializeToString(wrapper), width, height);
    const quality = normalizeExportQuality(options && options.quality);
    const scale = normalizeExportScale(options && options.scale);
    const dataUrl = await renderSvgMarkupToJpegDataUrl(markup, width, height, quality, scale, onProgress);
    return {
      dataUrl,
      width,
      height,
      scale,
      quality,
      suggestedName: `${target.id || "visual"}-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-")}.jpg`,
    };
  }

  function triggerDataUrlDownload(dataUrl, fileName) {
    const match = /^data:image\/jpeg;base64,(.+)$/.exec(String(dataUrl));
    if (!match) throw new Error("La captura no produjo un JPG valido.");
    const binary = window.atob(match[1]);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    const objectUrl = URL.createObjectURL(new Blob([bytes], { type: "image/jpeg" }));
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = fileName || "visualizacion.jpg";
    document.body.appendChild(link);
    try {
      link.click();
      // Keep the URL alive while the browser accepts the asynchronous download.
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
    } catch (error) {
      URL.revokeObjectURL(objectUrl);
      throw error;
    } finally {
      link.remove();
    }
  }

  function initExportJpgButton() {
    const exportButton = document.getElementById("export-visual-jpg-btn");
    const qualitySelect = document.getElementById("export-jpg-quality");
    const scaleSelect = document.getElementById("export-jpg-scale");
    if (!(exportButton instanceof HTMLButtonElement)) {
      return;
    }
    refreshExportControlsVisibility();

    let visibilityFrame = 0;
    const requestVisibilityRefresh = () => {
      if (visibilityFrame) {
        return;
      }
      visibilityFrame = window.requestAnimationFrame(() => {
        visibilityFrame = 0;
        refreshExportControlsVisibility();
      });
    };

    const observer = new MutationObserver(requestVisibilityRefresh);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["style", "class", "hidden"],
    });

    window.addEventListener("resize", requestVisibilityRefresh);

    exportButton.addEventListener("click", async () => {
      const target = resolveVisualExportTarget();
      if (!target) {
        window.alert("No hay un estado visual activo para exportar.");
        refreshExportControlsVisibility();
        return;
      }
      const originalText = exportButton.textContent || "Exportar JPG";
      exportButton.disabled = true;
      if (qualitySelect instanceof HTMLSelectElement) {
        qualitySelect.disabled = true;
      }
      if (scaleSelect instanceof HTMLSelectElement) {
        scaleSelect.disabled = true;
      }
      exportButton.textContent = "Exportando...";
      try {
        const selectedQuality = qualitySelect instanceof HTMLSelectElement ? qualitySelect.value : 0.92;
        const selectedScale = scaleSelect instanceof HTMLSelectElement ? scaleSelect.value : 2;
        const result = await exportVisualStateAsJpg({
          target,
          quality: selectedQuality,
          scale: selectedScale,
          onProgress: (message) => { exportButton.textContent = message; },
        });
        triggerDataUrlDownload(result.dataUrl, result.suggestedName);
      } catch (error) {
        // Exponer detalle en consola para facilitar depuracion del navegador/entorno.
        console.error("Export JPG error:", error);
        window.alert(error.message || "No fue posible exportar la visualizacion en JPG.");
      } finally {
        exportButton.disabled = false;
        if (qualitySelect instanceof HTMLSelectElement) {
          qualitySelect.disabled = false;
        }
        if (scaleSelect instanceof HTMLSelectElement) {
          scaleSelect.disabled = false;
        }
        exportButton.textContent = originalText;
        refreshExportControlsVisibility();
      }
    });
  }

  function initGlobalUiControls() {
    initDidacticModeSwitch();
    initExportJpgButton();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobalUiControls, { once: true });
  } else {
    initGlobalUiControls();
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function sleep(ms) {
    return new Promise((resolve) => {
      window.setTimeout(resolve, ms);
    });
  }

  function ensureCodeLines(codeElement) {
    if (!codeElement) {
      return [];
    }
    let lines = Array.from(codeElement.querySelectorAll(".code-line"));
    if (lines.length) {
      return lines;
    }

    const raw = codeElement.dataset.rawCode || codeElement.textContent || "";
    const rows = String(raw).replaceAll("\r\n", "\n").split("\n");
    codeElement.innerHTML = rows
      .map((line, index) => `<span class="code-line" data-line="${index}">${escapeHtml(line) || ""}</span>`)
      .join("");
    lines = Array.from(codeElement.querySelectorAll(".code-line"));
    return lines;
  }

  function clearLineClasses(lines) {
    lines.forEach((line) => {
      line.classList.remove("sim-active");
      line.classList.remove("sim-done");
      line.classList.remove("sim-skip");
    });
  }

  const C_KEYWORDS = new Set([
    "if", "else", "for", "while", "do", "switch", "case", "default", "break",
    "continue", "return", "sizeof", "typedef", "struct", "enum", "union",
    "static", "const", "volatile", "extern", "goto", "NULL", "true", "false",
  ]);

  const C_TYPES = new Set([
    "void", "int", "bool", "float", "double", "char", "short", "long",
    "signed", "unsigned", "size_t",
  ]);

  function isIdentStart(ch) {
    return /[A-Za-z_]/.test(ch);
  }

  function isIdentChar(ch) {
    return /[A-Za-z0-9_]/.test(ch);
  }

  function nextNonSpaceChar(text, from) {
    let i = from;
    while (i < text.length && /\s/.test(text[i])) {
      i += 1;
    }
    return i < text.length ? text[i] : "";
  }

  function highlightCLine(line, state) {
    const text = String(line || "");
    const out = [];
    let i = 0;
    const inState = { inBlockComment: Boolean(state && state.inBlockComment) };

    if (/^\s*#/.test(text)) {
      return { html: `<span class="code-directive">${escapeHtml(text)}</span>`, state: inState };
    }

    while (i < text.length) {
      const ch = text[i];
      const next = i + 1 < text.length ? text[i + 1] : "";

      if (inState.inBlockComment) {
        const end = text.indexOf("*/", i);
        if (end === -1) {
          out.push(`<span class="code-comment">${escapeHtml(text.slice(i))}</span>`);
          i = text.length;
          break;
        }
        out.push(`<span class="code-comment">${escapeHtml(text.slice(i, end + 2))}</span>`);
        i = end + 2;
        inState.inBlockComment = false;
        continue;
      }

      if (ch === "/" && next === "/") {
        out.push(`<span class="code-comment">${escapeHtml(text.slice(i))}</span>`);
        i = text.length;
        break;
      }

      if (ch === "/" && next === "*") {
        const end = text.indexOf("*/", i + 2);
        if (end === -1) {
          out.push(`<span class="code-comment">${escapeHtml(text.slice(i))}</span>`);
          inState.inBlockComment = true;
          i = text.length;
        } else {
          out.push(`<span class="code-comment">${escapeHtml(text.slice(i, end + 2))}</span>`);
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
        out.push(`<span class="code-string">${escapeHtml(text.slice(i, j))}</span>`);
        i = j;
        continue;
      }

      if (/[0-9]/.test(ch)) {
        let j = i + 1;
        while (j < text.length && /[0-9A-Fa-fxXuUlL\.]/.test(text[j])) {
          j += 1;
        }
        out.push(`<span class="code-number">${escapeHtml(text.slice(i, j))}</span>`);
        i = j;
        continue;
      }

      if (isIdentStart(ch)) {
        let j = i + 1;
        while (j < text.length && isIdentChar(text[j])) {
          j += 1;
        }
        const word = text.slice(i, j);
        let cls = "";
        if (C_TYPES.has(word)) {
          cls = "code-type";
        } else if (C_KEYWORDS.has(word)) {
          cls = "code-keyword";
        } else if (nextNonSpaceChar(text, j) === "(") {
          cls = "code-function";
        }
        out.push(cls ? `<span class="${cls}">${escapeHtml(word)}</span>` : escapeHtml(word));
        i = j;
        continue;
      }

      if ("{}[]();,*".includes(ch)) {
        out.push(`<span class="code-punct">${escapeHtml(ch)}</span>`);
        i += 1;
        continue;
      }

      out.push(escapeHtml(ch));
      i += 1;
    }

    return { html: out.join(""), state: inState };
  }

  function renderCode(codeElement, sourceCode, codeTitle) {
    if (!codeElement) {
      return;
    }
    const raw = String(sourceCode || "");
    codeElement.dataset.rawCode = raw;
    codeElement.dataset.codeTitle = String(codeTitle || "");
    const rows = raw.replaceAll("\r\n", "\n").split("\n");
    if (String(codeTitle || "").toLowerCase().includes("codigo c")) {
      let state = { inBlockComment: false };
      codeElement.innerHTML = rows
        .map((line, index) => {
          const highlighted = highlightCLine(line, state);
          state = highlighted.state;
          return `<span class="code-line" data-line="${index}">${highlighted.html || ""}</span>`;
        })
        .join("");
      return;
    }
    codeElement.innerHTML = rows
      .map((line, index) => `<span class="code-line" data-line="${index}">${escapeHtml(line) || ""}</span>`)
      .join("");
  }

    function setStatus(statusElement, text) {
      if (!statusElement) {
        return;
      }
      statusElement.textContent = text || "";
    }

    function stepStatusText(step, currentIndex, totalSteps) {
      let status = `Paso ${currentIndex}/${totalSteps}`;
      const debug = step && typeof step.debug === "object" ? step.debug : null;
      if (!debug) {
        return status;
      }
      const stage = String(debug.stage || "").trim();
      const note = String(debug.note || "").trim();
      if (stage && note) {
        return `${status} - ${stage}: ${note}`;
      }
      if (stage) {
        return `${status} - ${stage}`;
      }
      if (note) {
        return `${status} - ${note}`;
      }
      return status;
    }

  function createTracePlayer(options) {
    const codeElement = options ? options.codeElement : null;
    const renderState = options ? options.renderState : null;
    const statusElement = options ? options.statusElement : null;
    const counterElement = options ? options.counterElement : null;
    const onCursorChange = options ? options.onCursorChange : null;
    const defaultDelayMs = options && Number.isFinite(options.defaultDelayMs)
      ? Number(options.defaultDelayMs)
      : 170;
    const retainDoneLines = Boolean(options && options.retainDoneLines);

    let trace = null;
    let lines = [];
    let cursor = -1;
    let playing = false;
    let playToken = 0;
    let speedMultiplier = 1;

    function normalizeSpeed(raw) {
      const parsed = Number(raw);
      if (!Number.isFinite(parsed)) {
        return 1;
      }
      return Math.min(4, Math.max(0.25, parsed));
    }

    function emitCursorChange(reason, step) {
      if (typeof onCursorChange !== "function") {
        return;
      }
      onCursorChange({
        reason: reason || "",
        trace,
        cursor,
        step: step || null,
      });
    }

    function setCounter(current, total) {
      if (!counterElement) {
        return;
      }
      const safeCurrent = Math.max(0, Number.isFinite(current) ? Number(current) : 0);
      const safeTotal = Math.max(0, Number.isFinite(total) ? Number(total) : 0);
      counterElement.textContent = `Paso: ${safeCurrent}/${safeTotal}`;
    }

    function resetVisualLines() {
      lines = ensureCodeLines(codeElement);
      clearLineClasses(lines);
    }

    function applyStateSnapshot(step) {
      if (typeof renderState === "function" && step && step.state_snapshot) {
        renderState(step.state_snapshot, step);
      }
    }

    function applyStateAfter(step) {
      if (typeof renderState === "function" && step && step.state_after) {
        renderState(step.state_after, step);
      }
    }

    function markPreviousAsDone(previousIndex) {
      if (!retainDoneLines) {
        return;
      }
      if (previousIndex < 0 || previousIndex >= (trace?.steps?.length || 0)) {
        return;
      }
      const prev = trace.steps[previousIndex] || {};
      const prevLineIndex = Number.isInteger(prev.line_index) ? prev.line_index : -1;
      const previousLine = prevLineIndex >= 0 ? lines[prevLineIndex] : null;
      if (previousLine) {
        previousLine.classList.remove("sim-active");
        previousLine.classList.add("sim-done");
      }
    }

    function activateCurrentLine(step) {
      const lineIndex = Number.isInteger(step.line_index) ? step.line_index : -1;
      lines.forEach((line) => {
        line.classList.remove("sim-active");
        if (!retainDoneLines) {
          line.classList.remove("sim-done");
        }
      });
      const currentLine = lineIndex >= 0 ? lines[lineIndex] : null;
      if (!currentLine) {
        return;
      }
      currentLine.classList.add("sim-active");
      window.CCodeNavigation?.revealLine(codeElement, currentLine);
    }

    function finalizeLastLineIfNeeded() {
      if (!retainDoneLines) {
        return;
      }
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length || cursor < 0) {
        return;
      }
      const current = trace.steps[cursor] || {};
      const lineIndex = Number.isInteger(current.line_index) ? current.line_index : -1;
      const line = lineIndex >= 0 ? lines[lineIndex] : null;
      if (!line) {
        return;
      }
      line.classList.remove("sim-active");
      line.classList.add("sim-done");
    }

    function paintDoneLinesTo(indexInclusive) {
      if (!retainDoneLines || !trace || !Array.isArray(trace.steps)) {
        return;
      }
      for (let idx = 0; idx <= indexInclusive; idx += 1) {
        const step = trace.steps[idx] || {};
        const lineIndex = Number.isInteger(step.line_index) ? step.line_index : -1;
        const doneLine = lineIndex >= 0 ? lines[lineIndex] : null;
        if (doneLine) {
          doneLine.classList.add("sim-done");
        }
      }
    }

    async function _advanceOne(withDelay, token) {
      if (!trace || !Array.isArray(trace.steps) || cursor >= trace.steps.length - 1) {
        return false;
      }

      const previousIndex = cursor;
      const nextIndex = cursor + 1;
      const step = trace.steps[nextIndex] || {};
      if (withDelay) {
        const delay = Number.isFinite(step.delay_ms) ? Number(step.delay_ms) : defaultDelayMs;
        const scaledDelay = Math.round(delay / speedMultiplier);
        await sleep(Math.max(12, scaledDelay));
        if (token !== playToken) {
          return false;
        }
      }
      // Commit the code highlight and executed state together. A pause/reset
      // during the delay must not leave the next instruction highlighted.
      markPreviousAsDone(previousIndex);
      activateCurrentLine(step);
      applyStateAfter(step);
      cursor = nextIndex;
      setCounter(cursor + 1, trace.steps.length);
      setStatus(statusElement, stepStatusText(step, cursor + 1, trace.steps.length));

      if (cursor >= trace.steps.length - 1) {
        finalizeLastLineIfNeeded();
      }
      emitCursorChange("advance", step);
      return true;
    }

    async function _playLoop(fromStart) {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para reproducir.");
        return;
      }
      if (fromStart) {
        reset();
      }
      if (cursor >= trace.steps.length - 1) {
        reset();
      }
      playing = true;
      const token = ++playToken;

      while (playing && token === playToken && cursor < trace.steps.length - 1) {
        const advanced = await _advanceOne(true, token);
        if (!advanced) {
          break;
        }
      }
      if (token !== playToken) {
        return;
      }
      if (cursor >= trace.steps.length - 1) {
        playing = false;
        setStatus(statusElement, `Simulacion completada (${trace.steps.length} pasos).`);
      }
    }

    function loadTrace(newTrace) {
      trace = newTrace && Array.isArray(newTrace.steps) ? newTrace : null;
      playing = false;
      playToken += 1;

      cursor = -1;
      if (!trace) {
        resetVisualLines();
        setCounter(0, 0);
        setStatus(statusElement, "No hay traza cargada.");
        emitCursorChange("load", null);
        return;
      }
      if (trace.source_code) {
        renderCode(codeElement, trace.source_code, trace.code_title || "");
      }
      resetVisualLines();
      cursor = -1;
      const firstStep = trace.steps[0] || null;
      if (firstStep) {
        applyStateSnapshot(firstStep);
      }
      setCounter(0, trace.steps.length);
      setStatus(statusElement, `Simulacion lista: ${trace.steps.length} pasos.`);
      emitCursorChange("load", firstStep);
    }

    function clear(message) {
      pause();
      trace = null;
      cursor = -1;
      if (codeElement) {
        const clearLines = ensureCodeLines(codeElement);
        clearLineClasses(clearLines);
      }
      setCounter(0, 0);
      setStatus(statusElement, message || "Ejecuta una operacion para generar la simulacion.");
      emitCursorChange("clear", null);
    }

    function pause(silent) {
      if (!trace) {
        return;
      }
      playing = false;
      playToken += 1;
      if (!silent) {
        setStatus(statusElement, "Simulacion pausada.");
      }
    }

    function reset() {
      if (!trace) {
        return;
      }
      pause();
      resetVisualLines();
      cursor = -1;
      const firstStep = trace.steps[0] || null;
      if (firstStep) {
        applyStateSnapshot(firstStep);
      }
      setCounter(0, trace.steps.length);
      setStatus(statusElement, `Simulacion reiniciada (${trace.steps.length} pasos).`);
      emitCursorChange("reset", firstStep);
    }

    async function step() {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para avanzar.");
        return false;
      }
      pause(true);
      if (cursor >= trace.steps.length - 1) {
        setStatus(statusElement, "Simulacion completada. Ingresa nuevos datos para continuar.");
        return false;
      }
      return _advanceOne(false, playToken);
    }

    function prev() {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para retroceder.");
        return false;
      }
      pause(true);
      if (cursor < 0) {
        setStatus(statusElement, "Ya estas en el inicio de la simulacion.");
        return false;
      }
      if (cursor === 0) {
        resetVisualLines();
        cursor = -1;
        const firstStep = trace.steps[0] || null;
        if (firstStep) {
          applyStateSnapshot(firstStep);
        }
        setCounter(0, trace.steps.length);
        setStatus(statusElement, `Paso 0/${trace.steps.length}`);
        emitCursorChange("prev_to_start", firstStep);
        return true;
      }

      const previousIndex = cursor - 1;
      const previousStep = trace.steps[previousIndex] || {};
      resetVisualLines();
      paintDoneLinesTo(previousIndex - 1);
      activateCurrentLine(previousStep);
      applyStateAfter(previousStep);
      cursor = previousIndex;
      setCounter(cursor + 1, trace.steps.length);
      setStatus(statusElement, stepStatusText(previousStep, cursor + 1, trace.steps.length));
      emitCursorChange("prev", previousStep);
      return true;
    }

    function seek(targetIndex) {
      if (!trace || !Array.isArray(trace.steps) || !trace.steps.length) {
        setStatus(statusElement, "No hay traza para navegar.");
        return false;
      }
      pause(true);
      const parsed = Number(targetIndex);
      const target = Number.isFinite(parsed) ? Math.max(-1, Math.min(Math.trunc(parsed), trace.steps.length - 1)) : cursor;
      resetVisualLines();
      if (target < 0) {
        cursor = -1;
        const firstStep = trace.steps[0] || null;
        if (firstStep) applyStateSnapshot(firstStep);
        setCounter(0, trace.steps.length);
        setStatus(statusElement, `Paso 0/${trace.steps.length}`);
        emitCursorChange("seek", firstStep);
        return true;
      }
      const targetStep = trace.steps[target] || {};
      paintDoneLinesTo(target - 1);
      activateCurrentLine(targetStep);
      applyStateAfter(targetStep);
      cursor = target;
      setCounter(cursor + 1, trace.steps.length);
      setStatus(statusElement, stepStatusText(targetStep, cursor + 1, trace.steps.length));
      emitCursorChange("seek", targetStep);
      return true;
    }

    function hasTrace() {
      return Boolean(trace && Array.isArray(trace.steps) && trace.steps.length);
    }

    function setSpeed(multiplier) {
      speedMultiplier = normalizeSpeed(multiplier);
    }

    function getSpeed() {
      return speedMultiplier;
    }

    function getCursor() {
      return cursor;
    }

    function getTotalSteps() {
      return trace && Array.isArray(trace.steps) ? trace.steps.length : 0;
    }

    function isAtEnd() {
      const total = getTotalSteps();
      return total > 0 && cursor >= total - 1;
    }

    return {
      loadTrace,
      clear,
      pause,
      play: () => _playLoop(false),
      playFromStart: () => _playLoop(true),
      step,
      prev,
      seek,
      reset,
      hasTrace,
      setSpeed,
      getSpeed,
      getCursor,
      getTotalSteps,
      isAtEnd,
    };
  }

  async function playExecutionTrace(options) {
    const trace = options && options.trace ? options.trace : null;
    const codeElement = options ? options.codeElement : null;
    const renderState = options ? options.renderState : null;
    if (!trace || !codeElement) {
      return;
    }
    const player = createTracePlayer({
      codeElement,
      renderState,
      statusElement: options ? options.statusElement : null,
      defaultDelayMs: options ? options.defaultDelayMs : null,
    });
    player.loadTrace(trace);
    await player.playFromStart();
  }

  globalScope.InterpreterRuntime = {
    ensureCodeLines,
    renderCode,
    createTracePlayer,
    playExecutionTrace,
    exportVisualStateAsJpg,
    downloadJpg: triggerDataUrlDownload,
  };
}(window));
