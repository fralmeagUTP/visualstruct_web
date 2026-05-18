#ifndef TAD_AVL_H
#define TAD_AVL_H

/**
 * @file tad_avl.h
 * @brief TAD Arbol AVL de enteros.
 */

/** @brief Nodo de arbol AVL. */
typedef struct nodoAVL {
    int nro;                 
    int FE;                  
    struct nodoAVL *der;     
    struct nodoAVL *izq;     
    struct nodoAVL *padre;   
} nodoAVL;

/** @brief Alias de puntero al nodo AVL. */
typedef nodoAVL* AVL;

/** @brief Muestra el arbol AVL rotado 90 grados. */
void avl_verArbol(AVL arbol, int n);
/** @brief Verifica si un nodo es hoja. */
int avl_esHoja(AVL nodo);
/** @brief Calcula avl_altura del arbol. */
int avl_altura(AVL arbol);
/** @brief Rotacion simple derecha. */
void avl_RSD(AVL *r, AVL nodo);
/** @brief Rotacion simple izquierda. */
void avl_RSI(AVL *r, AVL nodo);
/** @brief Rotacion doble derecha (izq-der). */
void avl_RDD(AVL *r, AVL nodo);
/** @brief Rotacion doble izquierda (der-izq). */
void avl_RDI(AVL *r, AVL nodo);
/** @brief Inserta un valor. */
void avl_insertar(AVL *raiz, int x);
/** @brief Elimina un valor. */
void avl_eliminar(AVL *raiz, int x);
/** @brief Busca un valor. */
AVL avl_buscar(AVL raiz, int x);
/** @brief Devuelve el avl_minimo en un subarbol. */
AVL avl_minimo(AVL nodo);
/** @brief Libera toda la memoria del arbol. */
void avl_liberarAVL(AVL raiz);

#endif
