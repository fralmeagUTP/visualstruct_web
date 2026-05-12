#ifndef ABB_H
#define ABB_H

/**
 * @file abb_tad.h
 * @brief API pública para un Tipo Abstracto de Datos Árbol Binario de Búsqueda (ABB).
 *
 * Este módulo implementa un ABB de enteros en C estándar. La representación interna
 * del árbol y de sus nodos queda encapsulada en el archivo .c.
 */

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Tipo opaco que representa un Árbol Binario de Búsqueda.
 */
typedef struct Abb Abb;

/**
 * @brief Función de visita utilizada por los recorridos.
 * @param valor Valor almacenado en el nodo visitado.
 * @param contexto Puntero opcional definido por el usuario.
 */
typedef void (*AbbVisitador)(int valor, void *contexto);

/**
 * @brief Crea un ABB vacío.
 * @return Puntero al ABB creado, o NULL si no hay memoria disponible.
 */
Abb *abb_crear(void);

/**
 * @brief Libera todos los nodos del árbol y destruye la estructura ABB.
 * @param arbol Doble puntero al ABB. Al finalizar, *arbol queda en NULL.
 */
void abb_destruir(Abb **arbol);

/**
 * @brief Elimina todos los nodos del ABB, pero conserva la estructura principal.
 * @param arbol ABB a limpiar.
 */
void abb_limpiar(Abb *arbol);

/**
 * @brief Verifica si el ABB está vacío.
 * @param arbol ABB a consultar.
 * @return 1 si está vacío o si arbol es NULL; 0 en caso contrario.
 */
int abb_esta_vacio(const Abb *arbol);

/**
 * @brief Inserta un valor en el ABB.
 *
 * No se permiten duplicados. Si el valor ya existe, el árbol no se modifica.
 *
 * @param arbol ABB donde se insertará el valor.
 * @param valor Valor entero a insertar.
 * @return 1 si se insertó correctamente; 0 si hubo error de memoria, árbol NULL o duplicado.
 */
int abb_insertar(Abb *arbol, int valor);

/**
 * @brief Elimina un valor del ABB si existe.
 * @param arbol ABB del cual se eliminará el valor.
 * @param valor Valor entero a eliminar.
 * @return 1 si se eliminó; 0 si el árbol es NULL, está vacío o el valor no existe.
 */
int abb_eliminar(Abb *arbol, int valor);

/**
 * @brief Busca un valor en el ABB.
 * @param arbol ABB donde se realizará la búsqueda.
 * @param valor Valor entero a buscar.
 * @return 1 si el valor existe; 0 en caso contrario.
 */
int abb_contiene(const Abb *arbol, int valor);

/**
 * @brief Obtiene el menor valor almacenado en el ABB.
 * @param arbol ABB a consultar.
 * @param salida Dirección donde se almacenará el valor mínimo.
 * @return 1 si se obtuvo el mínimo; 0 si arbol/salida es NULL o el árbol está vacío.
 */
int abb_minimo(const Abb *arbol, int *salida);

/**
 * @brief Obtiene el mayor valor almacenado en el ABB.
 * @param arbol ABB a consultar.
 * @param salida Dirección donde se almacenará el valor máximo.
 * @return 1 si se obtuvo el máximo; 0 si arbol/salida es NULL o el árbol está vacío.
 */
int abb_maximo(const Abb *arbol, int *salida);

/**
 * @brief Calcula la altura del ABB medida en número de niveles.
 * @param arbol ABB a consultar.
 * @return Altura del árbol. Retorna 0 si el árbol es NULL o está vacío.
 */
int abb_altura(const Abb *arbol);

/**
 * @brief Retorna la cantidad total de nodos del ABB.
 * @param arbol ABB a consultar.
 * @return Número de nodos. Retorna 0 si arbol es NULL.
 */
size_t abb_tamano(const Abb *arbol);

/**
 * @brief Cuenta los nodos hoja del ABB.
 * @param arbol ABB a consultar.
 * @return Cantidad de hojas. Retorna 0 si arbol es NULL o está vacío.
 */
size_t abb_contar_hojas(const Abb *arbol);

/**
 * @brief Recorre el ABB en preorden: raíz, izquierdo, derecho.
 * @param arbol ABB a recorrer.
 * @param visitar Función que procesará cada valor.
 * @param contexto Puntero opcional que se entrega a la función visitar.
 */
void abb_recorrer_preorden(const Abb *arbol, AbbVisitador visitar, void *contexto);

/**
 * @brief Recorre el ABB en inorden: izquierdo, raíz, derecho.
 *
 * En un ABB válido, este recorrido entrega los valores en orden ascendente.
 *
 * @param arbol ABB a recorrer.
 * @param visitar Función que procesará cada valor.
 * @param contexto Puntero opcional que se entrega a la función visitar.
 */
void abb_recorrer_inorden(const Abb *arbol, AbbVisitador visitar, void *contexto);

/**
 * @brief Recorre el ABB en postorden: izquierdo, derecho, raíz.
 * @param arbol ABB a recorrer.
 * @param visitar Función que procesará cada valor.
 * @param contexto Puntero opcional que se entrega a la función visitar.
 */
void abb_recorrer_postorden(const Abb *arbol, AbbVisitador visitar, void *contexto);

/**
 * @brief Verifica si la estructura cumple la propiedad de ABB.
 * @param arbol ABB a validar.
 * @return 1 si es un ABB válido o está vacío; 0 si no cumple la propiedad.
 */
int abb_es_valido(const Abb *arbol);

/**
 * @brief Imprime el arbol en la consola de forma grafica (horizontal).
 * @param arbol ABB a imprimir.
 */
void abb_imprimir_arbol(const Abb *arbol);

#ifdef __cplusplus
}
#endif

#endif /* ABB_H */
