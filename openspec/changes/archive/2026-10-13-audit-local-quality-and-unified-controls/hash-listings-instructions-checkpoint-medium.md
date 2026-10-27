# Hash listings MEDIUM checkpoint: consolidación LOW pendiente

Asignación coordination-hash-listings-instructions-medium-20261003; operación hash.keys-values-items-instructions-medium. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Único escritor técnico; sin commit/push/merge/despliegue. Guarda before exit0; after se registra al final con fuentes frescas.

## Cambio y resultado

La fuente de keys/values/items muestra el caller char buffer[2048], th_formatear y helper privado th_append_text extraídos del C real. La traza dedicada respeta declaraciones, guardas, bucles, llamadas/retornos, scopes y tipos const TablaHash*, THNodo*, char*, size_t, size_t*, int y va_list. usado se actualiza por alias; el buffer tiene prefijo inicializado y zona indeterminada explícita que nunca se lee. Declaración de escritos y va_list precede su inicialización; va_end deja args inutilizable y el retorno retira los locales del helper. Los cierres de bloque y el retorno de tabla no inicializada resaltan sus líneas C reales. Nodos se leen sin mutaciones, malloc/free ni printf del kernel. La raíz conserva identidad simbólica por operación.

La API mantiene sus arrays completos y orden bucket/cadena. C escribe texto de tabla completa: no son la misma representación ni se obtiene la proyección API de un buffer truncado. El journal existente registra consultas reales iguales sin alterar historial de mutaciones. Cada main descargado conserva seis llamadas al formateador y calcula seis proyecciones mediante campos públicos C, con limpieza existente en todas las salidas. No hay nuevas funciones exportadas ni cambios de C/H/H1/capacidad/rehash/umbrales.

## Evidencia finita

134 IDs únicos = 123 anteriores + ocho del baseline + tres nuevos; todos pasan (84,19s). Primer pase 133/134 conservado: una aserción nueva confundía last_result/last_operation visuales con tabla C. Corregida para comparar buckets/cantidad/capacidad y verificar actualización de metadatos; no se modificaron los 131 tests previos. Tras ajustes de líneas/memoria pasan 11 IDs focales (33,77s), solapados con 134, sin sumarlos.

Cuatro fixtures originales y las mismas 12 proyecciones API coinciden con C. Los mismos 39 casos de buffer/guardas conservan su baseline. Observer independiente del C original, sólo con hooks QA y sin tocar C/H canónico: 2.953 eventos completos y 352 escrituras/cambios usado coinciden en orden, resultados escritos y prefijos/terminadores. Dos _Generic C17 verifican firmas de formateador/helper. La variante caller QA usa almacenamiento real 4096 y distingue tamaño pasado 0..4096 de la longitud física; no modela char[0] como C válido. C de producción y caller usan char[2048]. Sin UB/OOM intencionales ni lecturas de bytes indeterminados.

UI tres fixtures: 18 consultas, 3.270 frames/3.252 retrocesos, cinco secciones, cero errores JS/POST extra y recarga conserva consultas. Focal final mixed: 1.026/1.020, solapado. UI adicional sobre tabla destruida: una consulta, ocho frames/siete retrocesos y retorno exacto, sin errores/redispatch. No se suman los focos a la cobertura principal. report.json se capturó antes de ajustes menores finales de línea/metadata; native-observer-final.log, regresión focal y UI final documentan esos ajustes.

Cuatro main.c auténticos distintos (HTTP + tres browsers): C17 estricto, Doxygen cero advertencias, 24 líneas de proyección computadas por C coincidentes; 23 alloc/23 free/0 vivos y 23 puntos malloc NULL simulados. Estos callers no cierran clear/destroy_table.

Recursos de las mismas 12 consultas: máximo 44.675.534 bytes de pico tracemalloc Python, JSON 4.126.798 bytes y 5,5346485s con medición activa, incluidos Flask/session/serialización. No son RSS, SLA ni capacidad arbitraria. 56 archivos protegidos coinciden; sólo cambian los seis puntos de integración previstos y nuevo motor/tests/docs propios. Los 123 IDs, C/H, motores cerrados y once Sorting quedan conservados por hashes/regresión pertinente.

## Límites y siguiente paso

Modelo finito de formatos decimales ASCII exitosos; va_list/vsnprintf opacos, sin simulación del ABI/libc ni errores de codificación. Las máscaras expresan inicialización semántica C, no inspección física de bits del stack. Identidades simbólicas no garantizan direcciones numéricas entre procesos. Sanitizadores, capacidades arbitrarias, recursos de sesiones largas y campaña global pendientes; no se inventan pruebas ni cierres.

Hash mantiene cinco de once métodos cerrados hasta consolidación LOW. Pendientes: keys, values, items, stats, clear, destroy_table. Global 13/22, docs121/208 y C1 1/12 no cambian. Guía no normativa docs/qa/hash-listings-guide.md y nota de USER_GUIDE describen contrato existente. El delta ADDED previamente rechazado por auto-review no se creó, reintentó ni reemplazó por nuevas exigencias; razón preservada en evidence/visible-hash-remove-instructions-medium/auto-review-rejection.md.

Siguiente: coordinación LOW debe revisar alcance, tipos/scopes/buffers, caller real, recursos y restricciones antes de cerrar únicamente casos listados de keys/values/items. No implementar stats/clear/destroy desde este checkpoint. Handoff C1 propio: c1-evidence-handoff.json; no se tocó matriz/documentación de su propietario.
