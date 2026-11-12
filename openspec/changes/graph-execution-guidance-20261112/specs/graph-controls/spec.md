## ADDED Requirements
### Requirement: Inicio de una llamada de Grafos
La orientación sin traza DEBE indicar Ejecutar operación, distinguiéndola de navegar la llamada preparada.
#### Scenario: Entrada nueva
- GIVEN una selección sin traza o invalidada por nueva entrada
- WHEN se muestra la orientación
- THEN indica Ejecutar operación; Siguiente no inicia una llamada.
#### Scenario: Navegación preparada
- GIVEN una operación ejecutada en Paso a paso
- WHEN se navega adelante y atrás
- THEN no se repite POST ni se modifica el límite de traza.
