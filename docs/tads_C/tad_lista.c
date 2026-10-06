/**
 * @file tad_lista.c
 * @brief Implementación del TAD Lista enlazada.
 */

#include <stdio.h>
#include <stdlib.h>

/**
 * @brief Nodo de una lista enlazada simple.
 */
struct NodoLista {
    int nro; /**< Dato entero almacenado. */
    struct NodoLista *sgte; /**< Enlace al siguiente nodo. */
};

/** @brief Puntero a nodo o cabeza de lista; NULL representa lista vacía. */
typedef struct NodoLista* Tlista;

/**
 * @brief Reserva un nodo y establece su dato y enlace NULL.
 * @param valor Dato almacenado.
 * @return Nodo reservado o NULL en error de memoria; el llamador libera su memoria.
 * @note Un fallo de malloc escribe un diagnóstico en stdout.
 */
static Tlista CrearNodoLista(int valor) {
    Tlista q = (Tlista) malloc(sizeof(struct NodoLista));
    if (q == NULL) {
        printf("Error: no se pudo asignar memoria.\n");
        return NULL;
    }
    q->nro = valor;
    q->sgte = NULL;
    return q;
}


//----------------------------------------------------------------
/*
 * @brief Inserta un nuevo nodo al inicio de la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor entero a insertar.
 */
/**
 * @brief Reserva e inserta un nodo al inicio de la cadena.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato entero a insertar; se admiten valores repetidos.
 * @post En éxito, la nueva cabeza contiene valor y enlaza con la cabeza anterior.
 * @note Si lista es NULL no hace nada. Si malloc falla, conserva la cadena y escribe un diagnóstico en stdout.
 */
void lista_insertar_inicio(Tlista *lista, int valor) {
    if (lista == NULL) {
        return;
    }

    Tlista q = CrearNodoLista(valor);
    if (q == NULL) {
        return;
    }

    q->sgte = *lista;
    *lista = q;
}


//---------------------------------------------------------------
/*
 * @brief Inserta un nuevo nodo al final de la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor entero a insertar.
 */
/**
 * @brief Reserva e inserta un nodo al final de la cadena.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato entero a insertar; se admiten valores repetidos.
 * @post En éxito, la cadena vacía recibe una cabeza; en otra cadena cambia el enlace del último nodo.
 * @note Si lista es NULL no hace nada. Si malloc falla, conserva la cadena y escribe un diagnóstico en stdout.
 */
void lista_insertar_final(Tlista *lista, int valor) {
    if (lista == NULL) {
        return;
    }

    Tlista q = CrearNodoLista(valor);
    if (q == NULL) {
        return;
    }

    if (*lista == NULL) {
        *lista = q;
    } else {
        Tlista t = *lista;
        while (t->sgte != NULL) {
            t = t->sgte;
        }
        t->sgte = q;
    }
}

//---------------------------------------------------------------
/*
 * @brief Inserta un nodo en una posición dada.
 * @param lista Puntero a la lista.
 * @param valor Valor a insertar.
 * @param pos Posición base para la inserción.
 */
/**
 * @brief Inserta al inicio para pos=1, o después del nodo en la posición base pos.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato entero a insertar; se admiten valores repetidos.
 * @param[in] pos Posición base: 1 incluso en lista vacía, o 2..n si existe el nodo base.
 * @note pos=1 no significa insertar después del primer nodo: inserta al inicio.
 * @note Si lista es NULL o pos<=0, retorna sin reservar ni modificar la cadena.
 * @note Un fallo de malloc conserva la cadena y escribe un diagnóstico en stdout.
 * @note Si no existe la posición base, escribe un diagnóstico, libera el nodo temporal y conserva la cadena.
 */
void lista_insertar_elemento(Tlista *lista, int valor, int pos) {
    if (lista == NULL || pos <= 0) {
        return;
    }

    Tlista q = CrearNodoLista(valor);
    if (q == NULL) {
        return;
    }

    /*
     * Contrato actual:
     * - pos == 1: inserta al inicio.
     * - pos > 1 : inserta despues del nodo en posicion base `pos`.
     */
    if (pos == 1) {
        q->sgte = *lista;
        *lista = q;
        return;
    }

    Tlista t = *lista;
    int i = 1;
    while (t != NULL) {
        if (i == pos) {
            q->sgte = t->sgte;
            t->sgte = q;
            return;
        }
        t = t->sgte;
        i++;
    }

    printf("   Error...Posicion no encontrada..!\n");
    free(q);
}

//---------------------------------------------------------------
/*
 * @brief Recorre toda la lista e imprime las posiciones de todas las coincidencias.
 * @param lista Lista en la que se busca.
 * @param valor Valor a buscar.
 */
/**
 * @brief Recorre toda la cadena e imprime las posiciones de todas las coincidencias.
 * @param[in] lista Cabeza de la cadena por valor; NULL representa lista vacía.
 * @param[in] valor Dato buscado.
 * @post No modifica nodos ni enlaces; las posiciones impresas comienzan en 1.
 * @note Es void: comunica las coincidencias mediante stdout, no devuelve una colección C.
 * @note Si no hay coincidencias, incluida la lista vacía, imprime Numero no encontrado.
 */
void lista_buscar_elemento(Tlista lista, int valor) {
    int i = 1, encontrado = 0;
    Tlista q = lista;

    while (q != NULL) {
        if (q->nro == valor) {
            printf("\n Encontrado en la posicion %d\n", i);
            encontrado = 1;
        }
        q = q->sgte;
        i++;
    }

    if (!encontrado) {
        printf("\n Numero no encontrado..\n");
    }
}


//---------------------------------------------------------------

/**
 * @brief Imprime todos los elementos de la lista.
 * @param[in] lista Lista a mostrar.
 * @pre Lista prestada viva y aciclica; contador de posiciones debe caber en int durante todo recorrido.
 * @note Imprime posicion desde 1 y dato por linea; lista NULL no imprime nada. No reserva/libera ni modifica nodos.
 */
void lista_mostrar(Tlista lista) {
    int i = 1;
    Tlista aux = lista;
    while (aux != NULL) {
        printf(" %d) %d\n", i, aux->nro);
        aux = aux->sgte;
        i++;
    }
}


//---------------------------------------------------------------
/*
 * @brief Elimina la primera ocurrencia de un valor en la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor a eliminar.
 */
/**
 * @brief Desconecta y libera únicamente la primera ocurrencia del valor.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato cuya primera coincidencia se elimina.
 * @post Si hay coincidencia, reconecta la cabeza o el enlace anterior antes de free; las restantes ocurrencias se conservan.
 * @note Si lista es NULL, la cadena está vacía o no existe el valor, escribe un diagnóstico en stdout y no modifica la cadena.
 * @note No devuelve un estado de éxito: su tipo de retorno C es void.
 */
void lista_eliminar_elemento(Tlista *lista, int valor) {
    if (lista == NULL || *lista == NULL) {
        printf(" Valor no encontrado o lista vacia.\n");
        return;
    }

    Tlista p = *lista, ant = NULL;

    while (p != NULL) {
        if (p->nro == valor) {
            if (p == *lista) {
                *lista = p->sgte;
            } else {
                ant->sgte = p->sgte;
            }
            free(p);
            return;
        }
        ant = p;
        p = p->sgte;
    }

    printf(" Valor no encontrado o lista vacia.\n");
}


//---------------------------------------------------------------
/*
 * @brief Elimina todas las ocurrencias de un valor en la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor a eliminar.
 */
/**
 * @brief Desconecta y libera todas las ocurrencias del valor solicitado.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato cuyas coincidencias se eliminan, incluso si solo hay una.
 * @post Conserva el orden y los nodos de los demás valores; no deja una copia del valor eliminado.
 * @note Si lista es NULL o la cadena está vacía, no modifica nodos. Imprime Valores eliminados también si no encontró coincidencias.
 * @note Es void: no devuelve un contador en C; el contador de la aplicación es información adicional del wrapper.
 */
void lista_eliminar_repetidos(Tlista *lista, int valor) {
    if (lista == NULL || *lista == NULL) {
        printf("\n\n Valores eliminados..\n");
        return;
    }

    Tlista q = *lista, ant = NULL;

    while (q != NULL) {
        if (q->nro == valor) {
            Tlista temp = q;
            if (q == *lista) {
                *lista = q->sgte;
                q = *lista;
            } else {
                ant->sgte = q->sgte;
                q = ant->sgte;
            }
            free(temp);
        } else {
            ant = q;
            q = q->sgte;
        }
    }
    printf("\n\n Valores eliminados..\n");
}

//---------------------------------------------------------------
/*
 * @brief Libera todos los nodos de una lista enlazada.
 * @param lista Puntero a la lista que se vacía.
 */
/**
 * @brief Desconecta y libera todos los nodos; deja la cabeza en NULL.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @post Cada nodo se desconecta de la cabeza antes de free(q); una cabeza inicialmente NULL permanece NULL.
 * @note Si lista es NULL retorna sin hacer nada. No escribe en stdout.
 * @note q es un alias local; después de free(q) su valor es indeterminado hasta la siguiente asignación. No se lee durante ese intervalo.
 */
void lista_limpiar(Tlista *lista) {
    if (lista == NULL) {
        return;
    }

    Tlista q;
    while (*lista != NULL) {
        q = *lista;
        *lista = q->sgte;
        free(q);
    }
}

/**
 * @brief Desenlaza y libera el primer nodo.
 * @param lista Dirección de la cabeza que se actualiza.
 * @param valor Salida del dato eliminado; no debe ser NULL.
 * @return 1 al eliminar; 0 ante lista vacía o punteros NULL.
 * @pre Lista propia viva y aciclica; lista es direccion escribible de cabeza y valor int externo escribible sin solaparse con cabeza/nodos.
 * @note Guardas NULL/vacio/indice inexistente retornan 0 sin escribir valor ni liberar. Exito retorna 1, copia dato, cambia enlaces y libera un nodo; aliases al nodo quedan invalidos. No reserva ni imprime.
 */
int lista_eliminar_inicio(Tlista *lista, int *valor) {
    Tlista eliminado;
    if (lista == NULL || *lista == NULL || valor == NULL) return 0;
    eliminado = *lista;
    *valor = eliminado->nro;
    *lista = eliminado->sgte;
    free(eliminado);
    return 1;
}

/**
 * @brief Desenlaza y libera el último nodo.
 * @param lista Dirección de la cabeza que puede actualizarse.
 * @param valor Salida del dato eliminado; no debe ser NULL.
 * @return 1 al eliminar; 0 ante lista vacía o punteros NULL.
 * @pre Lista propia viva y aciclica; lista es direccion escribible de cabeza y valor int externo escribible sin solaparse con cabeza/nodos.
 * @note Guardas NULL/vacio/indice inexistente retornan 0 sin escribir valor ni liberar. Exito retorna 1, copia dato, cambia enlaces y libera un nodo; aliases al nodo quedan invalidos. No reserva ni imprime.
 */
int lista_eliminar_final(Tlista *lista, int *valor) {
    Tlista actual, anterior = NULL;
    if (lista == NULL || *lista == NULL || valor == NULL) return 0;
    actual = *lista;
    while (actual->sgte != NULL) { anterior = actual; actual = actual->sgte; }
    *valor = actual->nro;
    if (anterior == NULL) *lista = NULL; else anterior->sgte = NULL;
    free(actual);
    return 1;
}

/**
 * @brief Desenlaza y libera el nodo en un índice basado en cero.
 * @param lista Dirección de la cabeza.
 * @param posicion Índice: cero identifica el primer nodo.
 * @param valor Salida del dato eliminado; no debe ser NULL.
 * @return 1 al eliminar; 0 ante índice fuera de rango o punteros NULL.
 * @pre Lista propia viva y aciclica; lista es direccion escribible de cabeza y valor int externo escribible sin solaparse con cabeza/nodos.
 * @note Guardas NULL/vacio/indice inexistente retornan 0 sin escribir valor ni liberar. Exito retorna 1, copia dato, cambia enlaces y libera un nodo; aliases al nodo quedan invalidos. No reserva ni imprime.
 * @note Posicion basada en cero; negativa retorna 0. No es el contrato posicional de lista_insertar_elemento.
 */
int lista_eliminar_posicion(Tlista *lista, int posicion, int *valor) {
    Tlista actual, anterior = NULL;
    int indice = 0;
    if (lista == NULL || posicion < 0 || valor == NULL) return 0;
    actual = *lista;
    while (actual != NULL && indice < posicion) { anterior = actual; actual = actual->sgte; indice++; }
    if (actual == NULL) return 0;
    *valor = actual->nro;
    if (anterior == NULL) *lista = actual->sgte; else anterior->sgte = actual->sgte;
    free(actual);
    return 1;
}



/**
 * @brief Consulta el primer dato sin modificar enlaces.
 * @param lista Cabeza de la lista.
 * @param valor Salida del dato consultado.
 * @return 1 si existe el nodo y valor no es NULL; 0 en otro caso.
 * @pre Lista prestada viva y aciclica; valor es int externo escribible sin solaparse con nodos.
 * @note Lista NULL o valor NULL retorna 0 sin escritura. Exito retorna 1 y escribe dato; no reserva/libera/imprime ni modifica enlaces bajo precondiciones.
 */
int lista_primero(Tlista lista, int *valor) {
    if (lista == NULL || valor == NULL) return 0;
    *valor = lista->nro;
    return 1;
}

/**
 * @brief Consulta el último dato sin modificar enlaces.
 * @param lista Cabeza de la lista.
 * @param valor Salida del dato consultado.
 * @return 1 si existe el nodo y valor no es NULL; 0 en otro caso.
 * @pre Lista prestada viva y aciclica; valor es int externo escribible sin solaparse con nodos.
 * @note Lista NULL o valor NULL retorna 0 sin escritura. Exito retorna 1 y escribe dato; no reserva/libera/imprime ni modifica enlaces bajo precondiciones.
 */
int lista_ultimo(Tlista lista, int *valor) {
    if (lista == NULL || valor == NULL) return 0;
    while (lista->sgte != NULL) lista = lista->sgte;
    *valor = lista->nro;
    return 1;
}
