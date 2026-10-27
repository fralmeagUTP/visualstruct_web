# Dictamen independiente: AVL causal y Sorting17

**Aceptación focal de AVL causal; rechazo de la adopción directa de Sorting17 sin reparar su harness.** Este dictamen documental no integra código ni cierra QA global, cobertura o rendimiento.

## AVL causal

El ZIP revisado tiene SHA-256 `9429b057f8e19728e47352d2601f7cc04c198f335baf9a146cb837ec07db6198`: 48 entradas, 47 archivos más manifiesto. Se verificaron CRC, tamaños y SHA contra el manifiesto y sus originales. Los 994 inputs de la nueva fotografía coinciden con el destino canónico. Frente a la fotografía anterior, el único cambio de producto es `app/domain/hierarchical/avl_insert_instruction.py`; la cadena de fotografías anteriores resuelve con hashes correctos.

El contraste AST identifica únicamente las dos nuevas sentencias de metadatos en `emit`. La comparación recursiva de respuestas guardadas LL, RR, LR, RL y tres casos sin rotación conserva tipos, claves, orden, estados y valores anteriores, retirando únicamente los metadatos nuevos y restaurando la fase antigua mediante `instruction_phase`. El hint previo permanece igual.

En las cuatro rotaciones observadas hay exactamente dos etapas: selección en la llamada, con FE del pivote de magnitud 2 y camino del estado observado; aplicación inmediatamente después del retorno del helper exterior correspondiente. Los límites no mutan el estado por sí mismos. Las rotaciones dobles no introducen etapas públicas por sus primitivas internas. Los tres casos sin rotación no emiten etapas ni hint; el duplicado conserva `success=False`.

El XML anterior acredita un fallo de la aserción original; el posterior acredita ocho comprobaciones focales satisfactorias. Su composición es una regresión ejecutada y siete comprobaciones de capturas/AST, **no ocho nuevas ejecuciones del servicio**. Esta revisión no ejecutó ninguna prueba funcional. Los siete ejemplos no acreditan pivotes interiores no raíz, UI, replay, asignación de memoria ni comportamiento global.

## Sorting17: reparos obligatorios para adoptar

Las 17 unidades conservadas ofrecen invariantes útiles: resultado y multiconjunto, entrada intacta, snapshots sin alias, índices y métricas monótonas, subrango Quick, mezcla con empates/restos y Heapify local. Los tres oráculos nativos reverse conservan sus hashes y resultados finales; no acreditan eventos ni contadores C. La comparación adicional con el motor público es suplementaria. No se repitieron las 17 unidades ni los oráculos nativos.

1. `context()` exige `coverage.Coverage.current()` no nulo antes de las aserciones semánticas. Copiar el módulo exige instrumentación activa para todas las unidades. Hacer opcional la instrumentación o separar el harness de cobertura, conservando las aserciones.
2. Los reverse buscan `provenance.json` mediante `Path(__file__).resolve().parents[1]`. En staging existe; copiando el módulo a `tests/`, apuntaría a un archivo ausente en la raíz del proyecto. Además, sus referencias a archivos dependen del cwd y de rutas históricas. Proporcionar fixtures/oráculos durables y versionados con resolución explícita, preservando hashes, inputs y filas finales.

La corrección y adopción necesitan autorización e identidad de fuentes actualizadas. Después, la validación mínima debe acreditar las mismas 17 unidades con ejecución normal sin cobertura obligatoria; la prueba histórica no acredita automáticamente el harness editado. No se modificó el módulo staging ni se integró código.

Límites adicionales: duplicados enteros no demuestran estabilidad etiquetada; monotonía no demuestra fidelidad de métricas C; `isinstance(int)` admite booleanos. Quick singleton privado y público tienen contratos de métricas distintos.

## Alcance y evidencia

El denominador actual es estático: 186 archivos, 24147 sentencias y 4 exclusiones; no es cobertura medida. El incremento histórico de 106 líneas de los contextos Sorting usa el denominador anterior 24133 y no demuestra cumplimiento global. La cobertura histórica 42.79%, umbrales de 83/85%, límite de 5 s y QA global siguen pendientes; no se agregan las 17 pruebas históricas a las ocho comprobaciones actuales como 25 ejecuciones nuevas.

Evidencia: causalidad e integridad (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/avl-causal-stages-sorting17-independent-qa-low/source-causality-equivalence-and-provenance.json`), calidad y reparos Sorting17 (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/avl-causal-stages-sorting17-independent-qa-low/Sorting17-quality-and-adoption-repairs.json`), integridad final (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/avl-causal-stages-sorting17-independent-qa-low/integrity-after.json`), guarda before (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/avl-causal-stages-sorting17-independent-qa-low/before.json`), guarda after (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/avl-causal-stages-sorting17-independent-qa-low/after.json`).

Sólo se escribieron este informe, evidencia propia y el tracker propio. Sin pruebas técnicas nuevas, cobertura, benchmark, nativo, navegador, instalación, red, Git, cambios de preview o checkpoint del auditor.
