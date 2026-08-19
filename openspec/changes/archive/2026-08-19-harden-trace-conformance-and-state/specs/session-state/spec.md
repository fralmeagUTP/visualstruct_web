# Delta: session-state

## MODIFIED Requirements

### Requirement: Reconstrucción de estado por replay
El sistema MUST reconstruir el estado de una estructura desde el checkpoint compatible más
reciente y re-ejecutar en orden únicamente las operaciones posteriores. Si no existe checkpoint,
DEBE reconstruir mediante replay completo. Los pasos que fallen durante el replay DEBEN omitirse
silenciosamente y excluirse del historial válido devuelto.

Un checkpoint DEBE incluir versión de esquema, identificador de estructura, versión del adapter,
posición del historial, estado serializado sin `pickle` y checksum. Un checkpoint corrupto,
incompatible o de otra estructura DEBE descartarse y causar fallback a replay completo.

#### Scenario: estado reconstruido desde checkpoint
- **GIVEN** un historial de 120 operaciones y un checkpoint válido en la operación 100
- **WHEN** se solicita el view model de la estructura
- **THEN** el adapter importa el checkpoint y reproduce únicamente las 20 operaciones posteriores
- **AND** el estado final equivale al replay completo

#### Scenario: estado reconstruido tras recargar
- **GIVEN** un historial válido `[apilar(1), apilar(2)]`
- **WHEN** se solicita el view model de la estructura
- **THEN** el estado visual reconstruido contiene los elementos `[1, 2]`

#### Scenario: historial legado sin checkpoint
- **GIVEN** una sesión creada antes de introducir checkpoints
- **WHEN** se reconstruye la estructura
- **THEN** el sistema reproduce el historial completo sin perder operaciones

#### Scenario: checkpoint incompatible
- **GIVEN** un checkpoint con checksum inválido o versión de adapter distinta
- **WHEN** se reconstruye la estructura
- **THEN** el checkpoint se descarta
- **AND** el sistema usa replay completo y registra el fallback sin datos sensibles

#### Scenario: paso inválido omitido en replay
- **GIVEN** un historial que contiene un paso con payload que ahora falla
- **WHEN** se reconstruye el adapter
- **THEN** el paso inválido se omite y el historial devuelto solo contiene pasos válidos

## ADDED Requirements

### Requirement: Creación periódica de checkpoints
El sistema MUST crear un checkpoint después de un número configurable de operaciones mutantes,
con valor inicial de 50, y DEBE conservar como máximo el número de checkpoints configurado por
estructura.

#### Scenario: intervalo alcanzado
- **GIVEN** intervalo de checkpoint igual a 50
- **WHEN** se confirma la operación mutante número 50
- **THEN** el estado validado se serializa como checkpoint en esa posición

#### Scenario: operación de consulta
- **GIVEN** un historial situado una operación antes del intervalo
- **WHEN** se ejecuta una consulta no mutante
- **THEN** no se crea checkpoint ni cambia la posición del historial

### Requirement: Presupuesto de reconstrucción
En el entorno de rendimiento de referencia, la reconstrucción de una estructura con 300
operaciones y checkpoints habilitados DEBE completar con latencia p95 inferior a 200 ms. La CI o
un job periódico MUST registrar el resultado para detectar regresiones.

#### Scenario: historial máximo
- **GIVEN** un conjunto representativo de historiales de 300 operaciones por familia
- **WHEN** se ejecuta el benchmark de reconstrucción
- **THEN** la latencia p95 es menor a 200 ms
- **AND** el reporte incluye familia, operaciones reproducidas y uso de checkpoint
