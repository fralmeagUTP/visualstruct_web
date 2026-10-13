# Delta: didactic-conformance-qa

## ADDED Requirements

### Requirement: Inventario exhaustivo y trazable
La auditoría MUST descubrir desde el sistema todos los TAD, algoritmos, operaciones públicas,
funciones C asociadas, adapters, estrategias de traza y renderers, y MUST fallar su criterio de
cierre si algún elemento queda sin caso evaluado o sin una exclusión justificada.

#### Scenario: operación sin cobertura
- **GIVEN** una operación expuesta por `get_supported_operations()`
- **WHEN** no existe un caso QA asociado a su función C y renderer
- **THEN** la matriz la marca como no evaluada
- **AND** la auditoría no puede declararse completa

### Requirement: Código C como oráculo semántico
La auditoría MUST compilar y ejecutar el código de `docs/tads_C/` bajo C17 estricto y MUST
observar punteros, memoria, condiciones, ciclos, recursión, retornos y casos límite mediante
harnesses reproducibles con ASan y UBSan.

#### Scenario: defecto de memoria en un caso límite
- **GIVEN** una operación C ejecutada sobre una estructura vacía o en su límite
- **WHEN** ASan o UBSan reporta acceso inválido, fuga cubierta por el gate o comportamiento indefinido
- **THEN** el caso se clasifica como fallido con evidencia del sanitizer
- **AND** no se usa la visualización exitosa para ocultar el defecto C

### Requirement: Comparación paso a paso entre capas
Para cada instrucción relevante, la auditoría MUST contrastar el estado C esperado con el estado
interno del backend, `before_state`/`after_state`, historial técnico, consola y estado renderizado,
preservando identidad y enlaces aunque las direcciones físicas se abstraigan.

#### Scenario: mutación visual adelantada
- **GIVEN** una asignación de puntero que todavía no fue ejecutada en C
- **WHEN** el frontend ya muestra el enlace resultante
- **THEN** el caso falla y registra la primera línea y capa divergente

### Requirement: Causalidad entre ejecución C y visualización del TAD
La parte visual de cada TAD MUST representar el estado producido por el código C exactamente en
el paso que se está interpretando. Cada alta, baja, enlace, desplazamiento, intercambio, rotación,
recoloreo o cambio de estructura temporal MUST aparecer únicamente después de la instrucción C
que lo causa, y MUST permanecer ausente cuando esa instrucción o rama no se haya ejecutado.

#### Scenario: cambio visual sincronizado con su instrucción
- **GIVEN** un paso C que asigna el nuevo nodo como cabeza de una lista
- **WHEN** el cursor alcanza y ejecuta esa asignación
- **THEN** el frame posterior muestra el nuevo nodo como cabeza
- **AND** ningún frame anterior muestra ese enlace

#### Scenario: estado final correcto con secuencia visual falsa
- **GIVEN** una operación cuyo resultado final coincide con el C
- **WHEN** uno o más frames anticipan, retrasan, omiten o inventan una mutación intermedia
- **THEN** el caso se clasifica como fallido aunque el estado final sea correcto
- **AND** el informe identifica la primera instrucción y el primer frame divergentes

#### Scenario: efecto de rama no recorrida
- **GIVEN** una rama C que no se ejecuta para la entrada actual
- **WHEN** se reproduce la operación paso a paso
- **THEN** no aparece ningún nodo auxiliar, enlace, mensaje ni cambio visual exclusivo de esa rama

### Requirement: Fidelidad del flujo de control
La traza auditada MUST incluir únicamente ramas e iteraciones realmente ejecutadas y MUST
representar correctamente `if`, `else`, `while`, `for`, `switch`, llamadas recursivas, casos base,
retornos anticipados y reanudación de la llamada invocadora.

#### Scenario: rama no ejecutada incluida
- **GIVEN** una condición C evaluada como falsa
- **WHEN** la traza contiene pasos exclusivos de la rama verdadera
- **THEN** el resultado es fallido con severidad mínima alta

#### Scenario: recursión multinivel
- **GIVEN** una operación recursiva con al menos tres niveles
- **WHEN** se compara la secuencia de llamadas y retornos
- **THEN** cada paso visual conserva el orden de la pila lógica y el estado del marco activo

### Requirement: Temporales, punteros y consola didáctica
La auditoría MUST verificar que nodos auxiliares, arreglos temporales, colas, pilas, conjuntos,
variables de control y enlaces de puntero usados por el algoritmo sean visibles cuando sean
necesarios para explicar la mutación, y que la consola reproduzca sólo los `printf` alcanzados.

#### Scenario: salida no alcanzada
- **GIVEN** un `printf` ubicado en una rama no ejecutada
- **WHEN** su texto aparece en la consola didáctica
- **THEN** el caso falla y señala la rama y la línea de origen

### Requirement: Invariantes específicos por familia
Después de cada mutación relevante, la auditoría MUST validar LIFO, FIFO, prioridad, enlaces y
circularidad; orden y balance de árboles; colores y black-height; propiedad de heap; semántica de
grafos, caminos y MST; colisiones y rehash; y progreso correcto de los algoritmos de ordenamiento.

#### Scenario: invariante temporal violado
- **GIVEN** una rotación AVL en progreso
- **WHEN** un estado presentado como estable tiene `|FE| > 1` sin marcarse como estado transitorio
- **THEN** el caso falla aunque el árbol final quede balanceado

### Requirement: Controles reproducibles y equivalencia de modos
Para toda traza, la interfaz MUST permitir avanzar, retroceder, reproducir, pausar y reiniciar de
forma determinista, y el estado alcanzado al finalizar MUST ser idéntico al modo rápido y al
estado final del oráculo C.

#### Scenario: retroceso y repetición
- **GIVEN** una ejecución detenida en un paso intermedio
- **WHEN** el usuario retrocede dos pasos y vuelve a avanzar
- **THEN** obtiene exactamente los mismos estados, resaltados y consola que en el primer recorrido

#### Scenario: divergencia entre modos
- **GIVEN** la misma entrada y estado inicial
- **WHEN** finalizan el modo rápido y el modo paso a paso
- **THEN** sus estados canónicos, retornos e historial técnico son idénticos

### Requirement: Casos normales, límites e inválidos
Cada operación MUST evaluarse con casos nominales, estados vacíos y unitarios, límites relevantes,
entradas inválidas y rutas alternativas; los casos generados MUST registrar semilla y reducir la
primera divergencia a una secuencia mínima reproducible.

#### Scenario: fallo generado reproducible
- **GIVEN** una divergencia encontrada por una secuencia aleatoria
- **WHEN** se guarda el hallazgo
- **THEN** incluye TAD, operación, semilla, entrada original y caso reducido que reproduce el fallo

### Requirement: Informe QA estructurado
La auditoría MUST producir por operación y caso: entrada, precondición, estados esperados,
estados observados, resultado aprobado/fallido, discrepancia, severidad, causa probable,
archivo/función a revisar, prueba automatizada recomendada y corrección sugerida.

#### Scenario: hallazgo semántico
- **GIVEN** una traza cuyo estado visual contradice al C
- **WHEN** se registra el resultado
- **THEN** el informe identifica la primera divergencia y todas las capas afectadas
- **AND** asigna severidad crítica, alta, media o baja con justificación

### Requirement: Correcciones separadas de la auditoría
La ejecución de esta auditoría MUST limitarse a evidencia, harnesses, caracterización, informe y
pruebas propuestas; MUST NOT modificar lógica productiva para corregir discrepancias sin una
solicitud explícita posterior.

#### Scenario: defecto con corrección evidente
- **GIVEN** un fallo reproducible y una causa localizada
- **WHEN** se completa el informe
- **THEN** se documenta la corrección sugerida y su prueba de regresión
- **AND** el código productivo permanece sin modificar
