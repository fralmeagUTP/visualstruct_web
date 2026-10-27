## ADDED Requirements

### Requirement: Un único contrato ejecutable por operación
Cada operación pública que se presente como interpretación C MUST tener una función o composición
C explícita, y el backend, adapter, traza, consola y frontend MUST aplicar la misma semántica,
tipos, validaciones, orden y política de errores.

#### Scenario: implementaciones con igual resultado y algoritmo distinto
- **GIVEN** una operación cuyo C y backend producen el mismo resultado mediante algoritmos distintos
- **WHEN** la aplicación genera la explicación paso a paso
- **THEN** la operación se considera no conforme
- **AND** se corrige una capa para ejecutar el contrato canónico, no se fabrica una traza equivalente

#### Scenario: operación sin implementación C
- **GIVEN** una operación pública marcada como interpretación C
- **WHEN** no existe implementación o composición C compilable
- **THEN** la operación MUST implementarse y mapearse en C o retirarse explícitamente de ese contrato

### Requirement: Aritmética y memoria definidas en los límites
Los TAD C y sus transcripciones MUST evitar comportamiento indefinido y MUST validar tamaños y
rangos antes de reservar memoria, produciendo errores equivalentes y reproducibles en todas las
capas.

#### Scenario: Radix Sort contiene INT_MIN
- **GIVEN** un arreglo que contiene `INT_MIN`
- **WHEN** se ejecuta Radix Sort bajo UBSan
- **THEN** no ocurre overflow al obtener su magnitud
- **AND** el resultado conserva el multiconjunto y queda ordenado

#### Scenario: rango de conteo excesivo
- **GIVEN** pocos valores con una amplitud mayor que el límite documentado
- **WHEN** se solicita Counting Sort o Bin Sort
- **THEN** C y backend rechazan la entrada antes de reservar el arreglo de conteos
- **AND** la consola y la traza muestran el mismo error tipado

Los gates sanitizados MUST mantener fuentes/plataforma/fixtures exactos; ASan/UBSan con detect_leaks=0 MUST NOT certificar LSan. El fixture RadixINT_MIN admitido queda vinculado a CI38420918688/job115377686404/logSHA7a41064147c5bc3fb772e223eeab6aea6083f5adb8ca87d456b49cc6502224f4.


### Requirement: Contrato coherente para grafos
Grafos MUST definir de manera única dirección, tipo de peso, aristas duplicadas, extremos ausentes,
orden de recorridos, pesos inválidos, conectividad y significado de MST/bosque.

#### Scenario: arista con atributos no representables
- **GIVEN** una arista cuya dirección o peso no puede representarse en el contrato C activo
- **WHEN** se intenta insertar
- **THEN** se rechaza sin mutar el grafo o se almacena exactamente mediante el contrato C extendido
- **AND** consola, estado interno y visualización muestran el mismo valor efectivo

#### Scenario: grafo desconectado para MST
- **GIVEN** un grafo no dirigido con más de un componente
- **WHEN** termina Prim o Kruskal
- **THEN** el resultado se identifica como bosque mínimo y reporta sus componentes
- **AND** no se presenta como árbol abarcador completo

### Requirement: Contrato coherente para hash y secuenciales
Hash, pila, cola, prioridad y listas MUST compartir entre C y backend el dominio de datos, función
de índice, política de capacidad, orden, desempate, consultas y ciclo de vida.

#### Scenario: índice hash reproducible
- **GIVEN** la misma clave, capacidad y estado inicial en procesos diferentes
- **WHEN** C y backend calculan el bucket
- **THEN** ambos producen el mismo índice determinista y la misma cadena de colisión

#### Scenario: snippet de consulta
- **GIVEN** una consulta de cima, frente o final mostrada en el panel C
- **WHEN** se compila el fragmento con el header publicado
- **THEN** todos sus símbolos existen y la ejecución devuelve el valor presentado por la UI

La premisa de consulta mostrada públicamente MUST evaluarse contra la exposición vigente. CimaPila/FrenteFinalCola son núcleos privados con rechazoHTTPpúblico y sinconsultaUIexitosa; su C/header/traza privada se verifica separadamente. MUST NOT publicarse una consulta inexistente para fabricar el escenario. Priorityfrentehiddenregistrado conserva contrato propio.


### Requirement: Estado visual causado por eventos C
Cada frame MUST ser una proyección del snapshot posterior a un evento C real. Temporales, enlaces,
rotaciones, colores, intercambios, relajaciones y liberaciones MUST aparecer en el orden causal y
con identidad lógica estable.

#### Scenario: operación compuesta
- **GIVEN** una rotación doble, fix-up, sift o relajación con varios eventos mutantes
- **WHEN** se reproduce paso a paso
- **THEN** existe un frame por cada mutación didácticamente relevante
- **AND** ningún frame adelanta el estado final a la llamada de la subrutina

#### Scenario: nodo único circular
- **GIVEN** una lista circular de un elemento cuyo C enlaza `next` al mismo nodo
- **WHEN** se renderiza el snapshot posterior
- **THEN** el autoenlace es visible y HEAD/COLA conservan la misma identidad

### Requirement: Consola derivada de ejecución
La consola didáctica MUST consumir exclusivamente eventos de salida producidos por instrucciones C
alcanzadas y MUST reconstruirse determinísticamente al avanzar, retroceder o reiniciar.

#### Scenario: mensaje técnico sin printf
- **GIVEN** un mensaje descriptivo de traza que no procede de una salida C
- **WHEN** se reproduce la operación
- **THEN** el mensaje puede aparecer en historial técnico
- **AND** no aparece como salida equivalente a `printf`

### Requirement: Cierre verificable de los hallazgos QA
Cada uno de los 29 `case_id` publicados MUST conservar su fixture mínimo, prueba de regresión y
evidencia antes/después; un caso sólo puede cerrarse cuando la divergencia desaparece sin eliminar
o debilitar el oráculo.

#### Scenario: cierre de un hallazgo
- **GIVEN** un hallazgo del backlog P0, P1 o P2
- **WHEN** se propone marcarlo como corregido
- **THEN** su regresión pasa en la capa afectada y en integración
- **AND** C17, sanitizers y reproducción UI no muestran una divergencia equivalente

La admisión MUST conservar estados históricos fixed_pending_gate y las fuentes anteriores; los sucesores aceptados y los gates compartidos finitos MUST identificarse por case_id y fixture. CIRCULAR001/SORT003 tienen admisión finita; los29oráculos jerárquicos son otra selección, no sustituyen los29hallazgos.

