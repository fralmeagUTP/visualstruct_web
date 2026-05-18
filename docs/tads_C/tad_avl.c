#include <stdio.h>
#include <stdlib.h>

#define TRUE 1
#define FALSE 0

/**
 * @struct nodoAVL
 * @brief Estructura para un nodo de Árbol AVL.
 * @var nodoAVL::nro
 *  Valor entero almacenado en el nodo.
 * @var nodoAVL::FE
 *  Factor de equilibrio del nodo (der-izq).
 * @var nodoAVL::der
 *  Puntero al hijo derecho.
 * @var nodoAVL::izq
 *  Puntero al hijo izquierdo.
 * @var nodoAVL::padre
 *  Puntero al nodo padre (opcional para facilitar balanceo).
 */
typedef struct nodoAVL {
    int nro;
    int FE;
    struct nodoAVL *der;
    struct nodoAVL *izq;
    struct nodoAVL *padre;
} nodoAVL;

typedef nodoAVL* AVL;

/**
 * @brief Muestra el árbol AVL de forma visual (rotado 90°).
 * @param arbol Raíz del árbol a mostrar.
 * @param n Nivel de profundidad actual (usar 0 al invocar).
 */
void avl_verArbol(AVL arbol, int n) {
    int i;
    if (arbol == NULL) 
        return;
    avl_verArbol(arbol->der, n + 1);
    for (i = 0; i < n; i++) 
        printf("   ");
    printf("%d\n", arbol->nro);
    avl_verArbol(arbol->izq, n + 1);
}

/**
 * @brief Indica si un nodo es hoja.
 * @param nodo Nodo a evaluar (puede ser NULL).
 * @return 1 si no tiene hijos, 0 en otro caso.
 */
int avl_esHoja(AVL nodo) {
    if (nodo == NULL) return 0;
    return !nodo->der && !nodo->izq;
}

/**
 * @brief Calcula la avl_altura del árbol (número de niveles).
 * @param arbol Raíz del árbol.
 * @return Altura del árbol (0 si está vacío).
 */
int avl_altura(AVL arbol) {
    if (arbol == NULL) 
        return 0;
    int altIzq = avl_altura(arbol->izq);
    int altDer = avl_altura(arbol->der);
    return (altIzq > altDer ? altIzq : altDer) + 1;
}

/**
 * @brief Rotación simple derecha (avl_RSD).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso IZQUIERDA-IZQUIERDA o punto de rotación).
 */
void avl_RSD(AVL *r, AVL nodo) {
    if (r == NULL || nodo == NULL || nodo->izq == NULL) {
        return;
    }

    AVL padre = nodo->padre;
    AVL A = nodo;
    AVL B = A->izq;
    AVL C = B->der;

    if (padre) {
        if (padre->der == A) 
            padre->der = B;
        else 
            padre->izq = B;
    } 
    else {
        *r = B;
    }
    A->izq = C;
    B->der = A;
    A->padre = B;
    if (C) 
        C->padre = A;
    B->padre = padre;

    A->FE = 0;
    B->FE = 0;
}

/**
 * @brief Rotación simple izquierda (avl_RSI).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso DERECHA-DERECHA o punto de rotación).
 */
void avl_RSI(AVL *r, AVL nodo) {
    if (r == NULL || nodo == NULL || nodo->der == NULL) {
        return;
    }

    AVL padre = nodo->padre;
    AVL A = nodo;
    AVL B = A->der;
    AVL C = B->izq;

    if (padre) {
        if (padre->der == A) 
            padre->der = B;
        else 
            padre->izq = B;
    } 
    else {
        *r = B;
    }
    A->der = C;
    B->izq = A;
    A->padre = B;
    if (C) 
        C->padre = A;
    B->padre = padre;

    A->FE = 0;
    B->FE = 0;
}

/**
 * @brief Rotación doble derecha (avl_RDD).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso IZQUIERDA-DERECHA).
 */
void avl_RDD(AVL *r, AVL nodo) {
    if (r == NULL || nodo == NULL || nodo->izq == NULL || nodo->izq->der == NULL) {
        return;
    }

    AVL A = nodo;
    AVL B = A->izq;
    AVL C = B->der;

    if (C->FE == -1) {
        A->FE = 1; 
        B->FE = 0; 
        C->FE = 0;
    } 
    else if (C->FE == 1) {
        A->FE = 0; 
        B->FE = -1; 
        C->FE = 0;
    } 
    else {
        A->FE = 0; 
        B->FE = 0; 
        C->FE = 0;
    }
    avl_RSI(r, B);
    avl_RSD(r, A);
}

/**
 * @brief Rotación doble izquierda (avl_RDI).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso DERECHA-IZQUIERDA).
 */
void avl_RDI(AVL *r, AVL nodo) {
    if (r == NULL || nodo == NULL || nodo->der == NULL || nodo->der->izq == NULL) {
        return;
    }

    AVL A = nodo;
    AVL B = A->der;
    AVL C = B->izq;

    if (C->FE == -1) {
        A->FE = 0; 
        B->FE = 1; 
        C->FE = 0;
    } 
    else if (C->FE == 1) {
        A->FE = -1; 
        B->FE = 0; 
        C->FE = 0;
    } 
    else {
        A->FE = 0; 
        B->FE = 0; 
        C->FE = 0;
    }
    avl_RSD(r, B);
    avl_RSI(r, A);
}

/**
 * @brief Inserta un valor en el árbol AVL.
 * @param raiz Referencia a la raíz del árbol.
 * @param x Valor a avl_insertar (no se insertan duplicados).
 */
void avl_insertar(AVL *raiz, int x) {
    if (raiz == NULL) {
        return;
    }

    AVL padre = NULL, actual = *raiz;
    while (actual != NULL) {
        padre = actual;
        if (x < actual->nro) 
            actual = actual->izq;
        else if (x > actual->nro) 
            actual = actual->der;
        else 
            return; // no duplicados
    }

    AVL nuevo = malloc(sizeof(*nuevo));
    if (nuevo == NULL) {
        return;
    }
    nuevo->nro = x;
    nuevo->FE = 0;
    nuevo->izq = nuevo->der = NULL;
    nuevo->padre = padre;

    if (padre == NULL) {
        *raiz = nuevo;
        return;
    }
    if (x < padre->nro) 
        padre->izq = nuevo;
    else 
        padre->der = nuevo;

    // Rebalanceo incremental tras inserción
    AVL n = nuevo;
    while (padre != NULL) {
        if (n == padre->izq) 
            padre->FE--;
        else 
            padre->FE++;

        if (padre->FE == 0) 
            break;
        if (padre->FE == -2) {
            if (n->FE <= 0) 
                avl_RSD(raiz, padre);
            else 
                avl_RDD(raiz, padre);
            break;
        }
        if (padre->FE == 2) {
            if (n->FE >= 0) 
                avl_RSI(raiz, padre);
            else 
                avl_RDI(raiz, padre);
            break;
        }
        n = padre;
        padre = padre->padre;
    }
}

/**
 * @brief Reequilibra el árbol tras una eliminación, subiendo desde "nodo" hasta la raíz.
 * @param raiz Referencia a la raíz del árbol.
 * @param nodo Nodo desde el cual se inicia el rebalanceo (típicamente el padre del eliminado).
 */
AVL avl_buscar(AVL raiz, int x);
AVL avl_minimo(AVL nodo);

static void rebalancearTrasEliminar(AVL *raiz, AVL nodo) {
    while (nodo) {
        // Recalcular FE a partir de alturas actuales
        nodo->FE = avl_altura(nodo->der) - avl_altura(nodo->izq);

        if (nodo->FE == -2) {
            // Desbalance hacia la izquierda
            AVL L = nodo->izq;
            int feL = (L ? (avl_altura(L->der) - avl_altura(L->izq)) : 0);
            if (feL > 0) {
                // Caso IZQ-DER -> Rotación doble derecha
                avl_RDD(raiz, nodo);
            } else {
                // Caso IZQ-IZQ -> Rotación simple derecha
                avl_RSD(raiz, nodo);
            }
        } else if (nodo->FE == 2) {
            // Desbalance hacia la derecha
            AVL R = nodo->der;
            int feR = (R ? (avl_altura(R->der) - avl_altura(R->izq)) : 0);
            if (feR < 0) {
                // Caso DER-IZQ -> Rotación doble izquierda
                avl_RDI(raiz, nodo);
            } else {
                // Caso DER-DER -> Rotación simple izquierda
                avl_RSI(raiz, nodo);
            }
        }
        nodo = nodo->padre;
    }
}

/**
 * @brief Elimina el valor indicado del árbol AVL (con rebalanceo).
 * @param raiz Referencia a la raíz del árbol.
 * @param x Valor a avl_eliminar.
 */
void avl_eliminar(AVL *raiz, int x) {
    if (raiz == NULL) {
        return;
    }

    AVL z = avl_buscar(*raiz, x);
    if (!z) return;

    // Si tiene dos hijos, intercambiar con el sucesor inorden y descender
    while (z->izq && z->der) {
        AVL s = avl_minimo(z->der);
        int tmp = z->nro;
        z->nro = s->nro;
        s->nro = tmp;
        z = s; // continuar eliminando más abajo
    }

    // Ahora z tiene 0 o 1 hijo: avl_eliminar físicamente
    AVL padre = z->padre;
    AVL child = (z->izq) ? z->izq : z->der;
    if (child) child->padre = padre;

    if (!padre) {
        *raiz = child;
    } else if (padre->izq == z) {
        padre->izq = child;
    } else {
        padre->der = child;
    }
    free(z);

    // Reequilibrar subiendo desde el padre
    if (padre) rebalancearTrasEliminar(raiz, padre);
}

/**
 * @brief Busca un valor en el árbol AVL.
 * @param raiz Raíz del árbol.
 * @param x Valor a avl_buscar.
 * @return Puntero al nodo con el valor o NULL si no se encuentra.
 */
AVL avl_buscar(AVL raiz, int x) {
    if (!raiz) 
        return NULL;
    if (x < raiz->nro) 
        return avl_buscar(raiz->izq, x);
    if (x > raiz->nro) 
        return avl_buscar(raiz->der, x);
    return raiz;
}

/**
 * @brief Obtiene el nodo con el valor mínimo del subárbol dado.
 * @param nodo Raíz del subárbol.
 * @return Puntero al nodo con el valor mínimo.
 */
AVL avl_minimo(AVL nodo) {
    while (nodo->izq) 
        nodo = nodo->izq;
    return nodo;
}


/**
 * @brief Libera toda la memoria del árbol AVL (postorden).
 * @param raiz Raíz del árbol a liberar.
 */
void avl_liberarAVL(AVL raiz) {
    if (!raiz) 
        return;
    avl_liberarAVL(raiz->izq);
    avl_liberarAVL(raiz->der);
    free(raiz);
}

