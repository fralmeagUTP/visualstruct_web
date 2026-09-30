## ADDED Requirements

### Requirement: Flujo jerárquico unificado y numerado
ABB, AVL, Rojo-Negro y Montículo binario MUST presentar Preparar y controlar la ejecución, Visualizar y ejecutar, Relacionar con código C, Comprender y Resultados de la ejecución en ese orden, con numeración única de 1 a 5. El cambio MUST NOT alterar la operación ni el estado canónico.

#### Scenario: abrir una pantalla de AVL
- **WHEN** una persona visita `/hierarchical/avl`
- **THEN** encuentra cinco etapas en el orden común
- **AND** no existen números repetidos ni saltos

### Requirement: Ejecución reducida a acciones comprensibles
La preparación MUST ofrecer Ejecutar operación y Paso a paso como acciones principales. Al activar Paso a paso, la interfaz MUST ofrecer Anterior y Siguiente; ejecutar desde un frame intermedio MUST completar la operación hasta el estado final canónico.

#### Scenario: completar una inserción de ABB desde un frame intermedio
- **WHEN** una persona avanza parte de una traza de insertar en ABB y pulsa Ejecutar operación
- **THEN** la traza llega al último frame
- **AND** la visualización coincide con el estado final del backend

### Requirement: Código y estado jerárquico correlacionados
En escritorio, visualización y código C MUST poder consultarse simultáneamente durante una ejecución. El frame activo MUST actualizar el resaltado de código y el estado correspondiente, sin representar ramas, rotaciones, recoloreos o intercambios no ejecutados.

#### Scenario: inserción que rota un AVL
- **WHEN** una inserción activa una rotación AVL y se recorre paso a paso
- **THEN** código y visualización muestran la misma fase de la rotación
- **AND** altura y balance resultantes corresponden al frame mostrado

### Requirement: Navegación de funciones C vertical y legible
Relacionar con código C MUST ubicar el checkbox de documentación junto a su
encabezado, la lista de funciones sobre el código y el bloque de código a todo
el ancho disponible debajo. La lista MUST NOT usar una columna lateral que
provoque desplazamiento horizontal global; sus botones pueden distribuirse en
varias filas.

#### Scenario: código C de AVL con navegación
- **WHEN** una persona abre Relacionar con código C en AVL
- **THEN** puede elegir una función desde la franja superior
- **AND** el título y bloque C se muestran debajo a ancho completo
- **AND** Ocultar documentación extensa sigue disponible junto al encabezado

### Requirement: Visualización acorde con el tipo jerárquico
Cada estructura MUST comunicar sus invariantes: orden y recorridos en ABB; altura, balance y rotaciones en AVL; colores y reglas de Rojo-Negro; y propiedad min-heap, arreglo e índices en Montículo binario. Las etiquetas textuales MUST complementar el color.

#### Scenario: extracción de raíz de un montículo
- **WHEN** se ejecuta Extraer raíz en Montículo binario
- **THEN** se muestran arreglo y árbol con índices o relaciones padre-hijo relevantes
- **AND** Comprender explica comparaciones de bajada y la propiedad min-heap final

### Requirement: Resultados como una única unidad plegable
Resultados de la ejecución MUST ocultar o restaurar juntos Consola C, historial, exportaciones y Estructura del TAD. Al estar visible, la estructura del TAD MUST ser estática y no depender de un `details` individual.

#### Scenario: abrir resultados de Rojo-Negro
- **WHEN** una persona despliega Resultados de la ejecución en Rojo-Negro
- **THEN** ve consola C, historial, exportaciones y el TAD en la misma etapa
- **AND** puede ocultarlos todos con un único control sin contenido de resultados fuera de la etapa

### Requirement: Simplificación sin alterar algoritmos
Las pantallas jerárquicas MUST usar explicación intermedia fija y MUST NOT mostrar Ejemplo guiado, Predecir o Comparar conceptos. Retirar esos paneles MUST NOT eliminar endpoints de comparación, operaciones públicas, adaptadores ni datos de traza.

#### Scenario: operación de Rojo-Negro sin predicción
- **WHEN** una persona prepara una inserción de Rojo-Negro
- **THEN** puede iniciarla sin responder una predicción ni elegir nivel de explicación
- **AND** la operación conserva el mismo resultado que antes del rediseño
