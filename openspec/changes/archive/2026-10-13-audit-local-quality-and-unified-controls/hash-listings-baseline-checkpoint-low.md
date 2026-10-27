# Hash listings baseline LOW: fidelidad pendiente

Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Asignación coordination-hash-listings-baseline-low-20261003; operación hash.keys-values-items-baseline-low. Evidencia en evidence/visible-hash-listings-baseline-low.

Cuatro fixtures (vacío, cadenas con duplicados/negativos, extremos int32, buckets dispersos) producen 12 proyecciones API coincidentes con el recorrido bucket/cadena observado en C. C no exporta funciones keys/values/items: th_formatear produce texto, y la API proyecta pares completos por separado. No se equipara una proyección completa con un buffer truncado.

39 llamadas C reales al formateador: 36 combinaciones fixture/buffer y tres guardas. Capacidades 0,1,2,8,16,64,128,2048,4096; prefijos, terminación y guardas fuera del buffer coinciden. El harness inicializa su almacenamiento A5 para comprobar límites sin lecturas indeterminadas; esto no verifica máscaras de un buffer local sin inicializar. El primer compile del harness falló por indentación; se conservó el log y se corrigieron sólo sus llaves.

Ocho IDs nuevos disjuntos de los 123 anteriores: cinco pasan y tres fallan sin xfail. Los defectos son cuerpos C/helper ausentes, almacenamiento tipado/scopes ausentes y consultas repetidas omitidas del caller tras recarga. Las aserciones rojas en bucle paran en keys; report.json documenta por separado las 12 trazas. Hay 131 IDs registrados, no 131 pruebas verdes; no se repitieron los 123 cerrados.

UI real: 18 consultas, 36 frames, 18 retrocesos, cinco secciones, cero POST adicionales/errores JS; replay y recarga conservan el stub de dos instrucciones. Esto no prueba fidelidad del formateador. Los cuatro main.c distintos omiten las consultas: compilan C17 estricto y pasan Doxygen, pero no reproducen los listados. Ownership separado: 23 alloc/23 free/0 vivos y 23 malloc-NULL simulados, sin OOM real.

No se modificó producto, C/H, H1, contratos ni bloques cerrados. Hash conserva cinco de once métodos cerrados finitamente; pendientes keys, values, items, stats, clear, destroy_table. Global 13/22, documentación 121/208 y C1 1/12 no cambian. No se certifican capacidades arbitrarias, sanitizadores, ABI varargs ni rendimiento universal.

El rechazo previo de auto-review al delta ADDED se conserva en visible-hash-remove-instructions-medium/auto-review-rejection.md. No se creó ni reintentó ese spec; sólo se documentó el contrato H1 existente.

Siguiente paso: revisión MEDIUM acotada del plan hash-listings-instructions-plan-medium.md, pendiente coordinación. Este checkpoint cierra únicamente la recogida de baseline, no los tres métodos.
