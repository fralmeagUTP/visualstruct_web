# Resultado finito 2026-10-27

Copia aislada `vs-cf`, base bfe7ab0284a4735cd5660dcc0c88c5ac05b8a6ac. Worktree largo solicitado falló por filename too long; alternativa corta creada con core.longpaths. Sin commit/push/deploy ni cambios C/H, backend, graph.js, styles.css o base.html.

Implementación: console-history.js conserva stdout observado y prefijo activo por identidad de traza, no duplica replay, conserva repetidos y vacíos, sin límite de ocho líneas. publish conserva scroll manual y horizontal; sigue final sólo si ya estaba al final. sessionStorage versionado contiene observaciones, con identidad exacta JSON del historial; mismatch/reset lo invalidan. Caché no equivale a ejecución/replay de C; si falta, no reconstruye salida. Coordenación incorpora script antes de familias en base.html.

Pruebas: node --check de cinco JS PASS. check-console.cjs PASS sobre trazas reales Flask Lista y ABB y casos de prefijo/forward/back/replay/reset, repetidos legítimos, recarga de observaciones/history mismatch, scroll modelado manual/final. Endpoints reales: linked_list insertar_final(7), buscar_elemento(7) x2 emite `\n Encontrado en la posicion 1\n`; ABB insertar(7), inorden x2 emite stdout auténtico en memory_state. Hash insert(1,7), get(1) x2 y Sorting burbuja run x2 tienen éxito pero no publican stdout en console/console_stdout/console_events. JSON completo en endpoint-traces.json. Probe inicial stack/cima fue inválido (no operación pública) y no cuenta como cobertura.

Límites concretos: falta ejecutar/instrumentar printf del caller de Hash get y Sorting run, publicarlo con cursor y persistir/reconstruir desde ejecución auténtica. sorting_main_program.py incluye printf Run/Estado y resultado, mientras sorting_adapter.py/counting_trace_service.py/radix_trace_service.py entregan console_events vacíos; hash_structure_service.py sólo transporta result.console. No se reemplazó por data.message o síntesis de payload. No se afirma paridad nativa main/stdout ni cobertura de todas las operaciones.

Prueba visual: Playwright Chromium headless no inició por PermissionError WinError5 creando pipe del driver. Acción no ejecutada, sin aprobación automática rechazada; no screenshot. Se requiere verificación visual integrada de las cuatro familias y scroll real. El harness Node modela scroll pero no constituye prueba visual. Estas limitaciones mantienen abierta validación final.

Continuidad: índice ajustado sólo localmente a copia autorizada y añadido binding nuevo; no publicar ruta personal como canonical_project.
