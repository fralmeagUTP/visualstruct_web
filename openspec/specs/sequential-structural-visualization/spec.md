# sequential-structural-visualization Specification

## Purpose
TBD - created by archiving change extend-sequential-structural-visualizations. Update Purpose after archive.
## Requirements
### Requirement: Dos modos conservados por estructura secuencial
Cola, Cola de prioridad, Lista enlazada, Lista circular y Sublista MUST ofrecer
una Vista actual y una Vista de nodos y punteros. Cambiar de modo MUST NOT
mutar el TAD, reiniciar la traza ni modificar el historial. La vista actual
existente MUST permanecer disponible.

#### Scenario: alternar una cola durante una traza
- **WHEN** la persona cambia de Vista actual a Nodos y punteros después de
  preparar una traza de `encolar`
- **THEN** la misma operación y posición de traza permanecen seleccionadas
- **AND** la segunda vista muestra `delante`, `atras`, los nodos y sus enlaces

### Requirement: Diagrama fiel a cada modelo de enlace
La vista estructural MUST nombrar los campos y referencias reales del TAD:
`delante`/`atras` en colas, `HEAD` y `sgte` en lista enlazada, `HEAD`/`TAIL`
y retorno al inicio en lista circular, y padres/hijos en sublista. `NULL` MUST
aparecer solo donde represente una referencia nula real.

#### Scenario: lista circular no termina en NULL
- **WHEN** una lista circular contiene al menos un nodo
- **THEN** el enlace de su último nodo se representa hacia `HEAD`
- **AND** la vista no la presenta como una lista lineal terminada en `NULL`

### Requirement: Animación estructural por operación
Al navegar una traza, la vista de nodos y punteros MUST reflejar solo el estado
y la transición correspondiente al frame ejecutado. Debe mostrar auxiliares,
enlaces, recorridos o nodos liberados cuando la operación C los utilice, y no
debe mostrar esas transiciones en ramas no ejecutadas.

#### Scenario: desencolar deja vacía una cola de un nodo
- **WHEN** se recorre paso a paso `desencolar` sobre una cola con un solo nodo
- **THEN** se muestra el auxiliar que retiene el nodo, la actualización de los
  extremos y la liberación
- **AND** el estado final muestra `delante = NULL` y `atras = NULL`

### Requirement: Sublista conserva un carril independiente por padre
La vista de nodos y punteros de Sublista MUST mostrar cada padre completo en
una fila compacta con `PADRE` y `sgte padre`. La referencia a los hijos MUST
iniciar la rama correspondiente y cada cadena de hijos MUST desplazar sólo su
propio carril cuando no quepa. Una cadena larga MUST NOT ensanchar el lienzo
general, recortar un padre ni superponerse con el código C.

#### Scenario: dos padres con ramas de tamaño diferente
- **WHEN** el primer padre tiene varios hijos y el segundo tiene uno
- **THEN** ambos nodos padre se ven completos sin desplazamiento horizontal
  global de la tarjeta
- **AND** sólo el carril de hijos largo permite desplazamiento horizontal
- **AND** los campos `HIJO`, `sgte`, sus flechas y `NULL` permanecen legibles

### Requirement: Matriz semántica documentada para operaciones visibles
La documentación de cambio MUST definir por operación el estado inicial,
invariantes, campos C y transiciones permitidas para Cola, Cola de prioridad,
Lista enlazada, Lista circular y Sublista. Las consultas MUST quedar definidas
como recorridos sin mutación y las operaciones de limpieza como liberación
progresiva hasta el estado vacío.

#### Scenario: implementar una operación usando la matriz
- **WHEN** se implementa o revisa una operación visible de cualquier TAD del alcance
- **THEN** puede identificarse en la matriz su estado inicial, los punteros a
  exponer y los frames mutantes o de recorrido permitidos
