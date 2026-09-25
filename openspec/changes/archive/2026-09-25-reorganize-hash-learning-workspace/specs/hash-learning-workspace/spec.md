## ADDED Requirements

### Requirement: Flujo hash unificado y compacto
Tabla Hash MUST presentar Preparar y controlar, Visualizar y ejecutar, Relacionar con código C, Comprender y Resultados en orden y sin numeración repetida. Ejecutar operación y Paso a paso MUST ser las acciones principales.

#### Scenario: preparar una inserción
- **WHEN** se selecciona Insertar/Actualizar clave-valor
- **THEN** clave, valor y la opción real de fallo de `malloc` se preparan en la primera etapa
- **AND** el modo paso a paso ofrece Anterior/Siguiente durante la traza

### Requirement: Representación fiel del encadenamiento separado
La visualización MUST conservar capacidad fija, función hash, normalización, bucket y cadena canónicos. Inserción, actualización, consulta, eliminación y liberación MUST mostrar sólo enlaces y eventos de memoria del frame real.

#### Scenario: insertar una clave que colisiona
- **WHEN** una clave cae en un bucket ocupado
- **THEN** se muestra cálculo de índice y recorrido de cadena
- **AND** el nodo se actualiza o enlaza según la operación real

### Requirement: Código C vertical y resultados agrupados
Funciones C MUST aparecer sobre código a ancho completo, con checkbox de documentación junto al título. Resultados MUST plegar/restaurar juntos consola, historial, TAD y exportaciones; el TAD MUST ser estático al mostrarse.

#### Scenario: revisar una eliminación
- **WHEN** se abre el código de Eliminar clave y se recorre la traza
- **THEN** la función activa se relaciona con bypass y `free` visuales
- **AND** consola e historial quedan disponibles dentro de Resultados

### Requirement: Overflow contenido por bucket
Las cadenas o direcciones largas MUST ajustarse o desplazarse únicamente dentro de su tarjeta o carril. MUST NOT ensanchar lienzo global ni cubrir código.

#### Scenario: Colisión con una cadena extensa

- **WHEN** una inserción produce una cadena de colisión que supera el ancho disponible del bucket
- **THEN** la cadena se ajusta o se desplaza dentro de ese bucket
- **AND** el código C y los demás buckets conservan su posición y permanecen visibles
