/* Presentation only: existing execution nodes and source text retain identity. */
(function (global) {
  "use strict";
  const mounted = new WeakMap();
  const clampZoom = value => Math.max(.5, Math.min(2.5, Math.round(Number(value) * 100) / 100 || 1));
  const resolve = (value, root = document) => typeof value === "string" ? root.querySelector(value) : value;
  function button(label, action) {
    const node = document.createElement("button"); node.type = "button";
    node.className = "btn secondary"; node.textContent = label;
    node.addEventListener("click", action); return node;
  }
  function sourceText(node) {
    if (!node) return "";
    if (typeof node.dataset?.rawCode === "string") return node.dataset.rawCode;
    const lines = Array.from(node.querySelectorAll?.(".code-line") || []);
    return lines.length ? lines.map(line => line.textContent).join("\n") : node.textContent;
  }
  function revealTechnical(node, boundary) {
    for (let current=node; current && current!==boundary; current=current.parentElement) current.classList.remove("didactic-technical");
  }
  async function copyText(text) {
    if (!navigator.clipboard?.writeText) throw new Error("El navegador no permite copiar; selecciona el texto del código.");
    await navigator.clipboard.writeText(text);
  }
  function enlarge(panel, title) {
    const origin = document.createComment("classroom-panel-origin");
    const panelX = panel.scrollLeft, panelY = panel.scrollTop;
    const focus = document.activeElement; const x = global.scrollX, y = global.scrollY;
    panel.before(origin); panel.classList.add("classroom-expanded-content");
    const dialog = document.createElement("dialog"); dialog.className = "classroom-dialog";
    const heading = document.createElement("h2"); heading.textContent = title;
    const close = button("Cerrar ampliación", () => dialog.close());
    dialog.append(heading, close, panel); document.body.append(dialog);
    dialog.addEventListener("close", () => {
      origin.replaceWith(panel); panel.classList.remove("classroom-expanded-content"); dialog.remove(); panel.scrollLeft = panelX; panel.scrollTop = panelY; focus?.focus?.({preventScroll:true}); global.scrollTo(x,y);
    }, {once:true});
    dialog.showModal(); panel.scrollLeft = panelX; panel.scrollTop = panelY; close.focus({preventScroll:true});
  }
  function addCodeActions(panel, code, title, getText, copyLabel = "Copiar C") {
    // Only C readers use no-wrap scrolling; printf output keeps its own contract.
    if (copyLabel !== "Copiar salida") {
      code.classList.add("classroom-code-scroll");
      code.setAttribute("tabindex", "0");
      code.setAttribute("aria-label", `${title}: desplazar horizontal y verticalmente para leer`);
    }
    const actions = document.createElement("div"); actions.className = "classroom-code-actions";
    const status = document.createElement("span"); status.setAttribute("role", "status");
    actions.append(button(copyLabel, async () => {
      try { await copyText(getText ? getText() : sourceText(code)); status.textContent = copyLabel === "Copiar salida" ? "Salida copiada." : "Código copiado."; }
      catch (error) { status.textContent = error.message; }
    }), button("Ampliar", () => enlarge(code, title)), status);
    panel.prepend(actions); return actions;
  }
  function fitScale(width,height,viewWidth,viewHeight,minFont) {
    const ideal=Math.min(viewWidth/width,viewHeight/height,1);
    const readable=minFont>0 ? 14/minFont : 1;
    const zoom=clampZoom(Math.max(Math.floor(ideal*100)/100,Math.ceil(readable*100)/100));
    return {zoom, fits:width*zoom<=viewWidth && height*zoom<=viewHeight, readable:minFont>0 && minFont*zoom>=14};
  }
  function mount(options) {
    const root = resolve(options.root); if (!root) return null;
    if (mounted.has(root)) return mounted.get(root);
    const visual = resolve(options.visual, root), stage = resolve(options.stage, root) || visual;
    const code = resolve(options.code, root);
    let zoom = 1, panX = 0, panY = 0, queued = false, stageRepainted = false;
    const memories = new Map();
    const memoryPanels = new Map();
    root.classList.add("classroom-workspace");
    visual?.classList.add("classroom-visual"); stage?.classList.add("classroom-stage");
    if (code) { revealTechnical(code,root); code.classList.add("classroom-source"); code.parentElement.classList.add("classroom-code"); addCodeActions(code.parentElement,code,"Código C",options.getCodeText); }
    const toolbar = document.createElement("div"); toolbar.className = "classroom-view-tools";
    const indicator = document.createElement("output"); indicator.setAttribute("aria-live", "polite");
    function refresh() {
      queued = false;
      if (stage) {
        Array.from(stage.children).forEach(child => {
          if (!child.matches("svg") && !child.querySelector("svg") && !child.classList.contains("classroom-memory")) child.style.zoom = String(zoom);
        });
        stage.querySelectorAll("svg").forEach(svg => {
          const box = (svg.getAttribute("viewBox") || "").trim().split(/[ ,]+/).map(Number);
          if (box.length === 4 && box.every(Number.isFinite) && box[2] > 0 && box[3] > 0) {
            svg.style.setProperty("width", `${box[2]*zoom}px`, "important");
            svg.style.setProperty("height", `${box[3]*zoom}px`, "important");
            svg.style.setProperty("max-width", "none", "important");
            svg.style.setProperty("max-height", "none", "important");
            svg.style.setProperty("flex", "0 0 auto", "important");
          }
        });
        stage.scrollLeft = panX; stage.scrollTop = panY;
      }
      const specs = Array.isArray(options.memory) ? options.memory : options.memory ? [options.memory] : [];
      specs.forEach((spec,index) => {
        // Prefer newly rendered content inside the stage over the previous external copy.
        const fresh=typeof spec === "string" && stage?.querySelector(spec);
        let panel=memoryPanels.get(index);
        if(stageRepainted && panel?.fromStage && !fresh){panel.node?.remove();panel.details.remove();memoryPanels.delete(index);return;}
        const node=fresh || resolve(spec,root);
        if (!node) return;
        if(panel?.node===node) return;
        if(!panel){
          const details=document.createElement("details");details.className="classroom-memory";
          details.open=memories.get(index)||false;
          const summary=document.createElement("summary");summary.textContent="Memoria y reservas · abrir / cerrar";
          details.append(summary);visual.append(details);
          details.addEventListener("toggle",()=>memories.set(index,details.open));
          panel={details,node:null,fromStage:Boolean(fresh)};memoryPanels.set(index,panel);
        }
        panel.node?.remove();panel.details.append(node);panel.node=node;

      });
      stageRepainted=false;
      const label = `${Math.round(zoom*100)}%`; if (indicator.textContent !== label) indicator.textContent = label;
    }
    function setZoom(value) { zoom=clampZoom(value); refresh(); return zoom; }
    function fitView() {
      const svgs=Array.from(stage?.querySelectorAll("svg") || []);
      let width=0,height=0,minFont=Infinity;
      svgs.forEach(svg=>{
        const box=String(svg.getAttribute("viewBox") || "").trim().split(/[ ,]+/).map(Number);
        if(box.length===4 && box[2]>0 && box[3]>0){width=Math.max(width,box[2]);height+=box[3];}
        svg.querySelectorAll("text").forEach(text=>{const size=parseFloat(global.getComputedStyle(text).fontSize);if(text.textContent.trim() && size>0)minFont=Math.min(minFont,size);});
      });
      if(!svgs.length && stage){
        width=stage.scrollWidth/zoom;height=stage.scrollHeight/zoom;
        stage.querySelectorAll("*").forEach(node=>{
          if(node.closest(".classroom-memory")) return;
          if(Array.from(node.childNodes).some(n=>n.nodeType===3 && n.textContent.trim())){
            const size=parseFloat(global.getComputedStyle(node).fontSize);if(size>0)minFont=Math.min(minFont,size);
          }
        });
      }
      if(!width || !height || !Number.isFinite(minFont)) { notice.textContent="No hay dimensiones y texto verificables para encajar; utiliza zoom y desplazamiento manual.";return; }
      const result=fitScale(width,height,Math.max(1,stage.clientWidth-8),Math.max(1,stage.clientHeight-8),minFont);
      setZoom(result.zoom);
      notice.textContent=!result.readable ? "No se puede garantizar texto de 14 px con este contenido; amplía manualmente." : result.fits ? "Vista encajada sin reducir el texto por debajo de 14 px." : "Para mantener texto de 14 px, desplaza la imagen con sus barras.";
    }
    const notice=document.createElement("span");notice.className="classroom-view-notice";notice.setAttribute("role","status");
    toolbar.append(button("−",()=>setZoom(zoom-.1)),indicator,button("+",()=>setZoom(zoom+.1)),button("100%",()=>setZoom(1)),button("Encajar vista",fitView),button("Centrar inicio",()=>{panX=panY=0;refresh();}),notice);
    toolbar.title="Zoom manual: se conserva al avanzar. Desplaza la imagen con sus barras.";
    if (visual && stage) { visual.insertBefore(toolbar,visual.firstChild); stage.addEventListener("scroll",()=>{panX=stage.scrollLeft;panY=stage.scrollTop;},{passive:true}); }
    if (options.results?.length) {
      const entries=options.results.map(item=>({...item,panel:resolve(item.panel)})).filter(item=>item.panel);
      if(entries.length) {
        const shell=document.createElement("section"); shell.className="classroom-results";
        const tabs=document.createElement("div"); tabs.className="classroom-result-tabs"; tabs.setAttribute("role","tablist");
        entries[0].panel.before(shell); shell.append(tabs);
        entries.forEach((entry,index)=>{
          const tab=button(entry.label,()=>select(index)); tab.setAttribute("role","tab");
          entry.tab=tab;
          if(!entry.panel.id) entry.panel.id=`classroom-result-${options.key || "view"}-${index}`;
          tab.setAttribute("aria-controls",entry.panel.id); entry.panel.setAttribute("role","tabpanel");
          tab.addEventListener("keydown",event=>{
            const delta=event.key==="ArrowRight"?1:event.key==="ArrowLeft"?-1:0;
            if(delta){event.preventDefault();const next=(index+delta+entries.length)%entries.length;select(next);entries[next].tab.focus();}
          });
          tabs.append(tab); shell.append(entry.panel); entry.panel.classList.add("classroom-result-panel"); revealTechnical(entry.panel,shell);
          if(entry.panel.tagName==="DETAILS") entry.panel.open=true;
          const c=resolve(entry.code,entry.panel); if(c) addCodeActions(entry.panel,c,entry.label,entry.getText,entry.copyLabel || (/consola/i.test(entry.label) ? "Copiar salida" : "Copiar C"));
        });
        function select(index){entries.forEach((entry,i)=>{entry.panel.hidden=i!==index;entry.tab.setAttribute("aria-selected",String(i===index));entry.tab.tabIndex=i===index?0:-1;});}
        select(0);
      }
    }
    const observer=new MutationObserver(records=>{
      if((records || []).some(record=>record.target===stage && (record.addedNodes.length || Array.from(record.removedNodes).some(node=>!Array.from(memoryPanels.values()).some(panel=>panel.node===node))))) stageRepainted=true;
      if(!queued){queued=true;queueMicrotask(refresh);}
    });
    if(stage) observer.observe(stage,{childList:true,subtree:true});
    // Auxiliary memory may be rebuilt alongside the drawing.
    if(visual && visual!==stage) observer.observe(visual,{childList:true,subtree:true});
    const api={refresh,setZoom,getState:()=>({zoom,panX,panY}),destroy:()=>observer.disconnect()};
    mounted.set(root,api); refresh(); return api;
  }
  global.ClassroomView={mount,sourceText,clampZoom,fitScale,enlarge,copyText};
})(window);
