# Diseño

Geometría incremental de presentación, con posiciones previas y caché acotada de topologías para reproducción atrás/adelante. Nuevos vértices se ubican cerca de sus vecinos evitando solapamientos; aristas nuevas permiten ajuste local acotado, no reinicialización circular. Carga inicial grande usa la misma colocación incremental, sin umbral circular. Pesos, marcas, reciprocidad y orden de respuestas no cambian la geometría de una topología ya vista. El renderer conserva arcos, bucles, etiquetas y resultados algorítmicos. No se promete planaridad ni mínimo global.

No modificar el player antes de reproducción concreta en Desktop. La referencia completa en ayuda y el panel activo son superficies distintas. Comentarios C conservan número de líneas y tokens compilables para proteger índices canónicos; verificar parser/traza aparte.

## Frontera entre edición y reproducción

Cada respuesta de ejecución aceptada o C iniciado reinicia sólo la caché de snapshots, conservando coordenadas actuales como anclas. Rechazo con preserve_session no la altera. El renderer señala explícitamente reproducción, incluidos frames iniciales sin debug; no se cambia cursor, algoritmo ni player. Edición con topología ya vista no restaura snapshots de ejecuciones anteriores.

## Integridad de la fuente

Por solicitud explícita se elimina el comentario de adaptación y se explica GrafoEstado en las líneas existentes. Fuente anterior SHA256 691a85029957cce9cce8dc225fccf970429cfa312301d57d1f5309126e5ac1df; nueva 0ae9866ebb1431dd9680789c8cfa0c0dd06e899bc702d555e052a260a3005b2e. Los tokens no comentario por línea y las 618 líneas físicas se conservan. Actualización puntual de book_source.HASHES para reconocer esta revisión documentada, sin cambiar validadores ni hash del header. Se exige rechazo de cualquier byte alterado posterior. No se cambian fixtures de auditoría.

## Estado vacío en reproducción

El render vacío conserva snapshots cuando pertenece a reproducción, pero representa previous como vacío. Retroceder restaura coordenadas conocidas del último vértice; una nueva ejecución desde vacío empieza con mapa limpio. Un vaciado real fuera de reproducción elimina la caché. La bandera geométrica se propaga también por la rama vacía del renderer. Esta distinción fue detectada en revisión antes de publicar V2, nunca desplegada como corrección aprobada.
