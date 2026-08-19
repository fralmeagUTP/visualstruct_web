# c-code-interpreter Specification

## Purpose

Núcleo didáctico del sistema: extracción de código C real desde `docs/tads_C/`,
construcción de trazas de ejecución paso a paso que respetan el flujo de control
del código, y fallback a pseudocódigo cuando no existe mapeo C. La simulación DEBE
comportarse como un **intérprete gráfico de código C**, no como una reproducción
lineal de líneas.
## Requirements
### Requirement: Extracción de funciones C desde docs/tads_C
El sistema MUST extraer el cuerpo completo de cada función C mapeada (incluido su
comentario de documentación inmediatamente superior, si existe) desde los archivos
`.c` de `docs/tads_C/`, localizando la firma por nombre y el final por balanceo de
llaves. Si el archivo o la función no existe, DEBE devolver cadena vacía sin fallar.

#### Scenario: función extraída con su comentario
- **GIVEN** `tad_pila.c` define `pila_apilar` con un bloque `/** ... */` adjunto
- **WHEN** se solicita el snippet de `pila_apilar`
- **THEN** el texto incluye el comentario y el cuerpo completo de la función

#### Scenario: archivo inexistente
- **WHEN** se solicita código de un archivo que no existe en `docs/tads_C`
- **THEN** el servicio devuelve vacío y la UI usa el mensaje por defecto

### Requirement: Mapeo operación → función C por estructura
El sistema MUST mantener mapas de operación a símbolo C para todas las estructuras
soportadas (secuenciales, jerárquicas, grafo, hash y ordenamiento) y DEBE devolver
para cada estructura: `record` (definiciones C de la estructura), `operations`
(código por operación), `default_operation` (mensaje cuando no hay snippet) y
`code_title` (`"Codigo C"`).

#### Scenario: operación con mapeo directo
- **WHEN** se solicita el dato didáctico de `stack` para `apilar`
- **THEN** `operations["apilar"]` contiene la función `pila_apilar` real

#### Scenario: operación sin mapeo
- **WHEN** se solicita una operación sin función C asociada
- **THEN** se devuelve el `default_operation` indicando que no hay código disponible

### Requirement: Extracción de la estructura del TAD
El sistema MUST extraer los bloques de declaración C (structs, typedefs, enums) que
describen cada TAD desde los headers y fuentes, concatenándolos como texto
`record`. Si no encuentra ninguno, DEBE devolver un mensaje indicando que la
estructura no fue encontrada.

#### Scenario: estructura de pila encontrada
- **WHEN** se solicita el `record` de `stack`
- **THEN** incluye las declaraciones del nodo y del tipo Pila del TAD

### Requirement: Operaciones compuestas y derivadas
El sistema MUST enriquecer el mapeo con: operaciones de limpieza compuestas
(destruir + reinicializar), subrutinas auxiliares cuando la simulación las requiere
(p. ej. casos y rotaciones de `rbt_insertar`, `grafo_dfs_recursivo`) y snippets
didácticos para consultas no expuestas directamente por el TAD C.

#### Scenario: insertar RN incluye casos de fix-up
- **WHEN** se solicita el código de `insertar` para `red_black`
- **THEN** el snippet incluye `rbt_insertar` junto con los casos de inserción y rotaciones

#### Scenario: limpiar compuesto
- **WHEN** se solicita `limpiar` de `stack`
- **THEN** el snippet combina `pila_destruir` con el reinicio recomendado

### Requirement: Fallback a pseudocódigo
Cuando no exista mapeo C para una operación o estructura, el sistema MUST usar
`PseudocodeService` como respaldo didáctico (o el placeholder C para estructuras
C-first), sin romper la vista.

#### Scenario: estructura sin datos C
- **GIVEN** una estructura sin archivo en `docs/tads_C`
- **WHEN** se construye el contenido didáctico
- **THEN** se usa el servicio de pseudocódigo o el placeholder `"/* Codigo C no
  disponible ... */"`

### Requirement: Filtrado de líneas ejecutables
El constructor de trazas MUST excluir de la animación líneas vacías, comentarios de
línea y de bloque, llaves aisladas `{`/`}` y directivas de preprocesador `#` en
código C.

#### Scenario: traza sin comentarios
- **GIVEN** un snippet con comentarios y llaves en solitario
- **WHEN** se construye la traza
- **THEN** los pasos solo incluyen líneas ejecutables

### Requirement: Respeto del flujo de control
La traza MUST respetar el flujo de control real del código C: en operaciones
exitosas se omiten las ramas defensivas no ejecutadas (bloques `if (x == NULL)` con
salida temprana), y en operaciones fallidas se incluye únicamente el bloque
defensivo cuyo mensaje coincide con el error producido.

#### Scenario: éxito omite ramas defensivas
- **GIVEN** una operación que tiene éxito
- **WHEN** se construye la traza
- **THEN** los cuerpos de los `if` defensivos no ejecutados no aparecen como pasos

#### Scenario: fallo muestra la rama tomada
- **GIVEN** `desapilar` sobre pila vacía
- **WHEN** se construye la traza del error
- **THEN** se incluye el `if` de pila vacía y su salida temprana, y no otras ramas

### Requirement: Estados visuales progresivos alineados a la mutación
La traza MUST generar estados visuales intermedios entre el estado previo y el
final, alineados con la línea de código donde ocurre la mutación real (asignación),
de modo que el cambio visual coincida con el resaltado del código.

#### Scenario: inserción en lista muestra el enlace en el paso correcto
- **GIVEN** `insertar_final` en lista enlazada
- **WHEN** se reproduce la traza
- **THEN** el nuevo nodo aparece en el paso donde el código reasigna el enlace, no antes

### Requirement: Fases visuales de operaciones mutantes
Toda operación mutante MUST mostrar, según el método, las fases: estado inicial,
creación de estructura temporal (p. ej. `aux`), enlace/asignación intermedia,
reasignación a la estructura original y estado final confirmado; los nodos/punteros
temporales DEBEN renderizarse en un bloque separado con etiquetas de paso.

#### Scenario: apilar muestra el nodo auxiliar
- **WHEN** se reproduce `apilar` en modo interpretado
- **THEN** aparece un bloque temporal `aux` antes de la reasignación del tope

### Requirement: Pasos de depuración de árboles
Para `insertar`/`eliminar`/`buscar`/`minimo`/`maximo` en árboles, la traza MUST
incluir pasos de depuración con el camino recorrido (`path_keys`), etapa (`search`,
`apply`, `pre_rebalance`, `rebalance`, `fixup`, ...) y nodos activos. AVL DEBE
detectar e informar la rotación real aplicada (LL/RR/LR/RL) y Rojo-Negro DEBE
distinguir inserción BST, nacimiento rojo y fix-up.

#### Scenario: rotación AVL identificada en la traza
- **GIVEN** una inserción AVL que produce rotación RR
- **WHEN** se construye la traza
- **THEN** algún paso incluye `rotation_hint` con `type="RR"` y mensaje descriptivo

#### Scenario: fix-up RN etiquetado
- **GIVEN** una inserción RN con recoloreo
- **WHEN** se construye la traza
- **THEN** los pasos distinguen las etapas `apply`, `pre_fixup` y `fixup`

### Requirement: Consola printf e historial técnico
La traza MUST reflejar en la consola únicamente las salidas `printf` efectivamente
ejecutadas en la ruta de control actual, y DEBE evitar repetir mensajes consecutivos
equivalentes tanto en consola como en el historial técnico.

#### Scenario: sin mensajes redundantes consecutivos
- **GIVEN** una operación que imprime el mismo mensaje en iteraciones consecutivas
- **WHEN** se construye la consola
- **THEN** el mensaje no se repite de forma consecutiva

### Requirement: Coherencia historial–estado final
El historial renderizado como `main` MUST mantenerse coherente con la ejecución
real y con el estado visual final de la estructura.

#### Scenario: historial refleja operaciones mutantes ejecutadas
- **GIVEN** una sesión con `[apilar(1), apilar(2)]`
- **WHEN** se renderiza el historial
- **THEN** el `main` muestra esas llamadas en orden y la estructura final coincide

### Requirement: Contrato estable de pasos de traza
El sistema MUST representar cada paso mediante un contrato validable que incluya línea C,
evento semántico, etapa, estado previo, estado posterior, salida de consola y metadatos. El
estado posterior del último paso DEBE coincidir con el estado visual final de la operación.

#### Scenario: paso conforme al contrato
- **GIVEN** una operación con código C y estado inicial válido
- **WHEN** el motor construye su traza
- **THEN** cada paso contiene los campos obligatorios con tipos válidos
- **AND** el último `after_state` equivale al estado final de la operación

#### Scenario: estrategia produce un paso inválido
- **GIVEN** una estrategia que omite un campo obligatorio
- **WHEN** entrega sus pasos al motor
- **THEN** el motor rechaza la traza con un error de contrato identificable en pruebas

### Requirement: Estrategias de traza por familia
El sistema MUST delegar las reglas específicas de secuenciales, árboles, grafos, hash y
ordenamiento en estrategias independientes registradas por estructura. El motor común NO DEBE
contener condicionales de comportamiento propios de una estructura concreta.

#### Scenario: resolución de estrategia
- **GIVEN** una operación sobre `avl`
- **WHEN** se solicita construir su traza
- **THEN** el registro selecciona la estrategia de árboles
- **AND** la fachada pública conserva el esquema de respuesta vigente

#### Scenario: estructura sin estrategia
- **GIVEN** un identificador de estructura no registrado
- **WHEN** se solicita una traza
- **THEN** el sistema devuelve un error controlado o el fallback documentado

### Requirement: Conformidad observable entre C y Python
Para cada TAD soportado, el sistema DE pruebas MUST ejecutar escenarios equivalentes sobre la
implementación C y la implementación Python y comparar su estado observable canónico, resultado
y clasificación de error. Los escenarios DEBEN ser reproducibles mediante una semilla registrada.

#### Scenario: secuencia equivalente
- **GIVEN** una semilla y secuencia de operaciones válidas sobre una pila
- **WHEN** el runner ejecuta la secuencia en C y Python
- **THEN** ambos producen el mismo estado canónico y resultados observables

#### Scenario: divergencia detectada
- **GIVEN** una operación que produce estados canónicos distintos
- **WHEN** se ejecuta la prueba diferencial
- **THEN** la prueba falla e informa TAD, semilla, secuencia y primera divergencia

### Requirement: Verificación de C estándar y memoria
La CI MUST compilar los 13 TAD con C17, advertencias estrictas tratadas como error, y DEBE ejecutar
sus harnesses con AddressSanitizer y UndefinedBehaviorSanitizer en una plataforma compatible.

#### Scenario: advertencia o error de memoria
- **GIVEN** un cambio en un TAD C que genera una advertencia, fuga detectable, acceso inválido o comportamiento indefinido
- **WHEN** se ejecuta el pipeline C
- **THEN** el job falla y publica el diagnóstico correspondiente

#### Scenario: suite C conforme
- **GIVEN** los 13 TAD sin defectos detectables
- **WHEN** se ejecuta el pipeline C
- **THEN** todos compilan y sus harnesses finalizan correctamente

### Requirement: Compatibilidad durante la migración de trazas
Mientras exista código legado, el sistema MUST comparar en pruebas su salida con el nuevo motor
para los casos golden y DEBE conservar el contrato JSON consumido por la interfaz.

#### Scenario: migración de una familia
- **GIVEN** la familia secuencial migrada al nuevo motor
- **WHEN** se ejecutan sus fixtures golden
- **THEN** la semántica de pasos y el estado final permanecen equivalentes
- **AND** la UI recibe los campos públicos que esperaba antes de la migración

