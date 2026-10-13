## MODIFIED Requirements

### Requirement: Invariantes Rojo-Negro
Partiendo de un árbol RN válido, las operaciones completas `insertar`, `eliminar` y `limpiar` MUST conservar en su estado estable final las cinco propiedades clásicas: (1) cada nodo tiene color ROJO o NEGRO; (2) raíz no vacía negra; (3) toda hoja conceptual NULL negra; (4) los hijos de un nodo rojo son negros, sin rojo-rojo; (5) todo camino de un mismo nodo hasta una hoja conceptual tiene igual número de nodos negros. MUST conservar además orden ABB estricto sin duplicados, raíz con padre NULL y enlaces hijo/padre consistentes por identidad, sin ciclos ni reservas compartidas.

La conservación del árbol balanceado MUST exigirse al terminar la operación completa, no a primitivas de rotación aisladas, auxiliares de fix-up ni estados intermedios de rebalanceo. Las consultas MUST conservar exactamente la representación recibida; no tienen obligación de reparar una representación inválida.

`validar` MUST comprobar estas propiedades sobre el modelo nativo original, no sobre la vista NIL reconstruida. MUST retornar True/1 sólo si todas se cumplen y False/0 ante una infracción. Vacío MUST ser válido. La consulta MUST terminar ante ciclos o enlaces compartidos lógicos finitos de objetos vivos, sin mutar ni reparar el árbol. Una representación inválida detectada MUST ser resultado booleano de una consulta ejecutada, no error de entrada ni efecto mutante estructural. No se promete inspeccionar punteros arbitrarios, colgantes o memoria liberada; los objetos no NULL y sus campos examinados MUST ser vivos y legibles. Los helpers MUST evitar overflow al comprobar cotas y altura negra.

El término historial MUST distinguir el efecto mutante de la estructura del registro cronológico ejecutable de operaciones de RN. Conforme al comportamiento preexistente del servicio, una solicitud explícita `validar` completada con éxito MUST añadir exactamente una entrada de consulta a ese registro, incluso si el resultado es False/0; una representación inválida detectada no es fallo de ejecución. MUST conservar valores, colores, enlaces, reservas y secuencia de efectos mutantes. La reconstrucción por GET y la navegación MUST conservar entradas de consultas sin ejecutar de nuevo `validar` ni añadir duplicados. Esta distinción MUST usar el esquema existente: no exige un nuevo almacenamiento, un journal separado ni eliminación de entradas de consulta. Errores de entrada o ejecución rechazados MUST conservar el registro sin una consulta aparentemente ejecutada.

#### Scenario: raíz negra tras inserciones
- **WHEN** se insertan varios valores en el árbol RN
- **THEN** el nodo raíz del estado visual tiene color negro
- **AND** el modelo conserva las cinco propiedades y el orden/enlaces definidos

#### Scenario: validar en árbol sano
- **GIVEN** un árbol RN construido con inserciones válidas
- **WHEN** se ejecuta `validar`
- **THEN** responde éxito indicando que los invariantes se cumplen, con resultado True/1 y sin mutar el modelo ni añadir un efecto mutante estructural

#### Scenario: vacío y hoja válida
- **GIVEN** raíz NULL o una hoja negra con hijos NULL y padre NULL
- **WHEN** se ejecuta `validar`
- **THEN** devuelve True/1, considerando NULL hoja conceptual negra sin reservar nodos NIL

#### Scenario: infracción de las cinco propiedades
- **GIVEN** objetos vivos con color inválido, raíz roja, rojo-rojo o desigualdad de altura negra, incluidos contraejemplos que el validador parcial aceptaba
- **WHEN** se ejecuta `validar`
- **THEN** devuelve False/0 y conserva exactamente la representación inválida recibida, sin reparar, reservar, liberar ni imprimir

#### Scenario: orden y enlaces incorrectos
- **GIVEN** un duplicado, infracción de cota ancestral, padre de raíz no NULL o padre de hijo distinto por identidad
- **WHEN** se ejecuta `validar`
- **THEN** devuelve False/0, incluso si una vista reconstruida oculta el defecto del modelo
- **AND** INT_MIN/INT_MAX no requieren centinelas ni sumar/restar uno a una clave

#### Scenario: ciclo o nodo compartido vivo
- **GIVEN** objetos vivos con ciclo directo/interior o un mismo nodo alcanzable por enlaces distintos
- **WHEN** se ejecuta `validar` en fixture controlado sin serialización recursiva insegura
- **THEN** termina con False/0 sin mutación ni recorrer un destructor cíclico

#### Scenario: rebalanceo observado tras insertar y eliminar
- **GIVEN** fixtures alcanzables por el algoritmo real que ejercen rotación izquierda/derecha, inserción LL/LR/RR/RL y recoloreo o los casos de eliminación de `arreglarEliminacion` con sus espejos aplicables
- **WHEN** termina cada operación y se consulta `validar`
- **THEN** devuelve True/1 y un oráculo independiente confirma las cinco reglas y enlaces
- **AND** los casos se mapean a funciones/ramas reales; etiquetas clásicas no se convierten en ocho casos prometidos sin evidencia de alcance

## ADDED Requirements

### Requirement: Validación RN pública en el TAD descargable
El TAD RN MUST exportar `int rbt_validar(RBT raiz)` en `tad_rojo_negro.h` con implementación y helpers privados en `tad_rojo_negro.c`. El parámetro MUST ser prestado por valor, admitiendo NULL; retornar exclusivamente 1 válido o 0 inválido. La función MUST ser de sólo lectura, sin malloc/free, printf ni modificación de enlaces/colores/datos. Backend MUST reproducir la misma semántica sobre su raíz nativa con None, preservando booleano público, nombres visibles y política sin duplicados. El main MUST enlazar y llamar esta función sin redefinición homónima. La excepción C/H MUST limitarse a validación RN; no cambia el algoritmo de Insertar/Eliminar ni tipos/dominio de otros TAD.

#### Scenario: descargar compilar y llamar
- **GIVEN** C/H RN obtenidos de las rutas HTTP reales y el main mostrado/copied por el estudiante
- **WHEN** se compilan juntos en C17 con warnings como error y se ejecutan consultas repetidas
- **THEN** todos los símbolos existen, no hay definición duplicada y se imprime el resultado calculado por rbt_validar
- **AND** Doxygen y guía explican propiedades, precondición de referencias vivas y propiedad prestada

### Requirement: Traza causal y reproducción de Validar RN completo
La fuente mostrada MUST contener la función C real y los helpers alcanzados. Cada frame MUST corresponder a condiciones, llamadas/retornos, cotas, color/altura negra y scopes efectivamente ejecutados, conservando cortocircuito y antes/después sin fabricar mutaciones. La validación MUST conservar heap y estado estructural; ambas vistas y replay MUST restaurar variables/resultados sin POST adicional. La consola MUST separar ausencia de printf del validador de la salida real del caller. Root/parent NULL nativos MUST distinguirse del NIL sintético de presentación.

#### Scenario: rama inválida y cortocircuito
- **GIVEN** un fixture vivo que viola un invariante antes de visitar un subárbol posterior
- **WHEN** se observa la llamada y se navega adelante/atrás
- **THEN** sólo aparecen instrucciones alcanzadas y retorno False/0; no se muestran comprobaciones no ejecutadas ni una validación completa ficticia
- **AND** snapshots/heap permanecen idénticos y el resultado aparece en su retorno real

#### Scenario: consulta repetida y recarga
- **GIVEN** consultas Validar exitosamente ejecutadas y repetidas sobre un árbol válido
- **WHEN** se recarga y navega la traza o se compila el main real
- **THEN** conserva llamadas y resultados sin revalidar ni duplicar entradas por navegación/reload ni añadir efectos mutantes estructurales, y el main utiliza la función exportada una sola vez por llamada
