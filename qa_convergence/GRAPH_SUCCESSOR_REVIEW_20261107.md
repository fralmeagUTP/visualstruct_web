# Revisión de garantías actuales y obligaciones históricas Graph

## Decisión y alcance

Esta revisión añade controles adversariales a los sucesores `graph-book/v1` que ya existían. No duplica sus implementaciones ni cambia producto, C/H, workflows, selección de pruebas o tests históricos. **No reemplaza ninguno de los nueve gates históricos ni afirma equivalencia entre los motores antiguo y actual.**

Base revisada: commit `93bbd21dec0a27fb7a36b4065a0f60d88fa4e5dc`, árbol `c8d37a66091ae35a0cf66973ae3d736911dc4a17`. La posterior revisión Heap `950f716761bf59419a2ef714216de964b26489e6` no cambió estos archivos Graph. Cualquier integración posterior debe volver a verificar su árbol completo.

`current_graph_obligation_map.json` relaciona exactamente los nueve IDs fallidos con sus obligaciones, hashes de archivos originales, comprobaciones actuales y límites que siguen abiertos. El mapa es una descripción de garantías, no una admisión histórica ni una modificación de selección.

## Nuevos controles

`test_current_graph_successor_controls.py` contiene 27 casos:

- Tres comprobaciones aceptan ejecuciones reales de los oráculos actuales de recibo numérico, publicación de vértices y consultas.
- Veinte mutaciones de resultados reales deben ser rechazadas por esos mismos oráculos. Cubren límites entre C y host, identidad de retorno, tipos, ownership propio/prestado, memoria viva, cleanup, estado, resultados escalares, costo e historial.
- Una comprobación conserva los hashes de los cuatro archivos históricos registrados y las declaraciones existentes de no equivalencia y selección intacta.
- Tres mutantes temporales del harness nativo prueban que se rechazan un extremo inexistente, costo incorrecto y cleanup omitido. No mutan las fuentes C/H canónicas. Cada mutante debe compilar con C17 estricto, ejecutar los 30 escenarios y producir un fallo real, no un error accidental de compilación.

La revisión independiente verificó que las 20 mutaciones fallan en las aserciones de sus oráculos correspondientes. Los mutantes nativos terminaron con código 1 y rechazaron respectivamente 20, 6 y 30 escenarios. Estos números describen escenarios de mutantes y no son casos pytest adicionales.

## Verificación local

- 41 casos distintos aprobados en una ejecución integrada bajo pytest-cov: los 27 nuevos, los sucesores actuales, los controles de no vacuidad de narración y las pruebas actuales de guía del libro.
- Una comprobación adicional de capacidad actual aprobada. La unión de ambas ejecuciones contiene 42 IDs distintos y 126 eventos oficiales, coincidentes en contenido y orden con sus respectivos resúmenes, sin fallos.
- La revisión independiente repitió los 27 casos nuevos. Se solapan con los 41 integrados y no se suman al total.
- La colección sobre la base 93bb conserva sus 7737 IDs y añade 27: 7764 en total. Colección no equivale a ejecución ni certifica la selección del árbol que integre otros cambios.
- 345 archivos protegidos comparados con la base permanecen idénticos, incluidos producto, C/H, workflows, fuentes históricas y sucesores existentes.
- Los nueve gates históricos se ejecutaron sin modificaciones: siete fallaron en llamada y dos en setup. Sus fallos siguen visibles. No se añadieron skips, xfails ni reglas de exclusión.

No se ejecutó navegador en esta revisión. La cobertura focal no certifica cobertura global, CI completa, rendimiento, integración ni despliegue.

## Lo que sigue sin poder certificarse

### Tres comparaciones con programas históricos ausentes

Los tests de preservación esperan `numeric-null-baseline.py`, `graph-vertex-note-baseline.py` y `graph-query-note-baseline.py`. Esas preimágenes no están disponibles en las fuentes inspeccionadas. Cambiar sólo la narración actual y comprobar que no cambia su ejecución es útil, pero **no prueba equivalencia con esos programas ausentes**. Los mocks antiguos apuntan a motores retirados: hacerlos pasar sin invocación sería vacuo.

### Asignación, retorno y publicación de contratos distintos

El harness antiguo de reserva usa firmas anteriores del TAD; el actual usa las firmas canónicas y comprueba estado/costo además de los escenarios de extremos y memoria. Los historiales antiguos sin contrato no se reinterpretan como `graph-book/v1`. El recibo de una lista ocurre antes de su liberación explícita y de la publicación final API. Un costo ausente ejecuta C bajo el contrato actual, mientras la prueba antigua esperaba rechazo de entrada. Ninguna de esas diferencias se oculta mediante adaptadores genéricos.

### Ayuda renderizada

El gate histórico de ayuda alcanza y aprueba sus aserciones iniciales sobre el límite de 15 vértices y la distinción entre aplicación y TAD, pero falla en el enlace textual `Cola FIFO</a>`. Las pruebas actuales describen la cola de índices usada por el libro, el C renderizado exacto y los enlaces a sus funciones. Eso no demuestra todas las garantías de texto/enlaces del test antiguo, por lo que se conserva el gate.

## Próximo paso verificable

Recuperar las tres preimágenes auténticas y reconciliar explícitamente las obligaciones que pertenecen al contrato antiguo con las del contrato actual. Si esas fuentes no se recuperan, declarar la reserva histórica y obtener una decisión explícita sobre su tratamiento; no convertir esta mejora de QA actual en una afirmación de cierre de los nueve gates.
