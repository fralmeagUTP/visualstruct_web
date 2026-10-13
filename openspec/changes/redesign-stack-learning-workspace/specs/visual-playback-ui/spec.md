## ADDED Requirements

### Requirement: Laboratorio compacto de Pila
La página de Pila MUST ofrecer, en escritorio, una zona de trabajo que presente
simultáneamente la preparación de operación, los controles principales, el estado
visual de la pila y el código C activo.

#### Scenario: ejecutar sin recorrer la página
- **GIVEN** una ventana de al menos 1366×768 y la página de Pila recién abierta
- **WHEN** el estudiante escribe un valor y desea ejecutar la operación
- **THEN** puede localizar el dato, Ejecutar operación, Reproducir, el estado de
  la pila y el código C activo sin desplazamiento vertical de la página

### Requirement: Divulgación progresiva de detalles de Pila
Los controles secundarios y el material reflexivo de Pila MUST mantenerse
descubribles y accesibles, pero no deben desplazar los controles principales, la
visualización ni el código C fuera de la vista de trabajo inicial.

#### Scenario: abrir detalles sin perder el flujo principal
- **WHEN** el estudiante abre predicciones, velocidad, comparación o historial
- **THEN** el contenido aparece mediante paneles progresivos
- **AND** los controles principales continúan siendo alcanzables por teclado

### Requirement: Secuencia pedagógica y paneles plegables de Pila
El piloto de Pila MUST usar una numeración única y ordenada para sus etapas. Los
paneles Predecir, Comprender y Comparar MUST poder mostrarse u ocultarse sin
afectar el estado del TAD, la traza ni los controles principales.

#### Scenario: página de Pila compacta al iniciar
- **WHEN** una persona abre la página de Pila
- **THEN** observa las etapas numeradas sin duplicados ni saltos
- **AND** Predecir, Comprender y Comparar inician plegados
- **AND** puede abrir cualquiera de ellos sin desplazar ni perder la operación en curso
