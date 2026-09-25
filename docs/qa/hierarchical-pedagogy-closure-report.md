# Informe de cierre QA: pedagogía de estructuras jerárquicas

## Alcance

Validación de ABB, AVL, árbol rojo-negro y min-heap en modos rápido y paso a paso, niveles Básico/Intermedio/Avanzado, ejemplos guiados, comparación, práctica, teclado, responsividad, exportación y ayuda.

## Antes y después

| Área | Antes | Después |
|---|---|---|
| Causalidad | Visual técnico con contexto parcial | Frame canónico por instrucción C con condición, variables, pila, memoria, retorno e invariante |
| Ajustes | Rotaciones/recoloreos difíciles de justificar | Caso, roles, pivote, secuencia simple y evidencia textual |
| Heap | Arreglo y árbol sin contraste conceptual completo | Índices padre/hijos, región válida y advertencia explícita de prioridad parcial |
| Control | Reproducción, anterior y siguiente | Preparar, reproducir, pausar, inicio, anterior, siguiente, final, repetir y progreso navegable |
| Aprendizaje activo | Sin predicción estructurada | Predicciones, tres niveles de pista, omisión voluntaria, práctica oculta y progreso de sesión |
| Comparación | No disponible | ABB/AVL, AVL/RN, ABB/heap y recorridos sobre copias aisladas |
| Material docente | Ayuda operativa | Objetivo, estrategia, invariante, memoria, complejidad, errores, glosario, ejercicios y rúbrica |
| Evidencia | Captura global | Captura JPG y resumen JSON de ejecución/aprendizaje |

## Resultados automatizados

- Suite Python sin E2E/performance: **848 aprobadas**, 22 excluidas por marcador.
- Playwright completo: **20 aprobadas**.
- Cobertura: gate global `>= 83 %` y cuatro componentes críticos `>= 85 %`, aprobado.
- C17 estricto con `-Wall -Wextra -Wpedantic -Werror`: aprobado para ABB, AVL, rojo-negro y heap.
- ASan y UBSan: aprobados en Linux/GCC 14 mediante contenedor local; el repositorio se montó en solo lectura.
- JavaScript: comprobación sintáctica aprobada.
- OpenSpec: validación estricta aprobada.

Durante la primera suite apareció un bloqueo temporal de Windows al eliminar `graph_harness.exe`; el caso aislado aprobó inmediatamente y la repetición completa finalizó con 848/848 pruebas aprobadas.

## Accesibilidad y usabilidad

- Flujo completo operable con teclado: flechas, Inicio, Fin y Espacio.
- Foco visible reforzado en controles del laboratorio.
- Regiones dinámicas con `aria-live`; botones de exportación con nombre accesible.
- Color acompañado de nombres, símbolos y reglas textuales.
- `prefers-reduced-motion` reduce transiciones y velocidad de reproducción.
- Diseño comparativo y paneles jerárquicos se apilan en pantallas estrechas.
- Recorrido de tarea probado: preparar ejemplo, predecir, revelar estado, navegar, comparar y conservar el cursor al cambiar nivel/pestaña.

## Veredicto

**Aprobado.** Las fases 1–9 cumplen el contrato didáctico y los gates definidos. No quedan defectos bloqueantes conocidos en el alcance de esta especificación.
