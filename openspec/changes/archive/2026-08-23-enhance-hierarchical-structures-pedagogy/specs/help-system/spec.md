## ADDED Requirements

### Requirement: Ayuda pedagógica jerárquica
La ayuda de ABB, AVL, rojo-negro y heap SHALL incluir objetivo, conocimientos previos, estrategia, invariante, memoria, complejidad, errores frecuentes y ejemplos recomendados.

#### Scenario: consultar ayuda AVL
- **WHEN** se abre la ayuda AVL
- **THEN** explica FE, LL/RR/LR/RL, actualización de alturas y errores frecuentes de rotación

### Requirement: Glosario jerárquico contextual
El sistema SHALL definir raíz, hoja, altura, profundidad, subárbol, factor de equilibrio, rotación, recoloreo, black-height, heap y heapify desde la pantalla y la ayuda.

#### Scenario: consultar black-height
- **WHEN** se solicita el término durante una operación rojo-negro
- **THEN** se explica usando los caminos visibles del frame actual

### Requirement: Guía docente jerárquica
El proyecto SHALL publicar una guía con secuencias de clase, preguntas de predicción, ejercicios evaluables, errores esperados y rúbrica de comprensión.

#### Scenario: actividad ABB frente a AVL
- **WHEN** el docente selecciona la actividad comparativa
- **THEN** obtiene entrada común, preguntas, resultados esperados y criterios de evaluación
