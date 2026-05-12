#ifndef ROJO_NEGRO_H
#define ROJO_NEGRO_H

/**
 * @file rojo_negro.h
 * @brief API publica para un Tipo Abstracto de Datos Arbol Rojo-Negro.
 *
 * Este modulo define una interfaz opaca para manipular arboles Rojo-Negro
 * en C estandar. La estructura interna de los nodos queda encapsulada en
 * el archivo de implementacion.
 */

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Tipo opaco que representa un arbol Rojo-Negro.
 */
typedef struct RojoNegro RojoNegro;

/**
 * @brief Codigos de resultado para las operaciones del TAD.
 */
typedef enum RNResultado {
    RN_OK = 0,              /**< Operacion realizada correctamente. */
    RN_ERROR_MEMORIA = 1,   /**< No fue posible reservar memoria. */
    RN_ERROR_NULO = 2,      /**< Se recibio un puntero nulo invalido. */
    RN_ERROR_DUPLICADO = 3, /**< El valor ya existe en el arbol. */
    RN_ERROR_NO_EXISTE = 4, /**< El valor no existe en el arbol. */
    RN_ERROR_VACIO = 5      /**< La operacion requiere un arbol no vacio. */
} RNResultado;

/**
 * @brief Funcion callback usada por los recorridos del arbol.
 *
 * @param valor Valor almacenado en el nodo visitado.
 * @param nivel Nivel del nodo dentro del arbol. La raiz esta en nivel 0.
 * @param es_rojo 1 si el nodo es rojo, 0 si el nodo es negro.
 * @param contexto Puntero definido por el usuario para pasar informacion adicional.
 */
typedef void (*RNVisitador)(int valor, int nivel, int es_rojo, void *contexto);

/**
 * @brief Crea un arbol Rojo-Negro vacio.
 *
 * @return Puntero al arbol creado, o NULL si no hay memoria disponible.
 */
RojoNegro *rn_crear(void);

/**
 * @brief Libera toda la memoria asociada al arbol.
 *
 * @param arbol Arbol a destruir. Puede ser NULL.
 */
void rn_destruir(RojoNegro *arbol);

/**
 * @brief Elimina todos los nodos del arbol, dejandolo vacio.
 *
 * @param arbol Arbol a limpiar.
 * @return RN_OK si se limpio correctamente, RN_ERROR_NULO si arbol es NULL.
 */
RNResultado rn_limpiar(RojoNegro *arbol);

/**
 * @brief Inserta un valor en el arbol Rojo-Negro.
 *
 * No se permiten valores duplicados. La insercion respeta la propiedad de
 * arbol binario de busqueda y posteriormente aplica recoloreo y rotaciones.
 *
 * @param arbol Arbol donde se insertara el valor.
 * @param valor Valor entero a insertar.
 * @return RN_OK, RN_ERROR_NULO, RN_ERROR_MEMORIA o RN_ERROR_DUPLICADO.
 */
RNResultado rn_insertar(RojoNegro *arbol, int valor);

/**
 * @brief Elimina un valor del arbol Rojo-Negro.
 *
 * La eliminacion mantiene las propiedades Rojo-Negro mediante trasplantes,
 * recoloreo y rotaciones correctivas.
 *
 * @param arbol Arbol del cual se eliminara el valor.
 * @param valor Valor entero a eliminar.
 * @return RN_OK, RN_ERROR_NULO o RN_ERROR_NO_EXISTE.
 */
RNResultado rn_eliminar(RojoNegro *arbol, int valor);

/**
 * @brief Verifica si un valor existe en el arbol.
 *
 * @param arbol Arbol donde se realizara la busqueda.
 * @param valor Valor a buscar.
 * @return 1 si existe, 0 si no existe o si arbol es NULL.
 */
int rn_contiene(const RojoNegro *arbol, int valor);

/**
 * @brief Indica si el arbol esta vacio.
 *
 * @param arbol Arbol a consultar.
 * @return 1 si esta vacio o si arbol es NULL, 0 en caso contrario.
 */
int rn_esta_vacio(const RojoNegro *arbol);

/**
 * @brief Retorna la cantidad de nodos almacenados.
 *
 * @param arbol Arbol a consultar.
 * @return Numero de nodos. Retorna 0 si arbol es NULL.
 */
size_t rn_tamano(const RojoNegro *arbol);

/**
 * @brief Obtiene el menor valor del arbol.
 *
 * @param arbol Arbol a consultar.
 * @param salida Puntero donde se almacenara el minimo.
 * @return RN_OK, RN_ERROR_NULO o RN_ERROR_VACIO.
 */
RNResultado rn_minimo(const RojoNegro *arbol, int *salida);

/**
 * @brief Obtiene el mayor valor del arbol.
 *
 * @param arbol Arbol a consultar.
 * @param salida Puntero donde se almacenara el maximo.
 * @return RN_OK, RN_ERROR_NULO o RN_ERROR_VACIO.
 */
RNResultado rn_maximo(const RojoNegro *arbol, int *salida);

/**
 * @brief Calcula la altura del arbol en cantidad de niveles.
 *
 * Un arbol vacio tiene altura 0 y un arbol con solo raiz tiene altura 1.
 *
 * @param arbol Arbol a consultar.
 * @return Altura del arbol. Retorna 0 si arbol es NULL.
 */
int rn_altura(const RojoNegro *arbol);

/**
 * @brief Cuenta los nodos hoja del arbol.
 *
 * @param arbol Arbol a consultar.
 * @return Cantidad de nodos hoja. Retorna 0 si arbol es NULL.
 */
size_t rn_contar_hojas(const RojoNegro *arbol);

/**
 * @brief Recorre el arbol en preorden.
 *
 * @param arbol Arbol a recorrer.
 * @param visitar Funcion callback invocada por cada nodo.
 * @param contexto Puntero opcional definido por el usuario.
 * @return RN_OK o RN_ERROR_NULO.
 */
RNResultado rn_recorrer_preorden(const RojoNegro *arbol,
                                 RNVisitador visitar,
                                 void *contexto);

/**
 * @brief Recorre el arbol en inorden.
 *
 * En un arbol Rojo-Negro valido, este recorrido entrega los datos ordenados.
 *
 * @param arbol Arbol a recorrer.
 * @param visitar Funcion callback invocada por cada nodo.
 * @param contexto Puntero opcional definido por el usuario.
 * @return RN_OK o RN_ERROR_NULO.
 */
RNResultado rn_recorrer_inorden(const RojoNegro *arbol,
                                RNVisitador visitar,
                                void *contexto);

/**
 * @brief Recorre el arbol en postorden.
 *
 * @param arbol Arbol a recorrer.
 * @param visitar Funcion callback invocada por cada nodo.
 * @param contexto Puntero opcional definido por el usuario.
 * @return RN_OK o RN_ERROR_NULO.
 */
RNResultado rn_recorrer_postorden(const RojoNegro *arbol,
                                  RNVisitador visitar,
                                  void *contexto);

/**
 * @brief Recorre el arbol por niveles.
 *
 * @param arbol Arbol a recorrer.
 * @param visitar Funcion callback invocada por cada nodo.
 * @param contexto Puntero opcional definido por el usuario.
 * @return RN_OK, RN_ERROR_NULO o RN_ERROR_MEMORIA.
 */
RNResultado rn_recorrer_niveles(const RojoNegro *arbol,
                                RNVisitador visitar,
                                void *contexto);

/**
 * @brief Valida las invariantes fundamentales de un arbol Rojo-Negro.
 *
 * Comprueba: propiedad de ABB, raiz negra, ausencia de nodos rojos
 * consecutivos y misma altura negra en todos los caminos hacia hojas NIL.
 *
 * @param arbol Arbol a validar.
 * @return 1 si el arbol es valido, 0 si no lo es o si arbol es NULL.
 */
int rn_es_valido(const RojoNegro *arbol);

/**
 * @brief Imprime el arbol en la consola de forma grafica (horizontal), usando colores ANSI.
 * @param arbol Arbol Rojo-Negro a imprimir.
 */
void rn_imprimir_arbol(const RojoNegro *arbol);

#ifdef __cplusplus
}
#endif

#endif /* ROJO_NEGRO_H */
