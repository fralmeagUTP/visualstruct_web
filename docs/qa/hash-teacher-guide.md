# Guía docente: laboratorio de tablas hash

1. Inicie con una tabla vacía y pida calcular `clave % capacidad` antes de ejecutar.
2. Use la capacidad 1 para mostrar que una función correcta no garantiza buena distribución si hay pocos buckets.
3. Inserte claves congruentes, por ejemplo `1, 4, 7` en capacidad 3, y solicite explicar la cadena y `siguiente`.
4. Compare búsqueda en cabecera, medio, cola y clave ausente; el estudiante debe justificar el número de comparaciones.
5. Pida anticipar la diferencia entre actualizar una clave y reservar un nodo nuevo con `malloc`.
6. Elimine un nodo intermedio y exija identificar `actual`, `anterior`, el enlace sustituido y el instante de `free`.
7. Diferencie `th_vaciar` de `th_destruir`: el primero conserva el arreglo/capacidad; el segundo libera también buckets y deja `NULL`.
8. Compare las mismas entradas en capacidades 3, 7 y 17. La conclusión debe indicar que una muestra no demuestra complejidad promedio universal.
9. Use modo práctica, pistas y el resumen JSON como evidencia de razonamiento, no solo de respuestas correctas.

Atajos: `Alt+→` siguiente, `Alt+←` anterior, `Alt+Inicio` inicio, `Alt+Fin` final y `Alt+P` pausar.
