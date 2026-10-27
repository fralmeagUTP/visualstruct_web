# CI del candidato congelado y conciliación separada

Entrega congelada: `9ad887b2d52db64e198767086fde25a9bfcc3e91`, PR3. Los commits posteriores de pruebas se conservan en `audit/visualstruct-tests-20261027`; no cambian esa entrega.

## Resultados comprobados al 27 de octubre, 15:48 UTC

- C17, ASan/UBSan: aprobados, run40530123995.
- Regresiones de entrega: aprobadas, run40530123863.
- E2E principal de algoritmos de grafos: aprobado, run40530123826.
- Unitarias0: 1377passed,19failed,10errors; el job acabó cancelado cerca del límite de15min. El artifact12746373462 conserva los informes de pruebas, exit1. No significa que todos los casos quedaran sin ejecutar.
- Unitarias1: job cancelado alrededor de15min; artifact12747106629 conserva selección, sin resultado completo. Clasificación: ejecución incompleta, no defecto funcional demostrado.
- Coverage1: 1414passed,24failed,13errors,4864deselected,1472.12s. Artifact12747139667. La colección ya no aborta: se ejecutaron pruebas. No se interpreta como cobertura0 ni se afirma que el umbral de cobertura esté satisfecho.
- Chromium0: 54calls pasaron,69calls fallaron,3errores de setup. Chromium1 también terminó con fallo. Otros jobs seguían ejecutándose o pendientes; la conclusión global no es verde.

## Clasificación basada en evidencia, no en nombres

| Hallazgo | Clasificación comprobada |
| --- | --- |
| BFS exige función C en cada paso | Expectativa antigua: sólo tres fronteras sin C_executed tienen función nula. Regresión puntual nueva aprobada. |
| Bellman-Ford exige historial idéntico después de llamada C fallida | Expectativa antigua de historial. Grafo completo, marcas e identidades conservados; temporales liberados. El contrato actual conserva la llamada fallida para traza/caller. Regresión puntual nueva aprobada. |
| DFS exige literal antiguo y aridad anterior | Expectativa de contrato anterior; migración de navegador separada conserva inventario y compara descarga/nativo. |
| review.md no coincide con575ce6e9… | Discrepancia documental auténtica y estrictamente rechazada. No se cambió el hash esperado. No demuestra un fallo de binsort. |
| Algunos oráculos de sorting y rutas de ayuda | Expectativas/portabilidad reparadas y pruebas dirigidas aprobadas en la rama posterior; no se atribuye retroactivamente ese resultado al SHA congelado. |
| Primer E2E Chromium0, allocation fast error linked-head | Falló remotamente, pasó aisladamente en16.69s con sus aserciones originales. Causa remota inconclusa; no se generaliza a los demás casos. |
| Doxygen/ayuda, callers históricos sin resolver fixture, traza Dijkstra/tablas y otros errores de los artifacts | Pendientes de diagnóstico individual. Los metadatos seguros identifican casos, pero no justifican llamarlos todos obsoletos ni defectos del runtime. |

Los diagnósticos seguros omiten entradas/tracebacks privados. Algunos eventos quedan como unknown por sanitización; no se reconstruyen conclusiones inexistentes. No se redujeron gates, permisos ni umbrales. La auditoría global continúa abierta y separada de la prueba controlada solicitada por el usuario en VPS.

Ejecuciones: [unitarias y cobertura](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40530123863), [E2E](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40530123826), [C17 y sanitizadores](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40530123995).
