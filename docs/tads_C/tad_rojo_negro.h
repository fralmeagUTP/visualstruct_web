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
    int nro;                  
    char rbt_color;               
    struct nodoRBT *padre;   
    struct nodoRBT *izq;      
    struct nodoRBT *der;     
} nodoRBT;

/** @brief Alias de puntero al nodo RBT. */
typedef struct nodoRBT *RBT;

RBT rbt_abuelo(RBT n);
RBT rbt_tio(RBT n);
void rbt_rotar_dcha(RBT *r, RBT nodoRBT);
void rbt_rotar_izda(RBT *r, RBT nodoRBT);
void rbt_insercion_caso1(RBT n, RBT *arbol);
void rbt_insercion_caso2(RBT n, RBT *arbol);
void rbt_insercion_caso3(RBT n, RBT *arbol);
void rbt_insercion_caso4(RBT n, RBT *arbol);
void rbt_insercion_caso5(RBT n, RBT *arbol);
void rbt_color(int c);
RBT rbt_buscar(RBT nodoRBT, int dato);
void rbt_verArbol(RBT arbol, int n);
void rbt_insertar(RBT *arbol, int dato);
void rbt_eliminar(RBT *arbol, int key);
void rbt_liberar(RBT arbol);

#endif
