# Propuesta MEDIUM acotada: Hash listings

Pendiente coordinación; no es autorización de implementación. Baseline y contratos vigentes: hash-listings-baseline-checkpoint-low.md, openspec/specs/hash-table/spec.md y H1 de enteros C/capacidad fija/encadenamiento sin rehash. Mantener C/H y los 123 IDs previos.

Mostrar los cuerpos reales th_formatear y helper privado th_append_text, con caller char buffer[2048]. Contrastar declaraciones, guardas, bucket/cadena, llamadas y retornos con observación C independiente; scopes propios, alias const TablaHash*, char*, size_t* a usado, máscaras de bytes, terminación, contador y truncamiento. va_list y vsnprintf se modelan opacos en esta frontera finita; no prometer intérprete libc/ABI universal.

Conservar la distinción entre arrays API de pares completos y texto C formateado. No inventar funciones exportadas keys/values/items ni obtener arrays completos de un buffer truncado. Resolver explícitamente la presentación del texto C frente a la proyección API; si caller calcula proyecciones, usar recorrido de campos públicos existentes y etiquetarlo como código caller, sin API nueva.

Restituir cronología de las seis consultas repetidas y recarga mediante journal existente y caller con resultados computados por C, conservando historial de mutaciones. No introducir umbrales, rehash, contratos normativos nuevos ni cambios de capacidad. Cualquier decisión semántica distinta vuelve a coordinación.

Validar los ocho IDs de baseline, regresión previa pertinente sin sumar solapamientos, 12 proyecciones y 39 llamadas al buffer retenidas, observer de instrucciones C, UI cinco secciones/replay sin redispatch, descarga C17/Doxygen/ownership y recursos finitos. Registrar resultados y límites; volver a LOW para consolidar. No cerrar stats/clear/destroy_table por limpieza del caller.
