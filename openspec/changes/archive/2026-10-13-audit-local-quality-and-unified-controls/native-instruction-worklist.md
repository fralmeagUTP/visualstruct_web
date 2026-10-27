# Trabajo nativo por instrucciÃ³n pendiente â€” priorizaciÃ³n basada en riesgo

No declara cobertura exhaustiva de caminos. Reutilizar instrumentaciÃ³n sobre copias descargadas, eventos por ocurrencia y punteros identificados antes de free; comparar snapshots backend, resaltado/consola/DOM y replay sin POST.

1. Listas enlazada/circular/sublista: inserciÃ³n y eliminaciÃ³n inicio/interior/final, giro de enlaces, cierre de ciclo, sublista vacÃ­a, mÃºltiples coincidencias y memoria. Reutilizar observador de nodos de Cola/Prioridad; aÃ±adir guardas de ciclo.
2. ABB/AVL: bÃºsqueda vacÃ­a/ausente, inserciÃ³n duplicada, eliminaciÃ³n hoja/un hijo/dos hijos; AVL LL/RR/LR/RL. Capturar frames recursivos y retornos, root/child aliases, alturas antes/despuÃ©s.
3. Rojo-negro: inserciÃ³n recolor/rotaciÃ³n y eliminaciÃ³n con propagaciÃ³n del doble negro; revisar casos reales de C, sin asumir reconstrucciÃ³n.
4. MontÃ­culo: ascenso/descenso, extracciÃ³n Ãºltima/empates, lÃ­mites de capacidad y arreglo tras realloc.
5. Grafos: BFS cola y DFS recursiÃ³n; Dijkstra relajaciÃ³n/inaccesibles/rechazo negativo; Bellman-Ford iteraciones/ciclo negativo; Prim selecciÃ³n/arcos; Kruskal orden/Union-Find. BFS -1 pendiente de decisiÃ³n; demÃ¡s casos independientes continÃºan.
6. Hash: módulo negativo, colisiones, reemplazo/eliminación; H1 entero/capacidad fija aprobado y reconciliado documentalmente. Fidelidad por instrucción, cobertura funcional y legacy pendientes. Sin rehash nuevo.
   Nota histórica sustituida por H1 (2026-10-02T18:12:42.165328+00:00): 6. Hash: mÃ³dulo negativo, colisiones, reemplazo/eliminaciÃ³n; conservar claves enteras/capacidad fija. ContradicciÃ³n documental pendiente de consolidaciÃ³n, sin rehash nuevo.
7. Once ordenamientos: comparaciones, swaps, recursiÃ³n/particiÃ³n/mezcla, temporales y conteo/buckets, Ã­ndices sin mutaciÃ³n y memoria. Cubrir vacÃ­o, duplicados, negativos cuando admitidos y lÃ­mites.

Cada familia requiere casos reproducibles con eventos nativos independientes y matriz que identifique operaciones/caminos no observados. Las comparaciones de estado final anteriores no cierran estas tareas.


## Caso visible completado: Lista enlazada / Limpiar
Cuatro semillas con 36 observaciones nativas y 192 observaciones UI por instrucciÃ³n en ambas vistas/replay; parÃ¡metros, raÃ­z, identidades, enlaces, desconexiÃ³n y free verificados. Los otros seis mÃ©todos visibles de Lista y las otras familias continÃºan pendientes. Evidencia visible-linked-clear-review/after-fix.


## Caso visible completado: Lista enlazada / Eliminar elemento
8 casos/76 eventos nativos y 428 observaciones ambas vistas/replay. Identidad, parÃ¡metro/cabeza, p/ant, desconexiÃ³n/free y salida del Ã¡mbito resueltos sin cambios C. Evidencia visible-linked-delete-one-review/after-fix. Los demÃ¡s mÃ©todos/familias no se declaran cerrados.


## Caso visible completado: Lista enlazada / Eliminar repetidos
8casos/122eventos nativos y576observaciones ambas vistas/replay, identidad q/ant/temp, mÃºltiples unlink/free y Ã¡mbito resueltos. Evidencia visible-linked-delete-all-review/after-fix. Otros mÃ©todos/familias continÃºan pendientes.


## Tres inserciones visibles y familia Lista: checkpoint verificado
153eventos/16casos cero diferencias completas;748observaciones UI.128pruebas+4E2E anteriores aprobadas. Familia siete métodos:41casos/457eventos/2192observaciones UI de caminos registrados; no exhaustiva. Global 13/22 sin casillas nuevas. Evidencia evidence/visible-linked-three-insertions-review/after-fix/verification.md. Se cierra MEDIUM acotado; próxima continuación LOW. Circular/otrasfamilias/manual/main generado pendientes.


## LOW: main de Lista y documentación circular
Main real compilado contra descargas:18historiales/7métodos,2tests aprobados y9manual/ayudas. Correcciones decimal/firmaBuscar/espacioASCII, no cambioC. Ver evidence/generated-linked-main-review. Cuatro contratos circulares documentados/verificados; ledger12/208completos,196pendientes; C/H Doxygen aislado0warnings y compilación estricta. CircularInsertarinicio baseline36eventos+Insertarfinal36: próximos2métodos requieren MEDIUM acotado alias/heap/publicación/cantidad y ambosDOM. Global 13/22; no traza circular modificada.


## Circular: MEDIUM acotado terminado
Dos inserciones visibles verificadas:8casos/112eventos nativos (72métodos+40constructor),544observacionesUI,77tests aprobados108.32s. C/H sin cambios. Identidad/alias/enlacesparciales/cantidad/ramas exactas/scope/ambasvistas/replay sin diferencias. Ver evidence/visible-circular-two-insertions-review/after-fix/verification.md. VolverLOW inmediatamente. Otras5operaciones circulares pendientes; seguir main repetido y nombre de campo de tarjeta enLOW. Global 13/22 sin casillas nuevas.


## LOW: historial de búsquedas y contratos Circular
6 tests de búsqueda/repetición y2 regresiones posteriores aprobados; búsquedas Lista/Circular conservadas sin reejecución en GET. C/H Circular14/14contratos individuales revisados, compilación estricta y2Doxygen0warnings,5tests de contratos/guardas nativas. Ledger22/208revisados,186pendientes; no cierre global de manual/Doxygen. Global 13/22. Ver evidence/successful-search-history-review y circular-fourteen-document-contracts. Próxima fidelidad Circular: Buscar sin mutación necesita estrategia de snapshots; otros3métodos con cambios de enlaces/liberación siguen pendientes.


## LOW: Buscar Circular verificado
5casos76eventos nativos,384filasUI ambasvistas/replay,19tests nativos/servicio y3finales UI/servicio. Heap sin mutación, cursor/buffer/escalares/retorno/scope exactos; noPOSTextra. Ver evidence/visible-circular-search-review. Circular4/7escenarios de métodos; otros3siguenpendientes (eliminar primero99eventos/invertir44/limpiar56). Documentación22/208revisada,186pendiente. Global 13/22; finalgate agregado sigue abierto.


## Circular Eliminar primero: MEDIUM acotado completado
Método visible verificado:8casos99eventos nativos,540filasUI ambasvistas/replay,26tests finales pasan123.04s. Identidad actual/anterior,unlink/cantidad/free/ramasfisicas/retorno exactos. C/H intactos. Ver evidence/visible-circular-delete-first-review. VolverLOW inmediatamente; Circular5/7escenariosdemétodos, invertir44eventos y limpiar56eventospendientes. Global 13/22; documental22/208sin nuevas casillas.


# Circular: cierre de escenarios registrados

Invertir y Limpiar son métodos visibles existentes, no la inversión de Lista enlazada retirada. Ambos conservan el algoritmo C/H. 8 casos adicionales: vacío, único, tres distintos y duplicados para cada método. 44 eventos nativos de Invertir y 56 de Limpiar; compara identidad, heap completo, raíces, alias, enlaces, cantidad C separada de accesibilidad, condiciones y línea física. Invertir conserva las reservas; Limpiar separa unlink y free, no lee memoria liberada y distingue salida de ámbito.

103 pruebas pasan en121.85s en revisión conjunta con los cinco métodos previos, contratos descargados y68 regresiones secuenciales. 584 filas UI adicionales: ambas vistas, adelante/atrás, estados y líneas; cero POST de replay y cero errores JS. Captura linked de Limpiar inspeccionada: último free, raíces NULL, cantidad0, alias actual/next indeterminados y reserva liberada sin lectura. Evidencia automatizada de Invertir incluida; revisión visual manual de su captura aún pendiente.

Circular7/7 métodos en33 casos registrados,415 eventos nativos incluidos40 de constructor. No certifica todos los caminos ni todas las TAD. Global 13/22 y documentación22/208 siguen abiertos. Sanitizadores y WebKit no disponibles; revisión final agregada del aplicativo aún pendiente.


# Sublista: línea base y corrección focal en LOW

Inventario visible: Insertar padre, Insertar hijo, Eliminar padre, Eliminar hijo, Listar hijos y Limpiar. Se instrumentó C/H realmente descargado con registro de reservas padre/hijo, campos inicializados y enlaces completos. 24 escenarios,387 eventos. Se observan helpers de creación, búsqueda, copia y destrucción necesarios; no características ocultas nuevas. GCC C17 Wall/Wextra/Wpedantic/Werror. No se dereferencia memoria liberada ni campo sin inicializar. Condiciones sin efectos se evalúan dos veces, conservando resultado. Alias se guardan por frame y se invalidan como IDs enteros al liberar.

Corrección concreta: planificador Eliminar hijo usaba previo en lugar del anterior del C; omitía while/avance/guarda predecessor y elegía return de la guarda vacía para ausencia posterior. Ahora reproduce cada iteración, condición y enlace físico del C. Proyección reconoce anterior->sgte al desconectar. C/H conservan algoritmo. 6 casos nativos verifican secuencia física, condiciones y valores alcanzables, incluidos primer duplicado, último hijo, ausencia, padre sin hijos y padre inexistente/vacío. 2 casos de navegador verifican ambos modos, adelante/atrás, DOM de padres/hijos, valores contra C, highlight y no POST extra. 192 filas UI, 132 contrastadas también con evento nativo. 75 pruebas finales pasan:6nativas+1E2E2casos+68regresiones secuenciales. Cero errores JS.

Se corrigió selección DOM del observador: first-of-type no correspondía al campo HIJO porque el identificador era el primer div. La aserción exacta se mantiene. Un ensayo posterior quedó invalidado al añadir comentarios C/H durante su ejecución: desplazó índices físicos usados por el observador anterior. Se preservan registros, pero ninguno cuenta como defecto de producto o resultado final. La prueba coherente posterior fija la misma revisión para observador y aplicación.

Doxygen/descargas: source/header HTTP coinciden byte a byte con D:;0warnings en dos corridas aisladas, compilación estricta. Documentación de insertar_hijo/eliminar_hijo cambia lista a in,out porque mutan enlaces internos; eliminar_hijo y helper explican primera coincidencia, propiedad y guarda NULL. Revisión individual de eliminación incluye ambos contratos, no certifica otros símbolos ni manual completo.

Límites importantes: full_heap_identity_not_represented es ausencia de representación por observación, NO364defectos distintos. Aún falta identidad estable de hijos, raíces/sub/sgte, alias y ámbito entre wrappers/helpers en UI. Otras diferencias físicas y condiciones de inserciones/listado/limpieza requieren casos focales; comparar instante de llamada antes de entrar vs retorno después del helper antes de clasificar diferencias de Limpiar. mallocfailure y dirección top-levelNULL no inyectadas, buffer copiado pendiente. No toda Sublista aprobada, ni cierre global;13/22.

Siguiente caso difícil propuesto: Eliminar hijo, identidad padre/actual/anterior, reservas desconectadas/free, scopes buscar_padre y helper, ambas vistas y replay. Bounded MEDIUM solo para ese modelo de dos tipos de reservas; volverLOW al terminar. Otros símbolos/documentación pueden continuarLOW.

Documentación individual24/208;184pendientes.


# Sublista Eliminar hijo: MEDIUM acotado, verificación terminada

6casos existentes: primer duplicado3, último5, hijo99 ausente, padre8 sin hijos, padre99 ausente y lista principal vacía. 98eventos C independientes, contando entrada y finalización de llamadas como momentos distintos de la misma instrucción. No son16operaciones nuevas. C/H sin cambios de algoritmo, tokens idénticos. Oráculo C17 Werror conserva reservas separadas padre/hijo, máscaras de campos inicializados, y IDs enteros antes de free: no lee memoria liberada ni punteros indeterminados.

Heap por identidad estable P/H. Los padres conservan sgte/sub, los hijos sgte; padre->sub o anterior->sgte desconecta solo la primera coincidencia; hasta free la reserva sigue viva aunque ya no sea alcanzable. free elimina solo actual, que queda indeterminado hasta salir de ámbito; anterior y todas las demás ramas permanecen intactas. No se renumera el segundo duplicado al eliminar el primero.

Se separan llamada y finalización en la misma línea física: padre permanece sin asignar durante buscar_padre; su resultado se asigna al volver. El envoltorio retorna bool solo después del auxiliar; no se muestra un resultado de búsqueda como si fuera retorno bool pendiente. El stack distingue parámetros Nodo* y locales Sublista*, y registra pila antes/después de return. Call-site repeated highlighting representa la continuación de una llamada, no repetición de efectos C.

La comprobación UI detectó una fuga al rebobinar Paso0: callback tomaba memory_state del primer evento aunque recibía state_snapshot anterior. Corregido solo para este modelo de Sublista; ahora ambos modos restauran el estado anterior sin locales iniciados ni cambios adelantados. El validador final_state se conserva: última frontera canónica API, proyección educativa retiene heap vivo y elimina ámbitos, sin fabricar free al retornar.

81pruebas finales aprobadas:12nativas(6fuente+6heap/alias/scope)+1E2E+68regresiones secuenciales. 404filasUI ambas vistas/adelante/atrás y 300 contrastes UI adicionales con evento nativo. 4casos exitosos replay;2casos padre inexistente/vacío conservan error y navegación deshabilitada, sin convertir rechazo en nueva experiencia de ejecución. CeroPOSTextra durante replay y ceroerroresJS.

Píxeles linked tras unlink del primer3 inspeccionados: raízP1,padreP1,actualH1.1,anteriorNULL; P1.subH1.2, H1.2->H1.3, H1.1desconectado siguevivo con sgteH1.2; padresP2/P3 y sus hijos intactos. Captura current trasfree muestra H1.1liberado, actualindeterminado, sinlecturadememoria.

Límites: escenarios registrados, no todas las combinaciones/NULLtop-level/mallocfailure. Eliminar hijo es1/6métodos de Sublista con identidadreplay certificado para estos casos; las otras operaciones continúan abiertas. Quedan tareasLOW de presentación: título largo del card desconectado se superpone en captura estrecha; encabezado de progreso muestra raíz de call_stack en lugar de función activa del último frame. Candidato adicional de descarga main observado en píxeles: InsertarPadre debe verificarse compilando descarga real, no afirmar defecto sin esa comprobación. Auto-scroll de línea requiere comprobación tras animación, no concluir de una captura inmediata. No modificar otros métodos dentro de este bloque MEDIUM.

Global 13/22; documentación24/208. MEDIUM termina en este checkpoint, volverLOW inmediatamente. No push/merge/deploy.


# Sublista: main real, documentación individual y ajustes visuales

18 pruebas conjuntas aprobadas54.92s (12oráculo Eliminar hijo,2historialLista/Circular,1historialSublista,1contratosC/H,1mainE2E,1visualE2E). 26 programas main compilados/ejecutados,13 operaciones sucesivas cubren6métodos visibles, duplicados padre/hijo, campos decimales0007/008/003/-009, consulta repetida, reload después de cada operación, fallos y sesión aislada. GCC C17 Wall/Wextra/Wpedantic/Werror. El historial produce cada operación exitosa una vez; reload no ejecuta consultas. Los resultados de consultas se calculan al ejecutar C, no se precargan del resultado Python.

Aclaración de producto: C/H sí son archivos descargados víaHTTP; main es un fragmento mostrado/copiable, NOun archivo de descarga independiente. Se compila el fragmento DOM real con stdio.h y tad_sublista.h, junto al C descargado, siguiendo la guía. Solo el observador añade medición antes de return y limpieza final. Se mantienen intactas las llamadas del main. Línea base falló por InsertarPadre inexistente: ahora6nombres son funciones públicas reales; hijos usa Nodo* por valor, consulta tiene arreglo destino/capacidad y presenta lo realmente copiado. Se conserva consulta exitosa Listar hijos trasreload y se descarta consulta fallida/malformada; no se ejecuta de nuevo al reconstruir.

Cuatro capturas de unlink/free y ambas vistas verifican identificadores cortos sin solapamiento/overflow, función activa de último frame en progreso y línea C visible dentro del panel tras la animación de scroll. Píxeles linked/unlink inspeccionados: H1.1desconectado vivo muestra nro3 y sgteH1.2 sin título superpuesto; headP1/subH1.2 y ámbito auxiliar correctos. NoPOSTextra.

Revisión individual de19funciones C de Sublista, incluidas4privadas requeridas, contrastada con declaraciones H. Correcciones son notas de contrato: NULL, falla malloc sin publicación, primera coincidencia/duplicados, propiedad hijosantespadre, inicialización sinfree, copia acotada (no total cuando se trunca), buffer NUL/truncamiento. Test C/H real comprueba fallos de reserva, guardas, canarios, valores repetidos/identidades distintas, orden de liberación y9reservas/9liberaciones sinleer memoria liberada. Código de cada función y documentación revisados: no certificado de todos los caminos ni instrucciones UI. DoxygenaisladoC/H0warnings y compilaciónestricta; bytesHTTP==D:.

Guía distingue consulta, primer padre, límite destino y preparación de main.c. No declara manual completo del aplicativo. Documentación individual41/208;167pendientes. Global 13/22; no nueva casilla global porque26C/H/manual/oráculos de otrosTAD siguen abiertos. Eliminar hijo1/6métodos Sublista con identidad/replay porcasos; los restantes5están cubiertos funcionalmente/main/contratos pero no se certifica identidad porinstrucción.

El registro sublist-low-final quedó solo con cabecera y ningún proceso activo: ejecución perdida, no resultado aprobatorio. Recuperación sinproceso duplicado con python-u y registro durable pasó18pruebas; registros conservados. Los26mains de prueba individualprevia se mantienen como evidencia histórica sinsumarlos otra vez al agregado.


# Sublista: límite de consulta y rama vacía verificados en LOW

23pruebas finales58.43s. 26mains con formularios/reloads cubren6métodos visibles; un programa adicional usa rendererreal e historia válida con1025hijos, backendreal directo y C/HHTTP para no ejecutar1025reconstruccionesHTTP. Ambos copian1024valores y el C conserva1025hijos: consulta no muta. Capacidad generada min(1024,max(1,insercionesprevias)) respeta el límite real existente; guía lo documenta. No cambia algoritmo ni contrato de TAD C, que admite capacidades de otros llamadores.

Se corrigieron dos instrucciones omitidas al listar padre sin hijos: actual=padre->sub y evaluación whilefalse ocurren después de guarda válida; no es retorno temprano. Cuatro casos/50eventos nativos pasan fuente física/condiciones/valores alcanzables. No se certifica todavía el buffer por instrucción ni alias/heap/replay de Listar hijos. Eliminar hijo conserva12pruebas fuente/heap; otros métodos tienen baseline independiente: Eliminar padre6casos113eventos, Insertar padre2casos28eventos, Insertar hijo4casos56eventos, Limpiar2casos58eventos.

Siguiente caso requiere MEDIUM acotado: Eliminar padre, solo6casos113eventos, raíz Nodo** y padre desconectado aún vivo; destruir_hijos recibe dirección de sub, actual exteriorNodo* y actual interiorSublista* en ámbitos separados, unlink/free hijos antespadre, ambas vistas/replay. Reusar infraestructura comprobada sin modificar C. El resto permaneceLOW.

Doc19/19Sublista y41/208global; global13/22 sigue abierto. Maines ahora27programas únicos en el agregado (26forms+1boundary), no sumar resultados históricos duplicados. Fuente, contratos, UI y límites permanecen trazables en evidencias anteriores. No push/merge/deploy.


# Eliminar padre de Sublista: instrucciones, ámbitos y replay verificados

Seis casos registrados: primer padre con tres hijos, padre interior sin hijos, último padre con dos hijos, padre inexistente, lista vacía y padres duplicados. 121 observaciones nativas; la línea base de113 se amplió con8 observaciones de entrada/completado de llamada y cierre de auxiliar, sin sumar operaciones nuevas. Algoritmo C/H sin modificaciones; C descargado SHA256 644c9868b2baadfbd52c577b903a63aeb045f3a55654ace1e0fdfe716ce6a0ab.

El oráculo observa todas las reservas vivas, enlaces, raíz, alias enteros salvados antes de free, todos los frames y retorno bool real. No lee punteros liberados ni campos sin inicializar. Compara identidades por reserva, no por valor repetido ni orden de enumeración. Padre desconectado sigue vivo y conserva propiedad mientras se liberan hijos; *lista_hijos modifica su campo sub. Los dos actual coexisten: Nodo* del llamador suspendido y Sublista* del auxiliar. Retorno void del auxiliar restaura ámbito del padre; bool verdadero/falso del método retorna al llamador sin fabricar liberaciones.

Se corrigió pérdida/confusión de ámbitos en tablas pedagógicas: variables y punteros se identifican por (función,nombre), muestran tipo y ámbito, conservan locales suspendidos y marcan fuera de ámbito únicamente al finalizar ese frame. El cierre físico del auxiliar conserva call_stack antes y después. UI agrupa padre desconectado e hijos todavía vivos y separa reservas liberadas sin leerlas.

Paso0 tenía fuga de ámbitos del primer evento: dos pruebas fallaron mostrando2/3variables futuras. Corregido al cargar y rebobinar padre/hijo en ambas vistas: estado inicial explícito, ninguna instrucción ejecutada, sin ámbitos/variables futuros. La línea resaltada en Paso0 aún no se ha ejecutado; después de avanzar identifica la instrucción recién ejecutada y su estado causal posterior.

93 pruebas conjuntas aprobadas en revisión final focalizada:6oráculo padre,16regresiones nativas compartidas,1E2E padre,2Paso0 padre/hijo y68regresiones secuenciales. 604filas UI, 472contrastes con eventos nativos; ambas vistas adelante/atrás, heap y campos, todos los alias/ámbitos/tipos, doblepuntero, resaltado físico y consola vacía, endpoint y ausencia dePOSTde replay/erroresJS. El agregado anterior de2E2E pasó449.90s y conserva604filas padre+404filas hijo; resultados históricos no se suman otra vez. Replay final utiliza click() de botones DOM habilitados para evitar tiempo de auto-scroll al botón de navegación, sin acceder directamente al intérprete ni reducir aserciones; ejecución y selección de controles usan Playwright. Panel Variables C abierto y visible.

Se conserva el primer falso fallo del comparador por orden de enumeración del heap en sublist-parent-resumed-native.log, SUPERADO por comparación exacta por identidad en sublist-parent-resumed-comparison.log. No fue cambio de C ni supresión de campos/enlaces. Las dos pruebas negativas de Paso0 se conservan también.

Captura enlazada del primer free de hijo inspeccionada por píxeles: raízP2, actual exteriorP1 Nodo*, actual interior indeterminado Sublista*, *lista_hijos=P1.sub=H1.2, P1desconectado y H1.2/H1.3vivos, H1.1liberado; P2/P3 intactos. Capturas finales adicionales incluidas; no declarar inspección manual de todas ellas.

Cobertura Sublista por instrucción/identidad/replay:2/6métodos en escenarios registrados (Eliminar hijo y Eliminar padre). Insertar padre, Insertar hijo, Listar hijos y Limpiar siguen abiertos; fuente/condiciones de Listar hijos tienen comprobación parcial anterior. Documentación de19contratos Sublista ya revisada, incluidos eliminar_padre y destruir_hijos; este bloque añade evidencia pedagógica, no aumenta41/208. Global 13/22 sin nuevas casillas porque oráculos/manual/C/H de toda la aplicación y revisión final siguen pendientes. No certifica todos los caminos, NULLtop-level ni herramientas no disponibles. No push/merge/despliegue.


# Sublista: Limpiar y Listar hijos por instrucción, LOW

Limpiar2casos/66eventos nativos (lista vacía y3padres con5hijos); Listar hijos4casos/60eventos (padre con3hijos repetidos, padre sin hijos, padre inexistente y lista vacía). Se reutiliza el modelo verificado de identidad/ámbitos; C/H y sus algoritmos permanecen intactos. Se amplían observaciones de entrada/completado de llamadas y cierre físico de funciones, no operaciones nuevas.

Limpiar ahora sigue el C exacto: cabeza vacía no retorna en la guarda lista==NULL; evalúa actual=*lista, whilefalse y cierre void. En lista poblada, cada padre permanece alcanzable durante la destrucción de sus hijos; next exteriorNodo* y next interiorSublista* son independientes. Después del auxiliar, *lista=next desconecta padre, free lo libera y actual=next avanza. No se fabrica *lista=NULL ni return en una guarda que fue falsa; el cierre de ámbito no libera memoria.

Listar hijos observa todas las reservas/enlaces inmutables, alias/ámbitos, constNodo*/constSublista*, int*destino, capacidad1024 real de la aplicación, intusados y cada posición escrita. destino[usados]=actual->nro copia un int sin cambiar estructura; usados++ es otra instrucción. El arreglo presenta únicamente posiciones ya escritas, nunca el resultado futuro completo. El retorno de copiar es cantidad copiada; el wrapper retorna esa cantidad. Padre inexistente retorna el int-1 del C, no NULL procedente de búsqueda previa: dos regresiones negativas demostraron y corrigieron esa proyección. APIrechazo y botones deshabilitados se conservan, no se añade replay a fallos que antes no lo tenían.

El oráculo anterior de consulta usaba capacidad128 y solo certificaba fuente/condiciones/valores pequeños. El nuevo oráculo usa1024 como el wrapper real y verifica capacidad, usados, escrituras y entero de retorno. Conserva evidencia anterior como parcial, no la presenta como verificación de buffer/alias. El límite1025hijos→1024copiados del main sigue cubierto por evidencia anterior; este bloque no recorre todas sus instrucciones ni todas las capacidades de llamadores externos. No lee campos sin inicializar ni reservas liberadas; output nativo está inicializado en el arnés pero solo se comparan posiciones realmente escritas.

100 pruebas conjuntas pasan251.69s:6nativas nuevas,22regresiones nativas previas,2E2E(nuevosmétodos yEliminar padre),2Paso0 y68regresiones secuenciales. Inspección de píxeles después encontró narración intermedia que aún llamaba link a copia pese a conceptoAssignment: corregida en los tres niveles, con9pruebas focalizadas posteriores131.71s (6nativas,1E2E,2Paso0). No se suman como109pruebas únicas ni se declara suite global final. La prueba E2E abre Comprender y verifica texto de copia visible; el nivel visible predeterminado es intermedio, los tres textos se verifican en el contrato API.

530filas UI =528estados de4casos exitosos en ambas vistas adelante/atrás+2rechazos preservados. 412contrastes UI con observación nativa; heap, raíces, enlaces/campos, todos los alias/ámbitos/tipos, escrituras al buffer, resaltado, consola vacía, endpoint, Paso0 sin datos futuros. CeroPOSTde replay y ceroerroresJS. Se conserva el falso fallo inicial de comparador DOM (usados es atributo textual0 frente al entero0) y el fixture vacío que intentaba rellenar child en consulta que solo pide parent; ambos corregidos en arnés sin reducir condiciones reales ni alterar producto.

Captura linked de primera escritura inspeccionada: destino[0]=3, usados0, actualH1.1, capacidad1024, wrapper suspendido/auxiliar const activo, todas las ramas/enlaces intactos, línea exacta de copia resaltada, sin salidaC. Primera captura mostró captionlink contradictorio; corregido y E2Erevalidado, no se declara inspección manual de todas las capturas.

Sublista4/6métodos por instrucción/identidad/replay en escenarios registrados: Eliminar hijo, Eliminar padre, Listar hijos y Limpiar. Quedan dos inserciones visibles:6casos/84eventos línea base;79observaciones sin heap completo y2retornos físicos de rama incorrecta. Ejemplo real trasmalloc: máscara nativa0 (nro/sgte/sub aún sin inicializar; 0/-2 son sentinelas del observador, no lecturas de esos campos); metadata previa dibuja nextNULL y carece de ámbitos. Requiere revisión semántica acotada de inicialización, identidades y retornoNodo*/Sublista* desde constructor al llamador, hasta3ámbitos; no hay propuesta de cambiar algoritmo ni añadir métodos.

19contratos Sublista ya revisados, documentación global41/208; añade evidencia por instrucción para obtener_hijos/copiar_hijos/destruir, sin incrementar recuento documental. Global 13/22 porque verificación completa de TAD/resto del aplicativo y revisión final siguen abiertas. Sanitizadores/WebKit no disponibles; no instalar ni modificar seguridad. No push/merge/despliegue.


# Sublista: dos inserciones visibles verificadas, LOW

Insertar padre: lista vacía y lista con tres padres, incluida inserción de un valor padre repetido. Insertar hijo: padre con hijos, padre sin hijos, padre inexistente y lista vacía. Seis casos registrados; 102 observaciones nativas frente a84 de línea base. Se amplía observación de entradas/completados de llamadas y malloc, sin añadir métodos ni cambiar algoritmos C/H.

Se corrige selector de Insertar padre que comparaba Nodo con fuente normalizada a minúsculas y omitía el modelo de memoria. Pruebas estrictas iniciales fallaron2/6; tras corrección pasan6/6. Las reservas recién asignadas tienen nro/sgte/sub sin inicializar, noNULL ni valores futuros. El observador usa máscaras y no lee esos campos; sus valores0/-2 son sentinelas, no valoresC. Cada asignación inicializa únicamente su campo. El nodo permanece desconectado hasta publicar el enlace exacto. Heap separa reservas de nodos alcanzables; identidad es por reserva, nunca por valor repetido.

Constructores crear_padre/crear_hijo retornan la misma reserva; salir del ámbito no la libera. nuevo del llamador queda sin inicializar hasta completar la asignación de llamada. Hasta tres ámbitos separados preservan parámetros y locales suspendidos; nuevo de Nodo* y Sublista* tiene tipos correctos. La búsqueda asigna padre al volver; el wrapper retorna bool únicamente después del auxiliar. Se corrige retorno físico que usaba la rama vacía después de enlazar al final. Se corrige contradicción concepto link/evento heap stable; malloc es allocate y publicación es link.

7pruebas finales aprobadas:6nativas inserciones y1E2E inserciones. El agregado anterior dio34aprobadas y1fallida: *lista=nuevo tenía conceptoAssignment frente a eventoLink; corregido y revalidado por las7pruebas finales. Ese agregado incluía28regresiones nativas previas aprobadas. Antes de la extensión del observador y últimas etiquetas pasaron32regresiones compartidas, incluidos ambos E2E previos y Paso0. No sumar ejecuciones como pruebas únicas ni declarar agregado global final totalmente verde. 414filas UI: 412estados de4casos exitosos, vistas actual/enlazada adelante/atrás, más2rechazos preservados. 316contrastes con eventos nativos; heap/campos/enlaces/raíz, todos los ámbitos/locales/tipos/variables, resaltado físico, consola vacía y endpoint. CeroPOSTde replay y ceroerroresJavaScript. Paso0 no contiene ámbitos futuros. Fallos por padre inexistente/lista vacía siguen sin habilitar replay; no se añade comportamiento.

Inspección de píxeles de dos capturas enlazadas de Insertar padre: después de nro=valor, P4 separado muestra7 y sgte/sub sin inicializar; al retornar crear_padre, P4 sigue vivo/desconectado con punterosNULL y nuevo del llamador aún sin inicializar. Capturas adicionales automatizadas se incluyen sin afirmar inspección manual de todas.

Sublista6/6métodos visibles en24casos registrados con evidencia por instrucción/identidad/replay según los bloques previos y este. No certifica todos los caminos, NULLtop-level, mallocfallido ni todos los argumentos externos. C/H descargado conserva SHA registrado; contratos documentales19Sublista ya revisados, global41/208 sin incremento por repetir revisión. Global 13/22: otras familias, documentación completa y puerta de regresión final continúan abiertas. Sanitizadores/WebKit no disponibles. Sin push/merge/despliegue.


# ABB: linea base nativa y doce contratos documentales, LOW

52casos/1057eventos nativos sobre las12operaciones visibles. Se instrumentan copias C/HHTTP verificados byte a byte y se compilan GCC C17 Wall/Wextra/Wpedantic/Werror. Contar hojas y Validar se observan usando los auxiliares exactos mostrados por el servicio, agregados a la copia: NO estan en el C/H descargado, distincion explicita. No instalaron herramientas ni cambiaron algoritmos C/H.

| Operacion | Casos | Eventos nativos | Fidelidad por instruccion |
|---|---:|---:|---|
| insertar | 6 | 109 | abierta |
| eliminar | 11 | 202 | abierta |
| buscar | 5 | 44 | abierta |
| minimo | 3 | 18 | abierta |
| maximo | 3 | 16 | abierta |
| altura | 4 | 136 | abierta |
| contar_hojas | 3 | 38 | abierta |
| inorden | 3 | 100 | abierta |
| preorden | 3 | 100 | abierta |
| postorden | 3 | 100 | abierta |
| validar | 5 | 94 | abierta |
| limpiar | 3 | 100 | abierta |

Casos: vacio/unico, ramasizquierda/derecha yprofundidad, duplicado, busqueda encontrada/ausente, eliminacion ausente/hoja/unhijo/doshijos, sucesor inmediato y profundo con hijo derecho, recorridos/consultas, limpieza y extremos int. Los52arboles finales coinciden. Los resultados de busqueda/min/max/altura/hojas/recorridos coinciden en sus casos exitosos; Validar difiere enINT_MIN/INT_MAX. La interfaz rechaza duplicados/eliminacionesausentes/minmaxvacios antes de ejecutar TAD; el C tiene guardas/retornos distintos. No equiparar estas capas ni inventar replay de fallos.

Condiciones nativas se evaluan una vez; se capturan recursion/retornos, reservas conmascara de campos inicializados, enlaces y todos los alias por frame. free conserva soloIDsenteros de alias/raiz/enlaces anteriores; el observador no vuelve a leer punteros liberados ni campos sin inicializar. Asignaciones de llamada tienen observacion antes/despues. Los cierres/retornos implicitos void se observan. mallocfallido no se inyecta enesta matriz; si en pruebas documentales separadas.

Dos regresiones negativas reproducen defectos reales en backendactual: raiz global aparece al escribirnuevo->valor, antes del retorno/asignacion del llamador; malloccarece de heapindividual/identidad/campossin inicializar. Captura de pixeles muestra raiz7/tamano1/recorridos[7] mientras se resalta escritura devalor y lospunteros todavia no se inicializaron. Ambas regresiones estrictas fallan y quedan en evidencia para incorporarlas a tests al corregir. No se debilitan aserciones ni se presenta el bloque como aprobado. Un intento de pytestentreunidades selecciono raizWindows y fallo coleccion por junctions; se corrigio rootdir/confcutdir a workspace, sin revisitar rutas denegadas; el resultado posterior son dosfallos de producto, no permisos. Primer observador tambien tuvo fallo de comparador None, corregido y conservado sin clasificar como producto.

Contadores de linea base:744observaciones sinheap/aliasrepresentados,261ocurrencias no encontradas y60condiciones a revisar. No son1065defectos distintos ni todos implican error: se debe alinear ocurrencias/entradas/continuaciones y separar rechazos wrapperantesdelC. Ver findings.json. Validar requiere reconciliar limites exclusivosint con los extremos admitidos; no se cambia ese contrato sin decision. ABB solo tiene representacionarbol; las pestanas visual/codigo no son vistasindividual/enlazada. Esta carencia queda explicitamente pendiente, no fingir prueba de dosvistas.

Browser:74estados de insertarvacio/buscarprofundo/eliminardoshijos, adelante/atras, resaltadolinea y equivalencia DOMconbackendactual, ceroPOSTde replay y erroresJS. Es linea base de representacionexistente, NO equivalenciaC. Captura inspeccionada. Se corrige checkboxinterno residualvisible al ocultarlo sin retirar elestado/eventos usados por togglecontextual. Tresreplays y checkboxhidden verificados; otraspaginas jerarquicas siguen bajo puerta final.

Documentacion12/12funciones C/HABB revisada individualmente: duplicados/noop, reservasfallidas, retornos prestados, reconectar raizde retorno, sucesorcopiado conservaidentidad, aliasinvalidos, printfexacto/espaciofinal/sinsalto, liberacionpostorden sinNULLdel llamador y altura/niveles0vacio1hoja. Cuatropruebas focalizadas aprobadas4.84s, incluyendo dosregresiones documentalesprevias. Diezreservas/diezliberaciones nativas, fallo malloc inyectado, salidaestricta de los12simbolos. DosDoxygenaislados C/Hceroadvertencias y HTTPbytes==D:. Guia distingue CdeUI y explica auxiliares no descargados. Esto no cierra manualglobal ni fidelidad porinstruccion ABB.

Ledger53/208contratos individuales,155pendientes; antes41/208. Global 13/22 sincasillasnuevas. Proxima necesidadMEDIUMacotada: SOLO InsertarABB,6casos/109eventos (5exitosUI y1duplicado rechazado). Corregir reservaantesde inicializar/publicar, identidadesindependientesdevalor, framesrecursivos delmismofn, retorno/callerpublication y amboscomponentes de representacionacordados; preservaralgoritmoC yrechazoUI. Incorporar lasdos regresiones negativas y volverLOW al acabar ese caso. Busqueda/eliminacion/otras9operaciones permanecen abiertas. Sanitizadores/WebKit aun no disponibles; puerta final agregada pendiente. Sin push/merge/despliegue.


## ABB Insertar: cierre acotado por instruccion

Seis casos y 109 eventos independientes de C nativo contrastados: cinco inserciones visibles exitosas y un duplicado rechazado por la API; el contrato C del duplicado se verifica directamente sin fingir ejecucion UI. Identidad de reserva independiente de valor, campos sin inicializar, raiz del llamador, parametros/locales por invocacion, condiciones, llamadas, retorno y publicacion de enlaces/root quedan sincronizados. No se modifica el algoritmo ni los C/H descargados.

13 pruebas focalizadas pasan y las dos regresiones negativas historicas ahora pasan. Navegador recorre adelante/atras el arbol existente y paneles individuales de reservas/ambitos; no se inventan dos conmutadores de vista. Cinco llamadores C mostrados se compilan contra C/H HTTP reales con C17 y warnings como errores, y su salida coincide. El llamador mostrado explica la asignacion de raiz externa y no agrega otro metodo al menu/descarga.

El rechazo conserva su traza explicativa, arbol intacto y extremos de navegacion; no exige deshabilitar Siguiente antes de recorrer esa explicacion. La primera prueba nueva suponia erroneamente ausencia de traza y fallo; se conserva log y se reemplaza por verificacion mas concreta de rechazo/replay, sin cambiar contrato de duplicados.

C-ABB-PUBLISH-01 y C-ABB-HEAP-SCOPE-02 quedan corregidos SOLO para Insertar en estos seis casos. La linea base negativa anterior se conserva como evidencia historica. Validar INT_MIN/INT_MAX sigue pendiente de decision. Once metodos ABB restantes, revision responsive de tabla estrecha observada en captura, documentacion global y puerta final siguen abiertos. No significa certificacion exhaustiva. Global 13/22 y ledger 53/208 sin cambios.

Evidencia: evidence/visible-abb-insert-instruction-review/summary.json.


## ABB LOW: acceso a variables y operaciones de solo lectura

Tabla de variables: region con nombre accesible, foco visible y tabindex; los atajos globales de traza respetan su foco. Columnas de ancho fijo y texto envuelto permiten alcanzar Significado sin perder texto. Chromium verifica flechas de teclado, ultima columna completa y ausencia de overflow de pagina a 1366, 768 y 390 px. Se permite scroll local de tabla, no scrollbar horizontal de pagina/menu. Captura estrecha inspeccionada. Primeras dos pruebas detectaron bloqueo por atajos y columna demasiado ancha: corregidos, logs conservados. node --check aprobado. Preview 5051 sigue disponible; JS/CSS se sirven de D: sin reiniciar Python por estos cambios.

27 casos actuales de buscar, minimo, maximo, altura, contar_hojas, inorden, preorden y postorden: 377 pasos con arbol sin mutacion, resultado/estado final coherente con baseline nativo del mismo SHA C. No es signoff por instruccion: parametros, ambitos, retorno y consola por ocurrencia siguen pendientes. Hay divergencias de profundidad: minimo caso24 y maximo27 muestran tres frames aunque el C usa un solo frame iterativo; inorden36/preorden39/postorden42 muestran uno frente a cuatro nativos. Busqueda/altura/hojas tambien requieren reconstruccion real de invocaciones. La documentacion individual ABB12 ya revisada se conserva; no se incrementa ledger por repetir lectura.

Siguiente bloque dificil recomendado: recorridos inorden/preorden/postorden conjuntamente (9 casos, 300 eventos nativos de baseline), scopes recursivos y printf por instruccion/retorno, reutilizando identidades ABB. Pedir escalada acotada a MEDIUM solo para esa correccion, volver LOW al finalizar. Minimo/maximo iterativos pueden tratarse aparte sin inventar recursion. Eliminar y limpiar tambien siguen pendientes. Global 13/22 y ledger53/208 sin cambios; puerta final agregada abierta.

Evidencia: evidence/visible-abb-readonly-access-review; decision exacta en validar-decision.md.


## ABB: recorridos por instruccion, bloque acotado verificado

Inorden, preorden y postorden: nueve casos vacio/hoja/arbol ramificado y 300 eventos C nativos independientes (291eventos de instrucciones y9endpoints del llamador). Cada entrada introduce un parametro nodo del ambito F# correspondiente, incluyendo llamadas sobre NULL. Cada condicion coincide con C; los llamadores quedan suspendidos y retoman despues de cada retorno void. El cierre de la funcion termina solo su ambito, sin liberar reservas ni reconectar enlaces. Se conservan identidades, valores, enlaces, raiz y resultados finales; C/H descargados sin cambios (SHA en summary.json).

Resaltado: la linea identifica la instruccion en el limite del evento indicado, con estado posterior a ese evento. Una llamada tiene dos ocurrencias en la misma linea: call significa que la llamada se inicio y el padre queda suspendido; resume significa que retorno y se retoma el padre. return en la llave final de la funcion void muestra la salida implicita, sin inventar un return de puntero. El estado inicial no muestra parametros ni salida futuros. No atribuir estas transiciones a mutaciones estructurales.

Cada printf emite exactamente "%d " de la invocacion actual, incluido el espacio final y sin salto de linea. La consola publica el prefijo ejecutado, no el recorrido final anticipado; al retroceder vuelve al prefijo correspondiente. Se evita transformar stdout en lineas deduplicadas. No se agregan impresiones en reanudaciones o NULL.

23 pruebas focalizadas aprobadas: nueve nativas, una browser de los nueve casos, siete nativas previas de insercion, una browser de insercion y cinco contratos pedagogicos. La pasada nativa preliminar tuvo14aprobadas; son ejecuciones distintas, no sumar como37tests distintos. Browser verifica582registros adelante/atras de recorridos, parametros/variables por ambito, identidades/enlaces, DOM de arbol y reservas, linea C y stdout exacto. CeroPOSTextra de replay y erroresJS. La regresion de insercion conserva cinco llamadores compilados y rechazo duplicado. Capturas inspeccionadas y scripts/logs conservados. La inspeccion de pixeles revelo que elSVG recortaba nodos a la derecha pese a estar enDOM; se corrigio solo el canvas de recorridos con escala responsive. La prueba focalizada adicional fallo en overflowhorizontal de pagina a390px, despues de pasar geometria delSVG/nodos; no se declara aprobado el reflujo. Se conservan fallo y diagnostico para LOW. Las23pruebas del bloque pasaron antes del ajusteCSS; puerta geometrica final pendiente. No repetir suite global sin cambio relevante.

Representacion: arbolSVG existente y paneles individuales de identidades/ambitos, no dos conmutadores inventados. Se corrige la falsa pila unica de los recorridos en la linea base, SOLO para estos metodos/casos. ABB4/12metodos tiene verificacion por instruccion en casos registrados; buscar,minimo,maximo,altura,contar_hojas,eliminar,limpiar,validar siguen pendientes. Validar limitesint permanece sin cambios esperando decision. Global 13/22, ledger53/208 y puerta final global permanecen abiertos. Este bloque MEDIUM termina; corresponde regresar a LOW.

Evidencia: evidence/visible-abb-traversals-instruction-review/summary.json.


## ABB minimo/maximo: bloque iterativo LOW verificado

Se corrige la pila recursiva ficticia: C usa una sola invocacion y mientrasavanza cambia solo el alias local nodo. La raiz, identidades, valores y enlaces permanecen iguales. El retorno es el mismo puntero prestado a la reserva existente, no una nuevareserva, copia, liberacion ni reconexion. El guardNULL delminimo y elcortocircuito&& delmaximo se explican sininventarlecturas dereferenciadas.

6casos y34eventos nativos (28instrucciones +6endpoints) de vacio/hoja/arbolramificado. Dos contratosNULL se contrastan con elmodeloCdirecto porque la interfazrechaza arbolvacio antesdeejecutarC; no presentarlos como exitosUI. Cuatro consultasUI exitosas aportan44registros adelante/atras y dos rechazos conservados; ceroPOSTextra y erroresJS. Variables/alias F1, raiz del llamador, heap y lineaC sincronizados. Consola sinprintf enesta ruta, sinmensajesfabricados como stdout.

22tests nativos/contrato aprobados10.12s, 2browser relacionados88.92s (extremos y9geometriasrecorridos), y2guia/descargas aprobados2.38s. Sonpasadasfocalizadas distintas, no una suiteglobalfinal. Guiaexplica while sinrecursion/mutacion, aliasprestado, NULLenC yrechazoUI; C/HHTTPsin cambios, compilanC17strict y conservan12contratos documentadosincluyendoalloc/frees/salida. Captura inspeccionada. IdentidadesN# simbolicas, no direccionesreales; arbolSVG existente masreservas/ambitosindividuales, no inventar conmutadores.

ABB6/12metodos tienenverificacion porinstruccion en casosregistrados: insertar,minimo,maximo,inorden,preorden,postorden. Pendientes buscar,altura,contar_hojas,eliminar,limpiar,validar. Global 13/22 yledger53/208 sincasillasnuevas; no cerrar manualglobal por doscontratos revisados. Validar contratoINT_MIN/INT_MAXse mantiene sin cambios esperando decision.

Siguiente alcancepropuesto MEDIUMacotado: SOLO BuscarABB,5casos/44eventos baseline (incluye5endpoints); recursionesconretorno deexpresion, parametros nodo/valor porambito, cortocircuitoNULL||igualdad, retorno prestado oNULL y amboscomponentesderepresentacion/replay. Baselinecase8omisionNULLreduceprofundidad2a1, case10ausente4a3; native44actual noobserva limitepreciso antesde return abb_buscar(...). Añadir marcadoresobservacionalesprevios a esas6llamadas sin modificar algoritmo ampliaria eventos a50, no escenarios; documentar denominador. Revisar ese punto requiere razonar sobre suspension/retornoencadenado y observerindependiente, por eso se entregacheckpoint antesdecomenzarlo. No se iniciaMEDIUMenesteturno.

Evidencia: evidence/visible-abb-extremes-instruction-review.


## Minimo/maximo: contrato actual corregido y verificado en LOW

Correccion de un error de auditoria: la frase previa "sin ejecutar el TAD" era incorrecta. app/adapters/abb_adapter.py llama minimo/maximo; tad_wrappers.py:95-105 invoca abb_encontrarMinimo/Maximo y despues convierte None a ElementoNoEncontradoError. La aplicacion usa la implementacionPython delTAD; el Cdescargado se ejecuta aparte como oraculo independiente. Dos spiesconwraps confirman una llamada con raizNone y HTTP400 sin mutacion. No fingir que el proceso web ejecuta el binarioC del oraculo ni que el wrapper evita la consultaNULL.

Guia actual: while sinrecursion/mutacion, aliasprestado, CNULL y conversion de ese retorno a error de interfaz. La traza muestra ahora la consultaNULL real de3instrucciones porfuncion, sin convertir elHTTPerror enexito. C/H yalgoritmos sin cambios, mismosSHA. El unico ambitoF1 cambia suparametrolocal nodo durantewhile; guarda raiz ytodos losenlaces. Return entrega aliasprestado/NULL, sin reservanueva, free ni reconexion. Elmaximo respeta cortocircuito&& y no dereferenciaNULL.

26pruebas focalizadas de la revisionactual aprobadas en una pasada coherente:8extremos nativos/spy,1browserextremos,9regresionesnativasrecorridos,1geometriarecorridos,5contratospedagogicos,2guia/C-H descargados. Native6casos/34eventos=28instrucciones+6endpoints. Browser56registros adelante/atras para6casos,4exitos y2erroresconservados, incluyendo12registros deNULL. CeroPOSTextra yerrorJS; variables, alias, heap, root,linea y stdoutvacio verificados. El oraculoCcompila strictC17. Guia/descargastambiencomprueban12contratos individualesincluyendoreservas,liberacionesy salida. No son pruebasexhaustivas detodasprofundidades.

La geometria fallida390px ya fue corregida con la clase .hier-control-stage; evidence/visible-hier-control-wrapping-review aporta24configuraciones compartidas y9combinacionesSVG/viewport. La nuevapasada26repite geometriaconrenderizadoractual. No seocultan controles. Se conserva la evidencia histórica delerror de auditoria yse supera explicitamente por estearchivo.

ABB6/12metodos verificados porinstruccion en casosregistrados; global13/22 yledger53/208sin nuevascasillas. Cierre global/manual/sanitizadores/WebKit/ultima revision pendientes. Validar no se modifica: decisionINT_MIN/INT_MAX esperada.

Proximo bloque que necesita MEDIUMacotado: SOLO BuscarABB; cinco casos vacio,raizencontrada,ausentehoja,encontradoprofundo yausenteprofundo;44observacionesbaseline (39instrucciones+5endpoints). Retorno deexpresion recursiva requiere conservarpadres suspendidos hastaque elhijo devuelve aliasprestado oNULL, diferenciar parametronodo globalhead y valorporambito, explicarNULL||igualdad y<, noomitirinvocacionNULL. Las6llamadasencadenadas pueden requerir marcadoresindependientesantesdeexpresion eneloraculo; si seagregan pasar de44a50observaciones,sin ampliarcasos ni modificarCsemantico. Browseradelante/atras yconsolasinprintf. Estealcance sepropone y no secomienza enLOW.

Evidencia vigente: evidence/visible-abb-extremes-current-contract-review.


## BuscarABB: bloque MEDIUM acotado verificado

Cinco casos: vacio, raiz encontrada, ausente enhoja, encontrado profundo y ausente profundo. C/H descargados y algoritmo conservados. ElmodelointroduceambitosF# con nodo/valor propios, incluyendoNULL; padre suspendido conserva parametros hasta el retorno delhijo. NULL||igualdad respeta cortocircuito, sin leer nodo->valor cuandoNULL; rama< coincideC. Cada return propaga elmismoaliasprestado oNULL, sin copiar/reservar/free/reconectar nodos. Heap, enlaces y raiz permanecen iguales. Retornar delhijo no cambia el parametro nodo delpadre.

El oraculoindependiente compila elC real descargado conobservacion decondiciones/ambitos/retornos. Se agregan6marcadores antesde evaluar return abb_buscar(...), limitadosa esa funcion: baseline44observaciones pasa a50(45instrucciones+5endpoints), mismos5casos y ningunaampliaciondepaths. No se cambiaC/H. Se verifica cadaevento y profundidad, null, parametrovalor, heap/alias/result ycada salida deambito. IdentidadesN#simbolicas independientesdelvalor, no direccionesreales.

Llamador equivalente mostrado: int ejecutar_busqueda(ABBNodo* raiz) retorna abb_buscar(raiz,valor)!=NULL. No otro metodoTAD ni funcionañadidaaC/Hdescargados. ElpunteroretornoTAD se distingue del0/1delCllamador ybooleano expuesto porwrapper. Los5llamadoresmostrados compilancontraC/HHTTP constrictC17, ysu stdoutbooleano/inorden coincide conresultado/estadoAPI. Guiaexplica punteroprestado/NULL, conversionbooleanayausenciasinerror. API5casosHTTP 200successful incluidosnoencontrados. Llamadorintroduccion/call/conversionañade15pasos decontexto a45eventosdeinstrucciones=60pasosUI; no contarlos comoCdelTADoriginal.

Browser120registros adelante/atras, estados inicialessinvariablesfuturas, heap/raiz/SVGreservas, parametros/ambitos, resaltadolineafisica, consolavacia (buscarnohaceprintf), retornoprestado/NULL yconversionbooleanasoloal final. CeroPOSTde replay y erroresJS. Captura inspeccionada. Panelestado vivo eliminaambito alretornar; panelPila/retornos conserva contextodelainstruccion pero lo marca explicitamenteterminado. Retornoactivo yreconexiondelretorno se muestran porseparado: consultasnoreconectan. Laetiquetaanterior"Retornoyreconexionactivos" implicaba unefecto falso yse corrige, sin cambiar losflagsdelmodelo.

Pasada19pruebas aprobadas127.48s:10searchnativo/wrapper,1browsersearch,1browserinsercion afectadoporcaller-renderer,5contratospedagogicos,2guia/C-Hdocumentados. Despuesdelaclaracionvisual se ejecutan16pruebas actuales(search10+browser1+pedagogia5), resultadoen log actual; nosumar35comopruebasdistintas. Primera pasada15 tuvo4fallos deharness: spycontaba consultasduplicados de reconstruccionsession. Se conservafallo; conteoexactounallamadasepruebaenwrapper aislado conTADreal, yHTTPresultado/estado se verificanseparados. No se debilitanaserciones nativas ni se clasificaesteconteocomoerrorC.

ABB7/12metodos porinstruccion en casosregistrados: insertar,buscar,minimo,maximo,inorden,preorden,postorden. Pendientesaltura,contar_hojas,eliminar,limpiar,validar. Global 13/22 yledger53/208sin casillasnuevas; manualglobal ypuertafinal siguenabiertos. Validar contratoextremosint se dejaesperandoaprobacion. Este bloqueMEDIUM termina; corresponde regresar aLOW inmediatamente. Sin push/merge/despliegue.

Evidencia: evidence/visible-abb-search-instruction-review.


## Fresh LOW height/leaves baseline

7 cases / 174 native observations; final results and trees agree. Instruction fidelity remains pending. See evidence/visible-abb-height-leaves-low-baseline/summary.md. Next proposed bounded MEDIUM case: height initializer locals and recursive return propagation; leaves evaluation order is separately pending. Counts remain 13/22 tasks, 7/12 ABB methods, 53/208 documentation symbols.


## Altura ABB verified bounded checkpoint

5 cases / 196 native events / 412 Chromium forward-back rows / 5 compiled equivalent callers; 48 related tests pass. See evidence/visible-abb-height-instruction-review/summary.md. ABB8/12 recorded instruction cases; remaining leaves/delete/clear/held validate. Global 13/22 and symbols53/208 unchanged. End MEDIUM here, return LOW.


## Hojas ABB LOW contract checkpoint

8 tests pass; actual helper body unchanged, five native/API cases, generated-helper Doxygen0 and manual order/operand clarification. Evidence: evidence/visible-abb-leaves-contract-low-review/summary.md. Instruction scopes/replay remain pending; bounded MEDIUM needed for permitted expression evaluation orders. Counts13/22, ABB8/12, symbols53/208 unchanged.


## Hojas ABB instruction/native/replay verified checkpoint

5cases/126nativeevents/272Chromium forward-back rows/5compiled displayed callers;27 related tests passed. Evidence: evidence/visible-abb-leaves-instruction-review/summary.md. Observed GCC left-first distinct from permitted model alternatives; no C locals invented. ABB9/12, global13/22, symbols53/208 unchanged. Download-helper gap remains open; next delete/clear/held validate. End MEDIUM here for LOW.


## LOW Limpiar / actual Hojas main checkpoint

Limpiar3cases100nativeevents finalemptyagreement; instructionfree/root/alias replay still pending, bounded MEDIUM requested. Real Hojas history main computes levels3 where API leaves4: HIGH DOC-ABB-MAIN-LEAVES-05 confirmed by C17 probe. Compatible main-local canonical-helper repair proposed in abb-download-reproduction-plan.md; no C/H/API change applied. Evidence visible-abb-clear-and-leaves-main-low. Counts13/22,ABB9/12,symbols53/208 unchanged.


## Hojas main compatible repair verified in LOW

17distinct targetedtests acrossruns,9actual main/C/H programs strictC17 and Doxygen0; computedleaf outputs, onecanonicalhelper, repeatedqueries/reload/callcounts/failureguard verified. Evidence visible-abb-leaves-main-reproduction-fixed. Earlier main3levels-vs4leaves finding superseded. Main-local approved packaging resolves reproduction without changing publicC/H. Global 13/22,ABB9/12,symbols53/208 unchanged. Next boundedMEDIUM Limpiar, baseline3cases100events.


## ABB Limpiar verified checkpoint

10/12 ABB visible instruction families verified for recorded cases. Limpiar: 5 cases, 201 native events, 422 UI forward/backward rows, 21 final targeted tests passed (109.82s), no replay POST. Evidence: evidence/visible-abb-clear-instruction-review/README.md. C/H unchanged; actual caller NULL assignment distinguished from free. Eliminar and decision-held Validar remain; global 13/22 and symbol ledger 53/208 unchanged. Earlier runs superseded; no exhaustive-path claim.


## Eliminar ABB LOW baseline checkpoint

13 cases / 221 native events: final trees agree. 25 actual generated main programs compile/run before and after reload, no extra POST/browser errors. One focused negative regression reproduces premature successor deletion at child entry. Instruction correction pending bounded MEDIUM: visible Eliminar plus required minimum helper, return/link publication, allocation identity and free aliases. Evidence: evidence/visible-abb-delete-baseline-low/README.md. No app source change; Validar held; ABB10/12/global13/22/docs53/208 unchanged.


## Eliminar ABB verified checkpoint

11/12 ABB visible instruction families verified for recorded cases. Eliminar: 13 native cases /221 events, 436 UI rows in ten successful operations; three rejected operations preserved. 20 current main/context programs compile/run; 44 final targeted tests passed in 258.90s. Future-state regression fixed, C/H unchanged. Evidence: evidence/visible-abb-delete-instruction-review/README.md. Validar held; global13/22/docs53/208 unchanged.


## AVL LOW verified checkpoint

77 endpoint cases/9operations; ten backend differences, nine independent invariant violations, two unbalanced native shapes. AVL-C-FE-01 semantic decision pending; no algorithm change. Six C/H contracts reviewed, focused native test1pass, two isolated Doxygen runs0warnings; tokens preserved. Documentation59/208 reviewed149pending. Five actual query mains inspected: reproduction/warnings/reload gaps remain. See evidence/visible-avl-native-documentation-baseline-low/README.md and pending-by-tad.json. ABB11/12 Validarheld; global13/22 unchanged.


## AVL main/history verified compatible checkpoint

29 targeted tests pass129.29s. Three real histories, nine actual mains strictC17/no warnings plus generator preflight;77 successful query entries, each retained across GET without operation redispatch/extraPOST. Canonical helpers included once, actual computed results/ascending inorden, decimal normalization and failures omitted. Evidence: evidence/visible-avl-main-history-reproduction-fixed/README.md. C/H/FE algorithms unchanged. avl-fe-decision-proposal.md pending; ABB Validarheld. Global 13/22/docs59/208 unchanged; no new global completion checkbox.


## Altura AVL verified instruction checkpoint

1/9 AVL visible instruction families verified for recorded cases: five valid native fixtures,196 events (191 callee+5 caller),206 steps,412 bidirectional UI rows,5 actual displayed callers strictC17. Native6 tests pass3.03s; Chromium E2E1 pass84.71s. C/H unchanged, no replayPOST or JSerrors. Evidence: evidence/visible-avl-height-instruction-review/README.md. FEAVL and ValidarABB held; global13/22/docs59/208 unchanged. Remaining AVL instruction families: Buscar, Minimo, Maximo, Inorden, Limpiar, Insertar, Eliminar, Validar.


## Buscar AVL verified instruction checkpoint

AVL2/9 recorded families (Altura,Buscar). Final16 tests pass80.21s:9 nativeBuscar,1 Chromium8cases,6 Altura regressions.101 nativeevents/117steps/234 replayrows/8 displayedcallers strictC17; completeheap/parents/FE,scopes,borrowedreturns and boolean conversion; no replayPOST/JSerrors,C/H unchanged. Evidencia: evidence/visible-avl-search-instruction-review/README.md. Remaining7families and FEdecision held; global13/22/docs59/208 unchanged.


## Inorden AVL and query-result boundary verified

AVL3/9 recorded instruction families (Altura,Buscar,Inorden). Inorden:5 valid nativefixtures,185events (180helper+5caller),180steps/360replayrows,5 exact-helper programs strictC17;22targetedtests pass85.76s. Latest28tests pass for7 message-boundary E2Es plus21 native queryregressions; result appears only atcompletion and hides onrewind, using existingbuttons,no newPOST. Evidencia: evidence/visible-avl-inorden-instruction-review/README.md. C/H unchanged; main-localhelper not counted aspublicsymbol. Remaining6families,FEAVL and ValidarABB decisions held; global13/22/docs59/208 unchanged; finalaggregate gatepending.


## Minimo/Maximo AVL verified instruction checkpoint

AVL5/9 recordedfamilies. Extrema10cases/100events (49Minimo,51Maximo)/200replayrows;12tests pass96.41s.20 strictC17 programs (10 equivalentcallers+10actualmains),actualmainsDoxygen0; no replayPOST/JSerrors. EmptyAPI400/resultabsent distinguished from nonNULL minimumC precondition and rawmaximumNULL; alias/locals/outputint faithfully shown. Evidencia: evidence/visible-avl-extreme-instruction-review/README.md. C/H unchanged; global13/22/docs59/208 unchanged. RemainingLimpiar,Insertar,Eliminar,Validar; FEAVL/ValidarABBheld,finalappgatepending.


## Limpiar AVL verified instruction checkpoint

AVL6/9 recordedfamilies. Limpiar5valid nativefixtures/190events/15frees/200steps/400replayrows;16tests pass128.74s.10distinct actual/equivalent strictC17 programs;5actualmainsDoxygen0,actualcaller assertsNULL andallocations==frees. No replayPOST/JSerrors; historicalaliases,voidscopes and separateNULLassignment; no C/H/FEchange. After Desktoprecovery8relevantfile byte comparisons match testedartifacts; no duplicatefullrun. Evidencia: evidence/visible-avl-clear-instruction-review/README.md. Insertar/Eliminar/FE and changesValidarheld; global13/22/docs59/208 unchanged,finalgateopen.


## Heap copy/history/native documentation checkpoint

22targeted tests pass (8/122.72s +14/20.93s), full-copy0/1/255/256/257/513, actual repeated-success history/reload identical main/zeroPOST, raw null/empty/output/capacity guards, copy-allocation failure, strictC17 and actual main+C/H Doxygen0. C algorithm tokens unchanged.15 productprograms +2 probes; instruction query scalar/buffer/callee oracle stillpending, not fullfamilyclosure. Evidencia: evidence/visible-heap-copy-history-contract-fixed/README.md. Documentation61/208 reviewed,147pending; global13/22 unchanged. FEAVL/ValidarABBheld; finalgateopen.


## Heap queries native checkpoint; UI pending

17native/regression tests pass11.75s,281real-C observations/10cases, correct capacity20/40, separate output/buffer/scopes/loops/returns/free and readonly source. C/H unchanged. Browser final verification stillrunning session9515 (heap-query-browser-boundary.log); collect without duplicate, no family/global checkbox closure. Evidencia: evidence/visible-heap-query-instruction-review/README.md. Global 13/22/docs61/208 unchanged; FEAVL/ValidarABBheld. MEDIUM semantic reasoning boundary complete; routine browser collection continuesLOW.


## Verified LOW checkpoint (supersedes UI-pending checkpoint)

Browser run completed:2 tests passed178.54s,10 query cases,281 displayed instruction steps/562 forward-back observations,10 equivalent callers and10 actual history programs compiled strict C17; actual history main+C/H Doxygen0. Both array/tree plus independent destination/scalar checked; replay produced no POST. Screenshots and program sources retained in evidence/visible-heap-query-instruction-review. Native block17 passed11.75s; following guide/nullable metadata correction16 focused native/domain tests passed8.82s. Latest C/H edits are documentation only; executable-token guard checked when applied. Guide distinguishes readonly queries, initialized destination cells, historical freed records and capacity20/40. Current preview smoke verified request16=>20,21st insertion=>40,18 extractions retain40/count3. Heap recorded instruction coverage2/5 (raiz,a_lista); insertar,extraer_raiz,limpiar still require instruction review. Global 13/22 and documentation61/208 remain; getter NULL fixes are verified by focused regression but no new symbol signoff claimed. Whole-app final gate remains open; FEAVL/ValidarABB held.


## Heap Limpiar LOW baseline; fidelity defect held for bounded semantic fix

4 contract tests pass5.41s;4 downloaded/generated strictC17 programs/5 clear calls/Doxygen0;75 native observations,4cases/5executions. API final empty/capacity20 correct; trace invents progressive deletion, retains capacity40 and omits free/NULL even for allocated empty heap. Evidencia: evidence/visible-heap-clear-native-baseline-low/README.md. Instruction/UI/replay NOT signed off. Heap2/5/global13/22/docs61/208 unchanged. Next bounded MEDIUM: clear destructor+reinitialize+private reserve lifetime/scopes, preserving existing C algorithm. Insertar/Extraer require sift/comparison/swap and growth or root-output review after this clear correction; no implementation in this LOW baseline. FEAVL/ValidarABBheld.


## Heap Limpiar verified instruction checkpoint; MEDIUM boundary complete

393 native events/8 cases/10 executions;786 actual array+SVG forward/back rows,24 linked C17 programs,16 actual main+C/H Doxygen0,zero replay/reloadPOST/JSerrors. Final revision25passed+1guide harness failure recovered by exact targeted1pass (26distinct verified outcomes across runs, not a singlegreen aggregate). C/H algorithm unchanged; guide/destructor docs and transient lifetime invariant corrected. Evidencia: evidence/visible-heap-clear-instruction-review/README.md. Heap3/5 recorded operations; Insertar/Extraer remain. Documentation62/208 reviewed,146pending (destructor only newly signed, initializer/private helper not broadly signed). Global 13/22 unchanged; whole-app finalgate/FEAVL/ValidarABBheld. End boundedMEDIUM now; next routine workLOW.


## USER-ORDERED PAUSE — awaiting resume

No active owned tests/compilers; all current runs completed, none interrupted. Preview only6568/13536 stays5051. Saved:evidence/heap-mutation-low-paused-checkpoint/README.md and checkpoint.json. Clear joint13pass11.71s; mutation10pass9.55s plus recovered generated-main1pass15.24s;17actual C17 mains/Doxygen0;18nativecases747events/17API final comparisons. SimpleNULL/output/count-order and INT_MINprintf fixes saved, mutation instruction defects remain (helpers before publiccaller, prematurequantity/stalecapacity/swaps/scopes). Global 13/22,Heap3/5,docs62/208. New user approval for AVLrotations/FE and ABBINT_MIN/MAX validation preserved; APPROVED but not implemented. Resume only on user instruction; no new tests now.


## Heap Insertar consolidated LOW checkpoint

Resumed authorized work; preview5051 remains. Final18passed:9native+9Chromium;432events/864both-view forward-back rows;27strictC17programs,18actualmain+C/H Doxygen0;zero replay/reloadPOST/JSerrors. Actualproject D:\MisProyectos\Web_VisualEstruct. Evidencia: evidence/visible-heap-insert-instruction-review/README.md. Heap4/5 recorded operations; Extraer remains. Documentation63/208 reviewed,145pending; global13/22 unchanged, whole-app finalgate open. AVLFE/rotations and ABBextrema APPROVED, not implemented here. Historical pause/held notes superseded by current authorization, retained as history.


## Heap Extraer verified bounded semantic checkpoint

Final28passed; extraction530nativeevents/9cases/1060both-viewforwardbackrows,27strictC17programs(17UImains+1empty-generator+9callers),18generator/C/H Doxygen0;zero replay/reloadPOST/JSerrors. Evidencia: evidence/visible-heap-extract-instruction-review/README.md. Heap5/5 recordedoperations; docs64/208reviewed144pending;global13/22unchanged. Wholeappfinalgate open. ReturnLOWnow; AVLFE/rotations and ABBextrema approved,nextindependentblocks.


## Validar ABB approved semantic correction verified

Final41passed;474nativeevents/16trees/948both-viewreplayrows;16actualmains computed48validations,C17strict/Doxygen0,zero replay/reloadPOST/JSerrors;leafgenerator regression included. Evidencia: evidence/visible-abb-validate-instruction-review/README.md. PublicABB C/H bytes unchanged; helper signoff separate. ABB12/12recordedcases; global13/22/docs64/208 unchanged. AVLFE/rotations stillapproved/unimplemented. Wholeappfinalgateopen. ReturnLOWimmediately atboundedsemanticboundary.


## Approved AVL native FE repair checkpoint

188 passed;89 prefix cases/77 exact backend comparisons/20 direct rotations/1 guards-allocation contract plus existing six-query test. Evidence: evidence/visible-avl-fe-native-repair/README.md. Four rotations fixed in actual downloaded C/H; ABI preserved; no backend algorithm change. Native repair complete; AVL6/9 instruction coverage/global13/22/docs64/208 unchanged. Routine Doxygen81970 and actual-main58254 pending collection; returnLOW. Historical approval hold is superseded.


## LOW consolidation of approved native AVL repair

Actual-main Chromium4passed84.16s; actual downloaded C/H Doxygen0warnings, content review four rotation symbols/guide. Documentation ledger68/208 (140pending), AVL10/13 public-file symbol contracts reviewed; three caller/mutation symbols remain pending instructional/documentary signoff. Native188tests previously recorded, not added to browser counts as one suite. Initial documentation wrapper stalled in workspace-relative session-cache initialization before Doxygen; stopped only identified wrapper Python processes, recovered using byte-verified preview HTTP downloads. Preview 5051 remained intact. Global 13/22 and AVL6/9 instruction coverage unchanged.


## Validar AVL LOW baseline prepared

351nativehelperobservations/9cases,7public-seedtraces examined; missingrecursiveframes/localfe, nestedheightobservationpending. Isolatedunorderedbalancedfixture demonstratesheight-onlyshownC vsorder-and-heightbackend distinction; no behaviorchanged. Evidencia: evidence/visible-avl-validate-baseline-low/README.md. NextboundedMEDIUMscope:avl-validate-instruction-review-plan.md; thenInsertar/Eliminarseparately. Global 13/22,AVL6/9,docs68/208 unchanged.


## Validar AVL bounded instruction closure

30distincttests verified across24+18 runs with12overlappingnativechecks deduplicated;1321nativeevents/14cases/2642both-viewreplaystates/24actualCcaller-historyprogramsC17strictDoxygen0. Evidencia: evidence/visible-avl-validate-instruction-review/README.md. Purehelperheightbalance andbackendorder+heightbalance remainseparate; publicC/Hbytesunchanged. AVL7/9recordedoperations;Insertar/Eliminarpending. Global 13/22/docs68/208unchanged. Preview 5051launcher15948D:HTTP 200. ReturnLOWimmediately.


## Insertar AVL LOW baseline and documentation contract

714nativeevents15cases (supersedes694beforeternaryconditionextension),14originalC/instrumentedendpoint+independentinvariantcrosschecks,2actualmainregressions39.75s,C/H Doxygen0. Evidencia: evidence/visible-avl-insert-baseline-low/README.md. Docs69/208;avl_insertar contract signed independentlyofinstructionUI. Currenttraceslacknativeframes/rotationdefinitions/repeatedFEconditions; MEDIUMscopedinavl-insert-instruction-review-plan.md. AVL7/9/global13/22unchanged.


## Insertar AVL bounded instruction closure

26 passed in 263.07s; 714 native events/15 cases; 1354 Chromium forward/back states/11 successful visible cases; 33 caller/history C17 programs, Doxygen0. Evidence: evidence/visible-avl-insert-instruction-review/README.md. Public C/H bytes unchanged from LOW documentation signoff. Stable generated-main invocation output repaired without attributing status to void. AVL8/9 recorded operations; Eliminar pending. Global 13/22 and documentation69/208 unchanged; final whole-app gate remains open. Preview 5051 HTTP 200 launcher3676 D:. End MEDIUM now, return LOW.


## Eliminar AVL LOW preparation

19native cases/1890events and independent original-C/backend endpoint/invariants; four visible main-history cases/8 exact mains+8 observation variants, C17 strict and Doxygen0; stable invocation output repaired. Content-reviewed Eliminar/helper/manual contracts advance docs71/208 (137pending), AVL13/13 public-file entities. Evidencia: evidence/visible-avl-delete-baseline-low/README.md. Current traces lack native frames/called definitions; bounded MEDIUM planned in avl-delete-instruction-review-plan.md. AVL8/9/global13/22 unchanged; finalgate open.


## Eliminar AVL MEDIUM semantic checkpoint; browser final running

22 native/API tests passed:19cases/1913events (1890 baseline superseded by15 ternary selections and8 explicit lexical-scope exits), strict continuity and C/H bytes unchanged. Source/lifetime/return/recursive-height/rotation integration complete natively; final40-test aggregate in session80435 must be collected in LOW. Evidencia: evidence/visible-avl-delete-instruction-review/README.md and checkpoint.json. No AVL9/9 or global completion claim before final UI result; global13/22/docs71/208 remain. Preview 5051 launcher19416 D:.


## Eliminar AVL verified LOW consolidation

40 distinct checks verified (37 aggregate passes plus 6 corrected-contract passes, 3 overlap); 19 native cases/1913 events; 3744 successful browser states, 6 application rejection explanation states; 48 strict C17 programs/Doxygen0. Evidence: evidence/visible-avl-delete-instruction-review/README.md and verification.json. AVL9/9 recorded visible operations; no all-path claim. Global 13/22 and docs71/208 unchanged; remaining families/final gate open.


## Rojo-negro LOW baseline

Seven visible operations inventoried; 84 native scenarios/478 prefixes, strict downloaded C17, independent RB/order/parent invariants and exact successful backend topology/color agreement. 16 expected absent-delete application rejections separated from raw C no-op. Evidence: evidence/visible-red-black-baseline-low/README.md. Displayed helpers and generated-query main contracts remain unverified/contradictory; no instruction or documentation closure claimed. Global 13/22/docs71/208 unchanged.


## Rojo-negro query/main LOW verification

7focused tests (6aggregate+1additional no-reexecution); four browser histories/12actual C17 mains, reload stable, Doxygen0. Inorden/Altura/Validar run canonical documented helpers, query history preserved without replay. Validar matches actual backend root-black/order/red-red checks; black-height/parent validation NOT provided. Public Buscar/VerArbol/Color comments-only content signoff advances74/208(134pending); four app helpers outside denominator. Evidencia: evidence/visible-red-black-query-main-low/README.md. Global 13/22, instruction coverage and finalgate remain open.


## Rojo-negro bounded query instruction closure

37distinct checks:19normal native comparisons(460events),4test-only negative validator cases(90events),14browser scenarios(742forward/back states),23original callers/exactdownloaded C parity. Source/scopes/typedaliases/returns/printf/actualSVGedges/colors/pendingmessages and no replayPOST verified. Inorden/Altura/Validar/Buscar close4/7 recorded visibleoperations; Insertar/Eliminar/Limpiar remain. Validar contract remains root-black/order/red-red only. Evidencia: evidence/visible-red-black-query-instruction-review/README.md. Global 13/22/docs74/208 unchanged; finalgate open. EndboundedMEDIUM, returnLOW immediately.


## Limpiar Rojo-Negro LOW baseline and history fix

13distinct tests (5native lifecycle+4clear histories+4adjacent query histories),215nativeevents/15frees including5safe NULLrepetitions;12actual clear mains+12observervariants,12adjacent query mains C17/Doxygen0. Real repeated-history deduplication fixed in live/restored paths. Public rbt_liberar content signoff75/208(133pending), token guard/no C algorithm change. Evidencia: evidence/visible-red-black-clear-baseline-low/README.md. Instruction UI remains pending4/7, global13/22; next bounded review:red-black-clear-instruction-review-plan.md.


## Limpiar Rojo-Negro verified bounded instruction checkpoint

12 distinct checks:11 native +1 browser covering10 executions;215 native events/15 frees,235 steps/470 forward-back states,20 exact actual/equivalent C17 programs/Doxygen0 and20 separately counted observer variants. C/H hashes unchanged; scoped parameters, historical unusable references, actual NULL leaves and separate caller NULL assignment verified. Evidencia: evidence/visible-red-black-clear-instruction-review/README.md. RBT5/7 recorded visibleoperations; Insertar/Eliminar remain. Global 13/22/docs75/208 unchanged, final whole-app gate open. MEDIUM ends at this boundary; resumeLOW.


## Insertar Rojo-Negro LOW baseline/documentation checkpoint

29 distinct checks pass (25native/documentary4.22s +4actual-main111.99s),24cases/1460native observations,8exact downloaded-history programs and8ownership variants, C/H andmainDoxygen0. Ten symbol comments/manual content signoff advances85/208 (123pending); executable C/H tokens unchanged. Source includes all10helpers but full typed scopes/heap snapshots and instruction UI remain pending. C-MAIN-RBT-OWNERSHIP-01 open: actual mains keep finalfree commented,3/3/3/8live reserves at exit. Evidencia: evidence/visible-red-black-insert-baseline-low/README.md; bounded next:red-black-insert-instruction-review-plan.md. RBT5/7/global13/22/finalgate unchanged; Validar limit remains separate.


### Insertar LOW final observer supersession

Fresh safe baseline1460events/24cases;25native/documentary tests pass3.77s. Inactive seed borrowed returns no longer inspect a registry from previously freed cases; cached artifacts now guard C/H and observer SHA. Older successful native sample is superseded, not added to counts. Browser4tests111.99s independently unchanged. Evidence:visible-red-black-insert-baseline-low/rbt-insert-baseline-final-low. Docs85/208/global13/22/RBT5/7 remain; boundedMEDIUMplan ready, ownership/validator/finalgate open. Preview13812 HTTP 200.


## Insertar Rojo-Negro verified LOW closure

Recorded-case Insertar closure advances RBT6/7; Eliminar remains. Current affected74checks pass:57native/contracts68.25s,1actual C/H/helper/manual/Doxygen3.96s,16browser cases (11initial passes plus5focused corrections161.08s; retained first-run5expected fixture/count failures).36actual C17 mains/Doxygen0 plus24separate ownership variants:77allocations=77frees,0live.18exact operation callers verified independently. Full prior24case Chromium pass3634forward/back states/1817steps456.32s, with18real successes/6explicit native fixtures; current affected replay cases8/20 pass294states. C/H bytes unchanged, signedint insertion rejection and final caller main cleanup verified. C-RBT-INSERT-INT-RANGE-01 and C-MAIN-RBT-OWNERSHIP-01 closed for this recorded scope. Evidencia: evidence/visible-red-black-insert-final-low/README.md and final-summary.json. Preview D:5051 launcher15372 HTTP 200, cache retained. Global 13/22/docs85/208 remain; no all-path claim, validator/sanitizer/WebKit/whole-app final limits persist. No test remains active, no push/merge/deploy.


## Eliminar Rojo-Negro LOW baseline/documentation checkpoint

94distinct checks pass:90native/documentary3.47s +4actual-history112.05s;83cases/4898actualC observations,71original-z frees,0deletion allocations/printf. Original bodies and strong independent endpoint invariants agree with backend; final invariants do not prove instruction UI.8actual C17 mains/Doxygen0 +8ownership variants:30allocations=30frees,0live; repeat rejection/reload preserve history/output without extraPOST. Failure-only app trace corrected: no rbt_eliminar invocation fabricated. Five C/H contracts reviewed, ledger90/208(118pending), all19RBT declaration SHA/lines refreshed and stale markdown tables reconciled with JSON. C/H algorithm tokens unchanged; old cache hashes must regenerate, not bypass guards.

OPEN C-RBT-DELETE-TRACE-01: sourcewindow onlyrbt_eliminar, lacks6actual helper definitions; root withtwochildren36nativeevents vs16genericsteps, onlytopframe/noheap model. Next boundedMEDIUM:red-black-delete-instruction-review-plan.md for typedchar/pointer scopes, transplant/successor/originalfree, fix-up and bothviews/replay. C-RBT-VALIDAR-LIMIT-01 remains OPEN in red-black-validation-limit-decision.md evenafter7/7; product Validar doesnot certify blackheight/parents/cycles. Evidencia: evidence/visible-red-black-delete-baseline-low/README.md; reviewed-revision.json baseHEADba53ba7c0bcebaf7a4938328ebf4c863f19eadab plusuncommitted SHA-guarded changes. RBT6/7/global13/22/finalgate remain. Preview D:5051 launcher15156HTTP 200/cachepreserved. No active app tests; no AGENTSroot/newcontinuity edits or push/merge/deploy.


## Eliminar Rojo-Negro MEDIUM semantic checkpoint; LOW consolidation pending

119distinct testIDs verified across overlapping runs:83native cases+2app-rejection+17exact C17caller/Doxygen0+17Chromium scenarios.6585typed/lifetime/operand/ternary observations supersede4898baseline;71original-z frees,0allocation/printf.2514distinctboth-viewforward/backstates,0replayPOST/JSerrors. Finalaffected87passed127.14s (85native+UI70/73); prior32passed379.56s and focused5passed114.12s overlap, not added. All64fullcondition/25operand/15ternary OBSERVED outcomes represented in17selectedcases. C/H bytesunchanged. Sourcewindow/helpers/scopes/char/native successor/free/fixup andscope-exitvariable rows verified. Evidencia: evidence/visible-red-black-delete-instruction-review/{README.md,checkpoint.json}. RBT7/7 recorded semantic methods; no all-path/globalclosure. C-RBT-VALIDAR-LIMIT-01 stays OPEN. Global 13/22/docs90/208(118pending) unchanged. LOW consolidates expectedclosuremarker/affectedadjacent checks before moving worklist; wholeappfinalgate remains. EndMEDIUM immediately, returnLOW; no push/merge/deploy.


## Eliminar Rojo-Negro verified LOW closure

Recorded closure after semantic evidence119distinct testIDs and necessary adjacent3passed107.46s (not summed as new global counts). RBT7/7 recorded methods;83nativecases/6585events,17UIscenarios/2514states,17exactcallers remain the bounded semantic scope. CurrentLOW checks shared Insertar rotation/replay270states and2actual Eliminar/rejection/reload histories:4strictC17/Doxygen0 programs+4separateownershipvariants,20alloc=20free,0live. Evidencia: evidence/visible-red-black-delete-low-closure/{README.md,summary.json}. C-RBT-DELETE-TRACE-01 closed for thesecases; C/H andapplicationbytes unchanged inLOW. Global 13/22/docs90/208(118pending) unchanged; wholeappfinalgate open. C-RBT-VALIDAR-LIMIT-01 OPEN: concrete V1/V2/V3proposal in red-black-validation-extension-proposal.md, no implementation;2currentbackend/Ccounterexamples observed independently. Hash contract H1/H2/H3 still awaits user decision; hash-baseline-decision-gate-low.md records read-only sources, no new normative baseline chosen. Preserve5051; no push/merge/deploy.


## BFS MEDIUM semantic checkpoint; LOW consolidation pending

BFSonly:13focusedtests pass25.43s;10helpertests pass19.84s;2400realC observations/10cases/11runs INCLUDE720outerevents (not added). Actualhelpers, mark-on-enqueue, symbolicallocation/free/partialpublication/scopes and successful-query history/caller corrected; C/H bytes unchanged. Current8case Chromium run session99991 remains active; cases1,3 already152/730rows and strictC17 actualmain verified. Collect durable bfs-browser-final1.log before rerun; no BFS/allgraph/globalclosure yet. Evidencia: evidence/visible-graph-bfs-instruction-review/{README.md,checkpoint.json}. EndboundedMEDIUM now; LOW collects browser run, final affected regressions/docsignoff and currentpreview verification. Global 13/22/docs90/208 unchanged; other5graphalgorithms,Hashdecision,RNValidar andfinalgate remain open.


## BFS verified LOW closure for recorded cases

BFS1/6graph algorithms recorded:10nativecases/11runs/2400events INCLUDE720outer;8Chromiumcases/4524states,0replayPOST/JSerrors.99991collected8pass201.19s. Current73uniquechecks via72pass plus21targeted41.51s(overlap20,one repaired test variable); final2browser1,7 pass42.32s/782states overlap8.8actualC17/Doxygen0 mains+8ownershipvariants181alloc=181free,0live. HTTP4C/H/Doxygen0,7contracts signed, executabletokens unchanged. Docs97/208,111pending; global13/22 unchanged. D:5051 launcher14428/HTTP 200 newmodel/canonicalframes/rejection/-1/history verified inisolatedsession. Evidencia: evidence/visible-graph-bfs-low-closure/{README.md,summary.json}. Finite normalalloc,max4vertexnative scope only; largerperformance/nativetypedlocals/sanitizers/WebKit/globalfinal remain. DFS,Dijkstra,Bellman-Ford,Prim,Kruskal,Hashdecision,RNValidar open. DFS will be registerednext without algorithmexecution.


## DFS LOW contract checkpoint — instruction review OPEN

Evidencia: evidence/visible-graph-dfs-contract-low. 10nativecases/11runs finalorder match; corrected9graph/outputmark discrepancies and9lostsuccess histories, after0. 10focusedtests pass53.44s includes3actualChromium callers plus5sharedpedagogychecks. Three actualmains strictC17 compute2DFSresults after2reloads/failureomitted;4doc/ownershiptests pass5.65s,4HTTPfiles/Doxygen0,46alloc=46free/0live. C/H algorithms unchanged. Three sourcecontracts reviewed; docs100/208,108pending; global13/22 unchanged. Preview 5051 ownlauncher17900HTTP 200 currentmarks/history verified. DFS perinstruction/helperframes/aliases/heap/bothrepresentations/replay OPEN; next boundedcase in graph-dfs-instruction-review-plan.md. No closedfamily or allpaths claim; Hash/RNValidar pending.


## DFS bounded instruction checkpoint — context remains OPEN

Evidencia: evidence/visible-graph-dfs-instruction-review.10nativefixtures/11runs/1978events/8functions/max5frames; actualtypedpointercache/initializedheap/conditions/returns/aliases/head/frames conformance.8uniqueChromiumcases/3698states,0replayPOST/JSerrors,8actualC17mains; valuesTEXTstrongchecks cases1,7/632states.7pass184.06s plus final12pass53.63s(10native+2browser,case7overlap). Ownpreview5051launcher13908HTTP 200 DFSmodel/guard/canonicalframes verified. Global 13/22/docs100/208 unchanged.

NEW C-DFS-HISTORY-MARKS-01 OPEN: publictopologyrebuild skipsoldqueries and losespriorquerymarks; secondentry0 vsrawsamegraphC1 despiteequalorder. No fullcrosscallDFSclosure or closedBFSreopen. See graph-dfs-history-marks-context-decision.md; suggestseparatevalidatedeffectsnapshotrestoration withoutqueryredispatch, scopecoordinationneeded. ReturnLOW atsemanticcheckpoint; callers/docsfinal/sharedregression/contextdecision stillpending.


## DFS verified LOW closure for recorded cases

DFS2/6 graph algorithms recorded (BFS and DFS). Finite DFS scope:10 native cases/11runs/1978events/8actualfunctions/max5frames and8Chromium cases/3698forward/back states. All8 now assert previous/current variable values as text; earlier limited-case632state assertion statement is superseded. Head storage, symbolic heap/initialized fields, live aliases, recursive scopes/returns, highlights, conditions and console verified; no replay POST/page errors. Native current-repeat fixture uses actual captured service history.

Cross-call marks C-DFS-HISTORY-MARKS-01 corrected via validated chronological effect snapshots, no historical query dispatch. Additional native history matrix10sequences/31operations/62before-after mark observations matches repeatedDFS,BFS-to-DFS,mutation,clear,failure cases.15invalid effects, stale copies, foreign sessions and malformed histories tested. Existing vertex marks survive native mutations; new vertices start0. Legacy histories without valid captured effects cannot recover old marks and are deliberately not redispatched; no retrospective all-history claim.

Backend aggregate81passed113.92s. Full8instruction-browser cases passed before last fast-to-step correction. New context regression first exposed discarded fast-mode player trace; graph.js now retains the actual execution. Final focused affected suite13passed77.22s: one sharedBFS context, twoDFS replay cases1/7(632states overlap8),10documentation/ownership checks. Earlier focusedDFS context1passed19.70s:3actualcalls,0replay/reloadPOST,mutation input,actual downloaded4files/mainC17 and computed output. Nine unique actual DFS browser mains (8instruction+context), Doxygen0, strictC17 and9independent ownership variants144alloc=144free/0live; symlink current artifacts excluded from counts. Fresh4HTTP C/H Doxygen0, guides describe finite scope and historical-effect limits. C/H executable code unchanged. Docs100/208 reviewed/108pending, global13/22 unchanged.

D:preview5051 launcher332 verifiedHTTP 200/currentmodel/currentJS/signedmarkeffect/secondinput[1,1] in isolated session; original user cache retained. Evidencia: evidence/visible-graph-dfs-history-context-low. No active tests, push, merge or deployment. Normalalloc/max4nativevertices; malloc-failure paths, largegraphs/performance, sanitizers/WebKit, other4algorithms and whole-app final gate remain open. Dijkstra only scope preparation next; do not treat this closure as authorization for semantic execution.


## Dijkstra LOW baseline: execution authorized, instruction review OPEN

16independent native endpoint cases compile strictC17;13agree and3disagree:equal-priority order (C1-3-4/API1-2-4),INT_MAXtreatedas infinity inC but reachable inAPI, overflow sum2147483648discardedbyCbutacceptedAPI. Bothnegative-weightcases correctlyreject, includingdisconnectednegativearc; historicalGRAPH-004negativeguard claim is not a current proven defect. Newstrongregression18IDs:13pass/5fail8.50s (3parity+2successfulhistory). No xfail/suppression/assertionweakening.

3actualbrowser cases,6realqueries: repeatedidenticalcalls become1localmaincall and0after2reloads,0extraPOST/pageerrors. All3originalstudentmainsfailstrictC17unusedcamino;2nonemptyresultcallersleak2nodes each. Observationalvariants only:38alloc/34free/4live; originalcompilefail preserved, not counted as passing actualmains. They print precomputedUItext ratherthancomputedpath. Caller/history fixes pending.

1freshHTTP4C/H/doc/helpertestpasses1.62s,Doxygen0,actualprivatehelperbodies strictC17.5individualsourcecontracts reviewed; docs105/208,103pending;all71graphdeclarationmetadata refreshed. C/H executabletokensunchanged; integer infinity/tie/globalnegative/ownership notes andguide limits accurate. Genericinitialtrace presents double dist[1]=0beforeCarrayinit,auxiliarypriority_queue despiteactualminscan;Actualhelperframes/typedarrays/nativeinstructionconformance not verified. Evidencia: evidence/visible-graph-dijkstra-baseline-low. Global 13/22 andBFS/DFSclosures unchanged. Next boundedMEDIUMscope proposed in graph-dijkstra-instruction-review-plan.md; don't implement numeric/decimal policy redesign silently. No active tests/push/merge/deploy.


## Dijkstra: historial y caller verificados; semántica numérica abierta

Corrección LOW autorizada de C-DIJKSTRA-HISTORY-04 y C-DIJKSTRA-CALLER-05 para los casos registrados. Cada consulta exitosa se conserva, incluso repetida; los fallos no se agregan. La reconstrucción valida la consulta en su posición histórica sin ejecutarla. No se agregan efectos de marcas a Dijkstra. Una regresión compartida acotada confirma que las marcas DFS sobreviven las consultas de camino; no se repitieron oráculos BFS/DFS cerrados.

Backend:25 aprobadas/3 fallidas en 14.86 s. Las dos regresiones de historial antes fallidas ahora pasan; se mantienen sin xfail los tres fallos numéricos de empate/INT_MAX/suma. Nueve pruebas nuevas cubren repeticiones, fallos, recarga sin dispatch, mutación negativa posterior y marcas compartidas. Navegador:3 aprobadas en 39.12 s,6 consultas exitosas y3 rechazadas;2 llamadas por programa sobreviven recargas, ninguna petición adicional al reproducir/recargar, ningún error JS. Tres programas originales compilan C17 estricto, imprimen caminos/costos calculados por C y pasan Doxygen; tres variantes independientes de ownership verifican61 reservas = 61 liberaciones / 0 pendientes. NULL se explica como sin arcos/sin ruta/error, sin inventar un resultado calculado.

Comprobación final del manual/C/H:1 aprobada en 1.88 s, mismo ID documental incluido en backend, no un caso adicional. API observada con 11 entradas: rechaza 2.5 y"2.5"; acepta algunos pesos fuera del rango C;Infinity provoca HTTP 500. La afirmación anterior del manual sobre aceptación decimal fue corregida; la spec canónica conserva una contradicción pendiente. Dos sentencias reales del generador examinadas solamente en compilación/sintaxis:ninguna ejecución C insegura. 1e40 → int no representable es UB si se ejecuta; INT_MAX y la suma descartada por guarda del baseline son casos definidos. Ver graph-dijkstra-numeric-contract-decision.md:alternativas mínimas y recomendación C entero fiel, pendiente de decisión.

Hashes prueban que adapter, wrapper, dominio numérico y C/H permanecen idénticos al baseline; sólo historial/caller/manual/pruebas cambiaron. Evidencia: evidence/visible-graph-dijkstra-history-caller-low. Preview 5051 desdeD:,launcher 2812,HTTP 200,2 consultas conservadas tras 2 GET y JS nuevo verificados en sesión aislada; caché del usuario conservada. Global 13/22; documentación 105/208,103 pendientes. Dijkstra sigue abierto por fidelidad por instrucción y 3 regresiones numéricas. Sin pruebas activas/push/merge/despliegue.


## Bellman-Ford LOW: baseline y caller corregidos; instrucción abierta

Asignación coordination-graph-bellman-ford-baseline-low-20261002. Evidencia nueva en D: evidence/visible-graph-bellman-ford-baseline-low. Stage documental validado por cuatro hashes y tokens C/H idénticos antes de aplicar. 20 casos nativos:15 coincidentes/5 divergentes; dos arcos INT_MIN omiten ciclo negativo alcanzable por guarda sin UB ejecutado. Regresiones permanentes sin xfail:28 aprobadas/8 fallidas53.76s (5paridad+3estatusciclo, casos solapados). Historial/caller corregidos conservando contratos actuales:repeticiones,fallos,recarga sin redispatch y sin alterar marcas;3Chromium/6consultas exitosas/3rechazadas,0POSTreplay/recarga y0erroresJS;3mains originales C17 estricto/Doxygen0, resultados C reales y37alloc=37free/0vivos en variantes observadoras independientes. Doxygen4HTTP archivos sin advertencias; límite semántico y memoria normal documentados. No nueva firma del ledger:105/208;global13/22 sin cambios.

Opciones pendientes en graph-bellman-ford-numeric-cycle-options.md; no modificación numérica, decimal, algoritmo C ni success/error de ciclo. Fidelidad por instrucción no verificada; siguiente bloque requiere alcance separado de arreglos/pasadas/helpers/alias/memoria y ambas vistas. BFS/DFS cerrados conservados;Dijkstra abierto. Preview5051 HTTP200/currentJS verificado,PID2812/hijo16584;no push/merge/despliegue.


## Prim LOW baseline y caller corregidos; instrucción abierta

Asignación nueva coordination-graph-prim-baseline-low-20261002, registro Bellman conservado. Evidencia:evidence/visible-graph-prim-baseline-low.17nativos C17:11coincidentes por conjunto no dirigido/costo,6divergencias:empate,3negativos,INT_MAX,dirección C/API. API actual informa bosque/componentes desconectados;hallazgo histórico no reproducido. Baseline3callers reales fallanC17 y pierden historial,33alloc/30free/3vivos. Corrección autorizada de historial/main simétrico no dirigido/resultado C/ownership;3Chromium/6consultas+3rechazadas,2llamadas tras recarga,0POSTreplay/recarga/0erroresJS;3mains C17/Doxygen0 y70alloc=70free/0vivos en variantes. Historial26aprobadas11.80s:8Prim+9Bellman+9Dijkstra;no repetir conteos solapados. Native/docs12aprobadas6fallidas8.55s sin xfail;Doxygen4HTTP0advertencias. Prueba sintética separada para simetría/update/remove/cero/bucle;no3main extra. C/H sólo comentarios,guías actualizadas;global13/22 y ledger105/208 sin cambio. No fidelidad instruccional ni decisiones numéricas;ver graph-shared-numeric-options-low.md. Mantener5051,BFS/DFS cerrados;sin push/merge/despliegue.


## Kruskal LOW baseline/caller e inventario documental actualizado

Asignación coordination-graph-kruskal-baseline-low-20261002;before válida,evidencia evidence/visible-graph-kruskal-baseline-low.17nativos:15coincidentes(normalizado conjunto/costo)/2divergentes(empate,precondición dirigida),sin decisión semántica. Negativos/intmin/intmax/simétricos/bosque/límite total segurocoinciden;noUB. Baseline3mainsC17fallan,historial1→0,28alloc/24free/4vivos. Historial/caller corregidos:3Chromium/6consultas,2calls trasrecarga,0POSTreplay/recarga,0erroresJS;3mainsC17/Doxygen0 y38alloc=38free/0vivos.7testsaprobados37.46s,paridad/docs16aprobados2fallidos7.44s sinxfail. Regresión compartida26aprobadas12.00s:IDsexistentes,no incrementar conteo global.

Inventario documental nuevo:26HTTP C/H/479XML/382declaraciones/208entidades,hashescanónicos/Doxygen0;ledgeractual110revisados/98pendientes. Se agregan sólo5contratosindividuales Bellman/Prim/Kruskal/2UnionFind,helpersC17reales;previoledgerconservado,tododeclarationSHA/línea refrescado. No firma instruccional ni memoria fallida. Ayuda/guías corrigen burbujaKruskal,cota conservadoraO(E²+EV+V),bosque ylímites. Global13/22,BFS/DFScerrados,restoGrafoabierto,numéricoscompartidospendientes,preview5051conservado;sinpush/merge/despliegue.


## Sorting LOW inventario/baseline e historial corregido; instrucciones abiertas

Asignación coordination-sorting-baseline-low-20261002,beforeválida,evidence/visible-sorting-baseline-low.11métodosreales/7void+4int,110fixturesC17/220API(fast/paso),0divergenciasresultado/status. Vacío/single/repetidos/negativos/ordenado/inverso/extremosint/rangoguardado;Radixuint32INT_MINyCounting/Binlimitadosactuales,noUBhistóricoreproducido. RuntimebaselinepierderesultadoGETen73fixtures(dosmodos146observaciones,nocasosnuevos). Correcciónhistorialarray_effectvalidado,runexitosorepetidopreservadosinredispatch,GETrestauraordenado,APIstepentradaoriginal,failureomitido,UIhistoryservidor.

39IDs únicos finales:35pass35.69s+3browsercorregidos22.90s+1docsownership2.08s;primer3fallosbrowser delecturahistorialplegadoconservadosencorrectedlog,ningúnnativefailureomitido.3Chromium/6runs,2entradastrasrecarga,0reloadPOST/JSerrors;noactualmainUI,gapexplícito.110callsnativos equivalentesenobservador:95alloc=95free/0vivos,no110mainUIreal. Doxygen2HTTP0warnings,teoríacorrigeHeaprecursión/Quickstack/Radixestabilidadnegativos;Ctokensintactos. Ledger121/208revisados87pendientes,11contratospúblicos nuevos,SHA/líneasXMLsortingrefrescados,previaevidenciaconservada.

Planpropuesto sorting-intercambio-instruction-review-plan.md:6casosmáximo4elementos,helperssize_t/aliases/ramas/escrituras/replayreusable;requiereasignaciónpropia,ningúncierreporinstrucciónni mainUIinventado. Global13/22,Grafosnuméricospendientes,BFS/DFScerrados,noampliaciónmétodos,preview5051conservado;sinpush/merge/despliegue.


## Intercambio verified closure for recorded cases

Asignacion coordination-sorting-intercambio-medium-20261002; operacion sorting.intercambio-instructions; evidencia evidence/visible-sorting-intercambio-instructions. Implementacion dedicada de indices/condiciones/calls/scopes/alias/tres asignaciones parciales y codigo C, sin alterar otros10 metodos ni C. Seis entradas <=4 valores:176 observaciones C17 independientes,0divergencias; guardas n0/NULL separadas del rechazo API/UI. Seis Chromium:352 restauraciones de las mismas entradas,0POSTreplay/0JSerrors,modo rapido conserva traza; vistas tecnico/pila/alias visibles y ciclo caller suspendido. Ultima pasada19IDs unicos aprobados38.46s; pasadas/logs anteriores conservados,no sumar repetidos. DoxygenC/H y3prototiposmain0warnings;3callers offline reproducen historiaC17,no mainUIreal. Main ausente C-SORT-MAIN-01 sigue abierto; propuesta minima preparada en sorting-main-minimal-proposal.md. Ledger121/208,global13/22 sin cambio,Grafosnumericos pendientes,BFS/DFS conservados,preview5051 D:/PID2812->16584 HTTP200/currentJS/C/H hashidenticos. MEDIUM semantico terminado;handoffLOW,proximo bloque requiere nueva instruccion fina. Sinpush/merge/despliegue. Cierre solo estos casos:leer README limites;no ampliar ni reabrir desde checkpoint historico.


## Sorting main verified LOW closure for recorded callers

Asignacion coordination-sorting-main-low-20261002,operacion sorting.main-reproducible; evidencia evidence/visible-sorting-main-low. Integrado main real servidor en historialseccion5 ydescargamain.c por source existente,0botonesnuevos/Ctokenssinmodificacion.11historias/12programas UIreales C17/Doxygen0,43runs nativos,44alloc=44free/0vivos;4fallosprimerallocdeintmanejadoscodigo1sinresultadofuturo. Repetidos/recarga/aleatoriosmaterializados/recreacionextremos/size80Burbuja/rechazos/reset/exportJSON/aislamientos;0POSTreplay/recarga/0JSerrors.46IDs unicos aprobados116.59s:22main+24routes/history existentes,no sumarpasadas. Se corrigio resaltadorclassemainqueborrabaLFalrecargar;logsfallidos preservados. Legacyseedmaterializado/persistidouna vez,sin generar enGET posterior. C-SORT-MAIN-01cerradocondicionesregistradas,no firme instrucciones10metodos. Intercambiocierreseisconservado,solo expectationmain actualizada;sinrepetirbloque. PlanSeleccionpreparadodesdeC realguardaindice_menor!=i,sinimplementar. Ledger121/208/global13/22conservados,Grafosnumericospendientes. Preview5051seactualizoexclusivamentepropioPID2812->16584verificado(sinreloader,main404),nuevoPID6668->18136HTTP200/JSmainbytescanonicossinPOST. SiguienteaccionnuevainstruccionfinaLOW;sinpush/merge/despliegue.


## Seleccion verified closure for recorded cases

Asignacion coordination-sorting-seleccion-medium-20261002; operacion sorting.seleccion-instructions; evidencia evidence/visible-sorting-seleccion-instructions/README.md y summary.json. Seis entradas <=4,204observaciones C17/0diferencias,19observaciones de2guardas nativas separadas del rechazo API/UI vacio. Modulo dedicado observa minimo tras asignacion, guards/helper condicional, locals size_t sin inicializar,3writesparciales, caller externo suspendido/scopes/retorno. C/H e Intercambiomodule intactos,callerexistente reutilizado. SeisChromium408restauraciones mismasentradas/0POST/0JSerrors,modo ynext/prev;7mainUIrealdescargados C17/Doxygen0,6runsSelection,0alloc/free/vivos;historia/mainigualtrasrecarga.18IDsunicos pass72.32s;12mismosIDsfortalecidos source/guards pass2.52s,no sumar. Primerarnesfallido yprimerpreviewdefault5050preservados/corregidos. PreviewcanonicalD5051parent18520child2824HTTP200/bytesconfirmados. Global13/22,ledger121/208+87pendientes,nootros9instructionclosures,Grafosnumericospendientes. MEDIUMsemanticoterminado;handoffLOW/nuevainstruccionfinaantesdesiguienteaccion. Sinpush/merge/despliegue.


## Insercion LOW baseline collected; instruction fidelity pending

Asignacion coordination-sorting-insercion-baseline-low-20261002; operacion sorting.insercion-baseline-low. Evidencia evidence/visible-sorting-insercion-baseline-low/README.md y summary.json. ConsolidacionSeleccionporlectura/hashes8produccion iguales,sinrepetircierre18IDs. Insercion6<=4:162observacionesC17/48framesactuales,paridadfinal/metricas/mutaciones6/6,114observacionesausentes/30frameslocalsincompletos. Dosguardasnativas19observaciones/rechazoAPI/UIvacio separados,cortoj0sinUB. SeisChromium96restauracionescoarse/0POST/0JSerrors;4shiftsclavemissing/huecoj-1erroneo (8observacionesavanceretroceso,nocasosnuevos).7mainUIrealdescargadosC17/Doxygen0,6callsInsertion/0alloc/free/vivos,reloadbytes/historia correctos.21IDs15passed6failedcausales2.69s sinxfail,oraclependientenoocultado. PrimeraevaluacionscopelinesfullC corregidaalexcerpts,nohallazgolineafinal. No cambioC/H/produccion. MEDIUMdelimitadoen sorting-insercion-instruction-review-plan.md;necesitanuevainstruccionfinaantesdeimplementar114eventos/scopes/conditionUI,no cierrefidelidadInsertion. Global13/22/docs121/208+87pendientes,numericosaparte,preview5051PID18520/2824sinrestart. Sinpush/merge/despliegue.


## Insercion verified closure for recorded cases

Asignacion coordination-sorting-insercion-medium-20261002; operacion sorting.insercion-instructions; evidencia evidence/visible-sorting-insercion-instructions. Nuevo modulo opt-in conserva clave int/cuerpo scopes/j size_t,for/whileoperandscorto+compound,shiftarrayrealduplicado,--j/writekey yretorno;Indicej sin celda vacia ficticia. Seis<=4,162nativeevents=162frames/0diff;oracleC/JSONLidenticobaseline,twoNativeguards19obs/APIUIemptyseparate,sinUB.21baselineIDs incluidas6antesfallidas ahora pasan,su archivoenteroinalterado;14nuevos=>35IDsunique pass5.18s,prev21passsolapa/no sumar. SeisChromium324restaurations mismos162states/0POST/0JSerrors,faststepbuttons/varsstacksource/pointersnocallahelper.7sameUIcallersdownloadedC17/Doxygen0,6runs/0allocfreevivos,bytesidenticos7baseline,nosumar14programas. C/H ymodulosIntercambio/Seleccion intactos,callerexistente reusado,guideactualizada. Previewowned18520/2824canonicalidentityverified,restart hiddenexplicit5051actual22480/9980HTTP200/paginaJS/C/H/mainbytes. Global13/22/docs121/208+87pendientes,8otrosmetodos instrucciones/numericGraphaparte. MEDIUMsemanticoacabado,handoffLOW/nuevainstruccionfinaantesdesiguienteaccion. Sinpush/merge/despliegue. Cierre finitecasos/guardas,no allinput/taggedstability/failurealloc.


## Burbuja LOW baseline collected; instruction fidelity pending

Asignacion coordination-sorting-burbuja-baseline-low-20261002; operacion sorting.burbuja-baseline-low; evidencia evidence/visible-sorting-burbuja-baseline-low. Inventario1varianteBurbuja mejorada/ordenar_burbuja C/H/catalogoAPI/DOM;Kruskalbubblearccontractexcluido,0newmethods.7<=4:330nativeobservations/100runtimeframes,230omitidas/79frameslocalsgap/20helperb-nullstackgap. Result/comparison/swaps/earlystop7/7;pasadas0/1/3/1/2/2/2. CounterLOWoptin soloBurbujacorrige4casesmoves0->C18/3/6/3,cadastatement/final7/7moves,30moves/10swaps/24comparisons,observerC/JSONLidentico,C/Hintactos. Defaulhelperunchangedaisladocompare,sinrercerrados3moduleshashsame.3Chromium120coarserestoration/0POST/0JSerrors,4actualmainC17/Doxygen0/3calls/0allocfreevivos/reloadbytes.21IDs14pass7causalfailed2.79s sinxfail. MEDIUMdelimitado sorting-burbuja-instruction-review-plan.md,nonewcausalimplementationLOW. sorting-method-progress.md derivado3cierresfiniteIntercambio/Seleccion/Insercion y8pendinginclBurbuja;global13/22/docs121/208+87sinchange,numericalpendingaparte. Guideactualizada,counterpreviewown22480/9980verifiedrestartactual13840/13492D5051HTTP200/bytes. Guardasbefore/after,no push/merge/deploy. ScopeclosurebaselineLOWonly,nofidelitymethodsignoff.


## Burbuja verified closure for recorded cases

Asignacion coordination-sorting-burbuja-medium-20261002; operacion sorting.burbuja-instructions. Evidencia evidence/visible-sorting-burbuja-instructions/README.md y summary.json. Una variante existente, siete entradas <=4:330observaciones C17=330frames/0diferencias; controles/flag/scopes/helper alias reales/temporal/escrituras/break. Dos guardas nativas21observaciones aparte; rechazo vacio API/UI. Observer C y JSONL/C/H identicos; tres modulos cerrados intactos, LOW count_moves opt-in preservado. Archivo21regresiones original intacto: siete causales antes fallidas resueltas;16nuevas=>37IDsunicos passed7.42s, previo21se solapa/no sumar. Chromium7histories660restauraciones mismos330states/0POSTextra/0JSerror;faststep/prevnext/reload/five sections/typedlocals/callparams/source verificados.8actualmainUI descargados C17/Doxygen0,7calls/0allocfreevivos;4programas anteriores mismosbytes+4entradas nuevas,no12programas. Preview5051identity13840/13492loopbackcanonicalD; ultima instruccion consultaLAN sololectura prohibe reiniciar: preservado, backend sinrecarga anterior a implementacion; QAfuncional servidor efimero canonicalD. LAN Ethernet192.168.80.20, no firewall/red/server changes. USER_GUIDE y progreso derivado actualizados:4cierres finitecasos/7pending, global13/22/docs121/208+87 sin change, Graph numeric/cycles pending. No all-input/tagged-stability/allocation-fault closure. Semantico terminado;solicitarLOW/nuevainstruccionfina antes siguiente metodo. Sinpush/merge/deploy.


## Shell LOW baseline collected; instruction fidelity pending

Asignacion coordination-sorting-shell-baseline-low-20261002; operacion sorting.shell-baseline-low; evidencia evidence/visible-sorting-shell-baseline-low/README.md ysummary.json. LOWrefresca soloownedpreview13840/13492 verificados->17888/15000 canonicalD127.0.0.1:5051,hidden/no reloader,no red/firewall,GETbytesJS/C/H yprobeBurbujaactualinstructioneventsinrersuitecerrada. Shell siguienteexistenteinventario,0newmethods:6<=4cases322observationsC/93frames,229omitted/75frameslocalgap;finalresultsmetrics6/6 y cadaarregloproyectado/movesagree,2guards19obs/shortcircuitj<intervalosafe. 18IDs12pass6causalfailed2.64s,sinxfail;firstcp1252arneslogpreservedUTF8fixednoassertionweakening. Chromium3histories134restorations/67samecoarseframes/0POSTextra/0JSerrors,5shiftstates10forwardbackobservations temporalabsent/intervalostrategyconsulta fase.4actualUIprogramsC17Doxygen0/3Ccalls/0allocfreevivos,reloadmainpreserved;browserusesexisting5051nonewserver. Produccion/C/H/cuatroclosedmoduleshashesunchanged;guide/progressderivedupdatedLOWstatusonly,4recordedclosures7pendingglobal13/22docs121/208+87sinchange. PlanMEDIUMprepared sorting-shell-instruction-review-plan.md;no semanticimplementationuntilnewfineassignment. ClosedLOWbaselineonly,noinstructionShellclosure/allinput/taggedstability/allocatorfaultclaim. Graphnumericcyclependingaparte,sinpushmerge/deploy.


## Shell verified closure for recorded cases

Asignacion coordination-sorting-shell-medium-20261002;operacion sorting.shell-instructions;evidencia evidence/visible-sorting-shell-instructions/README.md ysummary.json. Scope6<=4,322actualCevents=322frames/0diff,typedlexicalintervalo/i/j/temporal/controlforgap/fori/whileoperandsandcompound/shortcircuit/realpartialshift/jsubtract/write/group/return;counterstatesagree. C/H/observerC/JSONLidenticosbaseline,4closedmoduleshashsame,original18regfileentero unchanged/seiscausales resueltas.32IDsunique pass6.45s;prev18pass3.29s y6UI strengthened DOMscopes pass0.22s overlaps/no sumar.6Chromiumhistories644restorations mismos322states/0replayPOST/0JSerrors,faststep/prevnext/reloadsource/currenttextvars/lexicalscopes/numericgap/groups/callers verificados.7actualUIprogramsC17Doxygen0,6nativecalls/0allocfreevivos;4samepreviousbytes+3newinputs,no11uniqueprograms. Guideupdatedfinite scope,5closures6pending derived,global13/22/docs121/208+87sinchange. Own17888/15000 identities+loopback verified restartonlythem23512/21400 canonicalD/currentShell5051actualChromium,no secondserver/network/firewall/cacheclear. MEDIUMsemanticfinished,returnLOW/newfineassignment beforeothermethod;noallinput/taggedidentity/allocatorfault/globalclaim. Graphnumericcyclepending;sinpushmergedeploy. Guardasbefore/after.


## Quick sort LOW baseline collected; instruction fidelity pending

Asignacion coordination-sorting-quicksort-baseline-low-20261002,operacion sorting.quicksort-baseline-low;evidence/visible-sorting-quicksort-baseline-low/README.md ysummary.json. Unavariant existenteQuick11catalogo,realhelpersarreglo_valido/quicksort_recursivo/intercambiar,noparticionfunctionindependiente.6<=4:386nativeevents/133coarseframes,253omitted/115localgap/maxdepth3;finalresults6/6,2nativeguards17obsAPI/UIemptyseparate. LOWsinglelineoptinQuick_swapcount_movesTrue corrige5metriccases0->C6/12/6/9/6moves;single0/0/0 vsC3compar1selfswap3moves abierto,nocausalengineLOWrewrite. C/H/observer/nativeJSONLidenticos;defaulthelperisolatedbeforeaftersame,no closedalgo reruns.25IDs18passed7causalfailed2.91s,sinxfail;firstharnessmissingconsole_eventskeylogpreservedmetadataNone,no assertionweakening.3Chromiumactualhistories114restorationssame57coarseframes/0POSTextra/0JSerrors/34forwardrecursive_depthgap/helperstackbNULLvsactualnonNULLpointer.4actualUIprogramsC17Doxygen0,3actualCcalls/0allocfreevivos,reloadmainbytespreserved. Fiveclosedmodules/adapter/pedagogy/JS/C_Hhashsame,no other closures. Guide/progressderivedupdatedLOWstatus5closures6pending/global13/22/docs121/208+87unchanged,Graphnumericcyclesaparte. BoundedMEDIUM sorting-quicksort-instruction-review-plan.md,nextfineassignmentrequiredbeforesemanticimplementation. Previewowned23512/21400verified->22520/3824hiddencanonicalD127.0.0.1:5051actualQuickmetricsUIverified,nored/firewall/secondserver/cacheclear. Guardsbefore/after;sinpushmergedeploy,no allinput/taggedstability/allocatorfaultclosure.


## Quick sort verified closure for recorded cases

Asignacion coordination-sorting-quicksort-medium-20261002;operacion sorting.quicksort-instructions;evidence/visible-sorting-quicksort-instructions/README.md ysummary.json. Opt-inrealrecursiontypedintframeparams/locals,parentssuspended,while scans/ifcross/left-rightcalls/returns/helperalias includingautoigual/temporals/assignments/beforeafter exactC.6<=4cases386nativeevents=386frames/0diff/maxdepth3;12recursivecalls/7selfswaps/56comparisons14swaps42moves. Single[7]32frames/native3-1-3/signedj=-1correctnoscanoutside.2guardraw17obs API/UIemptyrejectseparate,C/H/observer/JSONLidenticosbaseline,5closedmoduleshashsame,LOWdefaultcount_movesflagretained. Original25regfileentero unchanged/sieteantesfailresolved;14new=>39uniqueIDs passed7.16s,prior25pass3.91s overlapno64. SixactualChromiumhistories772restorationssame386states/0extraPOST/0JSerrors,recursivedepth/scopestext/params/realhelperaliasa==b/signedi-j/localpivote/source/condition/faststepbuttons/reload verified.7actualUIprogramsC17Doxygen0/6Ccalls/0allocfreevivos;4samepriorbytes+3newinputsno11programs. Guideupdated6finiteclosures5pendingderived/global13/22/docs121/208+87unchanged,Graphnumericcyclesaparte. Owned22520/3824identityloopbackverified,replacedonly14032/8096hidden/no reloaderD127.0.0.1:5051currentQuickactualsixUIhistories,nosecondserver/network/firewall/cacheclear. MEDIUMfinishedreturnLOW/newfineassignment before nextmethod,noallinput/taggedidentity/allocatorfault/huge-nunsafe/globalclosure. Guardbefore/after,sinpushmergedeploy.


## Merge sort LOW baseline collected; instruction fidelity pending

Asignación coordination-sorting-mergesort-baseline-low-20261002 / sorting.mergesort-baseline-low. Seis casos C:652eventos/63frames, resultados+métricas6/6;24IDs13pass11causalesfailed, auxiliar12cuadros ylocales45cuadros divergentes. TresUI52restauraciones0extraPOST/JSerrors;4programasC17/Doxygen0warnings,3calls3alloc3free0vivos y3faultprobes seguros. C/H/seis módulos cerrados intactos ypreview14032/8096loopback5051actual. Baselinecompleto, instrucciónMergependiente; planMEDIUMacotado sorting-mergesort-instruction-review-plan.md. Evidencia evidence/visible-sorting-mergesort-baseline-low/{README.md,summary.json,regression-first.log}. Global13/22/docs121/208 sincambio;cinco pendientes Merge sort,Heap sort,Counting sort,Binsort,Radix sort. No cierreglobal ni ejecuciónMEDIUM.


## Merge sort verified closure for recorded cases

Asignación coordination-sorting-mergesort-medium-20261002 / sorting.mergesort-instructions; plan sorting-mergesort-instruction-review-plan.md implementado para seis entradas <=4. C652observaciones=652frames, arrays/auxiliary/condiciones/scopes/calls/métricas fieles. Auxiliar indeterminado hasta cada escritura y retirado enfree; pila recursiva real, postincrementos por sentencia sinorden ficticio, copiadevueltaparcial. 38IDsúnicos pasan (24originales sinmodificar,oncecausas resueltas +14nuevos); validaciónfinal14nuevos solapada. UI1304restauraciones0extraPOST/JSerrors,fast->step/reload/main5secciones;7programasUI únicos=4LOWreutilizados+3nuevos,6calls6alloc/free0vivos y6faultprobes aparte. C/H/oracleC/JSONL/seis módulos anteriores intactos. Evidencia evidence/visible-sorting-mergesort-instructions/{README.md,summary.json,regression-combined-first.log,regression-new-final.log,browser-final/report.json}. Preview18500/19012D/run.py127.0.0.1:5051actualizado. Cierre solo6casos; noallinput ni API mallocfailure nihuge-n fuera1..80; guardas yfalloreservaC separados19/12eventos. Global13/22/docs121/208sincambio. VolverLOW bajo próximaasignación; pendientes Heap sort,Counting sort,Binsort,Radix sort.


## Heap sort LOW baseline collected; instruction fidelity pending

Asignación coordination-sorting-heapsort-baseline-low-20261002 / sorting.heapsort-baseline-low. Heap sort(ordenar_heapsort) distintoTADbinary_heap,helperheapify/intercambiar reales. Seis casos resultados/métricas6/6;LOWoptin3moves/helper corrige5métricas,alias/guardaFalse/nombrereal/rawprintf corregidos conhelperdefaultigual. C704observaciones/154frames,550omitidas/71mappedheaplocalsgap.26IDs14pass12causalesfailed2.91s;guardasCwrapper19yhelper13separados. UI3historias238restauraciones0POSTextra/JSerrors;4programasUI/3callsC17Doxygen0warnings,0alloc/free/live. C/H/observadorC/JSONL/sevenclosedmodules intactos. PlanMEDIUMdelimitado sorting-heapsort-instruction-review-plan.md, no ejecutado; Heap instrucciónpendiente. Own evidence evidence/visible-sorting-heapsort-baseline-low/{README.md,summary.json,regression-final.log}. Preview19824/8260D/run.py127.0.0.1:5051 actualizado. HashH1 nueva decisiónrecibida/fuentesreleídas, no trabajotécnicoHash/rolesadoptados/checkpointsreemplazados. Global13/22/docs121/208sincambio.


## Heap sort verified closure for recorded cases

Asignación coordination-sorting-heapsort-medium-20261002 / sorting.heapsort-instructions. Seis entradas <=4: C704 eventos=704frames; scopes/pila recursiva/cortocircuitos/alias temporal/for/retornos fuente C fieles. Árbol heap_n excluye sufijo confirmado, propiedad observada sin certificar fase parcial. 40 IDs únicos pasan (26originales íntegros,12 causas resueltas +14nuevos). UI1408 restauraciones0extraPOST/JSerrors,fast->step/nextprev/reload/main/JSON exacto,5etapas. 7programasUI únicos=4LOWreutilizados+3nuevos,6calls,C17/Doxygen0warnings,0alloc/free/live; guardas19wrapper+13helper aparte. C/H/oráculoC/JSONL y7módulos cerrados preservados. Evidencia evidence/visible-sorting-heapsort-instructions/{README.md,summary.json,regression-combined-final.log,browser-final-verified/report.json}. Preview17276/1800D/run.py127.0.0.1:5051actualizado. Cierre solo6casos,noallinput. Global13/22/docs121/208sincambio; ocho cierres finitos,pendientesCounting sort,Binsort,Radix sort. MEDIUM terminado,volverLOW bajo nueva coordinación; noHash/RN/grafos/roles ejecutados.


## Counting sort LOW baseline collected; instruction fidelity pending

Asignación coordination-sorting-counting-baseline-low-20261002 / sorting.counting-baseline-low. Seis casos<=4,416eventosC/60frames,356omitidos; resultados6/6. LOWcorrige métricas24comparisons/54moves,rawconsole/guardFalse/invariant agregado yfast->step optin;sinC/H ni8cierres modificados.26IDs14pass12causalesfail4.49s,sinxfail. Browser3casos64restauraciones0POSTextra/JSerrors,main/JSON/reload5etapas;4programasUI3callsC17/Doxygen0warnings,3calloc3free0live y3faultprobes aparte. Raw8public+4helperguards,capexacto3fronteras/above/fullspan/callocfail seguro:size_t64 exigido;32bitfullspan noejecutado ySIZE_MAXbranch noverificado. Evidencia evidence/visible-sorting-counting-baseline-low/{README.md,summary.json,regression-final.log,browser-verified/report.json}; planMEDIUM sorting-counting-instruction-review-plan.md sinimplementar. Preview18264/12108D/run.py127.0.0.1:5051actualizado. Baselinecompleto, instrucciónCounting pendiente;global13/22/docs121/208sincambio,ocho cierrespreservados.


## Counting sort verified closure for recorded cases

Asignación coordination-sorting-counting-medium-20261002 / sorting.counting-instructions. Seis casosn<=4,k<=4,C416eventos=416frames,scope/type/init/aliases/for/ifs/calloczero/arraywrite-decrement/free/source/before fieles;24cmp54moves0swaps.41IDs únicos pasan(26originales intactos/12causasresueltas+15nuevos),10.32s. UI832restauraciones0extraPOST/JSerrors,fast->step,nextprev,reload/main/JSON y5etapas;7programasUI únicos=4LOWreutilizados+3nuevos,6calls6calloc/free0live,C17/Doxygen0warnings,6faultprobesaparte. C/H/oráculoJSONL y8cierres anteriores intactos. Scopeacotado explícito: outside n<=4/k<=4 conserva rutaagregada/rango1000000aceptado, sin recorderO(k²);size_t64 y32bitinseguro noejecutado,SIZE_MAXbranchtrue noverificada. Evidencia evidence/visible-sorting-counting-instructions/{README.md,summary.json,regression-combined-current.log,browser-final-current/report.json}; decisión sorting-counting-resource-bound-decision.md. Preview4716/21140D/run.py127.0.0.1:5051actual. Cierre solo6casos;global13/22/docs121/208sincambio,nueve cierres finitos,pendingBinsort/Radix. MEDIUMterminado,volverLOW bajo próxima coordinación.


## Counting sort partial: admitted-input fidelity pending

Nueva instrucción coordination-sorting-counting-scope-review-low-20261002 / sorting.counting-scope-review-low. Counting quedaPARCIAL:guardn<=4/k<=4 conserva solo subsetfiel; cuatro entradasadmitidasfuera4(n5/k5,n2/k6,n2/k1001,n80/k1) pasanresultado pero0eventtyped/helperminmax/free. Otras8rutas inspeccionadasestáticamente:sin cutofffixture análogo,global80int32;no se reejecutaron. Evidencia previa416eventos/41tests/832restauraciones preservada,nocierre global delmétodo. Motivo guardO(k²) explica protección temporal,no soluciónfinal. Decisión sorting-counting-scope-correction-decision.md supera interpretación suficiente de resourcebound; plan sorting-counting-expanded-fidelity-plan.md propone sparse/deltas/paging/losslessspans/virtualización para todaentradaadmitida,sincontrato/restricciónsilenciosa. Sinimplementacióncompleja/C/H/producciónalterada/pruebasmasivas. Global13/22/docs121/208sincambio,ochocierresfinitospreservados+Countingparcial;Binsort/Radixnoiniciados.


## Counting sort expanded-domain verified closure with explicit limits

RevisiónLOW 2026-10-02T20:08:31.886208+00:00,coordination-sorting-counting-consolidated-review-low-20261002 / sorting.counting-expanded-fidelity. Criterio ytrazabilidad: sorting-counting-consolidated-closure-decision.md. UI n1..80/int32/size_t64; éxito k<=1m, rangoERROR ycallocNULL controlado; un núcleo sinfallback, spans3eventos/bucket exactos, scopes/source/retirada/replay/caller.59IDs vigentes yhashes productivosidénticos;3regresiones necesarias pasaron2.19s (subconjunto, no nuevosIDs). Oráculos416+5504eventos en gruposprevios,4errores450eventos,2digests máximos ybrowser/callers se reutilizan, no pruebas nuevas de este LOW. Ocho cierres previos preservados; Countingnoveno/11, pendientesBinsort/Radix. Sin hueco funcional abierto detectado en alcance; límites32bit/digest/fallo simulado/QAglobal explícitos, ninguna garantía exhaustiva. Evidencia evidence/visible-sorting-counting-consolidated-review-low. BaselineBinsort preparado, no ejecutado; guardafter informe solamente. Global13/22/docs121/208sincambio; preview18188/14756D127.0.0.1:5051sinreinicio. Sinpush/merge/despliegue/red.


## Binsort LOW baseline collected; instruction fidelity pending

2026-10-02T20:48:10.676126+00:00,coordination-sorting-binsort-baseline-low-20261002 / sorting.binsort-baseline-low. Evidencia propia evidence/visible-sorting-binsort-baseline-low ysorting-binsort-baseline-checkpoint-low.md. Ochoresultados8/8,métricasCcorregidasopt-in;4341eventoscompuestos(delegadoreusadoseparado) frente238agregados.32IDs19pass/13failcausales,0xfail;3UI78restauraciones/0POSTextra/JSerrors/faststep;4originalescallersC17Doxygen0/6calls6calloc6free0vivos. LímitesCcap1m/fullspansize64safe;APIsentinelantescopies, noOOM. ModelMemoryError controlado ymetadatosaceptadospreservados. MEDIUMdelimitado wrapperdeCountSparse/paging/ERRORscopes/replaystep;sinimplementar/cutfixture/C_Hedits/closed9reruns. Binsortinstrpendiente,9/11/global13/22/docs121/208igual. Guardafterreporta;previewcanónicoloopback5051. Sinpush/merge/deploy/red.


## Binsort MEDIUM checkpoint before method closure

2026-10-02T21:21:22.522603+00:00 — coordination-sorting-binsort-medium-20261002 / sorting.binsort-instructions.13fallos resueltos,60IDs únicos vigentes(32originales intactos+28nuevos),4341eventos éxito y462ERROR C/API iguales. TapeBin wrapperCount sincutoff, parámetros suspendidos/alias/source/scopes/free, /step/pages/reload/export sinredispatch. UI5probes+2errores adicionales/0POSTextra/JSerrors/5secciones;80/k1m conserva3000912pasos en1231records/12744946bytescontenedores/DOM64.4callers exactosreusados+1nuevo C17/Doxygen0/1alloc1free0vivos. C/H/nueve cierres/commonruntime/originaltestSHA intactos. Evidencia evidence/visible-sorting-binsort-instructions ysorting-binsort-instructions-checkpoint-medium.md. Binsort NOcerrado: revisiónLOWpendiente antes de10/11;Radixnoiniciado. Límites int32/size_t64/noexhaustividad/fingerprints/noOOMreal/fixtureNULLrotulada/memoriaretendida noRSS. Global13/22,ledger121/208 sin incremento. Previewpropio5051actualizado;afterinforma,sinpush/merge/deploy.


## Binsort expanded-domain verified closure with explicit limits

2026-10-02T21:32:01.509197+00:00 — Consolidación LOW autorizada: coordination-sorting-binsort-consolidated-review-low-20261002 / sorting.binsort-expanded-fidelity. Décimo de once bajo UI1..80/int32/size_t64, éxito k<=1m y errores registrados, por equivalencia estructural sobre Counting byteidéntico más oráculos y pruebas.60IDs vigentes,3probes sensibles3pass1.30s son subconjunto. C/H/nueve cierres/runtimes intactos; preview5051 actual verificado sin reinicio.4341eventos éxito y462errores, UI/callers/recursos se reutilizan, no nuevas pruebas Count. Límites, plataformas y simulaciones: sorting-binsort-consolidated-closure-decision.md y evidence/visible-sorting-binsort-consolidated-review-low. Sin brecha funcional abierta detectada en este alcance ni exhaustividad; fingerprints/NULLsimulado/noOOM/RSS/ABI32bit explícitos.10/11 no cierra auditoría global13/22/ledger121/208. Siguiente: Radixbaseline LOW autorizado con nueva asignación yguarda; sinpush/merge/deploy.

## Binsort verified instruction closure with explicit scope

La decisión sorting-binsort-consolidated-closure-decision.md consolida sorting.binsort-instructions sin reimplementar ni reejecutar ese MEDIUM. Dominio/errores/equivalencia y límites allí registrados; evidencia MEDIUM preservada.


## Radix LOW baseline collected; instruction fidelity pending

2026-10-02T21:55:30.309953+00:00 — coordination-sorting-radix-baseline-low-20261002 / sorting.radix-baseline-low. OchoresultadosC/API iguales;3748eventos estructurales/seleccionados frente72agregados.39IDs18pass21fallos sinxfail: controles/helper/lifecycle/línea/comparaciones/modelMemoryError500/stepredispatch/rawconsole. UI3casos78restauraciones0POSTextra/JSerrors5secciones;historial/main/JSON conservados,faststep/reload pierden traza.3originales callersC17/Doxygen0/6calls60alloc60free0vivos. Mismos8éxitos+6faultprobes sobreC/Horiginales, no doblecoverage;NULLmallocsimulado,int32size_t64/INT_MINdefinido,noOOM/UB. Código/C_H/diez cierres SHAidénticos ypreview16304/24752sinrestart. Baselinecompleto, Radixinstrabierto;10/11/global13/22/ledger121/208igual. Evidencia evidence/visible-sorting-radix-baseline-low ysorting-radix-baseline-checkpoint-low.md. MEDIUMplan preparado sin implementar, requiere nueva asignación. Sinpush/merge/deploy.


## Radix MEDIUM checkpoint before method closure

2026-10-02T22:45:24.844908+00:00 — coordination-sorting-radix-medium-20261002 / sorting.radix-instructions. Kernel/tape/typedvars/helper/memoria/errors/replay corregidos. Final48IDs47pass1fail71.35s; original39=38pass1failSHAintacto. Rojo presupuesto<5000contra11408eventos C; decisión pendiente documentada, no debilitar ni cortar.16casos/17295frames variables/prev/alias/scopes/pila iguales;8originales3748y4faults reutilizados,máximo+3segundosRun nuevos. UI3942restauraciones pequeñas+24muestras máximo+230errores simulados,0replayPOST/JSerrors/5secciones.3callers exactosreusados+1máximo C17/Doxygen0/22alloc22free0live. Tape47.9MB,JSON18MB,DOMobservado2031,noRSS/OOMreal/exhaustividad. Preview21196/19092D5051actualizado. Radixabierto10/11/global13/22/docs121/208sin cambio. Evidencia evidence/visible-sorting-radix-instructions; siguiente revisiónLOW/decisión/cierre, sinpush/merge/deploy.


## Radix LOW budget diagnosis; no test change or closure

2026-10-02T22:59:33.135621+00:00 — coordination-sorting-radix-budget-low-20261002 / sorting.radix-budget-low. <5000es expectativa auxiliar tests/test_sorting_radix_baseline_low.py:78, no requisitoaprobado/transporte localizado; lenTape cuenta eventos/registros, noframesJSON. Cota UI11564por controlflow, alcanzada probeC17 nuevo22alloc22free0live.10distribuciones midenretenciónmax49.27MB,seed16/~194KB,buildhasta9.09s,page128decode+JSONhasta0.30s;densohasta23.21MB/7.73s. Acotación estructural/medidas finitas,noSLA/RSS/globalconcurrency. Propuesta corregirmismoIDhaciaigualdadC/cleanup/gatestransporte, sinaplicar. OriginalSHA/copiapreservados/producto/C_H/intocables. Radixrojoabierto10/11/global13/22/docs121/208. Evidencia evidence/visible-sorting-radix-budget-low ysorting-radix-budget-diagnostic-low.md;preview5051sinrestart. Sinpush/merge/deploy.


## Radix expanded-domain verified closure with explicit limits

2026-10-02T23:12:20.739107+00:00 — ConsolidaciónLOWautorizada coordination-sorting-radix-consolidated-review-low-20261002 / sorting.radix-expanded-fidelity. UndécimodeonceSorting por kernelC-equivalenteuniformeUI1..80int32/size_t64, cota11564y oráculos finitos. Gate<5000sincontratocorregido conoriginalSHA/copiamismoIDycompletaigualdadC/typedobservations/result/cleanup.48IDs48pass74.05s, rerunfinalmismoID1pass9.05s es subconjunto, no49. Producto/C_H/diezcierresSHAintactos. Evidencia MEDIUM/LOWreusada,sin repetir cierres. LímitesmallocNULLsimulados/noOOMreal/noRSS/ABI32/SLA/fluidezuniversal;retención49.3MB/build9.09s/denso23.21MBobservados. Global13/22/docs121/208iguales. Preview21196/19092D5051HTTP200actualsinrestart. HashH1aprobado es siguiente no bloqueado propuesto, mapa preparado sin ejecutar; guardafterreporta. Sinpush/merge/deploy.

## Radix verified instruction closure with explicit scope

sorting-radix-consolidated-closure-decision.md consolida sorting.radix-instructions sin nueva implementación ni repetirMEDIUM; alcance/errores/plataforma/recursos/limitaciones/evidencia originales conservados.

## Hash creation/insertion LOW baseline collected; instruction review pending

See hash-create-insert-baseline-checkpoint-low.md. Eight native/API sequences; two real red creation regressions; caller/docs verification pending. No Hash instruction closure or global count increment.

## Hash create/insert MEDIUM checkpoint ready for LOW review

Checkpoint hash-create-insert-instructions-checkpoint-medium.md:93IDs verdes;34operaciones/oráculo retenido+errores delimitados;404framesUI/384restauraciones,0redispatch;5callersC17,25alloc/free,25NULLsimulados;Doxygen0warnings. C/H/11Sorting/arnés/test3 originales preservados. LOW debe revisar límites de scopes/tipos/recursos antes de cierre. Otros9Hash/global/RN/Grafos pendientes;13/22 ydocs121/208 sin incremento.

## Hash create/insert LOW review completed with blockers

Cierre de dos métodos retenido: init_parameter pedagógico sobrescrito con rootcapacity0 y falta parámetro scopedconst de th_indice, demostrados C17 _Generic/2regresiones rojas.93IDs previos únicos conservados,2nuevos rojos(95actuales,no95corrida). Recursos finitos medidos34ops;producto/C_H/test3/11Sorting intactos;preview5051 confirmado. Checkpoint hash-create-insert-consolidation-checkpoint-low.md; siguiente baseline condicionado a cierre todavía no iniciado. Mapa hash-next-pending-map-after-scope-review-low.md. Global/docs sinincremento.

## Hash scoped parameter correction checkpoint ready for LOW

Dos brechas scopes/type corregidas:capacidadparameter separado delstructfield;helperconstparampropio conalias/expiración.95IDs originales sineditar pasan+3nativosnuevos distintos(98únicos),404framesUI/384restauraciones0redispatch. C/H/11Sorting preservados. hash-scope-fix-checkpoint-medium.md antescierre; LOWrevisaroverhead/límites. No siguiente baseline/globalincremento.

## Hash creation/insertion finite cases verified closure

Cierre sólo casos registrados create_table/insert, decisión hash-create-insert-finite-closure-decision-low.md.98IDs previos únicos verdes conservados,34opsC+3casestypesalias,UI404/3840redispatch,caller25alloc/free25NULL,Doxygen0. Overheadactual6.88MBpico/646047bytesJSON/0.524s instrumentado en3/17;noSLA/hugecap. Otros9Hash pendientes yglobal/docs sinincremento; siguiente baseline get/contains autorizado según hash-next-pending-map-after-finite-closure-low.md.

## Hash get/contains LOW baseline collected; instruction review pending

Después cierrecreate/insertfinito,24consultasC/APIresultadoscoinciden;4getausentes200vs400spec,4normalizacionesfalsas(residuo0),24sin debugscopes.3regresiones rojas nuevas;98IDsprevios/C_H/11Sorting preservados(101actuales,no101corrida). UI5queries0redispatch,mainmutanteomiteconsultas conformelimitaciónactual. Checkpoint hash-get-contains-baseline-checkpoint-low.md delimitaMEDIUM,noimplementado. Otros9Hash/global/docs sin cierre/incremento.


## Hash query instruction MEDIUM checkpoint ready for LOW

Asignación coordination-hash-query-instructions-medium-20261003; operación hash.get-contains-instructions-medium. Correcciones y evidencia finita completadas: [checkpoint](hash-query-instructions-checkpoint-medium.md). 106IDs/106pass,24resultadosC preservados,3regresionesgreen,UI450/425sinredispatch,4callersC17/17alloc-free/0vivos/Doxygen0. Un testlegacy ausente400 sustituye expectativa200 con mismoID/originalarchivado. C/H/createinsert/11Sorting preservados. No cierre funcionalget/contains; siguiente revisiónLOW; retenciónlarga no certificada; global13/22/docs121/208 sinincremento.


## Hash query finite cases verified LOW closure

Get/contains cerrados sólo casos registrados en [decisión](hash-query-finite-closure-decision-low.md): Hash4/11=create_table,insert,get,contains;7pendientes exactos remove,keys,values,items,stats,clear,destroy_table.106IDs únicos=98intersección+8nuevos;24native/UI/caller solapados no sumados. Retenciónlarga/OOM/RSS/SLA sin certificar; global13/22/docs121/208 unchanged. Siguiente baselineLOWremove del [mapa vigente](hash-next-pending-map-after-query-closure-low.md).


## Hash remove LOW baseline collected; instruction review pending

[Checkpoint](hash-remove-baseline-checkpoint-low.md):23C/APIresultados/ordenestadofinalcoinciden,317eventos/17free.9IDs nuevos6pass3rojas,106previos preservados/disjuntos,no115pass. Defectos: mutación/costos/retorno anticipados, scopes ausentes, normalizaciónresiduo0falsa. UI232/219/0redispatch/0JS sólo replaytraza;4callersC17/21allocfree0live/Doxygen0. Hash4/11finito/7pendientes;global13/22/docs121/208 unchanged. MEDIUM propuesto antesfix/cierre, no ejecutado.


## Hash remove MEDIUM checkpoint ready for LOW

[Checkpoint](hash-remove-instructions-checkpoint-medium.md): tresregresiones originalesgreen,123uniqueIDs=106previous+9baseline+8new;122pass47.14s+1guard0.49s disjoint/final19subset14.64s.23C/APIresults/436events/17free causal;UI436frames413back,final97/92overlap,0redispatch/JS/5secciones/reloadigual.7authenticC17mains34allocfree0live/34NULLpoints=4SHAreused21+3new13,Doxygen0. C/H/H1/4Hashfinite/11Sorting/115originalIDs preserved. Remove funcionalpendienteLOW,global13/22/docs121/208 unchanged. C1handoff sóloevidencia,no matriz/ledger editado;auto-review deltaADDED rechazado,guía no normativa alternativa sincontratosnuevos. PreviewD5051launcher38832 actual.


## Hash remove finite cases verified LOW closure

[Decisión](hash-remove-finite-closure-decision-low.md):123uniqueIDs verdes/19rerunsubsetnoextra;23CAPIresultados436events,scopes/lifetime/count/resources verificadosfinito. H1 yC_H intactos;deltaADDEDrechazado no creado/expansión no implementada, notas sóloobservación. Hash5/11create_table,insert,get,contains,remove;6restanteskeys,values,items,stats,clear,destroy_table. Siguiente baselineLOW keys/values/items del [mapa](hash-next-pending-map-after-remove-closure-low.md). Sanitizadores/sesioneslargas/global13/22/docs121/208/C1 pendientes, no publicación.


## Hash listings LOW baseline collected; instruction review pending

Baseline registrado en hash-listings-baseline-checkpoint-low.md: 8 IDs nuevos, 5 pasan/3 rojos; 12 proyecciones C/API coincidentes, 39 llamadas formatter, 18 consultas UI stub. Cuatro callers omiten listados aunque C17/Doxygen/23 alloc-free pasan. Hash conserva 5/11 cierre finito. Plan MEDIUM pendiente; sin cambios producto/C_H/contratos.


## Hash listings MEDIUM checkpoint; LOW review pending

Corregidas tres regresiones sin nuevos contratos/C_H: 134 IDs únicos pasan; 39 casos/2953 eventos C y 12 proyecciones; UI 3270/3252 más focos solapados; cuatro callers completos C17/Doxygen/23 alloc-free. Evidencia y límites en hash-listings-instructions-checkpoint-medium.md. Hash sigue 5/11 hasta revisión LOW; global/docs/C1 sin cambios.


## Hash listings finite cases verified LOW closure

Cierre finito keys/values/items: hash-listings-finite-closure-decision-low.md y evidence/visible-hash-listings-finite-consolidation-low/review.json. Hash8/11; siguientes stats/clear/destroy. 134IDs únicos, no suma de focos; límites y recursos registrados. Global13/22/docs121/208/C1 1/12 unchanged.


## Hash stats LOW baseline collected; instruction review pending

Baseline stats:8IDs nuevos5pass/3red,27buffersC,8APIobservaciones enteroscoincidentes pero4diferenciasfloat,UI24/16stub,4callerssinqueries aunqueC17/Doxygen/16alloc-free. Checkpoint hash-stats-baseline-checkpoint-low.md y planMEDIUM pendientes; Hash8/11,sinproducto/C_H/contratos nuevos.


## Hash stats MEDIUM checkpoint; LOW review pending

Stats3regresiones corregidas,145IDs únicos verdes,27buffers/1658eventosC/542condiciones/1424campos;4probesfloat separados. UI634/626sinredispatch;4callersC17/Doxygen/16alloc-free completos. APIcociente preservado y floatC separado. Checkpoint hash-stats-instructions-checkpoint-medium.md; LOW pendiente,Hash8/11/global/docs/C1 unchanged.


## Hash stats finite cases verified LOW closure

Statsfinito cerrado: hash-stats-finite-closure-decision-low.md/evidence/visible-hash-stats-finite-consolidation-low/review.json. Hash9/11;145IDsúnicos,no suma11focos;precisiónC/APIseparada intacta yrecursoslimitados. Sóloclear/destroy pendientes. Global/docs/C1unchanged.


## Hash clear destroy LOW baseline collected; instruction review pending

16IDs nuevos11pass/5red;core16C/APIfinalescoincidentes,17freeobjetivo;recreación2caminosseparadosconsufijosnuevos. UI316/300genérico;10callersC17/Doxygen/47alloc-free. Scopes/pointersretirados/guardas instruccionalesabiertos. Checkpoint hash-clear-destroy-baseline-checkpoint-low.md;Hash9/11,productoC_H/contratosintactos.


## Hash clear destroy MEDIUM checkpoint; LOW review pending

Cinco baseline rojos corregidos;164IDs únicos verificados por unión162+2últimos(no corrida única164verde),24C/592eventos/170condiciones;UI412/396conDOMvidas/sinredispatch. Diez mains idénticos reutilizan C17/Doxygen/47alloc-free47NULL por hash. Checkpoint hash-clear-destroy-instructions-checkpoint-medium.md;Hash9/11,LOWpendiente/global/docs/C1unchanged.


## Hash clear destroy finite cases verified LOW closure

RevisiónLOWvalida164IDs únicos porunión/hashactual,24C/592eventos/170condiciones yUI412/396sinredispatch;10callersidénticos reusanC17/Doxygen/47ownership47NULL. Decisión hash-clear-destroy-finite-closure-decision-low.md cierra sóloclear/destroyfinito:Hash11/11; resumenhash-finite-closure-summary-low.md. Global13/22/docs121/208/C1unchanged,sinexhaustividad. Siguientepropuesta stack.limpiar-baseline-low sóloenmapa audit-next-pending-map-after-hash-closure-low.md trasrecuperarevidencia;ningúnnuevoMEDIUM iniciado.


## Stack limpiar LOW baseline collected; instruction review pending

Nuevaasignación coordination-stack-limpiar-baseline-low-20261003;baseline16IDs8pass8rojos1.84s sinxfail.9Ccalls/76eventos/25condiciones (8core72eventos vs64frames,8rootstoredivs);8finalesigual. UI128forward/112back ambasvistas0POST/JS,cincosecciones;reload0/4conservación: pierde traza aunquehistorialpersiste.4callersQAoffline C17/Doxygen0/8alloc-free noequivalenmainproducto ausente. Producto515hashesinalterados;HashSorting/popcerrados no reabiertos.Global13/22(20+2fuente),docs121/208unchanged. Checkpoint stack-limpiar-baseline-checkpoint-low.md/planstack-limpiar-instructions-plan-medium.md delimitado,MEDIUMnoiniciado.


## Stack limpiar MEDIUM checkpoint; LOW review pending

Asignación coordination-stack-limpiar-instructions-medium-20261003. 20 IDs/20 pass, 9 C calls/76 events/25 conditions, UI 144/128 y cuatro recargas exactas; cuatro main.c reales C17/Doxygen, 8 alloc/free y ocho fallos NULL balanceados. Checkpoint stack-limpiar-instructions-checkpoint-medium.md y evidence/visible-stack-limpiar-instructions-medium/summary.json. C/H y motores cerrados conservados. Pendiente revisión LOW antes de cierre finito. Global13/22 y docs121/208 sin incremento.


## Stack limpiar finite cases verified LOW closure

20IDsactuales16originales/20passreused;9Ccalls76events25conditions/UI144128/4reloadexact/4mainC17Dox0/8allocfree/8NULLsimulated. Sólo stack.limpiar.instructions casos finitos cerrados según stack-limpiar-finite-closure-decision-low.md; resto en audit-pila-colas-pending-map-low.md. Global13/22/docs121/208unchanged. Próximo baselineLOWColalimpiar autorizado, pendiente assignment fino/before antes ejecutar.


## Queue limpiar LOW baseline started; instruction review pending

9Ccalls92events25conditions,8APIcalls80framesvs88Ccoreevents;24rootvaluematches,8heapdetachedomissions,8voidreturnsomitted.12IDs5pass7redporunión con1QAcountrecovered. C17/C_H Doxygen0,8allocfree0live; browser/reload/actualcaller/resourcespeak pendientes. No producto cambiado ni MEDIUM. Ver queue-limpiar-baseline-checkpoint-low.md/evidence/visible-queue-limpiar-baseline-low. Global13/22/docs121/208unchanged.


## Queue limpiar LOW baseline complete; bounded MEDIUM pending

9Ccalls92events25conditionsreusedhashes/12IDsy7rojosconservados;4nuevosIDs2pass2red,16union7pass9red. Browser1601448calls5secciones0POSTJS,4historyreload/0tracereload.4mainsDOMC17/8allocfree0live/8NULLsimulatedexit0appliedmisleading/Dox0warningspero0docmain. Recursos716226Pythonbytes62803JSONmax0,051sfinito. Checkpoint queue-limpiar-baseline-completion-checkpoint-low.md,planMEDIUM queue-limpiar-instructions-plan-medium.md pendiente coordinación,no productoeditado ni cierreCola. Global13/22docs121/208unchanged.


## Queue limpiar MEDIUM checkpoint; LOW review pending

Asignación coordination-queue-limpiar-instructions-medium-20261003 completada:21/21 tests (16IDs originales),9Ccalls92events25conditions reutilizados; UI176/160,4reloadexact,5secciones,0POST/JS.4mainsDOMC17/Doxygen0+4documentados;8alloc/free0vivos y8NULLsimulated retorno1 sin éxito falso. C/H/motorescerrados conservados; checkpoint queue-limpiar-instructions-checkpoint-medium.md. RevisiónLOW antes cierre finito. Herramientas locales operativas06:21:32UTC, sin bloqueo ni comandos activos; preview87976/43684D5051. Global13/22docs121/208sin incremento.


## Queue limpiar finite cases verified LOW closure

Sólo queue.limpiar.instructions fixtures finitas cerradas;21IDsactuales/16originales,9C92events25conditions/UI176160/4reloadexact/4mainsC17Dox0+doc/8NULLsimulatedreturn1clean. Manifests vigentes y logs reutilizados, no reruns. Decisión queue-limpiar-finite-closure-decision-low.md;mapa audit-pila-colas-pending-map-after-queue-low.md. Siguiente baselineLOWPrioridadlimpiar autorizado, exigir assignment fino/before. Global13/22docs121/208sin incremento.


## Priority queue limpiar LOW baseline started; instruction review pending

9 C / 153 eventos / 41 condiciones; 32 observaciones coincidentes en valores, cantidad y cardinalidad; 16 IDs: 9 pass / 7 red. No producto modificado. Ver priority-queue-limpiar-baseline-checkpoint-low.md. Pendientes navegador/recarga/main/recursos; no cierre funcional.


## Priority queue limpiar LOW baseline completed; MEDIUM review pending

Baseline finito completo sin producto: nativo9/153/41 reutilizado, UI280/264 ambosviews,4reloadhistory/0trace,4C17mains8allocfree8NULLfaultsexit0falsesuccess,Dox6inputs0warnings0/4main docs;22IDsdisjuntos12pass10fail (16reused+6new),resources measured. Ver priority-queue-limpiar-baseline-completion-checkpoint-low.md y propuesta MEDIUM acotada. No cierre funcional/global.


## Priority queue limpiar MEDIUM checkpoint; LOW review pending

26/26IDs(22retained+4disjoint),9C153events41conditions32obsfullmatch,UI296/2804reloadexact0redispatch/JSerrors,4actualDOMmainsC17Dox4docs0warnings8alloc/free0live8NULLfaultscleanupreturn1nofalsesuccess. Resources measured5,857,080peakPythonbytes/509,335JSON/0.2305498s finite only. C/H/closedengines unchanged,215same4sharedgated+2newmodules. Ver priority-queue-limpiar-instructions-checkpoint-medium.md; termina MEDIUM y vuelve LOW para revisión finita, sin cierre global.


## Priority queue limpiar finite cases verified LOW closure

LOWconsolidación26IDsactuales/26passreused(22originales),288SHAúnicosvigentes,9C153events41conditions32obs/0divs,UI296/2804reloadexact,4actualC17Dox4main docs,8NULLcontrolledreturn1/ownershipcorrect. Se cierra sólo priority_queue.limpiar.instructions parafixtures finitos; límitespeakPython5.86MB/JSON509335bytes no stress universal. Ver priority-queue-limpiar-finite-closure-decision-low.md y audit-pila-colas-pending-map-after-priority-low.md. Propone stack.apilar-baseline-low sin iniciar;no reabrircierres/decidirRNGraph. Global13/22docs121/208sin incremento.


## Stack apilar LOW baseline complete; bounded MEDIUM pending

26IDs12pass14fail0xfail,14C124events27conditions(13original+only1emptyrootmallocNULL)/32values+heapcountmatches,8API/8UI112/964history0trace reload.4historiasmainsDOMvsHTTPambosC17:DOM12alloc0free12live/faultsexit0falseapplied/0docs,HTTP12balanced12faultsreturn1/4docs;no doblecontar superficies. Product221SHAunchanged/resources513194peakPythonbytes27562JSON0.0374567sfinite. Recuperó8pushprevias/sinreabrirpop/cleanupHashSorting;baselines no cierrefuncional. Ver stack-apilar-baseline-checkpoint-low.md,propuestaMEDIUM ymapaafter-stack-push-low. No producto/contratospublicación. Global13/22docs121/208unchanged.


## Stack apilar MEDIUM checkpoint; LOW review pending

Checkpoint recuperado LOW trasoffline;30/30reutilizados(26original+4disjoint),14C124events27conditions32obs0divs;UI160/1444exactreload+realNextnoPOST;4historiasDOMHTTPC17Dox4main0warnings12alloc/free0live+12NULLporruta return1nofalsesuccess.217/221same4sharedexpected+2new,C/Hclosedenginesunchanged. Ver stack-apilar-instructions-checkpoint-medium.md; limitaciónSHAhistóricoausente explícita,freshmanifests. Sin cierrefuncionalglobal13/22docs121/208intactos.


## Stack apilar finite cases verified LOW closure

Cierra sólo stack.apilar.instructions parafixturesregistrados conforme nuevaasignaciónLOW.443SHAúnicos0diferencias,30IDactualesidénticos(26+4),30passreutilizado sinC/UI/testsrerun;14C124events27conditions32obs0divs/UI160/1444exactreload+realNextnoPOST;4historiasDOM/HTTPC17Dox4doc0warning12balanced12NULLporruta. LimitaciónSHAhistóricofinalausente conservada,freshmanifestverificado. Ver stack-apilar-finite-closure-decision-low.md y audit-pila-colas-pending-map-after-stack-push-finite-low.md. PróximoPROPUESTOqueue.encolar-baseline-low,noejecutado. C/H/cierresRNGraphdecisiones/global13/22docs121/208intactos,no publicar.


## Stack apilar traceability LOW qualified current-code check

FaltabaSHAfinal6productorepresentatividad30testshistórica limitada. Beforecorregido0:current14C124events27conditions32obs0divsinC rerun,oneUIempty40/36exactreloadrealNextnoPOST,mainsHTTP4exacthistoricbytes,seisSHAantes/despuésequal. No30suite ni4UIrerun;restoUI/resourceshistóricoscalificados. PrimerguardIDpuntuaciónrechazado/intentoanticipado excluidopreservado. Sinproducto/C/H ysinampliarcierre;encolarLOWpendiente nuevaasignación. Ver addendumcheckpoint/decision yvisible-stack-apilar-traceability-low.


## Queue encolar LOW baseline complete; MEDIUM pending

33ID19pass14fail(29new+4previosencolargreen),14C140events35conditions/5mallocNULL+qNULL,40valuesheapmatches8frontrearfinalrootdivs;UI144/1284historyexact0traceexact,noJSextraPOST;4DOMmainsC17Dox4docs12balanced12NULLreturn1/HTTPmain404sinallowlist. Recursos658901Pythonpeak/42055JSON/.046212sfinite.223productSHAidenticalC/H/cierresintactos. Ver queue-encolar-baseline-checkpoint-low.md/MEDIUMpropuesto/mapafterqueueenqueue. Nueva prioridadRNvalidadorcompletoaprobado;noMEDIUMencolarniGraphcontratos. Baseline no cierrefuncional/global/C1ledger.


## RN full validator MEDIUM finite implementation checkpoint

V3implementado/Cpublicexport/RAWtrace/caller;17fixturescontrato17/17 y52regresionespass,antes9fallosresueltos. Ver red-black-full-validation-implementation-checkpoint-medium.md y evidence/visible-red-black-full-validator-implementation-medium/acceptance-matrix.md. AlgoritmosRNpreservados;cierrefinitocasosregistrados,noglobal/C1. Encolarbaselinependiente. PróximoLOWrevisión/consolidación, no reimplementar desdeafter.


## RN V3 LOW consolidation; independent QA pending

223productoSHA/1031evidenciaSHAverificados;13filas ymapas reales empaquetados en evidence/visible-red-black-full-validator-consolidation-low. Cierrefuncionalfinito candidato pendienteQA01a0ff54-79d7-7520-8e9f-224ef5ed700f;sanitizeralternativasdueñorevisor,noarchive/productedit/repeat suites. Ver red-black-full-validation-consolidation-checkpoint-low.md. Encolarpendiente sinMEDIUM.


## RN V3 finite functional closure LOW

QAindependientefuncional/documentalACEPTADA, RN-IMPL-01resuelto;ver red-black-full-validator-finite-closure-decision-low.md y evidence/visible-red-black-full-validator-finite-closure-low/closure-evidence.json. Cierresóloalcancefinito;sanitizers/global/C1pendientesseparados,noarchive,noreimplementación.


## Encolar MEDIUM readiness LOW después cierreRNfinito

Planvigente sin nuevo contrato:33baseline19/14conservado,no rerun,colaC/Hbytesiguales. Propuestaqueue.encolar.instructionsM1-M3 en queue-encolar-instructions-plan-medium-ready.md,requiereasignaciónMEDIUM/before. RNfinitoQAaceptadocerrado,sanitizers/global/C1pendientes;ningúnproductoeditadoenreadiness.


## Encolar MEDIUM finite implementation checkpoint

36pass(33IDsoriginales+3sesión),baseline19/14conservado;140eventosCcomparadossinreexecutar/40roots0divs;UI192/1764reloadSiguientereal0POST. C/Hprotegidos;4mainDOMidénticos+C17/Doxreusados. Recursosfinitemayoresdocumentados. Verqueue-encolar-instructions-checkpoint-medium.md y evidence/visible-queue-encolar-instructions-medium/summary.json. VolverLOWrevisiónfinita, noampliación/cierreglobal.


## Queue encolar finite cases verified LOW closure

Cerrado sólo queue.encolar.instructions:36IDs únicos(33baseline+3sesión,mismosMEDIUM,0newLOW),140eventosC/35condiciones reutilizadosrevisados/40roots0divs;UI2vistas192/1764reloadSiguientereal0POST porSHA;4mainDOM/C17/Dox/12balanced12NULLreusados.226producto/133baseline/63artefactosMEDIUMSHAiguales;1previewlogappend-onlycalificado. Recursos finite2.17MBPython/157.7KBJSON,no universal. Verqueue-encolar-finite-closure-decision-low.md yevidence/visible-queue-encolar-finite-consolidation-low/summary.json. Mapaafterqueueenqueuefinite y siguientePrioridadEncolarbaselineLOW sólopropuesto/noempezado. C/Hintactos/cierrespreviospreservados/SDDblockedintactos/Graphpendiente/no publicar.


## Priority queue encolar LOW baseline complete; bounded MEDIUM pending

42uniqueIDs20pass22fail0xfail(41new+1previo);14C242events48conditions12balanced,8API72obsfinalFIFOstablematchperoquantity8/front8/rear8/heap16divs;duplicateheap/falsefreecontador/guardsopesmasks/return/reload. UI240/2244historyexact0traceexactNextdisabled0extraPOST;4actualC17main12balanced12NULL/Dox4docs0warnings/HTTPmain404. Recursosfinite979576Python85753JSONbytes. ProductoC/Hintacto,cierrespreservados. Verpriority-queue-encolar-baseline-checkpoint-low.md yevidence/visible-priority-queue-encolar-baseline-low/summary.json;planMEDIUMpropuesto(noimplementado),nuevainstrucciónbeforeantesproducto.


## Priority queue encolar MEDIUM finite implementation checkpoint

46pass(42originalIDs+4session,legacyuna vez),baseline20/22intacto;242reusedCevents14calls48conditionsfullmatch72obs0divs. UI336/3204reload/Siguientereal0POST y4affectedcurrent-sourceGETreloadchecksnosumar.4mainDOMbytesidénticos/C17Doxownership12balanced12NULLreusados. Recursosfinite4.98MBPython367.7KBJSONincrementoregistrado.228productos/6QAsourcesSHAfinales/todosC_Hyotherclosedmodulesintactos. Verpriority-queue-encolar-instructions-checkpoint-medium.md yevidence/visible-priority-queue-encolar-instructions-medium/summary.json. TerminaMEDIUM→LOWfiniter eview,noglobalclosure/Graph/SDDblocked/publish.


## Prioridad Encolar: consolidación finita LOW 2026-10-03

Ver priority-queue-encolar-finite-closure-decision-low.md y evidencia propia visible-priority-queue-encolar-finite-consolidation-low: 46 IDs únicos reutilizados con hashes actuales; cierre sólo priority_queue.encolar.instructions. Mapa vigente audit-pila-colas-pending-map-after-priority-enqueue-finite-low.md; siguiente baseline Cola Desencolar sólo propuesto, no ejecutado. Sin sumar contadores ni ampliar cierres.


## Cola Desencolar baseline LOW 2026-10-03

Ver queue-desencolar-baseline-checkpoint-low.md y evidence/visible-queue-desencolar-baseline-low:42IDs10pass32fail0xfail,C87events19conditions. Baseline terminado; instrucción funcional abierta por identidad/num/heap/types/guard/console/raíces/scopes ypreparedreload. Caller real4C17/Dox/7balanced correcto. MEDIUM sólo propuesto en queue-desencolar-instructions-plan-medium-proposed.md. Sin cambiarC_H/producto/cierres ni contador global.


## Cola Desencolar MEDIUM: checkpoint finito 2026-10-03

Ver queue-desencolar-instructions-checkpoint-medium.md y evidence/visible-queue-desencolar-instructions-medium:46pass(42original+4session),87Cevents19conditions reutilizados iguales, UI4reloadSiguiente142/126,caller4C17/Dox/7balanced intacto. MEDIUM terminado; revisión/consolidación LOW pendiente, no cierre universal. Preservar baseline42IDs10pass32fail y13obs históricos parciales. Sin contador global ni Graph/SDDblocked/publicación.


## Cola Desencolar: cierre finito LOW 2026-10-03

Ver queue-desencolar-finite-closure-decision-low.md y evidence/visible-queue-desencolar-finite-consolidation-low:46IDs reutilizados con230productSHA/6QA,87Cevents19conditions y4reloadNext verificados, sin nuevaejecuciónC. Sólo operación registrada cerrada; mapa audit-pila-colas-pending-map-after-queue-dequeue-finite-low.md. Siguiente PrioridadDesencolar baselineLOW sólo propuesto con recuperaciónprevia/docs-onlyC_Hdiff; no ejecutado ni asignado. Preservar cierres yrestricciones, no contador global.


## Priority queue desencolar baseline LOW completed

2026-10-03: baseline únicamente;51 IDs29pass22fail,5 divergencias privadas,4main C17 fallidos,4preparedreload fallidos. Sin producto modificado ni cierre funcional. Evidencia visible-priority-queue-desencolar-baseline-low/README.md; MEDIUM propuesto priority-queue-desencolar-instructions-plan-medium-proposed.md requiere coordinación nueva. Cierres anteriores conservados.


## Priority queue desencolar MEDIUM implementation checkpoint

2026-10-03: implementación scoped verificada56IDs51originales+5privados sinxfail;198nativeobs/74conditions iguales,4reload/Siguiente real,4mainsC17/Doxygen0warnings/ownership12/12/0 y12NULLsetup. Baseline fallida conservada; consolidaciónLOW pendiente, no cierre funcional/global. Ver priority-queue-desencolar-implementation-checkpoint-medium.md y evidence/visible-priority-queue-desencolar-instructions-medium/README.md. C/H y226archivos anteriores protegidos;4existentes autorizados modificados.


## Priority queue desencolar finite cases verified LOW closure

2026-10-03: sólo priority_queue.desencolar.instructions casos registrados cerrado;56IDs51original+5private/198nativeobs74conditions/4reloadNext/4mainsC17/12allocfree0live12NULLDox0 reutilizados con76SHAcurrent. LOW sin producto modificado ni reruns. Ver priority-queue-desencolar-finite-closure-decision-low.md y mapa audit-pila-colas-pending-map-after-priority-dequeue-finite-low.md; próxima Frente oculta registrada sólo propuesta, CimaPila/FrenteFinalCola no registradas. Sin cierre familiar/global ni contadores.


## Priority queue Frente LOW baseline complete; bounded MEDIUM pending

2026-10-03: Frente registradooculto baseline64IDs29pass35fail;178historicevents/93currentobs39conditions iguales,7newnative49events11conditions/6setupbalanced y4privateguardfail.4UIexisting/8query readonly,0journal/callermainquery;4C17setup-only/9balanced/9NULL/Dox0. Producto233SHAigual. Scopeconst/output/aliases/return yhistorialcaller pendientes, nofeatureexposure ni functionalclosure. Mapa11publicmethods pending de20exports concriterio explícito; MEDIUMpropuesto, cierres anteriores intactos. Ver priority-queue-front-baseline-checkpoint-low.md ymapafter-priority-front-baseline-low.


## Priority queue Frente MEDIUM implementation checkpoint; LOW pending

2026-10-03:64originalIDs64pass0xfail/baseline29pass35fail conservado;93nativeobs39conditions current0divs,private7gapraw+engine/queryGETnodispatch.4UIcontexts8journal/callerqueries,hiddenselector intacto/noFrontplayback;4C17mains9allocfree0live9NULLDox0.229/233producto protegido,4existingallowed +engine/guide nuevos;C_H/nine-mutant-closures intactos. Mapa11pending siguehastaLOW, nofamily/globalclosure. Ver priority-queue-front-implementation-checkpoint-medium.md.


## Priority queue Frente finite functional closure LOW

64originalIDs/93obs39conditions/4C17mains9balanced9NULLDox0 reutilizados con125SHAcurrent;229protected/4authorized/2new. HiddenAPIquery journal sinmutationTAD, GETnoqueryredispatch; UIFrente noexpuesta/noplayerclosure. Sólo casos finitoscp_frente cerrado; mapa10pendingde20exports. LOWproducto0/rerun0. Verpriority-queue-front-finite-closure-decision-low.md; siguiente PilaCima baseline sólo propuesto.


## Stack Cima LOW baseline complete; bounded MEDIUM pending

73IDs25pass48fail0xfail,6gapcategories/8fixtures.16newnativecalls48events16conditions; publicunregistered400querydispatch0POSTGET/0journal butfakecallframesopen.4UIcontexts8rejects/3DOM+4HTTPmainsC17/7setupbalanced7NULLDox0.376productSHAunchanged;10publicmethodspending. NoUIfeatureexposure/closedrepeats. Verstack-cima-baseline-checkpoint-low.md yMEDIUMproposed; nofunctionalclosure.


## Stack Cima MEDIUM implementation verified; LOW pending

73sameIDs73pass/baseline25/48conservado;16privatequeries48events16conditions current0divs nativeexactreuse;validation400steps0/queryPOSTGETexec0/nojournalAPIUIunregisteredunchanged.4browsercontexts8rejects/3DOM+4HTTPmains6inputsSHAreuse4C17/7balanced7NULLDox0.372/376protected4authorized+newengine1,priorclosuresintact. Map10pending remains,nofunctionalclosure. Verstack-cima-implementation-checkpoint-medium.md.


## Stack Cima finite private core closure LOW

Sólo pila_cima núcleoC/Python/adapter/trazaprivada casos finitos cerrado;publicAPIUIexcluded/unregisteredunchanged.73IDs/16queries48events16conditions/400zeroCsteps/0queryPOSTGETdispatch/0journal y6inputsCcaller byteigual reutilizados120SHAcurrent;LOW0productchanges/0reruns. Map9corependingde20exports, nofamily/globalclosure. Verstack-cima-finite-private-closure-decision-low.md ymapafter-stack-cima-finite-low. Siguientequeue-front-final-baseline-plan-low-proposed.md sólo propuesta con2métodos/IDs independientes.


## Queue Front Final LOW baseline complete; independent MEDIUM pending

160IDs59pass101fail0xfail;Frente78IDs33/45,Final78IDs22/56+4shared4pass.Each22nativequerycalls66events22conditions/readonlyCbyvalue;rawFront11casesmatch/rawFinalmissing/typedguardaliasesreturnscopeandrejectedfakecallsopenboth.4browsercontexts16rejects0acceptedrecords/3realDOMsetupC17/8balanced8NULLDox0;377productSHAunchanged.9pending remains,nofunctionalclosure/nofeatureexposure. Verqueue-front-final-baseline-checkpoint-low.md yboundedMEDIUMplanproposed.


## Cola Frente/Final MEDIUM verificado; consolidación LOW pendiente

164pass =160originales+4privatepartialrootIDs;80Frente+80Final+4shared overlap0. 44consultas/132eventos/44condiciones comparados con C conservado. Validación400zeroCsteps;queriesunregistered/UIexcluida,3DOMcallers inputsbyteexactos C17/ownership8/8/0NULL8Dox0reuse. Mapa9sin cierre funcional. Véase queue-front-final-implementation-checkpoint-medium.md y evidence/visible-queue-front-final-instructions-medium/verification-summary.json.


## Cola Frente/Final finite private core LOW closures

Cierre independientequeue.frente.instructions yqueue.final.instructions sólocoreprivado finito,API/UIacceptedqueryexcluida.120manifest/378product/5callerinputsactuales iguales;164IDs80Frente80Final4shared overlap0 preserved;44queries132events44conditions0div,no reruns/productchangesLOW. Mapa9→7 segúnexports20/covered13/pending7: pila_mostrar,cola_mostrar,cp_inicializar,cp_vacia,cp_contar,cp_copiar_items,cp_formatear. SiguienteLOWpropuestoMostrarPila/Cola requiere nueva instrucción;no ejecución. Véase queue-front-final-consolidation-checkpoint-low.md ydecisionesindependientesqueue-frente/queue-final-finite-private-closure-decision-low.md.


## Mostrar Pila/Cola LOW baseline; private instruction review open

160IDs50pass110fail: Pila76(22/54),Cola80(24/56),4sharedpassoverlap0.40Ccalls432events126conds,rawconsole0/20equal readonly20/20;privategeneric source unavailable/loopprintfscope gaps andunsupported1invariantframemissingvalidation.8browsercontexts16reject400readonly,7C17callers/11inputs exactprepared reusePila7/7/0NULL7/Cola8/8/0NULL8Dox0.378productprotectednochanges/map7. See stack-queue-show-baseline-checkpoint-low.md andscopedMEDIUMproposedplan;not functionalclosure. GraphweightsintDijkstraCconfirmed,remainingBFrepresentation/cycleerrorseparate;RNownerhandoffdone,ASanUBSan/session-state/C1global stillpending.


## Grafos pesos enteros/Dijkstra C: decisión aprobada registrada LOW

Usuario confirmóenterosrepresentables/reglasCactualesDijkstra. Delta2req10scenarios ynotas2guíasactualizados,0runtime/C_Hedits;no technicalclosure/canonicalconsolidationunverified. Decision/checkpoint graph-approved-integer-dijkstra-contract-*-low.md. BaselinesPrim/Kruskalactuales recuperados,noprepeat. Restan decisionesBFlímitesdetección/cycleHTTP yPrimnegativosINTMAXdomain;empatesCconservador,no cambioAPIundirected. MostrarplanMEDIUM listo/map7;RNdocumentalownerhandoffclosed;ASanUBSan/session-statecanónica/C1global/agregadofinalpendientes.


## Mostrar Pila/Cola MEDIUM verificado; LOW pendiente

162pass=160originales+2privateCola,76Pila82Cola4sharedoverlap0,baseline50/110conservado. Consola20/20rawexactC y432eventos126condiciones40queriesreused0div;voidtypedaux/printf/scopesreadonly. API36reject400steps[]/0targetjournal;browser8contexts16rejectfive sections0extraPOST/JSerrors.7C17callers/11inputsbyteexact ownershipPila7/7/0NULL7Cola8/8/0NULL8Dox0reuse.373protected/5authorizedexisting+engine1,C_H/Graph/RN/UIwrapperintact. Map7sin functionalclosure. Véase stack-queue-show-implementation-checkpoint-medium.md ygraph-extremes-proposal.md propios.


## Mostrar Pila/Cola finite private cores LOW closed

stack.mostrar.instructions yqueue.mostrar.instructions cierres privados independientes.211manifest/379product/11callerinputsverified;162IDs432events126conditions0divreused,no reruns/productwrites. APIUIacceptedMostrar/playerexcluidos. Mapa7→5derivado20exports15finitecovered,pendientescp_inicializar/cp_vacia/cp_contar/cp_copiar_items/cp_formatear. Nueva instrucción autoriza su baselineLOW sinfixes/exposure/C_H. Véase stack-queue-show-consolidation-checkpoint-low.md ydecisionesindependientes.


## Priority five helpers LOW independent baseline (2026-10-04)

[Checkpoint](priority-queue-five-helpers-baseline-checkpoint-low.md):148unique IDs86pass62fail, C17/Doxygenactual; protected379unchanged. This is baselineonly, no helper closure or globalcountupdate;instructionfidelity open. Next coordination: [bounded MEDIUM proposal](priority-queue-five-helpers-instructions-plan-medium-proposed.md). Preserve Mostrar separateprivateclosures, pending fivehelpermap, preview5051,Graphdecision exclusion.


## Five Priority helpers MEDIUM verified (2026-10-04)

[Checkpoint](priority-queue-five-helpers-implementation-checkpoint-medium.md):326unique IDs,148originalunchanged;baseline86/62preserved,final326pass5.83s. Native148samefixtures2147events575conditions0divergence,APIUIhelpersnotregistered40isolated/40browserrejects400zeroCsteps,379→380product4allowededits1newengineC/Hunchanged. Per-method IDs13/25/25/111/147 +5shared. LOWper-methodclosurepending, map5notchanged. NewexplicitGraphapprovalaftercheckpoint preserved separately; no Graphedit underthisassignment. No globalcounter/fullsuite/archive.


## Five Priority helpers finite private LOW closures (2026-10-04)

Cinco cierres independientes cp_inicializar/vacia/contar/copiar_items/formatear sólocasosprivadosregistrados; [checkpoint](priority-queue-five-helpers-consolidation-checkpoint-low.md).326IDsúnicos unión326/326(no652),148baseline86/62preservado,2147eventos575condiciones0div;461manifest380product53baseline verified. LOW0producto/reruns/Graphedits. Mapa5→0sólosubgrupo20exportsfinito/comunicado,no cierreTAD/app/global;APIUIhelpersnoexpuestas. PróximoMEDIUMGraph específicamente aprobado, nuevaasignación antesactivar; pendientesglobales enaudit-next-sequence-after-priority-helpers-low.md. Hash11/Sorting11/RNfullvalidator ycierresanterioresintactos; no incrementoglobal/docs/C1.


## Graph: aceptación QA finita y consolidación documental LOW (2026-10-04)

[Addendum vigente](graph-qa-documentary-consolidation-addendum-low.md) corrige métricas del autor a tiempo transcurrido y precisión poolshared/records congelados; integra30148mutacionesChromiumQA, sin borrar bloqueo standalone histórico. QA real46IDs/seisfixturescríticos/before-verify-after0 acepta los tresajustes en casosregistrados. [Criterios poralgoritmo](graph-finite-acceptance-criteria-low.md) conserva BFS/DFS previos y acepta criterios finitos Bellman-Ford/Dijkstra/Prim/Kruskal; no6métodos→casilla global. Todas22casillas preservadas:13marcadas/9abiertas porcriterios agregados, ledger121/208histórico y87pendientes sin cambios;38GraphSHAstale y helperprivadonuevo no inventariado. [Preparación documental](documentary-stable-sources-after-graph-qa-plan-low.md) reutiliza67readreviewsSDD/hashesnongraphactuales. Sólo dosguías modificadas, runtime/C/H/preview/evidencia original y QAintactos; no reruns. Siguiente lote documental con bindingvigente y cualquier excepción C/H específica antes deeditar, sin ampliaralgoritmos.


## Delta documental de fuentes 2026-10-04

Ver `documentary-source-reconciliation-checkpoint-low.md`: Graph38 reconciliados + helper privado; 67 lecturas ordenadas; RN19 requieren recuperar binding. Cero signoffs/casillas nuevos; 13/22 preservado. Producto/C/H congelados.


## Recuperación documental de vínculos 2026-10-04

Ver `documentary-binding-recovery-checkpoint-low.md`: RN19 vinculado a QA/handoff vigente; Graph18 fuentes históricas recuperadas (15 cuerpos iguales/3 sustituidos); Desapilar hash entre informes históricos ligado, bytes íntegros aún no recuperados; rama Heap remove existe pero no en CHECKS estándar. 13/22, cero signoffs automáticos.


## Hitos documentales C/H autorizados 2026-10-04

Ver `documentary-comments-families-checkpoint-low.md` y ledger materializado vigente enlazado desde documentation-symbol-signoff-ledger.md: 67 contratos/117comentarios C/H revisados; 211 símbolos/386declaraciones reales; 118endorsements históricos ligados, 26registros sin endorsement individual global. Sólo14C/H modificados, tokens/preprocesado/13objetos idénticos, 26HTTP exactos y Doxygen0warnings. RN19/Graph15 vínculos preservados; Desapilar bytes nativos históricos aún no recuperados; Heap reporte específico no localizado. 13/22 sin casillas nuevas, sin suites históricas repetidas/preview/Git.


## Parcial26 documental y evidencia focal 2026-10-04

Ver `documentary26-partial-checkpoint-low.md`:25suficientes/1formalRN pendiente; DesapilarbytesSHA exactos recuperados y tokens iguales a D; Heap20nativos pasan, todos0vivos,13harnesses sólo enlazados. No casilla amplia nueva ni repetición por consulta.


## Contratos26 y evidencia focal completos 2026-10-04

Ver [checkpoint propio](documentary26-stack-heap-evidence-checkpoint-low.md):26contratos documentales aceptados, fuente histórica Desapilar recuperada SHA exacto y ligada al código actual;20regresiones nativas Heap nuevas pasan/cleanup0, sin repetirlas por consulta.26descargas reales/13harness enlazados sin ejecutar/Doxygen colectivo y autónomo0; código ejecutable intacto en las3fuentes de comentarios cambiadas. Catálogo211funciones/386declaraciones; evidencia histórica preservada. Nueve criterios amplios revisados y abiertos por sus residuales explícitos;13/22sin cambios, sin cierre funcional universal ni reapertura de familias.


## Miembros nofunción y criterio13 aceptado 2026-10-04

[Checkpoint vigente](documentary-nonfunction-global-criteria-checkpoint-low.md) y [decisión criterio13](documentary-c-h-criterion13-acceptance-decision-low.md).34declaraciones iniciales/tipos/campos/enums y fuente completa revisados; sólo8C/Hcomentarios, tokens/preprocesado/5objetosidénticos, HTTP/compilación/Doxygen reales y bindings actuales. Se marca exclusivamente fila13 de descargasC/H/compilación/Doxygen/exactitud;14/22derivado, ocho criterios abiertos con pendientes/condiciones precisos. No suites/algoritmosnuevos, no repetir26/67/Heap20/Desapilar. Bloqueos antiguos H1/Graph/RN/Sorting y faltantesdocumentales quedan sustituidos por fuentes vigentes, no por esta fotografía histórica. Preview/Git/owners intactos.
