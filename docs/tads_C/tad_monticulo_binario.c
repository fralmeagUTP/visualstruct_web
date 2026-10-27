/**
 * @file tad_monticulo_binario.c
 * @brief Implementación del TAD Montículo binario.
 */

#include "tad_monticulo_binario.h"
#include <limits.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

/**
 * @brief Base interna de crecimiento y reserva inicial por defecto: 10 elementos.
 * @note Se usa ante capacidad inicial <=0 o capacidad actual <=0 al reservar.
 * No es un maximo, ni obliga a que la capacidad solicitada se reserve exactamente.
 */
static const int MONTICULO_CAPACIDAD_POR_DEFECTO = 10;

/**
 * @brief Agrega texto formateado en un buffer de tamaño acotado.
 * @param destino Buffer de salida.
 * @param capacidad Capacidad total en bytes, incluido el terminador.
 * @param usado Contador actualizado de bytes; se satura a capacidad si hay truncamiento.
 * @param fmt Formato de vsnprintf para los argumentos variables.
 * @pre Buffer escribible de capacidad bytes; usado es size_t externo escribible; fmt y argumentos validos de vsnprintf, sin solaparse con salida.
 * @note NULL destino/usado o *usado >= capacidad se ignoran; error no incrementa usado. Truncamiento satura usado a capacidad. Caller inicializa buffer/contador; no reserva/libera ni imprime.
 */
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
 * @pre a y b son direcciones vivas escribibles de int; no admite NULL. Pueden identificar el mismo entero (sin cambio).
 * @note No reserva/libera ni imprime.
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
 * @note Comparacion estricta: empate retorna false. MONTICULO_MIN usa menor; cualquier otro tipo sigue rama mayor, sin validacion de enum. Sin reservas/escrituras.
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
 * @pre m inicializado y propio con datos NULL o reserva valida para realloc; sizeof(int)*nueva_capacidad cabe en size_t.
 * @note NULL m o objetivo <= 0 retorna false. Si capacidad suficiente y datos no NULL, no reserva. De otro modo crece por duplicacion con guarda INT_MAX/2 y realloc.
 * @note Realloc fallido conserva puntero/capacidad/datos. Exito puede invalidar aliases al arreglo previo; cantidad/tipo no se cambian. No garantiza soporte para indices enormes.
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
 * @pre m y datos validos; indice >= 0 identifica slot inicializado dentro de capacidad (puede ser cantidad antes de incrementarla). Antecesores satisfacen propiedad salvo ese slot.
 * @note No comprueba NULL/limites ni reserva/libera. Compara estrictamente con padres; empates no se intercambian.
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
 * @pre m y datos validos; 0 <= indice < cantidad <= capacidad; subarboles de hijos ya son heaps. Cada 2*indice+2 visitado debe ser representable en int.
 * @note No comprueba NULL ni corrige metadata. Compara hijo izquierdo antes de derecho y usa mejora estricta; no reserva/libera. No certifica indices enormes.
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
 * @pre Estructura escribible sin reserva propietaria pendiente; tamanos de reserva representables en size_t.
 * @note NULL m se ignora. Reinicializar no libera datos anteriores: destruir antes. Fija tipo, cantidad=0 y datos=NULL; capacidad inicial <=0 usa 10.
 * @note Fallo reserva deja cantidad=capacidad=0, datos=NULL, tipo conservado; retorno void no comunica exito. No valida enum.
 * @note La seleccion de capacidad por duplicacion realiza O(log capacidad_objetivo) iteraciones en el peor caso; el coste del allocator no se certifica.
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

/*
 * @brief Inserta un valor en el montículo preservando su propiedad.
 *
 * @details Si se alcanza la capacidad máxima del arreglo interno, este se
 *          redimensiona al doble automáticamente utilizando `realloc`.
 *
 * @param m     Puntero al montículo.
 * @param valor Valor entero a insertar.
 *
 * @return @c true  si la inserción fue exitosa.
 * @return @c false si hubo un error de memoria o `m` es nulo.
 *
 * @note Complejidad temporal: O(log N) promedio, O(N) si requiere redimensionar.
 */
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
 * @details El retorno es estado bool, no el entero insertado. Si m es NULL o
 * falla la reserva, devuelve false sin cambiar datos, cantidad, capacidad ni valores.
 * En exito escribe datos[cantidad], restaura la prioridad con heapify_up y solo
 * entonces incrementa cantidad. La celda escrita aun esta fuera de cantidad durante el ascenso.
 * El intercambio son tres asignaciones, no una mutacion atomica.
 * Un realloc exitoso termina la vida previa aunque reutilice direccion: no evaluar
 * alias anteriores; el temporal se publica en datos antes de asignar capacidad.
 * Si realloc falla, el buffer previo sigue vivo. Las celdas nuevas no se inicializan
 * por realloc; solo la asignacion del valor garantiza esa celda inicializada.
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

/*
 * @brief Consulta la raíz del montículo sin modificar la estructura.
 *
 * @param m         Puntero constante al montículo.
 * @param resultado Puntero donde se almacenará el valor de la raíz.
 *
 * @return @c true si el montículo no está vacío y se obtuvo el resultado.
 *         @c false si está vacío o los punteros son nulos.
 *
 * @note Complejidad temporal: O(1).
 */
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
 * @details Si devuelve false, no escribe resultado. Si devuelve true,
 * escribe el entero de datos[0], distinto del estado booleano retornado.
 * No reserva memoria ni cambia los datos, cantidad o capacidad del monticulo.
 */
bool monticulo_raiz(const MonticuloBinario *m, int *resultado) {
    if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;
    *resultado = m->datos[0];
    return true;
}

/*
 * @brief Extrae la raíz del montículo (el menor o mayor elemento según el tipo).
 *
 * @details Retorna la raíz, la reemplaza por el último elemento del árbol
 *          y restablece la propiedad hundiendo este nuevo elemento.
 *
 * @param m         Puntero al montículo.
 * @param resultado Puntero donde se escribirá el valor extraído.
 *
 * @return @c true si se extrajo correctamente.
 *         @c false si el montículo está vacío o nulo.
 *
 * @note Complejidad temporal: O(log N).
 */
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
 * @details El retorno bool indica estado, no el entero extraido. Si m es NULL,
 * cantidad es cero o resultado es NULL, devuelve false sin escribir la salida
 * ni modificar datos, cantidad o capacidad; la condicion usa cortocircuito.
 * En exito escribe *resultado antes de reducir cantidad. Si queda algun elemento,
 * copia la antigua cola en la raiz y ejecuta heapify_down. Cada intercambio son
 * tres asignaciones independientes: pueden existir valores duplicados transitorios.
 * Extraer no libera ni reduce capacidad; la celda de la antigua cola sigue viva
 * e inicializada fuera del prefijo logico. No se debe mostrar como otro elemento.
 * Las comparaciones reciben enteros por valor; el intercambio usa alias int *.
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
 * @pre Monticulo propio inicializado consistente; indices y 2*indice+2 de heapify_down deben ser representables en int.
 * @note NULL m, cantidad==0 o ausencia retorna false sin mutar. Elimina primera coincidencia por indice, decrementa cantidad; si era ultimo slot no reajusta.
 * @note En otro caso copia ultimo dato al hueco; sube si mejora padre, de otro modo baja. No reserva/libera ni reduce capacidad; slot fuera de cantidad no es parte logica.
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
 * @note Consulta cantidad==0 o m NULL sin validar datos/metadata; no reserva/libera ni modifica.
 */
bool monticulo_vacio(const MonticuloBinario *m) {
    return m == NULL || m->cantidad == 0;
}


/**
 * @brief Retorna la cantidad de elementos en el montículo.
 * 
 * @param[in] m Puntero constante al montículo.
 * @return La cantidad de elementos, o 0 si m es NULL.
 * 
 * @note Complejidad temporal: O(1).
 * @note Devuelve contador almacenado sin normalizar/recontar; m prestado inicializado o NULL. No reserva/libera ni modifica.
 */
int monticulo_cantidad(const MonticuloBinario *m) {
    if (m == NULL) return 0;
    return m->cantidad;
}


/**
 * @brief Retorna la capacidad total de almacenamiento actual del montículo.
 * 
 * @param[in] m Puntero constante al montículo.
 * @return Capacidad (en número de elementos), o 0 si m es NULL.
 * 
 * @note Complejidad temporal: O(1).
 * @note Devuelve capacidad almacenada sin validar reserva; m prestado inicializado o NULL. No reserva/libera ni modifica.
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
 * @pre m inicializado y propio; valores contiene al menos cantidad ints vivos legibles y no se solapa con m ni su reserva previa. Tamanos/indices y 2*indice+2 visitados deben ser representables.
 * @note NULL m/valores o cantidad <=0 retorna false sin destruir el anterior. Con parametros validos destruye datos previos antes de reservar: fallo deja heap vacio, no restaura el anterior.
 * @note Conserva tipo; copia exactamente cantidad entradas, no limita a longitud real de buffer. Resultado usa nueva reserva propia; aliases al arreglo anterior quedan invalidos.
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

/*
 * @brief Copia los valores internos a un arreglo de destino.
 *
 * @param m         Puntero constante al montículo.
 * @param destino   Arreglo pre-alocado donde se guardarán los elementos.
 * @param capacidad Tamaño máximo que acepta el destino.
 *
 * @return Número de valores efectivamente copiados.
 *
 * @note Complejidad temporal: O(N) (o hasta la capacidad).
 */
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
 * @details Conserva el orden del arreglo interno, no un orden total.
 * Copia min(cantidad, capacidad) enteros; el destino debe disponer de ese espacio.
 * Con m o destino nulos, o capacidad no positiva, devuelve 0 sin escribir.
 * Un destino independiente conserva los datos, cantidad y capacidad del monticulo.
 * La funcion no reserva ni libera el buffer del llamador.
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
 * @pre m inicializado consistente o NULL; destino es buffer externo de capacidad bytes, sin solaparse con m/datos.
 * @note NULL destino o capacidad cero no escriben. Buffer valido positivo termina con NUL; trunca a capacidad-1 caracteres, capacidad 1 da cadena vacia. m NULL o cantidad==0 produce Monticulo vacio. No reserva/libera/imprime stdout.
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
 * @pre m inicializado consistente o NULL; destino es buffer externo de capacidad bytes, sin solaparse con m/datos.
 * @note NULL destino o capacidad cero no escriben. Buffer valido positivo termina con NUL; trunca a capacidad-1 caracteres, capacidad 1 da cadena vacia. m NULL o cantidad==0 produce Monticulo vacio. No reserva/libera/imprime stdout.
 * @pre Los incrementos de nivel y duplicaciones de limite_nivel ejecutados deben caber en int; no certifica arboles de indices enormes.
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

/*
 * @brief Libera completamente la memoria reservada por el montículo.
 *
 * @param m Puntero al montículo a destruir.
 *
 * @note Tras ejecutarse, la cantidad y la capacidad se reinician a 0.
 * @note Complejidad temporal: O(1).
 */
/**
 * @brief Libera completamente la memoria reservada por el montículo.
 *
 * @param[in,out] m Puntero al montículo a destruir.
 *
 * @details Si m es NULL no hace nada. Si datos no es NULL libera ese buffer,
 * incluso con cantidad 0, y asigna datos NULL antes de reiniciar los contadores.
 * No modifica tipo. Los alias del buffer liberado no se deben evaluar ni usar.
 * Esta funcion no reinicializa ni reserva memoria: el llamador visible Limpiar
 * invoca despues monticulo_inicializar con capacidad solicitada 16 (reserva 20
 * si tiene exito; si falla, datos NULL y capacidad 0). Es otra vida de memoria.
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
