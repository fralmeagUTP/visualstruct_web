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
Los TAD MUST integrar selección de método, datos y controles pertinentes al estado y modo. MUST conservar Ejecutar operación y la navegación manual según los requisitos de modo intérprete y cinco etapas. En secuenciales y jerárquicos, los antiguos widgets de repetición automática y sliders de posición y velocidad están retirados. La comparación jerárquica MUST usar botones manuales y conservar su función educativa. Otros controles propios y sus obligaciones pendientes no quedan retirados por inferencia.

#### Scenario: retiro trazable
- **WHEN** se revisa el inventario de controles
- **THEN** se conservan los IDs históricos, las siete retiradas directas y la pausa jerárquica dependiente retirada se clasifican separadas de PASS y los dos botones nuevos de comparación se añaden con evidencia focal.

#### Scenario: Operación repetida
- **WHEN** se ejecuta apilar dos veces con el mismo valor
- **THEN** ocurren dos operaciones reales y aparecen dos nodos; navegar pasos no ejecuta otra inserción

#### Scenario: Uniformidad entre módulos
- **WHEN** se abre cualquier estructura, algoritmo o fase de grafo
- **THEN** selección y campos específicos siguen disponibles con controles pertinentes y excepciones documentadas
- **AND** conservar las cinco etapas no elimina capacidades necesarias por un conteo de botones

#### Scenario: orden de botones en pila
- **WHEN** se renderiza Pila y se cambia el modo de ejecución
- **THEN** Ejecutar operación, Cerrar paso a paso, Paso anterior y Siguiente paso siguen la pertinencia y visibilidad aprobadas, sin volver a la disposición Reproducir/Reiniciar de dos filas

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
La interfaz secuencial MUST distinguir Ejecutar operación de la navegación manual de una traza preparada. La ejecución prepara la traza; Paso anterior y Siguiente paso MUST navegarla sin mutar historial. Los widgets antiguos de repetición automática y sliders de posición y velocidad quedan retirados por autorización documentada; retirar no equivale a aprobar una prueba.

#### Scenario: navegación manual conservada
- **GIVEN** una traza preparada en modo paso a paso
- **WHEN** se avanza y retrocede
- **THEN** se muestran snapshots de la misma ejecución sin nueva petición de operación y sin repetición automática ni sliders antiguos.

#### Scenario: acciones diferenciadas
- **WHEN** se renderiza una estructura secuencial y se dispone de una traza
- **THEN** Ejecutar operación expresa una llamada nueva y los controles manuales pertinentes navegan la misma traza
- **AND** las etiquetas y ayudas distinguen esos efectos sin exigir los widgets antiguos Preparar/Reproducir siempre visibles

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

### Requirement: Laboratorio compacto de Pila
La página de Pila MUST ofrecer, en escritorio, una zona de trabajo que presente
simultáneamente la preparación de operación, los controles principales, el estado
visual de la pila y el código C activo.

#### Scenario: ejecutar sin recorrer la página
- **GIVEN** una ventana de al menos 1366×768 y la página de Pila recién abierta
- **WHEN** el estudiante escribe un valor y desea ejecutar la operación
- **THEN** puede localizar el dato, Ejecutar operación, el estado de
  la pila y el código C activo sin desplazamiento vertical de la página

### Requirement: Divulgación progresiva de detalles de Pila
Los controles secundarios y el material reflexivo de Pila MUST mantenerse
descubribles y accesibles, pero no deben desplazar los controles principales, la
visualización ni el código C fuera de la vista de trabajo inicial.

#### Scenario: abrir detalles sin perder el flujo principal
- **WHEN** el estudiante abre predicciones, comprensión, comparación o historial
- **THEN** el contenido aparece mediante paneles progresivos
- **AND** los controles principales continúan siendo alcanzables por teclado

### Requirement: Secuencia pedagógica y paneles plegables de Pila
El piloto de Pila MUST usar las cinco etapas canónicas: Preparar y controlar ejecución; Visualizar y ejecutar; Relacionar con código; Comprender; Resultados de ejecución. La preparación, el control y los contenidos adicionales MUST integrarse en esas etapas; no se restaura el diseño anterior de ocho etapas. Los
paneles Predecir, Comprender y Comparar MUST poder mostrarse u ocultarse sin
afectar el estado del TAD, la traza ni los controles principales.

#### Scenario: página de Pila compacta al iniciar
- **WHEN** una persona abre la página de Pila
- **THEN** observa las etapas numeradas sin duplicados ni saltos
- **AND** Predecir, Comprender y Comparar inician plegados
- **AND** puede abrir cualquiera de ellos sin desplazar ni perder la operación en curso

### Requirement: Adaptación y controles pertinentes del piloto Pila
La composición MUST preservar el dato y Ejecutar, el estado y código inicial visibles sin scroll de página en el escritorio evaluado; tableta/móvil MUST ofrecer pestañas accesibles y controles sticky sin superposición. Navegación manual MUST aparecer sólo cuando corresponde al modo y traza preparada. Los widgets retirados MUST NOT reaparecer para cumplir el diseño anterior.

#### Scenario: Modo y paneles preservan ejecución
- **GIVEN** Pila con traza preparada
- **WHEN** cambia el modo o abre/cierra paneles y pestañas
- **THEN** conserva estado, cursor y código, sin nueva operación
- **AND** los tamaños 1366×768, 768×1024, 390×844 y viewport683 documentan el alcance observado; viewport683 no se presenta como certificación de zoom nativo en todos los navegadores

### Requirement: Pestañas accesibles del piloto Pila
En Pila, las pestañas móviles Estado/Código MUST identificar tablist, tab y tabpanel, MUST conservar una sola pestaña en el orden Tab y MUST permitir flechas, Inicio y Fin con selección y foco coherentes sin cambiar el TAD ni la traza.

#### Scenario: seleccionar código con teclado
- **GIVEN** Pila en ancho de390 o768 píxeles con Visualización seleccionada
- **WHEN** se presiona Flecha derecha sobre esa pestaña
- **THEN** Código queda seleccionado y enfocado y su panel visible
- **AND** la operación, historial y traza se conservan

### Requirement: Memoria causal de Desapilar exitoso
La traza exitosa de pila_desapilar MUST conservar el nodo separado vivo hasta free, MUST copiar num antes de liberar, y MUST representar p como dirección prestada ptrPila* inmutable al cambiar *p. Aux liberado MUST ser indeterminado y no un NULL inventado.

#### Scenario: separar cima sin liberarla todavía
- **GIVEN** Pila con dos nodos vivos
- **WHEN** se interpreta *p=aux->sgte
- **THEN** la pila lógica tiene un elemento y el heap conserva ambos nodos vivos
- **AND** p sigue apuntando al slot caller y aux al nodo separado

#### Scenario: liberar y retornar copia
- **WHEN** termina free(aux) y luego return num
- **THEN** solo el nodo retirado deja de estar vivo, aux es inválido y num conserva el dato copiado
- **AND** el root caller permanece vivo tras terminar el scope

### Requirement: Educación jerárquica en cinco etapas
ABB, AVL, RedBlack y BinaryHeap MUST conservar ejemplos en Preparar, nivel explicativo en Relacionar con código y predicción, pistas, práctica y comparación en disclosures nativos dentro de Comprender. MUST conservar las cinco etapas vigentes.

#### Scenario: aprendizaje sin nueva ejecución accidental
- **GIVEN** una traza disponible en cualquiera de las cuatro familias
- **WHEN** se cambia nivel, se predice, se solicita una pista o se navega la comparación
- **THEN** se usan capacidades existentes, el teclado abre los disclosures y la navegación no ejecuta nuevamente la operación principal.

