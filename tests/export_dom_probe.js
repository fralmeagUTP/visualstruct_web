/* The E2E test and DOM-double controls execute this exact extractor. */
function extractExportEvidence(root) {
  const origin = root.getBoundingClientRect();
  const required = ['sorting-visual-state', 'sorting-pedagogy-narration', 'sorting-live-memory'];
  const relative = box => ({width: box.width, height: box.height,
    left: box.left - origin.left, top: box.top - origin.top,
    right: box.right - origin.left, bottom: box.bottom - origin.top});
  function painted(node) {
    for (let current = node; current; current = current.parentElement) {
      const style = getComputedStyle(current);
      if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility) ||
          Number(style.opacity) === 0 || current.hidden ||
          (current.tagName === 'DETAILS' && !current.open)) return false;
      if (current === root) break;
    }
    return true;
  }
  return [root, ...root.querySelectorAll('*')].map(node => {
    const style = getComputedStyle(node);
    const text = [];
    for (const child of node.childNodes) {
      if (child.nodeType !== 3 || !child.textContent.trim()) continue;
      const range = document.createRange(); range.selectNodeContents(child);
      let owner = node;
      while (owner && !required.includes(owner.id) && owner !== root) owner = owner.parentElement;
      const colorVisible = style.color !== 'transparent' && !/rgba\([^)]*,\s*0(?:\.0+)?\s*\)/.test(style.color);
      for (const rect of range.getClientRects()) text.push({...relative(rect),
        text: child.textContent.trim(), owner: owner?.id || '',
        painted: painted(node) && colorVisible, fontSize: parseFloat(style.fontSize)});
    }
    return {id: node.id, ...relative(node.getBoundingClientRect()), painted: painted(node), text};
  });
}
if (typeof module !== 'undefined') module.exports = extractExportEvidence;
