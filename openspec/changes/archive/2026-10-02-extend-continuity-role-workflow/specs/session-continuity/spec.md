## ADDED Requirements
### Requirement: Orquestación local por contratos activables
El arnés SHALL recuperar tareas persistidas y aplicar contratos activables de especificaciones, código, calidad independiente, diseño visual y documentación, con coordinador principal y escritura secuencial.
#### Scenario: recuperar sin chat
- **WHEN** una sesión carga configuración y tarea registradas
- **THEN** obtiene objetivo, requisitos, base, propietario, dependencias, entregables, siguiente paso y fuentes vigentes sin inferir tarea desde conversación ausente
#### Scenario: conflicto de escritura
- **WHEN** tareas activas reclaman rutas solapadas o más de un escritor
- **THEN** el gate rechaza ejecución y exige resolver asignaciones
### Requirement: Cierre condicionado por evidencia vigente
El arnés SHALL rechazar trabajo cerrado, decisión pendiente, checkpoint obsoleto, evidencia invalidada, verificación obligatoria fallida/no ejecutada y QA con identidad igual al autor; el cierre SHALL exigir entregables documentales vigentes.
#### Scenario: código cambió después de pruebas
- **WHEN** hashes actuales difieren de las entradas de la evidencia
- **THEN** verify y close rechazan esa evidencia y requieren nueva verificación
#### Scenario: autor intenta autocertificar cierre
- **WHEN** reviewer y author coinciden
- **THEN** close rechaza el cierre aunque las casillas estén marcadas

#### Scenario: configuración del llamador cambia después de captura
- **WHEN** se modifica la configuración anidada del llamador después de evaluate sin serializar ni copiar su resultado
- **THEN** el snapshot conserva valores anteriores y una nueva evaluación con previous rechaza la configuración cambiada

#### Scenario: tarea nueva retoma rutas cerradas
- **WHEN** una tarea de ID nuevo solapa rutas de otra cerrada
- **THEN** before/verify/close requieren una decisión resuelta y aprobada que vincule ambas tareas, propietario, rutas y motivo; un sucesor de alcance nuevo debe declararlo explícitamente

#### Scenario: fecha de evidencia inválida
- **WHEN** observed_at_utc no representa una fecha/hora ISO-8601 válida con zona UTC Z o +00:00
- **THEN** verify y close rechazan la evidencia aunque sus hashes coincidan
