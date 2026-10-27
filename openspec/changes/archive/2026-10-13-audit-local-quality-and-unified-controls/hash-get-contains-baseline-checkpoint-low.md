# Hash get/contains: baseline LOW checkpoint

Fecha UTC2026-10-03; proyecto D:\MisProyectos\Web_VisualEstruct; assignment coordination-hash-get-contains-baseline-low-20261003; operación hash.get-contains-baseline-low. Iniciado después de anuncio/decisión de cierre finito create/insert autorizada por instrucción nueva01a0fe61-3104-743a-b032-bcc289ad80cd. No repetir los métodos cerrados como nueva cobertura; sólo fixtures para consultas.

## Resultados reales

Cuatro fixtures capacidad3: vacía; colisiones head/middle/tail/ausente; negativos con residuo0/no0; INTMIN/INTMAX/ausente. Doce claves consultadas con get ycontains:24consultas C17O2strict/API. Los24resultados coinciden con C; el observador registra búsqueda/contiene/helper, branches, output_write/dummy_initialized, bool/valor y contadores. Dummy indeterminado nunca se lee antes de escritura. Sentinel de get ausente se mantiene en C, API devuelveNone; resultado coincide aunque status incumple spec.

Tres brechas con regresiones rojas permanentes, sinxfail:
-4getausentes devuelven200successTrue; openspec/specs/hash-table/spec.md exige400 ymensajeausente.
-4consultas negativas múltiplos3 (-6/-9 enget/contains) animan indice+=capacidad, cuando Cregistra residuo0 ynegative_guardFalse, sinnormalize.
-Las24trazas carecen debug/scopes/instructionmemory explícita; dummy/output-pointer/helperconst no se representan fielmente porinstrucción. No inferir fidelidad a partir de resultado correcto.

Tests nuevos tests/test_hash_get_contains_baseline_low.py:3fallan0.74s.98IDs anteriores/casosC17/C_H/11Sorting conservados SHA.101IDs actuales distintos(98verdes retenidos+3rojos nuevos), no corrida101 ni sumar pruebas solapadas. Primera observación nativa se conserva; helper se instrumentó después del hallazgo para confirmar causalmente normalización, sin contar otro24como cobertura.

UIactual5051:5consultas(repetición get4 incluida),0erroresJS/cinco secciones/0POSTextra navegación+modo+reload; última traza get restaura. CallerHTTPmain200 siguehistorialmutante5pasosfixture yno contiene th_buscar/th_contiene. Es limitación documentada actual, no fuga demostrada ni eliminación de historialmutante: reproducción de consultas queda pendiente y requiere observación separada sin incumplir specgetnomutahistorial.

## Próximo bloque MEDIUM delimitado, aún no ejecutado

Getausente debe adaptar error al400 ya especificado, sinnuevo contrato. Planner debe probar residuo real<0, no signo de clave. Motor acotado th_buscar/th_contiene/th_indice debe representar caller/helperconst/valoroutputpointer/dummyindeterminado, guardsNULL/retornos/cost/branch/scopes/heap estable porinstrucción, y replayUI sinredispatch. Consultas exitosas/fallidas para caller deben separarse delhistorialmutante si se autoriza ampliación de reproducción; no fabricar resultados ni declararownerquerycertificado. Reconciliar tests legacy que codifican200ausente con specvigente, conservando originales/evidencia; no debilitar regresiones.

Guardas before/after. C/H yproducto sin modificación LOW; preview10024/16576 D/run.py5051 mantenido. Cierrecreate/insert finito vigente, otros9Hash pendientes, global13/22/docs121/208 sinincremento, RN/Grafos sincontratos nuevos. No publicación/commit/push/merge/despliegue. GuardasNULLoutput/table/Ccap0 y más UIcasos/ownership/recursos de consultas quedan pendientes, sin fingir cierre get/contains.
