## ADDED Requirements

### Requirement: Progresión pedagógica de los TAD secuenciales
El módulo SHALL ofrecer niveles Básico, Intermedio y Avanzado sobre una ejecución canónica idéntica.

#### Scenario: cambiar de nivel durante una operación
- **GIVEN** una operación pausada en un frame
- **WHEN** el estudiante cambia de Básico a Avanzado
- **THEN** conserva TAD, operación, entrada, cursor y estado, y aparecen punteros, memoria y C del mismo frame

### Requirement: Invariantes secuenciales explícitos
Cada frame SHALL identificar el invariante aplicable y demostrar si permanece satisfecho para el estado mostrado.

#### Scenario: cola queda vacía
- **GIVEN** una cola con un único nodo
- **WHEN** se ejecuta el frame que retira y libera ese nodo
- **THEN** `FRONT` y `BACK` quedan en `NULL` y la explicación justifica el invariante FIFO

### Requirement: Semántica correcta de cola de prioridad
La cola de prioridad SHALL diferenciar el orden físico de llegada de la selección por prioridad y conservar
el desempate estable definido por el TAD C.

#### Scenario: empate de prioridad
- **GIVEN** dos elementos con igual prioridad insertados en momentos distintos
- **WHEN** se busca o desencola el siguiente elemento
- **THEN** la visualización recorre el orden real, identifica candidatos y selecciona primero el de llegada anterior

### Requirement: Visualización de memoria y punteros
Las operaciones SHALL representar reserva, objetos, campos, alias, enlaces, desconexión y liberación conforme
a la semántica del C ejecutado.

#### Scenario: desapilar libera un nodo
- **WHEN** `desapilar` avanza `TOP` y ejecuta `free(aux)`
- **THEN** el nodo se muestra primero desconectado, después liberado, y ningún puntero válido continúa apuntándolo

### Requirement: Ejemplos guiados por estructura
Cada TAD SHALL ofrecer casos vacío, unitario, múltiple, repetido, inválido y casos específicos de su invariante.

#### Scenario: demostrar circularidad
- **WHEN** el estudiante carga el ejemplo de eliminación del único nodo circular
- **THEN** la secuencia muestra cierre inicial, eliminación, terminación segura y estructura vacía válida

### Requirement: Comparación conceptual entre TAD
El módulo SHALL comparar estructuras sobre secuencias aisladas y explicar diferencias semánticas, de extremos,
enlaces e invariantes.

#### Scenario: pila frente a cola
- **GIVEN** la misma secuencia de inserciones
- **WHEN** se compara una extracción de pila con una de cola
- **THEN** se muestran lado a lado LIFO y FIFO sin presentar estados compartidos entre ejecuciones

### Requirement: Aprendizaje predictivo secuencial
El estudiante SHALL poder predecir ramas, reasignaciones, cambios de extremos y liberaciones sin bloquear la exploración.

#### Scenario: predecir transición de cola unitaria
- **GIVEN** una cola con un nodo y modo práctica activo
- **WHEN** el siguiente frame actualizará `BACK`
- **THEN** el resultado permanece oculto hasta responder o continuar y luego se explica por qué ambos extremos cambian

