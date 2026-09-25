# Diseño: espacio compacto y sincronizado para Ordenamiento

## Flujo de pantalla

```
1. Preparar y controlar la ejecución
   arreglo manual o aleatorio + algoritmo + Ejecutar operación + Paso a paso
   [Anterior | Siguiente] sólo mientras existe una traza

2. Visualizar y ejecutar       3. Relacionar con código C
   arreglo, estrategia y            funciones, código y línea activa
   leyenda del frame

4. Comprender (plegable)
5. Resultados de la ejecución (plegable)
   consola C + historial + TAD + exportaciones
```

La primera etapa reduce controles redundantes: no expone pausa, inicio, final, repetir, velocidad, barra de progreso o reinicio como acciones principales. **Ejecutar operación** prepara y completa una operación nueva, o continúa hasta el final si el cursor está a mitad de su traza. **Paso a paso** prepara el recorrido y revela Anterior/Siguiente. Los identificadores internos pueden mantenerse si son necesarios para el motor, pero la interfaz visible debe cumplir este contrato.

## Estado y traza

`execution_trace`, `visual_state`, métricas, consola e historial existentes son la fuente de verdad. Cambiar el algoritmo, datos o vista invalida la traza según el comportamiento actual; cambiar entre paneles, abrir/cerrar Comprender o Resultados y alternar en responsive no debe alterar el cursor ni recomputar una entrada aleatoria.

Cada frame conserva la correlación entre `line_index`/`line_text` del C, arreglo, comparación/intercambio, rango, temporales, auxiliar, métricas y estado ordenado. La pantalla no debe mostrar comparaciones, intercambios, pivotes, llamadas recursivas, buckets o valores auxiliares que no estén justificados por el frame.

## Contrato de representación por familia

| Familia o método | Evidencia visible requerida |
|---|---|
| Intercambio y Burbuja | pareja comparada, posible intercambio y frontera/rango activo; Burbuja comunica salida temprana cuando corresponda |
| Selección | prefijo confirmado y mínimo provisional dentro del rango pendiente |
| Inserción y Shell | clave o temporal, hueco/desplazamiento y, para Shell, gap y grupo activo |
| QuickSort | pivote, subrango, índices de partición y llamadas recursivas realmente activas |
| MergeSort | subrango en división/fusión y arreglo auxiliar usado al fusionar |
| HeapSort | arreglo y relaciones padre-hijo, heap activo y sufijo ya ordenado |
| Counting Sort y Binsort | rango/frecuencias o urnas reales; Binsort conserva la delegación real a conteos |
| Radix Sort | dígito o exponente activo, buckets decimales y tratamiento real de positivos/negativos |

Los estados se complementan con texto y leyenda, no sólo color. Los índices ordenados, invariante y métricas observadas permanecen derivados de la traza existente.

## Código C, comprensión y resultados

El área de Código C seguirá la convención compartida de no envolver líneas. El checkbox de documentación permanece junto al encabezado; las funciones se presentan en una franja superior y el bloque de código usa todo el ancho disponible debajo. Si una línea excede el panel, se desplaza localmente sin ensanchar la página ni ocultar la visualización.

**Comprender** inicia plegado y utiliza explicación intermedia fija. Dentro conserva fase, condición, variables, pila de llamadas, ciclos, punteros/auxiliares, invariante, métricas observadas y perfil teórico ya generados por la traza. **Resultados** agrupa consola C, historial, exportaciones y TAD estático; no habrá un `details` separado únicamente para el TAD.

El selector de nivel, ejemplos guiados, práctica/predicción y la comparación visual se retiran de la pantalla. Sus datos o endpoint pueden mantenerse internamente, siempre que no sean visibles ni bloqueen una ejecución.

## Responsive y accesibilidad

- En escritorio, Visualizar y Código C se ven en paralelo con ancho legible; los dos paneles tienen `min-width: 0`.
- En pantallas estrechas, las pestañas existentes alternan visualización y código con `aria-selected` correcto y sin cambiar la traza.
- Arreglos, buckets, arreglos auxiliares, tablas de variables e historial se ajustan o desplazan exclusivamente en su propio carril.
- Los controles principales tienen nombres explícitos, orden de foco lógico y el estado del paso se anuncia de forma accesible.

## Verificación manual planificada

Se revisarán los cinco bloques, el plegado, el código sin wrapping y el responsive. Se ejecutarán manualmente casos representativos de intercambio, selección/inserción, QuickSort o MergeSort, HeapSort, Counting/Binsort y Radix con negativos, comprobando Anterior/Siguiente y ejecución final desde un frame intermedio. No se crearán ni ejecutarán suites automatizadas.
