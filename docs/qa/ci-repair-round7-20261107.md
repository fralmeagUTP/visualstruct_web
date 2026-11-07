# Séptima revisión CI: preservación auténtica del baseline Heap

## Alcance

Base exacta: `93bbd21dec0a27fb7a36b4065a0f60d88fa4e5dc`, árbol `c8d37a66091ae35a0cf66973ae3d736911dc4a17`. Esta revisión cambia siete archivos de pruebas/evidencia y este informe. No cambia producto, C/H, workflows, selección de CI, presupuestos ni límites de rendimiento. La PR permanece en borrador. No certifica cierre total, integración ni despliegue.

El gate de preservación de Heap comparaba el hash histórico de un test original con su sucesor portable actual. Se recuperó el contenido auténtico de `tests/test_sorting_heapsort_baseline_low.py` del [commit dde0d956](https://github.com/fralmeagUTP/visualstruct_web/blob/dde0d95691482e7c6db1922d0983ef287479dacf/tests/test_sorting_heapsort_baseline_low.py), blob `a6b24b7346869a9978a0dc9271b694bad84e9019`.

Los 7493 bytes LF de Git se conservan literalmente. La conversión exclusiva LF a CRLF produce 7562 bytes y reproduce el pin histórico inalterado `8a59530b549cf79ed726e9be3f5d5311b47a5bbea46882e2d038f3361007b637`. Es reconstrucción de transporte verificada, no una afirmación de haber descargado los bytes CRLF originales.

## Garantías

- Se preservan ambos snapshots, sus hashes, el blob Git y la procedencia. El recibo y el adaptador AST existente quedan fijados por hash.
- El gate sigue leyendo el registro histórico original y conserva su pin. Verifica los bytes históricos y la igualdad AST completa del sucesor, con los adaptadores ya existentes de rutas, transporte y texto aprobado.
- No se amplían los adaptadores. El baseline actual, los siete módulos protegidos y sus controles permanecen intactos.
- Los controles negativos rechazan alteraciones de hashes, procedencia, adapter, casos, aserciones, valores esperados y comportamiento adicional.
- Recuperar el archivo no recupera autorizaciones, informes de ejecución ni otros inputs históricos ausentes. Esta es una decisión actual y explícita de sucesión verificable, no una aprobación histórica retroactiva.

## Validación local

Revisión independiente: 54 pruebas de contratos aprobadas y 15 mutaciones adicionales rechazadas. El revisor recuperó los bytes directamente de GitHub y comparó baseline y adaptador con el head remoto. Esa revisión aislada no ejecutó la aplicación completa.

Integración en copia nueva del árbol base: **121 PASS y un fallo histórico conservado**, en 122 casos distintos y **366 eventos oficiales**, idénticos en contenido y orden al resumen. Se ejecutaron los siete módulos de pruebas relacionados bajo pytest-cov, con directorio relativo de diagnósticos, `NODE_PATH` sin definir, Python 3.12.14 y Doxygen 1.9.8. Incluye el gate reparado y el baseline Heap completo. El fallo restante es `test_mechanical_negative_controls_and_observer_unchanged`, por ausencia del `native-final-second/native.jsonl` histórico. No se regeneró ese input ni se omitió el test.

Los 54 controles independientes y los 121 casos aprobados se solapan. No se suman como casos únicos. La cobertura focal no certifica el umbral de cobertura global.

Colección completa: **7753 IDs**, conserva todos los **7737** anteriores y añade 16. Los **568 IDs Chromium general** permanecen idénticos. Colección no equivale a ejecución. Los 334 paths protegidos de producto, workflows y C/H comparados permanecen idénticos a la base.

## CI de la base, terminada

La CI de `93bbd21` terminó antes de esta publicación:

- C17/Sanitizers, Caller, Graph E2E, Firefox, runtime y delivery: aprobados.
- Chromium general: **568/568 PASS**.
- Unit: **6964 PASS y tres fallos históricos**.
- Coverage: **7140 PASS y 20 fallos históricos** (18 de llamada y dos de setup); coverage-gates quedó omitido.
- Los 12 streams están completos y coinciden ordenadamente con los resúmenes. Las uniones de selección no tienen pérdidas ni solapamientos.
- Los 18 ZIPs tienen digest correcto y head exacto. De 24 capturas, 23 coinciden con imágenes revisadas y una fue inspeccionada: diferencia limitada al logo, sin hallazgo bloqueante nuevo dentro del alcance sintético.
- Graph p95 **111,262 ms**, mediana **110,651 ms**, cinco iteraciones e historial/replay de 300 operaciones, frente al límite intacto de 200 ms.

[Unit y cobertura de la base](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42339582775). [E2E de la base](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42339582799).

## Pendiente

La CI del nuevo commit debe ejecutarse y revisarse por separado. Localmente se resolvió un gate de los 20 históricos; no se declara una CI verde ni se da por aprobados los otros 19. Persisten la ejecución Heap ausente, la discrepancia documental BinSort, ocho preservaciones documentales y nueve contratos Graph pre-libro que requieren recuperación auténtica o sucesores explícitos con garantías equivalentes y revisión. Se conserva la historia y no se sustituyen hashes para forzar aceptación.
