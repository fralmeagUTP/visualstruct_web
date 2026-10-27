## ADDED Requirements

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

## MODIFIED Requirements

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
