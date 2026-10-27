# Contrato vigente y depuración pendiente

## Conteos
109 operaciones de metadata: 98 sin marca hidden, 11 ocultas. La cifra anterior 110 incluía 12 ocultas; los resultados históricos se conservan, no representan 110 métodos visibles. 13 páginas inspeccionadas en navegador real. Grafos requiere además mapear las cuatro fases y acciones por botón; Ordenamiento tiene controles propios.

## Lista enlazada visible: siete métodos verificados en DOM
Insertar inicio, Insertar final, Lista insertar elemento, Eliminar elemento, Eliminar repetidos, Buscar elemento, Limpiar. Invertir retirado de menú/metadata/API/wrapper/C/H/mapa; no se creó una opción nueva.

## Dependencias y APIs ocultas restantes
La comprobación previa no encontró llamadas productivas desde los siete métodos visibles a invertir; sus únicas raíces eran operación legacy propia, export C y pruebas. Esas raíces se retiraron por autorización expresa.

Se conservan helpers reales: CrearNodoLista reserva nodos; insertar_elemento requiere insertar_inicio; limpiar y eliminar_repetidos implementan recorridos propios, sin inferir una llamada compartida a lista_eliminar_elemento; metadata de wrappers mantiene tamaño/cola. No eliminar funciones por ausencia del menú.

Lista: buscar_posiciones, eliminar_final, eliminar_inicio, eliminar_posicion, eliminar_primero, insertar_elemento, insertar_posicion, mostrar, primero, ultimo siguen como APIs hidden aceptadas. Algunas comparten implementación con métodos visibles; eliminar_inicio es dependencia de eliminar_final y eliminar_posicion en el wrapper. Sus raíces API vigentes hacen ambigua su retirada global. Es necesario decidir si se retiran contratos legacy, conservando los helpers que compartan implementaciones. Prioridad: frente sigue como API hidden con contrato C y pruebas nativas; sin decisión de retirada. No se eliminaron estas once por ser ocultas.

## Calidad/documentación
Descargas actuales sin lista_invertir y con Doxygen sin advertencias individual/colectivo. Eliminar el método no demuestra exactitud global de todos los símbolos ni prueba nativa por instrucción de los siete métodos; esa auditoría continúa.

## Revisión estática de once API
Evaluadas las once: cero API demostradas muertas; once contratos HTTP vigentes ambiguos para retirada. Ver evidence/visible-linked-clear-review/hidden-api-dependency-review.md y JSON con SHA/callgraph. eliminar_inicio es helper de dos métodos wrapper; insertar_elemento comparte implementación visible. El wrapper insertar_posicion no atiende la API homónima y requiere decisión de compatibilidad pública antes de retirarlo. No se eliminaron contratos ambiguos.


## Nueva decision vigente: limite educativo Graph30 (2026-10-05)

Fuente autorizada: graph-educational-limit30-decision-low.md y assignment
coordination-graph-educational-limit30-low-20261005. Sustituye el alcance100de
performance y200de generacion, no los resultados historicos ni contratos C/H.
Nuevas inserciones/extremos implicitos/generacion/comparacion: maximo30vertices
 distintos; IDs int32 no se limitan a1..30.31se rechaza sin estado/resultado/RNG/
 historial nuevos y con ceroCejecutado. Legado>30se preserva en replay, main y
 descargas; lectura/reduccion explicita permitidas, inserciones/algoritmos
 bloqueados hasta volver a30. Ningun cierre global se deriva de este cambio.
Matrizdelta: evidence/visible-graph-educational-limit30-low/capacity-contract-matrix.json.

## Supersesión vigente MAX15 (2026-10-06)

La decisión graph-max15-only8-current-user-decision-low.md sustituye el límite30 anterior por15 vértices distintos;16 se rechaza antes de C/estado/historial. Legado mayor se conserva y sólo permite lectura/reducción hasta volver al dominio. Campaña autorizada de algoritmos limitada a ocho vértices; no pruebas15/20/30 ni adopción privada Bellman. Entrega final y reservas: criteria18-19-final-max15-technical-handoff-low.md. El apartado30 anterior permanece como historia fechada.
