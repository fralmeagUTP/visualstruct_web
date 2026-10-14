# Secuenciales: aceptación finita y criterios C1

Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Operación residuals.sequential-acceptance-criteria, asignación coordination-sequential-acceptance-criteria-low-20261014. CatálogoC1 original1admitido/11pendientes intacto; ninguna admisión automática. La aceptación auditoría11/12/16 del acta20261005 conserva sus casos y no exige todos los caminos. Cierre de evidencia nominal finita es distinto de conformidad integral de familia y de aceptaciónC1.

## Impedimento concreto encontrado

SEQ-ALLOC-HTTP-001 (Alta): diez puntos de entrada/seisfamilias fallan el transporte de MemoryError. C17canónico: siete nuevos mallocNULL de listas conservan roots/heap/counters, cero objeto publicado; Stack/Queue/Priority reutilizan sus pruebasNULL privadas aceptadas. API con denegación determinista en constructor objetivo:500HTML, sinJSON/trace, sesión sinmutación. Fuente: app/services/structure_service.py:248-250. DosprocesosAPI exit1 preservados:2nominalesPASS+7faultFAIL, luego3faultFAIL; ni xfail ni supresión. Un hallazgo compartido, no10defectos independientes. Impide admitir equivalencia de errores REM01/REM02/REM07/QA03; no invalida escenarios nominales previamente aceptados. No se modifica producto en esta consolidación.

## Dos brechas condicionadas de sublista completadas

Criterio aplicable: audit-didactic-c-trace-fidelity/design.md, Diseño de casos exige unidad cuando aplica y causalidad/memoria de enlaces. Singleton inicial P7→H3 elimina hijo+padre y deja raízNULL; hijo interior distinto[3,4,5] elimina4 y reconecta3→5 antes de free. Ambos C/API/UI PASS. NuevoharnessC17 captura8snapshots post-store/free/final, no todas las condiciones/locales; ambas vistas51framesporvista/98restauraciones totales,0POSTextra/erroresJS. No se reejecutan los11casosSublista previos. La brecha concretasecircular selflink ya tiene evidencia: no se pide repetición.

## Por familia: alcance terminado y requisito que falta

|Familia|Alcance nominal finito|Impedimento de conformidad de errores|
|---|---|---|
|stack|Casos referidos completos; controles avanzan/retroceden sinredispatch|SEQ-ALLOC-HTTP-001, 1 punto(s)API|
|queue|Casos referidos completos; controles avanzan/retroceden sinredispatch|SEQ-ALLOC-HTTP-001, 1 punto(s)API|
|priority_queue|Casos referidos completos; controles avanzan/retroceden sinredispatch|SEQ-ALLOC-HTTP-001, 1 punto(s)API|
|linked_list|Casos referidos completos; controles avanzan/retroceden sinredispatch|SEQ-ALLOC-HTTP-001, 3 punto(s)API|
|circular_list|Casos referidos completos; controles avanzan/retroceden sinredispatch|SEQ-ALLOC-HTTP-001, 2 punto(s)API|
|sublist|Casos referidos completos; controles avanzan/retroceden sinredispatch|SEQ-ALLOC-HTTP-001, 2 punto(s)API|

Las familiasno quedan pendientes por falta de todoslos caminos. Para una declaración de todo el contrato falta además la disposición de9IDsseq delinventario y unión formal requisito→operación→fixture→oráculo→fuenteactual→historia/caller/UI. Más semillasnominales no resuelven esa disposición. Otros métodos ya aceptados se reutilizan por sus registros, no se repiten. APIs ocultas/privadas sinUI requieren N/A explícito sólo de UI, no borrado del contratoHTTP/C.

## Once obligaciones: prueba satisfecha frente a criterio faltante

|ID|Satisfecho finito|Falta para admisión más amplia|Límite documentable/N/A|
|---|---|---|---|
|C1-QA-01|PASS finite binding gate;375items/345bindings and controls explicitly unassigned|Missing disposition for9sequential controlIDs; dynamic inputs outside finite manifest not discovered, cannot claim exhaustiveness|Extra values/paths do not resolve a missing control disposition|
|C1-QA-02|PASS selected normal/empty/unit/positions; original accepted audit11/12 evidence reused|For all-option claim, bind each finite operation+required normal/boundary/invalid fixture to current source/evidence; no new global campaign implied|All possible inputs/path combinations NOT required;2sublist boundary gaps now covered|
|C1-QA-03|PASS selected C/API/frames/DOM forward-back; accepted scopes/history/callers retained|Failure path transport concretely FAIL; whole-contract claim needs history/fast/caller proofs linked, not more successful seeds|Old observer missing indirect stores limits specific event claims; not reason to reopen accepted nominal cases|
|C1-QA-04|PASS measured bounded resources and reproduced/reportable fault classification; focal Pilaresponsive evidence|Only defined accessibility/security/compatibility/report gates require disposition; these executions do not certify all QA classes|No mandatory all-browser/all-depth/OOM stress inference; do not require containers now|
|C1-REM-01|PASS successful operations within contracts; integer/fixed capacity decisions unchanged|MemoryError target execution fails the cross-layer error contract; failed constructor must not produce fictitious successful allocation frames|Do not revive H1/Graph decisions or require semantic redesign|
|C1-REM-02|PASS7new C17 mallocNULL paths and preserved state/counterownership;3accepted C/model NULL families reused|10API points FAIL error equivalence; Linux/LSan absent here is qualification, not fake defect or a new container requirement|No real OOM/arbitrary pointers/allalloc failure positions required for chosen corpus; RadixINT_MIN UBSan remains separate explicit scenario|
|C1-REM-03|NOT_APPLICABLE sequential acceptance|Graph direction/weights/duplicates/endpoints/forest scenario belongs to graph block;no sequential test closes it|Do not make graph a prerequisite for closing this nominal sequential scope|
|C1-REM-04|PASS selected domains/orders/ties/lifetimes; accepted query/C17 caller scopes reusable|Publish a finite binding of all declared methods/query snippets to actual C/header/outputs; hash combined obligation separate, not new H1permission|Hidden/no UI methods can be explicitly N/A for UI only, cannot erase their HTTP/Ccontract|
|C1-REM-05|PASS selected causal mutations/live-detached-freed identity and circular selflink;2newSublist witnesses|No successful reservation projection on failed allocation; for full frame claim, independent proof only for events actually captured or declared equivalent harness|No all execution paths demanded; *lista stores absent in older observer remain UNOBSERVED, never invented|
|C1-REM-07|PASS reached/no-output routes and rewind reconstruction; linked empty printf newline corrected|HTTP500 failure has no equivalent reached-printf/NULL console trace; errors must not become arbitrary technical stdout|Raw console chunks and DOM formatting distinguished; allprintf paths not certified by these two seeds|
|C1-REM-08|PASS finite before/failure evidence and strong regressions retained; old audit accepted criterion16 not reopened|New finding stays OPEN: no green correction/integration proof. Original29 case_ids need referenced finite adjudications, not count renaming|Cannot demand universal sanitizer runs to consolidate; original named sanitizer gates cannot be declared PASS without proof|

## Límites que no crean por sí solos nuevas campañas

No ausencia universal de UB/leaks/OOM, todos los inputs, todos los navegadores ni todas las combinaciones. C17/counters/witnesses no se renombran ASan/LSan. Sanitizers Pila aceptados se reutilizan; no containers nuevos. Las asignaciones *lista omitidas por observer histórico no cuentan como observadas; limitan esa afirmación y no autorizan reabrir casos aceptados. Sólo si se reclama cobertura independiente de ese frame se requiere su witness concreto/equivalente declarado. Sublista nuevoobserver sí acredita los stores registrados. Lecturas/tipos/scopes no capturados por nuevoharness no se inventan.

## Propuesta mínima de próximos bloques (no ejecutados)

1. SEQ-ALLOC-HTTP-001: contexto preciso de denegación de reserva en operación validada, traducción estructurada coherente con C; distinguir fallo durante replay de operación nueva y no fabricar eventos. Nada de faulttoggle público. Bloques120s/2GiB: (a) puenteError/política porfirmaC y10regresionesrojas; (b) framesNULL/no-object/printf alcanzado yUIdeunrepresentante porcomportamiento distinto, sólo tras cambio. Repetir únicamente fallos tras fix, no casos nominales aceptados ni oráculosC consumidos.
2. Disposición documental:9seqIDs+30globales, decisiones pedagógicas/sliders pendientes y unión a escenarios vigentes. No restaurar/retirar capacidades sin decisión; ningún test adicional necesario para decidir un contrato.
3. Familiasrestantes: primero recuperar/marcar criterio+evidencia aceptada; ejecutar sólo un escenario obligatorio ausente, no una batería nueva. Grafos: C1REM03 dirección/pesoinrepresentable y Prim/Kruskal desconectado como bosque, ≤8vértices/MAX15. Hash: REM04 índice enprocesosdistintos ycadena decolisión, clavesenteras/capacidadfija; no rehash/texto. Sorting: REM02 RadixINT_MIN conUBSan existente compatible y Counting/Bin amplitud mayor quelímite actualdocumentado sinreserva inválida; verificar decisiones posteriores, no imponer límite antiguo. Árboles/heap: QA03/REM05 yREM08 de susfixturesmutantes/fixup/sift yaaceptados, vincular fuenteactual/UI/caller; nocaso nuevo predeterminado antes de localizar eslabón faltante. Sanitizergate obligatorio sinprueba compatible queda faltante explícito, no se resuelve creando containers prohibidos.

## Evidencia y conservación

evidence/sequential-criteria-final.json matriz6familias×11criterios(disposiciones documentales, no66ejecuciones); evidence/sequential-allocation-finding.json; evidence/sequential-criteria-native contieneC17fuentes/stdout/stderr/compilación,2witnesses+7faultcontracts ybindingsSHA. Regresión tests/test_sequential_acceptance_criteria_focal.py:2API/2UIverdes y10APIrojas intencionalmenteconservadas porque criteriofalla, no xfail. Proceso nativo3.343s/30072832bytes; API2.484s y1.547s; UI24.985s/31.782s, todoslímites120s2GiB respetados,0timeouts.26C/3904sesiones originales conservanSHA, preview/containers intactos,0producto/publicación/commit/push. Informesanteriores se conservan comofotografías; dos brechasSublista ahora superadas enalcance descrito.

## Cierre del trabajo de consolidación
Sólo evaluación y pruebas autorizadas completadas; hallazgo permaneceOPEN yC1 noadmitido.
