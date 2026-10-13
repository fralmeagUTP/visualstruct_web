## MODIFIED Requirements

### Requirement: Modo intérprete conmutado
Todos los módulos MUST ofrecer **Paso a paso**. Activado, Ejecutar operación obtiene una ejecución y prepara su traza para navegación manual. Desactivado, muestra el resultado final y OCULTA Paso anterior/Siguiente paso del layout y de tabulación.
#### Scenario: modo rápido deshabilita navegación
- **GIVEN** Paso a paso desactivado
- **WHEN** se ejecuta una operación
- **THEN** aparece el resultado final y ambos botones de navegación están ocultos.
#### Scenario: modo interpretado habilita navegación
- **GIVEN** Paso a paso activado y traza válida
- **WHEN** se pulsa Siguiente paso o Paso anterior
- **THEN** se cambia solo la vista de la misma traza, con límites deshabilitados y sin mutar historial ni backend.
#### Scenario: Sin traza y extremos
- **GIVEN** Paso a paso activado
- **WHEN** no hay traza o se alcanza un extremo
- **THEN** ambos botones están visibles pero deshabilitados sin traza; en inicio se deshabilita anterior y en final siguiente, con estado comprensible.
#### Scenario: Cambiar modo tras ejecutar
- **WHEN** se desactiva Paso a paso durante una traza
- **THEN** se presenta su resultado final sin nueva operación; la reactivación conserva la traza disponible.

### Requirement: Disposición de controles de simulación
Todos los TAD MUST integrar selección de método y captura de datos con controles claros pertinentes a operación, estado y modo. Pila aporta cuatro controles visibles de referencia: Ejecutar operación, Cerrar paso a paso, Paso anterior y Siguiente paso. La activación/cierre del modo y la ejecución deben ser comprensibles; Paso anterior/Siguiente paso aparecen solo en modo activo. Otros TAD pueden requerir cinco controles u otros propios: cada excepción MUST justificarse y probarse por estado. No se impone conteo fijo ni se elimina una capacidad por el número de botones en fuente. Pila sirve como referencia evaluada, sin replicar defectos.
#### Scenario: Operación repetida
- **WHEN** se ejecuta apilar dos veces con el mismo valor
- **THEN** ocurren dos operaciones reales y aparecen dos nodos; navegar pasos no ejecuta otra inserción.
#### Scenario: Uniformidad entre módulos
- **WHEN** se abre cualquier estructura, algoritmo o fase de grafo
- **THEN** selección y campos específicos siguen disponibles con contrato comprensible, solo controles pertinentes y excepciones documentadas; controles propios necesarios no se eliminan por una regla numérica.

#### Scenario: orden de botones en pila
- **WHEN** se renderiza Pila y se cambia el modo de ejecución
- **THEN** Ejecutar operación, Cerrar paso a paso, Paso anterior y Siguiente paso siguen el contrato de pertinencia y visibilidad aprobado; no se exige la antigua disposición Reproducir/Reiniciar de dos filas

## ADDED Requirements

### Requirement: Menú superior uniforme sin scroll horizontal
Todas las estructuras MUST usar el mismo menú, orden, herramientas y criterio responsive. Se MUST corregir el desbordamiento, no esconder la barra dejando contenido inaccesible.
#### Scenario: Escritorio y viewport estrecho
- **WHEN** se inspeccionan todos los módulos a 1366×768, 1920×1080, 768×1024 y 390×844
- **THEN** el menú usa reflujo natural a nuevas filas con orden y estilo uniformes, no requiere desplazamiento horizontal, todos los destinos son accesibles por teclado y no provoca overflow horizontal del documento; Pila cumple el mismo criterio. No se permite resolverlo ocultando la barra o recortando enlaces.

### Requirement: Cinco etapas pedagógicas uniformes
Todos los 13 TAD y los métodos de Ordenamiento MUST usar exactamente estas etapas numeradas y ordenadas: 1 Preparar y controlar ejecución; 2 Visualizar y ejecutar; 3 Relacionar con código; 4 Comprender; 5 Resultados de ejecución. Preparación/control MUST quedar integrados. Contenido adicional se conserva dentro de las etapas pertinentes; excepciones de controles no permiten números/etapas inconsistentes.
#### Scenario: Navegación entre estructuras y algoritmos
- **WHEN** se abre cada TAD, cada fase de Grafos y cada algoritmo de Ordenamiento
- **THEN** las cinco etiquetas/números y su orden coinciden; no aparecen preparación y control como etapas separadas ni numeración duplicada.
