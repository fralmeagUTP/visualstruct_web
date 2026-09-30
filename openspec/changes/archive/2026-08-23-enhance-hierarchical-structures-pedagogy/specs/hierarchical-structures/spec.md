## ADDED Requirements

### Requirement: Progresión pedagógica jerárquica
El módulo SHALL ofrecer niveles Básico, Intermedio y Avanzado sobre una única traza canónica y conservar estructura, operación, entrada, estado y cursor al cambiar de nivel.

#### Scenario: cambiar de nivel durante una rotación
- **GIVEN** un AVL pausado antes de una rotación
- **WHEN** el estudiante cambia de Básico a Avanzado
- **THEN** permanece en el mismo frame y aparecen parámetros, pila, punteros y C de ese ajuste

### Requirement: Invariantes jerárquicos verificables
Cada frame SHALL publicar el invariante aplicable, su estado y evidencia concreta por nodo, índice o camino.

#### Scenario: detectar desequilibrio AVL temporal
- **WHEN** un nodo alcanza `FE=2` antes del ajuste
- **THEN** el frame marca el balance como temporalmente incumplido, identifica el nodo crítico y anuncia la fase de reparación

#### Scenario: verificar árbol rojo-negro final
- **WHEN** termina una inserción rojo-negro
- **THEN** la vista demuestra raíz negra, ausencia de rojo-rojo y black-height uniforme

### Requirement: Explicación causal de ABB
Las operaciones ABB SHALL mostrar comparación, rama, llamada recursiva, retorno y caso de eliminación sin omitir la reconexión del subárbol.

#### Scenario: eliminar nodo con dos hijos
- **GIVEN** un nodo con dos hijos
- **WHEN** se elimina
- **THEN** la traza identifica sucesor, copia/sustitución, eliminación recursiva y enlace retornado

### Requirement: Explicación causal de rotaciones AVL
Las rotaciones SHALL identificar desequilibrio, caso LL/RR/LR/RL, pivote, hijo, subárbol transferido y actualización de alturas.

#### Scenario: rotación LR
- **WHEN** la ruta produce un caso izquierda-derecha
- **THEN** se muestran dos rotaciones simples en frames consecutivos y se verifica `|FE| ≤ 1`

### Requirement: Explicación causal rojo-negro
El fix-up SHALL identificar nodo, padre, abuelo, tío, orientación, caso, recoloreo, rotación y punto de continuación.

#### Scenario: tío rojo
- **WHEN** padre y tío son rojos
- **THEN** la vista explica el recoloreo, mueve el foco al abuelo y no inventa una rotación

### Requirement: Correspondencia arreglo-árbol del heap
Cada elemento del heap SHALL conservar el mismo índice visible en arreglo y árbol y SHALL mostrar las fórmulas de padre e hijos usadas en el C.

#### Scenario: descenso después de extraer raíz
- **WHEN** el algoritmo compara ambos hijos
- **THEN** identifica sus índices, selecciona el menor, muestra el intercambio y marca la región que ya satisface el min-heap

### Requirement: Ejemplos guiados jerárquicos
Cada TAD SHALL incluir ejemplos normales, límites, inválidos y casos estructurales específicos preparados mediante operaciones públicas reales.

#### Scenario: cargar caso RL
- **WHEN** se carga el ejemplo AVL RL
- **THEN** la entrada, estado inicial y operación quedan preparados sin modificar la traza al cambiar la explicación

### Requirement: Comparación jerárquica aislada
Las comparaciones SHALL usar copias profundas independientes de una entrada inmutable y sincronizarse por operación o concepto.

#### Scenario: ABB frente a AVL con entrada ordenada
- **WHEN** ambos reciben la misma secuencia ascendente
- **THEN** se comparan altura, ruta, ajustes e invariante sin compartir nodos ni historial
