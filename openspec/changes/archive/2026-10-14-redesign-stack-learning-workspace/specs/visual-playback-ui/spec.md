## ADDED Requirements

### Requirement: Laboratorio compacto de Pila
La página de Pila MUST ofrecer, en escritorio, una zona de trabajo que presente
simultáneamente la preparación de operación, los controles principales, el estado
visual de la pila y el código C activo.

#### Scenario: ejecutar sin recorrer la página
- **GIVEN** una ventana de al menos 1366×768 y la página de Pila recién abierta
- **WHEN** el estudiante escribe un valor y desea ejecutar la operación
- **THEN** puede localizar el dato, Ejecutar operación, el estado de
  la pila y el código C activo sin desplazamiento vertical de la página

### Requirement: Divulgación progresiva de detalles de Pila
Los controles secundarios y el material reflexivo de Pila MUST mantenerse
descubribles y accesibles, pero no deben desplazar los controles principales, la
visualización ni el código C fuera de la vista de trabajo inicial.

#### Scenario: abrir detalles sin perder el flujo principal
- **WHEN** el estudiante abre predicciones, comprensión, comparación o historial
- **THEN** el contenido aparece mediante paneles progresivos
- **AND** los controles principales continúan siendo alcanzables por teclado

### Requirement: Secuencia pedagógica y paneles plegables de Pila
El piloto de Pila MUST usar las cinco etapas canónicas: Preparar y controlar ejecución; Visualizar y ejecutar; Relacionar con código; Comprender; Resultados de ejecución. La preparación, el control y los contenidos adicionales MUST integrarse en esas etapas; no se restaura el diseño anterior de ocho etapas. Los
paneles Predecir, Comprender y Comparar MUST poder mostrarse u ocultarse sin
afectar el estado del TAD, la traza ni los controles principales.

#### Scenario: página de Pila compacta al iniciar
- **WHEN** una persona abre la página de Pila
- **THEN** observa las etapas numeradas sin duplicados ni saltos
- **AND** Predecir, Comprender y Comparar inician plegados
- **AND** puede abrir cualquiera de ellos sin desplazar ni perder la operación en curso
### Requirement: Adaptación y controles pertinentes del piloto Pila
La composición MUST preservar el dato y Ejecutar, el estado y código inicial visibles sin scroll de página en el escritorio evaluado; tableta/móvil MUST ofrecer pestañas accesibles y controles sticky sin superposición. Navegación manual MUST aparecer sólo cuando corresponde al modo y traza preparada. Los widgets retirados MUST NOT reaparecer para cumplir el diseño anterior.

#### Scenario: Modo y paneles preservan ejecución
- **GIVEN** Pila con traza preparada
- **WHEN** cambia el modo o abre/cierra paneles y pestañas
- **THEN** conserva estado, cursor y código, sin nueva operación
- **AND** los tamaños 1366×768, 768×1024, 390×844 y viewport683 documentan el alcance observado; viewport683 no se presenta como certificación de zoom nativo en todos los navegadores

