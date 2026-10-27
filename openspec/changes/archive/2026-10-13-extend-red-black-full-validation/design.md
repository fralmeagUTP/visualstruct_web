# Diseño del contrato aprobado, implementación pendiente

Fuentes leídas en D: tad_rojo_negro.h usa nro:int, rbt_color:char, padre/izq/der y RBT puntero; colores ROJO='r', NEGRO='n'. C inserción repetida es no-op; wrapper público la rechaza con ElementoDuplicadoError. La extensión no cambia esa diferencia de envoltura ni permite duplicados en representación. C y backend nativo usan NULL/None; _NilNode y padres de _NodoRNView son presentación reconstruida y NO oráculo del validador.

Cinco reglas enumeradas en delta. Convención interna: altura negra(NULL)=1, igual que la propuesta y oráculo existentes; igualdad importa, no publicar número como nuevo resultado. La comprobación de cotas usa límites opcionales/presencia, jamás nro±1 ni extremos int como centinelas. El contador interno de altura no debe desbordarse: escoger representación/guarda definida sin alterar booleano público.

Plan compatible: helper compara padre esperado por identidad antes de descender; comprueba color y límites estrictos, rojo-rojo, subárbol izquierdo/derecho y altura negra. Esa combinación con raíz.padre=NULL rechaza ciclos/nodos compartidos vivos. No dar esta terminación por probada sólo por pseudocódigo: justificar estructura y ejecutar negativos finitos según acceptance-plan.md. No introducir silenciosamente visitados con malloc ni diagnóstico multivalor; serían otro contrato de memoria/errores. Complejidad objetivo O(n) tiempo/O(h) pila en árboles válidos; árboles inválidos profundos y agotamiento de pila no quedan certificados por casos pequeños.

Rotaciones: primitivas rbt_rotar_izda/rbt_rotar_dcha. Inserción real usa caso1 raíz, caso2 padre negro, caso3 tío rojo, caso4 zigzag y caso5 alineado. LL/RR mapean a caso5; LR/RL a caso4→caso5; recoloreo a caso3→caso1. Eliminación: `arreglarEliminacion` es el símbolo C real, descrito como deleteFixup, sin NIL tiene hermano rojo, ambos sobrinos negros, sobrino cercano rojo con lejano negro y resolución con lejano rojo, con ramas es_izq y espejo. Mapear a código/fixtures existentes; no cambiar algoritmo para satisfacer plantilla ni proclamar ocho configuraciones alcanzables sin evidencia.

El defecto acreditado previo es validación incompleta; no se ha demostrado un defecto de rotaciones. Insertar/Eliminar conservan algoritmo y cierres finitos; sólo regresiones focales nuevas justificadas por integración del validador. Alineación de wrappers, funciones extraídas, planificador, renderer, main y guías por único auditor después de checkpoint Encolar y asignación propia. Fixtures corruptos se construyen test-only sobre reservas vivas; no serializar ciclos con _build_view ni liberar mediante rbt_liberar cíclico: usar registro de reservas únicas para cleanup externo.

Esta entrega contiene specs/documentación solamente. No función pública actual añadida, no escenarios ejecutados ni spec canónica consolidada. C1 y QA global siguen abiertos; Grafos/Dijkstra no aprobados por esta decisión.

## Aclaración RN-DOC-01

Conservación de invariantes sólo en estado estable final de insertar/eliminar/limpiar completos partiendo de árbol válido. No se exige balance completo tras una rotación aislada o durante fix-up. Las consultas conservan su entrada; Validar admite representaciones vivas inválidas y devuelve False sin reparar. Los negativos y el mapa de rotaciones no amplían contratos de las primitivas ni autorizan cambios de algoritmo.

## RN-IMPL-01: estructura no mutante y consulta registrada

El servicio RN mantiene consultas explícitas completadas en su registro cronológico history; reconstruir preserva sus entradas sin redispatch. La pureza de rbt_validar se refiere a objeto/valores/enlaces/colores/reservas yefectos mutantes, no a borrar el evento observable de consulta. True yFalse ejecutados conéxito se registran una vez; False no es errorHTTP ni reparación. Mantener esquema actual combinado, sin journal nuevo. La frase previa no mutar historial se acota a efectos mutantes yno duplicaciónporreplay. La spec general session-state sigue describiendo historial mutante: discrepancia de documentación general fuera del alcance de esta aclaración RN, sin decidir ni editar ese contrato.
