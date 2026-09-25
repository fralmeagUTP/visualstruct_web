# Propuesta: reorganizar el espacio de aprendizaje de Métodos de Ordenamiento

## Why

La pantalla actual reúne preparación de datos, ejemplos, controles de reproducción, práctica, comparación, visualización, código C, explicación y resultados en bloques extensos. Aunque cada algoritmo cuenta con una traza didáctica real, la distribución obliga a desplazarse y dificulta explicar al mismo tiempo la línea C activa y el cambio que sucede en el arreglo.

Esta propuesta adopta el espacio compacto ya establecido en estructuras secuenciales, jerárquicas, grafos y tablas hash. El objetivo es simplificar la interacción sin cambiar los once algoritmos, las rutas, la traza ni el estado canónico.

## Inventario real incluido

El módulo contiene una sola estructura, `sorting_array`, disponible en `/sorting/visualizador` y `/sorting/sorting_array`. Sus APIs actuales permiten crear un arreglo manual, generar uno aleatorio, seleccionar algoritmo, ejecutar, avanzar o retroceder por la traza, consultar estado, reiniciar y comparar dos algoritmos sobre copias aisladas.

Los algoritmos existentes que se conservarán son: Intercambio directo, Selección directa, Inserción directa, Burbuja mejorada, Shell sort, Quick sort, Merge sort, Heap sort, Counting sort, Binsort y Radix sort. La visualización actual ya representa comparaciones, intercambios, pivote, índices ordenados, rango activo, temporales, arreglo auxiliar y métricas; también proporciona una representación específica por estrategia.

## What Changes

- Reorganizar la pantalla con cinco etapas numeradas: 1. **Preparar y controlar la ejecución**; 2. **Visualizar y ejecutar**; 3. **Relacionar con código C**; 4. **Comprender**; 5. **Resultados de la ejecución**.
- Mantener datos manuales/aleatorios y algoritmo en la primera etapa, junto con dos acciones principales: **Ejecutar operación** y **Paso a paso**. Durante una traza, Paso a paso muestra solamente **Anterior** y **Siguiente**; ejecutar desde un frame intermedio completa esa misma traza.
- Mostrar simultáneamente en escritorio el arreglo, su estrategia específica y el código C resaltado. En móvil se conservará la alternativa actual de cambio entre ambas vistas sin perder el cursor ni el estado.
- Conservar representaciones reales por algoritmo: parejas/frontera para burbuja e intercambio, mínimo/prefijo para selección, clave/hueco para inserción y Shell, pivote/subrango para QuickSort, división-fusión/arreglo auxiliar para MergeSort, relaciones padre-hijos para HeapSort, frecuencias/urnas para Counting/Binsort y dígito/buckets para Radix.
- Convertir **Comprender** en un panel plegable que concentre explicación de nivel intermedio, condición, variables, llamadas/recursión, ciclos, punteros/auxiliares, invariante y métricas observadas.
- Convertir **Resultados de la ejecución** en una única sección plegable para consola C, historial, TAD y exportaciones.
- Retirar del flujo visible selector de nivel, Ejemplo guiado, modo práctica/Predecir y comparación visual. La API de comparación y sus copias aisladas se conservarán.
- Aplicar la convención existente de código sin ajuste artificial de líneas: el código conserva su formato y usa desplazamiento horizontal local únicamente cuando sea necesario.

## Out of Scope

- Cambiar la semántica, C interpretado, algoritmos soportados, validaciones de entrada, límite de rango de Counting/Binsort o tratamiento de signos de Radix.
- Crear métodos nuevos, modificar las métricas canónicas o sustituir el código C por pseudocódigo como fuente de verdad.
- Eliminar los endpoints existentes, incluidos `/api/ordenamiento/compare` y la navegación de trazas.
- Añadir pruebas automatizadas; la validación del cambio será manual.

## Success Criteria

Una persona puede preparar el arreglo y método, ejecutar o recorrer la traza, y observar simultáneamente el arreglo/estrategia y la línea C activa. La simplificación no altera el arreglo final, métricas, cursor, consola ni historial; los resultados y explicación pueden abrirse sólo cuando hagan falta.
