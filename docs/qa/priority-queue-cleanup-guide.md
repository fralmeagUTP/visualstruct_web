# Prioridad limpiar: guía de lectura por instrucción

Fuente vigente: `docs/tads_C/tad_cola_prioridad.c/.h`; cp_vaciar no ordena por prioridad. El struct ColaPrioridad pertenece al llamador; sus campos delante/atras/cantidad siguen vivos al retornar. El parámetro cola y los punteros CPNodo *aux/*next pertenecen al alcance local.

En declaración aux y next no están inicializados. aux=cola->delante toma el primer nodo. Cada vuelta guarda next=aux->sgte antes de cambiar delante; aux conserva la identidad original del nodo desconectado y éste vive hasta free. El último atras se pone NULL antes de free. Después de free, aux es indeterminado y no se sigue; la UI separa campos históricos de campos actuales con máscara0. next sigue apuntando al sucesor vivo o NULL. cantidad decrece después de free; su valor temporal no es el largo de la cadena alcanzable entre unlink y decrement. aux=next vuelve a asignar puntero válido antes de evaluar while.

El retorno void termina sólo el alcance local; el struct caller queda vacío e inicializado. El frame inicial muestra antes de llamar, sin locales futuros ni línea ejecutada. Ambas vistas muestran la misma ejecución; sgte aparece en la vista enlazada. Retroceso restaura exactamente el frame almacenado. La traza preparada de limpiar se conserva al recargar mientras corresponda al mismo historial, y se invalida tras otra operación exitosa o reset.

El main real de historial usa cp_encolar con su retorno int vigente: ante0 informa el fallo, limpia su propiedad y retorna1 antes de anunciar éxito. Dos limpiezas registradas permanecen como dos llamadas; finalcleanup también cubre propiedad del caller. Su documentación Doxygen se verifica por símbolos XML, además de warnings.

Alcance de QA: casos finitos consistentes vacío/uno/multi FIFO con duplicados/prioridades heterogéneas/negativos, repetición y reinserción; NULL del parámetro sólo en observador seguro y motor directo. Fallos malloc NULL simulados, no OOM real. No certifica ABI, padding, profundidad/historial arbitrarios ni toda ColaPrioridad. Ver evidencia y checkpoint del cambio audit-local-quality-and-unified-controls; no elevar contadores globales por esta guía.
