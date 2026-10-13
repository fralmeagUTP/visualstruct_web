# Stats Hash: C float y API existente

Notas no normativas del contrato H1 y de los casos registrados; no añade funciones, campos API ni políticas de capacidad.

La API stats mantiene size, capacity y load_factor, con su cociente Python. Metadata redondea seis decimales y el mensaje tres. C devuelve THEstadisticas con capacidad,cantidad,buckets_ocupados,colisiones,factor_carga float. Convierte ambos enteros a float antes de dividir y asigna el resultado a float; el texto C presenta dos decimales. Esas representaciones se muestran por separado: por ejemplo API2/3=0.6666666666666666 y Cfloat=0.6666666865348816.

El caller primero calcula THEstadisticas stats. La estructura interna {0} inicializa sus cinco campos, incluida la ruta de guarda; no se inspecciona padding. Al retornar, sus locales expiran y el caller recibe una copia. El formateador invoca de nuevo th_estadisticas y conserva su propia copia, con scope distinto. El panel muestra int/float,const TablaHash*,THNodo*,size_t,char*,scopes y máscaras semánticas de campos/bytes.

char texto[512] comienza indeterminado; la guarda de destino/capacidad precede toda escritura. destino[0] escribe terminador inicial y snprintf escribe prefijo/terminador acotados. La cola indeterminada no se lee. Tabla destruida/NULL produce Tabla no inicializada. El kernel no usa printf; el main real imprime resultados C, proyección API calculada en C con double y texto formateado, por separado. Consultas repetidas permanecen en journal/caller tras recarga; retroceso reproduce frames sin redispatch.

Evidencia finita: openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-stats-instructions-medium. Cuatro fixtures,27buffers/guardas,ocho observaciones API/UI; observerC original y cuatro probes aritméticos aislados de conversión float (no tablas gigantes ni nuevos casos de método). Máscaras describen inicialización C, no bytes físicos del stack/ABI.

Se verificó host nativo binary32/double53 para esos casos; no ABI alternativo,modo de redondeo no estándar,errores snprintf,capacidades arbitrarias,OOMreal/sanitizadores ni campaña global. Revisión LOW pendiente antes de cerrar stats. clear/destroy_table no se cierran por cleanup del caller.
