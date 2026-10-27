# Reconciliación documental de fuentes — 2026-10-04

Asignación coordination-documentary-source-reconciliation-low-20261004; operación documentation.symbols. Producto, C/H, tests y preview congelados. No se ejecutaron algoritmos ni Doxygen; se reutilizó XML existente cuya entrada Graph/Cola coincide byte a byte con D.

## Delta comprobado

Se reconciliaron las declaraciones de los 38 símbolos Graph históricos con XML y SHA vigentes. Los 18 endorsements documentales históricos revisados necesitan revisión/rebinding al archivo actual; los otros 20 siguen pendientes. Esto no invalida las aceptaciones funcionales finitas. Se añadió grafo_sucesores_atomicos, privado de Prim/Dijkstra, con ubicación, firma y ownership: 39 funciones Graph confirmadas. El catálogo de 209 es una proyección del histórico más ese helper, no un nuevo censo global. Cero signoffs nuevos.

El original 208/121 se conserva íntegro. Además aparecen 19 registros RN con hash histórico distinto: recuperar el handoff documental posterior y vincular su evidencia antes de trasladar endorsement; no reabrir el cierre funcional RN ni tocar registros del propietario. Doxygen usó EXTRACT_ALL y WARN_IF_UNDOCUMENTED=NO: cero advertencias no certifica exhaustividad.

Se ordenaron las 67 lecturas SDD en bloques 14/15/38, por símbolo, fuente vigente y referencias de test encontradas. Una lectura o un archivo de test no acredita ejecución ni cierre.

## Nueve casillas globales: evidencia y pendiente necesario

|Criterio|Fuente/evidencia vigente|Recuperación pendiente|Verificación o trabajo aún necesario|
|---|---|---|---|
|11 Oráculo C|Cierres finitos por TAD/Graph y native-stack-statements.json|Vincular hash histórico de Desapilar (normal y vacía); registros específicos por utilidad|Ramas C de construir/eliminar_valor Heap no acreditadas por modelos Python; revisar cobertura restante por operación sin repetir cierres|
|12 Sección 2|graph-finite-acceptance-criteria-low.md; QA Graph; step-views-after-canonical.json|Agregar correspondencia caso/instrucción/vista de cierres anteriores|Cobertura pendiente de operaciones aún no cerradas; no inferir UI para utilidades Lista no expuestas|
|13 C/H y Doxygen|reconciled-symbol-catalog.json; XML B1 ligado a bytes actuales|RN19 handoff; endorsements Graph18 necesitan rebinding|Signoff de contenido Graph39 y restantes pendientes; comentarios C/H esperan permiso explícito ya solicitado por coordinación|
|14 Manual/ayudas|USER_GUIDE.md y graph-teacher-guide.md corregidos; consolidación Graph|Cruzar contratos aprobados por módulo con ayuda actual|Comprobar formatos/límites de módulos restantes; no certificar por lectura|
|16 Cambios/regresiones|Aceptación independiente Graph tres ajustes, freezes preservados|Agregar regresiones aceptadas de otros bloques a matriz final|Regresiones aplicables tras futuros cambios autorizados; no ampliar 200 vértices|
|17 Decisiones|Decisiones aprobadas Graph/H1/RN; continuidad actual|Mapa decisión→contrato→evidencia sin volver a pedir decisiones sustituidas|Resolver sólo ambigüedades nuevas vigentes; reconciliación global/C1 no cerrada|
|18 Revisión final|Resultados finitos fechados por bloque|Reunir comandos, revisiones y límites del agregado|Gate final aún no ejecutado; ASan/UBSan no disponibles según evidencia, sin instalación|
|19 Entrega|Tasks/progress/worklist y cierres finitos preservados|Matriz única referenciada y diff final|Entrega global y límites pendientes; no archivar|
|22 Raíces/dependencias|Inventarios existentes y matriz por símbolo|Clasificar utilidades Lista/Heap y helpers privados por raíces reales|Auditoría de uso/API ocultas/legacy pendiente; falta de UI no equivale a función muerta|

## Distinción de pruebas

Desapilar tiene informe nativo histórico con pop normal (incluye -1), liberación y printf de pila vacía: recuperar el binding SHA, no fingir nueva prueba. Test gcov existente es C real, pero encontrar su reporte durable antes de contar ejecución vigente.

Heap construir/eliminar_valor tienen fixtures del modelo Python; no se encontró evidencia nativa específica de guards, reserva fallida, eliminación ausente/última y reajuste arriba/abajo en la búsqueda acotada. La fixture construir con cantidad=99 y buffer de cinco valores no satisface la precondición C: no ejecutarla en C ni presentarla como equivalencia.

Lista seis utilidades: clasificar primero uso/raíces. Las siete operaciones visibles ya cerradas permanecen cerradas; la entrada eliminar_inicio de step-views registra not_available, no un resultado de UI.

## Entregables

- evidence/visible-documentary-source-reconciliation-low/reconciled-symbol-catalog.json: histórico preservado, declaraciones actuales y alertas de procedencia.
- evidence/visible-documentary-source-reconciliation-low/read-review-recovery-matrix.json: 67 filas ordenadas, sin endorsements nuevos.
- evidence/visible-documentary-source-reconciliation-low/specific-evidence-recovery-search.json: búsqueda acotada; resultados negativos no demuestran inexistencia universal.

Estado global permanece 13/22. Siguiente bloque: recuperar handoff RN y bindings específicos; después revisión documental de contenido conforme al permiso vigente. Ninguna autorización C/H se presupone.
