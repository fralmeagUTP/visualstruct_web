## ADDED Requirements

### Requirement: Reproductor pedagógico con pausa y progreso
El reproductor SHALL soportar pausa real, salto a inicio/final, repetición y selección de frame
mediante progreso, preservando todos los canales pedagógicos asociados al cursor.

#### Scenario: retroceder restaura todos los canales
- **GIVEN** un frame con código, variables, pila, condición, narración y visualización
- **WHEN** se avanza y luego se retrocede
- **THEN** todos los canales recuperan exactamente los valores originales del frame

### Requirement: Diseño adaptable sin pérdida de contexto
La interfaz SHALL mantener accesibles código, visualización y explicación en escritorio, tableta y
móvil sin reiniciar la ejecución al cambiar disposición, orientación o pestaña.

#### Scenario: cambiar orientación en una tableta
- **GIVEN** una ejecución pausada
- **WHEN** cambia la orientación de vertical a horizontal
- **THEN** el cursor y el estado permanecen y los paneles se reorganizan sin ocultar controles esenciales
