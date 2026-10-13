# Revision independiente PQ event delta — 2026-10-07

Veredicto: ACEPTADO focalmente para los dos archivos vinculados. No autoriza publicacion por este revisor.

36 hashes coinciden con D:. XML before: 3 FAIL/1 PASS; after: 4 PASS. Tres fixtures empty/single/three nodes y el test original de conformance. Los nuevos controles revisan cada frame: IDs freed exactos before-minus-after, unicidad, un free por node_free y cero en otros eventos, sin liberaciones repetidas, historial acumulado/counter/masks/campos invalidos preservados. El fallo anterior reaparecia tambien despues de free porque retired era acumulativo; los controles lo detectan.

Comparacion AST normalizando exclusivamente heap_transition.freed: codigo previo y nuevo identicos. En este flujo los IDs vivos son unicos, el heap conserva nodos retirados y solo node_free cambia alive a False; filtrar retired por previous-live entrega exactamente previous-live minus current-live. No afecta stores C, scopes, state, source, listas vivas, historial_fields ni contadores. Se preservan 250 de los 251 hashes runtime historicos; la unica diferencia es el archivo de cleanup autorizado. C y tests previos vinculados coinciden. Worker guardado final exit0, Job 2GiB antes de importar app; no se repitieron pruebas HTTP/native/browser o suites.

Aclaracion de evidencia: pq-after-result.json incluye la etiqueta generica test_only_no_C_runtime_changes=true. Esa etiqueta no describe literalmente este lote, que SI cambia metadata en un archivo runtime Python. Se requiere una nota aclaratoria append-only del autor, conservando el log; la prueba independiente de alcance es el diff/AST y hashes, no esa etiqueta. No invalida los 4 resultados XML ni el cambio focal.

Indice: se mantiene la limitacion ya declarada de recuperacion semantica, sin identidad byte a byte ni prueba de metadata nunca persistida. No se edito indice/producto/tests desde esta revision.

E2E7630e77 cancelado: sigue abierto; la espera/test concreto permanece sin identificar. Otros defectos/59 causas, Sorting, RN y cumplimiento global no cerrados.
