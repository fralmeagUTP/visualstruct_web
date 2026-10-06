#ifndef TAD_AVL_H
#define TAD_AVL_H

/**
 * @file tad_avl.h
 * @brief TAD Arbol AVL de enteros.
 */

/**
 * @brief Nodo de arbol AVL.
 * @note En una representacion AVL estable, FE es altura(der)-altura(izq), los
 * enlaces padre/hijos son consistentes y la raiz tiene padre NULL. El tipo no
 * impone estas reglas: asignaciones intermedias de una mutacion pueden no cumplirlas.
 * Copiar el nodo o el alias AVL no copia reservas ni crea propiedad independiente.
 */
typedef struct nodoAVL {
    int nro; /**< Dato entero almacenado. */
    int FE; /**< Factor de equilibrio: altura del hijo derecho menos altura del izquierdo. */
    struct nodoAVL *der; /**< Hijo derecho. */
    struct nodoAVL *izq; /**< Hijo izquierdo. */
    struct nodoAVL *padre; /**< Enlace al padre del nodo. */
} nodoAVL;

/** @brief Alias de puntero al nodo AVL. */
typedef nodoAVL* AVL;

/**
 * @brief Muestra el árbol AVL de forma visual (rotado 90°).
 * @param arbol Raíz del árbol a mostrar.
 * @param n Nivel de profundidad actual (usar 0 al invocar).
  * @note NULL no produce salida. Imprime primero el subarbol derecho, despues el nodo y luego el izquierdo; usa tres espacios por nivel y salto de linea por valor. No es recorrido inorden ascendente ni modifica enlaces.
 */
void avl_verArbol(AVL arbol, int n);
/**
 * @brief Indica si un nodo es hoja.
 * @param nodo Nodo a evaluar (puede ser NULL).
 * @return 1 si no tiene hijos, 0 en otro caso.
  * @note NULL retorna 0. Un nodo vivo sin hijos retorna 1; consultar no reserva ni libera memoria.
 */
int avl_esHoja(AVL nodo);
/**
 * @brief Calcula la avl_altura del árbol (número de niveles).
 * @param arbol Raíz del árbol.
 * @return Altura del árbol (0 si está vacío).
  * @note Cuenta niveles: vacio 0 y hoja 1. Calcula las alturas recursivamente sin consultar ni modificar FE o enlaces; no cuenta nodos.
 */
int avl_altura(AVL arbol);
/**
 * @brief Rotación simple derecha (avl_RSD).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso IZQUIERDA-IZQUIERDA o punto de rotación).
 * @pre Enlaces finitos y aciclicos, padres consistentes y FE exacto en el subarbol rotado.
 * @note Las identidades y valores de A/B/C se conservan; no reserva ni libera. Reenlaza padre o raiz y los padres de hijos transferidos. Con FE previo correcto en el subarbol, calcula el FE posterior de A y luego B mediante identidades de altura en O(1), incluyendo hijo FE0 tras eliminar. No presupone ambos FE finales cero. Factores de ancestros son responsabilidad del llamador; los enlaces/FE intermedios no certifican un AVL final.
 * @note r/nodo NULL o hijo requerido ausente hacen la operacion vacia; no valida punteros invalidos.
 */
void avl_RSD(AVL *r, AVL nodo);
/**
 * @brief Rotación simple izquierda (avl_RSI).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso DERECHA-DERECHA o punto de rotación).
 * @pre Enlaces finitos y aciclicos, padres consistentes y FE exacto en el subarbol rotado.
 * @note Espejo de RSD: conserva identidades/valores sin reservar ni liberar; actualiza raiz/padres/hijo transferido. Calcula FE posterior de A y luego B en O(1) a partir de factores previos correctos. Incluye hijo FE0 tras eliminar; no pone ambos FE a cero. Ancestros se mantienen en el llamador y los estados intermedios no son una certificacion AVL.
 * @note r/nodo NULL o hijo requerido ausente hacen la operacion vacia; no valida punteros invalidos.
 */
void avl_RSI(AVL *r, AVL nodo);
/**
 * @brief Rotación doble derecha (avl_RDD).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso IZQUIERDA-DERECHA).
 * @pre Enlaces finitos y aciclicos, padres consistentes y FE exacto en el subarbol rotado.
 * @note Compone RSI sobre el hijo izquierdo y RSD sobre A. No preasigna FE antes de esas rotaciones: cada simple necesita los factores exactos de su topologia de entrada y mantiene los posteriores. Cubre nieto FE-1/0/1. Conserva identidades/valores, no reserva/libera ni introduce una nueva API. Ancestros requieren mantenimiento por el llamador.
 * @note r/nodo NULL o hijo requerido ausente hacen la operacion vacia; no valida punteros invalidos.
 */
void avl_RDD(AVL *r, AVL nodo);
/**
 * @brief Rotación doble izquierda (avl_RDI).
 * @param r Referencia a la raíz del árbol.
 * @param nodo Nodo desequilibrado (caso DERECHA-IZQUIERDA).
 * @pre Enlaces finitos y aciclicos, padres consistentes y FE exacto en el subarbol rotado.
 * @note Compone RSD sobre el hijo derecho y RSI sobre A, conservando FE de entrada exactos hasta cada simple. Cubre nieto FE-1/0/1 sin preasignaciones que invaliden las formulas. Conserva valores/reservas; publica enlaces padre/raiz sin reservar ni liberar. El llamador mantiene FE de ancestros.
 * @note r/nodo NULL o hijo requerido ausente hacen la operacion vacia; no valida punteros invalidos.
 */
void avl_RDI(AVL *r, AVL nodo);
/**
 * @brief Inserta un valor en el árbol AVL.
 * @param raiz Referencia a la raíz del árbol.
 * @param x Valor a avl_insertar (no se insertan duplicados).
 * @pre raiz apunta a una variable valida (o es NULL); su arbol inicial tiene enlaces finitos/aciclicos, orden estricto, padres consistentes y FE exactos de un AVL equilibrado.
 * @note Retorna void: referencia raiz NULL, duplicado o fallo de malloc no producen estado de error retornado ni cambian el arbol. La API web rechaza duplicados antes de mutar; no equivale a ejecutar este cuerpo C.
 * @note Un valor nuevo reserva exactamente un nodo, inicializa nro/FE/hijos/padre y luego lo publica mediante raiz o enlace del padre. Los campos de malloc no se leen antes de inicializarlos.
 * @note Conserva identidades/valores de nodos previos; no libera reservas ni imprime. Recorre con padre/actual, propaga FE con n/padre y compone las rotaciones necesarias; enlaces y FE parciales no certifican un AVL terminado.
 * @note Cada nueva reserva queda propiedad del llamador hasta liberarla con avl_liberarAVL. No modifica referencias prestadas externas; pueden cambiar los enlaces/raiz pero no la identidad de reservas previas.
 */
void avl_insertar(AVL *raiz, int x);
/**
 * @brief Elimina el valor indicado del árbol AVL (con rebalanceo).
 * @param raiz Referencia a la raíz del árbol.
 * @param x Valor a avl_eliminar.
 * @pre raiz es NULL o referencia una variable valida con un AVL finito/aciclico, orden estricto, padres consistentes y FE exactos.
 * @note Retorna void. Referencia raiz NULL, vacio o valor ausente dejan el arbol sin cambios; la API web rechaza vacio/ausencia antes de mutar y no equivale a ejecutar este cuerpo C.
 * @note Con dos hijos intercambia nro con el sucesor minimo del hijo derecho, conservando las reservas durante el intercambio. Despues libera la reserva del sucesor, no necesariamente la reserva encontrada inicialmente.
 * @note Con cero/un hijo reenlaza raiz o padre y actualiza el padre del hijo antes de free. Libera exactamente una reserva si encuentra x; no reserva memoria ni imprime. Los alias a la reserva liberada dejan de ser utilizables; la reserva retenida puede cambiar de valor.
 * @note Reequilibra desde el padre de la reserva retirada mediante alturas y rotaciones. Identidades vivas se conservan; los enlaces, orden y FE intermedios no certifican un AVL final. El llamador mantiene propiedad del arbol restante y debe liberarlo al terminar.
 */
void avl_eliminar(AVL *raiz, int x);
/**
 * @brief Busca un valor en el árbol AVL.
 * @param raiz Raíz del árbol.
 * @param x Valor a avl_buscar.
 * @return Puntero al nodo con el valor o NULL si no se encuentra.
  * @note Retorna un alias prestado a una reserva existente o NULL por ausencia/vacio. No reserva, libera ni modifica enlaces. El alias deja de ser utilizable cuando se libera esa reserva.
 */
AVL avl_buscar(AVL raiz, int x);
/**
 * @brief Obtiene el nodo con el valor mínimo del subárbol dado.
 * @param nodo Raíz del subárbol.
 * @return Puntero al nodo con el valor mínimo.
 * @pre nodo debe ser distinto de NULL.
  * @note Requiere nodo no NULL y enlaces validos. Recorre izquierdo cambiando solo su alias local y retorna un alias prestado; no modifica la raiz, reserva ni libera memoria. El llamador debe comprobar el vacio.
 */
AVL avl_minimo(AVL nodo);
/**
 * @brief Libera toda la memoria del árbol AVL (postorden).
 * @param raiz Raíz del árbol a liberar.
  * @note Libera hijos izquierdo/derecho antes del padre. Recibe la raiz por valor y no pone a NULL la raiz del llamador: asignar NULL despues de esta llamada. Los alias a reservas liberadas dejan de ser utilizables; NULL no tiene efecto.
 */
void avl_liberarAVL(AVL raiz);

#endif
