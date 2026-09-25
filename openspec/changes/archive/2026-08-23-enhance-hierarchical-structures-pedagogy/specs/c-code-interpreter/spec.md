## ADDED Requirements

### Requirement: Frame causal jerárquico
El intérprete SHALL emitir frames versionados que vinculen cada instrucción C ejecutada con condición, variables, pila recursiva, nodos, punteros, memoria, estado anterior/posterior, ajuste e invariante.

#### Scenario: regresar de una llamada recursiva
- **WHEN** `insertar(raiz->izq, valor)` devuelve una nueva raíz local
- **THEN** el frame muestra valor retornado, continuación y reconexión en `raiz->izq`

### Requirement: Ruta jerárquica sin inferencia frontend
El frontend SHALL NOT deducir ramas, rotaciones, recoloreos o intercambios por texto, proporción de líneas o diferencias visuales aproximadas.

#### Scenario: caso rojo-negro sin rotación
- **GIVEN** un fix-up que solo recolorea
- **WHEN** se reproduce
- **THEN** no aparece una rotación si el backend no emitió ese evento

### Requirement: Semántica de memoria jerárquica
Los frames SHALL representar reserva, inicialización, enlaces, sustitución, desconexión y liberación con identidades lógicas estables y sin referencias a memoria liberada.

#### Scenario: liberar nodo ABB
- **WHEN** el C ejecuta `free(nodo)`
- **THEN** el nodo ya está desconectado, se marca liberado y ningún puntero válido continúa apuntándolo

### Requirement: Condiciones y valores derivados
Alturas, factores, colores, black-height, índices y comparaciones SHALL mostrar la expresión C, valores sustituidos, resultado y consecuencia real.

#### Scenario: comprobar hijo menor en heap
- **WHEN** se evalúa `arreglo[hijo] < arreglo[menor]`
- **THEN** el frame muestra índices y valores concretos y solo sigue la rama registrada
