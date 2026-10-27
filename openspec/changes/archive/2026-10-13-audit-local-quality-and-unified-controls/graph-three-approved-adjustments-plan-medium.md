# Tres ajustes Graph aprobados, bloques acotados MEDIUM

Asignación actual coordination-graph-three-approved-adjustments-medium-20261004, operación ya abierta graph.bellman-prim-integer-cycle-approved-medium. Aprobación exacta en graph-three-adjustments-user-approval.json: usuario «Si» a tres ajustes e independiente QA. Supersede congelación técnica anterior; conserva evidencia y permisos anteriores. No elegir bloque desde checkpoint histórico.

1. Helper C privado atómico para sucesores, utilizado sólo por Prim/Dijkstra: devolver estado explícito privado, liberar lista parcial al fallar reserva; caller abandona con su limpieza y NULL. Firmas públicas, structs, enteros, Dijkstra INT_MAX/empate/negativos, Prim candidato/forest y BFS/DFS/otros callers permanecen. Sólo este helper nuevo y dos cuerpos C/callercleanup, sus trazas/wrappers/docs/pruebas sincronizadas. No modificar grafo_sucesores público ni cabecera fuera de comentarios específicos necesarios. Publicar hito/freeze1.
2. Reducir duplicación de snapshots/metadata y transporte, conservando todos eventos y reconstrucción exacta antes/después, scopes/arrays/retirados/stdout/highlight. No muestreo/corte/dominio nuevo. Medición comparativa finita, equivalencia de expansión y player adelante/atrás/seek, límites de recursos explícitos. Publicar hito/freeze2.
3. Un generador compartido para main DOM y descarga HTTP de misma sesión, llamadas cronológicas iguales preservadas, ciclo/rechazo sin llamada exitosa, sin redispatch; filenames/bytes/C17/outputs/recarga/aislamiento. Publicar hito/freeze3.

Único escritor técnico actual. QA real distinto: 01a0ff54-79d7-7520-8e9f-224ef5ed700f, binding separado review-graph-three-approved-adjustments. No escritor/revisor paralelo sobre fuentes canónicas; checks QA usan puntos congelados/fixtures privados, coordenador informa reanudación. La creación binding no prueba ejecución QA ni cierre.

No AISEF/arnés general, scripts de guardas, instalaciones, funciones C/H ajenas, reejecución de cierres BFS/DFS/otrosTAD, suite global, push/merge/commit/despliegue. Guardas before/after por tarea; cada hito antes del siguiente, LOW para consolidar tras MEDIUM acotado.
