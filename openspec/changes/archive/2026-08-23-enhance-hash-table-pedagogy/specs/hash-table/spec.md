## ADDED Requirements

### Requirement: Contrato fiel de tipos y capacidad
El módulo SHALL presentar una tabla de capacidad fija y SHALL almacenar directamente claves y valores enteros equivalentes a los usados por el TAD C.

#### Scenario: insertar claves que colisionan
- **GIVEN** capacidad 3 y claves 1, 4 y 7
- **WHEN** se insertan los tres pares
- **THEN** el TAD C conserva las claves originales en el bucket 1 sin sustituirlas por identificadores ocultos

#### Scenario: capacidad fija
- **WHEN** el factor de carga supera 1
- **THEN** la capacidad no cambia y la interfaz no anuncia resize ni rehash

### Requirement: Explicación de la función hash
Cada operación por clave SHALL mostrar la expresión módulo con semántica C, el residuo, la normalización de negativos y el índice final.

#### Scenario: clave negativa
- **GIVEN** clave -2 y capacidad 3
- **WHEN** se calcula el índice
- **THEN** se muestra residuo -2, normalización `-2 + 3` e índice 1

### Requirement: Representación de encadenamiento separado
La vista SHALL representar arreglo de buckets, cabeceras, nodos, claves, valores, enlaces y `NULL` con identidades lógicas estables.

#### Scenario: colisión al insertar
- **WHEN** una clave se inserta en un bucket ocupado
- **THEN** se conserva la cadena anterior, el nuevo nodo se enlaza según el C y cada dirección permanece estable

### Requirement: Inserción y actualización causales
La inserción SHALL distinguir clave nueva, colisión y actualización, mostrando recorrido, comparaciones, reserva, inicialización y enlaces realmente ejecutados.

#### Scenario: actualizar clave existente
- **WHEN** la cadena contiene la clave
- **THEN** cambia solo su valor y no cambian cantidad, dirección, longitud ni colisiones

#### Scenario: fallo de memoria
- **WHEN** `malloc` retorna `NULL`
- **THEN** la operación falla sin cambiar nodos, enlaces ni cantidad

### Requirement: Búsqueda causal y costo observado
Buscar y contener SHALL mostrar nodo actual, comparación sustituida, avance, resultado y número de nodos examinados.

#### Scenario: búsqueda ausente en cadena
- **WHEN** ninguna clave coincide
- **THEN** se muestran todas las comparaciones ejecutadas y el recorrido termina en `NULL`

### Requirement: Eliminación causal
Eliminar SHALL distinguir cabecera, nodo intermedio y ausencia, mostrando `actual`, `anterior`, enlace sustituido, liberación y cantidad.

#### Scenario: eliminar cabecera
- **WHEN** la clave está en el primer nodo
- **THEN** `bucket[indice]` recibe `actual->siguiente` antes de `free(actual)`

#### Scenario: eliminar nodo intermedio
- **WHEN** existe un nodo anterior
- **THEN** `anterior->siguiente` omite al nodo antes de liberarlo

### Requirement: Ciclo de vida de la tabla
El módulo SHALL diferenciar vaciado y destrucción según la semántica C.

#### Scenario: vaciar
- **WHEN** se ejecuta `th_vaciar`
- **THEN** todos los nodos se liberan, los buckets quedan en `NULL` y se conservan arreglo y capacidad

#### Scenario: destruir
- **WHEN** se ejecuta `th_destruir`
- **THEN** se liberan nodos y arreglo y la tabla queda con buckets `NULL`, capacidad 0 y cantidad 0

### Requirement: Invariantes verificables
Cada frame SHALL publicar ubicación, unicidad, cantidad, aciclicidad, alcanzabilidad y seguridad de memoria con evidencia concreta.

#### Scenario: validar después de eliminar
- **WHEN** termina una eliminación exitosa
- **THEN** cantidad coincide con nodos alcanzables y ninguna referencia apunta al nodo liberado

### Requirement: Comparación aislada por capacidad
La comparación SHALL ejecutar una entrada inmutable sobre copias independientes y SHALL reportar distribución y costo observado.

#### Scenario: comparar capacidades
- **WHEN** se comparan capacidades 3, 7 y 17
- **THEN** cada copia recibe las mismas claves y se contrastan ocupación, colisiones, longitud máxima/promedio y comparaciones
