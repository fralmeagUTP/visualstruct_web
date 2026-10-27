# Shared presentation controller — classroom v1

Scope: `static/js/classroom_view.js`, `static/css/classroom_view.css`, imports in
`templates/base.html`; export-only adaptation in `interpreter_runtime.js`.
No backend/source C/H, playback algorithm or stdout producer changed.

API: `ClassroomView.mount({root,visual,stage,code,memory,results,key,getCodeText})`.
DOM nodes or selectors accepted. Root is the two-column workspace, visual its
stable visual region, stage its stable renderer target. Memory selectors may
identify dynamically recreated auxiliary panels. Results hold existing panels,
not cloned content; optional getText supplies raw source.

Zoom starts at100%, range50–250%, explicit only. New SVG children get natural
viewBox dimensions at the selected zoom; their coordinates/origin are untouched.
HTML-only diagram children use presentation zoom. Local pan persists in this
page across renderer child replacement and next/back. Browser navigation starts
fresh at100%; no persisted cross-structure state. Memory openness persists across
recreated panels in the page and starts closed. Main TAD nodes are not memory
selectors. Source copy prefers exact dataset.rawCode (even empty/CRLF), then
joins rendered code lines with newline; no synthetic line numbers/NBSP inserted.
Ampliar moves the same node into a modal, then restores its position, focus and
window scroll on close/Escape. No execute/reload handler is called.

Results reserve300px and use accessible tabs with arrow navigation. Console
content is not rewritten. Header, navigation and control padding compacted while
retaining identity, fields and all actions.

Export: detached copy opens only classroom-memory details, removes zoom/action
controls and resets zoom. Existing measured clone expansion includes all drawing
and memory, independent of live scroll/folds. Sorting v1 target is promoted to
its visual region to include the memory sibling. LiveDOM is not modified.

Validation:7controller tests +18existing export tests pass (25 total), logs
combined_shared_export.log. Independent reviewer verified10real code renderers,
20raw/fallbackcopy routes. Before/after continuity gates recorded. Browser sizing,
actual interaction and JPEG pixels are the exclusive UI auditor's remaining
validation, not claimed by these Node model tests.

## QA corrections 11:40 UTC
Actual browser review prompted C index height budget44px and intrinsic-width
scrollable function items (AVL multi-function overlap fixed), modal history single
full-height scroller, and sticky execution controls. Memory details now live
outside the panned stage. New rendered memory replaces prior content; absence in
a later renderer clears old auxiliary evidence. A20-repaint model regression
checks identity/open state/no stale duplicates.
Explicit Encajar vista measures content and actual font sizes; readable minimum
14px takes precedence over fitting, with honest pan/limit messages. No automatic
fit on mount/next/back. Current suite10controller+18export=28PASS. Pixel retests
remain independently recorded by UI auditor.

## Real-browser corrections through12:00 UTC
- CVUI002: memory is outside the panned stage; while opened it receives~180px
  with a temporary smaller drawing. Closing restores≥300px drawing without
  growing the workspace. Hash actual185px memory/150px drawing, closed307px,
  accepted by UI reviewer. All source nodes/data remain available.
- CVUI004: function index is one non-wrapping row, intrinsic widths and horizontal
  scroll. CVUI006: Sorting included in these shared rules. Controls extracted by
  family owner use the shared sticky classroom-execution-controls style.
- CVUI005: instruction-memory sequential cell grids auto-fit170px, excluding
  renderers with explicit vertical arrow children so adjacency is not changed.
- CVUI007: selected result tab explicitly overrides old learning-level hiding of
  console/TAD; inactive tabs remain hidden. Copy bytes unchanged.
- CVUI009: compact Hash options,20px minimap without clipped indices,14px node
  fields. UI reviewer confirmed actual indices0..16 and memory readability.
- CVUI008: real Sorting JPG exposed two limitations absent from initial Node
  tests: generic expansion erased absolute bar dimensions, and formerly closed
  details retained a clipped content box. Clone now preserves data-bearing bar
  geometry, overrides important viewport constraints during offscreen measurement,
  and materializes ONLY classroom-memory disclosures as static expanded blocks
  before measuring. No liveDOM change. Real panel JPEG retest PASS12:00; global
  and other families still pending independent pixels at this writing.

Current shared suite12tests +18export regression tests =30PASS. New tests preserve
bar dimensions, important viewport override and all evidence identities during
static-disclosure conversion. No Node test is claimed to replace browser pixels.

## Final finite closure12:04 UTC
Lead relayed independent UI acceptance:10JPEG panel/global across5families plus
extra red-black export complete; memory open/close, Cola grid and modal no pending
blockers. Sorting panel/global bytes already individually confirmed above.
Current code frozen; no speculative changes. Final rerun30/30PASS in
`combined_shared_export_final.log`; exact four shared app-file SHA256 values in
`shared_final_manifest.json`. Full UI evidence remains in auditor-owned qa_ui.
New page navigation intentionally resets zoom to100%; within-page next/back and
renderer refresh preserve explicit choice and local pan. Optional memory opening
shares height temporarily; minimum300px drawing applies when it is closed.
