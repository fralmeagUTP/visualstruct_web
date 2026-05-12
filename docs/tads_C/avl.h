#ifndef AVL_H
#define AVL_H

/**
 * @file avl.h
 * @brief API publica para un Tipo Abstracto de Datos Arbol AVL.
 *
 * Este modulo implementa un arbol AVL de claves enteras en C estandar.
 * La estructura interna del arbol y de sus nodos permanece encapsulada
 * en el archivo avl_tad.c.
 */

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

/**
 * @brief Tipo opaco que representa un arbol AVL.
 */
typedef struct Avl Avl;

/**
 * @brief Funcion de visita usada por los recorridos del AVL.
 * @param valor Valor almacenado en el nodo visitado.
 * @param contexto Puntero opcional definido por el usuario.
 */
typedef void (*AvlVisitante)(int valor, void *contexto);

/**
 * @brief Codigos de resultado para las operaciones del AVL.
 */
typedef enum AvlResultado {
    AVL_OK = 0,              /**< Operacion realizada correctamente. */
    AVL_ERROR_NULL = 1,      /**< Puntero nulo recibido como parametro. */
    AVL_ERROR_MEMORIA = 2,   /**< No fue posible reservar memoria dinamica. */
    AVL_ERROR_DUPLICADO = 3, /**< El valor ya existe en el arbol. */
    AVL_ERROR_NO_EXISTE = 4, /**< El valor no existe en el arbol. */
    AVL_ERROR_VACIO = 5      /**< La operacion requiere un arbol no vacio. */
} AvlResultado;

/**
 * @brief Crea un arbol AVL vacio.
 * @return Puntero al AVL creado o NULL si no hay memoria disponible.
 */
Avl *avl_crear(void);

/**
 * @brief Libera todos los nodos y la estructura principal del AVL.
 * @param arbol Arbol a destruir. Si es NULL, no realiza ninguna accion.
 */
void avl_destruir(Avl *arbol);

/**
 * @brief Elimina todos los nodos del AVL y conserva la estructura principal.
 * @param arbol Arbol AVL.
 * @return AVL_OK si se vacio correctamente; AVL_ERROR_NULL si arbol es NULL.
 */
AvlResultado avl_vaciar(Avl *arbol);

/**
 * @brief Inserta un valor en el AVL manteniendo el balance.
 * @param arbol Arbol AVL.
 * @param valor Valor entero a insertar.
 * @return AVL_OK, AVL_ERROR_NULL, AVL_ERROR_MEMORIA o AVL_ERROR_DUPLICADO.
 */
AvlResultado avl_insertar(Avl *arbol, int valor);

/**
 * @brief Elimina un valor del AVL manteniendo el balance.
 * @param arbol Arbol AVL.
 * @param valor Valor entero a eliminar.
 * @return AVL_OK, AVL_ERROR_NULL o AVL_ERROR_NO_EXISTE.
 */
AvlResultado avl_eliminar(Avl *arbol, int valor);

/**
 * @brief Verifica si un valor existe en el AVL.
 * @param arbol Arbol AVL.
 * @param valor Valor entero a buscar.
 * @return 1 si existe; 0 si no existe o si arbol es NULL.
 */
int avl_contiene(const Avl *arbol, int valor);

/**
 * @brief Obtiene el menor valor almacenado en el AVL.
 * @param arbol Arbol AVL.
 * @param salida Puntero donde se almacena el valor minimo.
 * @return AVL_OK, AVL_ERROR_NULL o AVL_ERROR_VACIO.
 */
AvlResultado avl_minimo(const Avl *arbol, int *salida);

/**
 * @brief Obtiene el mayor valor almacenado en el AVL.
 * @param arbol Arbol AVL.
 * @param salida Puntero donde se almacena el valor maximo.
 * @return AVL_OK, AVL_ERROR_NULL o AVL_ERROR_VACIO.
 */
AvlResultado avl_maximo(const Avl *arbol, int *salida);

/**
 * @brief Retorna la altura del AVL.
 * @param arbol Arbol AVL.
 * @return Altura del arbol; 0 si esta vacio o si arbol es NULL.
 */
int avl_altura(const Avl *arbol);

/**
 * @brief Retorna el numero de nodos almacenados en el AVL.
 * @param arbol Arbol AVL.
 * @return Cantidad de nodos; 0 si arbol es NULL.
 */
size_t avl_tamano(const Avl *arbol);

/**
 * @brief Verifica si el AVL esta vacio.
 * @param arbol Arbol AVL.
 * @return 1 si esta vacio o si arbol es NULL; 0 en caso contrario.
 */
int avl_esta_vacio(const Avl *arbol);

/**
 * @brief Cuenta los nodos hoja del AVL.
 * @param arbol Arbol AVL.
 * @return Numero de hojas; 0 si esta vacio o si arbol es NULL.
 */
size_t avl_contar_hojas(const Avl *arbol);

/**
 * @brief Calcula el factor de equilibrio de un valor dentro del AVL.
 * @param arbol Arbol AVL.
 * @param valor Valor cuyo nodo se desea consultar.
 * @param salida Puntero donde se almacena el factor: altura(izq)-altura(der).
 * @return AVL_OK, AVL_ERROR_NULL o AVL_ERROR_NO_EXISTE.
 */
AvlResultado avl_factor_equilibrio(const Avl *arbol, int valor, int *salida);

/**
 * @brief Recorre el AVL en preorden: raiz, izquierdo, derecho.
 * @param arbol Arbol AVL.
 * @param visitante Funcion invocada por cada nodo visitado.
 * @param contexto Puntero opcional definido por el usuario.
 * @return AVL_OK o AVL_ERROR_NULL si arbol o visitante son NULL.
 */
AvlResultado avl_recorrer_preorden(const Avl *arbol,
                                   AvlVisitante visitante,
                                   void *contexto);

/**
 * @brief Recorre el AVL en inorden: izquierdo, raiz, derecho.
 * @param arbol Arbol AVL.
 * @param visitante Funcion invocada por cada nodo visitado.
 * @param contexto Puntero opcional definido por el usuario.
 * @return AVL_OK o AVL_ERROR_NULL si arbol o visitante son NULL.
 */
AvlResultado avl_recorrer_inorden(const Avl *arbol,
                                  AvlVisitante visitante,
                                  void *contexto);

/**
 * @brief Recorre el AVL en postorden: izquierdo, derecho, raiz.
 * @param arbol Arbol AVL.
 * @param visitante Funcion invocada por cada nodo visitado.
 * @param contexto Puntero opcional definido por el usuario.
 * @return AVL_OK o AVL_ERROR_NULL si arbol o visitante son NULL.
 */
AvlResultado avl_recorrer_postorden(const Avl *arbol,
                                    AvlVisitante visitante,
                                    void *contexto);

/**
 * @brief Recorre el AVL por niveles usando una cola interna.
 * @param arbol Arbol AVL.
 * @param visitante Funcion invocada por cada nodo visitado.
 * @param contexto Puntero opcional definido por el usuario.
 * @return AVL_OK, AVL_ERROR_NULL o AVL_ERROR_MEMORIA.
 */
AvlResultado avl_recorrer_niveles(const Avl *arbol,
                                  AvlVisitante visitante,
                                  void *contexto);

/**
 * @brief Valida que el arbol cumpla la propiedad ABB y AVL.
 * @param arbol Arbol AVL.
 * @return 1 si la estructura es valida; 0 si no lo es o si arbol es NULL.
 */
int avl_es_valido(const Avl *arbol);

/**
 * @brief Imprime el arbol en la consola de forma grafica (horizontal).
 * @param arbol AVL a imprimir.
 */
void avl_imprimir_arbol(const Avl *arbol);

#ifdef __cplusplus
}
#endif

#endif
