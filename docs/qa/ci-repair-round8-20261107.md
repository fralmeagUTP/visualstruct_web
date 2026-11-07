# Octava revisión: controles Graph integrados con la recuperación Heap

Base exacta: `950f716761bf59419a2ef714216de964b26489e6`, árbol `13cfc3579d5f39c50b3fbeb964687e44cbf88c4c`.

## Alcance y reserva

Se integran los tres archivos Graph revisados: controles adversariales, mapa de nueve obligaciones e informe de su alcance. Este documento es el cuarto archivo nuevo. **Esta tanda cierra cero gates históricos.** Los nueve gates Graph se conservan; mejores pruebas del producto actual no equivalen a recuperar programas históricos ausentes ni a demostrar equivalencia entre contratos distintos.

Los ocho archivos de la revisión Heap anterior permanecen byte por byte idénticos. También permanecen intactos los 334 paths protegidos comparados, incluidos producto, workflows y los 73 archivos C/H del repositorio, de los cuales 26 son fuentes canónicas. No cambian selección de CI, presupuestos ni límites.

## Verificación de la combinación

- Ejecución focal conjunta Heap + Graph bajo pytest-cov: **163 PASS y un fallo histórico preservado**, 164 IDs distintos y **492 eventos oficiales**. Cada ID tiene setup, call y teardown; JSONL y resumen coinciden en contenido y orden, y contienen la selección completa.
- El único fallo es `test_mechanical_negative_controls_and_observer_unchanged`: falta el `native-final-second/native.jsonl` histórico. El test no se omitió y su input no se fabricó. El gate de preservación del baseline Heap reparado en R7 sigue aprobando.
- Entorno local: Python 3.12.14, Doxygen 1.9.8, directorio relativo de diagnósticos y `NODE_PATH` sin definir. La cobertura focal no certifica el umbral global.
- Colección completa: **7780 IDs**, conserva los **7753** de R7 y añade los 27 controles Graph. Los **568 IDs Chromium general** permanecen idénticos. Colección no equivale a ejecución.

Las ejecuciones previas descritas en el informe Graph se solapan con esta combinación; no se suman como casos únicos adicionales. La revisión independiente de los controles verificó 20 mutaciones rechazadas en sus oráculos correctos y tres mutantes nativos que compilan y ejecutan 30 escenarios cada uno antes de rechazar resultados inválidos.

## Qué falta

El mapa [current_graph_obligation_map.json](../../qa_convergence/current_graph_obligation_map.json) distingue exactamente cada obligación histórica, su comprobación actual y la reserva pendiente. El [informe Graph](../../qa_convergence/GRAPH_SUCCESSOR_REVIEW_20261107.md) conserva el detalle de las tres preimágenes ausentes, firmas anteriores, puntos de observación distintos y contrato de ayuda.

No se ejecutó navegador local en esta revisión. La CI de R7 debe concluir y ser revisada antes de autorizar esta publicación. Después será necesaria la CI del commit nuevo, separada de las pruebas de su padre. Esta revisión no certifica suite completa verde, cierre de gates históricos, merge ni despliegue.
