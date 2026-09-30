# Propuesta: Mejorar la pedagogía de las estructuras jerárquicas

## Why

El módulo jerárquico ya representa ABB, AVL, árbol rojo-negro y montículo binario, e incluye rutas, factores de equilibrio, colores, rotaciones y transiciones. Sin embargo, esos datos aparecen principalmente como información técnica de una simulación. La experiencia todavía no explica de forma continua la relación causal entre comparación, recursión, cambio estructural, ajuste y verificación del invariante.

La pantalla tampoco ofrece progresión por niveles, ejemplos guiados, práctica predictiva, comparación entre estructuras, pila recursiva, controles completos ni material docente suficiente. Esto dificulta que un estudiante comprenda por qué ocurre una rotación, un recoloreo o un intercambio de heap, aunque pueda observar el resultado final.

## What Changes

- Emitir frames jerárquicos canónicos que vinculen cada línea C ejecutada con estado, recursión, memoria, decisión e invariante.
- Reorganizar la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.
- Añadir niveles Básico, Intermedio y Avanzado sobre una misma traza.
- Explicar casos de eliminación ABB, rotaciones AVL, casos de fix-up rojo-negro y ajustes ascendentes/descendentes del heap.
- Mostrar invariantes con evidencia por nodo y por camino, sin depender únicamente del color.
- Incorporar ejemplos guiados, predicciones, pistas, práctica, navegación completa y progreso conceptual de sesión.
- Comparar ABB/AVL, AVL/rojo-negro, ABB/heap y representaciones de recorridos.
- Ampliar ayuda, glosario, guía docente, accesibilidad y exportación de evidencia.
- Cerrar con contratos, golden traces, propiedades, Playwright, cobertura, C17, ASan y UBSan.

## Out of Scope

- Cambiar la semántica pública de los TAD C existentes.
- Añadir B-tree, trie u otras estructuras no registradas.
- Ejecutar código C arbitrario proporcionado por el usuario.
- Persistir calificaciones o datos personales fuera de la sesión.
- Presentar un heap como árbol de búsqueda o como arreglo totalmente ordenado.

## Dependencies

- Reutiliza el motor común de trazas y reproducción.
- Conserva las correcciones de fidelidad causal ya cerradas.
- Puede reutilizar patrones pedagógicos de ordenamiento y estructuras secuenciales, sin compartir estado mutable entre módulos.

## Impact

- Backend: contrato de frames jerárquicos, invariantes y metadatos de recursión/ajuste.
- Frontend: plantilla, controlador, visualizaciones y comparador jerárquico.
- Ayuda: contenido por TAD, glosario y guía docente.
- QA: golden traces, propiedades estructurales, equivalencia de modos, accesibilidad y usabilidad.
