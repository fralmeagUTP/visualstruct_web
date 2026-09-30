# Change: Mejorar la didáctica y pedagogía del módulo de ordenamiento

## Why

El módulo ya reproduce los algoritmos y su código C con fidelidad, pero su experiencia se
concentra en observar movimientos y líneas resaltadas. Para funcionar como instrumento de
enseñanza debe ayudar al estudiante a construir modelos mentales sobre control de flujo,
variables, funciones, punteros, recursión, invariantes, complejidad y diferencias entre métodos.

## What Changes

- Se incorporan niveles básico, intermedio y avanzado con divulgación progresiva.
- Se visualizan pila de llamadas, parámetros, retornos, variables y evaluación de condiciones.
- Cada algoritmo obtiene una representación pedagógica específica de su estrategia e invariante.
- Se amplían los controles con pausa, inicio, final, repetición y navegación por progreso.
- Se añaden predicciones y retroalimentación formativa opcional.
- Se permite comparar dos algoritmos sobre la misma entrada.
- Se mejora la representación de negativos, accesibilidad y navegación por teclado.
- Se publican explicaciones, objetivos de aprendizaje y criterios de dominio por algoritmo.

## Out of Scope

- Cambiar la semántica de los once algoritmos C.
- Sustituir el código C por pseudocódigo como fuente de verdad.
- Calificar o identificar estudiantes de forma persistente.
- Ejecutar código C arbitrario proporcionado por usuarios.

## Dependencies

Este cambio depende de `validate-and-harden-sorting-module`, que garantiza fidelidad de estado,
líneas C, funciones auxiliares, historial aleatorio y equivalencia rápido/paso a paso.

## Impact

- Capacidades afectadas: `sorting-visualizer`, `visual-playback-ui`, `c-code-interpreter`,
  `help-system`.
- Componentes principales: plantilla y JavaScript de ordenamiento, modelo de traza, intérprete,
  estilos, ayuda, pruebas de API y pruebas Playwright.
