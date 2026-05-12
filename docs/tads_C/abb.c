/**
 * @file abb.c
 * @brief Implementación encapsulada del TAD Árbol Binario de Búsqueda (ABB).
 */

#include "abb.h"

#include <stdlib.h>
#include <stdio.h>

/**
 * @struct NodoAbb
 * @brief Nodo interno del ABB. No forma parte de la API pública.
 */
typedef struct NodoAbb {
    int valor;
    struct NodoAbb *izquierdo;
    struct NodoAbb *derecho;
} NodoAbb;

/**
 * @struct Abb
 * @brief Representación interna del ABB.
 */
struct Abb {
    NodoAbb *raiz;
    size_t tamano;
};

static NodoAbb *nodo_crear(int valor);
static void nodo_destruir(NodoAbb *nodo);
static int insertar_rec(NodoAbb **nodo, int valor);
static int eliminar_rec(NodoAbb **nodo, int valor);
static NodoAbb *extraer_minimo(NodoAbb **nodo);
static const NodoAbb *buscar_nodo(const NodoAbb *nodo, int valor);
static int altura_rec(const NodoAbb *nodo);
static size_t contar_hojas_rec(const NodoAbb *nodo);
static void preorden_rec(const NodoAbb *nodo, AbbVisitador visitar, void *contexto);
static void inorden_rec(const NodoAbb *nodo, AbbVisitador visitar, void *contexto);
static void postorden_rec(const NodoAbb *nodo, AbbVisitador visitar, void *contexto);
static int validar_rec(const NodoAbb *nodo, int tiene_minimo, int minimo, int tiene_maximo, int maximo);

/**
 * @brief Crea un Árbol Binario de Búsqueda (ABB) vacío.
 * @return Puntero a la nueva estructura `Abb` o `NULL` si falla la asignación de memoria.
 */
Abb *abb_crear(void)
{
    Abb *arbol = (Abb *)malloc(sizeof(Abb));

    if (arbol == NULL) {
        return NULL;
    }

    arbol->raiz = NULL;
    arbol->tamano = 0U;
    return arbol;
}

/**
 * @brief Destruye el árbol y libera toda su memoria.
 * @param[in,out] arbol Doble puntero al árbol que se va a destruir.
 *                      Si el puntero o el árbol es `NULL`, no hace nada.
 */
void abb_destruir(Abb **arbol)
{
    if (arbol == NULL || *arbol == NULL) {
        return;
    }

    abb_limpiar(*arbol);
    free(*arbol);
    *arbol = NULL;
}

/**
 * @brief Vacía el árbol eliminando todos sus nodos.
 * @param[in,out] arbol Puntero al árbol que se va a limpiar.
 *                     Si el puntero o el árbol es `NULL`, no hace nada.
 */
void abb_limpiar(Abb *arbol)
{
    if (arbol == NULL) {
        return;
    }

    nodo_destruir(arbol->raiz);
    arbol->raiz = NULL;
    arbol->tamano = 0U;
}

/**
 * @brief Verifica si el árbol está vacío.
 * @return `1` (true) si el árbol está vacío o es `NULL`.
 * @return `0` (false) si el árbol contiene al menos un elemento.
 */
int abb_esta_vacio(const Abb *arbol)
{
    return (arbol == NULL || arbol->raiz == NULL) ? 1 : 0;
}

/**
 * @brief Inserta un nuevo valor en el ABB.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in]     valor Entero a insertar.
 * @return `1` si se insertó con éxito.
 * @return `0` si el valor ya existe, falla la memoria, o `arbol` es `NULL`.
 */
int abb_insertar(Abb *arbol, int valor)
{
    if (arbol == NULL) {
        return 0;
    }

    if (insertar_rec(&arbol->raiz, valor) == 0) {
        return 0;
    }

    arbol->tamano++;
    return 1;
}

/**
 * @brief Elimina un valor específico del ABB.
 * @param[in,out] arbol Puntero al árbol.
 * @param[in]     valor Entero a eliminar.
 * @return `1` si el valor fue encontrado y eliminado.
 * @return `0` si el valor no existe o `arbol` es `NULL`.
 */
int abb_eliminar(Abb *arbol, int valor)
{
    if (arbol == NULL || arbol->raiz == NULL) {
        return 0;
    }

    if (eliminar_rec(&arbol->raiz, valor) == 0) {
        return 0;
    }

    arbol->tamano--;
    return 1;
}

/**
 * @brief Comprueba si un valor existe en el árbol.
 * @param[in] arbol Puntero constante al árbol.
 * @param[in] valor Entero a buscar.
 * @return `1` si el valor se encuentra en el árbol.
 * @return `0` si no se encuentra o el árbol es `NULL`.
 */
int abb_contiene(const Abb *arbol, int valor)
{
    if (arbol == NULL) {
        return 0;
    }

    return buscar_nodo(arbol->raiz, valor) != NULL ? 1 : 0;
}

/**
 * @brief Obtiene el valor mínimo almacenado en el árbol.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[out] salida Puntero donde se escribirá el valor mínimo.
 * @return `1` si se obtuvo el mínimo con éxito.
 * @return `0` si el árbol está vacío o alguno de los punteros es `NULL`.
 */
int abb_minimo(const Abb *arbol, int *salida)
{
    const NodoAbb *actual;

    if (arbol == NULL || salida == NULL || arbol->raiz == NULL) {
        return 0;
    }

    actual = arbol->raiz;
    while (actual->izquierdo != NULL) {
        actual = actual->izquierdo;
    }

    *salida = actual->valor;
    return 1;
}

/**
 * @brief Obtiene el valor máximo almacenado en el árbol.
 * @param[in]  arbol  Puntero constante al árbol.
 * @param[out] salida Puntero donde se escribirá el valor máximo.
 * @return `1` si se obtuvo el máximo con éxito.
 * @return `0` si el árbol está vacío o alguno de los punteros es `NULL`.
 */
int abb_maximo(const Abb *arbol, int *salida)
{
    const NodoAbb *actual;

    if (arbol == NULL || salida == NULL || arbol->raiz == NULL) {
        return 0;
    }

    actual = arbol->raiz;
    while (actual->derecho != NULL) {
        actual = actual->derecho;
    }

    *salida = actual->valor;
    return 1;
}

/**
 * @brief Calcula la altura máxima del árbol.
 * @param[in] arbol Puntero constante al árbol.
 * @return La altura del árbol, o 0 si está vacío o es `NULL`.
 */
int abb_altura(const Abb *arbol)
{
    if (arbol == NULL) {
        return 0;
    }

    return altura_rec(arbol->raiz);
}

/**
 * @brief Obtiene el número total de nodos en el árbol.
 * @param[in] arbol Puntero constante al árbol.
 * @return El tamaño actual del árbol.
 */
size_t abb_tamano(const Abb *arbol)
{
    return (arbol == NULL) ? 0U : arbol->tamano;
}

/**
 * @brief Cuenta la cantidad de nodos hoja (sin hijos).
 * @param[in] arbol Puntero constante al árbol.
 * @return El número total de hojas.
 */
size_t abb_contar_hojas(const Abb *arbol)
{
    if (arbol == NULL) {
        return 0U;
    }

    return contar_hojas_rec(arbol->raiz);
}

/**
 * @brief Ejecuta un recorrido preorden y aplica un visitador.
 * @param[in] arbol    Puntero constante al árbol.
 * @param[in] visitar  Callback a invocar en cada nodo.
 * @param[in] contexto Puntero a datos adicionales pasados al callback.
 */
void abb_recorrer_preorden(const Abb *arbol, AbbVisitador visitar, void *contexto)
{
    if (arbol == NULL || visitar == NULL) {
        return;
    }

    preorden_rec(arbol->raiz, visitar, contexto);
}

/**
 * @brief Ejecuta un recorrido inorden y aplica un visitador.
 * @param[in] arbol    Puntero constante al árbol.
 * @param[in] visitar  Callback a invocar en cada nodo.
 * @param[in] contexto Puntero a datos adicionales pasados al callback.
 */
void abb_recorrer_inorden(const Abb *arbol, AbbVisitador visitar, void *contexto)
{
    if (arbol == NULL || visitar == NULL) {
        return;
    }

    inorden_rec(arbol->raiz, visitar, contexto);
}

/**
 * @brief Ejecuta un recorrido postorden y aplica un visitador.
 * @param[in] arbol    Puntero constante al árbol.
 * @param[in] visitar  Callback a invocar en cada nodo.
 * @param[in] contexto Puntero a datos adicionales pasados al callback.
 */
void abb_recorrer_postorden(const Abb *arbol, AbbVisitador visitar, void *contexto)
{
    if (arbol == NULL || visitar == NULL) {
        return;
    }

    postorden_rec(arbol->raiz, visitar, contexto);
}

/**
 * @brief Valida que la estructura cumpla las reglas de un ABB.
 * @param[in] arbol Puntero constante al árbol.
 * @return `1` si es un ABB válido o está vacío.
 * @return `0` si existe alguna violación en la estructura.
 */
int abb_es_valido(const Abb *arbol)
{
    if (arbol == NULL) {
        return 1;
    }

    return validar_rec(arbol->raiz, 0, 0, 0, 0);
}

/**
 * @brief Recorre recursivamente el árbol para imprimirlo en formato gráfico.
 * @param[in] nodo Puntero al nodo actual.
 * @param[in] n    Nivel de profundidad actual para la tabulación.
 */
static void imprimir_rec(NodoAbb *nodo, int n) {
    if (nodo == NULL) return;
    
    imprimir_rec(nodo->derecho, n + 1);
    
    for (int i = 0; i < n; i++) {
        printf("    ");
    }
    printf("%d\n", nodo->valor);
    
    imprimir_rec(nodo->izquierdo, n + 1);
}

/**
 * @brief Imprime una representación gráfica del árbol en consola.
 * @param[in] arbol Puntero constante al árbol.
 */
void abb_imprimir_arbol(const Abb *arbol) {
    if (!arbol || !arbol->raiz) {
        printf("Arbol vacio\n");
        return;
    }
    imprimir_rec(arbol->raiz, 0);
}

/**
 * @brief Crea un nuevo nodo de ABB.
 * @param[in] valor Valor entero a almacenar.
 * @return Puntero al nuevo nodo, o `NULL` si falla la memoria.
 */
static NodoAbb *nodo_crear(int valor)
{
    NodoAbb *nuevo = (NodoAbb *)malloc(sizeof(NodoAbb));

    if (nuevo == NULL) {
        return NULL;
    }

    nuevo->valor = valor;
    nuevo->izquierdo = NULL;
    nuevo->derecho = NULL;
    return nuevo;
}

/**
 * @brief Destruye un nodo y todos sus descendientes.
 * @param[in,out] nodo Puntero al nodo a destruir.
 */
static void nodo_destruir(NodoAbb *nodo)
{
    if (nodo == NULL) {
        return;
    }

    nodo_destruir(nodo->izquierdo);
    nodo_destruir(nodo->derecho);
    free(nodo);
}

/**
 * @brief Función recursiva para insertar un valor.
 * @param[in,out] nodo Doble puntero al nodo actual.
 * @param[in]     valor Valor a insertar.
 * @return `1` si se insertó, `0` si falló o ya existe.
 */
static int insertar_rec(NodoAbb **nodo, int valor)
{
    if (nodo == NULL) {
        return 0;
    }

    if (*nodo == NULL) {
        *nodo = nodo_crear(valor);
        return (*nodo != NULL) ? 1 : 0;
    }

    if (valor < (*nodo)->valor) {
        return insertar_rec(&(*nodo)->izquierdo, valor);
    }

    if (valor > (*nodo)->valor) {
        return insertar_rec(&(*nodo)->derecho, valor);
    }

    return 0;
}

/**
 * @brief Función recursiva para eliminar un valor.
 * @param[in,out] nodo Doble puntero al nodo actual.
 * @param[in]     valor Valor a eliminar.
 * @return `1` si se eliminó, `0` si no se encontró.
 */
static int eliminar_rec(NodoAbb **nodo, int valor)
{
    NodoAbb *eliminar;
    NodoAbb *reemplazo;

    if (nodo == NULL || *nodo == NULL) {
        return 0;
    }

    if (valor < (*nodo)->valor) {
        return eliminar_rec(&(*nodo)->izquierdo, valor);
    }

    if (valor > (*nodo)->valor) {
        return eliminar_rec(&(*nodo)->derecho, valor);
    }

    eliminar = *nodo;

    if (eliminar->izquierdo == NULL) {
        *nodo = eliminar->derecho;
        free(eliminar);
        return 1;
    }

    if (eliminar->derecho == NULL) {
        *nodo = eliminar->izquierdo;
        free(eliminar);
        return 1;
    }

    reemplazo = extraer_minimo(&eliminar->derecho);
    if (reemplazo == NULL) {
        return 0;
    }

    reemplazo->izquierdo = eliminar->izquierdo;
    reemplazo->derecho = eliminar->derecho;
    *nodo = reemplazo;
    free(eliminar);
    return 1;
}

/**
 * @brief Extrae el nodo con el valor mínimo de un subárbol.
 * @param[in,out] nodo Doble puntero a la raíz del subárbol.
 * @return Puntero al nodo extraído.
 */
static NodoAbb *extraer_minimo(NodoAbb **nodo)
{
    NodoAbb *minimo;

    if (nodo == NULL || *nodo == NULL) {
        return NULL;
    }

    if ((*nodo)->izquierdo == NULL) {
        minimo = *nodo;
        *nodo = minimo->derecho;
        minimo->derecho = NULL;
        return minimo;
    }

    return extraer_minimo(&(*nodo)->izquierdo);
}

/**
 * @brief Busca un valor en un subárbol.
 * @param[in] nodo  Puntero constante a la raíz del subárbol.
 * @param[in] valor Valor entero a buscar.
 * @return Puntero constante al nodo que contiene el valor, o `NULL` si no se encuentra.
 */
static const NodoAbb *buscar_nodo(const NodoAbb *nodo, int valor)
{
    const NodoAbb *actual = nodo;

    while (actual != NULL) {
        if (valor == actual->valor) {
            return actual;
        }

        actual = (valor < actual->valor) ? actual->izquierdo : actual->derecho;
    }

    return NULL;
}

/**
 * @brief Calcula de forma recursiva la altura de un subárbol.
 * @param[in] nodo Puntero constante al nodo actual.
 * @return Altura del subárbol desde el nodo actual.
 */
static int altura_rec(const NodoAbb *nodo)
{
    int altura_izq;
    int altura_der;

    if (nodo == NULL) {
        return 0;
    }

    altura_izq = altura_rec(nodo->izquierdo);
    altura_der = altura_rec(nodo->derecho);

    return (altura_izq > altura_der ? altura_izq : altura_der) + 1;
}

/**
 * @brief Cuenta recursivamente las hojas de un subárbol.
 * @param[in] nodo Puntero constante al nodo actual.
 * @return Número de hojas en el subárbol.
 */
static size_t contar_hojas_rec(const NodoAbb *nodo)
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
 * @param[in] nodo     Puntero constante al nodo actual.
 * @param[in] visitar  Callback a invocar.
 * @param[in] contexto Contexto del usuario.
 */
static void preorden_rec(const NodoAbb *nodo, AbbVisitador visitar, void *contexto)
{
    if (nodo == NULL) {
        return;
    }

    visitar(nodo->valor, contexto);
    preorden_rec(nodo->izquierdo, visitar, contexto);
    preorden_rec(nodo->derecho, visitar, contexto);
}

/**
 * @brief Realiza un recorrido inorden recursivo.
 * @param[in] nodo     Puntero constante al nodo actual.
 * @param[in] visitar  Callback a invocar.
 * @param[in] contexto Contexto del usuario.
 */
static void inorden_rec(const NodoAbb *nodo, AbbVisitador visitar, void *contexto)
{
    if (nodo == NULL) {
        return;
    }

    inorden_rec(nodo->izquierdo, visitar, contexto);
    visitar(nodo->valor, contexto);
    inorden_rec(nodo->derecho, visitar, contexto);
}

/**
 * @brief Realiza un recorrido postorden recursivo.
 * @param[in] nodo     Puntero constante al nodo actual.
 * @param[in] visitar  Callback a invocar.
 * @param[in] contexto Contexto del usuario.
 */
static void postorden_rec(const NodoAbb *nodo, AbbVisitador visitar, void *contexto)
{
    if (nodo == NULL) {
        return;
    }

    postorden_rec(nodo->izquierdo, visitar, contexto);
    postorden_rec(nodo->derecho, visitar, contexto);
    visitar(nodo->valor, contexto);
}

/**
 * @brief Valida recursivamente si el subárbol es un ABB válido.
 * @param[in] nodo         Puntero constante al nodo actual.
 * @param[in] tiene_minimo Indicador booleano (1 si hay límite inferior).
 * @param[in] minimo       Límite inferior para los valores del subárbol.
 * @param[in] tiene_maximo Indicador booleano (1 si hay límite superior).
 * @param[in] maximo       Límite superior para los valores del subárbol.
 * @return `1` si es válido, `0` si no lo es.
 */
static int validar_rec(const NodoAbb *nodo,
                       int tiene_minimo,
                       int minimo,
                       int tiene_maximo,
                       int maximo)
{
    if (nodo == NULL) {
        return 1;
    }

    if ((tiene_minimo && nodo->valor <= minimo) ||
        (tiene_maximo && nodo->valor >= maximo)) {
        return 0;
    }

    return validar_rec(nodo->izquierdo,
                       tiene_minimo,
                       minimo,
                       1,
                       nodo->valor) &&
           validar_rec(nodo->derecho,
                       1,
                       nodo->valor,
                       tiene_maximo,
                       maximo);
}
