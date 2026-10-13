# Revisión independiente de Sorting, opción A aprobada

Fecha: 2026-10-07. Proyecto canónico: `D:\MisProyectos\Web_VisualEstruct`.
Change: `review-sorting-source-A-approved`; operación: `qa.sorting-source-A-approved`; assignment: `coordination-sorting-source-A-independent-qa-low-20261007`.

## Dictamen: RECHAZO focal

La opción A sí dispone de aprobación explícita para rechazar fuente ausente, vacía o incompleta antes de construir el intérprete, sin fallback, éxito ficticio ni historial exitoso. No autoriza decisiones RN/Grafos, nuevas semánticas de algoritmos ni un editor de C arbitrario. La implementación conserva los rechazos ordinarios y los asserts anteriores, pero deja una vía material para admitir fuente C sin funciones activas.

`validate_sorting_source` compara cuerpos extraídos y omite el contexto de preprocesamiento. En la reproducción independiente, las once fuentes canónicas originales, incluidos sus helpers requeridos, fueron aceptadas al envolverlas íntegramente en `#if 0` / `#endif`. En C esos cuerpos quedan desactivados. La comprobación previa permite continuar hacia el intérprete Python pese a no existir las funciones C activas requeridas. Véase reproducción (evidencia local: `openspec/changes/archive/2026-10-13-review-sorting-source-A-approved/evidence/independent-review/preprocessor-counterexample.json`).

La reproducción compiló únicamente AST de las funciones originales de ensamblado/extracción y del validador, con proveedor de lectura local. No importó ni ejecutó algoritmos del producto, intérpretes, C nativo, navegador ni suites técnicas. Las once fuentes canónicas sin envoltorio fueron aceptadas. Las variantes íntegramente comentadas fueron rechazadas. Esto demuestra un defecto de admisión, no una ejecución observada del intérprete ni fidelidad global de Sorting.

## Cambio requerido

Rechazar tempranamente directivas de preprocesamiento que el contrato de fuente soportado no pueda interpretar de forma segura, o validar su contexto semántico completo. Añadir controles negativos para `#if 0` y directivas capaces de alterar las instrucciones admitidas, verificando ausencia de constructor del intérprete y conservación de estado/historial. Conservar controles positivos de las once fuentes canónicas y las variaciones de comentarios/indentación ya admitidas. No se requiere aceptar C arbitrario, introducir un compilador general, modificar algoritmos ni debilitar los cuatro fallos restantes.

## Evidencia preservada

- Los 84 inputs de `final-input-sha-binding.json` coinciden con sus hashes actuales; no hay discrepancias.
- Todos los asserts de los seis consumidores modificados se conservan mediante comparación AST: 10, 26, 129, 14, 44 y 44 respectivamente. Véase checks (evidencia local: `openspec/changes/archive/2026-10-13-review-sorting-source-A-approved/evidence/independent-review/checks.json`).
- Los dos XML finales guardados contienen 38 casos únicos, 34 PASS y 4 FAIL al deduplicar classname/nombre; los 14 originales quedan 10 PASS y 4 FAIL. No se repitieron pruebas. Véase deduplicación (evidencia local: `openspec/changes/archive/2026-10-13-review-sorting-source-A-approved/evidence/independent-review/xml-dedup-check.json`).
- Los resultados focales y cierres operativos no acreditan cumplimiento global de Sorting, C1, RN/Grafos ni E2E.

## Anomalía del índice

La anomalía reportada corresponde a `.git/index`. Su SHA actual coincide con el último registro de preservación del autor, pero difiere del SHA histórico. HEAD sigue en `ba53ba7c0bcebaf7a4938328ebf4c863f19eadab` y `git diff --cached --name-status` está vacío. No se estableció la causa del cambio de bytes ni se restauró el índice. Estos datos no muestran cambio actual de contenido staged, HEAD o inputs congelados; no prueban identidad binaria histórica. Véase lectura del índice (evidencia local: `openspec/changes/archive/2026-10-13-review-sorting-source-A-approved/evidence/independent-review/git-index-readonly-check.json`).

La comparación separada del índice de continuidad conserva los cambios, fuentes y operaciones previamente registrados; las diferencias observadas son adiciones del binding final y de la revisión. No debe confundirse ese índice documental con el índice Git. La guarda de esta revisión identifica la asignación independiente vigente.

## Alcance y siguiente acción

Se leyeron originales y se escribió exclusivamente evidencia independiente de este change. No se tocaron código, C/H, contratos, matrices, evidencia/checkpoint del auditor, preview ni índices; no hubo instalación, red, publicación, commit, merge o despliegue. La aceptación focal requiere cerrar la admisión por preprocesamiento y presentar evidencia concreta del arreglo preservando los inputs y resultados anteriores. La causa histórica del SHA del índice continúa sin determinar y se conserva como limitación trazable, sin restauraciones especulativas.
