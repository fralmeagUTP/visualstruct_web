# Propuesta: Mejorar la pedagogía de las estructuras secuenciales

## Why

El módulo secuencial representa operaciones sobre pila, cola, cola de prioridad, lista enlazada,
lista circular y sublista, pero todavía presenta la experiencia principalmente como una animación de
operaciones. Para convertirse en un instrumento de enseñanza debe explicar la relación causal entre
la semántica del C, los punteros, la memoria, la rama realmente ejecutada, el cambio visual y el
invariante de cada TAD.

La asociación aproximada entre líneas C y frames visuales puede producir explicaciones falsas. También
faltan progresión por niveles, ejemplos guiados, práctica predictiva, comparación conceptual entre TAD,
controles completos, accesibilidad y material docente.

## What Changes

- Sustituir asociaciones visuales aproximadas por frames canónicos emitidos por el backend.
- Incorporar objetivos, invariantes, condiciones, variables, pila de llamadas, punteros y memoria por frame.
- Reorganizar la pantalla como Preparar, Predecir, Ejecutar, Comprender, Relacionar con C y Reflexionar.
- Ofrecer niveles Básico, Intermedio y Avanzado sobre una única traza causal.
- Crear visualizaciones especializadas para los seis TAD secuenciales.
- Corregir la explicación de cola de prioridad para distinguir orden físico y selección por prioridad.
- Añadir navegación reversible, ejemplos guiados, práctica, comparación, accesibilidad y exportación.
- Ampliar la ayuda y publicar una guía docente y evidencia de QA pedagógica.

## Out of Scope

- Cambiar la semántica pública de los TAD C.
- Añadir estructuras no registradas actualmente en el módulo secuencial.
- Ejecutar código C arbitrario proporcionado por usuarios.
- Persistir calificaciones o información personal fuera de la sesión.

## Dependencies

- Reutiliza el motor común de trazas y reproducción.
- Debe conservar las correcciones cerradas de `remediate-didactic-c-trace-fidelity`.
- No depende de la implementación pedagógica del módulo de ordenamiento, aunque puede reutilizar sus patrones.

## Impact

- Backend: contratos de traza y adaptadores secuenciales.
- Frontend: plantilla, controlador y visualizaciones del módulo secuencial.
- Ayuda: contenido por TAD, glosario y guía docente.
- QA: golden traces, propiedades, C17, E2E, accesibilidad y evaluación de usabilidad.

