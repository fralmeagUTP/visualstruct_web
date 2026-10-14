# Balance del bloque de 122 pendientes

Se revisaron los 25 controles ya identificados y los otros 97 candidatos. Se añadieron 92 vínculos comprobables: **345 vinculados y 30 sin vínculo**, frente a253/122al inicio. Ningún requisito eliminado; ninguna nueva aceptación. Los30 pendientes son los25 anteriores y cinco widgets adicionales sin flujo vigente. Además queda un fallo de uso con ratón en un control vinculado por teclado:el conteo de vínculos no equivale al de brechas resueltas.

## Resultados por familia

| Familia | Casos nuevos PASS | Verificación |
|---|---:|---|
| Barra de navegación |7E2E| Activación, destino y encabezado específico. |
| Inicio e índices |21E2E| Enlaces de una instancia concreta del template. |
| Ayudas |20E2E| Navegación y contenido de destino. |
| Enlaces de estructura |8E2E| Ayuda, fase y constructor actuales. |
| Descargas |3E2E| Dos C/H byteidénticos; mainGraph verificado por teclado, con fallo de ratón abierto. |
| Widgets actuales |14E2E| Tipo y pasos de grafo; hash; random/reset; calidadJPEG; vistas/predicción; Counting pequeño; comentarios y resets. |
| Rutas |2API| AliasSorting y reset de ABB propio. |
| Propósito legado |1E2E| AltHome/End/R/P sobre traza existente, sinPOST. |

Para los97 candidatos:73E2E nuevos y2API nuevos pasan. Se reutilizan además dos casos de espejos internos Hash/Sorting cuyo hash de fuente no cambió. El caso de propósito legado pertenece al cotejo de los25, no se suma como widget nuevo. Total de casos nuevos distintos PASS en este bloque:76. Los reintentos corregidos no cuentan como casos adicionales. Los59 enlaces se acreditan en una instancia concreta, no en todas las expansiones Jinja.

## Fallo de puntero y correcciones de pruebas

La descarga de mainGraph falla con clic:un `.graph-panel-content` intercepta el puntero en `/graph/graph`, viewport1366x1000. Focus/Enter sí descarga un main con limpieza `free(g.a)` y `free(g.v)`. La evidencia de teclado no cierra el defecto con ratón. Registro:review122-mouse-gap.json y logs originales.

El borrador esperaba `grafo_destruir`, pero el generador vigente graph_main_service.py:11 libera ambas listas en línea. Se corrigió el esperado contra esa fuente, sin editar C. Otros errores iniciales fueron precondiciones:los resets piden confirmación; Counting restauraba modo manual y no debía cerrarse; mainHash está dentro de Resultados. Se corrigieron los estímulos con controles públicos y se conservaron los fallos.

El filtro Hash pasó dentro de un bloque mixto cuyo proceso terminó conexit1 por la descarga de otro caso. Se mantienen recursos yexit1 originales, yPASS por caso separado. Un recurso derivado incorrecto quedó marcado retirado; no es evidencia de un proceso exitoso.

## Disposición y conflicto de los25

**13 corresponden a presentación anterior;12 a funciones pedagógicas sin flujo actual;0 son internos.** No se encontró autorización individual para borrarlos en las decisiones citadas. REC1622–1626 de reconciliation-detailed sustituye disposición, etiquetas y visibilidad, conservando capacidades. No permite excluir funciones por cantidad de botones.

Para los13, disposition25.json detalla el propósito y sustitución actual:Home/End/Space en jerárquicas;modo manual y AltHome/End/P/R en secuenciales. La secuencia secuencial se probó sin nueva mutación. No se afirma equivalencia completa de autoplay o slider donde sólo se leyó fuente.

Hay una contradicción literal:visual-playback-ui:138 exige Preparar/Reproducir visibles, mientras sus reglas10/28/179 y la sustitución aprobada permiten controles compactos. La alternativa mínima es una delta que distinga ejecutar una operación nueva de preparar/navegar/reproducir una traza existente, mediante controles o atajos probados;sin exigir aquellos tres botones exactos. No se consolidó esa decisión aquí.

Las12 funciones afectadas son:predicción(selector,pista,skip,practice,resetprogress);comparación(kind,values,run,progress);guiado y nivel(level,example,load). hierarchical.js:2331–2337 elimina sus secciones y controles, mientras el contrato de cinco etapas exige conservar contenido adicional dentro de las etapas pertinentes. El usuario pierde esos flujos aunque queden modelos y handlers históricos.

La alternativa mínima recomendada, si permanecen en alcance, es conservar Predecir/Comparar como disclosures opcionales de Comprender, guiado en Preparar y explicación en Relacionar con código. No restaurar ocho etapas ni widgets antiguos. Si el retiro era intencional, hace falta decisión/deltas explícitos antes de cambiar el inventario. El conflicto exacto, sus fuentes e IDs están en review122-scope-conflict.md. No se restauró ni excluyó nada.

Los cinco widgets adicionales sin flujo son hier-check-prediction(mismo conflicto),hier-speed-slider,seq-speed-slider,seq-restart-execution yseq-sim-play. Se conserva su requisito;los atajos o datos internos no acreditan por sí solos el widget.

## Evidencia y límites

Todos los bloques usaron sesiones/cookies propias y límites120s/2GiB;ninguno alcanzó el límite. Máximo observado:84,375s y291,92MiB en inicio/índices. Counting usó[1000,0],no la campaña histórica de999999. Los26C y3904sesiones originales quedaron byteidénticos. SinDocker,proveedores externos,preview5051,commit,push ni despliegue.

Registro autoritativo:bindings-review122. Listado accionable:remaining30.csv. Fuente,vínculo,ejecución y aceptación separados;no cierre globalC1. Guardas finales correctas.
