## ADDED Requirements

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
