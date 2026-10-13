# C-RBT-VALIDAR-LIMIT-01: open quality limitation for global closure

Severity: medium. Status: OPEN, product decision pending; not solved by reaching7/7 recorded methods.

Current Rojo-Negro Validar checks black root, strict BST order and no red-red parent/child. The Python wrapper and canonical C main helpers agree for those checks, and the label/manual describe that restricted scope. They do not check uniform black height, parent-link integrity or cycles. Thus an OK does not certify the complete red-black representation. Existing independent native fixture checkers include stronger properties; their passing results are not the product's validator capability.

Evidence: app/domain/hierarchical/tad_wrappers.py RojoNegro.validar/_validar_rec; canonical helper/source tested in visible-red-black-query-main-low and visible-red-black-query-instruction-review; guide explicitly restricts the claim. The insertion/deletion native oracle separately checks order, parents, colors, root black and equal black height for finite fixtures.

Decision needed before global closure: accept this documented partial validator as the current product contract, or authorize a scoped extension of both backend and canonical C helpers with negative black-height/parent/cycle fixtures. Do not silently add this semantic behavior during deletion fidelity work. Keep it open in findings/progress/tasks regardless of method playback coverage; no application change made here.


## Concrete proposal prepared in LOW

See red-black-validation-extension-proposal.md for V1/V2/V3, V3recommended including actual C/H, compatibility/main/traces/docs impact and plannednegativefixtures. Two existing partial-validator counterexamples (blackheight,parentlink) were observed in backend and canonical C helper against independent native invariants; evidence:red-black-validator-extension-proposal-low. No extension implemented, no option approved; status stays OPEN. RBT7/7 is separately recorded, not an acceptance of this limitation.


## Implementación V3 registrada 2026-10-03

La nuevaaprobaciónextend-red-black-full-validation/decision.md supersede la decisiónpendiente. El defectoparcial fue corregido enalcancefinito del checkpoint red-black-full-validation-implementation-checkpoint-medium.md:exportC/H+RAWwrapper+traza/main,17fixtures17/17. No reescribir conclusioneshistóricas ni declarar auditoríaRN/globalcerrada;reviewC1propio pendiente.


## RN V3 finite functional closure LOW

QAindependientefuncional/documentalACEPTADA, RN-IMPL-01resuelto;ver red-black-full-validator-finite-closure-decision-low.md y evidence/visible-red-black-full-validator-finite-closure-low/closure-evidence.json. Cierresóloalcancefinito;sanitizers/global/C1pendientesseparados,noarchive,noreimplementación.
