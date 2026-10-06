#ifndef TAD_GRAFO_H
#define TAD_GRAFO_H

/**
 * @file tad_grafo.h
 * @brief TAD Grafo dirigido ponderado implementado con listas enlazadas.
 */

/** @brief Nodo de vertice. */
typedef struct NodoV {
    int dato; /**< Identificador del vértice. */
    struct NodoV* sig; /**< Siguiente nodo de la lista; NULL al terminar. */
    int marcado; /**< Marca de visita de recorridos. */
} *ListaVertice; /**< Alias de puntero a nodo o cabeza de vertices; NULL es lista vacia. */

/** @brief Nodo de arco. */
typedef struct NodoA {
    int origen; /**< Identificador del origen del arco. */
    int destino; /**< Identificador del destino del arco. */
    int costo; /**< Peso entero del arco. */
    struct NodoA* sig; /**< Siguiente nodo de la lista; NULL al terminar. */
    } *ListaArco; /**< Alias de puntero a nodo o cabeza de arcos; NULL es lista vacia. */

/**
 * @brief Par de cabezas de listas de vertices y arcos, recibido por valor.
 * @note Copiar Grafo comparte nodos; no reserva, libera ni crea un propietario
 * independiente. v y a son listas vivas aciclicas o NULL bajo sus contratos.
 * El tipo no contiene bandera de direccion ni comprueba extremos de los arcos;
 * eliminar un vertice no elimina automaticamente sus arcos incidentes.
 */
typedef struct nodoGrafo {
    ListaVertice v; /**< Lista de vértices. */
    ListaArco a; /**< Lista de arcos. */
} Grafo;

/**
 * @brief Union-Find sobre indices 0..n-1, no sobre identificadores de vertices.
 * @note Con n positivo, padre dispone de n ints vivos y escribibles; cada
 * padre[i] pertenece a 0..n-1 y las cadenas terminan en una raiz padre[r]==r.
 * encontrar comprime caminos; unir modifica el arreglo. La estructura no
 * reserva ni libera por si sola: el caller administra el arreglo y sus aliases.
 */
typedef struct Conjunto {
    int *padre; /**< Arreglo propio o prestado de n indices padre; no punteros a nodos. */
    int n; /**< Número de elementos del arreglo padre. */
} Conjunto;

/**
 * @brief Crea un grafo vacío.
 * @return Grafo - Un grafo vacío.
 */
Grafo grafo_crear(void);
/**
 * @brief Reserva un vertice al inicio si el identificador no existe.
 * @param[in,out] g Grafo inicializado por valor con lista propia de vertices.
 * @param[in] x Identificador int, incluidos negativos y extremos.
 * @return Grafo con nueva cabeza, o g sin cambios ante duplicado o fallo malloc.
 * @pre Lista propia viva y aciclica o NULL.
 * @note Nuevo nodo tiene marcado=0 y pertenece al grafo; caller administra su liberacion. Retorno no comunica causa de fallo y no hay diagnostico.
 * @note Para publicar una nueva cabeza el caller asigna el retorno; no copia los nodos anteriores ni modifica arcos.
 */
Grafo grafo_insertar_vertice(Grafo g, int x);
/**
 * @brief Intenta crear extremos y actualiza o reserva un arco dirigido.
 * @param[in,out] g Grafo inicializado por valor con listas propias vivas y aciclicas.
 * @param[in] x Identificador origen int.
 * @param[in] y Identificador destino int.
 * @param[in] z Costo int, admite negativos y extremos.
 * @return Grafo resultante, posiblemente parcial si alguna reserva falla.
 * @note Llama primero insertar_vertice(x) e insertar_vertice(y). Si el arco ya existe, actualiza el costo del primer coincidente sin reservar otro arco.
 * @note Si no existe, reserva y prepend un NodoA. Fallo malloc conserva vertices ya creados; no rollback ni estado de error separado. Fallo al crear extremos no impide intentar reservar el arco, por lo que no garantiza extremos presentes.
 * @note Caller asigna retorno y administra nodos propios; actualizar un arco compartido se observa por aliases. No crea automaticamente el sentido inverso.
 */
Grafo grafo_insertar_arco(Grafo g, int x, int y, int z);
/**
 * @brief Imprime la lista de vértices del grafo
 * @param g Grafo del cual se imprimirán los vértices
 */
void grafo_imprimir_vertices(Grafo g);
/**
 * @brief Imprime la lista de arcos del grafo
 * @param g Grafo del cual se imprimirán los arcos
*/
void grafo_imprimir_arcos(Grafo g);
/**
 * @brief Devuelve la cabeza compartida de vertices sin copiar nodos.
 * @param[in] g Grafo inicializado por valor.
 * @return g.v tal cual, incluida NULL para lista vacia.
 * @note Referencia prestada: no reserva, libera ni transfiere nueva propiedad. Escribir por el alias modifica los nodos originales; liberar nodos requiere coordinar al propietario, no tratar el resultado como copia independiente.
 */
ListaVertice grafo_vertices(Grafo g);
/**
 * @brief Devuelve la cabeza compartida de arcos sin copiar nodos.
 * @param[in] g Grafo inicializado por valor.
 * @return g.a tal cual, incluida NULL para lista vacia.
 * @note Referencia prestada: no reserva, libera ni transfiere nueva propiedad. Escribir por el alias modifica los nodos originales; liberar nodos requiere coordinar al propietario, no tratar el resultado como copia independiente.
 */
ListaArco grafo_arcos(Grafo g);
/**
 * @brief Sustituye la cabeza de vertices en la copia por valor.
 * @param[in] g Grafo inicializado por valor.
 * @param[in] k Nueva cabeza prestada; NULL admitido.
 * @return Grafo con v=k y la otra cabeza conservada.
 * @note No copia, reserva, libera ni valida nodos. El caller debe usar el retorno para cambiar su cabeza; los demas aliases conservan las referencias anteriores.
 * @note No libera la lista sustituida ni define ownership nuevo: el caller administra las reservas y conserva la referencia anterior si necesita liberarla.
 */
Grafo grafo_cambiar_vertices(Grafo g, ListaVertice k);
/**
 * @brief Sustituye la cabeza de arcos en la copia por valor.
 * @param[in] g Grafo inicializado por valor.
 * @param[in] k Nueva cabeza prestada; NULL admitido.
 * @return Grafo con a=k y la otra cabeza conservada.
 * @note No copia, reserva, libera ni valida nodos. El caller debe usar el retorno para cambiar su cabeza; los demas aliases conservan las referencias anteriores.
 * @note No libera la lista sustituida ni define ownership nuevo: el caller administra las reservas y conserva la referencia anterior si necesita liberarla.
 */
Grafo grafo_cambiar_arcos(Grafo g, ListaArco k);
/**
 * @brief Consulta exclusivamente si la cabeza de vertices es NULL.
 * @param[in] g Grafo inicializado por valor.
 * @return 1 si g.v==NULL, 0 en otro caso.
 * @note No inspecciona g.a: puede devolver 1 aunque haya arcos almacenados. No recorre, reserva, libera ni modifica nodos.
 */
int grafo_vacio(Grafo g);
/**
 * @brief Verifica si el vértice existe en el grafo
 * @param g Grafo del cual se verificará la existencia del vértice
 * @param x Vértice a buscar
 * @return int - 1 si el vértice existe, 0 en caso contrario
*/
int grafo_existe_vertice(Grafo g, int x);
/**
 * @brief Verifica si el arco existe en el grafo
 * @param g Grafo del cual se verificará la existencia del arco
 * @param x Vértice origen
 * @param y Vértice destino
 * @return int - 1 si el arco existe, 0 en caso contrario
*/
int grafo_existe_arco(Grafo g, int x, int y);
/**
 * @brief Desenlaza y libera el primer vertice coincidente; conserva los arcos.
 * @param[in,out] g Grafo por valor con lista propia de vertices.
 * @param[in] x Identificador int a buscar.
 * @return Grafo con cabeza actualizada; vacio o ausencia no cambian nodos.
 * @pre Lista propia viva y aciclica; nodos liberables sin ownership compartido.
 * @note No elimina arcos incidentes: sus identificadores pueden quedar sin vertice asociado. No reserva ni imprime.
 * @note Caller asigna retorno para cambiar cabeza; aliases al nodo liberado quedan indeterminados y no deben leerse ni usarse. Los demas nodos se comparten, no se copian.
 */
Grafo grafo_eliminar_vertice(Grafo g, int x);
/**
 * @brief Desenlaza y libera el primer arco con origen y destino coincidentes.
 * @param[in,out] g Grafo por valor con lista propia de arcos.
 * @param[in] x Identificador origen.
 * @param[in] y Identificador destino.
 * @return Grafo con cabeza de arcos actualizada; ausencia conserva el grafo.
 * @pre Lista propia viva y aciclica; reservas liberables sin ownership compartido.
 * @note No borra vertices ni arco de sentido inverso. No reserva; imprime diagnostico solo si elimina un nodo posterior a la cabeza.
 * @note Caller asigna retorno para nueva cabeza; aliases al nodo liberado quedan indeterminados y no se deben leer ni usar.
 */
Grafo grafo_eliminar_arco(Grafo g, int x, int y);
/**
 * @brief Retorna el costo del arco que parte del vértice x al vértice y del grafo
 * @param g Grafo del cual se retornará el costo del arco
 * @param x Vértice origen
 * @param y Vértice destino
 * @return Costo del arco, o -1 si no existe; un arco válido también puede tener costo -1.
 * @note Para distinguir ausencia de costo -1, consultar grafo_existe_arco.
*/
int grafo_costo_arco(Grafo g, int x, int y);
/**
 * @brief Cuenta nodos almacenados de vertices.
 * @param[in] g Grafo inicializado por valor con lista prestada.
 * @return Numero de nodos de g.v; 0 si la cabeza es NULL.
 * @pre Lista viva, aciclica y con numero de nodos <= INT_MAX.
 * @note No valida identificadores, consistencia de extremos ni unicidad; no reserva/libera/imprime ni modifica. No certifica contadores fuera del rango int.
 */
int grafo_orden(Grafo g);
/**
 * @brief Cuenta nodos almacenados de arcos.
 * @param[in] g Grafo inicializado por valor con lista prestada.
 * @return Numero de nodos de g.a; 0 si la cabeza es NULL.
 * @pre Lista viva, aciclica y con numero de nodos <= INT_MAX.
 * @note No valida identificadores, consistencia de extremos ni unicidad; no reserva/libera/imprime ni modifica. No certifica contadores fuera del rango int.
 */
int grafo_tamano(Grafo g);
/**
 * @brief Cuenta arcos almacenados cuyo origen es x (grado de salida).
 * @param[in] g Grafo inicializado por valor con lista de arcos prestada.
 * @param[in] x Identificador origen a contar.
 * @return Numero de coincidencias de origen, 0 si no hay; no exige que exista vertice x.
 * @pre Lista de arcos viva y aciclica; contador resultante <= INT_MAX.
 * @note No cuenta entradas; un bucle con origen x aporta uno. No valida simetria/direccion ni reserva/libera/imprime/modifica.
 */
int grafo_grado_vertice(Grafo g, int x);
/**
 * @brief Escribe cero en la marca del primer vertice cuyo dato coincide.
 * @param[in,out] g Copia por valor con nodos de vertices compartidos modificables.
 * @param[in] x Identificador int buscado, incluidos negativos.
 * @return La misma pareja de cabezas; ausencia conserva todas las marcas.
 * @pre Lista de vertices viva y aciclica o NULL.
 * @note No reserva/libera ni imprime. La escritura es visible por aliases a nodos aunque el caller no asigne el retorno; no cambia arcos.
 */
Grafo grafo_desmarcar_vertice(Grafo g, int x);
/**
 * @brief Pone a cero las marcas de todos los nodos de vertices compartidos.
 * @param[in,out] g Copia por valor del grafo; listas validas o NULL.
 * @return La misma pareja de cabezas; no reserva ni libera nodos.
 * @note Copiar Grafo no copia sus nodos: las escrituras se observan en los aliases.
 */
Grafo grafo_desmarcar(Grafo g);
/**
 * @brief Escribe 1 en la marca del primer vertice cuyo dato es x.
 * @param[in,out] g Grafo por valor con nodos prestados validos.
 * @param x Identificador entero, incluidos negativos y -1.
 * @return La misma pareja de cabezas; si x no existe no cambia nodos.
 * @note No reserva ni libera memoria; el grafo vacio es valido.
 */
Grafo grafo_marcar_vertice(Grafo g, int x);
/**
 * @brief Consulta la marca almacenada del primer vertice coincidente.
 * @param g Grafo prestado por valor; listas validas o NULL.
 * @param x Identificador entero buscado.
 * @return Valor int de marcado, o 0 si x no existe; no normaliza otro valor a 1.
 * @note No modifica nodos ni transfiere propiedad.
 */
int grafo_marcado_vertice(Grafo g, int x);
/**
 * @brief Reserva una lista independiente de destinos de arcos cuyo origen es x.
 * @param g Grafo prestado por valor; lista de arcos valida o NULL.
 * @param x Identificador entero de origen; no exige que exista un vertice x.
 * @return Lista nueva, o NULL sin coincidencias/reservas; el caller libera cada nodo.
 * @note Ante fallo malloc omite ese destino y sigue; puede retornar lista parcial.
 * @note Prepend invierte el orden de recorrido de la lista de arcos; marcado es 0.
 * @note No modifica marcas ni enlaces del grafo original y no imprime salida.
 */
ListaVertice grafo_sucesores(Grafo g, int x);
/**
 * @brief Reserva una lista independiente de origenes de arcos cuyo destino es x.
 * @param[in] g Grafo inicializado por valor con arcos prestados.
 * @param[in] x Identificador destino; no exige vertice x presente.
 * @return Lista nueva propia, o NULL sin coincidencias/reservas; caller libera cada nodo.
 * @pre Lista de arcos viva y aciclica o NULL.
 * @note Cada nodo nuevo tiene marcado=0. Prepend invierte el orden del barrido de arcos; puede repetir origenes. No modifica grafo ni libera sus nodos.
 * @note Fallo malloc omite ese origen y continua: puede devolver lista parcial sin flag de error. Imprime predecesor solo para cada nodo cuya reserva tuvo exito.
 */
ListaVertice grafo_predecesores(Grafo g, int x);
/**
 * @brief Recorre desde inicio con FIFO y publica una lista nueva en orden BFS.
 * @param[in,out] g Grafo por valor con nodos prestados validos; comparte sus marcas.
 * @param inicio Identificador entero inicial, incluidos negativos y -1.
 * @return Lista nueva de vertices procesados; NULL si inicio no existe o no obtiene nodos.
 * @note Desmarca primero, incluso si inicio falta; luego marca al intentar encolar.
 * @note El caller libera todos los nodos del resultado; sus marcas propias son 0.
 * @note Cola y listas de sucesores son temporales y se liberan durante la ruta normal.
 * @note Fallos de reserva pueden omitir vertices o dar resultado parcial/NULL. Si
 *       cola_encolar falla, BFS puede marcar un vertice que no sera procesado.
 * @note La guarda de cola no vacia permite extraer -1 como dato valido, no como error.
 * @note Ignora costos: minimiza cantidad de arcos, no peso. Este TAD barre listas de
 *       vertices/arcos repetidamente: cota O(V*(V+E)), no O(V+E) de una implementacion
 *       con adyacencia directa y consulta de marcas constante.
 */
ListaVertice grafo_bfs(Grafo g, int inicio);
/**
 * @brief Marca un vértice y agrega su recorrido en profundidad.
 * @param g Grafo cuyos nodos de vértice se marcan.
 * @param actual Vértice actual, que debe pertenecer al grafo.
 * @param recorrido Dirección de una lista de recorrido; NULL se ignora.
 * @note Comparte los nodos y marcas de g y la cabeza referenciada por recorrido.
 * No desmarca ni comprueba que actual estuviera sin visitar: el wrapper y la
 * prueba de marcas de cada sucesor establecen ese contrato. Marca antes de
 * reservar el nodo de resultado, cuyo marcado es 0. Cada frame libera su lista
 * temporal de sucesores, no los nodos del grafo ni el resultado del caller.
 * Un fallo de reserva puede dejar marcas y resultado parciales. Recorrido NULL
 * retorna antes de marcar. Profundidad de recursion acotada por vertices alcanzables.
 */
void grafo_dfs_recursivo(Grafo g, int actual, ListaVertice *recorrido);
/**
 * @brief Desmarca el grafo y recorre desde inicio en profundidad.
 * @param g Grafo cuyos nodos se marcan durante el recorrido.
 * @param inicio Identificador del vértice inicial.
 * @return Lista nueva de vértices visitados, o NULL si inicio no existe o no se reservan nodos.
 * @note Comprueba inicio antes de desmarcar: si falta, conserva las marcas previas.
 * Identificadores negativos, incluido -1, son datos validos. Con inicio valido,
 * desmarca todos los vertices y marca los alcanzables al entrar en recursion.
 * El resultado usa nodos nuevos con marcado=0; el caller libera cada nodo.
 * No libera vertices prestados del grafo ni modifica arcos. El orden depende
 * de la lista de arcos, no de ordenar identificadores. Una reserva fallida
 * puede dejar marcas y resultado parciales; NULL no identifica por si solo la causa.
 * El TAD real barre listas: cota O(V*(V+E)), frente al modelo ideal O(V+E).
 */
ListaVertice grafo_dfs(Grafo g, int inicio);
/**
 * @brief Calcula un camino mínimo con pesos no negativos.
 * @param g Grafo dirigido ponderado.
 * @param inicio Vértice inicial.
 * @param llegada Vértice destino.
 * @return Lista nueva de arcos del camino; NULL si no hay arcos de resultado, hay pesos negativos, vértices inválidos o error de memoria.
 * @note NULL también representa el camino sin arcos de un vértice a sí mismo. El llamador libera el resultado.
 * @note INT_MAX es infinito: no se publica un camino con costo total mayor o igual a INT_MAX. Las sumas que excederían INT_MAX se descartan antes de sumar.
 * @note Los empates eligen el primer índice con distancia mínima en el orden de la lista de vértices; una distancia igual no reemplaza el predecesor.
 * @note Se rechaza cualquier peso negativo del grafo, incluso en componentes no alcanzables. No se modifican sus marcas.
 */
ListaArco grafo_dijkstra(Grafo g, int inicio, int llegada);
/**
 * @brief Calcula un camino mínimo admitiendo pesos negativos.
 * @param g Grafo dirigido ponderado.
 * @param inicio Vértice inicial.
 * @param llegada Vértice destino.
 * @return Lista nueva de arcos del camino; NULL si no hay arcos de resultado, vértices inválidos, ciclo negativo alcanzable o error de memoria.
 * @note El llamador libera el resultado. La detección de ciclo negativo escribe una advertencia en stdout.
 * @note Las distancias internas son long long con alcanzabilidad separada: INT_MAX es un costo válido.
 * @note La suma se comprueba antes de ejecutarse. Una caminata inferior a (n-1)*INT_MIN demuestra un ciclo negativo y evita descenso ilimitado.
 * @note Un límite interno no representable produce diagnóstico explícito y NULL; no se descartan ni saturan candidatas.
 * @note Un inicio igual a llegada sin arcos de resultado también retorna NULL. Se validan ambos índices antes de relajar.
 */
ListaArco grafo_bellman_ford(Grafo g, int inicio, int llegada);
/**
 * @brief Construye el bosque con la selección de Prim sobre los arcos disponibles.
 * @param g Grafo; para la interpretación no dirigida se requieren arcos simétricos.
 * @param inicio Vértice desde el que comienza la selección.
 * @return Lista nueva de arcos seleccionados o NULL si el bosque no tiene arcos, inicio no existe o falla memoria.
 * @note Admite todos los costos int, incluidos INT_MIN e INT_MAX, con presencia de candidato separada.
 * @note Reinicia la selección en componentes desconectadas. El llamador libera el resultado.
 * @note Los empates de extracción conservan el primer índice mínimo de la lista de vértices y la mejora de padre es estricta.
 * @note El grafo y sus marcas se conservan. La API rechaza dirigidos, pero este C no tiene bandera de dirección ni comprueba simetría.
 */
ListaArco grafo_prim(Grafo g, int inicio);
/**
 * @brief Busca la raíz de Union-Find y comprime el camino.
 * @param c Conjunto con arreglo padre válido y sin ciclos.
 * @param x Índice del elemento.
 * @return Índice de raíz o -1 ante puntero NULL o índice fuera de rango.
 */
int grafo_encontrar_conjunto(Conjunto *c, int x);
/**
 * @brief Enlaza la raíz de y a la raíz de x si ambas son válidas.
 * @param c Conjunto Union-Find que se modifica.
 * @param x Índice del primer elemento.
 * @param y Índice del segundo elemento.
 */
void grafo_unir_conjuntos(Conjunto *c, int x, int y);
/**
 * @brief Selecciona arcos por costo evitando ciclos mediante Union-Find.
 * @param g Grafo cuyos arcos se consideran como conexiones para la selección.
 * @return Lista nueva del bosque seleccionado; NULL si no hay arcos de resultado o falla memoria.
 * @note El llamador libera los nodos del resultado; no se modifica la lista de arcos del grafo.
 * @note Admite costos negativos y extremos int; ordena punteros a arcos por burbuja estable, no por O(E log E).
 * @note Arcos simétricos se consideran por separado; Union-Find descarta el segundo sentido y los bucles.
 * @note En empates conserva el orden de la lista de arcos; ante desconexión devuelve un bosque. No modifica marcas.
 * @note El C no tiene bandera dirigida: considera arcos como conexiones; la API rechaza grafos dirigidos.
 */
ListaArco grafo_kruskal(Grafo g);

#endif
