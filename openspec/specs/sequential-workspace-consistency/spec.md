# sequential-workspace-consistency Specification

## Purpose
TBD - created by archiving change extend-sequential-structural-visualizations. Update Purpose after archive.
## Requirements
### Requirement: Espacio de trabajo secuencial coherente
Las estructuras secuenciales incluidas MUST conservar la secuencia y los
controles aprobados para Pila: preparación/control, visualización, relación con
código C, comprensión y resultados. El código C y el estado visual MUST poder
consultarse en la misma pantalla de escritorio sin una fila nueva de pestañas.

#### Scenario: lectura de código durante una operación de lista
- **WHEN** se elige una operación de Lista enlazada
- **THEN** el selector de función aparece antes del código asociado
- **AND** el checkbox de ocultar documentación aparece junto a su etiqueta

### Requirement: Resultados como panel único plegable
La etapa Resultados de la ejecución MUST tener un botón Ocultar/Mostrar que
pliegue o despliegue en conjunto exportaciones, Consola C, seguimiento y
Estructura del TAD. Su encabezado y botón MUST permanecer visibles.

#### Scenario: ocultar resultados de una sublista
- **WHEN** se pulsa Ocultar en Resultados de la ejecución de Sublista
- **THEN** no quedan visibles por fuera de la etapa Consola C, seguimiento,
  exportaciones ni estructura del TAD
- **AND** al pulsar Mostrar reaparecen todos los elementos

### Requirement: Estructura del TAD siempre abierta dentro de resultados
Dentro de una etapa de resultados desplegada, Estructura del TAD MUST mostrarse
como contenido estático completo sin un control de flecha que permita cerrarla.

#### Scenario: abrir resultados de Cola de prioridad
- **WHEN** se despliega Resultados de la ejecución
- **THEN** se muestra el registro de estructura C de Cola de prioridad
- **AND** no existe un `summary` o control individual para plegarlo
