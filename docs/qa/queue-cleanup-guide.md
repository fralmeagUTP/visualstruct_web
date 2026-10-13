# Cola: limpiar, memoria y caller real

Ejecute limpiar y navegue la misma traza en Vista actual o Nodos y punteros. Las cinco secciones mantienen controles, visualización, código, explicación y resultados. Antes de la primera sentencia no aparecen parámetros/locales ni llamadas futuros; los campos delante/atras pertenecen al struct Cola del llamador.

q es una dirección prestada de struct Cola; aux es struct NodoCola*. aux se declara indeterminado. aux=q->delante captura un nodo vivo; q->delante=aux->sgte adelanta el frente mientras aux continúa vivo y separado. free retira el nodo e invalida aux; campos actuales/máscara quedan inválidos y sólo se conserva historia separada. Los duplicados tienen IDs simbólicos diferentes y estables dentro de esa llamada.

Al liberar el último nodo, atras pasa a indeterminado hasta q->atras=NULL. No se lee ni se sigue ese puntero; while sólo consulta delante válido. q->delante=NULL es una sentencia real aunque ya sea NULL. El retorno void termina el ámbito de q/aux; el struct del llamador sigue vivo con delante y atras NULL. Una cola vacía ejecuta las guardas sin free. qNULL sólo se prueba nativamente y retorna antes del while.

Recargar conserva exactamente la última traza limpiar ligada al historial. Otra mutación o reset descarta ese registro; un rechazo lo preserva. Los controles restauran frames sin otro POST; sigue existiendo reconstrucción histórica normal de la sesión. No es garantía para historiales arbitrariamente largos.

El main real está mostrado en Seguimiento de operaciones, no en una ruta de descarga. Copie sus líneas a main.c y añada #include <stddef.h>, #include <stdio.h> y #include "tad_cola.h". Compile junto con tad_cola.c descargado y su header. Ante malloc NULL, el caller comprueba que atras no avanzó, emite error, libera su cola y retorna1 antes de anunciar éxito. La comparación usa un puntero anterior todavía vivo; no compara punteros retirados. Al finalizar libera propiedad residual. Sus datos deben ser representables como signed32: la generación de caller rechaza otros valores con error/limpieza/retorno1, sin cambiar la API de operaciones.

Verificados cuatro callers reales C17/Doxygen, ownership8alloc8free0vivos y ocho fallos NULL simulados. No OOM real, ABI, sanitizers, sesiones largas ni toda Cola. Checkpoint MEDIUM openspec/changes/audit-local-quality-and-unified-controls/queue-limpiar-instructions-checkpoint-medium.md; revisión LOW pendiente.
