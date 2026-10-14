## ADDED Requirements

### Requirement: Descripción exacta de inserción en primera posición
El mensaje de una inserción exitosa MUST describir la rama alcanzada del contrato C canónico; para insertar_elemento con position1 MUST indicar inserción al inicio, independientemente del desplazamiento permitido.

#### Scenario: Primera posición con desplazamiento después
- **GIVEN** lista[1,3] yposition1,relative0,value2.
- **WHEN** insertar_elemento se ejecuta exitosamente.
- **THEN** lista[2,1,3] ymensaje al inicio, sin afirmar después.

#### Scenario: Posición posterior conserva su descripción
- **GIVEN** lista[1,3] yposition2,relative0,value2.
- **WHEN** insertar_elemento se ejecuta exitosamente.
- **THEN** lista[1,3,2] ymensaje después de la posición2.

### Requirement: Fragmento printf de eliminación simple
La traza de eliminar_elemento en lista simple MUST conservar el literal printf ejecutado, incluido el terminador de línea, en el evento correspondiente.

#### Scenario: Eliminación en lista vacía
- **GIVEN** lista simple vacía y eliminación por valor.
- **WHEN** el C alcanza el printf de lista vacía y retorna.
- **THEN** console contiene exactamente un fragmento " Valor no encontrado o lista vacia.\n" en el printf y ningún fragmento nuevo en return.

## MODIFIED Requirements

### Requirement: Operaciones por estructura
El sistema MUST exponer las operaciones registradas vigentes: Pila apilar/desapilar/limpiar; Cola encolar/desencolar/limpiar; Prioridad encolar/desencolar/limpiar y frente como API hidden registrada; listas/sublista según metadata canónica. Invertir de Lista enlazada está retirado por autorización y MUST NOT reaparecer; invertir de Lista circular conserva su contrato. CimaPila/FrenteFinalCola permanecen núcleos privados con rechazo público, sin player ni consulta UI exitosa. Prioridad MUST conservar el orden de llegada y seleccionar el primer mínimo estable sin ordenar físicamente la cadena. Las APIs hidden conservadas MUST distinguirse de opciones del selector.

#### Scenario: encolar con prioridad
- **GIVEN** una cola con entradas de prioridades distintas
- **WHEN** se encola un elemento con prioridad
- **THEN** el nodo se añade según orden de llegada y la selección de frente/desencolar respeta el mínimo estable
- **AND** no se presenta una ordenación de la cadena como ejecución C

#### Scenario: insertar hijo en padre inexistente
- **GIVEN** una sublista sin el padre10
- **WHEN** se ejecuta insertar_hijo con parent10/child1
- **THEN** el rechazo conserva estructura e historial conforme al contrato C y no inventa una inserción

### Requirement: Registro de historial solo en mutaciones
El sistema MUST conservar operaciones reales mutantes y consultas registradas explícitamente por el journal aprobado. Las consultas MUST preservar el estado estructural aunque añadan evidencia cronológica; GET/reconstrucción/replay MUST NOT volver a ejecutar la consulta histórica. Una consulta pública rechazada o no registrada MUST NOT crear entrada exitosa, llamada C ni resultados inventados.

#### Scenario: consulta registrada y recarga
- **GIVEN** una consulta Priorityfrente exitosa registrada por el contrato vigente
- **WHEN** se recarga o reconstruye su historial
- **THEN** mantiene resultado cronológico y estado sin un nuevo dispatch de consulta

#### Scenario: consulta privada no publicada
- **WHEN** se pide CimaPila o FrenteFinalCola por la API pública no registrada
- **THEN** responde rechazo sin journal exitoso ni ejecución C y no se publica una nueva opción para satisfacer el diseño antiguo

#### Scenario: consulta exitosa no muta historial
- **GIVEN** una pila con historial apilar5 y núcleo privado cima
- **WHEN** se evalúa la consulta privada en su harness aceptado
- **THEN** retorna5 sin cambiar estructura ni fabricar una entrada de historial
- **AND** una solicitud pública no registrada permanece rechazada; no se afirma un éxito API o UI
