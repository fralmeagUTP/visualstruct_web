# Diseño y etapas
1. **Fijar canon:** extracción Word2v3 revalidada, C/H byte-exactos, manifiesto y11firmas; sin dependencia del TAD Cola.
2. **Oráculos y contratos:** compilar canon C17 estricto; matrices normales/límites y fallo de cada reserva alcanzable; comparar estados, orden, marcas, propiedad y resultados.
3. **Semántica e integración:** extender un intérprete restringido al subconjunto real del libro, fail-closed ante sintaxis/tipos no soportados. GrafoEstado0..7, Trabajo, agregados/compound literals, sizeof expresión y long long. Normal y pasos deben compartir semántica del canon, no un fallback con algoritmo viejo.
4. **Trazas pedagógicas:** sustituir planes de construcción/BFS/DFS antiguos por instrucciones reales del libro; estado antes/después, ámbitos, publicaciones, memoria y retornos fieles. Mantener transporte compacto sin perder pasos.
5. **Clase y compatibilidad:** snippets/main/descargas/ayuda usan firmas nuevas exactas; fuente de estado diferente de stdout. Explicar NULL+OK frente NULL+error, costo_arco int0/1+salida, costos longlong, ausencia de bosque en MST desconectado, vecinos propios y listas prestadas. Sesiones/contratos separados; no cargar checkpoints antiguos ni reinterpretar historia con resultados antiguos implícitos.
6. **QA y paquete separado:** revisión independiente contra nativo, regresiones de otras familias y UI en5054 coordinada por auditor exclusivo. Nuevo paquete, nunca sobrescribir el verificado5053.

## Propiedad
Lead: integración GraphAdapter/services/rutas/canon y coordinación. Runtime writer: motor único y luego wrappers de trazas, archivos delegados explícitamente. Frontend writer: graph.js/template/ayuda/main cuando contrato esté fijado; no motor. Auditores: oráculos/QA/UI sin editar implementación. Fuente C/H canónica no se edita tras copiar.
## Compatibilidad explícita
Pesos y vértices siguen int32; acumulación longlong con sumar_seguro. NULL no basta para determinar éxito. Eliminar vértice ahora elimina incidentes dentro de C. Prim/Kruskal validan simetría/conectividad y no devuelven un bosque como éxito. BFS/DFS publican marcas sólo al éxito. Las listas prestadas de vertices/arcos no se liberan como propias. UI conserva modo dirigido/no dirigido como política del caller, explicando las llamadas reales y sus límites transaccionales.
## Límites de la prueba
Es un intérprete/simulador de C, no compilación nativa dentro de la app. Nativo sólo como oráculo QA. ABI de prueba int32/longlong64/size_t64 explícito; no certificación universal de plataformas o entradas.


## Presupuesto de captura aprobado (2026-10-27 10:12 UTC)

La interfaz captura como máximo 4.000 eventos C/caller más la publicación final.
El límite es de la visualización, no del C del libro. Preflight en una copia sin
snapshots ni escrituras de sesión; nunca se recortan eventos aceptados. Por encima,
modo paso rechaza sin cambiar historial/estado y modo normal conserva el resultado
real sin una traza extensa, con aviso explícito y controles de paso deshabilitados.
Medición: Dijkstra disperso 8 vértices, 2.553 pasos, 8,67 MB JSON y 149,7 MiB pico;
Kruskal denso 15 vértices contó 255.403 eventos sin construir snapshots. No se
provocó agotamiento de memoria ni se afirma soporte monolítico de ese caso.

La instancia aislada 5054 utilizará `SESSION_REFRESH_EACH_REQUEST=False`: las
lecturas/exportaciones no renuevan ni reescriben el almacenamiento de sesión.
Se conserva la configuración general y los otros doce TAD.
