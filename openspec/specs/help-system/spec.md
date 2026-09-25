# help-system Specification

## Purpose

Sistema de ayuda didáctica: manual de usuario, páginas de ayuda por módulo y por
estructura, enriquecidas con el código C real del TAD, introducciones descriptivas
y explicaciones por método.
## Requirements
### Requirement: Manual de usuario
El sistema MUST responder `GET /help/manual` renderizando el manual didáctico
completo de la aplicación.

#### Scenario: acceso al manual
- **WHEN** un cliente hace `GET /help/manual`
- **THEN** responde `200` con la página del manual

### Requirement: Índices de ayuda por módulo
El sistema MUST responder páginas de ayuda por módulo en `GET /help/sequential`,
`GET /help/hierarchical`, `GET /help/graph`, `GET /help/hash` y `GET /help/sorting`,
cada una con la descripción del módulo y el listado de sus estructuras.

#### Scenario: índice de ayuda secuencial
- **WHEN** un cliente hace `GET /help/sequential`
- **THEN** responde `200` con la ayuda del módulo y sus 6 estructuras enlazadas

### Requirement: Ayuda por estructura enriquecida con código C
El sistema MUST responder `GET /help/<modulo>/<structure_id>` con una página que
incluya: introducción del TAD, descripción combinada (summary + introducción),
bloque de estructura C (`c_structure_code`), lista de métodos con explicación,
snippet C y símbolo representativo, e indicador `c_available`.

#### Scenario: ayuda de pila con código real
- **WHEN** un cliente hace `GET /help/sequential/stack`
- **THEN** la página muestra `c_available=true`, la estructura C de la pila y los
  métodos con sus snippets de `tad_pila.c`

#### Scenario: estructura sin datos C
- **GIVEN** una estructura sin mapeo en `docs/tads_C`
- **WHEN** se solicita su página de ayuda
- **THEN** muestra `c_available=false` con el placeholder de estructura no documentada

### Requirement: Introducciones y explicaciones didácticas
El sistema MUST proveer una introducción específica por TAD y una explicación por
método; cuando falte una explicación específica, MUST generar una genérica que
indique que el método debe interpretarse respetando el flujo real del código C.

#### Scenario: explicación conocida
- **WHEN** se muestra el método `apilar` en la ayuda
- **THEN** la explicación describe la reserva del nodo auxiliar y la actualización del tope

#### Scenario: explicación genérica de respaldo
- **GIVEN** un método sin explicación registrada
- **WHEN** se muestra en la ayuda
- **THEN** aparece el texto genérico de interpretación del flujo de control

### Requirement: Símbolos C en la lista de operaciones
La ayuda MUST mostrar las operaciones soportadas usando el símbolo C real extraído
del snippet (p. ej. `pila_apilar`) cuando sea posible extraerlo, y el nombre de la
operación en caso contrario.

#### Scenario: operación mostrada con símbolo C
- **WHEN** se lista `apilar` en la ayuda de `stack`
- **THEN** la etiqueta visible es `pila_apilar`

#### Scenario: operación sin símbolo extraíble
- **GIVEN** una operación cuyo snippet no tiene firma C identificable
- **WHEN** se muestra en la ayuda
- **THEN** se usa el nombre de la operación original

### Requirement: Cobertura de ayuda para todos los módulos
Cada módulo (secuencial, jerárquico, grafos, hash y ordenamiento) MUST tener página
de ayuda de módulo y páginas de ayuda por cada estructura registrada en su servicio
de estructuras correspondiente.

#### Scenario: ayuda de ordenamiento
- **WHEN** un cliente hace `GET /help/sorting/sorting_array`
- **THEN** responde `200` con el TAD de ordenamiento, sus 11 algoritmos y snippets C

### Requirement: Descarga de fuente canónica por TAD
Cada ayuda específica MUST ofrecer la descarga del archivo `.c` canónico completo del TAD mostrado y de su encabezado `.h` asociado. La descarga MUST corresponder a un activo existente y permitido de `docs/tads_C`.

#### Scenario: descargar el código de una Cola

- **WHEN** una persona abre la ayuda específica de Cola
- **THEN** encuentra las acciones para descargar `tad_cola.c` y `tad_cola.h`
- **AND** cada archivo descargado coincide con su fuente canónica

### Requirement: Dependencias transparentes
La ayuda MUST informar toda dependencia de otro TAD necesaria para interpretar o compilar el archivo principal.

#### Scenario: descargar Grafo

- **WHEN** una persona abre la ayuda del Grafo
- **THEN** ve que los recorridos requieren el TAD Cola
- **AND** puede llegar a la ayuda de Cola para obtener sus fuentes

### Requirement: Descargas restringidas
El servicio MUST resolver descargas mediante una lista permitida de identificadores de TAD y tipos `source` o `header`; MUST NOT construir rutas desde valores arbitrarios de la solicitud.

#### Scenario: solicitar un archivo no permitido

- **WHEN** se solicita un identificador o tipo de archivo fuera de la lista permitida
- **THEN** el servidor responde 404

### Requirement: Ayuda coherente con el flujo actual
El Manual y las portadas de los módulos MUST guiar por elegir el módulo, preparar datos, ejecutar o recorrer por pasos, observar código y resultado, y consultar fuentes; MUST NOT exigir controles que no son universales en la interfaz vigente.

#### Scenario: abrir el Manual

- **WHEN** una persona abre el Manual de uso
- **THEN** puede ubicar el flujo general y enlaces a los cinco módulos
- **AND** entiende que los nombres concretos de controles pueden variar según el módulo
