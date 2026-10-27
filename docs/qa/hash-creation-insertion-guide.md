# Hash H1: creación e inserción verificadas en casos finitos

Claves y valores son enteros C; esta revisión se verifica en int32. La capacidad es positiva y fija: insertar colisiones y superar carga 1 no provoca resize. Recrear una tabla libera primero sus nodos y arreglo; `th_inicializar` por sí solo no libera una instancia anterior.

`th_inicializar` escribe capacidad/cantidad, reserva un arreglo de punteros e inicializa cada celda a NULL. Antes de esa escritura individual, una celda es indeterminada. Si malloc retorna NULL, el C fija capacidad0; la UI no ofrece inyección de ese fallo de inicialización. No se ejecutó OOM real ni se certifica capacidad enorme/rendimiento universal.

`th_insertar` llama a `th_indice`: el residuo negativo de C se normaliza sumando capacidad. Recorre `actual` hasta coincidencia o NULL. Una coincidencia actualiza valor sin malloc ni cambio de cantidad. Un nodo nuevo se reserva sin publicar, inicializa clave/valor/siguiente y luego se publica en la cabecera. Entre publicar cabecera y `cantidad++` hay una instrucción real con contador pendiente; la traza lo declara. El fallo simulado de reserva de nodo retorna false sin cambiar contenido. Las validaciones públicas rechazadas no se presentan como llamadas C ejecutadas.

Las variables tipadas, pila de llamadas, heap y máscaras aparecen en Comprender. Un campo indeterminado no equivale a cero/NULL. Las identidades son simbólicas dentro de la operación; no representan direcciones físicas ni identidad persistente certificada entre llamadas o recreaciones.

Ejecutar aplica una operación nueva. Paso a paso recupera su traza; Paso anterior/Siguiente paso y cerrar/reactivar el modo restauran frames sin POST extra. Cambiar entradas invalida la selección anterior. La recarga recupera la última traza conservada y el caller confirmado de la sesión. Reiniciar borra ambos. El historial admite dos inserciones iguales consecutivas.

Descargar main.c entrega bytes C17 desde el historial mutante confirmado. El caller comprueba reservas y el bool calculado de cada inserción, imprime resultados reales y sale por cleanup con status1 ante error. INT_MIN procede de limits.h. No incorpora consultas ni operaciones rechazadas, ni inyecta los fallos QA. Libera objetos en éxito y fallo; las pruebas inyectan cada punto finito de malloc NULL en un observador externo.

C/H se conservan byte a byte. Doxygen se genera desde las descargas reales y callers. Cero advertencias no completa su documentación semántica: el comentario de inicialización no detalla toda la responsabilidad de ownership/errores; esta guía la explica. La auditoría de otros nueve métodos Hash, de recursos grandes y el cierre global permanecen pendientes.


## Actualización de consultas Hash (checkpoint MEDIUM)

El caller incorpora get/contains mediante un journal separado del historial mutante, conserva repeticiones y get ausente (HTTP400). Esta actualización sustituye únicamente la afirmación histórica de que omite consultas. Scopes, salida indeterminada, recarga y límites finitos: [guía de consultas](hash-query-guide.md).
