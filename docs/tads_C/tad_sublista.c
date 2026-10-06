/**
 * @file tad_sublista.c
 * @brief Implementación del TAD Lista de padres y sublistas.
 */

#include "tad_sublista.h"

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

/**
 * @brief Crea un nuevo nodo padre.
 * @param[in] valor Valor entero a almacenar.
 * @return Puntero al nuevo nodo, o NULL si falla la memoria.
 * @note Inicializa nro con valor, sgte y sub en NULL; si malloc falla no hay reserva que liberar.
 */
static Nodo *crear_padre(int valor) {
    Nodo *nuevo = (Nodo *)malloc(sizeof(Nodo));
    if (nuevo == NULL) {
        return NULL;
    }
    nuevo->nro = valor;
    nuevo->sgte = NULL;
    nuevo->sub = NULL;
    return nuevo;
}

/**
 * @brief Crea un nuevo nodo hijo para una sublista.
 * @param[in] valor Valor entero a almacenar.
 * @return Puntero a la nueva sublista, o NULL si falla la memoria.
 * @note Inicializa nro con valor y sgte en NULL; si malloc falla retorna NULL sin publicar un enlace.
 */
static Sublista *crear_hijo(int valor) {
    Sublista *nuevo = (Sublista *)malloc(sizeof(Sublista));
    if (nuevo == NULL) {
        return NULL;
    }
    nuevo->nro = valor;
    nuevo->sgte = NULL;
    return nuevo;
}

/**
 * @brief Agrega texto formateado en un buffer de tamaño acotado.
 * @param destino Buffer de salida.
 * @param capacidad Capacidad total en bytes, incluido el terminador.
 * @param usado Contador actualizado de bytes; se satura a capacidad si hay truncamiento.
 * @param fmt Formato de vsnprintf para los argumentos variables.
 */
static void sublista_append_text(char *destino, size_t capacidad, size_t *usado, const char *fmt, ...) {
    va_list args;
    int escritos;

    if (destino == NULL || usado == NULL || *usado >= capacidad) {
        return;
    }

    va_start(args, fmt);
    escritos = vsnprintf(destino + *usado, capacidad - *usado, fmt, args);
    va_end(args);
    if (escritos < 0) {
        return;
    }
    if ((size_t)escritos >= capacidad - *usado) {
        *usado = capacidad;
    } else {
        *usado += (size_t)escritos;
    }
}

/**
 * @brief Libera la memoria de todos los nodos en una sublista de hijos.
 * @param[in,out] lista_hijos Doble puntero al primer nodo hijo.
 * @note Con lista_hijos NULL no accede a memoria; con una cadena válida libera cada hijo y deja su cabeza NULL. No libera el padre.
 */
static void destruir_hijos(Sublista **lista_hijos) {
    Sublista *actual;
    Sublista *next;

    if (lista_hijos == NULL) {
        return;
    }

    actual = *lista_hijos;
    while (actual != NULL) {
        next = actual->sgte;
        *lista_hijos = next;
        free(actual);
        actual = next;
    }
}

/*
 * @brief Inicializa la lista principal de nodos padre estableciéndola en NULL.
 * @param lista Doble puntero a la lista a inicializar.
 */
/**
 * @brief Inicializa la lista principal de nodos padre estableciéndola en NULL.
 * @param[out] lista Doble puntero a la lista a inicializar.
 * @note Con lista NULL no accede a memoria. Solo asigna NULL: no libera una cadena previamente existente; el llamador debe destruirla o conservar su referencia.
 */
void sublista_inicializar(Nodo **lista) {
    if (lista == NULL) {
        return;
    }
    *lista = NULL;
}

/*
 * @brief Inserta un nuevo nodo padre al final de la lista principal.
 * @param lista       Doble puntero a la lista principal.
 * @param valor_padre Valor del nuevo padre.
 * @return Puntero al nuevo nodo insertado, o NULL si falla.
 */
/**
 * @brief Inserta un nuevo nodo padre al final de la lista principal.
 * @param[in,out] lista       Doble puntero a la lista principal.
 * @param[in]     valor_padre Valor del nuevo padre.
 * @return Puntero al nuevo nodo insertado, o NULL si falla.
 * @note Admite valores repetidos como reservas distintas. Con lista NULL o malloc fallido retorna NULL sin modificar la cadena.
 */
Nodo *sublista_insertar_padre_final(Nodo **lista, int valor_padre) {
    Nodo *nuevo;
    Nodo *actual;

    if (lista == NULL) {
        return NULL;
    }

    nuevo = crear_padre(valor_padre);
    if (nuevo == NULL) {
        return NULL;
    }

    if (*lista == NULL) {
        *lista = nuevo;
        return nuevo;
    }

    actual = *lista;
    while (actual->sgte != NULL) {
        actual = actual->sgte;
    }
    actual->sgte = nuevo;
    return nuevo;
}

/*
 * @brief Busca un nodo padre por su valor.
 * @param lista       Puntero al primer nodo de la lista.
 * @param valor_padre Valor a buscar.
 * @return Puntero al nodo padre encontrado, o NULL si no existe.
 */
/**
 * @brief Busca un nodo padre por su valor.
 * @param[in] lista       Puntero al primer nodo de la lista.
 * @param[in] valor_padre Valor a buscar.
 * @return Puntero al nodo padre encontrado, o NULL si no existe.
 * @note Devuelve la primera coincidencia desde la cabeza. Con lista NULL retorna NULL; no modifica nodos ni enlaces.
 */
Nodo *sublista_buscar_padre(Nodo *lista, int valor_padre) {
    Nodo *actual = lista;
    while (actual != NULL) {
        if (actual->nro == valor_padre) {
            return actual;
        }
        actual = actual->sgte;
    }
    return NULL;
}

/*
 * @brief Elimina la primera ocurrencia de un nodo padre y todos sus hijos.
 * @param lista       Doble puntero a la lista.
 * @param valor_padre Valor del padre a eliminar.
 * @return true si fue eliminado con éxito, false si no se encontró.
*/
/**
 * @brief Elimina la primera ocurrencia de un nodo padre y todos sus hijos.
 * @param[in,out] lista       Doble puntero a la lista.
 * @param[in]     valor_padre Valor del padre a eliminar.
 * @return true si fue eliminado con éxito, false si no se encontró.
 * @note Libera los hijos uno a uno y después el primer padre coincidente; conserva los demás padres. Con lista NULL o cabeza NULL retorna false sin cambios. Alias externos a las reservas liberadas dejan de ser válidos.
 */
bool sublista_eliminar_padre_primero(Nodo **lista, int valor_padre) {
    Nodo *actual;
    Nodo *anterior = NULL;

    if (lista == NULL || *lista == NULL) {
        return false;
    }

    actual = *lista;
    while (actual != NULL) {
        if (actual->nro == valor_padre) {
            if (anterior == NULL) {
                *lista = actual->sgte;
            } else {
                anterior->sgte = actual->sgte;
            }
            destruir_hijos(&actual->sub);
            free(actual);
            return true;
        }
        anterior = actual;
        actual = actual->sgte;
    }

    return false;
}

/*
 * @brief Cuenta el número de nodos padre en la lista.
 * @param lista Puntero constante a la lista.
 * @return Cantidad de nodos padre.
 */
/**
 * @brief Cuenta el número de nodos padre en la lista.
 * @param[in] lista Puntero constante a la lista.
 * @return Cantidad de nodos padre.
 * @note Con lista NULL retorna 0. Recorre una cadena válida sin modificarla.
 */
int sublista_contar_padres(const Nodo *lista) {
    int n = 0;
    const Nodo *actual = lista;
    while (actual != NULL) {
        n++;
        actual = actual->sgte;
    }
    return n;
}

/*
 * @brief Inserta un nuevo nodo hijo al final de la sublista de un padre.
 * @param padre      Puntero al nodo padre.
 * @param valor_hijo Valor del nuevo hijo.
 * @return true si se insertó exitosamente, false en caso de error.
 */
/**
 * @brief Inserta un nuevo nodo hijo al final de la sublista de un padre.
 * @param[in,out] padre      Puntero al nodo padre.
 * @param[in]     valor_hijo Valor del nuevo hijo.
 * @return true si se insertó exitosamente, false en caso de error.
 * @note Con padre NULL o malloc fallido retorna false sin cambiar enlaces. Los hijos repetidos ocupan reservas distintas.
 */
bool sublista_insertar_hijo_final(Nodo *padre, int valor_hijo) {
    Sublista *nuevo;
    Sublista *actual;

    if (padre == NULL) {
        return false;
    }

    nuevo = crear_hijo(valor_hijo);
    if (nuevo == NULL) {
        return false;
    }

    if (padre->sub == NULL) {
        padre->sub = nuevo;
        return true;
    }

    actual = padre->sub;
    while (actual->sgte != NULL) {
        actual = actual->sgte;
    }
    actual->sgte = nuevo;
    return true;
}

/*
 * @brief Busca el padre por valor e inserta al final de su sublista.
 * @param lista Lista principal de padres.
 * @param valor_padre Valor del padre destino.
 * @param valor_hijo Valor del nuevo hijo.
 * @return true si el padre existe y el hijo se inserta; false en otro caso.
 */
/**
 * @brief Busca el padre por valor e inserta al final de su sublista.
 * @param[in,out] lista Lista principal de padres.
 * @param[in] valor_padre Valor del padre destino.
 * @param[in] valor_hijo Valor del nuevo hijo.
 * @return true si el padre existe y el hijo se inserta; false en otro caso.
 * @note Busca el primer padre coincidente. Si no existe o falla la reserva retorna false, sin crear hijos huérfanos ni modificar otras ramas.
 */
bool sublista_insertar_hijo(Nodo *lista, int valor_padre, int valor_hijo) {
    Nodo *padre = sublista_buscar_padre(lista, valor_padre);
    if (padre == NULL) {
        return false;
    }
    return sublista_insertar_hijo_final(padre, valor_hijo);
}

/*
 * @brief Busca un nodo hijo dentro de una sublista por su valor.
 * @param lista_hijos Puntero al primer nodo de la sublista.
 * @param valor_hijo  Valor a buscar.
 * @return Puntero al hijo encontrado, o NULL si no existe.
 */
/**
 * @brief Busca un nodo hijo dentro de una sublista por su valor.
 * @param[in] lista_hijos Puntero al primer nodo de la sublista.
 * @param[in] valor_hijo  Valor a buscar.
 * @return Puntero al hijo encontrado, o NULL si no existe.
 * @note Devuelve la primera coincidencia. Una cabeza NULL produce NULL; no modifica la sublista.
 */
Sublista *sublista_buscar_hijo(Sublista *lista_hijos, int valor_hijo) {
    Sublista *actual = lista_hijos;
    while (actual != NULL) {
        if (actual->nro == valor_hijo) {
            return actual;
        }
        actual = actual->sgte;
    }
    return NULL;
}

/*
 * @brief Elimina la primera ocurrencia de un hijo en la sublista de un padre.
 * @param padre      Puntero al nodo padre.
 * @param valor_hijo Valor del hijo a eliminar.
 * @return true si se eliminó correctamente, false si no se encontró.
 */
/**
 * @brief Elimina la primera ocurrencia de un hijo en la sublista de un padre.
 * @param[in,out] padre      Puntero al nodo padre.
 * @param[in]     valor_hijo Valor del hijo a eliminar.
 * @return true si se eliminó correctamente, false si no se encontró.
 * @note Libera solo la primera coincidencia; conserva el padre y los demás hijos.
 * @note Con padre NULL o sin hijos retorna false sin modificar memoria.
 */
bool sublista_eliminar_hijo_primero(Nodo *padre, int valor_hijo) {
    Sublista *actual;
    Sublista *anterior = NULL;

    if (padre == NULL || padre->sub == NULL) {
        return false;
    }

    actual = padre->sub;
    while (actual != NULL) {
        if (actual->nro == valor_hijo) {
            if (anterior == NULL) {
                padre->sub = actual->sgte;
            } else {
                anterior->sgte = actual->sgte;
            }
            free(actual);
            return true;
        }
        anterior = actual;
        actual = actual->sgte;
    }

    return false;
}

/*
 * @brief Busca el padre por valor y elimina la primera coincidencia de hijo.
 * @param lista Lista principal de padres.
 * @param valor_padre Valor del padre destino.
 * @param valor_hijo Valor del hijo a eliminar.
 * @return true si se elimina un hijo; false si no existe padre o hijo.
 */
/**
 * @brief Busca el padre por valor y elimina la primera coincidencia de hijo.
 * @param[in,out] lista Lista principal de padres.
 * @param[in] valor_padre Valor del padre destino.
 * @param[in] valor_hijo Valor del hijo a eliminar.
 * @return true si se elimina un hijo; false si no existe padre o hijo.
 * @note Opera sobre el primer padre coincidente; no elimina otras coincidencias.
 * @note La lista se pasa por valor, pero los enlaces de sus hijos pueden cambiar.
 */
bool sublista_eliminar_hijo(Nodo *lista, int valor_padre, int valor_hijo) {
    Nodo *padre = sublista_buscar_padre(lista, valor_padre);
    if (padre == NULL) {
        return false;
    }
    return sublista_eliminar_hijo_primero(padre, valor_hijo);
}

/*
 * @brief Cuenta cuántos hijos tiene un nodo padre.
 * @param padre Puntero constante al padre.
 * @return Número de hijos del padre.
 */
/**
 * @brief Cuenta cuántos hijos tiene un nodo padre.
 * @param[in] padre Puntero constante al padre.
 * @return Número de hijos del padre.
 * @note Con padre NULL retorna 0; no modifica campos ni enlaces.
 */
int sublista_contar_hijos(const Nodo *padre) {
    int n = 0;
    const Sublista *actual;

    if (padre == NULL) {
        return 0;
    }

    actual = padre->sub;
    while (actual != NULL) {
        n++;
        actual = actual->sgte;
    }
    return n;
}

/*
 * @brief Copia los valores de los hijos de un padre a un arreglo.
 * @param padre     Puntero constante al padre.
 * @param destino   Arreglo donde se copiarán los valores.
 * @param capacidad Tamaño máximo del arreglo destino.
 * @return El número de elementos copiados.
 */
/**
 * @brief Copia los valores de los hijos de un padre a un arreglo.
 * @param[in]  padre     Puntero constante al padre.
 * @param[out] destino   Arreglo donde se copiarán los valores.
 * @param[in]  capacidad Tamaño máximo del arreglo destino.
 * @return El número de elementos copiados.
 * @note Copia como máximo capacidad valores y retorna los copiados, no el total de hijos si el arreglo es menor. Con padre NULL, destino NULL o capacidad no positiva retorna 0 sin escribir. Las posiciones restantes del arreglo no se inicializan.
 */
int sublista_copiar_hijos(const Nodo *padre, int *destino, int capacidad) {
    int usados = 0;
    const Sublista *actual;

    if (padre == NULL || destino == NULL || capacidad <= 0) {
        return 0;
    }

    actual = padre->sub;
    while (actual != NULL && usados < capacidad) {
        destino[usados] = actual->nro;
        usados++;
        actual = actual->sgte;
    }
    return usados;
}

/*
 * @brief Copia los hijos del primer padre con el valor indicado.
 * @param lista Lista principal de padres.
 * @param valor_padre Valor del padre buscado.
 * @param destino Arreglo que recibe los valores de los hijos.
 * @param capacidad Capacidad del arreglo destino.
 * @return Cantidad copiada, o -1 si no existe el padre.
 */
/**
 * @brief Copia los hijos del primer padre con el valor indicado.
 * @param[in] lista Lista principal de padres.
 * @param[in] valor_padre Valor del padre buscado.
 * @param[out] destino Arreglo que recibe los valores de los hijos.
 * @param[in] capacidad Capacidad del arreglo destino.
 * @return Cantidad copiada, o -1 si no existe el padre.
 * @note Consulta solo el primer padre coincidente. Si no existe retorna -1; si existe pero destino es NULL o capacidad no positiva retorna 0 sin escribir. No modifica la estructura.
 */
int sublista_obtener_hijos(Nodo *lista, int valor_padre, int *destino, int capacidad) {
    Nodo *padre = sublista_buscar_padre(lista, valor_padre);
    if (padre == NULL) {
        return -1;
    }
    return sublista_copiar_hijos(padre, destino, capacidad);
}

/*
 * @brief Genera una representación textual de la lista y sus sublistas.
 * @param lista     Puntero constante a la lista de padres.
 * @param destino   Buffer para escribir la cadena resultante.
 * @param capacidad Capacidad máxima del buffer.
 */
/**
 * @brief Genera una representación textual de la lista y sus sublistas.
 * @param[in]  lista     Puntero constante a la lista de padres.
 * @param[out] destino   Buffer para escribir la cadena resultante.
 * @param[in]  capacidad Capacidad máxima del buffer.
 * @note Con destino NULL o capacidad 0 no escribe. Con capacidad positiva la salida queda terminada en NUL y puede truncarse; una lista NULL se representa como Lista padre vacia. No modifica la estructura.
 */
void sublista_formatear(const Nodo *lista, char *destino, size_t capacidad) {
    const Nodo *padre;
    const Sublista *hijo;
    size_t usado = 0;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';
    if (lista == NULL) {
        snprintf(destino, capacidad, "Lista padre vacia");
        return;
    }

    padre = lista;
    while (padre != NULL && usado < capacidad) {
        sublista_append_text(destino, capacidad, &usado, "P(%d): ", padre->nro);

        hijo = padre->sub;
        if (hijo == NULL) {
            sublista_append_text(destino, capacidad, &usado, "(sin hijos)");
        } else {
            while (hijo != NULL && usado < capacidad) {
                sublista_append_text(destino, capacidad, &usado, "[%d]", hijo->nro);
                hijo = hijo->sgte;
                if (hijo != NULL && usado < capacidad) {
                    sublista_append_text(destino, capacidad, &usado, " -> ");
                }
            }
        }

        padre = padre->sgte;
        if (padre != NULL && usado < capacidad) {
            sublista_append_text(destino, capacidad, &usado, "\n");
        }
    }
}

/*
 * @brief Libera completamente la memoria de todos los padres y sus respectivos hijos.
 * @param lista Doble puntero a la lista principal.
 */
/**
 * @brief Libera completamente la memoria de todos los padres y sus respectivos hijos.
 * @param[in,out] lista Doble puntero a la lista principal.
 * @note Con lista NULL no accede a memoria. Libera los hijos de cada padre antes de ese padre, deja la cabeza NULL y no altera listas ajenas. Alias externos a nodos liberados dejan de ser válidos.
 */
void sublista_destruir(Nodo **lista) {
    Nodo *actual;
    Nodo *next;

    if (lista == NULL) {
        return;
    }

    actual = *lista;
    while (actual != NULL) {
        next = actual->sgte;
        destruir_hijos(&actual->sub);
        *lista = next;
        free(actual);
        actual = next;
    }
}
