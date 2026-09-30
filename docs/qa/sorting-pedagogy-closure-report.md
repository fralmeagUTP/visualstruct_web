# Informe de cierre: mejora pedagógica del módulo de ordenamiento

## Antes

La pantalla concentraba controles, barras y código, pero no diferenciaba fases de aprendizaje, niveles,
variables, pila, invariantes ni teoría. La navegación era lineal y no existían práctica o comparación.

## Después

- Flujo Preparar–Visualizar–Comprender–Relacionar con C–Reflexionar.
- Tres niveles sobre una traza canónica y reversible.
- Variables, condiciones sustituidas, ciclos, pila, punteros e invariantes por frame.
- Visualizaciones específicas para los once métodos.
- Reproductor navegable, modo práctica y comparador aislado.
- Accesibilidad por teclado, símbolos textuales, anuncios y diseño adaptable.
- Ayuda por algoritmo, guía docente, glosario y exportación de evidencia.

## Evidencia

La evidencia ejecutable reside en las pruebas de contrato de pedagogía, rutas de ordenamiento y escenarios
Playwright.

| Gate | Resultado |
|---|---|
| Contratos pedagógicos y módulo | 174 aprobadas |
| Matriz Playwright de ordenamiento | 6 aprobadas |
| Suite global sin E2E/performance | 807 aprobadas, 17 excluidas por marcador |
| Cobertura | Umbral global ≥83 % y cuatro componentes ≥85 % aprobado |
| C17 estricto de ordenamiento | Aprobado con warnings como error y eventos QA |
| ASan/UBSan | Evidencia Linux previa vigente; no cambió código C. MinGW local carece de `libasan`/`libubsan` y la distribución `docker-desktop` de WSL no incluye GCC/Bash |
| OpenSpec estricta | Aprobada |

## Recomendación posterior

Mantener el job Linux de CI como autoridad para sanitizadores y realizar una evaluación formativa con
estudiantes reales antes de fijar definitivamente densidad de información, tiempos y dificultad de pistas.
