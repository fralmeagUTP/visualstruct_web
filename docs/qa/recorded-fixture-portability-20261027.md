# Portabilidad de entradas históricas y validación previa a C

La primera ejecución de CI encontró archivos históricos ausentes y comparaciones de fin de línea que impedían ejecutar pruebas ya existentes. Las entradas recuperadas proceden de la copia original de sólo lectura; no son ejecuciones nuevas ni resultados reconstruidos.

## Entradas verificadas

El archivo de pruebas contiene 2.325 entradas con manifiesto, SHA-256 y tamaño. Sobre las 1.824 entradas anteriores se añadieron 148 archivos auténticos referenciados por el inventario nativo de los cinco auxiliares de prioridad, seis documentos de autoridad con referencias SHA ya declaradas y 347 entradas de subárboles concretos consumidos por las pruebas permanentes de pila, cola, prioridad y Hash. Las adiciones conservan datos y fuentes de texto, logs de contadores de propiedad explícitamente comprobados y XML de documentación solicitado por las pruebas; no incluyen ejecutables ni imágenes. El archivo histórico `before-3.bin` se verificó como fuente C UTF-8 sin bytes NUL, no como binario ejecutable.

La autoridad `dfs-transport-jpg-canonical-integration-independent-review/review.md` no coincidió con la referencia declarada ni en bytes originales ni con el único ajuste de transporte CRLF→LF. No se incorporó como autoridad coincidente ni se modificó el hash esperado. `source-binding-recovery-report.json` conserva el detalle del rechazo para su conciliación independiente.

## Resolución y rendimiento

`audit_input_path` verifica el SHA global y la lista exacta del archivo, y materializa sólo el archivo o subárbol solicitado, verificando sus bytes. Antes extraía aproximadamente 425 MiB para cada proceso auxiliar aunque éste necesitara un único JSON. La función explícita `recorded_input_root()` sigue materializando el árbol completo para los consumidores que lo requieren. Las rutas archivadas y los separadores de Windows se resuelven de forma portable.

Los observadores históricos no se alteran para fabricar nuevos resultados: sus fuentes y datos siguen siendo los originales. Los consumidores reciben las rutas verificadas correctas. Las pruebas de Hash comparan código descargado tolerando exclusivamente el transporte CRLF/LF y compilan los bytes efectivamente descargados.

## Rechazo de entradas y documentación

Las pruebas Rojo-Negro distinguen la validación de entrada en la API (`execution_started=False`, cero pasos) del rechazo de una precondición válida del TAD, que mantiene su comprobación específica. Se conserva la exigencia de que estado e historial no cambien y de que no se inventen instrucciones C, variables o reservas.

La ayuda mantiene su inicio sencillo y recupera dentro de la referencia avanzada los contratos de salida acotada/circularidad, los estados/rango de ordenamiento y la responsabilidad del llamador al liberar Rojo-Negro. No se modificaron los C/H.

## Verificación finita

- 214 pruebas focalizadas pasadas: resolución de fixtures, auxiliares de prioridad, llamadores Hash/C17/Doxygen, validación Rojo-Negro y contratos documentados nativos.
- 10 pruebas pasadas de integridad/publicación, incluidas cinco pruebas de extracción acotada, alias, digest global, hash de archivo y entradas ZIP no declaradas. Estas cinco también están incluidas en las 214 anteriores.
- Seguimiento ampliado: 338 pruebas relacionadas de pila, cola, prioridad y Hash pasadas en 31,08 s; 10 pruebas E2E se seleccionan en su ejecución separada, no en este seguimiento sin navegador.
- El seguimiento nativo Rojo-Negro/documentación produjo 314 pruebas pasadas y seis fallos Hash por una versión ya cargada del helper Doxygen compartido que añadía documentación de grafos a otros TAD. Con la condición corregida por nombre de archivo en ese helper, la ejecución nueva de las seis pruebas Hash pasa; está incluida en el seguimiento de 338.
- Las 2.325 entradas del ZIP verificaron su SHA-256 y tamaño originales; se preservaron aproximadamente 475 MiB de entradas sin ejecutables ni imágenes.

Estos resultados no certifican la suite completa ni un SHA para despliegue. La conciliación de autoridad rechazada y los resultados de CI global se informan por separado.
