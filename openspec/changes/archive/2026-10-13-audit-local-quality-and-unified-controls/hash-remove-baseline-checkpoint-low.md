# Hash remove LOW baseline collected; instruction review pending

ProyectoD:\MisProyectos\Web_VisualEstruct, asignacióncoordination-hash-remove-baseline-low-20261003, operaciónhash.remove-baseline-low. Nuevo mapa autoriza remove después de cierre finitoqueries. beforeexit0; after fresco capturado en evidencia. Producto/C_H/106IDs/creación-inserción/queries/11Sorting preservados. No cierre remove ni nueva semántica.

## Resultado y evidencia nativa

Seisfixtures capacidad3,23eliminaciones: vacía/repetición, head de cadena4 y repetición ausente, middle, tail, negativos (-6,-4,-1,-9), INT_MIN/INT_MAX y ausentes.23resultadosbool/estadofinal/ordenbuckets/cantidad/capacidad C/API idénticos.317eventos observados th_eliminar,17free de nodos,0reserva en eliminación. Observador inspecciona sólo nodos aún vivos; después de free no lee/compara actual retirado. Identidad por clave válida dentrofixture, no direcciones físicas. Helpercanónico th_indice ejecutado, eventos internos/typedscopes/lifetimes completos no instrumentados en este baseline; no fingirparidadporinstrucción. Fuenteinstrumentada bajo native/ y kernelcanónico descargado/compilado intacto. Sonda C17 original aparte verifica firma bool(TablaHash*,int),NULLtabla/tabla0/destruida.

## Tres regresiones abiertas permanentes

1. REMOVE-FUTURE-STATE: remove7 en cadena10→7→4→1 muestra size0 durante `int indice = clave % tabla->capacidad`, y estadofinalsize3 antes de unlink/free/count--. C conserva cantidad4 hasta `tabla->cantidad--`, incluso tras desvincular/liberar. Costos/comparaciones/retorno/valor_salida anticipan resultado en entry. Regresión verifica no mutación antesenlace, count4 trasfree, entrycost0/no retorno.
2. REMOVE-SCOPE:23trazas sin debugscopes; TablaHash*tabla mutable propio th_eliminar/constTablaHash*tabla helper/intclave/indice/THNodo*actual/anterior no acreditados por instrucción/alias/lifetime.
3. REMOVE-MODULO-ZERO: remove-6/cap3 ejecuta visualmente `indice += tabla->capacidad` aunque residuoC0; rama falsa. No cambia resultado final, sífidelidad.

Archivo tests/test_hash_remove_baseline_low.py:9IDs nuevos,6pass3fail/4.93s, sinxfail. Intersección0 con106anteriores, unión115IDsregistrados; no115passni corrida115. Primerresultadoversión/log preservados; segunda añadeassertcost/return sin quitar aserciones. Scopeasserts no fueron ejecutados más alládelprimerfallo, pendientesvalidaciónMEDIUM.

## UI/caller/documentación

UI trescasos/13operaciones/232frames/219restauraciones, cinco secciones,0POST adicional/0JS,últimatrazaigualmente incorrecta recuperada en recarga. Esto prueba replay de traza, no fidelidadC. Repeticiónausente se conserva en main;13llamadasCactuales debrowsermás4 delcallerHTTP=17calls, solapadascon23baseline, nocoberturanueva. Cuatro callers realmente descargados strictC17 O2WallWextraWpedanticWerror:21alloc21free0vivos y21puntosmallocNULL externoscleanupstatus1. Main imprimebool calculado porC, includingremovefalse. Doxygen real C/H descargados y cuatromain:0warnings. C/Hhash iguales; noledgerdocumentacióncerrado.

## Límites y siguiente paso

Cap3/cadenas<=4/int32/extremos/Windows/Python3.10.5/GCCptr64/Chromium147. No OOMreal/sanitizadores/sesioneslargas/RSS/SLA/cadenas arbitrarias, noNULLtabla enAPI. Consultas4/11finito,removeabierto,7restantesexactosremove,keys,values,items,stats,clear,destroy_table. Global13/22/docs121/208 sinincremento. PreviewD5051preservado sinrestart/cambiosproducto. PropuestaMEDIUMacotada hash-remove-instructions-plan-medium.md: intérprete causal de remove/helper/heap/free/count/scopes/cost, preservar23resultados/3rojas/106IDs/H1/C_H; reportecheckpointantesLOW. No implementarMEDIUMsin instrucciónnueva.


## Continuidad y estimación al terminar

Primera guarda after rechazó prefijos del índice recodificados; original y log conservados. Se restauraron69campos de texto mediante reversión de codificación, sin cambios de tareas/contratos/estados previos; todos los bindings únicos y after0. continuity-status-comparison.json muestra sólo cierre del checkpointbaseline actual. Lecturas/escrituras finales índice UTF8 explícito. [Estimación provisional y backlog](audit-estimate-after-hash-query-low.md): siguientehito remove1–3h conMEDIUM; totalorientativo24–48h efectivo bajo supuestos/decisiones, sin compromiso calendárico ni porcentaje13/22.
