# Prioridad limpiar: cierre LOW de casos finitos

ID cerrado: `priority_queue.limpiar.instructions`. Autorización: nueva asignación `coordination-priority-queue-limpiar-finite-consolidation-low-20261003`, fuente coordinación01a0fe61-3104-743a-b032-bcc289ad80cd. La guarda documental no sustituye esa instrucción ni las pruebas. Se cierra únicamente el alcance registrado de cp_vaciar, no la familia Prioridad ni la auditoría global.

Revisión LOW: hashes actuales de siete piezas producto/guía, once fuentes QA/tests,155artefactos previos y115artefactos MEDIUM;288entradas únicas,0diferencias. Colección actual26IDs idéntica a MEDIUM:22anteriores+4nuevos disjuntos,26pass1.55s reutilizado sin ejecutar otra vez C/browser/regresiones. Anterioresrojos/límites/logs conservados.

Casos: vacío,uno(-1,2),multiFIFO[(7,3),(-2,1),(7,1)],reinserción(8,-1);dos limpiezas por fixture, ocho APIcalls. NULL del parámetro sólo oráculo nativo y motor directo. NueveCcalls153events41conditions32observaciones originales,0divergencias. Scope/init/types de cola/aux/next, identidad original del nodo desconectado, nextsucesor válido, rearNULLantesúltimofree, cantidaddecrecedespuésfree, auxretirado indeterminado con máscara0/historia separada, aux=next y returnvoidcaller vivo verificados.

UI ocho calls ambasvistas296adelante280atrás, snapshots exactos/masks/IDs/tipos/scopes/enlaces,cinco encabezados numerados;cuatro recargas exactas de historial+traza,0erroresJS/POSTextra. Cuatro mainsDOMreales originales conwrapperincludes,C17estricto,Doxseisinputs0warnings4/4main documentados,8alloc8free0live. Ocho mallocNULLsimulados:exit1,cleanup sinvivos y sin anuncio falso de la operación fallida. NoOOMreal niUB.

Recursos: ocho llamadas finitas contracemalloc,peakPython5,857,080bytes,maxJSON509,335bytes,maxinstrumented0.2305498s. NoRSS/browser/C/SLA,estrésuniversal ni límites de profundidad/historial arbitrarios. Excluye ABI/padding y cantidadinconsistente con cadena viva (rama guardcantidadfalse noAPI/fixture), todos los demás métodos y certificación global. El costo de metadatos respecto baseline1.59MB/138KB queda registrado.

C/H y contratos inmutables;215/219archivos protegidos iguales,cuatrofachadas/UI previstos congatesPriority,2módulos propios nuevos ya verificados. Cierres Pila/Cola limpiar, Hash/Sorting y popcomunicado intactos, RN/Grafos decisiones pendientes no elegidas. Preview45512/hijo49556D/run.py5051 se mantiene;sincommit/push/merge/despliegue. Global13/22/docs121/208 no incrementados por método.

Evidencia propia: `evidence/visible-priority-queue-limpiar-finite-consolidation-low/review.json`, verified-artifacts.json, verified-product-hashes.json y current-IDs-collection.log; evidencia funcional reutilizada MEDIUM y baseline preservados. Una reapertura futura requiere IDexacto/motivo/evidencia nueva/decisión/autorización real y guarda segúncontinuidad. No reimplementar por usar after.
