# Hito funcional Grafos: reparación autorizada, sin cierre por instrucción

Asignación actual: coordination-graph-bellman-prim-integer-cycle-resumed-medium-20261004. Operación graph.bellman-prim-integer-cycle-approved-medium. Proyecto D:\MisProyectos\Web_VisualEstruct. Único escritor técnico. Fecha de captura 2026-10-04; la guarda before-resumed pasó. Este hito no sustituye la asignación ni autoriza ampliar C.

## Resultados por algoritmo

- Bellman-Ford: C long long con alcanzabilidad independiente, suma previa comprobada y prueba por límite de ruta simple; mantiene relajación en sitio/orden/empate. Detecta dos INT_MIN alcanzables; acepta INT_MAX y rutas fuera de int. Veinte fixtures permanentes revisados contra autorización vigente: todos conformes. El observador histórico conserva cuatro etiquetas unexpected_backend_rejection porque esperaba success=true; son los cuatro errores de ciclo ahora requeridos, revisados separadamente sin borrar reporte.
- Prim: presencia de candidato separada, negativos/extremos, bosque y orden C. Diecisiete fixtures: dieciséis en dominio C/API no dirigido coinciden también en orientación/orden; el dirigido demuestra rechazo API y selección legacy C sin bandera. No se presenta ese caso como equivalencia.
- Dijkstra: cuerpo C intacto, Python adopta orden C, mejora estricta, INT_MAX infinito/guarda, rechazo de todo negativo. Dieciséis fixtures sin divergencias.
- Kruskal: cuerpo C intacto, Python usa orden estable de todos los arcos raw/mirrors y lista resultante por prepend. Diecisiete fixtures: dieciséis en dominio coinciden también en orientación/orden; dirigido rechazo API conforme.

## API, persistencia, memoria y documentación

Ciclo ejecutado retorna HTTP400/success=false, conserva result/flag/diagnóstico y last_operation error; no añade consulta exitosa, conserva consultas anteriores. 21 regresiones de pesos/historial pasan en4.99s: no se suman a los casos nativos ni se afirma unión global única. Pesos int32 finitos,2.0 y texto2.0 normalizan2;fracciones/Inf/NaN/fuera de rango/bool se rechazan.

Cuatro contextos Chromium reales; dos consultas exitosas por algoritmo, recarga/replay sin POST extra, cero errores JS, cuatro mains originales C17-O2-Werror pasan. Bellman además cambia el grafo a ciclo y observa400 conservando las dos consultas previas; su main no registra la llamada fallida. Capturas/HTML/stdout en browser-functional-after. Fixtures del navegador no suman nuevas garantías de instrucciones.

Observador C17-O2 sobre los fixtures anteriores conserva todos los campos/enlaces/marcas del grafo. Reservas/liberaciones: BF181/181,Prim249/249,Dijkstra172/172,Kruskal163/163,cero vivos. Incluye setup/auxiliares/resultados/liberación final; no son cifras de sólo el algoritmo ni del caller Chromium. Sin inyección de fallos, sin ASan/UBSan, sin promesa no acotada.

Sólo cuerpos C Bellman-Ford/Prim y sus comentarios cambiaron; todos los demás tokens C y firmas/estructuras H son idénticos. AST Python ajeno a los métodos autorizados es idéntico. BFS/DFS, helpers privados cerrados, Hash/Sorting/RN no se reejecutaron ni reabrieron. CCodeService/ExecutionTraceService actuales no se editaron en este hito. Guías y comentarios C/H Bellman/Prim sincronizados. Doxygen real C/H:0warnings; no firma208símbolos ni se avanza contador documental global.

## Pendiente explícito / siguiente trabajo en la misma asignación

No hay cierre instruccional de ninguno de los cuatro algoritmos. Los planners actuales aproximan pasadas, candidatos y auxiliares. Con ciclo y success=false la traza legacy todavía cae en un recorrido genérico de14pasos; conserva consola/flag, pero NO prueba ni muestra correctamente todas las instrucciones del algoritmo ejecutado. Debe corregirse antes de declarar completa la autorización: reproducir C por instrucción, short circuit, índices/arcos/arrays, ramas de ciclo temprano/final, candidatos/fallo/limpieza y fuente ejecutada; contrastar observador C independiente y player real. También quedan límites/fallos de reserva acotados y signoff de nuevos deltas/documentación sólo después de verificación completa. No ampliar C fuera de BF/Prim.

Preview propio reiniciado tras verificar identidad, con FLASK_PORT5051: launcher17660,hijoPython16044;HTTP200. Conhost20788 no es Python. Logs vivos fuera del manifiesto. No commit/push/merge/deploy. No cambio13/22,121/208 ni C1 del otro propietario. Se conserva el intento browser de importación fallido y su corrección parents[5] antes de ejecutar Chromium.

Evidencia principal: evidence/visible-graph-bellman-prim-integer-cycle-approved-medium/functional-authorization-review.json,protected-source-review.json,ownership-readonly-review.json,product-delta-functional.json,functional-regressions.xml,browser-functional-after/report.json,doxygen-after/warnings.log. Resultados anteriores intactos. La guarda after reporta este hito abierto, no permite reimplementación de bloques cerrados.
