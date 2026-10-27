# Hash keys/values/items: cierre LOW de casos finitos

Autorización actual coordination-hash-listings-finite-consolidation-low-20261003. Operación hash.keys-values-items-finite-consolidation-low. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Revisión documental/hashes, sin repetir tests ni implementación cerrada.

Se cierran únicamente keys, values e items para cuatro fixtures (vacío capacidad3; colisiones/duplicados/negativos capacidad3; int32 extremos capacidad1; disperso capacidad7), 12 proyecciones completas en orden bucket/cadena, 39 casos de buffer/guardas, 18 consultas UI registradas y cuatro callers reales. Guardas NULL/tabla vaciada y tamaños0,1,2,8,16,64,128,2048,4096 están registrados. La guarda UI de tabla destruida es adicional y separada.

134 IDs únicos verdes =123 previos+8 baseline+3 nuevos. Los 11 focales y UI1026/1020 se solapan, no se agregan. Observer C2953 eventos/352 escrituras-contador coincide; UI3270/3252 cinco secciones sin redispatch/errores, recarga conserva seis consultas por caller. Cuatro mains C17/Doxygen0, 24 proyecciones computadas C, 23alloc/23free/0vivos y23NULL simulados. Evidencia revisada en visible-hash-listings-instructions-medium y review.json.

Tipos/scopes: root const TablaHash*, THNodo*, char*, size_t/size_t*, int y va_list opaco; alias usado y buffer; locales expirados al retorno/cierre; bytes indeterminados no leídos. Se distingue arreglo físico QA4096 de capacidad pasada, incluido0, y caller C2048. Máscaras semánticas, no lectura física de stack/ABI. API proyecta pares completos; C formatea texto acotado, sin inferir arrays de un texto truncado. No nuevas APIs exportadas ni semántica H1.

Límites: formatos decimales ASCII exitosos; no errores libc/ABI/sanitizadores/arbitrario/sesiones largas. Recursos observados hasta44.675.534bytes Python/4.126.798bytesJSON/5,5346485s instrumentados; no RSS ni SLA. La escala fuera de los fixtures sigue abierta. C/H, 11Sorting y manifiestos de producto/test coinciden. El ADDED rechazado no existe ni fue reintentado; se preserva H1 sin nuevos contratos.

Hash pasa a8/11 métodos cerrados finitamente: create_table,insert,get,contains,remove,keys,values,items. Pendientes stats,clear,destroy_table. No cierre global:13/22,docs121/208,C1 1/12 unchanged. Preview51764/hijo53104 ejecuta run.pyD en5051, identidad y HTTP200 verificados, no tocado.

Siguiente baseline LOW: stats, separado de clear/destroy. No inferir cierre de estos últimos por cleanup de callers. No publicación/commit/push/merge/despliegue.
