#include "tad_monticulo_binario.h"
#include <limits.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

static const int MONTICULO_CAPACIDAD_POR_DEFECTO = 10;

static void monticulo_append_text(char *destino, size_t capacidad, size_t *usado, const char *fmt, ...) {
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
 * @brief Intercambia dos valores enteros en memoria.
 *
 * @param[in,out] a Puntero al primer valor.
 * @param[in,out] b Puntero al segundo valor.
 *
 * @note Complejidad temporal: O(1).
 */
static void intercambiar(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

/**
 * @brief Compara dos valores según el tipo de montículo.
 *
 * @param[in] tipo Tipo de montículo (Min-Heap o Max-Heap).
 * @param[in] a    Primer valor a comparar.
 * @param[in] b    Segundo valor a comparar.
 *
 * @return @c true si `a` tiene mayor prioridad que `b` (es decir, debe estar más arriba).
 *         En Min-Heap, retorna true si a < b. En Max-Heap, retorna true si a > b.
 *
 * @note Complejidad temporal: O(1).
 */
static bool comparar(TipoMonticulo tipo, int a, int b) {
    if (tipo == MONTICULO_MIN) {
        return a < b;
    } else {
        return a > b;
    }
}

/**
 * @brief Asegura que el monticulo tenga al menos la capacidad solicitada.
 *
 * @param[in,out] m                  Puntero al monticulo.
 * @param[in]     capacidad_objetivo Capacidad minima requerida.
 *
 * @return @c true si hay capacidad suficiente tras la llamada.
 *         @c false si falla la reserva o los parametros son invalidos.
 */
static bool asegurar_capacidad(MonticuloBinario *m, int capacidad_objetivo) {
    int nueva_capacidad;
    int *nuevos_datos;

    if (m == NULL || capacidad_objetivo <= 0) {
        return false;
    }

    if (m->capacidad >= capacidad_objetivo && m->datos != NULL) {
        return true;
    }

    nueva_capacidad = (m->capacidad > 0) ? m->capacidad : MONTICULO_CAPACIDAD_POR_DEFECTO;
    while (nueva_capacidad < capacidad_objetivo) {
        if (nueva_capacidad > INT_MAX / 2) {
            nueva_capacidad = capacidad_objetivo;
            break;
        }
        nueva_capacidad *= 2;
    }

    nuevos_datos = (int *)realloc(m->datos, sizeof(int) * (size_t)nueva_capacidad);
    if (nuevos_datos == NULL) {
        return false;
    }

    m->datos = nuevos_datos;
    m->capacidad = nueva_capacidad;
    return true;
}

/**
 * @brief Restaura la propiedad del montículo moviendo un elemento hacia arriba.
 *
 * @details Compara el elemento en el `indice` dado con su padre. Si tiene mayor
 *          prioridad (según `comparar`), los intercambia y repite el proceso.
 *
 * @param[in,out] m      Puntero al montículo.
 * @param[in]     indice Índice del elemento que se va a subir.
 *
 * @note Complejidad temporal: O(log N).
 */
static void heapify_up(MonticuloBinario *m, int indice) {
    int padre = (indice - 1) / 2;
    while (indice > 0 && comparar(m->tipo, m->datos[indice], m->datos[padre])) {
        intercambiar(&m->datos[indice], &m->datos[padre]);
        indice = padre;
        padre = (indice - 1) / 2;
    }
}

/**
 * @brief Restaura la propiedad del montículo hundiendo un elemento hacia abajo.
 *
 * @details Compara el elemento con sus dos hijos. Si alguno de los hijos tiene
 *          mayor prioridad, intercambia el elemento con el hijo más prioritario
 *          y repite el proceso hacia abajo.
 *
 * @param[in,out] m      Puntero al montículo.
 * @param[in]     indice Índice del elemento que se va a hundir.
 *
 * @note Complejidad temporal: O(log N).
 */
static void heapify_down(MonticuloBinario *m, int indice) {
    int hijo_izq, hijo_der, seleccionado;

    while (1) {
        hijo_izq = 2 * indice + 1;
        hijo_der = 2 * indice + 2;
        seleccionado = indice;

        if (hijo_izq < m->cantidad && comparar(m->tipo, m->datos[hijo_izq], m->datos[seleccionado])) {
            seleccionado = hijo_izq;
        }

        if (hijo_der < m->cantidad && comparar(m->tipo, m->datos[hijo_der], m->datos[seleccionado])) {
            seleccionado = hijo_der;
        }

        if (seleccionado != indice) {
            intercambiar(&m->datos[indice], &m->datos[seleccionado]);
            indice = seleccionado;
        } else {
            break;
        }
    }
}

/**
 * @brief Inicializa un montículo vacío con una capacidad inicial y un tipo.
 *
 * @param[out] m                 Puntero al montículo a inicializar.
 * @param[in]  tipo              Tipo de montículo (`MONTICULO_MIN` o `MONTICULO_MAX`).
 * @param[in]  capacidad_inicial Capacidad base a reservar en el arreglo. Si es <= 0, se usa 10 por defecto.
 *
 * @note Complejidad temporal: O(1).
 */
void monticulo_inicializar(MonticuloBinario *m, TipoMonticulo tipo, int capacidad_inicial) {
    int capacidad_objetivo;

    if (m == NULL) return;
    m->tipo = tipo;
    m->cantidad = 0;
    m->capacidad = 0;
    m->datos = NULL;

    capacidad_objetivo = (capacidad_inicial > 0) ? capacidad_inicial : MONTICULO_CAPACIDAD_POR_DEFECTO;
    if (!asegurar_capacidad(m, capacidad_objetivo)) {
        m->capacidad = 0;
    }
}

/**
 * @brief Inserta un valor en el montículo preservando su propiedad.
 *
 * @details Si se alcanza la capacidad máxima del arreglo interno, este se
 *          redimensiona al doble automáticamente utilizando `realloc`.
 *
 * @param[in,out] m     Puntero al montículo.
 * @param[in]     valor Valor entero a insertar.
 *
 * @return @c true  si la inserción fue exitosa.
 * @return @c false si hubo un error de memoria o `m` es nulo.
 *
 * @note Complejidad temporal: O(log N) promedio, O(N) si requiere redimensionar.
 */
bool monticulo_insertar(MonticuloBinario *m, int valor) {
    if (m == NULL) return false;

    if (!asegurar_capacidad(m, m->cantidad + 1)) {
        return false;
    }

    m->datos[m->cantidad] = valor;
    heapify_up(m, m->cantidad);
    m->cantidad++;
    return true;
}

/**
 * @brief Consulta la raíz del montículo sin modificar la estructura.
 *
 * @param[in]  m         Puntero constante al montículo.
 * @param[out] resultado Puntero donde se almacenará el valor de la raíz.
 *
 * @return @c true si el montículo no está vacío y se obtuvo el resultado.
 *         @c false si está vacío o los punteros son nulos.
 *
 * @note Complejidad temporal: O(1).
 */
bool monticulo_raiz(const MonticuloBinario *m, int *resultado) {
    if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;
    *resultado = m->datos[0];
    return true;
}

/**
 * @brief Extrae la raíz del montículo (el menor o mayor elemento según el tipo).
 *
 * @details Retorna la raíz, la reemplaza por el último elemento del árbol
 *          y restablece la propiedad hundiendo este nuevo elemento.
 *
 * @param[in,out] m         Puntero al montículo.
 * @param[out]    resultado Puntero donde se escribirá el valor extraído.
 *
 * @return @c true si se extrajo correctamente.
 *         @c false si el montículo está vacío o nulo.
 *
 * @note Complejidad temporal: O(log N).
 */
bool monticulo_extraer_raiz(MonticuloBinario *m, int *resultado) {
    if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;
    
    *resultado = m->datos[0];
    m->cantidad--;
    
    if (m->cantidad > 0) {
        m->datos[0] = m->datos[m->cantidad];
        heapify_down(m, 0);
    }
    
    return true;
}

/**
 * @brief Elimina una ocurrencia de un valor dentro del montículo.
 *
 * @details Busca el elemento de forma secuencial. Al encontrarlo, lo sustituye
 *          por el último elemento del arreglo y evalúa si es necesario subirlo o
 *          hundirlo para mantener la propiedad de montículo.
 *
 * @param[in,out] m     Puntero al montículo.
 * @param[in]     valor Valor a eliminar.
 *
 * @return @c true si el valor existía y fue eliminado.
 *         @c false si no se encontró.
 *
 * @note Complejidad temporal: O(N) para buscar + O(log N) para reestructurar.
 */
bool monticulo_eliminar_valor(MonticuloBinario *m, int valor) {
    if (m == NULL || m->cantidad == 0) return false;
    
    int indice = -1;
    for (int i = 0; i < m->cantidad; i++) {
        if (m->datos[i] == valor) {
            indice = i;
            break;
        }
    }
    
    if (indice == -1) return false;
    
    m->cantidad--;
    if (indice == m->cantidad) return true; // Era el ultimo
    
    m->datos[indice] = m->datos[m->cantidad];
    
    // Puede que necesite subir o bajar
    int padre = (indice - 1) / 2;
    if (indice > 0 && comparar(m->tipo, m->datos[indice], m->datos[padre])) {
        heapify_up(m, indice);
    } else {
        heapify_down(m, indice);
    }
    
    return true;
}

/**
 * @brief Verifica si el montículo está vacío.
 *
 * @param[in] m Puntero constante al montículo.
 * @return @c true si no hay elementos o el puntero es NULL.
 *
 * @note Complejidad temporal: O(1).
 */
bool monticulo_vacio(const MonticuloBinario *m) {
    return m == NULL || m->cantidad == 0;
}

/**
 * @brief Retorna la cantidad de elementos en el montículo.
 *
 * @param[in] m Puntero constante al montículo.
 * @return La cantidad de elementos.
 *
 * @note Complejidad temporal: O(1).
 */
int monticulo_cantidad(const MonticuloBinario *m) {
    if (m == NULL) return 0;
    return m->cantidad;
}

/**
 * @brief Retorna la capacidad total de almacenamiento actual del montículo.
 *
 * @param[in] m Puntero constante al montículo.
 * @return Capacidad (en número de elementos).
 *
 * @note Complejidad temporal: O(1).
 */
int monticulo_capacidad(const MonticuloBinario *m) {
    if (m == NULL) return 0;
    return m->capacidad;
}

/**
 * @brief Construye un montículo a partir de un arreglo de valores dados.
 *
 * @details Crea el arreglo dinámico, copia los elementos y llama a `heapify_down`
 *          desde los últimos nodos padres hasta la raíz, lo cual es el algoritmo
 *          estándar de construcción con complejidad O(N).
 *
 * @param[in,out] m        Puntero al montículo.
 * @param[in]     valores  Arreglo constante con los valores.
 * @param[in]     cantidad Número de elementos en el arreglo de entrada.
 *
 * @return @c true si se construyó exitosamente, @c false en caso de error.
 *
 * @note Complejidad temporal: O(N).
 */
bool monticulo_construir(MonticuloBinario *m, const int *valores, int cantidad) {
    if (m == NULL || valores == NULL || cantidad <= 0) return false;
    
    monticulo_destruir(m); // Asegurarse de liberar previo si habia

    m->cantidad = cantidad;

    if (!asegurar_capacidad(m, cantidad)) {
        m->cantidad = 0;
        return false;
    }
    
    for (int i = 0; i < cantidad; i++) {
        m->datos[i] = valores[i];
    }
    
    // Heapify desde el ultimo nodo con hijos hasta la raiz
    for (int i = (cantidad / 2) - 1; i >= 0; i--) {
        heapify_down(m, i);
    }
    
    return true;
}

/**
 * @brief Copia los valores internos a un arreglo de destino.
 *
 * @param[in]  m         Puntero constante al montículo.
 * @param[out] destino   Arreglo pre-alocado donde se guardarán los elementos.
 * @param[in]  capacidad Tamaño máximo que acepta el destino.
 *
 * @return Número de valores efectivamente copiados.
 *
 * @note Complejidad temporal: O(N) (o hasta la capacidad).
 */
int monticulo_copiar_valores(const MonticuloBinario *m, int *destino, int capacidad) {
    if (m == NULL || destino == NULL || capacidad <= 0) return 0;
    
    int a_copiar = m->cantidad < capacidad ? m->cantidad : capacidad;
    for (int i = 0; i < a_copiar; i++) {
        destino[i] = m->datos[i];
    }
    return a_copiar;
}

/**
 * @brief Genera un string que representa visualmente el arreglo interno.
 *
 * @param[in]  m         Puntero constante al montículo.
 * @param[out] destino   Buffer en el cual se escribe la salida (estilo `[x, y, ...]`).
 * @param[in]  capacidad Tamaño en bytes del buffer de destino.
 *
 * @note Complejidad temporal: O(N).
 */
void monticulo_formatear_arreglo(const MonticuloBinario *m, char *destino, size_t capacidad) {
    if (destino == NULL || capacidad == 0) return;
    
    destino[0] = '\0';
    if (m == NULL || m->cantidad == 0) {
        snprintf(destino, capacidad, "Monticulo vacio");
        return;
    }
    
    size_t usado = 0;
    monticulo_append_text(destino, capacidad, &usado, "[");
    for (int i = 0; i < m->cantidad; i++) {
        monticulo_append_text(destino, capacidad, &usado, "%d", m->datos[i]);
        if (i < m->cantidad - 1) {
            monticulo_append_text(destino, capacidad, &usado, ", ");
        }
    }
    monticulo_append_text(destino, capacidad, &usado, "]");
}

/**
 * @brief Genera un string estructurando los valores en saltos de línea por niveles.
 *
 * @param[in]  m         Puntero constante al montículo.
 * @param[out] destino   Buffer para escribir la salida multilínea.
 * @param[in]  capacidad Tamaño en bytes del buffer.
 *
 * @note Complejidad temporal: O(N).
 */
void monticulo_formatear_arbol(const MonticuloBinario *m, char *destino, size_t capacidad) {
    if (destino == NULL || capacidad == 0) return;
    
    destino[0] = '\0';
    if (m == NULL || m->cantidad == 0) {
        snprintf(destino, capacidad, "Monticulo vacio");
        return;
    }
    
    size_t usado = 0;
    int nivel = 0;
    int limite_nivel = 1;
    int count_nivel = 0;
    
    for (int i = 0; i < m->cantidad; i++) {
        if (count_nivel == 0 && i != 0) {
            monticulo_append_text(destino, capacidad, &usado, "\n");
        }
        
        if (count_nivel == 0) {
             monticulo_append_text(destino, capacidad, &usado, "L%d: ", nivel);
        }
        
        monticulo_append_text(destino, capacidad, &usado, "%d ", m->datos[i]);
        count_nivel++;
        
        if (count_nivel == limite_nivel) {
            nivel++;
            limite_nivel *= 2;
            count_nivel = 0;
        }
    }
}

/**
 * @brief Libera completamente la memoria reservada por el montículo.
 *
 * @param[in,out] m Puntero al montículo a destruir.
 *
 * @note Tras ejecutarse, la cantidad y la capacidad se reinician a 0.
 * @note Complejidad temporal: O(1).
 */
void monticulo_destruir(MonticuloBinario *m) {
    if (m != NULL) {
        if (m->datos) {
            free(m->datos);
            m->datos = NULL;
        }
        m->cantidad = 0;
        m->capacidad = 0;
    }
}
