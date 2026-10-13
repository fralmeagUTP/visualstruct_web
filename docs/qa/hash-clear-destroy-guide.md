# Hash: vaciar y destruir por instrucción

Observación finita de `th_vaciar` y `th_destruir` del C canónico, sin nuevos requisitos ni cambios al contrato H1.

`th_vaciar` guarda `siguiente` mientras el nodo sigue vivo, libera `actual` y luego asigna `actual = siguiente`. Entre esas instrucciones, el puntero local y el slot head que refería al nodo son indeterminados: la UI no recorre esa cadena ni los presenta como NULL. Los campos retirados tienen máscara semántica cero; la copia histórica se etiqueta aparte. `siguiente` sólo existe dentro del cuerpo de esa iteración. La cantidad C conserva su valor hasta `tabla->cantidad = 0`; la invariante aparece transitoria durante ese intervalo.

Vaciar conserva el array y la capacidad. Destruir llama al vaciado y después libera el array. Su puntero raíz queda indeterminado hasta la escritura NULL; capacidad y cantidad cambian en stores posteriores. El objeto TablaHash de la pila sigue vivo. Ambas funciones retornan inmediatamente si tabla o buckets es NULL, sin ejecutar stores ni frees.

El replay permite avanzar/retroceder por estos estados sin volver a despachar la operación. El kernel no imprime: los printf pertenecen al main descargado. Las identidades de heap son símbolos de cada operación y no garantizan direcciones físicas entre llamadas.

La evidencia incluye 16 llamadas core, dos caminos de recreación con cuatro observaciones (sus primeras llamadas solapan core) y cuatro guardas directas NULL/tabla cero. El observer C sólo lee objetos vivos; las máscaras de vida son inferencias semánticas, no inspección de padding. No certifica ABI, sanitizadores, capacidad arbitraria, OOM real, sesiones largas ni SLA. El checkpoint MEDIUM queda pendiente de revisión LOW.
