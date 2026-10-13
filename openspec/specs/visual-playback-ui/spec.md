# visual-playback-ui Specification

## Purpose

Define el comportamiento de la capa de presentación (templates + JS/CSS vanilla):
simulación paso a paso sincronizada con el código C, controles de reproducción,
renderizado de estructuras (incluido SVG para árboles y grafos), consola printf y
exportación de la vista como imagen.
## Requirements
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

### Requirement: Resaltado sincronizado código–animación
El resaltado de la línea de código C MUST avanzar sincronizado con la animación del
estado visual en cada paso de la traza.

#### Scenario: línea activa coincide con el estado animado
- **GIVEN** una traza de `apilar` en reproducción
- **WHEN** el paso muestra la creación del nodo `aux`
- **THEN** la línea resaltada es la de creación del nodo en el snippet C

### Requirement: Clasificación de la acción actual en grafos
En el módulo de grafos, `Siguiente paso` MUST avanzar línea a línea y el indicador
`Accion actual` MUST clasificar el paso como `Evaluando condicion` o
`Aplicando cambio`.

#### Scenario: clasificación de paso condicional
- **WHEN** el paso actual corresponde a un `if` del algoritmo
- **THEN** `Accion actual` muestra `Evaluando condicion`

### Requirement: Estado final limpio en secuenciales
En estructuras secuenciales, al finalizar la simulación MUST quedar visible solo la
estructura final, sin bloques temporales `aux`.

#### Scenario: fin de simulación sin auxiliares
- **GIVEN** una simulación de inserción completada
- **WHEN** termina el último paso
- **THEN** la vista muestra únicamente la estructura resultante

### Requirement: Equivalencia de modo rápido en grafos
En grafos, el resultado visual del modo rápido MUST ser equivalente al último paso
del modo interpretado (mismos nodos/aristas resaltados para recorrido, camino
mínimo o MST), y MUST ocultarse los controles de navegación por paso (Anterior,
Siguiente, velocidad, contador y acción actual).

#### Scenario: modo rápido en BFS
- **WHEN** se ejecuta BFS con el intérprete desactivado
- **THEN** el resaltado final coincide con el del último paso interpretado y los
  controles de paso no son visibles

### Requirement: Visibilidad de detalles técnicos
El control global `Mostrar codigo y detalles tecnicos` MUST ubicarse en la fila del
menú superior y MUST alternar la visibilidad del panel de código C, consola e
historial técnico.

#### Scenario: ocultar panel técnico
- **WHEN** el usuario desmarca el control
- **THEN** el panel de código y los detalles técnicos se ocultan de la vista

### Requirement: Paneles didácticos por operación
La UI MUST presentar `Estructura del TAD` (definiciones C), `Codigo C: <Operacion>`
(función asociada a la operación seleccionada) y `Historial` (renderizado didáctico
como `main`), junto con la consola printf de la ejecución.

#### Scenario: cambio de operación actualiza el snippet
- **WHEN** el usuario selecciona otra operación en el panel
- **THEN** el panel de código muestra la función C de esa operación

### Requirement: Exportación de la vista como JPG
El sistema MUST ofrecer un botón global `Exportar JPG` en la fila del menú superior
que descargue el estado visual actual, permitiendo elegir `Calidad` (`Media`,
`Alta`, `Maxima`) y `Escala` (`1x`, `2x`, `3x`).

#### Scenario: exportación con calidad y escala elegidas
- **GIVEN** una estructura con contenido visible
- **WHEN** el usuario exporta con `Calidad=Alta` y `Escala=2x`
- **THEN** se descarga un JPG del área visual con esos parámetros

### Requirement: Renderizado de estructuras
La UI MUST renderizar: listas/pilas/colas como nodos enlazados (la lista circular
con flecha de retorno al primero), árboles y grafos como SVG con aristas y nodos
resaltables (incluyendo color en Rojo-Negro y FE en AVL), heap como árbol más
arreglo, y la tabla hash por buckets.

#### Scenario: lista circular muestra el ciclo
- **WHEN** se renderiza una lista circular no vacía
- **THEN** el último nodo muestra una flecha de regreso al primero

#### Scenario: AVL muestra factor de equilibrio
- **WHEN** se renderiza un AVL
- **THEN** los nodos exhiben su FE/altura y los bordes conectan padre-hijo en SVG

### Requirement: Consola printf y deduplicación visual
La consola C MUST mostrar las salidas printf de la ruta ejecutada y, junto con el
historial técnico, MUST evitar repetir mensajes consecutivos equivalentes para
reducir redundancia visual.

#### Scenario: mensajes consecutivos colapsados
- **WHEN** la ejecución produce el mismo mensaje en pasos consecutivos
- **THEN** la consola no lo repite de forma consecutiva

### Requirement: Escape de contenido dinámico
Todo contenido dinámico insertado en el DOM desde datos de usuario o del servidor
MUST escaparse (p. ej. `escapeHtml`) para prevenir inyección HTML/XSS.

#### Scenario: valor con HTML escapado
- **WHEN** un mensaje o valor contiene `<script>`
- **THEN** se renderiza como texto escapado, nunca como HTML ejecutable

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
