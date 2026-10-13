# Propuesta: rediseñar el espacio de aprendizaje de Pila

## Why

La pantalla actual de Pila presenta preparación, visualización, código C y
controles como etapas verticales. En una resolución de escritorio común, el
estudiante debe desplazarse para ingresar un dato, ejecutar, ver el estado y
relacionarlo con el código. Esa separación rompe la continuidad didáctica y hace
que la interfaz se perciba como una página larga, no como un laboratorio.

## What Changes

- Crear un piloto exclusivo para **Pila** antes de modificar las demás
  estructuras secuenciales.
- Convertir la zona inicial en un espacio de trabajo compacto de tres áreas:
  preparación y controles; estado visual; código C activo.
- Mantener visibles, sin desplazamiento vertical de página en escritorio, la
  entrada de operación, Ejecutar/Reproducir, la pila y el fragmento C relevante.
- Usar desplazamiento interno, compacto y accesible para código largo, funciones,
  controles avanzados e información secundaria.
- Convertir Predicción, detalles técnicos, comparación y reflexión en contenido
  progresivo para no competir con la tarea principal.
- Corregir la secuencia visible de etapas para que no repita ni salte números:
  Preparar, Predecir, Ejecutar y visualizar, Controlar la ejecución, Relacionar
  con C, Comprender, Comparar y Reflexionar.
- Permitir mostrar u ocultar explícitamente Predecir, Comprender y Comparar,
  conservando su estado durante la sesión y sin ocultar la operación principal.
- En móvil y tableta conservar una única columna con controles pegajosos y
  pestañas claras de Estado/Código.
- Validar el piloto con tareas de inserción, extracción, reproducción y lectura
  de código antes de proponer la extensión a Cola, Cola de prioridad, listas y
  sublista.

## Out of Scope

- Aplicar este rediseño a las demás estructuras secuenciales antes de la
  aprobación del piloto de Pila.
- Cambiar algoritmos, trazas, endpoints o semántica C.
- Quitar contenido pedagógico; solo se reorganiza y prioriza.

## Success Criteria

En una ventana de escritorio de 1366×768, una persona puede seleccionar una
operación, ingresar el valor, ejecutar o reproducir, ver la pila y localizar el
código C activo sin desplazar la página. El contenido secundario permanece
descubrible, accesible por teclado y sin ocultar información esencial.
