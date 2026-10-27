# Desencolar en Cola de prioridad

La cadena conserva el orden de llegada. Desencolar recorre todos sus nodos y escoge la menor prioridad; la comparación estricta `<` conserva el primer nodo cuando hay empate. El candidato durante la búsqueda corresponde sólo al prefijo recorrido.

Los cuatro locales CPNodo* están indeterminados al declararse. No significan NULL hasta su asignación. `valor` y `prioridad` son dos punteros int* al almacenamiento del caller. El kernel devuelve bool y copia ambos enteros antes de liberar el nodo seleccionado. El kernel no imprime. El main de ejemplo muestra las copias calculadas por C y limpia los nodos restantes.

Desvincular cambia los enlaces, pero el nodo separado sigue vivo hasta free. Después de free su identidad puede aparecer en la historia de la visualización; no es un puntero usable y sus campos actuales no se leen. Raíces y contador del caller sobreviven al retorno; los locales terminan su scope. El contador se decrementa sólo bajo `cantidad > 0`.

Los argumentos NULL y la cola vacía devuelven false sin escribir outputs ni mutar la estructura. Los casos NULL son pruebas privadas del contrato C, sin nuevos controles públicos. El caso contador cero con nodo vivo se conserva como fixture inconsistente, no como cola pública válida.

Ejecutar prepara una traza de esa llamada. Avanzar, retroceder y recargar reutilizan la misma traza; no extraen otro nodo. Las dos vistas muestran el mismo objeto e identidad. La API conserva su resultado escalar de valor; el caller C reproduce valor y prioridad por separado.

La evidencia finita de esta corrección vive en openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-desencolar-instructions-medium. El informe priority-queue-audit-summary.md describe una fotografía histórica, no el estado actual. No se certifican todas las combinaciones, OOM real ni sanitizadores.
