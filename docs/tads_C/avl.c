/**
 * @file avl.c
 * @brief Implementacion encapsulada del TAD Arbol AVL en C estandar.
 */

#include "avl.h"

#include <limits.h>
#include <stdlib.h>
#include <stdio.h>

/**
 * @brief Nodo interno del arbol AVL.
 */
typedef struct NodoAvl {
    int valor;
    int altura;
    struct NodoAvl *izquierdo;
    struct NodoAvl *derecho;
} NodoAvl;

/**
 * @brief Estructura principal del AVL.
 */
struct Avl {
    NodoAvl *raiz;
    size_t tamano;
};

/**
 * @brief Devuelve el máximo entre dos enteros.
 * @param[in] a Primer entero.
 * @param[in] b Segundo entero.
 * @return El valor máximo entre a y b.
 */
static int maximo_int(int a, int b)
{
    return (a > b) ? a : b;
}

/**
 * @brief Obtiene la altura de un nodo de forma segura.
 * @param[in] nodo Puntero constante al nodo.
 * @return La altura del nodo, o 0 si el nodo es NULL.
 */
static int altura_nodo(const NodoAvl *nodo)
{
    return (nodo == NULL) ? 0 : nodo->altura;
}

/**
 * @brief Calcula el factor de equilibrio de un nodo.
 * @param[in] nodo Puntero constante al nodo.
 * @return La diferencia de altura entre el subárbol izquierdo y el derecho.
 */
static int factor_nodo(const NodoAvl *nodo)
{
    if (nodo == NULL) {
        return 0;
    }

    return altura_nodo(nodo->izquierdo) - altura_nodo(nodo->derecho);
}

/**
 * @brief Actualiza la altura de un nodo basándose en sus hijos.
 * @param[in,out] nodo Puntero al nodo cuya altura se actualizará.
 */
static void actualizar_altura(NodoAvl *nodo)
{
    if (nodo != NULL) {
        nodo->altura = 1 + maximo_int(altura_nodo(nodo->izquierdo),
                                      altura_nodo(nodo->derecho));
    }
}

/**
 * @brief Crea un nuevo nodo de AVL.
 * @param[in] valor Valor entero a almacenar.
 * @return Puntero al nuevo nodo, o NULL si falla la asignación de memoria.
 */
static NodoAvl *crear_nodo(int valor)
{
    NodoAvl *nuevo = (NodoAvl *)malloc(sizeof(NodoAvl));

    if (nuevo == NULL) {
        return NULL;
    }

    nuevo->valor = valor;
    nuevo->altura = 1;
    nuevo->izquierdo = NULL;
    nuevo->derecho = NULL;

    return nuevo;
}

/**
 * @brief Realiza una rotación simple a la derecha.
 * @param[in,out] y Puntero al nodo desbalanceado.
 * @return Puntero a la nueva raíz del subárbol tras la rotación.
 */
static NodoAvl *rotar_derecha(NodoAvl *y)
{
    NodoAvl *x;
    NodoAvl *t2;

    if (y == NULL || y->izquierdo == NULL) {
        return y;
    }

    x = y->izquierdo;
    t2 = x->derecho;

    x->derecho = y;
    y->izquierdo = t2;

    actualizar_altura(y);
    actualizar_altura(x);

    return x;
}

/**
 * @brief Realiza una rotación simple a la izquierda.
 * @param[in,out] x Puntero al nodo desbalanceado.
 * @return Puntero a la nueva raíz del subárbol tras la rotación.
 */
static NodoAvl *rotar_izquierda(NodoAvl *x)
{
    NodoAvl *y;
    NodoAvl *t2;

    if (x == NULL || x->derecho == NULL) {
        return x;
    }

    y = x->derecho;
    t2 = y->izquierdo;

    y->izquierdo = x;
    x->derecho = t2;

    actualizar_altura(x);
    actualizar_altura(y);

    return y;
}

/**
 * @brief Balancea un nodo si su factor de equilibrio está fuera del rango [-1, 1].
 * @param[in,out] nodo Puntero al nodo a balancear.
 * @return Puntero a la nueva raíz del subárbol balanceado.
 */
static NodoAvl *balancear(NodoAvl *nodo)
{
    int factor;

    if (nodo == NULL) {
        return NULL;
    }

    actualizar_altura(nodo);
    factor = factor_nodo(nodo);

    if (factor > 1) {
        if (factor_nodo(nodo->izquierdo) < 0) {
            nodo->izquierdo = rotar_izquierda(nodo->izquierdo);
        }
        return rotar_derecha(nodo);
    }

    if (factor < -1) {
        if (factor_nodo(nodo->derecho) > 0) {
            nodo->derecho = rotar_derecha(nodo->derecho);
        }
        return rotar_izquierda(nodo);
    }

    return nodo;
}

/**
 * @brief Función recursiva para insertar un valor en el AVL.
 * @param[in,out] nodo      Puntero a la raíz del subárbol actual.
 * @param[in]     valor     Valor entero a insertar.
 * @param[out]    resultado Código de resultado de la operación.
 * @return Puntero a la raíz del subárbol actualizado y balanceado.
 */
static NodoAvl *insertar_rec(NodoAvl *nodo, int valor, AvlResultado *resultado)
{
    if (nodo == NULL) {
        NodoAvl *nuevo = crear_nodo(valor);

        if (nuevo == NULL) {
            *resultado = AVL_ERROR_MEMORIA;
            return NULL;
        }

        *resultado = AVL_OK;
        return nuevo;
    }

    if (valor < nodo->valor) {
        nodo->izquierdo = insertar_rec(nodo->izquierdo, valor, resultado);
    } else if (valor > nodo->valor) {
        nodo->derecho = insertar_rec(nodo->derecho, valor, resultado);
    } else {
        *resultado = AVL_ERROR_DUPLICADO;
        return nodo;
    }

    if (*resultado != AVL_OK) {
        return nodo;
    }

    return balancear(nodo);
}

/**
 * @brief Obtiene el nodo con el valor mínimo de un subárbol.
 * @param[in] nodo Puntero a la raíz del subárbol.
 * @return Puntero al nodo con el valor más pequeño.
 */
static NodoAvl *minimo_nodo(NodoAvl *nodo)
{
    while (nodo != NULL && nodo->izquierdo != NULL) {
        nodo = nodo->izquierdo;
    }

    return nodo;
}

/**
 * @brief Obtiene el nodo con el valor máximo de un subárbol.
 * @param[in] nodo Puntero a la raíz del subárbol.
 * @return Puntero al nodo con el valor más grande.
 */
static NodoAvl *maximo_nodo(NodoAvl *nodo)
{
    while (nodo != NULL && nodo->derecho != NULL) {
        nodo = nodo->derecho;
    }

    return nodo;
}

/**
 * @brief Función recursiva para eliminar un valor en el AVL.
 * @param[in,out] raiz      Puntero a la raíz del subárbol actual.
 * @param[in]     valor     Valor entero a eliminar.
 * @param[out]    resultado Código de resultado de la operación.
 * @return Puntero a la raíz del subárbol actualizado y balanceado.
 * @note Complejidad temporal: O(log n).
 */
static NodoAvl *eliminar_rec(NodoAvl *raiz, int valor, AvlResultado *resultado)
{
    if (raiz == NULL) {
        *resultado = AVL_ERROR_NO_EXISTE;
        return NULL;
    }

    if (valor < raiz->valor) {
        raiz->izquierdo = eliminar_rec(raiz->izquierdo, valor, resultado);
    } else if (valor > raiz->valor) {
        raiz->derecho = eliminar_rec(raiz->derecho, valor, resultado);
    } else {
        *resultado = AVL_OK;

        if (raiz->izquierdo == NULL || raiz->derecho == NULL) {
            NodoAvl *hijo = (raiz->izquierdo != NULL) ? raiz->izquierdo : raiz->derecho;
            free(raiz);
            return hijo;
        } else {
            NodoAvl *sucesor = minimo_nodo(raiz->derecho);
            raiz->valor = sucesor->valor;
            raiz->derecho = eliminar_rec(raiz->derecho, sucesor->valor, resultado);
            *resultado = AVL_OK;
        }
    }

    if (*resultado != AVL_OK || raiz == NULL) {
        return raiz;
    }

    return balancear(raiz);
}

/**
 * @brief Función recursiva que verifica si un valor existe.
 * @param[in] nodo  Puntero constante al nodo actual.
 * @param[in] valor Valor entero a buscar.
 * @return 1 si lo encuentra, 0 si no.
 */
static int contiene_rec(const NodoAvl *nodo, int valor)
{
    while (nodo != NULL) {
        if (valor == nodo->valor) {
            return 1;
        }

        nodo = (valor < nodo->valor) ? nodo->izquierdo : nodo->derecho;
    }

    return 0;
}

/**
 * @brief Función recursiva que busca y devuelve el nodo con un valor dado.
 * @param[in] nodo  Puntero constante al nodo actual.
 * @param[in] valor Valor entero a buscar.
 * @return Puntero constante al nodo si lo encuentra, NULL si no.
 */
static const NodoAvl *buscar_nodo(const NodoAvl *nodo, int valor)
{
    while (nodo != NULL) {
        if (valor == nodo->valor) {
            return nodo;
        }

        nodo = (valor < nodo->valor) ? nodo->izquierdo : nodo->derecho;
    }

    return NULL;
}

/**
 * @brief Libera recursivamente todos los nodos de un subárbol.
 * @param[in,out] nodo Puntero al nodo a destruir.
 */
static void destruir_rec(NodoAvl *nodo)
{
    if (nodo == NULL) {
        return;
    }

    destruir_rec(nodo->izquierdo);
    destruir_rec(nodo->derecho);
    free(nodo);
}

/**
 * @brief Cuenta recursivamente las hojas de un subárbol.
 * @param[in] nodo Puntero constante al nodo actual.
 * @return El número de hojas.
 */
static size_t contar_hojas_rec(const NodoAvl *nodo)
{
    if (nodo == NULL) {
        return 0U;
    }

    if (nodo->izquierdo == NULL && nodo->derecho == NULL) {
        return 1U;
    }

    return contar_hojas_rec(nodo->izquierdo) + contar_hojas_rec(nodo->derecho);
}

/**
 * @brief Realiza un recorrido preorden recursivo.
 * @param[in] nodo      Puntero constante al nodo actual.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Contexto del usuario.
 */
static void preorden_rec(const NodoAvl *nodo, AvlVisitante visitante, void *contexto)
{
    if (nodo == NULL) {
        return;
    }

    visitante(nodo->valor, contexto);
    preorden_rec(nodo->izquierdo, visitante, contexto);
    preorden_rec(nodo->derecho, visitante, contexto);
}

/**
 * @brief Realiza un recorrido inorden recursivo.
 * @param[in] nodo      Puntero constante al nodo actual.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Contexto del usuario.
 */
static void inorden_rec(const NodoAvl *nodo, AvlVisitante visitante, void *contexto)
{
    if (nodo == NULL) {
        return;
    }

    inorden_rec(nodo->izquierdo, visitante, contexto);
    visitante(nodo->valor, contexto);
    inorden_rec(nodo->derecho, visitante, contexto);
}

/**
 * @brief Realiza un recorrido postorden recursivo.
 * @param[in] nodo      Puntero constante al nodo actual.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Contexto del usuario.
 */
static void postorden_rec(const NodoAvl *nodo, AvlVisitante visitante, void *contexto)
{
    if (nodo == NULL) {
        return;
    }

    postorden_rec(nodo->izquierdo, visitante, contexto);
    postorden_rec(nodo->derecho, visitante, contexto);
    visitante(nodo->valor, contexto);
}

/**
 * @brief Valida recursivamente si el subárbol cumple las reglas del AVL.
 * @param[in]  nodo   Puntero constante al nodo actual.
 * @param[in]  minimo Límite inferior permitido para el valor.
 * @param[in]  maximo Límite superior permitido para el valor.
 * @param[out] altura Puntero para almacenar la altura verificada.
 * @return 1 si el subárbol es un AVL válido, 0 en caso contrario.
 */
static int validar_rec(const NodoAvl *nodo, long minimo, long maximo, int *altura)
{
    int altura_izq;
    int altura_der;
    int balance;

    if (nodo == NULL) {
        *altura = 0;
        return 1;
    }

    if ((long)nodo->valor <= minimo || (long)nodo->valor >= maximo) {
        return 0;
    }

    if (!validar_rec(nodo->izquierdo, minimo, (long)nodo->valor, &altura_izq)) {
        return 0;
    }

    if (!validar_rec(nodo->derecho, (long)nodo->valor, maximo, &altura_der)) {
        return 0;
    }

    balance = altura_izq - altura_der;
    *altura = 1 + maximo_int(altura_izq, altura_der);

    if (nodo->altura != *altura) {
        return 0;
    }

    return balance >= -1 && balance <= 1;
}

/**
 * @brief Crea un Árbol AVL vacío.
 * @return Puntero a la nueva estructura Avl, o NULL si falla la memoria.
 */
Avl *avl_crear(void)
{
    Avl *arbol = (Avl *)malloc(sizeof(Avl));

    if (arbol == NULL) {
        return NULL;
    }

    arbol->raiz = NULL;
    arbol->tamano = 0U;

    return arbol;
}

/**
 * @brief Destruye el árbol y libera toda su memoria.
 * @param[in,out] arbol Puntero al árbol que se va a destruir.
 */
void avl_destruir(Avl *arbol)
{
    if (arbol == NULL) {
        return;
    }

    destruir_rec(arbol->raiz);
    free(arbol);
}

/**
 * @brief Vacía el árbol eliminando todos sus nodos sin destruir la estructura.
 * @param[in,out] arbol Puntero al árbol.
 * @return AVL_OK si se vació exitosamente. AVL_ERROR_NULL si el árbol es NULL.
 */
AvlResultado avl_vaciar(Avl *arbol)
{
    if (arbol == NULL) {
        return AVL_ERROR_NULL;
    }

    destruir_rec(arbol->raiz);
    arbol->raiz = NULL;
    arbol->tamano = 0U;

    return AVL_OK;
}

/**
 * @brief Inserta un nuevo valor en el AVL y lo balancea.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in]     valor Entero a insertar.
 * @return AVL_OK si se insertó, AVL_ERROR_DUPLICADO si ya existía,
 *         o AVL_ERROR_MEMORIA si falló malloc.
 */
AvlResultado avl_insertar(Avl *arbol, int valor)
{
    AvlResultado resultado;

    if (arbol == NULL) {
        return AVL_ERROR_NULL;
    }

    resultado = AVL_OK;
    arbol->raiz = insertar_rec(arbol->raiz, valor, &resultado);

    if (resultado == AVL_OK) {
        arbol->tamano++;
    }

    return resultado;
}

/**
 * @brief Elimina un valor específico del AVL y lo balancea.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in]     valor Entero a eliminar.
 * @return AVL_OK si se eliminó, AVL_ERROR_NO_EXISTE si no se encontró.
 */
AvlResultado avl_eliminar(Avl *arbol, int valor)
{
    AvlResultado resultado;

    if (arbol == NULL) {
        return AVL_ERROR_NULL;
    }

    resultado = AVL_OK;
    arbol->raiz = eliminar_rec(arbol->raiz, valor, &resultado);

    if (resultado == AVL_OK && arbol->tamano > 0U) {
        arbol->tamano--;
    }

    return resultado;
}

/**
 * @brief Comprueba si un valor existe en el árbol AVL.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] valor Entero a buscar.
 * @return 1 si lo encuentra, 0 si no existe o el árbol es NULL.
 */
int avl_contiene(const Avl *arbol, int valor)
{
    if (arbol == NULL) {
        return 0;
    }

    return contiene_rec(arbol->raiz, valor);
}

/**
 * @brief Obtiene el valor mínimo del árbol AVL.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[out] salida Puntero donde se almacenará el mínimo.
 * @return AVL_OK si se obtuvo el mínimo, AVL_ERROR_VACIO si está vacío.
 */
AvlResultado avl_minimo(const Avl *arbol, int *salida)
{
    NodoAvl *nodo;

    if (arbol == NULL || salida == NULL) {
        return AVL_ERROR_NULL;
    }

    if (arbol->raiz == NULL) {
        return AVL_ERROR_VACIO;
    }

    nodo = minimo_nodo(arbol->raiz);
    *salida = nodo->valor;

    return AVL_OK;
}

/**
 * @brief Obtiene el valor máximo del árbol AVL.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[out] salida Puntero donde se almacenará el máximo.
 * @return AVL_OK si se obtuvo el máximo, AVL_ERROR_VACIO si está vacío.
 */
AvlResultado avl_maximo(const Avl *arbol, int *salida)
{
    NodoAvl *nodo;

    if (arbol == NULL || salida == NULL) {
        return AVL_ERROR_NULL;
    }

    if (arbol->raiz == NULL) {
        return AVL_ERROR_VACIO;
    }

    nodo = maximo_nodo(arbol->raiz);
    *salida = nodo->valor;

    return AVL_OK;
}

/**
 * @brief Obtiene la altura del árbol AVL.
 * @param[in] arbol Puntero constante al árbol.
 * @return La altura del árbol, o 0 si está vacío.
 */
int avl_altura(const Avl *arbol)
{
    if (arbol == NULL) {
        return 0;
    }

    return altura_nodo(arbol->raiz);
}

/**
 * @brief Obtiene el número total de nodos en el árbol.
 * @param[in] arbol Puntero constante al árbol.
 * @return El número de nodos.
 */
size_t avl_tamano(const Avl *arbol)
{
    return (arbol == NULL) ? 0U : arbol->tamano;
}

/**
 * @brief Verifica si el árbol AVL está vacío.
 * @param[in] arbol Puntero constante al árbol.
 * @return 1 si está vacío o es NULL, 0 en caso contrario.
 */
int avl_esta_vacio(const Avl *arbol)
{
    return arbol == NULL || arbol->raiz == NULL;
}

/**
 * @brief Cuenta la cantidad de nodos hoja en el AVL.
 * @param[in] arbol Puntero constante al árbol.
 * @return Número de hojas.
 */
size_t avl_contar_hojas(const Avl *arbol)
{
    if (arbol == NULL) {
        return 0U;
    }

    return contar_hojas_rec(arbol->raiz);
}

/**
 * @brief Obtiene el factor de equilibrio de un nodo específico por su valor.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[in]  valor  Valor del nodo a consultar.
 * @param[out] salida Puntero donde se almacenará el factor de equilibrio.
 * @return AVL_OK si se encontró, AVL_ERROR_NO_EXISTE si no se encuentra.
 */
AvlResultado avl_factor_equilibrio(const Avl *arbol, int valor, int *salida)
{
    const NodoAvl *nodo;

    if (arbol == NULL || salida == NULL) {
        return AVL_ERROR_NULL;
    }

    nodo = buscar_nodo(arbol->raiz, valor);
    if (nodo == NULL) {
        return AVL_ERROR_NO_EXISTE;
    }

    *salida = factor_nodo(nodo);
    return AVL_OK;
}

/**
 * @brief Ejecuta un recorrido preorden y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return AVL_OK si se recorrió correctamente.
 */
AvlResultado avl_recorrer_preorden(const Avl *arbol, AvlVisitante visitante, void *contexto)
{
    if (arbol == NULL || visitante == NULL) {
        return AVL_ERROR_NULL;
    }

    preorden_rec(arbol->raiz, visitante, contexto);
    return AVL_OK;
}

/**
 * @brief Ejecuta un recorrido inorden y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return AVL_OK si se recorrió correctamente.
 */
AvlResultado avl_recorrer_inorden(const Avl *arbol, AvlVisitante visitante, void *contexto)
{
    if (arbol == NULL || visitante == NULL) {
        return AVL_ERROR_NULL;
    }

    inorden_rec(arbol->raiz, visitante, contexto);
    return AVL_OK;
}

/**
 * @brief Ejecuta un recorrido postorden y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return AVL_OK si se recorrió correctamente.
 */
AvlResultado avl_recorrer_postorden(const Avl *arbol, AvlVisitante visitante, void *contexto)
{
    if (arbol == NULL || visitante == NULL) {
        return AVL_ERROR_NULL;
    }

    postorden_rec(arbol->raiz, visitante, contexto);
    return AVL_OK;
}

/**
 * @brief Ejecuta un recorrido por niveles (BFS) y aplica un visitador.
 * @param[in] arbol     Puntero constante al árbol.
 * @param[in] visitante Callback a invocar en cada nodo.
 * @param[in] contexto  Datos adicionales para el callback.
 * @return AVL_OK si se recorrió correctamente. AVL_ERROR_MEMORIA si falla la cola interna.
 */
AvlResultado avl_recorrer_niveles(const Avl *arbol, AvlVisitante visitante, void *contexto)
{
    const NodoAvl **cola;
    size_t frente;
    size_t final;
    size_t capacidad;

    if (arbol == NULL || visitante == NULL) {
        return AVL_ERROR_NULL;
    }

    if (arbol->raiz == NULL) {
        return AVL_OK;
    }

    capacidad = arbol->tamano;
    cola = (const NodoAvl **)malloc(capacidad * sizeof(NodoAvl *));
    if (cola == NULL) {
        return AVL_ERROR_MEMORIA;
    }

    frente = 0U;
    final = 0U;
    cola[final++] = arbol->raiz;

    while (frente < final) {
        const NodoAvl *actual = cola[frente++];

        visitante(actual->valor, contexto);

        if (actual->izquierdo != NULL) {
            cola[final++] = actual->izquierdo;
        }

        if (actual->derecho != NULL) {
            cola[final++] = actual->derecho;
        }
    }

    free(cola);
    return AVL_OK;
}

/**
 * @brief Valida que la estructura cumpla estrictamente las reglas de un AVL.
 * @param[in] arbol Puntero constante al árbol.
 * @return 1 si es un AVL válido, 0 si hay violaciones (de orden o balanceo).
 */
int avl_es_valido(const Avl *arbol)
{
    int altura;

    if (arbol == NULL) {
        return 0;
    }

    altura = 0;
    return validar_rec(arbol->raiz, (long)INT_MIN - 1L, (long)INT_MAX + 1L, &altura);
}

/**
 * @brief Función recursiva para imprimir el AVL gráficamente.
 * @param[in] nodo Puntero al nodo actual.
 * @param[in] n    Profundidad actual.
 */
static void imprimir_avl_rec(NodoAvl *nodo, int n) {
    if (nodo == NULL) return;
    
    imprimir_avl_rec(nodo->derecho, n + 1);
    
    for (int i = 0; i < n; i++) {
        printf("    ");
    }
    printf("%d\n", nodo->valor);
    
    imprimir_avl_rec(nodo->izquierdo, n + 1);
}

/**
 * @brief Imprime una representación gráfica del árbol AVL en consola.
 * @param[in] arbol Puntero constante al árbol.
 */
void avl_imprimir_arbol(const Avl *arbol) {
    if (!arbol || !arbol->raiz) {
        printf("Arbol vacio\n");
        return;
    }
    imprimir_avl_rec(arbol->raiz, 0);
}
