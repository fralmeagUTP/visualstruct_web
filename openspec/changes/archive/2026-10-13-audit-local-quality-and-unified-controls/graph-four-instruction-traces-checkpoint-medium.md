# Checkpoint de trazas Graph MEDIUM para QA y consolidación LOW

Fecha UTC: 2026-10-04T03:19:41.980947+00:00. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Change audit-local-quality-and-unified-controls, operación abierta graph.bellman-prim-integer-cycle-approved-medium. Asignación vigente coordination-graph-four-instruction-traces-medium-20261004; el hito funcional anterior se conserva. La coordinación pidió publicación por algoritmo y residual concreto; no cierre automático ni estimación por 13/22.

Se implementó un modelo AST restringido del C actual y helpers reales con variables tipadas, ámbitos/frame IDs, condiciones y operandos short circuit, arrays inicialmente indeterminados, reservas/retiros, referencias prestadas/propias, llamadas/retornos y printf. No se invoca un compilador en producción: el C nativo instrumentado es oráculo QA. La traza rechaza sintaxis/lecturas no soportadas en vez de inventar pasos. Los resultados no aparecen antes de la recepción explícita del caller. El retorno implícito void ahora marca la invocación terminada; el fallo inicial y su corrección están preservados.

| Algoritmo | Cohorte C17 -O2 normal/límites | Fallo de reserva privado | Navegador actual | Residual propio |
|---|---|---|---|---|
| Bellman-Ford | 20/20 fixtures coincidentes, incluido ciclo extremo/final y no alcanzable | 6/6; limpiezas y retorno NULL coinciden | 389 pasos de éxito y 406 de ciclo; 780/814 fronteras DOM; printf sólo en paso388 del ciclo | Recursos, QA independiente y actualización documental |
| Prim | 17/17 ejecuciones C coincidentes; dirigido se valida aparte en API | 13/13; helper puede omitir sucesores por malloc fallido | 469 pasos, 940 fronteras DOM | Recursos; no afirmar MST óptimo ante falla de helper; QA/documentación |
| Dijkstra | 16/16 coincidentes; C y semántica INT_MAX protegidos | 9/9; helper puede omitir sucesores por malloc fallido | 351 pasos, 704 fronteras DOM | Recursos; no afirmar ruta óptima ante falla de helper; QA/documentación |
| Kruskal | 17/17 coincidentes; orden estable/arcos simétricos/UF | 5/5; cleanup y retorno NULL coinciden | 430 pasos, 862 fronteras DOM | Recursos y QA/documentación; C no fija orden de operandos != |

Estas cantidades pertenecen a cohortes distintas; no se suman como grafos únicos ni porcentaje de auditoría. El modelo final se recontrastó con todos sus ledgers C preservados sin reejecutar compilaciones normales: current-model-native-recheck-after-void.json. La corrección del observador Kruskal cambió sólo preparación de call; eventos distintos de call permanecen iguales. El orden observado de GCC es una ejecución válida, no garantía universal de evaluación izquierda-primero.

Pruebas permanentes: tests/test_graph_four_instruction_contract.py (12 passed, 4.14s); tests/test_graph_four_instruction_e2e.py (4 passed, 88.11s tras corrección void). La primera corrida E2E también pasó4 y no constituye4 IDs extra. La corrida conjunta inicial dio20 passed/1 failed/1 deselected: fallo void luego corregido y cubierto por las12 finales; nueve regresiones existentes BF/historial pasaron en esa corrida, no se anuncian como una nueva suite final global. tests/_audit_graph_four_instruction_observer.py conserva runner C normal y --allocation-faults. Artefactos y errores iniciales preservados.

Seis rechazos previos API verifican cero eventos C, cero printf, call_stack/variables vacíos y ningún query nuevo. Un destino entero inexistente mantiene el contrato API de consulta exitosa sin ruta, pero ahora wrapper y traza reflejan retorno temprano C y no publican distancias calculadas después de ese retorno. BF ciclo realmente ejecutado produce HTTP400, diagnóstico y limpieza sin historial exitoso. En navegador se conservan dos llamadas exitosas iguales; reload/replay/seek no hacen POST ni redispatch de consulta. Cuatro mains reales del DOM compilan C17 -O2 -Wall -Wextra -Wpedantic -Werror y sus salidas calculadas coinciden con API. C/H HTTP tienen nombres y bytes canónicos. /help/source/graph/main responde404: no existe descarga HTTP Graph main, no se finge esa cobertura ni se añade route en este bloque.

Fuentes compartidas protegidas: protected-source-review.json y diffs. C/H canónico y engine funcional integer_algorithms.py intactos; sólo GraphAdapter.execute, Grafo.dijkstra/bellman_ford (destino opcional), CCodeService._build_graph_data y ExecutionTraceService.build_trace cambian dentro del alcance. Renderer BFS previo intacto. No ejecución de cierres BFS/DFS/Priority/Hash/Sorting/RN ni nuevas firmas/dominio C.

## Límites que impiden un cierre global

Recursos: api-final-integration-resources.json mide tres vértices por algoritmo, 409–811 eventos, JSON HTTP9.05–22.19MB y pico Python75.40–183.42MB durante generación+serialización. Tiempos6.90–16.34s incluyen tracemalloc; no son SLA ni estimación de tiempo restante. Medición anterior al ajuste sólo de status void; tamaños son esa medición fechada. No hay muestreo ni interpolación final. No se certifican grafos admitidos de200 vértices ni inputs densos; hace falta resolver representación/transportes de snapshots antes de cierre de escalabilidad. No ejecutar estrés sin límites que pueda agotar memoria.

Opciones concretas para siguiente asignación: deduplicar snapshots con reconstrucción exacta en el player (versionar transporte/validar ambas vistas); o paginar eventos desde una ejecución persistida (validar aislamiento, ciclo y navegación sin redispatch). Conservar todos los eventos; un corte/muestreo o reducir el dominio requiere decisión explícita. Ninguna opción se implementó silenciosamente.

Fallos malloc/calloc son un hook privado del oráculo/modelo, no inyección en API/browser. En Prim fallo6/8 y Dijkstra fallo5/7 del fixture conectado altera resultado mediante sucesores omitidos por el helper heredado. Se conserva fidelidad y ownership, no se corrige ese contrato C fuera de autorización ni se garantiza mínimo bajo fallo de reserva. La firma C NULL continúa ambigua (error, vacío, no-ruta, ciclo), sin nuevo enum/outparam. ABI verificado int32/longlong64/size_t64/pointer64; no otras implementaciones C certificadas. ASan/UBSan no disponibles según evidencia previa, sin nueva instalación/probe ni afirmar UB universalmente ausente.

Documentación: ledger existente contiene121/208 entidades revisadas y87 pendientes (82 sin signoff+5 revisión completa pendiente), pero38 entidades Graph registran hashes completos C/H previos al hito funcional. graph-documentation-ledger-readonly-review.json explicita esta desactualización; refrescar ubicaciones/hashes y revisar cambios semánticos BF/Prim antes de tratar ledger como evidencia actual. No se modificó ledger de otro dueño ni se reabren por mero hash funciones C protegidas intactas. Doxygen0 del hito funcional anterior no equivale a signoff individual completo.

## Criterios todavía abiertos de las nueve tareas globales

| Tarea en tasks.md | Evidencia necesaria para reconciliar, además de parciales existentes |
|---|---|
| Oráculo C/instrucciones/ownership | Integrar QA independiente por alcance, residual de helpers/malloc/ABI/invariantes y excepciones documentadas; estas cuatro cohortes no cierran todos TAD |
| Sección2 de todas operaciones | Matriz de aceptación de ambas vistas, scopes, resaltado, antes/después, consola y replay para todos métodos, con límites explícitos y solución recursos Graph |
| Descargas/Doxygen/símbolos | Bytes/nombres/conjunto C actuales, XML/warnings y signoff individual pendiente; refresco de38 entradas Graph y87 pendientes del ledger |
| Manual/ayudas | Contraste final de instrucciones, contratos aprobados, controles/formato/límites y hallazgos pendientes |
| Implementación menú/controles/documentación | Reconciliar regresiones aprobadas y revisión transversal final; trabajo parcial mayor ya implementado no basta para casilla global |
| Decisiones semánticas | Confirmar decisiones vigentes y registrar cualquier residual nuevo (recursos/fallo helpers), sin resucitar decisiones superadas |
| Verificación final/cobertura/C/sanitizadores | Suite final coherente sólo cuando coordinación autorice, cobertura actual y límites de herramientas; no correr suite global ahora |
| Entrega matriz/evidencias/diff/instrucciones | Consolidar registros actuales, alcance de cierres finitos y límites; no archivar por verde sintáctico |
| Limpieza raíces/dependencias | Resolver UI/API oculta/internals, demostrar uso/inutilidad y coordinar rupturas; no eliminar por hidden=true |

Global13/22 no modificado. C1/documentación transversal/QA independiente pertenecen a sus dueños. No porcentaje de esfuerzo ni promesa de plazo. Para LOW: revisar este checkpoint/manifest, priorizar recursos y refresco documental y solicitar QA independiente; sólo después evaluar decisiones finitas de cierre. No ampliar otros bloques desde checkpoint histórico.

Preview propio actualizado: launcher21408, Python14888 (parent21408), conhost18112, run.py canónico, listener127.0.0.1:5051 PID14888 y HTTP200. Logs vivos excluidos manifest. No push/merge/commit/despliegue. Guarda before ya verde; after se registra en evidencia junto con manifest y hashes actuales.
