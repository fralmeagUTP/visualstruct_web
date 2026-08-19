# hierarchical-structures Specification

## Purpose

Módulo de estructuras jerárquicas: ABB (`abb`), AVL (`avl`), Rojo-Negro
(`red_black`) y Montículo Binario (`binary_heap`). Comparte el patrón de endpoints
del módulo secuencial y añade estados visuales de árbol con información de balance,
color y representación de heap.

## Requirements

### Requirement: Catálogo y endpoints del módulo
El sistema DEBE mantener un registro de las 4 estructuras jerárquicas y exponer
`GET /hierarchical/`, `GET /hierarchical/<structure_id>`,
`POST /hierarchical/<structure_id>/operate` y
`POST /hierarchical/<structure_id>/reset` con el mismo contrato JSON que el módulo
secuencial (`success`, `message`, `result?`, `visual_state`, `history`,
`execution_trace`; `200`/`400`/`404`).

#### Scenario: índice jerárquico
- **WHEN** un cliente hace `GET /hierarchical/`
- **THEN** responde `200` listando ABB, AVL, Rojo-Negro y Montículo Binario

#### Scenario: operación exitosa en AVL
- **WHEN** se envía `{"operation": "insertar", "payload": {"value": 15}}` a `/hierarchical/avl/operate`
- **THEN** responde `200` con `success=true` y el árbol actualizado en `visual_state`

### Requirement: Estado visual de árbol binario
Los adapters de ABB, AVL y Rojo-Negro DEBEN exponer un estado visual serializable
con `kind: "binary_tree"` y un `root` recursivo de nodos `{"value", "left",
"right"}`. AVL DEBE incluir factor de equilibrio/altura por nodo y Rojo-Negro DEBE
incluir `color` por nodo.

#### Scenario: nodo AVL con metadata de balance
- **GIVEN** un AVL con varios nodos
- **WHEN** se solicita el estado visual
- **THEN** cada nodo incluye su factor de equilibrio o altura para la vista

#### Scenario: nodo Rojo-Negro con color
- **GIVEN** un árbol RN tras inserciones
- **WHEN** se solicita el estado visual
- **THEN** cada nodo incluye `color` (`RED`/`BLACK` o equivalente)

### Requirement: Estado visual de montículo
El adapter de `binary_heap` DEBE exponer el arreglo interno (`array`) y una vista de
árbol casi completo (`root`) derivada de los índices del arreglo, junto con `size` y
`empty`.

#### Scenario: heap con arreglo y árbol coherentes
- **GIVEN** un min-heap con valores insertados `[1, 5, 3, 7]`
- **WHEN** se solicita el estado visual
- **THEN** `array` refleja el orden interno del heap y `root` representa el mismo
  heap con hijos en `2i+1`/`2i+2`

### Requirement: Invariantes de ABB
Las operaciones `insertar`, `eliminar` y `buscar` del ABB DEBEN respetar la
propiedad de orden (menores a la izquierda, mayores a la derecha) y la eliminación
DEBE manejar los casos hoja, un hijo y dos hijos (sucesor mínimo del subárbol
derecho).

#### Scenario: inserciones mantienen el orden
- **WHEN** se insertan `[8, 3, 10, 1, 6]` en el ABB
- **THEN** el recorrido inorden del estado visual produce `[1, 3, 6, 8, 10]`

#### Scenario: eliminar nodo con dos hijos
- **GIVEN** un ABB con `[8, 3, 10, 6, 7]`
- **WHEN** se elimina `3`
- **THEN** el sucesor `6` ocupa su posición y el orden se conserva

### Requirement: Balanceo AVL
El AVL DEBE rebalancear tras `insertar` y `eliminar` aplicando rotaciones simples o
dobles (LL, RR, LR, RL) de modo que todo nodo mantenga |FE| ≤ 1. La traza de
inserción DEBE identificar el tipo de rotación aplicada cuando ocurra.

#### Scenario: inserción que provoca rotación RR
- **GIVEN** un AVL con `[10, 20]`
- **WHEN** se inserta `30`
- **THEN** la raíz pasa a ser `20` y la traza identifica la rotación a la izquierda

#### Scenario: AVL se mantiene balanceado tras muchas inserciones
- **WHEN** se insertan 15 valores en orden ascendente
- **THEN** la altura del árbol resultante es logarítmica y todo nodo tiene |FE| ≤ 1

### Requirement: Invariantes Rojo-Negro
El árbol Rojo-Negro DEBE mantener tras `insertar` (con casos de fix-up
recoloreo/rotación) que la raíz sea negra, que no haya dos nodos rojos consecutivos
y que las rutas raíz-hoja tengan igual black-height. La operación `validar` DEBE
comprobar estos invariantes.

#### Scenario: raíz negra tras inserciones
- **WHEN** se insertan varios valores en el árbol RN
- **THEN** el nodo raíz del estado visual tiene color negro

#### Scenario: validar en árbol sano
- **GIVEN** un árbol RN construido con inserciones válidas
- **WHEN** se ejecuta `validar`
- **THEN** responde éxito indicando que los invariantes se cumplen

### Requirement: Propiedad de heap
El `binary_heap` DEBE mantener la propiedad de min-heap (padre ≤ hijos) tras
`insertar` (sift-up) y `extraer_raiz` (sift-down), y `raiz` DEBE retornar el mínimo
sin mutar la estructura.

#### Scenario: raíz es el mínimo
- **GIVEN** un heap con `[9, 4, 7, 1]`
- **WHEN** se consulta `raiz`
- **THEN** retorna `1` y el historial no cambia

#### Scenario: extracción reordena el heap
- **GIVEN** el mismo heap
- **WHEN** se ejecuta `extraer_raiz`
- **THEN** retorna `1` y la nueva raíz es el siguiente mínimo

### Requirement: Recorridos y consultas
ABB y AVL DEBEN soportar recorridos (`inorden`, `preorden`, `postorden` según TAD),
`minimo`, `maximo`, `altura` y `validar` como operaciones de consulta que no mutan
el historial.

#### Scenario: inorden no muta
- **GIVEN** un ABB con elementos
- **WHEN** se ejecuta `inorden`
- **THEN** responde `200` con el recorrido en `result` y el historial permanece igual
