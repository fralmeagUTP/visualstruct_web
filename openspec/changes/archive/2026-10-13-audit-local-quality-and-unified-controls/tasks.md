# Tareas — implementación aprobada, auditoría en curso

- [x] Localizar checkout limpio y confirmar commit/equipo; preservar original mediante copia local autorizada.
- [x] Leer instrucciones OpenSpec y localizar propuestas previas, menú, controles y ruta de descarga C/H.
- [x] Completar revisión de cada requisito/delta/tarea vigente abierto y archivado; publicar clasificación mantenido/sustituido/verificar/fuera de alcance con motivo y evidencia. Ver reconciliation-detailed.md y evidence/prior-commitment-reconciliation.json: 18 cambios previos, 16 specs actuales, 106 fuentes SHA verificadas y 1653 compromisos/secciones. Clasificación documental; no declara cumplimiento funcional ni reabre archivos/casillas anteriores.
- [x] Incorporar inspección de píxeles de las tres referencias realizada por el agente principal; distinguirla de QA dinámico local.
- [x] Obtener aprobación explícita de este borrador y resolver supuestos.
- [x] Tras aprobación, iniciar servidor oculto sin cerrar otros procesos; verificar puerto libre, HTTP y URL local Desktop-FM; comunicarla inmediatamente.
- [x] Confirmar navegador/Playwright realmente lanzable; declarar límites y alternativa manual si falla.
- [x] Construir inventario y matriz exhaustiva desde rutas, adapters, algoritmos, controles, manual y descargas reales.
- [x] Medir línea base: suite, cobertura, C toolchain, navegador, Doxygen; registrar versiones, comandos, revisión y salidas.
- [x] Ejecutar matriz de funcionalidad, error, límites, aislamiento de sesiones, historial y replay. Evidencia: 110 resultados/estados esperados independientes (dos aleatorios por restricciones), 180 escenarios adicionales, 13 TAD con dos clientes HTTP, reset y reconstrucción por GET; E2E de ambas vistas/navegación sin POST. Alcance basado en riesgo y semillas documentadas, no todas las combinaciones de entrada ni equivalencia C por instrucción.
- [x] Ejecutar oráculo C instrumentado y contrastar estado/eventos por paso con backend/traza/UI; analizar UB, malloc/free, alias, recursión e invariantes. Aceptación finita QA19:38: [acta y límites](criteria11-12-16-finite-QA-acceptance-acta-low.md).
- [x] Auditar sección 2 por instrucción en todas las operaciones/TAD, vistas individual/enlazada aplicables y adelante/atrás; verificar resaltado, antes/después, consola, memoria, líneas sin mutación y ausencia de estados futuros/remutación. Aceptación finita QA19:38: [acta y límites](criteria11-12-16-finite-QA-acceptance-acta-low.md).
- [x] Descargar C/H desde HTTP, verificar nombres/cabeceras/bytes, compilar conjunto real, generar Doxygen y revisar advertencias y exactitud por símbolo.
- [x] Contrastar manual/ayudas con operaciones, controles, formatos y límites reales; documentar faltantes. Aceptación actual: criterion14-current-acceptance-decision-low.md; 13 ayudas/129 snippets/26 descargas HTTP y manual actual ligados a revisión semántica previa. Criterios causales/handlers11/12/16 y QA18 separados.
- [x] Medir Pila y todos los módulos en resoluciones acordadas; teclado, foco, zoom y ausencia de scroll indebido. Evidencia: browser-final-menu.json (52 combinaciones) y accessibility-reflow.json (13 TAD); zoom CSS 200% es aproximación de reflujo, no zoom nativo ni certificación de lector de pantalla/contraste.
- [x] Implementar únicamente menú, controles y documentación aprobados con pruebas de regresión significativas. Aceptación finita QA19:38: [acta y límites](criteria11-12-16-finite-QA-acceptance-acta-low.md).
- [x] Consultar antes de cambios semánticos mayores o decisiones ambiguas. Aceptación íntegra de obligación de consulta para cambios ejecutados: criterion17-consultation-acceptance-decision-low.md y registro decisión/contrato/fuentes/evidencia. C1/session-state conserva reconciliación técnica/documental, sin nueva semántica seleccionada.
- [x] Ejecutar pruebas aplicables en revisión final, cobertura y C/sanitizadores disponibles; registrar lo no ejecutable sin fingir resultados. Aceptación finita QA final y reservas: [acta18/delta19](criteria18-acceptance-and19-RN-V3-documentary-addendum-low.md).
- [x] Entregar matriz, hallazgos, evidencias, diff, instrucciones locales y límites; mantener propuesta sin archivar hasta decisión correspondiente. Aceptación técnica finita QA19 y reservas: [acta final](criterion19-finite-QA-acceptance-final-acta-low.md).

- [x] Verificar las cinco etapas exactas en los 13 TAD, fases de Grafos y once métodos de Ordenamiento; conservar aprendizaje adicional dentro de las etapas correspondientes.

## Evidencia de avance
Aprobación explícita recibida: «Ok. Puedes comenzar con el plan de implementación, con las tareas». Servidor Desktop-FM iniciado desde D: en 127.0.0.1:5051, GET /sequential/stack HTTP 200; usuario confirmó apertura. Chromium local lanzado y 13 TAD inspeccionados. Ver `progress.md` y `evidence/`. Las casillas restantes NO equivalen a trabajo terminado por existir una suite verde.


## Ampliación autorizada: limpieza de código y descargas
- [x] Retirar únicamente inversión legacy de Lista enlazada tras comprobar dependencias; actualizar C/H HTTP, wrapper/API/mapas/documentación/pruebas y verificar siete métodos visibles y conservación de inversión circular. Evidencia: evidence/retired-linked-reverse, 147 pruebas aprobadas, 26 Doxygen aislados/colectivo sin advertencias, DOM siete métodos y API400 sin mutación.
- [x] Auditar raíces de uso y dependencias para depuración adicional; distinguir UI real, API oculta e internals en inventario actual, eliminar solo código demostrado innecesario y consultar ruptura API ambigua. Disposiciones/source-consumers explícitos en criterion22-root-disposition-acceptance-decision-low.md; todos los grupos/11API retenidos, ningún borrado ni ruptura adicional justificado.

Se agregan dos tareas: denominador pasa de 20 a 22; las 12 verificadas anteriores permanecen como evidencia histórica, sin estimación de porcentaje de tiempo.


## AVL main/history verified compatible checkpoint

29 targeted tests pass129.29s. Three real histories, nine actual mains strictC17/no warnings plus generator preflight;77 successful query entries, each retained across GET without operation redispatch/extraPOST. Canonical helpers included once, actual computed results/ascending inorden, decimal normalization and failures omitted. Evidence: evidence/visible-avl-main-history-reproduction-fixed/README.md. C/H/FE algorithms unchanged. avl-fe-decision-proposal.md pending; ABB Validarheld. Global 13/22/docs59/208 unchanged; no new global completion checkbox.


## Altura AVL verified instruction checkpoint

1/9 AVL visible instruction families verified for recorded cases: five valid native fixtures,196 events (191 callee+5 caller),206 steps,412 bidirectional UI rows,5 actual displayed callers strictC17. Native6 tests pass3.03s; Chromium E2E1 pass84.71s. C/H unchanged, no replayPOST or JSerrors. Evidence: evidence/visible-avl-height-instruction-review/README.md. FEAVL and ValidarABB held; global13/22/docs59/208 unchanged. Remaining AVL instruction families: Buscar, Minimo, Maximo, Inorden, Limpiar, Insertar, Eliminar, Validar.


## Buscar AVL verified instruction checkpoint

AVL2/9 recorded families (Altura,Buscar). Final16 tests pass80.21s:9 nativeBuscar,1 Chromium8cases,6 Altura regressions.101 nativeevents/117steps/234 replayrows/8 displayedcallers strictC17; completeheap/parents/FE,scopes,borrowedreturns and boolean conversion; no replayPOST/JSerrors,C/H unchanged. Evidencia: evidence/visible-avl-search-instruction-review/README.md. Remaining7families and FEdecision held; global13/22/docs59/208 unchanged.


## Inorden AVL and query-result boundary verified

AVL3/9 recorded instruction families (Altura,Buscar,Inorden). Inorden:5 valid nativefixtures,185events (180helper+5caller),180steps/360replayrows,5 exact-helper programs strictC17;22targetedtests pass85.76s. Latest28tests pass for7 message-boundary E2Es plus21 native queryregressions; result appears only atcompletion and hides onrewind, using existingbuttons,no newPOST. Evidencia: evidence/visible-avl-inorden-instruction-review/README.md. C/H unchanged; main-localhelper not counted aspublicsymbol. Remaining6families,FEAVL and ValidarABB decisions held; global13/22/docs59/208 unchanged; finalaggregate gatepending.


## Minimo/Maximo AVL verified instruction checkpoint

AVL5/9 recordedfamilies. Extrema10cases/100events (49Minimo,51Maximo)/200replayrows;12tests pass96.41s.20 strictC17 programs (10 equivalentcallers+10actualmains),actualmainsDoxygen0; no replayPOST/JSerrors. EmptyAPI400/resultabsent distinguished from nonNULL minimumC precondition and rawmaximumNULL; alias/locals/outputint faithfully shown. Evidencia: evidence/visible-avl-extreme-instruction-review/README.md. C/H unchanged; global13/22/docs59/208 unchanged. RemainingLimpiar,Insertar,Eliminar,Validar; FEAVL/ValidarABBheld,finalappgatepending.


## Limpiar AVL verified instruction checkpoint

AVL6/9 recordedfamilies. Limpiar5valid nativefixtures/190events/15frees/200steps/400replayrows;16tests pass128.74s.10distinct actual/equivalent strictC17 programs;5actualmainsDoxygen0,actualcaller assertsNULL andallocations==frees. No replayPOST/JSerrors; historicalaliases,voidscopes and separateNULLassignment; no C/H/FEchange. After Desktoprecovery8relevantfile byte comparisons match testedartifacts; no duplicatefullrun. Evidencia: evidence/visible-avl-clear-instruction-review/README.md. Insertar/Eliminar/FE and changesValidarheld; global13/22/docs59/208 unchanged,finalgateopen.


## Heap copy/history/native documentation checkpoint

22targeted tests pass (8/122.72s +14/20.93s), full-copy0/1/255/256/257/513, actual repeated-success history/reload identical main/zeroPOST, raw null/empty/output/capacity guards, copy-allocation failure, strictC17 and actual main+C/H Doxygen0. C algorithm tokens unchanged.15 productprograms +2 probes; instruction query scalar/buffer/callee oracle stillpending, not fullfamilyclosure. Evidencia: evidence/visible-heap-copy-history-contract-fixed/README.md. Documentation61/208 reviewed,147pending; global13/22 unchanged. FEAVL/ValidarABBheld; finalgateopen.


## Heap queries native checkpoint; UI pending

17native/regression tests pass11.75s,281real-C observations/10cases, correct capacity20/40, separate output/buffer/scopes/loops/returns/free and readonly source. C/H unchanged. Browser final verification stillrunning session9515 (heap-query-browser-boundary.log); collect without duplicate, no family/global checkbox closure. Evidencia: evidence/visible-heap-query-instruction-review/README.md. Global 13/22/docs61/208 unchanged; FEAVL/ValidarABBheld. MEDIUM semantic reasoning boundary complete; routine browser collection continuesLOW.


## Verified LOW checkpoint (supersedes UI-pending checkpoint)

Browser run completed:2 tests passed178.54s,10 query cases,281 displayed instruction steps/562 forward-back observations,10 equivalent callers and10 actual history programs compiled strict C17; actual history main+C/H Doxygen0. Both array/tree plus independent destination/scalar checked; replay produced no POST. Screenshots and program sources retained in evidence/visible-heap-query-instruction-review. Native block17 passed11.75s; following guide/nullable metadata correction16 focused native/domain tests passed8.82s. Latest C/H edits are documentation only; executable-token guard checked when applied. Guide distinguishes readonly queries, initialized destination cells, historical freed records and capacity20/40. Current preview smoke verified request16=>20,21st insertion=>40,18 extractions retain40/count3. Heap recorded instruction coverage2/5 (raiz,a_lista); insertar,extraer_raiz,limpiar still require instruction review. Global 13/22 and documentation61/208 remain; getter NULL fixes are verified by focused regression but no new symbol signoff claimed. Whole-app final gate remains open; FEAVL/ValidarABB held.


## Heap Limpiar LOW baseline; fidelity defect held for bounded semantic fix

4 contract tests pass5.41s;4 downloaded/generated strictC17 programs/5 clear calls/Doxygen0;75 native observations,4cases/5executions. API final empty/capacity20 correct; trace invents progressive deletion, retains capacity40 and omits free/NULL even for allocated empty heap. Evidencia: evidence/visible-heap-clear-native-baseline-low/README.md. Instruction/UI/replay NOT signed off. Heap2/5/global13/22/docs61/208 unchanged. Next bounded MEDIUM: clear destructor+reinitialize+private reserve lifetime/scopes, preserving existing C algorithm. Insertar/Extraer require sift/comparison/swap and growth or root-output review after this clear correction; no implementation in this LOW baseline. FEAVL/ValidarABBheld.


## Heap Limpiar verified instruction checkpoint; MEDIUM boundary complete

393 native events/8 cases/10 executions;786 actual array+SVG forward/back rows,24 linked C17 programs,16 actual main+C/H Doxygen0,zero replay/reloadPOST/JSerrors. Final revision25passed+1guide harness failure recovered by exact targeted1pass (26distinct verified outcomes across runs, not a singlegreen aggregate). C/H algorithm unchanged; guide/destructor docs and transient lifetime invariant corrected. Evidencia: evidence/visible-heap-clear-instruction-review/README.md. Heap3/5 recorded operations; Insertar/Extraer remain. Documentation62/208 reviewed,146pending (destructor only newly signed, initializer/private helper not broadly signed). Global 13/22 unchanged; whole-app finalgate/FEAVL/ValidarABBheld. End boundedMEDIUM now; next routine workLOW.


## USER-ORDERED PAUSE — awaiting resume

No active owned tests/compilers; all current runs completed, none interrupted. Preview only6568/13536 stays5051. Saved:evidence/heap-mutation-low-paused-checkpoint/README.md and checkpoint.json. Clear joint13pass11.71s; mutation10pass9.55s plus recovered generated-main1pass15.24s;17actual C17 mains/Doxygen0;18nativecases747events/17API final comparisons. SimpleNULL/output/count-order and INT_MINprintf fixes saved, mutation instruction defects remain (helpers before publiccaller, prematurequantity/stalecapacity/swaps/scopes). Global 13/22,Heap3/5,docs62/208. New user approval for AVLrotations/FE and ABBINT_MIN/MAX validation preserved; APPROVED but not implemented. Resume only on user instruction; no new tests now.


## Heap Insertar consolidated LOW checkpoint

Resumed authorized work; preview5051 remains. Final18passed:9native+9Chromium;432events/864both-view forward-back rows;27strictC17programs,18actualmain+C/H Doxygen0;zero replay/reloadPOST/JSerrors. Actualproject D:\MisProyectos\Web_VisualEstruct. Evidencia: evidence/visible-heap-insert-instruction-review/README.md. Heap4/5 recorded operations; Extraer remains. Documentation63/208 reviewed,145pending; global13/22 unchanged, whole-app finalgate open. AVLFE/rotations and ABBextrema APPROVED, not implemented here. Historical pause/held notes superseded by current authorization, retained as history.


## Heap Extraer verified bounded semantic checkpoint

Final28passed; extraction530nativeevents/9cases/1060both-viewforwardbackrows,27strictC17programs(17UImains+1empty-generator+9callers),18generator/C/H Doxygen0;zero replay/reloadPOST/JSerrors. Evidencia: evidence/visible-heap-extract-instruction-review/README.md. Heap5/5 recordedoperations; docs64/208reviewed144pending;global13/22unchanged. Wholeappfinalgate open. ReturnLOWnow; AVLFE/rotations and ABBextrema approved,nextindependentblocks.


## Validar ABB approved semantic correction verified

Final41passed;474nativeevents/16trees/948both-viewreplayrows;16actualmains computed48validations,C17strict/Doxygen0,zero replay/reloadPOST/JSerrors;leafgenerator regression included. Evidencia: evidence/visible-abb-validate-instruction-review/README.md. PublicABB C/H bytes unchanged; helper signoff separate. ABB12/12recordedcases; global13/22/docs64/208 unchanged. AVLFE/rotations stillapproved/unimplemented. Wholeappfinalgateopen. ReturnLOWimmediately atboundedsemanticboundary.


## Approved AVL native FE repair checkpoint

188 passed;89 prefix cases/77 exact backend comparisons/20 direct rotations/1 guards-allocation contract plus existing six-query test. Evidence: evidence/visible-avl-fe-native-repair/README.md. Four rotations fixed in actual downloaded C/H; ABI preserved; no backend algorithm change. Native repair complete; AVL6/9 instruction coverage/global13/22/docs64/208 unchanged. Routine Doxygen81970 and actual-main58254 pending collection; returnLOW. Historical approval hold is superseded.


## LOW consolidation of approved native AVL repair

Actual-main Chromium4passed84.16s; actual downloaded C/H Doxygen0warnings, content review four rotation symbols/guide. Documentation ledger68/208 (140pending), AVL10/13 public-file symbol contracts reviewed; three caller/mutation symbols remain pending instructional/documentary signoff. Native188tests previously recorded, not added to browser counts as one suite. Initial documentation wrapper stalled in workspace-relative session-cache initialization before Doxygen; stopped only identified wrapper Python processes, recovered using byte-verified preview HTTP downloads. Preview 5051 remained intact. Global 13/22 and AVL6/9 instruction coverage unchanged.


## Validar AVL LOW baseline prepared

351nativehelperobservations/9cases,7public-seedtraces examined; missingrecursiveframes/localfe, nestedheightobservationpending. Isolatedunorderedbalancedfixture demonstratesheight-onlyshownC vsorder-and-heightbackend distinction; no behaviorchanged. Evidencia: evidence/visible-avl-validate-baseline-low/README.md. NextboundedMEDIUMscope:avl-validate-instruction-review-plan.md; thenInsertar/Eliminarseparately. Global 13/22,AVL6/9,docs68/208 unchanged.


## Validar AVL bounded instruction closure

30distincttests verified across24+18 runs with12overlappingnativechecks deduplicated;1321nativeevents/14cases/2642both-viewreplaystates/24actualCcaller-historyprogramsC17strictDoxygen0. Evidencia: evidence/visible-avl-validate-instruction-review/README.md. Purehelperheightbalance andbackendorder+heightbalance remainseparate; publicC/Hbytesunchanged. AVL7/9recordedoperations;Insertar/Eliminarpending. Global 13/22/docs68/208unchanged. Preview 5051launcher15948D:HTTP 200. ReturnLOWimmediately.


## Insertar AVL LOW baseline and documentation contract

714nativeevents15cases (supersedes694beforeternaryconditionextension),14originalC/instrumentedendpoint+independentinvariantcrosschecks,2actualmainregressions39.75s,C/H Doxygen0. Evidencia: evidence/visible-avl-insert-baseline-low/README.md. Docs69/208;avl_insertar contract signed independentlyofinstructionUI. Currenttraceslacknativeframes/rotationdefinitions/repeatedFEconditions; MEDIUMscopedinavl-insert-instruction-review-plan.md. AVL7/9/global13/22unchanged.


## Insertar AVL bounded instruction closure

26 passed in 263.07s; 714 native events/15 cases; 1354 Chromium forward/back states/11 successful visible cases; 33 caller/history C17 programs, Doxygen0. Evidence: evidence/visible-avl-insert-instruction-review/README.md. Public C/H bytes unchanged from LOW documentation signoff. Stable generated-main invocation output repaired without attributing status to void. AVL8/9 recorded operations; Eliminar pending. Global 13/22 and documentation69/208 unchanged; final whole-app gate remains open. Preview 5051 HTTP 200 launcher3676 D:. End MEDIUM now, return LOW.


## Eliminar AVL LOW preparation

19native cases/1890events and independent original-C/backend endpoint/invariants; four visible main-history cases/8 exact mains+8 observation variants, C17 strict and Doxygen0; stable invocation output repaired. Content-reviewed Eliminar/helper/manual contracts advance docs71/208 (137pending), AVL13/13 public-file entities. Evidencia: evidence/visible-avl-delete-baseline-low/README.md. Current traces lack native frames/called definitions; bounded MEDIUM planned in avl-delete-instruction-review-plan.md. AVL8/9/global13/22 unchanged; finalgate open.


## Eliminar AVL MEDIUM semantic checkpoint; browser final running

22 native/API tests passed:19cases/1913events (1890 baseline superseded by15 ternary selections and8 explicit lexical-scope exits), strict continuity and C/H bytes unchanged. Source/lifetime/return/recursive-height/rotation integration complete natively; final40-test aggregate in session80435 must be collected in LOW. Evidencia: evidence/visible-avl-delete-instruction-review/README.md and checkpoint.json. No AVL9/9 or global completion claim before final UI result; global13/22/docs71/208 remain. Preview 5051 launcher19416 D:.


## Eliminar AVL verified LOW consolidation

40 distinct checks verified (37 aggregate passes plus 6 corrected-contract passes, 3 overlap); 19 native cases/1913 events; 3744 successful browser states, 6 application rejection explanation states; 48 strict C17 programs/Doxygen0. Evidence: evidence/visible-avl-delete-instruction-review/README.md and verification.json. AVL9/9 recorded visible operations; no all-path claim. Global 13/22 and docs71/208 unchanged; remaining families/final gate open.


## Rojo-negro query/main LOW verification

7focused tests (6aggregate+1additional no-reexecution); four browser histories/12actual C17 mains, reload stable, Doxygen0. Inorden/Altura/Validar run canonical documented helpers, query history preserved without replay. Validar matches actual backend root-black/order/red-red checks; black-height/parent validation NOT provided. Public Buscar/VerArbol/Color comments-only content signoff advances74/208(134pending); four app helpers outside denominator. Evidencia: evidence/visible-red-black-query-main-low/README.md. Global 13/22, instruction coverage and finalgate remain open.

Rojo-negro affected shared regression20passed; old ABB mutating-only history expectation corrected to six exact operations including persisted Validar. Evidence:visible-red-black-query-main-low. No application ABB change. Total27focusedchecks, finalwholeappgate remains open.


## Rojo-negro bounded query instruction closure

37distinct checks:19normal native comparisons(460events),4test-only negative validator cases(90events),14browser scenarios(742forward/back states),23original callers/exactdownloaded C parity. Source/scopes/typedaliases/returns/printf/actualSVGedges/colors/pendingmessages and no replayPOST verified. Inorden/Altura/Validar/Buscar close4/7 recorded visibleoperations; Insertar/Eliminar/Limpiar remain. Validar contract remains root-black/order/red-red only. Evidencia: evidence/visible-red-black-query-instruction-review/README.md. Global 13/22/docs74/208 unchanged; finalgate open. EndboundedMEDIUM, returnLOW immediately.


## Limpiar Rojo-Negro LOW baseline and history fix

13distinct tests (5native lifecycle+4clear histories+4adjacent query histories),215nativeevents/15frees including5safe NULLrepetitions;12actual clear mains+12observervariants,12adjacent query mains C17/Doxygen0. Real repeated-history deduplication fixed in live/restored paths. Public rbt_liberar content signoff75/208(133pending), token guard/no C algorithm change. Evidencia: evidence/visible-red-black-clear-baseline-low/README.md. Instruction UI remains pending4/7, global13/22; next bounded review:red-black-clear-instruction-review-plan.md.


## Limpiar Rojo-Negro verified bounded instruction checkpoint

12 distinct checks:11 native +1 browser covering10 executions;215 native events/15 frees,235 steps/470 forward-back states,20 exact actual/equivalent C17 programs/Doxygen0 and20 separately counted observer variants. C/H hashes unchanged; scoped parameters, historical unusable references, actual NULL leaves and separate caller NULL assignment verified. Evidencia: evidence/visible-red-black-clear-instruction-review/README.md. RBT5/7 recorded visibleoperations; Insertar/Eliminar remain. Global 13/22/docs75/208 unchanged, final whole-app gate open. MEDIUM ends at this boundary; resumeLOW.


## Insertar Rojo-Negro LOW baseline/documentation checkpoint

29 distinct checks pass (25native/documentary4.22s +4actual-main111.99s),24cases/1460native observations,8exact downloaded-history programs and8ownership variants, C/H andmainDoxygen0. Ten symbol comments/manual content signoff advances85/208 (123pending); executable C/H tokens unchanged. Source includes all10helpers but full typed scopes/heap snapshots and instruction UI remain pending. C-MAIN-RBT-OWNERSHIP-01 open: actual mains keep finalfree commented,3/3/3/8live reserves at exit. Evidencia: evidence/visible-red-black-insert-baseline-low/README.md; bounded next:red-black-insert-instruction-review-plan.md. RBT5/7/global13/22/finalgate unchanged; Validar limit remains separate.


### Insertar LOW final observer supersession

Fresh safe baseline1460events/24cases;25native/documentary tests pass3.77s. Inactive seed borrowed returns no longer inspect a registry from previously freed cases; cached artifacts now guard C/H and observer SHA. Older successful native sample is superseded, not added to counts. Browser4tests111.99s independently unchanged. Evidence:visible-red-black-insert-baseline-low/rbt-insert-baseline-final-low. Docs85/208/global13/22/RBT5/7 remain; boundedMEDIUMplan ready, ownership/validator/finalgate open. Preview13812 HTTP 200.


## Approved Rojo-negro insertion contract follow-up (LOW)

C-RBT-INSERT-INT-RANGE-01 and C-MAIN-RBT-OWNERSHIP-01 are addressed within the existing fidelity/documentation/regression tasks; no new checkbox or denominator is added. Require signed-int bounds/rejection without mutation, actual main final caller cleanup with NULL, HTTP C/H compilation/Doxygen, independent live allocation count, repeated-history/reload preservation and adjacent query/cleanup regression before RBT Insertar signoff. Native MEDIUM browser24/24 passed456.32s; the current LOW revision's affected regression is running. Global 13/22/docs85/208 and whole-app final gate remain open.


## Insertar Rojo-Negro verified LOW closure

Recorded-case Insertar closure advances RBT6/7; Eliminar remains. Current affected74checks pass:57native/contracts68.25s,1actual C/H/helper/manual/Doxygen3.96s,16browser cases (11initial passes plus5focused corrections161.08s; retained first-run5expected fixture/count failures).36actual C17 mains/Doxygen0 plus24separate ownership variants:77allocations=77frees,0live.18exact operation callers verified independently. Full prior24case Chromium pass3634forward/back states/1817steps456.32s, with18real successes/6explicit native fixtures; current affected replay cases8/20 pass294states. C/H bytes unchanged, signedint insertion rejection and final caller main cleanup verified. C-RBT-INSERT-INT-RANGE-01 and C-MAIN-RBT-OWNERSHIP-01 closed for this recorded scope. Evidencia: evidence/visible-red-black-insert-final-low/README.md and final-summary.json. Preview D:5051 launcher15372 HTTP 200, cache retained. Global 13/22/docs85/208 remain; no all-path claim, validator/sanitizer/WebKit/whole-app final limits persist. No test remains active, no push/merge/deploy.


## Eliminar Rojo-Negro LOW baseline/documentation checkpoint

94distinct checks pass:90native/documentary3.47s +4actual-history112.05s;83cases/4898actualC observations,71original-z frees,0deletion allocations/printf. Original bodies and strong independent endpoint invariants agree with backend; final invariants do not prove instruction UI.8actual C17 mains/Doxygen0 +8ownership variants:30allocations=30frees,0live; repeat rejection/reload preserve history/output without extraPOST. Failure-only app trace corrected: no rbt_eliminar invocation fabricated. Five C/H contracts reviewed, ledger90/208(118pending), all19RBT declaration SHA/lines refreshed and stale markdown tables reconciled with JSON. C/H algorithm tokens unchanged; old cache hashes must regenerate, not bypass guards.

OPEN C-RBT-DELETE-TRACE-01: sourcewindow onlyrbt_eliminar, lacks6actual helper definitions; root withtwochildren36nativeevents vs16genericsteps, onlytopframe/noheap model. Next boundedMEDIUM:red-black-delete-instruction-review-plan.md for typedchar/pointer scopes, transplant/successor/originalfree, fix-up and bothviews/replay. C-RBT-VALIDAR-LIMIT-01 remains OPEN in red-black-validation-limit-decision.md evenafter7/7; product Validar doesnot certify blackheight/parents/cycles. Evidencia: evidence/visible-red-black-delete-baseline-low/README.md; reviewed-revision.json baseHEADba53ba7c0bcebaf7a4938328ebf4c863f19eadab plusuncommitted SHA-guarded changes. RBT6/7/global13/22/finalgate remain. Preview D:5051 launcher15156HTTP 200/cachepreserved. No active app tests; no AGENTSroot/newcontinuity edits or push/merge/deploy.


## Eliminar Rojo-Negro MEDIUM semantic checkpoint; LOW consolidation pending

119distinct testIDs verified across overlapping runs:83native cases+2app-rejection+17exact C17caller/Doxygen0+17Chromium scenarios.6585typed/lifetime/operand/ternary observations supersede4898baseline;71original-z frees,0allocation/printf.2514distinctboth-viewforward/backstates,0replayPOST/JSerrors. Finalaffected87passed127.14s (85native+UI70/73); prior32passed379.56s and focused5passed114.12s overlap, not added. All64fullcondition/25operand/15ternary OBSERVED outcomes represented in17selectedcases. C/H bytesunchanged. Sourcewindow/helpers/scopes/char/native successor/free/fixup andscope-exitvariable rows verified. Evidencia: evidence/visible-red-black-delete-instruction-review/{README.md,checkpoint.json}. RBT7/7 recorded semantic methods; no all-path/globalclosure. C-RBT-VALIDAR-LIMIT-01 stays OPEN. Global 13/22/docs90/208(118pending) unchanged. LOW consolidates expectedclosuremarker/affectedadjacent checks before moving worklist; wholeappfinalgate remains. EndMEDIUM immediately, returnLOW; no push/merge/deploy.


## Eliminar Rojo-Negro verified LOW closure

Recorded closure after semantic evidence119distinct testIDs and necessary adjacent3passed107.46s (not summed as new global counts). RBT7/7 recorded methods;83nativecases/6585events,17UIscenarios/2514states,17exactcallers remain the bounded semantic scope. CurrentLOW checks shared Insertar rotation/replay270states and2actual Eliminar/rejection/reload histories:4strictC17/Doxygen0 programs+4separateownershipvariants,20alloc=20free,0live. Evidencia: evidence/visible-red-black-delete-low-closure/{README.md,summary.json}. C-RBT-DELETE-TRACE-01 closed for thesecases; C/H andapplicationbytes unchanged inLOW. Global 13/22/docs90/208(118pending) unchanged; wholeappfinalgate open. C-RBT-VALIDAR-LIMIT-01 OPEN: concrete V1/V2/V3proposal in red-black-validation-extension-proposal.md, no implementation;2currentbackend/Ccounterexamples observed independently. Hash contract H1/H2/H3 still awaits user decision; hash-baseline-decision-gate-low.md records read-only sources, no new normative baseline chosen. Preserve5051; no push/merge/deploy.


## BFS MEDIUM semantic checkpoint; LOW consolidation pending

BFSonly:13focusedtests pass25.43s;10helpertests pass19.84s;2400realC observations/10cases/11runs INCLUDE720outerevents (not added). Actualhelpers, mark-on-enqueue, symbolicallocation/free/partialpublication/scopes and successful-query history/caller corrected; C/H bytes unchanged. Current8case Chromium run session99991 remains active; cases1,3 already152/730rows and strictC17 actualmain verified. Collect durable bfs-browser-final1.log before rerun; no BFS/allgraph/globalclosure yet. Evidencia: evidence/visible-graph-bfs-instruction-review/{README.md,checkpoint.json}. EndboundedMEDIUM now; LOW collects browser run, final affected regressions/docsignoff and currentpreview verification. Global 13/22/docs90/208 unchanged; other5graphalgorithms,Hashdecision,RNValidar andfinalgate remain open.


## BFS verified LOW closure for recorded cases

BFS1/6graph algorithms recorded:10nativecases/11runs/2400events INCLUDE720outer;8Chromiumcases/4524states,0replayPOST/JSerrors.99991collected8pass201.19s. Current73uniquechecks via72pass plus21targeted41.51s(overlap20,one repaired test variable); final2browser1,7 pass42.32s/782states overlap8.8actualC17/Doxygen0 mains+8ownershipvariants181alloc=181free,0live. HTTP4C/H/Doxygen0,7contracts signed, executabletokens unchanged. Docs97/208,111pending; global13/22 unchanged. D:5051 launcher14428/HTTP 200 newmodel/canonicalframes/rejection/-1/history verified inisolatedsession. Evidencia: evidence/visible-graph-bfs-low-closure/{README.md,summary.json}. Finite normalalloc,max4vertexnative scope only; largerperformance/nativetypedlocals/sanitizers/WebKit/globalfinal remain. DFS,Dijkstra,Bellman-Ford,Prim,Kruskal,Hashdecision,RNValidar open. DFS will be registerednext without algorithmexecution.


## DFS LOW contract checkpoint — instruction review OPEN

Evidencia: evidence/visible-graph-dfs-contract-low. 10nativecases/11runs finalorder match; corrected9graph/outputmark discrepancies and9lostsuccess histories, after0. 10focusedtests pass53.44s includes3actualChromium callers plus5sharedpedagogychecks. Three actualmains strictC17 compute2DFSresults after2reloads/failureomitted;4doc/ownershiptests pass5.65s,4HTTPfiles/Doxygen0,46alloc=46free/0live. C/H algorithms unchanged. Three sourcecontracts reviewed; docs100/208,108pending; global13/22 unchanged. Preview 5051 ownlauncher17900HTTP 200 currentmarks/history verified. DFS perinstruction/helperframes/aliases/heap/bothrepresentations/replay OPEN; next boundedcase in graph-dfs-instruction-review-plan.md. No closedfamily or allpaths claim; Hash/RNValidar pending.


## DFS bounded instruction checkpoint — context remains OPEN

Evidencia: evidence/visible-graph-dfs-instruction-review.10nativefixtures/11runs/1978events/8functions/max5frames; actualtypedpointercache/initializedheap/conditions/returns/aliases/head/frames conformance.8uniqueChromiumcases/3698states,0replayPOST/JSerrors,8actualC17mains; valuesTEXTstrongchecks cases1,7/632states.7pass184.06s plus final12pass53.63s(10native+2browser,case7overlap). Ownpreview5051launcher13908HTTP 200 DFSmodel/guard/canonicalframes verified. Global 13/22/docs100/208 unchanged.

NEW C-DFS-HISTORY-MARKS-01 OPEN: publictopologyrebuild skipsoldqueries and losespriorquerymarks; secondentry0 vsrawsamegraphC1 despiteequalorder. No fullcrosscallDFSclosure or closedBFSreopen. See graph-dfs-history-marks-context-decision.md; suggestseparatevalidatedeffectsnapshotrestoration withoutqueryredispatch, scopecoordinationneeded. ReturnLOW atsemanticcheckpoint; callers/docsfinal/sharedregression/contextdecision stillpending.


## DFS verified LOW closure for recorded cases

DFS2/6 graph algorithms recorded (BFS and DFS). Finite DFS scope:10 native cases/11runs/1978events/8actualfunctions/max5frames and8Chromium cases/3698forward/back states. All8 now assert previous/current variable values as text; earlier limited-case632state assertion statement is superseded. Head storage, symbolic heap/initialized fields, live aliases, recursive scopes/returns, highlights, conditions and console verified; no replay POST/page errors. Native current-repeat fixture uses actual captured service history.

Cross-call marks C-DFS-HISTORY-MARKS-01 corrected via validated chronological effect snapshots, no historical query dispatch. Additional native history matrix10sequences/31operations/62before-after mark observations matches repeatedDFS,BFS-to-DFS,mutation,clear,failure cases.15invalid effects, stale copies, foreign sessions and malformed histories tested. Existing vertex marks survive native mutations; new vertices start0. Legacy histories without valid captured effects cannot recover old marks and are deliberately not redispatched; no retrospective all-history claim.

Backend aggregate81passed113.92s. Full8instruction-browser cases passed before last fast-to-step correction. New context regression first exposed discarded fast-mode player trace; graph.js now retains the actual execution. Final focused affected suite13passed77.22s: one sharedBFS context, twoDFS replay cases1/7(632states overlap8),10documentation/ownership checks. Earlier focusedDFS context1passed19.70s:3actualcalls,0replay/reloadPOST,mutation input,actual downloaded4files/mainC17 and computed output. Nine unique actual DFS browser mains (8instruction+context), Doxygen0, strictC17 and9independent ownership variants144alloc=144free/0live; symlink current artifacts excluded from counts. Fresh4HTTP C/H Doxygen0, guides describe finite scope and historical-effect limits. C/H executable code unchanged. Docs100/208 reviewed/108pending, global13/22 unchanged.

D:preview5051 launcher332 verifiedHTTP 200/currentmodel/currentJS/signedmarkeffect/secondinput[1,1] in isolated session; original user cache retained. Evidencia: evidence/visible-graph-dfs-history-context-low. No active tests, push, merge or deployment. Normalalloc/max4nativevertices; malloc-failure paths, largegraphs/performance, sanitizers/WebKit, other4algorithms and whole-app final gate remain open. Dijkstra only scope preparation next; do not treat this closure as authorization for semantic execution.


## Dijkstra LOW baseline: execution authorized, instruction review OPEN

16independent native endpoint cases compile strictC17;13agree and3disagree:equal-priority order (C1-3-4/API1-2-4),INT_MAXtreatedas infinity inC but reachable inAPI, overflow sum2147483648discardedbyCbutacceptedAPI. Bothnegative-weightcases correctlyreject, includingdisconnectednegativearc; historicalGRAPH-004negativeguard claim is not a current proven defect. Newstrongregression18IDs:13pass/5fail8.50s (3parity+2successfulhistory). No xfail/suppression/assertionweakening.

3actualbrowser cases,6realqueries: repeatedidenticalcalls become1localmaincall and0after2reloads,0extraPOST/pageerrors. All3originalstudentmainsfailstrictC17unusedcamino;2nonemptyresultcallersleak2nodes each. Observationalvariants only:38alloc/34free/4live; originalcompilefail preserved, not counted as passing actualmains. They print precomputedUItext ratherthancomputedpath. Caller/history fixes pending.

1freshHTTP4C/H/doc/helpertestpasses1.62s,Doxygen0,actualprivatehelperbodies strictC17.5individualsourcecontracts reviewed; docs105/208,103pending;all71graphdeclarationmetadata refreshed. C/H executabletokensunchanged; integer infinity/tie/globalnegative/ownership notes andguide limits accurate. Genericinitialtrace presents double dist[1]=0beforeCarrayinit,auxiliarypriority_queue despiteactualminscan;Actualhelperframes/typedarrays/nativeinstructionconformance not verified. Evidencia: evidence/visible-graph-dijkstra-baseline-low. Global 13/22 andBFS/DFSclosures unchanged. Next boundedMEDIUMscope proposed in graph-dijkstra-instruction-review-plan.md; don't implement numeric/decimal policy redesign silently. No active tests/push/merge/deploy.


## Dijkstra: historial y caller verificados; semántica numérica abierta

Corrección LOW autorizada de C-DIJKSTRA-HISTORY-04 y C-DIJKSTRA-CALLER-05 para los casos registrados. Cada consulta exitosa se conserva, incluso repetida; los fallos no se agregan. La reconstrucción valida la consulta en su posición histórica sin ejecutarla. No se agregan efectos de marcas a Dijkstra. Una regresión compartida acotada confirma que las marcas DFS sobreviven las consultas de camino; no se repitieron oráculos BFS/DFS cerrados.

Backend:25 aprobadas/3 fallidas en 14.86 s. Las dos regresiones de historial antes fallidas ahora pasan; se mantienen sin xfail los tres fallos numéricos de empate/INT_MAX/suma. Nueve pruebas nuevas cubren repeticiones, fallos, recarga sin dispatch, mutación negativa posterior y marcas compartidas. Navegador:3 aprobadas en 39.12 s,6 consultas exitosas y3 rechazadas;2 llamadas por programa sobreviven recargas, ninguna petición adicional al reproducir/recargar, ningún error JS. Tres programas originales compilan C17 estricto, imprimen caminos/costos calculados por C y pasan Doxygen; tres variantes independientes de ownership verifican61 reservas = 61 liberaciones / 0 pendientes. NULL se explica como sin arcos/sin ruta/error, sin inventar un resultado calculado.

Comprobación final del manual/C/H:1 aprobada en 1.88 s, mismo ID documental incluido en backend, no un caso adicional. API observada con 11 entradas: rechaza 2.5 y"2.5"; acepta algunos pesos fuera del rango C;Infinity provoca HTTP 500. La afirmación anterior del manual sobre aceptación decimal fue corregida; la spec canónica conserva una contradicción pendiente. Dos sentencias reales del generador examinadas solamente en compilación/sintaxis:ninguna ejecución C insegura. 1e40 → int no representable es UB si se ejecuta; INT_MAX y la suma descartada por guarda del baseline son casos definidos. Ver graph-dijkstra-numeric-contract-decision.md:alternativas mínimas y recomendación C entero fiel, pendiente de decisión.

Hashes prueban que adapter, wrapper, dominio numérico y C/H permanecen idénticos al baseline; sólo historial/caller/manual/pruebas cambiaron. Evidencia: evidence/visible-graph-dijkstra-history-caller-low. Preview 5051 desdeD:,launcher 2812,HTTP 200,2 consultas conservadas tras 2 GET y JS nuevo verificados en sesión aislada; caché del usuario conservada. Global 13/22; documentación 105/208,103 pendientes. Dijkstra sigue abierto por fidelidad por instrucción y 3 regresiones numéricas. Sin pruebas activas/push/merge/despliegue.


## Graph: aceptación QA finita y consolidación documental LOW (2026-10-04)

[Addendum vigente](graph-qa-documentary-consolidation-addendum-low.md) corrige métricas del autor a tiempo transcurrido y precisión poolshared/records congelados; integra30148mutacionesChromiumQA, sin borrar bloqueo standalone histórico. QA real46IDs/seisfixturescríticos/before-verify-after0 acepta los tresajustes en casosregistrados. [Criterios poralgoritmo](graph-finite-acceptance-criteria-low.md) conserva BFS/DFS previos y acepta criterios finitos Bellman-Ford/Dijkstra/Prim/Kruskal; no6métodos→casilla global. Todas22casillas preservadas:13marcadas/9abiertas porcriterios agregados, ledger121/208histórico y87pendientes sin cambios;38GraphSHAstale y helperprivadonuevo no inventariado. [Preparación documental](documentary-stable-sources-after-graph-qa-plan-low.md) reutiliza67readreviewsSDD/hashesnongraphactuales. Sólo dosguías modificadas, runtime/C/H/preview/evidencia original y QAintactos; no reruns. Siguiente lote documental con bindingvigente y cualquier excepción C/H específica antes deeditar, sin ampliaralgoritmos.


## Delta documental de fuentes 2026-10-04

Ver `documentary-source-reconciliation-checkpoint-low.md`: Graph38 reconciliados + helper privado; 67 lecturas ordenadas; RN19 requieren recuperar binding. Cero signoffs/casillas nuevos; 13/22 preservado. Producto/C/H congelados.


## Recuperación documental de vínculos 2026-10-04

Ver `documentary-binding-recovery-checkpoint-low.md`: RN19 vinculado a QA/handoff vigente; Graph18 fuentes históricas recuperadas (15 cuerpos iguales/3 sustituidos); Desapilar hash entre informes históricos ligado, bytes íntegros aún no recuperados; rama Heap remove existe pero no en CHECKS estándar. 13/22, cero signoffs automáticos.


## Hitos documentales C/H autorizados 2026-10-04

Ver `documentary-comments-families-checkpoint-low.md` y ledger materializado vigente enlazado desde documentation-symbol-signoff-ledger.md: 67 contratos/117comentarios C/H revisados; 211 símbolos/386declaraciones reales; 118endorsements históricos ligados, 26registros sin endorsement individual global. Sólo14C/H modificados, tokens/preprocesado/13objetos idénticos, 26HTTP exactos y Doxygen0warnings. RN19/Graph15 vínculos preservados; Desapilar bytes nativos históricos aún no recuperados; Heap reporte específico no localizado. 13/22 sin casillas nuevas, sin suites históricas repetidas/preview/Git.


## Parcial26 documental y evidencia focal 2026-10-04

Ver `documentary26-partial-checkpoint-low.md`:25suficientes/1formalRN pendiente; DesapilarbytesSHA exactos recuperados y tokens iguales a D; Heap20nativos pasan, todos0vivos,13harnesses sólo enlazados. No casilla amplia nueva ni repetición por consulta.


## Contratos26 y evidencia focal completos 2026-10-04

Ver [checkpoint propio](documentary26-stack-heap-evidence-checkpoint-low.md):26contratos documentales aceptados, fuente histórica Desapilar recuperada SHA exacto y ligada al código actual;20regresiones nativas Heap nuevas pasan/cleanup0, sin repetirlas por consulta.26descargas reales/13harness enlazados sin ejecutar/Doxygen colectivo y autónomo0; código ejecutable intacto en las3fuentes de comentarios cambiadas. Catálogo211funciones/386declaraciones; evidencia histórica preservada. Nueve criterios amplios revisados y abiertos por sus residuales explícitos;13/22sin cambios, sin cierre funcional universal ni reapertura de familias.


## Miembros nofunción y criterio13 aceptado 2026-10-04

[Checkpoint vigente](documentary-nonfunction-global-criteria-checkpoint-low.md) y [decisión criterio13](documentary-c-h-criterion13-acceptance-decision-low.md).34declaraciones iniciales/tipos/campos/enums y fuente completa revisados; sólo8C/Hcomentarios, tokens/preprocesado/5objetosidénticos, HTTP/compilación/Doxygen reales y bindings actuales. Se marca exclusivamente fila13 de descargasC/H/compilación/Doxygen/exactitud;14/22derivado, ocho criterios abiertos con pendientes/condiciones precisos. No suites/algoritmosnuevos, no repetir26/67/Heap20/Desapilar. Bloqueos antiguos H1/Graph/RN/Sorting y faltantesdocumentales quedan sustituidos por fuentes vigentes, no por esta fotografía histórica. Preview/Git/owners intactos.

## Aceptación finita de reparación focal20261004

Registrosfinitoaceptados RAW-HEAP-FOCAL-REPAIR-20261004,LINKED-HIDDEN-POSITIONAL-CALLERS-20261004 yGRAPH-NEIGHBORS-FOCAL-INSTRUCTIONS-20261004 en canonical-focal-finite-acceptance-decision-low.md. Casosfuentes/logs antes/después/ownership ylímites allí enlazados.15rawheap+fallológico,12callerfixtures,6nativequeryy2DOMsolapados;no suma artificial ni cierrefamilias/global. Las casillas11/12/14/16/18/19 siguenabiertas;22/17 aceptadas antes se conservan. Matrix517filas actualiza7afectadas yrootinternobuilderretain. C1/session-stateadopción externa aceptada,sin nuevaadmisiónC1. Previewsinreactivación aquí.


## Activación preview y consolidación finita20261004

Preview5051 reiniciado una vez con entorno/sesiones conservados; tres smoke focales pasan, sin repetir suitesaceptadas. Criterio14aceptado por contrasteactual;17/22derivado, abiertos11/12/16/18/19. Inventario exhaustivo de dimensiones aplicables con vínculos faltantes y comprobaciones realmente ausentes distinguidos, en evidence/visible-preview-focal-criteria-consolidation-low/exhaustive-applicable-unresolved-cells.json. Fuentes/C-H estables; QAglobal preparado, no ejecutado en este bloque.


## Seguimiento propio 2026-10-04 Graph/controles LOW

Checkpoint parcial: [unresolved-graph-controls-partial-checkpoint-low.md](unresolved-graph-controls-partial-checkpoint-low.md). Diez regresiones Graph rojas; reparacion MEDIUM propuesta, sin modificar producto. Controles verificados por capas y contextos; exportacion global Sorting vacio tiene observacion de contenido pendiente. Navegacion con traza/Counting e integracion16 pendientes. Sin nuevas casillas cerradas:17/22.


## Seguimiento propio Graph10 MEDIUM 2026-10-04

[graph10-repair-verification-medium.md](graph10-repair-verification-medium.md): diez regresiones reparadas,23tests permanentes,24fixtures C17 con dos capas no48casos,166boundariesDOM seleccionados; navegacion/Countingpaginas verificadas sin redispatch y caption/aria restaurados. C/H/Graph6/cuatro callers previos intactos. Defecto nuevo acotado exportacionglobalSortingvacio confirmado; reparacion exporter/revisionintegracion16/QA18/entrega19 pendientes. Sin nuevas casillas globales:17/22. Preview intacto; validacion privada D.

Revision final Graph10:24IDs distintos en union23+1, sin repetir suites por consulta. Frame/funcion activa verificados focalmente; fuentes finales summary/protected-product-after/diffs.17/22sin cambio.


## JPEG y trazas HTTP ocultas Lista: evidencia focal, criterios globales abiertos

Asignacion coordination-jpeg-hidden-list-traces-low-20261004. Reparacion minima JPEG y modelo exclusivo3alias sin modificar C/H/contratos/callers anteriores.16IDs unicos aprobados (15Lista+1JPEG),11fixturesC17/237observaciones,3contextosDOM/256limites/ceroPOSTreplay. Scope y limites en jpeg-hidden-list-traces-checkpoint-low.md y evidence/visible-jpeg-hidden-list-traces-low/summary.json. Matriz propia aggregate-correspondence-current.json preserva historia;16deltas propios exactos registrados sin cerrar16. Preview17716/19612 activo; sesiones originales preservadas por hashes; correccion de aislamiento fixture documentada.11/12/16/18/19 permanecen abiertos; ninguna casilla global modificada. Siguiente consolidacionLOW/QAindependiente en consolidation-and-independent-QA-list.json.


## Consolidación LOW11/12/16 y preparación independiente18

36.383 referencias verificadas; matriz517filas y registro16unificado24registros. No cierre global nuevo:17/22. Ver criteria-consolidation-global-QA-checkpoint-low.md; binding review-global-application-quality para reviewer01a0ff54-79d7-7520-8e9f-224ef5ed700f. Cero suites/producto modificados en preparación.


## Tres reparaciones revisadas adoptadas LOW

Ultimo/Sublista/manualRN adoptados exactamente;11focales canónicos passed3.44s, nuevo QA14pending. UIretirado/C/Hintactos. Ver three-reviewed-repairs-canonical-checkpoint-low.md. Global17/22sin nuevos cierres;1938previos y2604pendientes noaprobados conservados.


## QA14 aceptada y residual oculto exacto LOW

Aceptados14IDs/18consumidores independientes;12fixturesC17nuevos diagnostican4trazas ocultasdefectuosas. No funcionalesnuevos ni cierresglobales;17/22. Ver four-hidden-residual-and-final-disposition-checkpoint-low.md y QA18-obligation-disposition-current.json;2604pendientes noaprobados.


## Cuatro trazas ocultas reparadas LOW

13IDs finales passed21.44s/4contextosDOM172boundaries;12oráculosnativeprevios.C/H/UI/APIintactos.NuevoQAfinalbindingreview-four-hidden-terminal-and-final-qualitypending;ver four-hidden-terminal-repair-checkpoint-low.md.Sin cierre global/2604aprobacionesporomisión.

- [x] pq-shared-runtime-defects: minimal proven runtime repairs and independent batch QA.

- [x] graph-observed-invariant-repair2: explicit false flag repair and finite QA binding.

- [x] graph-codec-e2e-diagnostics: proven shared reference boundary and diagnostics finite QA.

- [x] e2e-safe-diagnostics-repair: diagnostic-only safe failure metadata and independent review.

- [x] publish-reviewed-pq-graph-safe-e2e: reviewed15files joint publication and exactCI diagnosis.

- [x] e2e-diagnostic-directory-anchor: publishedCI diagnosed path mismatch, unpublished focal repair andQA.

- [x] sequential-final-logical-projection:3exactEcb runtime final projections and independentQA.

- [ ] publish-reviewed-seq-e2e-delivery: accepted8files publication and actualCI/metadata.

## Focal E2E manual cost and remaining87 LOW

- [x] e2e-manual-cost-and-remaining87: focal contract/cost decision and current common-cause classification; own plan e2e-manual-cost-and-remaining87-low.md.

## PQ formatter and Sorting policy inventory LOW

- [x] pq-format-sorting-policy-inventory: isolated formatter test and inventory only.

## Direct range rejection oracle LOW

- [x] sorting-direct-range-error-oracle: currenttext and noauxiliaryallocation.

## Three accepted test-oracle lots publication LOW

- [x] publish-reviewed-three-test-oracle-lots: exact3files andterminalCI, no globalclosure.

## User approved Sorting source A LOW

- [x] sorting-source-A-approved: controlled earlyrejection andrealCconsumers, ownQA andindependentreview.

- [x] sorting-source-A-preprocessor-repair: approved focal preprocessing admission repair.

- [x] publish-sorting-source-A-accepted: exact accepted source and tests publication / CI.

- [x] sorting-four-later-oracles: causal current-C oracle review and small tests.

- [x] sorting-radix-source-consumer: exact CI missing-C caller adjustment.

- [x] publish-sorting-followup-oracles: normal main accepted3testfiles, terminalCI/differential.

- [x] sorting-boundary-radix-fidelity: scoped initial metadata and inactive Radix group repair.

- [ ] publish-sorting-boundary-radix-accepted: Publish independently accepted focal lot, exact CI comparison and evidence-only next cause.

- [x] hierarchical-frame-invariant-diagnosis: source/log contract diagnosis only, preserve prepared publication lot.

- [x] hierarchical-frame-oracle-repair: independent causal/final oracle for eleven diagnosed cases.

- [x] stack-push-legacy-memory-consumers: pending memory consumers only; preserve closed native engine.

- [ ] linked-list-console-consumers: console consumers only; closed list engines preserved.

- [ ] priority-dequeue-memory-consumer: focal legacy consumer and QA handoff; own plan.

- [ ] priority-front-candidate-delta: focal candidate projection repair and QA pending; own plan.

- [ ] circular-insert-consumer: focal insertion consumer; own plan, no formal closure.

- [ ] linked-head-insert-consumer: focal consumer with accepted console sections frozen; QA pending.

- [ ] circular-delete-consumer: first-match root/link/free consumer, own plan; no formal closure.

- [ ] circular-clear-consumer: existing3node destructor consumer, own plan; QA pending.

- [ ] stack-canonical-golden-consumers: two original consumers, no formal closure, own plan.

- [ ] tree-intermediate-consumers: ABB successor and AVL LR/RL consumer cases only; own plan, QA pending.

- [ ] rbt-legacy-consumers: three original RN consumers, focal C contract evidence and independent QA handoff.

- [ ] sorting-mapping-consumers: three original source-mapping consumers and independent QA handoff.

- [ ] quicksort-comparison-consumers: two original QuickSort consumers and independent QA handoff.

- [ ] bubble-canonical-consumers: three original Bubble consumers and independent QA handoff.

- [ ] sorting-catalog-consumer: original catalog consumer and independent QA handoff.

- [ ] dijkstra-legacy-consumers: two original Dijkstra consumers and independent QA handoff.

- [ ] hash-two-consumers: two original Hash consumers, focal evidence, pending independent QA.

- [ ] bellman-http-consumers: two original HTTP consumers; pending independent QA.

- [ ] graph-avl-golden-consumers: two original golden IDs; pending independent QA.

- [ ] rn-console-consumer: one original console ID; pending independent QA.

- [ ] graph-delete-kruskal-consumers: two original parameter IDs; pending independent QA.

- [ ] graph-bellman-traversal-consumers: two instructed original Graph IDs; pending independent QA.

- [ ] hash-visible-method-consumer: original all-visible Hash consumer only; pending independent QA.

- [ ] phase8-duplicates-consumer: original duplicates consumer only, pending independent QA.

- [ ] linked-list-canonical-consumer: original linked_list parameter only; independent QA pending.

- [ ] phase8-limits-diagnosis: diagnosis only; original ID pending, see phase8-limits-diagnosis-low.md.

- [ ] phase8-size-provenance: read-only provenance, see phase8-size-provenance-low.md.

- [ ] phase8-limits-consumer: final consumer correction, see phase8-limits-consumer-low.md.
- [ ] author-evidence-four-bindings: author manifest completion only; independent QA pending; see evidence/visible-phase8-limits-consumer-low/four-bindings-completion-scope.md.

- [ ] author-integration-collection: bounded syntax/import/66IDs collection only; see evidence/visible-author-integration-collection-low/scope.md.

- [ ] pending39-bounded-regression: author only bounded regression; see evidence/visible-pending39-regression-low-20261009/scope.md.

- [ ] independent39-handoff-coverage-plan: author transfer and coverage planning only; see evidence/visible-independent39-handoff-coverage-plan-low-20261009/scope.md.

- [ ] bellman-coverage900-once: exactly one900s/2GiBapprovedinstrumentedtrial, noautomaticretry; see evidence/visible-bellman-coverage900-once-low-20261009/scope.md.

- [ ] rejected12-projection-repair-preparation: prepare rejected12 public projection repair; verification/independent reevaluation pending.

- [ ] rejected12-tests-remaining-coverage: authorized12 regressions/negatives and CI coverage blocks120s2GiB; independent reevaluation pending.

- [ ] remaining-coverage-smaller-blocks: continue4889unrecorded coverage IDs in smaller120s2GiB blocks; preserve474+Bellman, single-case limits explicitly blocked.

- [ ] github-vps-qualified-delivery: publish only curated audited changes and update existing VisualStruct VPS service with exact-version/CI/health verification, preserving data/config/reservations; user authorized20261012, no Factor6 or deniedSDD writing. GitHub main e79b8c0 published and exact remote verified; C17/sanitizers CI PASS, remaining CI pending; VPS blocked by unverified permitted access, public health HTTP200 only. Own evidence: visible-github-vps-qualified-delivery-low-20261012/delivery-result.json. CI continuation approved20261012: workflow-only 3a1b3fc; single run38320783829 terminal: unit/inventory PASS, coverage suite PASS; sorting coverage38.13<85 gateFAIL. No retries/VPS. Own final-result: visible-github-unit-coverage-split-once-low-20261012/final-result.json. Sorting six-file CI closure: cdf331a/run38324875785 once, unit1524PASS+inventoryPASS; coverage1521PASS, global85.41/Sorting95.92/allgatesPASS, within30min. No retries/localtests/VPS; evidence visible-github-sorting-six-files-once-low-20261012/final-result.json. E2E/reserve readonly closure review20261013: run38324875699 timeout20min,13PASS/1partial/15Chromium+5Firefoxunstarted; exact pending-case two-file draft prepared, requiresbudget/CI approval. Currentreserve reconciliation and3Graph functionalCI successors separatefrom120s historicaltimeouts. No tests/changes/VPS; evidence visible-e2e-reservations-closure-readonly-low-20261013/current-reservation-reconciliation.json. Authorized pending21E2E once: branch76170f5/run38333230154 terminal18PASS/1SortingFAIL/2Graphtimeouts; maincdf331a/unitcoverage intact.40/20limitsused,no retries;3case readonlyfollowupplan. Own evidence visible-e2e-pending21-once-low-20261013/final-result.json. Pending3 authorized preparation: two-file patch+AST/data/assertion/apply checks PASS, ready independentQA; base76170f5/maincdf331a intact, no publish/tests/CI beforeQA. Own request visible-e2e-pending3-prepare-QA-low-20261013/independent-QA-request.md. QAapproved pending3 closedfinite: b811db1/run38343382252 oneattempt3PASS, exactdata/manual/scopes;maincdf331a unchanged.3closurebindings registered,logs/artifacts/safe-derivedXML retained; no retries/unitcoverage/VPS/globalreservewaiver. Evidence visible-e2e-pending3-QA-approved-once-low-20261013/final-result.json. Mainintegration preparation:3filepatchbasecdf331a,fullE2E34=1+28+5/shards40/20/20,max2;tests+selector exactb811,static/applyPASS. QA pending/skip-ci userdecisionpending;no commit/push/CI/deliverydocedit. Evidence visible-main-E2E-integration-prepare-QA-low-20261013/independent-QA-request.md. Mainhelp404 e5032dc once QAconforme4files/skipci; authorized3dispatches terminal38350850391(E2E33PASS1FAIL),38350861737(unit1557PASS2FAIL;coverage1554PASS2FAIL85.40,gates/inventorynotexecuted),38350870538(C17/sanitizersPASS). Help35PASS/noXFAIL;28Chromium16m15,Graph35m45;7jobs84.7runner-min<155. TwoJPEGauthorizedattempts preparationERROR(sys.path thenbasetemp parent), nofunctionalJPEG/no thirdattempt. No retries/VPS/documentownerwrites. Currentevidence visible-help404-final-publish-JPEG-CI-once-low-20261013/CI-final-result.json. Userapproved3focalblocks isolatedDworktree e5032dc+exactQA3testpatches20261013: unit2PASS,AVL1PASS(counters1/17->2/17->0/17;6originalasserts),originalJPEG1PASS/3exports996x38/996x334/pixelsidentical/0exportPOST/JSerrors. Onceeach120s/2GiBverified,aggregate13.843s<360. Canonicaldirtytestfilespreserved,unpublished/nofullCIrepeat. HistoricalCIFAIL/JPEGERROR/SKIP unchanged; Counting/resource/performance reserves unchanged. Own successor evidence visible-three-approved-focal-blocks-once-low-20261013/final-result.json. UserapprovedQA3testedtestfiles published c395f5f70072d211fb0654af9b321294305e64b4 over e5032dc withskipciONLYthiscommit; exactdiff70164fdc719fe3c268077ab59e802bf5561b0ac70ce80f1a81274664f9f20518/3filehashesremoteverified. No newtests/dispatch/VPS/document; workflowsobserved0,newSHAnoCI/globalCInotPASS. Canonicaldirtytestfilespreserved. Own publication evidence visible-three-tested-oracles-publish-skipci-low-20261013/final-result.json.
