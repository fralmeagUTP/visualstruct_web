# Propuesta: reorganizar el espacio de aprendizaje de estructuras jerárquicas

## Why

Las pantallas de árboles y montículos reúnen preparación, predicción, controles, visualización, código, comparación y resultados en una secuencia extensa y con numeración duplicada. Esto dificulta explicar simultáneamente qué instrucción C se interpreta y qué cambio ocurre en la estructura.

La experiencia aprobada para las estructuras secuenciales resolvió ese problema con un flujo corto, controles esenciales y resultados agrupados. Este cambio aplica el mismo criterio al módulo jerárquico, sin modificar algoritmos, adaptadores ni trazas canónicas.

## Inventario real incluido

El módulo expone cuatro pantallas bajo `/hierarchical/<structure_id>`:

| Identificador | Pantalla | Operaciones públicas actuales |
|---|---|---|
| `abb` | ABB | insertar, eliminar, buscar, mínimo, máximo, altura, contar hojas, inorden, preorden, postorden, validar, limpiar |
| `avl` | AVL | insertar, eliminar, buscar, mínimo, máximo, altura, inorden, validar, limpiar |
| `red_black` | Rojo-Negro | insertar, eliminar, buscar, inorden, altura, validar, limpiar |
| `binary_heap` | Montículo binario mínimo | insertar, extraer raíz, ver raíz, ver arreglo, limpiar |

También existen el índice `/hierarchical/` y endpoints de operar, reiniciar y comparar. No se inventarán nuevas estructuras ni rutas.

## What Changes

- Reordenar las cuatro pantallas con una numeración única: 1. **Preparar y controlar la ejecución**; 2. **Visualizar y ejecutar**; 3. **Relacionar con código C**; 4. **Comprender**; 5. **Resultados de la ejecución**.
- Mantener juntos operación, entradas y controles esenciales. La ejecución directa y el modo paso a paso serán los controles principales; el modo paso a paso revelará únicamente Anterior y Siguiente cuando sea aplicable.
- Conservar visualización y código C simultáneamente legibles en escritorio; en pantallas estrechas se usará el mecanismo responsive existente sin perder estado ni posición de traza.
- Adaptar la visualización al tipo real: orden y recorridos en ABB, altura y rotaciones en AVL, color y reglas en Rojo-Negro, y arreglo más árbol completo en montículo binario.
- Retirar del flujo principal **Predecir**, **Ejemplo guiado** y **Comparar conceptos**. La comparación de backend no se elimina.
- Fijar el contenido didáctico de estas cuatro pantallas en nivel intermedio, sin selector visible de nivel.
- Convertir **Resultados de la ejecución** en una unidad plegable que agrupe consola C, historial, exportaciones y estructura del TAD, con el TAD siempre abierto cuando el bloque esté visible.

## Out of Scope

- Cambiar operaciones, invariantes, C interpretado, endpoints, adaptadores o semántica de trazas.
- Eliminar la capacidad de comparación del servicio o sus endpoints.
- Extender el rediseño a secuenciales, grafos, hash u ordenamiento.
- Añadir pruebas automatizadas; la validación será manual, conforme a la preferencia establecida para el proyecto.

## Success Criteria

En cada ruta una persona puede elegir una operación, ejecutarla o recorrerla paso a paso, y entender simultáneamente el estado jerárquico y el código C asociado. Los resultados se pueden ocultar y restaurar como una sola unidad, la numeración no se repite y ningún algoritmo cambia de resultado por el rediseño.
