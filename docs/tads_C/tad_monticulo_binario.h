#ifndef MONTICULO_BINARIO_H
#define MONTICULO_BINARIO_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_monticulo_binario.h
 * @brief TAD Monticulo binario (min o max heap) sobre arreglo dinamico.
 */

/**
 * @brief Selector de la comparacion de prioridad del monticulo.
 * @note Use uno de los dos enumeradores declarados. La inicializacion no valida
 * el selector; comparar usa menor para MIN y mayor para cualquier otro valor.
 */
typedef enum {
    MONTICULO_MIN = 0,  /**< Menor valor tiene prioridad; comparacion estricta. */
    MONTICULO_MAX = 1   /**< Mayor valor tiene prioridad; comparacion estricta. */
} TipoMonticulo;

/**
 * @brief Monticulo propietario de un arreglo dinamico de ints.
 * @note Estado inicializado: 0<=cantidad<=capacidad; los primeros cantidad
 * elementos estan inicializados. datos es NULL sin reserva, o una reserva de
 * capacidad ints. El tipo no valida heap ni contadores. Copiar la estructura
 * comparte datos: no crea copia independiente; destruir libera la reserva
 * propia y los aliases al arreglo dejan de ser utilizables.
 */
typedef struct {
    int *datos; /**< Arreglo de datos del montículo. */
    int cantidad; /**< Número de elementos almacenados. */
    int capacidad; /**< Capacidad reservada de la estructura. */
    TipoMonticulo tipo; /**< Tipo de montículo mínimo o máximo. */
} MonticuloBinario;

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
void monticulo_inicializar(MonticuloBinario *m, TipoMonticulo tipo, int capacidad_inicial);
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
bool monticulo_insertar(MonticuloBinario *m, int valor);
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
bool monticulo_raiz(const MonticuloBinario *m, int *resultado);
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
bool monticulo_extraer_raiz(MonticuloBinario *m, int *resultado);
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
bool monticulo_eliminar_valor(MonticuloBinario *m, int valor);
/**
 * @brief Verifica si el montículo está vacío.
 * 
 * @param[in] m Puntero constante al montículo.
 * @return @c true si no hay elementos o el puntero es NULL.
 * 
 * @note Complejidad temporal: O(1).
 * @note Consulta cantidad==0 o m NULL sin validar datos/metadata; no reserva/libera ni modifica.
 */
bool monticulo_vacio(const MonticuloBinario *m);
/**
 * @brief Retorna la cantidad de elementos en el montículo.
 * 
 * @param[in] m Puntero constante al montículo.
 * @return La cantidad de elementos, o 0 si m es NULL.
 * 
 * @note Complejidad temporal: O(1).
 * @note Devuelve contador almacenado sin normalizar/recontar; m prestado inicializado o NULL. No reserva/libera ni modifica.
 */
int monticulo_cantidad(const MonticuloBinario *m);
/**
 * @brief Retorna la capacidad total de almacenamiento actual del montículo.
 * 
 * @param[in] m Puntero constante al montículo.
 * @return Capacidad (en número de elementos), o 0 si m es NULL.
 * 
 * @note Complejidad temporal: O(1).
 * @note Devuelve capacidad almacenada sin validar reserva; m prestado inicializado o NULL. No reserva/libera ni modifica.
 */
int monticulo_capacidad(const MonticuloBinario *m);
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
bool monticulo_construir(MonticuloBinario *m, const int *valores, int cantidad);
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
int monticulo_copiar_valores(const MonticuloBinario *m, int *destino, int capacidad);
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
void monticulo_formatear_arreglo(const MonticuloBinario *m, char *destino, size_t capacidad);
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
void monticulo_formatear_arbol(const MonticuloBinario *m, char *destino, size_t capacidad);
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
void monticulo_destruir(MonticuloBinario *m);

#endif
