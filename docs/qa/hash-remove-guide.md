# Hash remove: checkpoint instruccional MEDIUM

Notas técnicas del cambio autorizado; no introduce requisitos ni contrato nuevo. Fuentes normativas vigentes: openspec/specs/hash-table/spec.md y deltas application-quality-audit/visual-playback-ui del cambio activo.

Remove conserva H1: clave int C, capacidad fija y encadenamiento. Ausente devuelve false/HTTP200, sin unlink/free/cambio de cantidad; entrada pública inválida responde400 sin llamada C. El C guardiaNULL/tabla sinbuckets/capacidad0 también retornafalse. Nodo nuevo no se reserva durante eliminación.

Th_eliminar recibe TablaHash* mutable y clave int. Th_indice recibe constTablaHash* propio con alias de la misma raíz. Scopes muestran llamadas/retornos y máscaras de locales; indice del caller no está escrito hasta la asignación después del retorno helper. ResiduoC0 de clave negativa no se normaliza. Comparaciones/retorno no aparecen antes de sus instrucciones.

Cabecera escribe tabla->buckets[indice]; interior/cola escribe anterior->siguiente. Tras unlink el nodo sigue vivo, ya no alcanzable desde buckets; cantidad aún no decrece. Free termina su vida: máscara actual0, máscara/campos previos sólo históricos. Actual queda value=null/initialized=false/valid=false; JSONnull no significa asignaciónNULL en C. El C no convierte actual aNULL: su valor deja de ser utilizable. Pointers.actual/memory.freed conservan identidad simbólica histórica explícitamente etiquetada, nunca dirección física leída después de free.

Cantidad decrece en la instrucción posterior. El panel declara mientras tanto cantidad=nodosalcanzables+1, sin adelantar contador ni fingir fallo de invariantes. Arreglo THNodo*, heap, variables tipadas, código, cadenas, costos y consola conservan antes/después. Kernel remove/helper no imprime; main.c imprime bool calculado después de cada llamada.

Paso anterior/Siguiente, cerrar/reabrir modo y recarga restauran traza sin ejecutar otra eliminación. Caller conserva repeticiones ausentes/orden real y cleanup en éxito/error. Siete callers finitos: cuatro reutilizan evidencia por bytesidénticos, tres nuevos. MallocNULL QA es simulación externa punto por punto; no OOM real ni opción pública de remove.

Seisfixtures cap3/cadenas<=4/int32 y guard API cap0;23eliminaciones nativas/436eventos seleccionados. Sin intérpreteC universal, aliasdirecciones físicas, sesioneslargas/cadenas arbitrarias/RSS/SLA/ABI32/sanitizadores exhaustivos. CheckpointMEDIUM pendiente LOW; seisotrosmétodosHash/global abiertos. Doxygen0 no firma documentos por símbolo. C/H/H1/RN/Grafos intactos.
