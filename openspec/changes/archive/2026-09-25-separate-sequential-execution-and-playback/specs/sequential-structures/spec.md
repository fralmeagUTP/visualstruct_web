## ADDED Requirements

### Requirement: Ejecución explícita por operación secuencial
Las páginas de Pila, Cola, Cola de Prioridad, Lista Enlazada, Lista Circular y
Sublista MUST ofrecer un control **Ejecutar operación**. Cada activación válida
MUST emitir una nueva solicitud de operación contra el estado actual, incluso si
la estructura, operación y datos coinciden con una ejecución anterior.

#### Scenario: apilar el mismo valor dos veces
- **GIVEN** una pila vacía y el valor `7` seleccionado
- **WHEN** el usuario ejecuta `apilar` dos veces mediante **Ejecutar operación**
- **THEN** el estado canónico contiene dos nodos con valor `7`
- **AND** el historial contiene dos operaciones exitosas de `apilar`

#### Scenario: desapilar dos veces no repite una animación
- **GIVEN** una pila con dos elementos
- **WHEN** el usuario ejecuta `desapilar` y después vuelve a ejecutar `desapilar`
- **THEN** cada solicitud actúa sobre el estado resultante de la anterior
- **AND** no se reutiliza la traza de la primera extracción como sustituto de la segunda

### Requirement: Reproducción secuencial sin efectos de dominio
Preparar, Reproducir, Inicio, Anterior, Siguiente, Final y Repetir MUST operar
únicamente sobre una traza ya preparada en el cliente. No DEBEN emitir una
solicitud a `POST /sequential/<structure_id>/operate`, modificar el historial de
sesión ni cambiar el estado canónico del TAD.

#### Scenario: reproducir una operación preparada
- **GIVEN** una ejecución paso a paso ya preparada para una operación de cola
- **WHEN** el usuario pulsa Reproducir, pausa y repite la traza
- **THEN** el número de operaciones registradas no cambia
- **AND** la animación puede navegar sus frames sin ejecutar nuevamente la cola

#### Scenario: no hay traza preparada
- **GIVEN** no existe una traza compatible con la operación y entrada actuales
- **WHEN** el usuario intenta usar un control de reproducción
- **THEN** el sistema no muta el TAD
- **AND** informa que debe ejecutar una operación en modo paso a paso primero

### Requirement: Trazas asociadas a una ejecución concreta
Una traza secuencial MUST asociarse a una revisión única de ejecución, además de
la estructura, operación y entrada. Dos ejecuciones consecutivas con datos
idénticos DEBEN generar trazas distinguibles.

#### Scenario: valores repetidos crean trazas distintas
- **GIVEN** el usuario ejecutó `encolar(4)` una vez
- **WHEN** vuelve a ejecutar `encolar(4)`
- **THEN** la segunda ejecución genera una nueva traza
- **AND** su estado final muestra dos elementos `4`
