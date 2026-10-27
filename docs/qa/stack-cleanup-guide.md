# Pila: limpiar y reproducir la memoria

En Pila, apile valores y ejecute limpiar. Las cinco secciones mantienen controles, visualización, código, explicación y resultados. Avance por sentencia o retroceda en ambas vistas; el cursor reutiliza la traza preparada.

El parámetro p señala el slot de la raíz. aux nace indeterminado; sólo después de aux=*p contiene un nodo vivo. *p=aux->sgte adelanta la raíz mientras ese nodo sigue vivo y separado. free retira el nodo, invalida aux y sus campos actuales; el panel distingue la copia histórica. Nodos con valores iguales conservan identidades diferentes. El retorno termina variables y pila de llamadas; la raíz caller queda viva y NULL.

Recargar conserva la última ejecución limpiar ligada al historial, sin nuevo POST de operación. Otra mutación o reiniciar descarta ese registro; un rechazo lo conserva. Esto usa la reconstrucción histórica existente y no garantiza historiales arbitrariamente largos.

En resultados, Descargar main.c de la sesión genera el caller real usando historial vigente y el TAD original. Compile junto con tad_pila.c y tad_pila.h. La salida se calcula en C. El caller limpia al finalizar y trata malloc NULL sin leer memoria retirada. La exportación requiere valores representables como signed32; un valor fuera de rango se rechaza en la descarga, sin cambiar la operación de la API.

Verificación finita: vacía, un nodo, tres nodos con duplicado y negativo, reinserción y limpiar repetido; NULL de raíz sólo en observer nativo. Checkpoint MEDIUM y evidencia en openspec/changes/audit-local-quality-and-unified-controls/stack-limpiar-instructions-checkpoint-medium.md. Revisión LOW pendiente; no certificación de ABI, OOM real, sesiones largas ni toda Pila.
