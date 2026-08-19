# Delta: c-code-interpreter

## ADDED Requirements

### Requirement: Contrato estable de pasos de traza
El sistema MUST representar cada paso mediante un contrato validable que incluya línea C,
evento semántico, etapa, estado previo, estado posterior, salida de consola y metadatos. El
estado posterior del último paso DEBE coincidir con el estado visual final de la operación.

#### Scenario: paso conforme al contrato
- **GIVEN** una operación con código C y estado inicial válido
- **WHEN** el motor construye su traza
- **THEN** cada paso contiene los campos obligatorios con tipos válidos
- **AND** el último `after_state` equivale al estado final de la operación

#### Scenario: estrategia produce un paso inválido
- **GIVEN** una estrategia que omite un campo obligatorio
- **WHEN** entrega sus pasos al motor
- **THEN** el motor rechaza la traza con un error de contrato identificable en pruebas

### Requirement: Estrategias de traza por familia
El sistema MUST delegar las reglas específicas de secuenciales, árboles, grafos, hash y
ordenamiento en estrategias independientes registradas por estructura. El motor común NO DEBE
contener condicionales de comportamiento propios de una estructura concreta.

#### Scenario: resolución de estrategia
- **GIVEN** una operación sobre `avl`
- **WHEN** se solicita construir su traza
- **THEN** el registro selecciona la estrategia de árboles
- **AND** la fachada pública conserva el esquema de respuesta vigente

#### Scenario: estructura sin estrategia
- **GIVEN** un identificador de estructura no registrado
- **WHEN** se solicita una traza
- **THEN** el sistema devuelve un error controlado o el fallback documentado

### Requirement: Conformidad observable entre C y Python
Para cada TAD soportado, el sistema DE pruebas MUST ejecutar escenarios equivalentes sobre la
implementación C y la implementación Python y comparar su estado observable canónico, resultado
y clasificación de error. Los escenarios DEBEN ser reproducibles mediante una semilla registrada.

#### Scenario: secuencia equivalente
- **GIVEN** una semilla y secuencia de operaciones válidas sobre una pila
- **WHEN** el runner ejecuta la secuencia en C y Python
- **THEN** ambos producen el mismo estado canónico y resultados observables

#### Scenario: divergencia detectada
- **GIVEN** una operación que produce estados canónicos distintos
- **WHEN** se ejecuta la prueba diferencial
- **THEN** la prueba falla e informa TAD, semilla, secuencia y primera divergencia

### Requirement: Verificación de C estándar y memoria
La CI MUST compilar los 13 TAD con C17, advertencias estrictas tratadas como error, y DEBE ejecutar
sus harnesses con AddressSanitizer y UndefinedBehaviorSanitizer en una plataforma compatible.

#### Scenario: advertencia o error de memoria
- **GIVEN** un cambio en un TAD C que genera una advertencia, fuga detectable, acceso inválido o comportamiento indefinido
- **WHEN** se ejecuta el pipeline C
- **THEN** el job falla y publica el diagnóstico correspondiente

#### Scenario: suite C conforme
- **GIVEN** los 13 TAD sin defectos detectables
- **WHEN** se ejecuta el pipeline C
- **THEN** todos compilan y sus harnesses finalizan correctamente

### Requirement: Compatibilidad durante la migración de trazas
Mientras exista código legado, el sistema MUST comparar en pruebas su salida con el nuevo motor
para los casos golden y DEBE conservar el contrato JSON consumido por la interfaz.

#### Scenario: migración de una familia
- **GIVEN** la familia secuencial migrada al nuevo motor
- **WHEN** se ejecutan sus fixtures golden
- **THEN** la semántica de pasos y el estado final permanecen equivalentes
- **AND** la UI recibe los campos públicos que esperaba antes de la migración
