# Listados Hash: texto C y proyecciones API

Notas de verificación finita del contrato H1 existente; no añade requisitos ni funciones C.

keys, values e items devuelven proyecciones API en orden bucket/cadena. El TAD C exporta th_formatear: escribe texto de la tabla completa en un buffer del caller, no devuelve arrays de claves/valores/pares. El caller descargado muestra ambas representaciones por separado; calcula sus proyecciones recorriendo TablaHash/THNodo públicos y conserva consultas iguales repetidas tras recarga.

La sección C muestra char buffer[2048], th_formatear y su helper privado th_append_text. El buffer nace indeterminado; destino[0] escribe el primer terminador. vsnprintf escribe un prefijo acotado y su terminador, devuelve la longitud solicitada y usado avanza o se satura a capacidad. La parte indeterminada del arreglo no se lee. El panel distingue bytes inicializados y alcance de const TablaHash*, char*, size_t*, va_list y escritos. va_list/libc son una frontera opaca; no representa su ABI interna.

La guardia de destino/capacidad precede la escritura. Tabla NULL o sin buckets produce Tabla no inicializada. Los bucles siguen el orden C y dejan de formatear al agotarse el buffer. Un resultado API completo no se obtiene analizando un texto truncado. El kernel no imprime: consola del trace vacía; printf pertenece al main real descargado.

Evidencia: openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-listings-instructions-medium. Cuatro fixtures y 39 combinaciones de buffers/guardas, 12 proyecciones API; eventos de C nativo independientes. Retroceso y recarga reproducen frames retenidos sin repetir consultas. C/H se conservan.

Estos casos no verifican capacidades arbitrarias, errores de codificación libc, todas las plataformas/ABI, sanitizadores ni persistencia de sesiones largas. El cierre de casos requiere consolidación LOW posterior.
