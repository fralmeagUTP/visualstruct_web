# Dictamen independiente QA535 y conexión Sorting

**ACEPTADO, con alcance finito.** Se acepta la procedencia del paquete y su gate de cobertura de líneas, y la reparación focal del runner acreditada por los casos registrados. No se acepta ni se declara cierre global, suite final, fidelidad universal o rendimiento. Revisión de lectura; cero pytest, ejecuciones C, navegador, aplicación o campañas nuevas.

Proyecto canónico: `D:\MisProyectos\Web_VisualEstruct`. Change `review-final-coverage535-sorting-runner-quality`; operación `audit.final-coverage535-runner-source-review`; assignment `coordination-final-coverage535-runner-source-independent-qa-low-20261005`. Dictamen separado del verificador mecánico del autor.

## Comprobaciones propias

- SHA actuales de 1000 fuentes y 1715 pares original/copia del paquete coinciden. Los 186 módulos permanecen en el denominador, con cuatro líneas excluidas. Sólo cambia `app/services/conformance/runner.py`; los otros 185 módulos son byteidénticos.
- Al retirar del AST actual exclusivamente el import, el helper y restaurar las tres llamadas delegadas, resulta exactamente el AST anterior. PythonParser identifica 229→239 sentencias en runner: +10 explica 24154→24164 sin excluir código.
- Los 21 XML contienen 536 casos PASS; los eventos concuerdan exactamente con cada selección y tienen setup/call/teardown PASS. 535 IDs únicos; sólo `tests/test_conformance_scenarios.py::test_deterministic_error_is_rejected_by_c_and_python[sorting]` aparece dos veces. No dobleconteo de ese ID.
- SQL independiente de los 15 raws anteriores y seis actuales reproduce exactamente los 4800 pares archivo/contexto de la unión del autor y de la recombinación privada. Remapeo exclusivamente del runner; se descartan exactamente las antiguas 294/326. Las nuevas llamadas 308/340/400 y helper tienen cobertura actual, sin atribuirles ejecución antigua.
- El verificador inspeccionado y ejecutado con salida privada verifica también igualdad textual/propietario AST del mapa, contextos de prior485/remapped485/final535 y líneas ejecutadas, faltantes, exclusiones y resumen por módulo. Resultado: **20065/24164 = 83,03674888263532%**, 4099 faltantes. Gate83 de líneas PASS.
- El bloque de reparación conserva 39 invocaciones PASS y aporta 38 IDs nuevos; los últimos 12 agregan 12 IDs. Por tanto 485+38+12=535 únicos. Los intentos mixtos/fallidos originales se conservan y no forman parte de los raws aceptados.

Evidencia propia: AST, hashes, XML e IDs (evidencia local: `openspec/changes/archive/2026-10-13-review-final-coverage535-sorting-runner-quality/evidence/independent-review/independent-static-provenance.json`), unión SQL independiente (evidencia local: `openspec/changes/archive/2026-10-13-review-final-coverage535-sorting-runner-quality/evidence/independent-review/independent-sql-union.json`), recombinación privada (evidencia local: `openspec/changes/archive/2026-10-13-review-final-coverage535-sorting-runner-quality/evidence/independent-review/recomputed/result.json`). El último archivo mantiene explícitamente su etiqueta mecánica: no sustituye este dictamen.

## Reparación y límites

El helper copia el payload y obtiene el snippet del algoritmo activo mediante CCodeService, con el directorio C/H configurado en el runner. Compare, compare_error y CompiledConformanceRunner usan la conexión. No hay cambio adicional de normalización, dominio, adapters, rutas, C/H o contratos en este diff. Para estructuras distintas de Sorting la llamada conserva operación y copia de payload. La prueba privada compilada registrada conserva equivalencia y payload original; no equivale a certificar los once algoritmos ni todos los caminos.

La equivalencia de conexión es la de los escenarios del runner: selección explícita `select_algorithm` antes de `run`. `_sorting_arguments` rechaza `step`; el helper lo contempla pero ese camino no queda certificado. El servicio web además procesa `algorithm_id` inline en run/step; ese preprocesamiento no forma parte del contrato de escenarios del runner. No interpretar la expresión del autor «replica esa conexión» como paridad completa de entradas web.

Los 485 PASS anteriores siguen siendo resultados históricos con cobertura derivada de líneas intactas. Igualdad textual y propietario AST no demuestran por sí solas comportamiento; la aceptación combina esos límites con el diff mínimo y la evidencia focal actual. No son 535 ejecuciones nuevas. La nueva conexión supersede legítimamente el SHA live anterior del runner, sin alterar el paquete QA387 histórico ni usar su verificador para certificar fuentes actuales.

La cobertura conjunta tampoco atribuye a cada ID toda línea aportada por fixtures compartidos o preparación nativa, ni demuestra fidelidad instrucción por instrucción. Se conserva la distinción entre test PASS, cobertura ejecutada y contrato global. Los criterios 11/12/16/18/19 y la auditoría global no se cierran por este dictamen; BFS/performance conserva su estado previo.

## Cambios requeridos

Ninguno para aceptar este paquete y repair en el alcance indicado. Al comunicar o consolidar el resultado es obligatorio preservar los límites anteriores: «gate de líneas PASS en unión compatible derivada», no suite final/global ni 535 tests nuevos. No es necesario ampliar ahora pruebas o contrato de step/entradas web.

No se editaron paquete del autor, fuentes, tests, C/H, contratos, configuración, preview5051, bindings, índice o evidencia previa. Seguimiento actualizado sólo en el tracker propio. Guardas before y after propias acompañan la revisión; la guarda documental no aporta aprobación funcional.
