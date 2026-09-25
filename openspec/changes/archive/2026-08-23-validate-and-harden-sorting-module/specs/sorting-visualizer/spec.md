## MODIFIED Requirements

### Requirement: Creación de arreglos
El sistema SHALL crear arreglos de enteros C desde texto o lista mediante
`POST /api/ordenamiento/create-array`, rechazando campos vacíos, elementos ausentes,
valores no enteros y números fuera de `INT_MIN..INT_MAX` sin mutar el estado anterior. También
DEBE generar arreglos mediante `POST /api/ordenamiento/random-array`; `min_value` y `max_value`
SHALL pertenecer al rango de `int`, y una misma semilla y parámetros SHALL producir el mismo arreglo.

#### Scenario: arreglo con extremos C
- **WHEN** se crea el arreglo `[-2147483648, 0, 2147483647]`
- **THEN** el arreglo se acepta sin conversión ni pérdida

#### Scenario: entero fuera del contrato C
- **GIVEN** un estado válido existente
- **WHEN** se intenta crear un arreglo con `2147483648`
- **THEN** responde `400` y conserva el estado previo

#### Scenario: aleatorio reproducible
- **WHEN** se generan dos arreglos con los mismos tamaño, límites y semilla
- **THEN** ambos arreglos son idénticos y todos sus valores respetan los límites

#### Scenario: aleatorio permanece estable al reproducir
- **GIVEN** un arreglo generado sin que el usuario proporcione semilla
- **WHEN** el historial se reconstruye para seleccionar o reproducir un algoritmo
- **THEN** el sistema reutiliza la semilla efectiva persistida y conserva exactamente el arreglo mostrado

### Requirement: Selección y ejecución de algoritmos
El sistema SHALL soportar `intercambio`, `seleccion`, `insercion`, `burbuja`, `shell`,
`quicksort`, `mergesort`, `heapsort`, `counting_sort`, `binsort` y `radixsort`. Cada método
SHALL preservar el multiconjunto de entrada, producir orden ascendente y mostrar el fragmento C
del algoritmo realmente ejecutado. El modo rápido y el paso a paso SHALL terminar en el mismo estado.

#### Scenario: matriz común de algoritmos
- **GIVEN** una entrada normal, ordenada, inversa, con duplicados, con signos o unitaria
- **WHEN** se ejecuta cualquiera de los once algoritmos
- **THEN** el resultado coincide con el oráculo ascendente y conserva el multiconjunto

#### Scenario: algoritmo de ejecución sustituye selección anterior
- **GIVEN** `burbuja` como selección previa
- **WHEN** `run` solicita `quicksort`
- **THEN** se ejecuta QuickSort y cada línea resaltada pertenece al fragmento C de QuickSort

#### Scenario: rango excesivo de conteo
- **WHEN** Counting Sort o Binsort recibe valores cuyo rango supera el máximo publicado
- **THEN** rechaza la operación antes de reservar el arreglo de conteo y conserva la entrada

### Requirement: Navegación por cursor paso a paso
El sistema SHALL aceptar `next` y `previous`, además del alias compatible `prev`, limitar el
cursor a la traza vigente y devolver el frame exacto sin alterar la secuencia interpretada.

#### Scenario: alias anterior
- **GIVEN** una traza disponible y cursor mayor que cero
- **WHEN** se solicita `direction: "prev"`
- **THEN** se devuelve el frame inmediatamente anterior

### Requirement: Trazas didácticas de ordenamiento
Cada paso didáctico SHALL corresponder a una instrucción visible del C ejecutado; `line_index` y
`line_text` SHALL ser consistentes. Las trazas SHALL mostrar comparaciones, movimientos,
intercambios, rangos, pivote o auxiliares cuando corresponda, mantener continuidad entre frames
y finalizar en el mismo estado que la ejecución rápida.

#### Scenario: auxiliares transitivos visibles
- **WHEN** se ejecuta QuickSort, MergeSort, HeapSort, Binsort o Radix Sort
- **THEN** el panel incluye las funciones auxiliares realmente llamadas y ningún paso ejecutado carece de línea C

#### Scenario: utilidades comunes visibles
- **WHEN** un algoritmo evalúa `arreglo_valido` o llama `intercambiar`
- **THEN** esas funciones aparecen en el código seguido y sus llamadas no ocultan lógica ejecutada

#### Scenario: navegación reversible
- **GIVEN** dos frames consecutivos de una ejecución
- **WHEN** se avanza y luego se retrocede
- **THEN** se recuperan exactamente sus estados correspondientes sin recomputar otra historia
