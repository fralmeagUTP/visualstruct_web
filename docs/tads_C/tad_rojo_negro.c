/**
 * @file tad_rojo_negro.c
 * @brief Implementación del TAD Árbol rojo-negro.
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#ifdef _WIN32
#include <windows.h>
#endif

/** @brief Representación del color rojo: carácter r. */
#define ROJO 'r'
/** @brief Representación del color negro: carácter n. */
#define NEGRO 'n'

/**
 * @struct nodoRBT
 * @brief Estructura para un nodo de Árbol Rojo-Negro.
 */
typedef struct nodoRBT {
    int nro; /**< Dato entero almacenado. */
    char rbt_color; /**< Color del nodo rojo-negro. */
    struct nodoRBT *padre; /**< Enlace al padre; NULL en la raiz. */
    struct nodoRBT *izq; /**< Hijo izquierdo. */
    struct nodoRBT *der; /**< Hijo derecho. */
} nodoRBT; /**< Alias del nodo rojo-negro. */

/** @brief Puntero a un nodo o raíz rojo-negro. */
typedef struct nodoRBT *RBT;

/* Prototipos de funciones */
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
void rbt_color(int c) {
#ifdef _WIN32
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), c);
#else
    (void)c;
#endif
}


/**
 * @brief Busca un entero por comparaciones sin mutar ni reservar memoria.
 * @param nodoRBT Raiz prestada de un arbol valido; NULL admitido.
 * @param dato Entero buscado.
 * @return Alias prestado al nodo encontrado o NULL; no transfiere propiedad.
 * @note Imprime un mensaje distinto para arbol vacio, dato presente o dato ausente.
 * El alias pierde validez cuando esa reserva es liberada; no debe liberarse por la consulta.
 */
RBT rbt_buscar(RBT nodoRBT, int dato) {
    RBT actual = nodoRBT;
    if (nodoRBT == NULL) {
        printf("\n\tEl arbol esta vacio\n\n");
        return NULL;
    }
    while (actual != NULL) {
        if (dato == actual->nro) {
            printf("\n\tEl numero %d existe en el arbol\n", dato);
            return actual;
        } else if (dato < actual->nro)
            actual = actual->izq;
        else if (dato > actual->nro)
            actual = actual->der;
    }
    printf("\n\tEl numero %d NO existe en el arbol\n", dato);
    return NULL;
}

/**
 * @brief Imprime el arbol rotado: subarbol derecho, nodo, subarbol izquierdo.
 * @param arbol Raiz prestada de un arbol valido; NULL no imprime nada.
 * @param n Profundidad inicial no negativa, normalmente 0.
 * @note Cada nivel agrega tres espacios y cada entero termina en salto de linea.
 * Solicita color rojo/negro y luego blanco en consola Windows; no garantiza soporte.
 * No es recorrido inorden ascendente y no muta ni libera el arbol.
 */
void rbt_verArbol(RBT arbol, int n) {
    int i;
    if (arbol == NULL)
        return;
    rbt_verArbol(arbol->der, n + 1);

    for (i = 0; i < n; i++)
        printf("   ");

    if (arbol->rbt_color == ROJO)
        rbt_color(12);
    else if (arbol->rbt_color == NEGRO)
        rbt_color(8);
    printf("%d\n", arbol->nro);

    rbt_verArbol(arbol->izq, n + 1);
    rbt_color(15);
}


/**
 * @brief Consulta el abuelo sin mutar ni transferir propiedad.
 * @param n Nodo prestado vivo o NULL.
 * @return Alias prestado al padre del padre, o NULL si n o su padre son NULL.
 * @pre Los enlaces de nodos no NULL consultados apuntan a reservas vivas consistentes.
 * @note No recorre todo el arbol, imprime, reserva o libera memoria; O(1).
 */
RBT rbt_abuelo(RBT n) {
    if ((n != NULL) && (n->padre != NULL))
        return n->padre->padre;
    else
        return NULL;
}

/**
 * @brief Consulta el hermano del padre mediante rbt_abuelo.
 * @param n Nodo prestado vivo o NULL.
 * @return Alias al hijo opuesto del abuelo; NULL si no hay abuelo o tio.
 * @pre Los enlaces padre/hijos consultados son vivos y consistentes.
 * @note Si el padre es hijo izquierdo devuelve der; en otro caso devuelve izq.
 * No muta, imprime, reserva ni libera; el alias no transfiere propiedad; O(1).
 */
RBT rbt_tio(RBT n) {
    RBT a = rbt_abuelo(n);
    if (a == NULL)
        return NULL;
    if (n->padre == a->izq)
        return a->der;
    else
        return a->izq;
}

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
void rbt_rotar_dcha(RBT *r, RBT nodoRBT) {
    if (r == NULL || nodoRBT == NULL || nodoRBT->izq == NULL) {
        return;
    }

    RBT padre = nodoRBT->padre;
    RBT A = nodoRBT;
    RBT B = A->izq;
    RBT C = B->der;
    if (padre != NULL) {
        if (padre->der == A)
            padre->der = B;
        else
            padre->izq = B;
    } else
        *r = B;

    A->izq = C;
    B->der = A;
    A->padre = B;
    if (C)
        C->padre = A;
    B->padre = padre;
}

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
void rbt_rotar_izda(RBT *r, RBT nodoRBT) {
    if (r == NULL || nodoRBT == NULL || nodoRBT->der == NULL) {
        return;
    }

    RBT padre = nodoRBT->padre;
    RBT A = nodoRBT;
    RBT B = A->der;
    RBT C = B->izq;
    if (padre != NULL) {
        if (padre->der == A)
            padre->der = B;
        else
            padre->izq = B;
    } else
        *r = B;

    A->der = C;
    B->izq = A;
    A->padre = B;
    if (C)
        C->padre = A;
    B->padre = padre;
}

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
void rbt_insercion_caso5(RBT n, RBT *arbol) {
    RBT a = rbt_abuelo(n);
    n->padre->rbt_color = NEGRO;
    a->rbt_color = ROJO;
    if ((n == n->padre->izq) && (n->padre == a->izq)) {
        rbt_rotar_dcha(arbol, a);
    } else {
        rbt_rotar_izda(arbol, a);
    }
}

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
void rbt_insercion_caso4(RBT n, RBT *arbol) {
    RBT a = rbt_abuelo(n);
    RBT nuevo_n = n;

    if ((n == n->padre->der) && (n->padre == a->izq)) {
        rbt_rotar_izda(arbol, n->padre);
        nuevo_n = n->izq;
    } else if ((n == n->padre->izq) && (n->padre == a->der)) {
        rbt_rotar_dcha(arbol, n->padre);
        nuevo_n = n->der;
    }
    rbt_insercion_caso5(nuevo_n, arbol);
}

/**
 * @brief Recolorea padre y tio rojos o delega al caso geometrico.
 * @param n Nodo vivo con padre rojo y abuelo no NULL.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion, enlaces vivos consistentes.
 * @note Tio rojo: padre y tio NEGRO, abuelo ROJO y caso1 sobre el abuelo.
 * Tio negro o NULL: caso4. La recursion puede propagar la reparacion a ancestros;
 * no cambia valores ni reserva/libera/imprime. Retorno void.
 */
void rbt_insercion_caso3(RBT n, RBT *arbol) {
    RBT t = rbt_tio(n);
    RBT a;

    if ((t != NULL) && (t->rbt_color == ROJO)) {
        n->padre->rbt_color = NEGRO;
        t->rbt_color = NEGRO;
        a = rbt_abuelo(n);
        a->rbt_color = ROJO;
        rbt_insercion_caso1(a, arbol);
    } else {
        rbt_insercion_caso4(n, arbol);
    }
}

/**
 * @brief Termina si el padre es negro o delega a caso3.
 * @param n Nodo vivo con padre no NULL en la reparacion.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion y enlaces vivos consistentes.
 * @note Padre negro no cambia campos; padre rojo requiere reparar. Este caso
 * no comprueba globalmente orden, altura negra ni padres. Void, sin reserva/free/printf.
 */
void rbt_insercion_caso2(RBT n, RBT *arbol) {
    if (n->padre->rbt_color == NEGRO)
        return;
    else
        rbt_insercion_caso3(n, arbol);
}

/**
 * @brief Pinta de negro un nodo sin padre o continua la reparacion.
 * @param n Nodo vivo de la reparacion, insertado o ancestro al propagar recoloreos.
 * @param arbol Referencia escribible y no NULL a la raiz.
 * @pre Contexto valido de insercion; n no es NULL y enlaces vivos son consistentes.
 * @note Decide por n->padre==NULL, no por una comparacion con *arbol.
 * Si no es raiz llama caso2. Retorna void, sin reserva, free ni printf.
 */
void rbt_insercion_caso1(RBT n, RBT *arbol) {
    if (n->padre == NULL)
        n->rbt_color = NEGRO;
    else
        rbt_insercion_caso2(n, arbol);
}

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
void rbt_insertar(RBT *arbol, int dato) {
    if (arbol == NULL) {
        return;
    }

    RBT padre = NULL;
    RBT actual = *arbol;
    while (actual != NULL && dato != actual->nro) {
        padre = actual;
        if (dato < actual->nro)
            actual = actual->izq;
        else if (dato > actual->nro)
            actual = actual->der;
    }
    if (actual != NULL)
        return;
    actual = malloc(sizeof(struct nodoRBT));
    if (actual == NULL) {
        return;
    }
    actual->nro = dato;
    actual->izq = actual->der = NULL;
    actual->padre = padre;
    actual->rbt_color = ROJO;
    if (padre == NULL) {
        *arbol = actual;
    } else if (dato < padre->nro) {
        padre->izq = actual;
    } else if (dato > padre->nro) {
        padre->der = actual;
    }
    rbt_insercion_caso1(actual, arbol);
    printf("\tEl numero ha sido insertado\n");
}

/* ====== Eliminacion con rebalanceo (algoritmo tipo CLRS), sin NIL ====== */
/**
 * @brief Lee el color prestado o representa una hoja NULL como negra.
 * @param n Nodo vivo prestado, o NULL; no consume propiedad.
 * @return NEGRO para NULL; en otro caso el char literal almacenado en rbt_color.
 * @note No valida el char, no escribe ni reserva/libera/imprime; tiempo y pila O(1).
 */
static char colorOf(RBT n) { return (n == NULL) ? NEGRO : n->rbt_color; }

/**
 * @brief Sustituye el enlace propietario a u y actualiza el padre de v.
 * @param root Referencia escribible y no NULL a la raiz.
 * @param u Nodo vivo enlazado al arbol, no NULL, con padre consistente.
 * @param v Subarbol vivo sustituto, o NULL.
 * @pre Las reservas y enlaces son validos en el contexto de eliminacion.
 * @note Si u no tiene padre escribe *root; si no, escribe el hijo izq/der del padre.
 * Solo cuando v existe le asigna u->padre. Conserva los campos de u, incluido
 * su padre antiguo para el caller; no libera u ni cambia valores o colores.
 * Void, sin reserva/free/printf; tiempo y pila O(1).
 */
static void transplantar(RBT *root, RBT u, RBT v) {
    if (u->padre == NULL) {
        *root = v;
    } else if (u == u->padre->izq) {
        u->padre->izq = v;
    } else {
        u->padre->der = v;
    }
    if (v) v->padre = u->padre;
}

/**
 * @brief Recorre enlaces izquierdos y retorna su ultimo nodo prestado.
 * @param n Raiz viva de una cadena izquierda finita; NULL admitido.
 * @return Alias prestado al extremo izquierdo, o NULL para entrada NULL.
 * @note Es el minimo bajo orden BST; no valida ese orden. Solo modifica su
 * parametro local, sin reconectar, reservar, liberar ni imprimir. Tiempo O(h), pila O(1).
 */
static RBT minimo(RBT n) {
    while (n && n->izq) n = n->izq;
    return n;
}

/**
 * @brief Repara el deficit de negro mediante hermanos, recoloreos y rotaciones.
 * @param root Referencia escribible y no NULL a la raiz.
 * @param x Reserva viva que reemplaza al eliminado, o NULL.
 * @param x_parent Padre vivo del reemplazo; necesario cuando x es NULL salvo arbol vacio.
 * @pre Contexto de eliminacion valido: referencias restantes vivas y padres consistentes.
 * @note NULL se considera NEGRO, no una reserva NIL. Mientras x no sea raiz y
 * sea negro, distingue lado, hermano y colores de sus hijos; las ramas espejo
 * reparan con las rotaciones reales o propagan x al padre. Si x_parent es NULL
 * sale por break; al finalizar, x no NULL se pinta NEGRO. Retorna void, sin
 * reserva, free ni printf; no cambia enteros. Tiempo O(h), pila auxiliar O(1).
 */
static void arreglarEliminacion(RBT *root, RBT x, RBT x_parent) {
    /* Mientras x no sea la raiz y sea negro, corregimos desde abajo hacia arriba */
    while (x != *root && colorOf(x) == NEGRO) {
        if (x_parent == NULL) {
            break;
        }

        int es_izq = (x == (x_parent ? x_parent->izq : NULL));
        RBT w = x_parent ? (es_izq ? x_parent->der : x_parent->izq) : NULL; /* hermano de x */
        RBT w_izq = w ? w->izq : NULL;
        RBT w_der = w ? w->der : NULL;

        if (es_izq) {
            /* CASO 1 (simétrico): w rojo -> rotar izda en padre */
            if (colorOf(w) == ROJO) {
                w->rbt_color = NEGRO;
                x_parent->rbt_color = ROJO;
                rbt_rotar_izda(root, x_parent);
                w = x_parent->der; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
            }
            /* CASO 2: w negro y sus dos hijos negros -> recolorear w y subir */
            if (colorOf(w_izq) == NEGRO && colorOf(w_der) == NEGRO) {
                if (w) w->rbt_color = ROJO;
                x = x_parent;
                x_parent = x ? x->padre : NULL;
            } else {
                /* CASO 3: w negro, hijo derecho negro, hijo izquierdo rojo -> rotar dcha en w */
                if (colorOf(w_der) == NEGRO) {
                    if (w_izq) w_izq->rbt_color = NEGRO;
                    if (w) { w->rbt_color = ROJO; rbt_rotar_dcha(root, w); }
                    w = x_parent ? x_parent->der : NULL; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
                }
                /* CASO 4: w negro, hijo derecho rojo -> rotar izda en padre y recolorear */
                if (w) w->rbt_color = colorOf(x_parent);
                x_parent->rbt_color = NEGRO;
                if (w_der) w_der->rbt_color = NEGRO;
                rbt_rotar_izda(root, x_parent);
                x = *root; /* terminamos */
            }
        } else {
            /* Lado derecho: casos espejo */
            if (colorOf(w) == ROJO) {
                w->rbt_color = NEGRO;
                x_parent->rbt_color = ROJO;
                rbt_rotar_dcha(root, x_parent);
                w = x_parent ? x_parent->izq : NULL; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
            }
            if (colorOf(w_der) == NEGRO && colorOf(w_izq) == NEGRO) {
                if (w) w->rbt_color = ROJO;
                x = x_parent;
                x_parent = x ? x->padre : NULL;
            } else {
                if (colorOf(w_izq) == NEGRO) {
                    if (w_der) w_der->rbt_color = NEGRO;
                    if (w) { w->rbt_color = ROJO; rbt_rotar_izda(root, w); }
                    w = x_parent ? x_parent->izq : NULL; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
                }
                if (w) w->rbt_color = colorOf(x_parent);
                x_parent->rbt_color = NEGRO;
                if (w_izq) w_izq->rbt_color = NEGRO;
                rbt_rotar_dcha(root, x_parent);
                x = *root;
            }
        }
    }
    if (x) x->rbt_color = NEGRO;
}

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
void rbt_eliminar(RBT *arbol, int key) {
    RBT z = *arbol;
    while (z != NULL && z->nro != key) {
        if (key < z->nro) z = z->izq; else z = z->der;
    }
    if (z == NULL) return; /* no encontrado */

    RBT y = z;
    char y_color_original = y->rbt_color;
    RBT x = NULL;
    RBT x_parent = NULL;

    if (z->izq == NULL) {
        x = z->der;
        x_parent = z->padre;
        transplantar(arbol, z, z->der);
    } else if (z->der == NULL) {
        x = z->izq;
        x_parent = z->padre;
        transplantar(arbol, z, z->izq);
    } else {
        y = minimo(z->der);
        y_color_original = y->rbt_color;
        x = y->der;
        if (y->padre == z) {
            x_parent = y;
        } else {
            transplantar(arbol, y, y->der);
            x_parent = y->padre;
            y->der = z->der;
            y->der->padre = y;
        }
        transplantar(arbol, z, y);
        y->izq = z->izq;
        y->izq->padre = y;
        y->rbt_color = z->rbt_color;
    }

    free(z);

    if (y_color_original == NEGRO) {
        arreglarEliminacion(arbol, x, x_parent);
    }
    if (*arbol) (*arbol)->rbt_color = NEGRO;
}

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
void rbt_liberar(RBT arbol) {
    if (arbol == NULL)
        return;
    rbt_liberar(arbol->izq);
    rbt_liberar(arbol->der);
    free(arbol);
}



/**
 * @brief Obtiene altura negra o cero si falla una regla estructural.
 * @param nodo Nodo prestado vivo y legible; NULL representa hoja negra.
 * @param padreEsperado Identidad del padre exigido, NULL en la raiz.
 * @param tieneMin Indica presencia de cota inferior exclusiva.
 * @param minimo Cota inferior cuando tieneMin es uno.
 * @param tieneMax Indica presencia de cota superior exclusiva.
 * @param maximo Cota superior cuando tieneMax es uno.
 * @return Altura negra positiva (NULL=1) o cero ante invalidez.
 * @note Solo lectura, sin reservas, liberaciones ni salida. Padres y cotas
 * estrictas rechazan ciclos y nodos compartidos vivos. No admite referencias
 * colgantes. Usa O(h) pila y O(n) tiempo en arboles validos.
 */
static int rbt_validar_altura_negra(RBT nodo, RBT padreEsperado, int tieneMin, int minimo, int tieneMax, int maximo) {
    if (nodo == NULL) return 1;
    if (nodo->padre != padreEsperado) return 0;
    if (nodo->rbt_color != ROJO && nodo->rbt_color != NEGRO) return 0;
    if (tieneMin && nodo->nro <= minimo) return 0;
    if (tieneMax && nodo->nro >= maximo) return 0;
    if (nodo->rbt_color == ROJO &&
        ((nodo->izq != NULL && nodo->izq->rbt_color == ROJO) ||
         (nodo->der != NULL && nodo->der->rbt_color == ROJO))) return 0;
    int bhIzq = rbt_validar_altura_negra(nodo->izq, nodo, tieneMin, minimo, 1, nodo->nro);
    if (bhIzq == 0) return 0;
    int bhDer = rbt_validar_altura_negra(nodo->der, nodo, 1, nodo->nro, tieneMax, maximo);
    if (bhDer == 0 || bhIzq != bhDer) return 0;
    if (nodo->rbt_color == NEGRO && bhIzq == INT_MAX) return 0;
    return bhIzq + (nodo->rbt_color == NEGRO ? 1 : 0);
}

/**
 * @brief Comprueba reglas RN, orden estricto y padres/ciclos/nodos compartidos.
 * @param raiz Raiz prestada; NULL valido; referencias no NULL vivas y legibles.
 * @return 1 valido, 0 invalido, sin reparar ni mutar la representacion.
 * @note Solo lectura: no reserva, libera ni imprime. NULL es hoja negra;
 * altura negra uniforme y raiz negra con padre NULL. No punteros colgantes.
 */
int rbt_validar(RBT raiz) {
    if (raiz == NULL) return 1;
    if (raiz->rbt_color != NEGRO) return 0;
    return rbt_validar_altura_negra(raiz, NULL, 0, 0, 0, 0) != 0;
}
