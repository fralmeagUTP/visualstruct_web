## ADDED Requirements

### Requirement: Salida real del caller de Ordenamiento

El backend DEBE producir la salida ejecutada de las instrucciones reales de impresión del programa/caller de Ordenamiento, conservando su procedencia y sin sintetizarla desde el arreglo visual.

#### Scenario: Main imprime y algoritmo no imprime
- **GIVEN** un main generado con instrucciones reales de impresión y un algoritmo C sin printf
- **WHEN** se ejecuta la operación
- **THEN** la salida coincide con el mismo programa compilado como C17 y se atribuye al caller, sin inventar impresiones del algoritmo.

#### Scenario: Programa no imprime
- **GIVEN** un camino de programa sin instrucciones de impresión ejecutadas
- **WHEN** se ejecuta o consulta su traza
- **THEN** no aparece stdout sintetizado desde sus valores.

### Requirement: Historial y cursor estables

La consulta y reproducción DEBEN conservar stdout y su correspondencia con el cursor sin ejecutar nuevamente el algoritmo ni agregar historial.

#### Scenario: Reproducción y consulta
- **GIVEN** una ejecución terminada con stdout real del caller
- **WHEN** se consulta el estado o se navega atrás y adelante
- **THEN** se conserva la salida correspondiente, los estados y el número de operaciones sin nuevas ejecuciones.
