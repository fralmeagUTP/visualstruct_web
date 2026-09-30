# Propuesta: Validación integral de calidad y cobertura funcional de la aplicación

## Why

La aplicación dispone de módulos, operaciones, trazas, controles de reproducción y ayudas didácticas que han evolucionado de forma independiente. Las pruebas actuales cubren partes importantes, pero no existe todavía un plan único, ejecutable y auditable que demuestre que **cada opción expuesta al estudiante** funciona y conserva la semántica del código C que se interpreta.

Sin una matriz centralizada se corre el riesgo de que una ruta, una variante de algoritmo, una acción de UI, un caso límite o un modo de accesibilidad quede sin probar, o que el modo rápido y el modo paso a paso terminen en estados diferentes.

## What Changes

- Definir un inventario versionado de cobertura que se genere desde las rutas, adaptadores, algoritmos y controles realmente registrados por la aplicación.
- Crear una matriz exhaustiva para los módulos secuencial, jerárquico, grafos, hash y ordenamiento; incluye todas sus estructuras, operaciones, fases, algoritmos y opciones visibles.
- Establecer casos normales, límite, inválidos y de regresión para cada operación, así como oráculos de estado, traza, consola, historial y visualización.
- Verificar equivalencia entre código C, backend, traza, historial técnico, consola, estado visual, reproducción rápida y paso a paso.
- Automatizar pruebas API, dominio, integración, Playwright, accesibilidad, seguridad, rendimiento, compatibilidad de navegador y conformidad C17/sanitizers.
- Publicar reportes reproducibles de cobertura funcional y de calidad, con evidencias, hallazgos, severidad y recomendaciones de corrección.
- Convertir la matriz y sus gates en controles CI, con tratamiento explícito de dependencias de infraestructura faltantes.

## Out of Scope

- Corregir defectos funcionales que se encuentren durante esta fase; cada defecto se registrará y se abordará mediante un OpenSpec de remediación.
- Ejecutar código C arbitrario proporcionado por usuarios.
- Certificar navegadores o sistemas operativos no incluidos en la matriz acordada.
- Realizar pruebas de carga de Internet o de infraestructura de producción fuera del entorno controlado.

## Impact

- `tests/`, `tests/golden/`, `tests/conformance/` y scripts QA: nuevos manifiestos, fixtures, pruebas y reportes.
- CI: jobs y artefactos separados por tipo de prueba.
- Documentación QA: catálogo de cobertura, informe de ejecución y backlog trazable de defectos.
- Todos los módulos: se validan sin modificar su contrato como parte de esta especificación.
