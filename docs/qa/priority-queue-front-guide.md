# Frente de Cola de prioridad

Frente es una consulta readonly registrada en la API con hidden:true. El selector de la página conserva Encolar, Desencolar y Limpiar; esta reparación no añade un control de Frente ni su playback UI.

El C recibe const ColaPrioridad* y dos int*. Declara actual y objetivo como const CPNodo* indeterminados, selecciona objetivo=delante, comienza actual=delante->sgte y compara < estricto. El primer empate permanece. No se cambian nodos, enlaces, raíces ni cantidad, y no se reserva/libera memoria durante la consulta.

valor y prioridad apuntan a almacenamiento independiente del caller. Las dos copias se realizan antes del bool true. Parámetros NULL o cola vacía producen false sin escribir outputs. El kernel no imprime. Los scopes locales terminan al retornar, mientras el caller, outputs y todos los nodos permanecen vivos. La traza API usa como caller C didáctico int valor=0, prioridad=0; los observers privados suministran sus sentinels explícitos.

Las consultas exitosas por la API se registran como acciones para el main y conservan repeticiones. El replay reconstruye sólo mutaciones, sin reconsultar Frente. Una consulta fallida no se agrega al journal. El main realmente mostrado después de recargar usa cp_frente(&cp,&valor,&prioridad), comprueba bool, imprime las copias calculadas por C y limpia la propiedad restante.

Registrar la acción no altera la cola. La API conserva su result escalar; prioridad también se verifica en adapter/C y se muestra en caller, sin ampliación del esquema API. Invalidation de otras trazas preparadas continúa según su contrato existente; no se certifica Siguiente/retroceso de Frente en UI oculta.

Baseline y pruebas finitas en openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-front-instructions-medium. Sin prueba universal de entradas, OOM real o sanitizadores.
