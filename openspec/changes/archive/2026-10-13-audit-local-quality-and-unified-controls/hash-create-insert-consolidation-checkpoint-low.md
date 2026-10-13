# Revisión LOW de creación/inserción Hash: cierre retenido

Fecha UTC2026-10-03; assignment coordination-hash-create-insert-consolidation-low-20261003; operación hash.create-insert-consolidation-low; fuente nueva coordinador01a0fe61-3104-743a-b032-bcc289ad80cd. Cierre funcional/instruccional de las dos operaciones NO justificado todavía. MEDIUM sigue siendo checkpoint, no cierre global Hash.

## Hallazgos nuevos confirmados

1. init_entry: `debug.variables.capacidad.value=3`, pero `pedagogy.variables.capacidad=0`. El parámetro C se sobrescribe al fusionar campos del struct con el mismo nombre. C17 observado confirma parámetro3 y campo raíz0 antes de tabla->capacidad=capacidad.
2. th_indice tiene un parámetro propio `const TablaHash *tabla`; el modelo solo conserva `tabla` del caller con tipo `TablaHash *` y no representa el parámetro scoped del helper. El `th_indice.indice` sí está separado, por lo que su tratamiento de parámetros resulta incompleto/inconsistente. _Generic C17 confirma puntero const e int para clave. El código C/H canónico permanece intacto.

Pruebas permanentes nuevas: tests/test_hash_creation_insert_scope_consolidation.py,2 fallos sinxfail. No debilitar esas expectativas, los tres tests LOW originales ni los 93 IDs anteriores. Corrección próxima acotada: separar nombres de campos del struct de parámetros C; representar parámetros/locals de cada frame helper/caller con tipo y alcance correctos, incluido const. Verificar exportación pedagógica, UI y retorno/entrada sin confundir scopes, contra observador independiente. No reescribir semántica H1 ni C/H.

## Pruebas y recursos sin doble conteo

Se enumeraron93IDs previos y todos son únicos;93pasados del checkpoint MEDIUM se conservan. Hay2IDs nuevos rojos:95IDs actuales, NO una nueva ejecución global95 ni95aprobados. No sumar distintas corridas de las mismas pruebas. Las34 operaciones/oráculo anterior,20operacionesUI y25fallos de caller son evidencias con solapamiento y unidades diferentes, no una suma de cobertura.

Medición nueva de recursos sobre las mismas34 operaciones pequeñas: pico tracemalloc máximo6094678bytes, respuesta JSONmáxima602919bytes, llamada máxima0.471s bajoinstrumentación. Incluye cliente Flask/JSON/sesión; no RSS ni SLA. Capacidad3/17 solamente; snapshots densos/deepcopy por instrucción replican buckets al menos cuadráticamente en creación. No intentarINT_MAX/memoria enorme/OOM real. Los límites pueden sustentar un futuro cierre finito después de corregir tipos, no dominio entero admitido universal.

## Preservación y continuidad

Producto sin cambios durante LOW; Hash C/H, tres regresiones originales, once kernelsSorting/arnés compartido con hashes preservados. Preview confirmado en127.0.0.1:5051,launcher24164/listener2988,D/run.py,HTTP200,assetHash20261002-hash-medium1; no reinicio. Guardas before/after. Global13/22,docs121/208 sin incremento; RN/Grafos sin cambios.

La instrucción condiciona el siguiente baseline al cierre justificado: no se inició otro bloque ni se repitieron métodos declarados cerrados. Mapa preparado en hash-next-pending-map-after-scope-review-low.md. Siguiente acción primero resolver los dos defectos acotados y revisar LOW, luego get/contains como siguiente baseline no bloqueado de nueve pendientes. No publicar/archivar/consolidar auditoría global por estas comprobaciones.
