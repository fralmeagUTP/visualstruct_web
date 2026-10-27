# Cierre finito Hash: creación/inserción

Fecha UTC2026-10-03, autorización nueva01a0fe61-3104-743a-b032-bcc289ad80cd. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Decisión LOW derivada de checkpoint hash-scope-fix-checkpoint-medium.md, fuentes C/H/specH1 y medición actual. Sólo los casos registrados de create_table/th_inicializar y insert/th_insertar (incluido th_indice) quedan verificados; Hash completo no cierra.

## Alcance exacto

Ocho secuencias nativas34operaciones originales: create3, empty insertion, colisiones/load4/3sinresize, update head/middle/tail, negativos/INTMIN/INTMAX, cap17colisiones. Tres casos C17 adicionales de parámetros/scopes/alias en capacidades1/3/17 con key-1/INTMIN/INTMAX. Validaciones públicas cap0/texto/keyfueraint en tests, nunca fingir llamada C. Fallo mallocNULL de nodo y actualización con fallo configurado (sinreserva) comparados por instrucción. Cinco callers descargados cleanup25alloc/free/0vivos,25puntosNULLsimulados; noOOMreal. Inicialización NULL C/caller verificada, no inyección pública de su traza.

Kernel statements, branches, indices/actual/nuevo/i/root, masks/unpublishednodes/linkwrites/countwrites/cost/return coinciden con observador nativo seleccionado. Parámetrocapacidad separado de structfield, helperconstparam/clave/indice con scopepropio y aliasroot C17_Generic; helperscopes expiran y callerindice sigue indeterminado hasta asignación. Análisis C seleccionado, no intérprete universal/todos los locales físicos.

98IDs únicos pasan en conjuntos disjuntos95+3 del checkpoint, hashes inalterados; no reruninnecesario ni suma de corridas repetidas. Cuatrocasos UI404frames/384restauraciones0redispatch/0JS,cinco secciones yreload igual. Doxygen C/H+callers0warnings y suplementoownership/errores; comentarios C/H concisos no equivalen a cierre documental global.

## Overhead actual acotado

Misma34operaciones para medición, no cobertura nueva: pico tracemalloc6878420bytes, JSONmáximo646047bytes, tiempo instrumentado máximo0.524s. IncluyeFlask/JSON/sesión; noRSS/SLA/timingproducción. Capacidades3/17 y cadenas≤5. Scopes recientes están incluidos. Creación mediante snapshotsdensos/deepcopy replica buckets al menos cuadráticamente: capacidadenorme admitida/entradaarbitraria no quedan certificadas, sin reservarmemoriaenorme/OOMreal. Mediciones anteriores históricas se conservan.

## Plataforma y límites de cierre

Windows,Python3.10.5,GCC C17 int32/puntero64,Chromium147 de plataforma verificada. Const/type/alias observados medianteC17, direccionesUI simbólicas sólo dentro de operación. No mallocNULLreal/OOM, noNULLtabla/valorarbitrarios de API noexpone, noexpansión aotras9operacionesHash, nofrontendmultipantalla universal ni suiteglobal/coverage reejecutada. H1enteros/capacidadfija intacto. C/H/95originaltests+nativos3/11Sorting/arnés hashes preservados. Global13/22/docs121/208 sinincremento.

Creación/inserción no deben reimplementarse/repetirse como bloque cerrado sin evidencia nueva,decisión yguardareopen auténtica; usar fixtures no genera nueva cobertura. Siguiente trabajo autorizado: baselineLOW get/contains segúnmapa, sin implementar semántica ni cierresprematuros. RN/Grafos/no publicación/commit/push/merge/despliegue.
