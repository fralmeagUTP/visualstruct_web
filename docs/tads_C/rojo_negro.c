/**
 * @file rojo_negro.c
 * @brief Implementacion encapsulada del TAD Arbol Rojo-Negro.
 */

#include "rojo_negro.h"

#include <limits.h>
#include <stdlib.h>
#include <stdio.h>

typedef enum ColorRN {
    COLOR_ROJO = 0,
    COLOR_NEGRO = 1
} ColorRN;

typedef struct NodoRN {
    int valor;
    ColorRN color;
    struct NodoRN *padre;
    struct NodoRN *izq;
    struct NodoRN *der;
} NodoRN;

struct RojoNegro {
    NodoRN *raiz;
    NodoRN *nil;
    size_t tamano;
};

/**
 * @brief Crea un nuevo nodo Rojo-Negro.
 * @param[in,out] arbol Puntero al árbol (usado para la referencia al nodo nil).
 * @param[in]     valor Entero a insertar en el nodo.
 * @return Puntero al nuevo nodo creado (color rojo por defecto), o NULL si no hay memoria.
 */
static NodoRN *crear_nodo(RojoNegro *arbol, int valor);

/**
 * @brief Libera la memoria de todos los nodos en el subárbol dado.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] nodo  Raíz del subárbol a destruir.
 */
static void liberar_subarbol(RojoNegro *arbol, NodoRN *nodo);

/**
 * @brief Busca un nodo con el valor dado.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] valor Valor a buscar.
 * @return Puntero al nodo si se encuentra, o al nodo nil si no existe.
 */
static NodoRN *buscar_nodo(const RojoNegro *arbol, int valor);

/**
 * @brief Devuelve el nodo con el valor mínimo del subárbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Raíz del subárbol.
 * @return Puntero al nodo con el valor mínimo.
 */
static NodoRN *minimo_nodo(const RojoNegro *arbol, NodoRN *nodo);

/**
 * @brief Devuelve el nodo con el valor máximo del subárbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Raíz del subárbol.
 * @return Puntero al nodo con el valor máximo.
 */
static NodoRN *maximo_nodo(const RojoNegro *arbol, NodoRN *nodo);

/**
 * @brief Realiza una rotación a la izquierda sobre el nodo x.
 *
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] x     Nodo sobre el que se realiza la rotación.
 *
 * @note Complejidad temporal: O(1).
 */

 static void rotar_izquierda(RojoNegro *arbol, NodoRN *x);
/**
 * @brief Realiza una rotación a la derecha sobre el nodo x.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] x     Nodo sobre el que se realiza la rotación.
 */
static void rotar_derecha(RojoNegro *arbol, NodoRN *x);

/**
 * @brief Corrige violaciones a las propiedades Rojo-Negro después de una inserción.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] z     Nodo recién insertado que puede estar violando reglas.
 */
static void arreglar_insercion(RojoNegro *arbol, NodoRN *z);

/**
 * @brief Reemplaza el subárbol con raíz u por el subárbol con raíz v.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] u     Nodo que será reemplazado.
 * @param[in,out] v     Nodo que tomará el lugar de u.
 */
static void trasplantar(RojoNegro *arbol, NodoRN *u, NodoRN *v);

/**
 * @brief Corrige violaciones a las propiedades Rojo-Negro después de una eliminación.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] x     Nodo auxiliar desde el que se empiezan las correcciones.
 */
static void arreglar_eliminacion(RojoNegro *arbol, NodoRN *x);

/**
 * @brief Calcula recursivamente la altura de un nodo.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Nodo actual.
 * @return La altura del nodo.
 */
static int altura_rec(const RojoNegro *arbol, const NodoRN *nodo);

/**
 * @brief Cuenta recursivamente el número de hojas en el subárbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Nodo actual.
 * @return La cantidad de hojas en el subárbol.
 */
static size_t hojas_rec(const RojoNegro *arbol, const NodoRN *nodo);
static void preorden_rec(const RojoNegro *arbol, const NodoRN *nodo,
                         int nivel, RNVisitador visitar, void *contexto);
static void inorden_rec(const RojoNegro *arbol, const NodoRN *nodo,
                        int nivel, RNVisitador visitar, void *contexto);
static void postorden_rec(const RojoNegro *arbol, const NodoRN *nodo,
                          int nivel, RNVisitador visitar, void *contexto);
static int validar_rec(const RojoNegro *arbol, const NodoRN *nodo,
                       long min, long max, int negros, int *altura_negra);

/**
 * @brief Crea un Árbol Rojo-Negro vacío.
 * @return Puntero a la nueva estructura RojoNegro, o NULL si falla la memoria.
 */
RojoNegro *rn_crear(void)
{
    RojoNegro *arbol = (RojoNegro *)malloc(sizeof(RojoNegro));

    if (arbol == NULL) {
        return NULL;
    }

    arbol->nil = (NodoRN *)malloc(sizeof(NodoRN));
    if (arbol->nil == NULL) {
        free(arbol);
        return NULL;
    }

    arbol->nil->valor = 0;
    arbol->nil->color = COLOR_NEGRO;
    arbol->nil->padre = arbol->nil;
    arbol->nil->izq = arbol->nil;
    arbol->nil->der = arbol->nil;
    arbol->raiz = arbol->nil;
    arbol->tamano = 0U;

    return arbol;
}

/**
 * @brief Destruye el árbol y libera toda su memoria.
 * @param[in,out] arbol Puntero al árbol que se va a destruir.
 */
void rn_destruir(RojoNegro *arbol)
{
    if (arbol == NULL) {
        return;
    }

    liberar_subarbol(arbol, arbol->raiz);
    free(arbol->nil);
    free(arbol);
}

/**
 * @brief Vacía el árbol eliminando todos sus nodos sin destruir la estructura.
 * @param[in,out] arbol Puntero al árbol.
 * @return RN_OK si se vació exitosamente. RN_ERROR_NULO si el árbol es NULL.
 */
RNResultado rn_limpiar(RojoNegro *arbol)
{
    if (arbol == NULL) {
        return RN_ERROR_NULO;
    }

    liberar_subarbol(arbol, arbol->raiz);
    arbol->raiz = arbol->nil;
    arbol->nil->padre = arbol->nil;
    arbol->tamano = 0U;

    return RN_OK;
}

/**
 * @brief Inserta un nuevo valor en el Árbol Rojo-Negro.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in]     valor Entero a insertar.
 * @return RN_OK si se insertó, RN_ERROR_DUPLICADO si ya existía,
 *         o RN_ERROR_MEMORIA si falló malloc.
 */
RNResultado rn_insertar(RojoNegro *arbol, int valor)
{
    NodoRN *padre;
    NodoRN *actual;
    NodoRN *nuevo;

    if (arbol == NULL) {
        return RN_ERROR_NULO;
    }

    padre = arbol->nil;
    actual = arbol->raiz;

    while (actual != arbol->nil) {
        padre = actual;
        if (valor == actual->valor) {
            return RN_ERROR_DUPLICADO;
        }
        actual = (valor < actual->valor) ? actual->izq : actual->der;
    }

    nuevo = crear_nodo(arbol, valor);
    if (nuevo == NULL) {
        return RN_ERROR_MEMORIA;
    }

    nuevo->padre = padre;
    if (padre == arbol->nil) {
        arbol->raiz = nuevo;
    } else if (valor < padre->valor) {
        padre->izq = nuevo;
    } else {
        padre->der = nuevo;
    }

    arreglar_insercion(arbol, nuevo);
    arbol->tamano++;

    return RN_OK;
}

/**
 * @brief Elimina un valor específico del Árbol Rojo-Negro.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in]     valor Entero a eliminar.
 * @return RN_OK si se eliminó, RN_ERROR_NO_EXISTE si no se encontró.
 */
RNResultado rn_eliminar(RojoNegro *arbol, int valor)
{
    NodoRN *z;
    NodoRN *y;
    NodoRN *x;
    ColorRN color_original;

    if (arbol == NULL) {
        return RN_ERROR_NULO;
    }

    z = buscar_nodo(arbol, valor);
    if (z == arbol->nil) {
        return RN_ERROR_NO_EXISTE;
    }

    y = z;
    color_original = y->color;

    if (z->izq == arbol->nil) {
        x = z->der;
        trasplantar(arbol, z, z->der);
    } else if (z->der == arbol->nil) {
        x = z->izq;
        trasplantar(arbol, z, z->izq);
    } else {
        y = minimo_nodo(arbol, z->der);
        color_original = y->color;
        x = y->der;

        if (y->padre == z) {
            x->padre = y;
        } else {
            trasplantar(arbol, y, y->der);
            y->der = z->der;
            y->der->padre = y;
        }

        trasplantar(arbol, z, y);
        y->izq = z->izq;
        y->izq->padre = y;
        y->color = z->color;
    }

    free(z);
    arbol->tamano--;

    if (color_original == COLOR_NEGRO) {
        arreglar_eliminacion(arbol, x);
    }

    if (arbol->raiz != arbol->nil) {
        arbol->raiz->color = COLOR_NEGRO;
    }

    return RN_OK;
}

/**
 * @brief Comprueba si un valor existe en el Árbol Rojo-Negro.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] valor Entero a buscar.
 * @return 1 si lo encuentra, 0 si no existe o el árbol es NULL.
 */
int rn_contiene(const RojoNegro *arbol, int valor)
{
    if (arbol == NULL) {
        return 0;
    }

    return buscar_nodo(arbol, valor) != arbol->nil;
}

/**
 * @brief Verifica si el árbol está vacío.
 * @param[in] arbol Puntero constante al árbol.
 * @return 1 si está vacío o es NULL, 0 en caso contrario.
 */
int rn_esta_vacio(const RojoNegro *arbol)
{
    return (arbol == NULL || arbol->tamano == 0U) ? 1 : 0;
}

/**
 * @brief Obtiene el número total de nodos en el árbol.
 * @param[in] arbol Puntero constante al árbol.
 * @return El número de nodos.
 */
size_t rn_tamano(const RojoNegro *arbol)
{
    return (arbol == NULL) ? 0U : arbol->tamano;
}

/**
 * @brief Obtiene el valor mínimo del Árbol Rojo-Negro.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[out] salida Puntero donde se almacenará el mínimo.
 * @return RN_OK si se obtuvo el mínimo, RN_ERROR_VACIO si está vacío.
 */
RNResultado rn_minimo(const RojoNegro *arbol, int *salida)
{
    NodoRN *minimo;

    if (arbol == NULL || salida == NULL) {
        return RN_ERROR_NULO;
    }
    if (arbol->raiz == arbol->nil) {
        return RN_ERROR_VACIO;
    }

    minimo = minimo_nodo(arbol, arbol->raiz);
    *salida = minimo->valor;

    return RN_OK;
}

/**
 * @brief Obtiene el valor máximo del Árbol Rojo-Negro.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[out] salida Puntero donde se almacenará el máximo.
 * @return RN_OK si se obtuvo el máximo, RN_ERROR_VACIO si está vacío.
 */
RNResultado rn_maximo(const RojoNegro *arbol, int *salida)
{
    NodoRN *maximo;

    if (arbol == NULL || salida == NULL) {
        return RN_ERROR_NULO;
    }
    if (arbol->raiz == arbol->nil) {
        return RN_ERROR_VACIO;
    }

    maximo = maximo_nodo(arbol, arbol->raiz);
    *salida = maximo->valor;

    return RN_OK;
}

/**
 * @brief Obtiene la altura del árbol (incluyendo nodos nil como fin).
 * @param[in] arbol Puntero constante al árbol.
 * @return La altura del árbol, o 0 si está vacío.
 */
int rn_altura(const RojoNegro *arbol)
{
    if (arbol == NULL) {
        return 0;
    }

    return altura_rec(arbol, arbol->raiz);
}

/**
 * @brief Cuenta la cantidad de nodos hoja en el árbol (sin contar el nil).
 * @param[in] arbol Puntero constante al árbol.
 * @return Número de hojas.
 */
size_t rn_contar_hojas(const RojoNegro *arbol)
{
    if (arbol == NULL) {
        return 0U;
    }

    return hojas_rec(arbol, arbol->raiz);
}

/**
 * @brief Ejecuta un recorrido preorden y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitar   Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return RN_OK si se recorrió correctamente.
 */
RNResultado rn_recorrer_preorden(const RojoNegro *arbol, RNVisitador visitar, void *contexto)
{
    if (arbol == NULL || visitar == NULL) {
        return RN_ERROR_NULO;
    }

    preorden_rec(arbol, arbol->raiz, 0, visitar, contexto);
    return RN_OK;
}

/**
 * @brief Ejecuta un recorrido inorden y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitar   Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return RN_OK si se recorrió correctamente.
 */
RNResultado rn_recorrer_inorden(const RojoNegro *arbol, RNVisitador visitar, void *contexto)
{
    if (arbol == NULL || visitar == NULL) {
        return RN_ERROR_NULO;
    }

    inorden_rec(arbol, arbol->raiz, 0, visitar, contexto);
    return RN_OK;
}

/**
 * @brief Ejecuta un recorrido postorden y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitar   Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return RN_OK si se recorrió correctamente.
 */
RNResultado rn_recorrer_postorden(const RojoNegro *arbol, RNVisitador visitar, void *contexto)
{
    if (arbol == NULL || visitar == NULL) {
        return RN_ERROR_NULO;
    }

    postorden_rec(arbol, arbol->raiz, 0, visitar, contexto);
    return RN_OK;
}

/**
 * @brief Ejecuta un recorrido por niveles (BFS) y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitar   Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return RN_OK si se recorrió correctamente. RN_ERROR_MEMORIA si falla la cola interna.
 */
RNResultado rn_recorrer_niveles(const RojoNegro *arbol, RNVisitador visitar, void *contexto)
{
    typedef struct ElementoCola {
        const NodoRN *nodo;
        int nivel;
    } ElementoCola;

    ElementoCola *cola;
    size_t frente;
    size_t fin;

    if (arbol == NULL || visitar == NULL) {
        return RN_ERROR_NULO;
    }
    if (arbol->raiz == arbol->nil) {
        return RN_OK;
    }

    cola = (ElementoCola *)malloc(arbol->tamano * sizeof(ElementoCola));
    if (cola == NULL) {
        return RN_ERROR_MEMORIA;
    }

    frente = 0U;
    fin = 0U;
    cola[fin].nodo = arbol->raiz;
    cola[fin].nivel = 0;
    fin++;

    while (frente < fin) {
        const NodoRN *actual = cola[frente].nodo;
        int nivel = cola[frente].nivel;
        frente++;

        visitar(actual->valor, nivel,
                actual->color == COLOR_ROJO ? 1 : 0,
                contexto);

        if (actual->izq != arbol->nil) {
            cola[fin].nodo = actual->izq;
            cola[fin].nivel = nivel + 1;
            fin++;
        }
        if (actual->der != arbol->nil) {
            cola[fin].nodo = actual->der;
            cola[fin].nivel = nivel + 1;
            fin++;
        }
    }

    free(cola);
    return RN_OK;
}

/**
 * @brief Valida que la estructura cumpla estrictamente las propiedades del Árbol Rojo-Negro.
 * @param[in] arbol Puntero constante al árbol.
 * @return 1 si es un RN válido, 0 si hay violaciones.
 */
int rn_es_valido(const RojoNegro *arbol)
{
    int altura_negra;

    if (arbol == NULL || arbol->nil == NULL) {
        return 0;
    }
    if (arbol->raiz == arbol->nil) {
        return 1;
    }
    if (arbol->raiz->color != COLOR_NEGRO) {
        return 0;
    }

    altura_negra = -1;
    return validar_rec(arbol, arbol->raiz, LONG_MIN, LONG_MAX, 0,
                       &altura_negra);
}

/**
 * @brief Función recursiva para imprimir el árbol Rojo-Negro gráficamente.
 * @param[in] arbol Puntero al árbol (usado para chequear nil).
 * @param[in] nodo  Puntero al nodo actual.
 * @param[in] n     Profundidad actual.
 */
static void imprimir_rn_rec(const RojoNegro *arbol, NodoRN *nodo, int n) {
    if (nodo == arbol->nil || nodo == NULL) return;
    
    imprimir_rn_rec(arbol, nodo->der, n + 1);
    
    for (int i = 0; i < n; i++) {
        printf("    ");
    }
    
    // Usar códigos ANSI para colores en consola. Rojo = \033[31m, Gris oscuro = \033[90m
    if (nodo->color == COLOR_ROJO) {
        printf("\033[31m%d\033[0m\n", nodo->valor);
    } else {
        printf("\033[90m%d\033[0m\n", nodo->valor);
    }
    
    imprimir_rn_rec(arbol, nodo->izq, n + 1);
}

/**
 * @brief Imprime una representación gráfica del árbol RN en consola.
 * @param[in] arbol Puntero constante al árbol.
 */
void rn_imprimir_arbol(const RojoNegro *arbol) {
    if (!arbol || arbol->raiz == arbol->nil) {
        printf("Arbol vacio\n");
        return;
    }
    imprimir_rn_rec(arbol, arbol->raiz, 0);
}

/**
 * @brief Crea un nuevo nodo Rojo-Negro.
 * @param[in,out] arbol Puntero al árbol (usado para la referencia al nodo nil).
 * @param[in]     valor Entero a insertar en el nodo.
 * @return Puntero al nuevo nodo creado (color rojo por defecto), o NULL si no hay memoria.
 */
static NodoRN *crear_nodo(RojoNegro *arbol, int valor)
{
    NodoRN *nodo = (NodoRN *)malloc(sizeof(NodoRN));

    if (nodo == NULL) {
        return NULL;
    }

    nodo->valor = valor;
    nodo->color = COLOR_ROJO;
    nodo->padre = arbol->nil;
    nodo->izq = arbol->nil;
    nodo->der = arbol->nil;

    return nodo;
}

/**
 * @brief Libera la memoria de todos los nodos en el subárbol dado.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] nodo  Raíz del subárbol a destruir.
 */
static void liberar_subarbol(RojoNegro *arbol, NodoRN *nodo)
{
    if (nodo == arbol->nil) {
        return;
    }

    liberar_subarbol(arbol, nodo->izq);
    liberar_subarbol(arbol, nodo->der);
    free(nodo);
}

/**
 * @brief Busca un nodo con el valor dado.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] valor Valor a buscar.
 * @return Puntero al nodo si se encuentra, o al nodo nil si no existe.
 */
static NodoRN *buscar_nodo(const RojoNegro *arbol, int valor)
{
    NodoRN *actual = arbol->raiz;

    while (actual != arbol->nil && valor != actual->valor) {
        actual = (valor < actual->valor) ? actual->izq : actual->der;
    }

    return actual;
}

/**
 * @brief Devuelve el nodo con el valor mínimo del subárbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Raíz del subárbol.
 * @return Puntero al nodo con el valor mínimo.
 */
static NodoRN *minimo_nodo(const RojoNegro *arbol, NodoRN *nodo)
{
    while (nodo->izq != arbol->nil) {
        nodo = nodo->izq;
    }

    return nodo;
}

/**
 * @brief Devuelve el nodo con el valor máximo del subárbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Raíz del subárbol.
 * @return Puntero al nodo con el valor máximo.
 */
static NodoRN *maximo_nodo(const RojoNegro *arbol, NodoRN *nodo)
{
    while (nodo->der != arbol->nil) {
        nodo = nodo->der;
    }

    return nodo;
}

/**
 * @brief Realiza una rotación a la izquierda sobre el nodo x.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] x     Nodo sobre el que se realiza la rotación.
 */
static void rotar_izquierda(RojoNegro *arbol, NodoRN *x)
{
    NodoRN *y = x->der;

    x->der = y->izq;
    if (y->izq != arbol->nil) {
        y->izq->padre = x;
    }

    y->padre = x->padre;
    if (x->padre == arbol->nil) {
        arbol->raiz = y;
    } else if (x == x->padre->izq) {
        x->padre->izq = y;
    } else {
        x->padre->der = y;
    }

    y->izq = x;
    x->padre = y;
}

/**
 * @brief Realiza una rotación a la derecha sobre el nodo x.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] x     Nodo sobre el que se realiza la rotación.
 */
static void rotar_derecha(RojoNegro *arbol, NodoRN *x)
{
    NodoRN *y = x->izq;

    x->izq = y->der;
    if (y->der != arbol->nil) {
        y->der->padre = x;
    }

    y->padre = x->padre;
    if (x->padre == arbol->nil) {
        arbol->raiz = y;
    } else if (x == x->padre->der) {
        x->padre->der = y;
    } else {
        x->padre->izq = y;
    }

    y->der = x;
    x->padre = y;
}

/**
 * @brief Corrige violaciones a las propiedades Rojo-Negro después de una inserción.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] z     Nodo recién insertado que puede estar violando reglas.
 */
static void arreglar_insercion(RojoNegro *arbol, NodoRN *z)
{
    while (z->padre->color == COLOR_ROJO) {
        if (z->padre == z->padre->padre->izq) {
            NodoRN *y = z->padre->padre->der;

            if (y->color == COLOR_ROJO) {
                z->padre->color = COLOR_NEGRO;
                y->color = COLOR_NEGRO;
                z->padre->padre->color = COLOR_ROJO;
                z = z->padre->padre;
            } else {
                if (z == z->padre->der) {
                    z = z->padre;
                    rotar_izquierda(arbol, z);
                }
                z->padre->color = COLOR_NEGRO;
                z->padre->padre->color = COLOR_ROJO;
                rotar_derecha(arbol, z->padre->padre);
            }
        } else {
            NodoRN *y = z->padre->padre->izq;

            if (y->color == COLOR_ROJO) {
                z->padre->color = COLOR_NEGRO;
                y->color = COLOR_NEGRO;
                z->padre->padre->color = COLOR_ROJO;
                z = z->padre->padre;
            } else {
                if (z == z->padre->izq) {
                    z = z->padre;
                    rotar_derecha(arbol, z);
                }
                z->padre->color = COLOR_NEGRO;
                z->padre->padre->color = COLOR_ROJO;
                rotar_izquierda(arbol, z->padre->padre);
            }
        }
    }

    arbol->raiz->color = COLOR_NEGRO;
}

/**
 * @brief Reemplaza el subárbol con raíz u por el subárbol con raíz v.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] u     Nodo que será reemplazado.
 * @param[in,out] v     Nodo que tomará el lugar de u.
 */
static void trasplantar(RojoNegro *arbol, NodoRN *u, NodoRN *v)
{
    if (u->padre == arbol->nil) {
        arbol->raiz = v;
    } else if (u == u->padre->izq) {
        u->padre->izq = v;
    } else {
        u->padre->der = v;
    }

    v->padre = u->padre;
}

/**
 * @brief Corrige violaciones a las propiedades Rojo-Negro después de una eliminación.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in,out] x     Nodo auxiliar desde el que se empiezan las correcciones.
 */
static void arreglar_eliminacion(RojoNegro *arbol, NodoRN *x)
{
    while (x != arbol->raiz && x->color == COLOR_NEGRO) {
        if (x == x->padre->izq) {
            NodoRN *w = x->padre->der;

            if (w->color == COLOR_ROJO) {
                w->color = COLOR_NEGRO;
                x->padre->color = COLOR_ROJO;
                rotar_izquierda(arbol, x->padre);
                w = x->padre->der;
            }
            if (w->izq->color == COLOR_NEGRO &&
                w->der->color == COLOR_NEGRO) {
                w->color = COLOR_ROJO;
                x = x->padre;
            } else {
                if (w->der->color == COLOR_NEGRO) {
                    w->izq->color = COLOR_NEGRO;
                    w->color = COLOR_ROJO;
                    rotar_derecha(arbol, w);
                    w = x->padre->der;
                }
                w->color = x->padre->color;
                x->padre->color = COLOR_NEGRO;
                w->der->color = COLOR_NEGRO;
                rotar_izquierda(arbol, x->padre);
                x = arbol->raiz;
            }
        } else {
            NodoRN *w = x->padre->izq;

            if (w->color == COLOR_ROJO) {
                w->color = COLOR_NEGRO;
                x->padre->color = COLOR_ROJO;
                rotar_derecha(arbol, x->padre);
                w = x->padre->izq;
            }
            if (w->der->color == COLOR_NEGRO &&
                w->izq->color == COLOR_NEGRO) {
                w->color = COLOR_ROJO;
                x = x->padre;
            } else {
                if (w->izq->color == COLOR_NEGRO) {
                    w->der->color = COLOR_NEGRO;
                    w->color = COLOR_ROJO;
                    rotar_izquierda(arbol, w);
                    w = x->padre->izq;
                }
                w->color = x->padre->color;
                x->padre->color = COLOR_NEGRO;
                w->izq->color = COLOR_NEGRO;
                rotar_derecha(arbol, x->padre);
                x = arbol->raiz;
            }
        }
    }

    x->color = COLOR_NEGRO;
}

/**
 * @brief Calcula recursivamente la altura de un nodo.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Nodo actual.
 * @return La altura del nodo.
 */
static int altura_rec(const RojoNegro *arbol, const NodoRN *nodo)
{
    int izquierda;
    int derecha;

    if (nodo == arbol->nil) {
        return 0;
    }

    izquierda = altura_rec(arbol, nodo->izq);
    derecha = altura_rec(arbol, nodo->der);

    return (izquierda > derecha ? izquierda : derecha) + 1;
}

/**
 * @brief Cuenta recursivamente el número de hojas en el subárbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] nodo  Nodo actual.
 * @return La cantidad de hojas en el subárbol.
 */
static size_t hojas_rec(const RojoNegro *arbol, const NodoRN *nodo)
{
    if (nodo == arbol->nil) {
        return 0U;
    }
    if (nodo->izq == arbol->nil && nodo->der == arbol->nil) {
        return 1U;
    }

    return hojas_rec(arbol, nodo->izq) + hojas_rec(arbol, nodo->der);
}

static void preorden_rec(const RojoNegro *arbol, const NodoRN *nodo,
                         int nivel, RNVisitador visitar, void *contexto)
{
    if (nodo == arbol->nil) {
        return;
    }

    visitar(nodo->valor, nivel, nodo->color == COLOR_ROJO ? 1 : 0, contexto);
    preorden_rec(arbol, nodo->izq, nivel + 1, visitar, contexto);
    preorden_rec(arbol, nodo->der, nivel + 1, visitar, contexto);
}

static void inorden_rec(const RojoNegro *arbol, const NodoRN *nodo,
                        int nivel, RNVisitador visitar, void *contexto)
{
    if (nodo == arbol->nil) {
        return;
    }

    inorden_rec(arbol, nodo->izq, nivel + 1, visitar, contexto);
    visitar(nodo->valor, nivel, nodo->color == COLOR_ROJO ? 1 : 0, contexto);
    inorden_rec(arbol, nodo->der, nivel + 1, visitar, contexto);
}

static void postorden_rec(const RojoNegro *arbol, const NodoRN *nodo,
                          int nivel, RNVisitador visitar, void *contexto)
{
    if (nodo == arbol->nil) {
        return;
    }

    postorden_rec(arbol, nodo->izq, nivel + 1, visitar, contexto);
    postorden_rec(arbol, nodo->der, nivel + 1, visitar, contexto);
    visitar(nodo->valor, nivel, nodo->color == COLOR_ROJO ? 1 : 0, contexto);
}

static int validar_rec(const RojoNegro *arbol, const NodoRN *nodo,
                       long min, long max, int negros, int *altura_negra)
{
    if (nodo == arbol->nil) {
        negros++;
        if (*altura_negra == -1) {
            *altura_negra = negros;
            return 1;
        }
        return negros == *altura_negra;
    }

    if ((long)nodo->valor <= min || (long)nodo->valor >= max) {
        return 0;
    }

    if (nodo->color == COLOR_NEGRO) {
        negros++;
    } else {
        if (nodo->izq->color != COLOR_NEGRO ||
            nodo->der->color != COLOR_NEGRO) {
            return 0;
        }
    }

    if (nodo->izq != arbol->nil && nodo->izq->padre != nodo) {
        return 0;
    }
    if (nodo->der != arbol->nil && nodo->der->padre != nodo) {
        return 0;
    }

    return validar_rec(arbol, nodo->izq, min, nodo->valor,
                       negros, altura_negra) &&
           validar_rec(arbol, nodo->der, nodo->valor, max,
                       negros, altura_negra);
}
