#ifndef TAD_ROJONEGRO_H
#define TAD_ROJONEGRO_H

/**
 * @file tad_rojo_negro.h
 * @brief TAD Arbol Rojo-Negro de enteros.
 */

/** @brief Color rojo. */
#define ROJO 'r'
/** @brief Color negro. */
#define NEGRO 'n'

/** @brief Nodo de arbol Rojo-Negro. */
typedef struct nodoRBT {
    int nro; /**< Dato entero almacenado. */
    char rbt_color; /**< Color del nodo: r para rojo, n para negro. */               
    struct nodoRBT *padre; /**< Enlace al padre del nodo. */
    struct nodoRBT *izq; /**< Hijo izquierdo. */
    struct nodoRBT *der; /**< Hijo derecho. */
} nodoRBT;

/** @brief Alias de puntero al nodo RBT. */
typedef struct nodoRBT *RBT;

/**
 * @brief Consulta el abuelo sin mutar ni transferir propiedad.
 * @param n Nodo prestado vivo o NULL.
 * @return Alias prestado al padre del padre, o NULL si n o su padre son NULL.
 * @pre Los enlaces de nodos no NULL consultados apuntan a reservas vivas consistentes.
 * @note No recorre todo el arbol, imprime, reserva o libera memoria; O(1).
 */
RBT rbt_abuelo(RBT n);
/**
 * @brief Consulta el hermano del padre mediante rbt_abuelo.
 * @param n Nodo prestado vivo o NULL.
 * @return Alias al hijo opuesto del abuelo; NULL si no hay abuelo o tio.
 * @pre Los enlaces padre/hijos consultados son vivos y consistentes.
 * @note Si el padre es hijo izquierdo devuelve der; en otro caso devuelve izq.
 * No muta, imprime, reserva ni libera; el alias no transfiere propiedad; O(1).
 */
RBT rbt_tio(RBT n);
/**
 * @brief Rota a la derecha conservando identidad y orden de los nodos.
 * @param r Referencia escribible a la raiz; NULL es no-op.
 * @param nodoRBT Pivote vivo; NULL o hijo izq NULL es no-op.
 * @pre Para una rotacion efectiva, el pivote pertenece al arbol y padre/hijos
 * son vivos y consistentes. Su hijo izquierdo y el posible subarbol transferido son vivos.
 * @note Actualiza el enlace del padre o *r, transfiere B->der a A->izq,
 * coloca A como B->der y corrige padres. No reserva, libera, imprime ni recolorea;
 * O(1). La rotacion aislada no garantiza todas las reglas rojo-negro.
 * Los enlaces intermedios son pasos de escritura, no un arbol final certificado.
 */
void rbt_rotar_dcha(RBT *r, RBT nodoRBT);
/**
 * @brief Rota a la izquierda conservando identidad y orden de los nodos.
 * @param r Referencia escribible a la raiz; NULL es no-op.
 * @param nodoRBT Pivote vivo; NULL o hijo der NULL es no-op.
 * @pre Para una rotacion efectiva, el pivote pertenece al arbol y padre/hijos
 * son vivos y consistentes. Su hijo derecho y el posible subarbol transferido son vivos.
 * @note Actualiza el enlace del padre o *r, transfiere B->izq a A->der,
 * coloca A como B->izq y corrige padres. No reserva, libera, imprime ni recolorea;
 * O(1). La rotacion aislada no garantiza todas las reglas rojo-negro.
 * Los enlaces intermedios son pasos de escritura, no un arbol final certificado.
 */
void rbt_rotar_izda(RBT *r, RBT nodoRBT);
/**
 * @brief Pinta de negro un nodo sin padre o continua la reparacion.
 * @param n Nodo vivo de la reparacion, insertado o ancestro al propagar recoloreos.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion; n no es NULL y enlaces vivos son consistentes.
 * @note Decide por n->padre==NULL, no por una comparacion con *arbol.
 * Si no es raiz llama caso2. Retorna void, sin reserva, free ni printf.
 */
void rbt_insercion_caso1(RBT n, RBT *arbol);
/**
 * @brief Termina si el padre es negro o delega a caso3.
 * @param n Nodo vivo con padre no NULL en la reparacion.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion y enlaces vivos consistentes.
 * @note Padre negro no cambia campos; padre rojo requiere reparar. Este caso
 * no comprueba globalmente orden, altura negra ni padres. Void, sin reserva/free/printf.
 */
void rbt_insercion_caso2(RBT n, RBT *arbol);
/**
 * @brief Recolorea padre y tio rojos o delega al caso geometrico.
 * @param n Nodo vivo con padre rojo y abuelo no NULL.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion, enlaces vivos consistentes.
 * @note Tio rojo: padre y tio NEGRO, abuelo ROJO y caso1 sobre el abuelo.
 * Tio negro o NULL: caso4. La recursion puede propagar la reparacion a ancestros;
 * no cambia valores ni reserva/libera/imprime. Retorno void.
 */
void rbt_insercion_caso3(RBT n, RBT *arbol);
/**
 * @brief Alinea un triangulo y pasa el alias ajustado a caso5.
 * @param n Nodo vivo con padre rojo y abuelo no NULL.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion, tio negro o NULL y enlaces consistentes.
 * @note LR: rota izda en padre y nuevo_n=n->izq; RL: rota dcha en padre
 *  y nuevo_n=n->der. Si ya esta alineado no rota aqui. n no se reasigna:
 *  nuevo_n es otro local y puede identificar al padre previo. Luego llama caso5.
 * Retorna void; no reserva/libera/imprime ni recolorea directamente.
 */
void rbt_insercion_caso4(RBT n, RBT *arbol);
/**
 * @brief Recolorea padre/abuelo y rota el abuelo del caso alineado.
 * @param n Nodo vivo en configuracion LL o RR de la reparacion.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion; padre y abuelo vivos no NULL, enlaces
 * consistentes y tio negro o NULL. No es entrada general para un nodo arbitrario.
 * @note Padre NEGRO y abuelo ROJO; LL rota dcha, el caso espejo rota izda.
 * Las rotaciones conservan reservas/valores y pueden cambiar *arbol. Void,
 * sin reserva/free/printf; no asegura una invariante global en cada escritura parcial.
 */
void rbt_insercion_caso5(RBT n, RBT *arbol);
/**
 * @brief Solicita un color de texto de consola en Windows; no imprime caracteres.
 * @param c Atributo Win32, por ejemplo 12 rojo, 8 gris, 15 blanco.
 * @note En otras plataformas no realiza ninguna accion. El efecto depende de la consola;
 * no cambia el color almacenado en nodos ni garantiza que la solicitud tenga exito.
 */
void rbt_color(int c);
/**
 * @brief Busca un entero por comparaciones sin mutar ni reservar memoria.
 * @param nodoRBT Raiz prestada de un arbol valido; NULL admitido.
 * @param dato Entero buscado.
 * @return Alias prestado al nodo encontrado o NULL; no transfiere propiedad.
 * @note Imprime un mensaje distinto para arbol vacio, dato presente o dato ausente.
 * El alias pierde validez cuando esa reserva es liberada; no debe liberarse por la consulta.
 */
RBT rbt_buscar(RBT nodoRBT, int dato);
/**
 * @brief Imprime el arbol rotado: subarbol derecho, nodo, subarbol izquierdo.
 * @param arbol Raiz prestada de un arbol valido; NULL no imprime nada.
 * @param n Profundidad inicial no negativa, normalmente 0.
 * @note Cada nivel agrega tres espacios y cada entero termina en salto de linea.
 * Solicita color rojo/negro y luego blanco en consola Windows; no garantiza soporte.
 * No es recorrido inorden ascendente y no muta ni libera el arbol.
 */
void rbt_verArbol(RBT arbol, int n);
/**
 * @brief Inserta un entero distinto mediante enlace BST y reparacion rojo-negro.
 * @param arbol Referencia escribible a la raiz; NULL es no-op.
 * @param dato Entero a insertar, incluidos los extremos del tipo int.
 * @pre Si arbol no es NULL, *arbol es NULL o un arbol rojo-negro finito, ordenado,
 * con enlaces padre/hijos consistentes y reservas vivas propias del TAD.
 * @note Retorna void. Duplicado, arbol NULL o fallo de malloc no mutan el arbol
 * ni imprimen confirmacion. No hay codigo de estado para distinguir esos casos.
 * Busca sin reservar; luego malloc crea una reserva inicialmente no inicializada.
 * Escribe dato, hijos NULL, padre y ROJO antes de publicar el enlace o la raiz.
 * Los auxiliares reparan por recoloreos/rotaciones sin reservar ni liberar nodos.
 * Solo despues de la reparacion imprime "El numero ha sido insertado" con tabulador y salto.
 * La raiz final es negra; las hojas C son NULL, no reservas NIL. Tiempo O(log n)
 * y pila O(log n) bajo la precondicion; malloc reserva un nodo y no se llama free.
 * @warning El caller no debe interpretar el retorno void como una confirmacion
 * ni volver a ejecutar para descubrir si la primera llamada inserto.
 */
void rbt_insertar(RBT *arbol, int dato);
/**
 * @brief Desconecta un entero y libera su reserva original, reparando el arbol.
 * @param arbol Referencia escribible y no NULL a la raiz; *arbol puede ser NULL.
 * @param key Entero C a buscar; si no existe, retorna sin modificar ni imprimir.
 * @pre Arbol finito, ordenado y rojo-negro con padres consistentes y reservas vivas.
 * @note Retorna void. Vacio/ausente son no-op nativos, no un codigo de error.
 * Con cero/un hijo trasplanta ese hijo; con dos hijos traslada el sucesor minimo
 * del derecho, su reserva y enlaces, no copia el valor sobre z. Siempre free(z),
 * nunca free(y) si el sucesor y es otra reserva. No reserva ni ejecuta printf.
 * Guarda y_color_original antes de liberar; solo si era NEGRO ejecuta fix-up
 * con x y x_parent vivos o NULL. Colorea la raiz final de NEGRO si existe.
 * Tiempo O(h), O(log n) bajo la precondicion; pila auxiliar O(1), sin recursion.
 * @warning Tras free(z), todos sus alias son indeterminados y no deben leerse.
 * Si y era z, ese alias tambien termina; el color guardado es un char independiente.
 * El caller conserva propiedad del arbol restante y debe liberarlo al finalizar.
 */
void rbt_eliminar(RBT *arbol, int key);
/**
 * @brief Libera cada reserva en postorden sin asignar la raiz del llamador.
 * @param arbol Raiz por valor del arbol a consumir; NULL admitido.
 * @pre Los enlaces forman un arbol finito sin ciclos ni reservas compartidas;
 * cada nodo no NULL es una reserva viva compatible con free.
 * @note Recorre primero izq, luego der y libera el nodo. No reserva memoria,
 * imprime, retorna un puntero ni rebalancea. Los colores no condicionan la liberacion.
 * Las hojas C son NULL, no reservas NIL. Tiempo O(n), pila recursiva O(h).
 * @warning Tras liberar, los alias a cada reserva tienen valor indeterminado y no
 * deben leerse ni desreferenciarse. El llamador debe asignar NULL a su variable raiz
 * sin leer su valor anterior. Repetir con NULL es seguro; repetir con el alias antiguo no.
 */
void rbt_liberar(RBT arbol);

/**
 * @brief Comprueba reglas RN, orden estricto y padres/ciclos/nodos compartidos.
 * @param raiz Raiz prestada; NULL valido; referencias no NULL vivas y legibles.
 * @return 1 valido, 0 invalido, sin reparar ni mutar la representacion.
 * @note Solo lectura: no reserva, libera ni imprime. NULL es hoja negra;
 * altura negra uniforme y raiz negra con padre NULL. No punteros colgantes.
 */
int rbt_validar(RBT raiz);

#endif
