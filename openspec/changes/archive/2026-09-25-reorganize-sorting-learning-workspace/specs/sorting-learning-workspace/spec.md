## ADDED Requirements

### Requirement: Flujo compacto de Ordenamiento
El módulo de Ordenamiento MUST presentar Preparar y controlar la ejecución, Visualizar y ejecutar, Relacionar con código C, Comprender y Resultados de la ejecución en ese orden y con numeración única de 1 a 5. El rediseño MUST conservar los once algoritmos y sus resultados canónicos.

#### Scenario: abrir el visualizador

- **WHEN** una persona visita `/sorting/visualizador`
- **THEN** encuentra las cinco etapas sin números repetidos
- **AND** puede configurar arreglo y algoritmo antes de iniciar una traza

### Requirement: Controles de ejecución simplificados
Preparar y controlar la ejecución MUST ofrecer Ejecutar operación y Paso a paso como acciones principales. Paso a paso MUST mostrar Anterior y Siguiente sólo cuando una traza esté disponible. Ejecutar operación desde un frame intermedio MUST completar la misma traza hasta su snapshot final.

#### Scenario: completar MergeSort desde un frame intermedio

- **WHEN** una persona avanza parcialmente una traza de MergeSort y pulsa Ejecutar operación
- **THEN** la ejecución alcanza el último frame de esa traza
- **AND** el arreglo, métricas y código muestran el estado final canónico sin regenerar la entrada

### Requirement: Estado de ordenamiento y código C correlacionados
En escritorio, la visualización y el código C MUST ser legibles simultáneamente. Cada frame MUST actualizar la línea C resaltada y sólo los índices, rango, auxiliar, pivote, heap o buckets que el frame real describe.

#### Scenario: partición de QuickSort

- **WHEN** se recorre un frame de partición de QuickSort
- **THEN** se muestran el subrango activo, el pivote y los índices correspondientes
- **AND** el resaltado pertenece a una instrucción de QuickSort o a una función auxiliar realmente llamada

### Requirement: Representación específica del algoritmo
La visualización MUST conservar las representaciones actuales por estrategia: comparación/frontera, mínimo/prefijo, clave/hueco, gap, partición, división-fusión, heap, frecuencias/urnas y dígitos. La interfaz MUST complementar el color con etiquetas textuales y leyenda.

#### Scenario: Radix Sort con valores negativos

- **WHEN** se ejecuta Radix Sort sobre una entrada con positivos, cero y negativos
- **THEN** la estrategia muestra el dígito activo y buckets decimales derivados del frame
- **AND** no representa un orden o tratamiento de signos distinto del algoritmo interpretado

### Requirement: Comprensión y resultados plegables
Comprender MUST poder plegarse y mostrar explicación intermedia, condición, variables, llamadas, ciclos, auxiliares, invariante y métricas del frame activo. Resultados de la ejecución MUST plegar o restaurar juntos consola C, historial, TAD y exportaciones; el TAD MUST ser estático cuando el panel esté abierto.

#### Scenario: consultar una inserción sin sobrecargar la vista

- **WHEN** una persona termina una traza de Inserción y abre Resultados de la ejecución
- **THEN** puede consultar consola, historial y TAD en la misma sección
- **AND** cerrar o abrir Comprender o Resultados no cambia el cursor, arreglo ni código activo

### Requirement: Código C sin overflow global
Relacionar con código C MUST ubicar el checkbox de documentación junto a su título, las funciones sobre el código y el bloque C a ancho completo. Las líneas C MUST conservar su formato; cuando excedan el ancho, MUST usar desplazamiento horizontal local y MUST NOT provocar scroll horizontal global.

#### Scenario: función auxiliar extensa

- **WHEN** una persona navega a `intercambiar`, `arreglo_valido` o una función recursiva auxiliar
- **THEN** la línea C se conserva sin envolverse artificialmente
- **AND** el desplazamiento, si se necesita, se limita al bloque de código

### Requirement: Simplificación sin eliminar capacidades de servicio
La interfaz MUST usar explicación intermedia fija y MUST NOT mostrar selector de nivel, Ejemplo guiado, modo práctica/Predecir ni comparación visual. Retirar esos elementos MUST NOT eliminar las APIs de crear, aleatorio, ejecutar, navegar traza, reiniciar o comparar, ni alterar los algoritmos soportados.

#### Scenario: ejecutar Burbuja sin predicción

- **WHEN** una persona prepara Burbuja mejorada
- **THEN** puede ejecutarla directamente o recorrerla paso a paso sin responder una predicción
- **AND** la API de comparación continúa disponible para consumidores que ya la usen
