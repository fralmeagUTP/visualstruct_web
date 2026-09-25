## ADDED Requirements

### Requirement: Controles separados de ejecutar y reproducir en secuenciales
La interfaz de todas las estructuras secuenciales MUST separar visualmente
**Ejecutar operación**, **Preparar** y **Reproducir**. Ejecutar expresa una
mutación nueva; Preparar y Reproducir expresan acciones sobre una traza existente.

#### Scenario: acciones diferenciadas
- **WHEN** se renderiza cualquier página de estructura secuencial
- **THEN** son visibles los controles Ejecutar operación, Preparar y Reproducir
- **AND** sus etiquetas y ayudas permiten distinguir su efecto sobre el TAD

### Requirement: Navegación habilitada solo para trazas preparadas
Los controles de reproducción y navegación MUST permanecer deshabilitados o
producir una orientación no mutante mientras no haya una traza paso a paso
preparada y compatible. El control Ejecutar operación MUST continuar disponible
cuando la entrada sea válida.

#### Scenario: operación nueva invalida la reproducción anterior
- **GIVEN** existe una traza preparada para una inserción
- **WHEN** el usuario cambia la operación o uno de sus datos de entrada
- **THEN** la traza anterior deja de estar disponible para reproducir
- **AND** el estado ya persistido del TAD permanece visible e intacto

### Requirement: Estado canónico visible después de ejecutar
Después de una ejecución exitosa en modo paso a paso, la interfaz MUST mostrar el
estado canónico final del TAD. La carga de la traza no puede dejar visible su
primer frame si este representa el estado anterior a la operación. Preparar o
Reproducir son las acciones que pueden volver a ese frame inicial para fines
didácticos.

#### Scenario: último desapilado deja visible una pila vacía
- **GIVEN** una pila con un único nodo
- **WHEN** el usuario ejecuta `desapilar` en modo paso a paso
- **THEN** la pantalla muestra una pila vacía inmediatamente después de la respuesta exitosa
- **AND** Reproducir puede animar la transición desde el nodo original hasta la pila vacía
