//---------------------------------------------------------------------------
/**
 * @file tad_grafo.c
 * @brief Definición de un grafo dirigido y funciones asociadas.
 *
 * Este archivo contiene la definición de un grafo dirigido utilizando listas
 * enlazadas y funciones para manipularlo, incluyendo la inserción de vértices
 * y arcos, eliminación, búsqueda y recorridos (grafo_bfs y grafo_dfs).
 *
 * @author [Tu Nombre]
 * @date [Fecha]
 */

//---------------------------------------------------------------------------
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "tad_cola.h"


//----------------------------------------------------------------------------
/**
 * @brief Nodo de vértice en el grafo.
 */
typedef struct NodoV {
    int dato; /**< Identificador del vértice. */
    struct NodoV* sig; /**< Enlace al siguiente nodo. */
    int marcado; /**< Marca de visita usada por recorridos. */
} *ListaVertice; /**< Alias de puntero a nodo o cabeza de vertices; NULL es lista vacia. */

//----------------------------------------------------------------------------
/**
 * @brief Nodo de arco en el grafo.
 */
typedef struct NodoA {
    int origen; /**< Identificador del vértice origen. */
    int destino; /**< Identificador del vértice destino. */
    int costo; /**< Peso entero del arco. */
    struct NodoA* sig; /**< Enlace al siguiente nodo. */
} *ListaArco; /**< Alias de puntero a nodo o cabeza de arcos; NULL es lista vacia. */

//----------------------------------------------------------------------------
/**
 * @brief Par de cabezas de listas de vertices y arcos, recibido por valor.
 * @note Copiar Grafo comparte nodos; no reserva, libera ni crea un propietario
 * independiente. v y a son listas vivas aciclicas o NULL bajo sus contratos.
 * El tipo no contiene bandera de direccion ni comprueba extremos de los arcos;
 * eliminar un vertice no elimina automaticamente sus arcos incidentes.
 */
typedef struct nodoGrafo {
    ListaVertice v; /**< Cabeza de la lista de vértices. */
    ListaArco a; /**< Cabeza de la lista de arcos. */
} Grafo;


//---------------------------------------------------------------------------
/**
 * @brief Crea un grafo vacío.
 * @return Grafo - Un grafo vacío.
 */
Grafo grafo_crear(void) {
      Grafo g;
    g.v = NULL;
    g.a = NULL;
      return g;
  }
      
//----------------------------------------------------------------------------
/**
 * @brief Reserva un vertice al inicio si el identificador no existe.
 * @param[in,out] g Grafo inicializado por valor con lista propia de vertices.
 * @param[in] x Identificador int, incluidos negativos y extremos.
 * @return Grafo con nueva cabeza, o g sin cambios ante duplicado o fallo malloc.
 * @pre Lista propia viva y aciclica o NULL.
 * @note Nuevo nodo tiene marcado=0 y pertenece al grafo; caller administra su liberacion. Retorno no comunica causa de fallo y no hay diagnostico.
 * @note Para publicar una nueva cabeza el caller asigna el retorno; no copia los nodos anteriores ni modifica arcos.
 */
Grafo grafo_insertar_vertice(Grafo g, int x) {
    ListaVertice actual = g.v;
    while (actual != NULL) {
        if (actual->dato == x) return g;
        actual = actual->sig;
    }
    ListaVertice nuevo = (ListaVertice)malloc(sizeof(struct NodoV));
    if (nuevo == NULL) return g;
    
    nuevo->sig = g.v;
    nuevo->dato = x;
    nuevo->marcado = 0;
    g.v = nuevo;
    return g;
}

//-------------------------------------------------------------------------------
/**
 * @brief Intenta crear extremos y actualiza o reserva un arco dirigido.
 * @param[in,out] g Grafo inicializado por valor con listas propias vivas y aciclicas.
 * @param[in] x Identificador origen int.
 * @param[in] y Identificador destino int.
 * @param[in] z Costo int, admite negativos y extremos.
 * @return Grafo resultante, posiblemente parcial si alguna reserva falla.
 * @note Llama primero insertar_vertice(x) e insertar_vertice(y). Si el arco ya existe, actualiza el costo del primer coincidente sin reservar otro arco.
 * @note Si no existe, reserva y prepend un NodoA. Fallo malloc conserva vertices ya creados; no rollback ni estado de error separado. Fallo al crear extremos no impide intentar reservar el arco, por lo que no garantiza extremos presentes.
 * @note Caller asigna retorno y administra nodos propios; actualizar un arco compartido se observa por aliases. No crea automaticamente el sentido inverso.
 */
Grafo grafo_insertar_arco(Grafo g, int x, int y, int z) {
    ListaArco existente;
    g = grafo_insertar_vertice(g, x);
    g = grafo_insertar_vertice(g, y);
    existente = g.a;
    while (existente != NULL) {
        if (existente->origen == x && existente->destino == y) {
            existente->costo = z;
            return g;
        }
        existente = existente->sig;
    }
    ListaArco nuevo = (ListaArco)malloc(sizeof(struct NodoA));
    if (nuevo == NULL) return g;
    
    nuevo->sig = g.a;
    nuevo->origen = x;
    nuevo->destino = y;
    nuevo->costo = z;
    g.a = nuevo;
   return g;
}


//------------------------------------------------------------------------------
/**
 * @brief Imprime la lista de vértices del grafo
 * @param g Grafo del cual se imprimirán los vértices
 */
void grafo_imprimir_vertices(Grafo g)
{
     ListaVertice k=g.v;
     while (k!=NULL)
     {
           printf(" \n%d     %d",k->dato, k->marcado);
           k=k->sig;
           }
 }


//----------------------------------------------------------------------
/**
 * @brief Imprime la lista de arcos del grafo
 * @param g Grafo del cual se imprimirán los arcos
*/
void grafo_imprimir_arcos(Grafo g)
{
     ListaArco k=g.a;
     while (k!=NULL)
     {
           printf(" \n%d    %d     %d",k->origen, k->destino, k->costo);
           k=k->sig;
           }
 }


//------------------------------------------------------------------
/**
 * @brief Devuelve la cabeza compartida de vertices sin copiar nodos.
 * @param[in] g Grafo inicializado por valor.
 * @return g.v tal cual, incluida NULL para lista vacia.
 * @note Referencia prestada: no reserva, libera ni transfiere nueva propiedad. Escribir por el alias modifica los nodos originales; liberar nodos requiere coordinar al propietario, no tratar el resultado como copia independiente.
 */         
ListaVertice grafo_vertices (Grafo g)
 {
     return g.v;
 }


//---------------------------------------------------------------
/**
 * @brief Devuelve la cabeza compartida de arcos sin copiar nodos.
 * @param[in] g Grafo inicializado por valor.
 * @return g.a tal cual, incluida NULL para lista vacia.
 * @note Referencia prestada: no reserva, libera ni transfiere nueva propiedad. Escribir por el alias modifica los nodos originales; liberar nodos requiere coordinar al propietario, no tratar el resultado como copia independiente.
 */         
ListaArco grafo_arcos (Grafo g)
 {
     return g.a;
 }


//------------------------------------------------------------------
/**
 * @brief Sustituye la cabeza de vertices en la copia por valor.
 * @param[in] g Grafo inicializado por valor.
 * @param[in] k Nueva cabeza prestada; NULL admitido.
 * @return Grafo con v=k y la otra cabeza conservada.
 * @note No copia, reserva, libera ni valida nodos. El caller debe usar el retorno para cambiar su cabeza; los demas aliases conservan las referencias anteriores.
 * @note No libera la lista sustituida ni define ownership nuevo: el caller administra las reservas y conserva la referencia anterior si necesita liberarla.
 */
Grafo grafo_cambiar_vertices (Grafo g, ListaVertice k)
{
   g.v = k;
   return g;
}


//----------------------------------------------------------------------
/**
 * @brief Sustituye la cabeza de arcos en la copia por valor.
 * @param[in] g Grafo inicializado por valor.
 * @param[in] k Nueva cabeza prestada; NULL admitido.
 * @return Grafo con a=k y la otra cabeza conservada.
 * @note No copia, reserva, libera ni valida nodos. El caller debe usar el retorno para cambiar su cabeza; los demas aliases conservan las referencias anteriores.
 * @note No libera la lista sustituida ni define ownership nuevo: el caller administra las reservas y conserva la referencia anterior si necesita liberarla.
 */
Grafo grafo_cambiar_arcos (Grafo g, ListaArco k)
{
   g.a = k;
   return g;
}


//--------------------------------------------------------------------------------
/**
 * @brief Consulta exclusivamente si la cabeza de vertices es NULL.
 * @param[in] g Grafo inicializado por valor.
 * @return 1 si g.v==NULL, 0 en otro caso.
 * @note No inspecciona g.a: puede devolver 1 aunque haya arcos almacenados. No recorre, reserva, libera ni modifica nodos.
 */
int grafo_vacio (Grafo g)
       // Devuelve verdadero si el grafo es vacio
    {
      if (g.v==NULL)
         return 1;
      else
         return 0;
    }


//--------------------------------------------------------------------------
/**
 * @brief Verifica si el vértice existe en el grafo
 * @param g Grafo del cual se verificará la existencia del vértice
 * @param x Vértice a buscar
 * @return int - 1 si el vértice existe, 0 en caso contrario
*/
int grafo_existe_vertice (Grafo g, int x)
{
    ListaVertice k=g.v;

    while ((k!=NULL) && (k->dato != x))
       k=k->sig;
    if (k==NULL)
       return 0;
    else
       return 1;
}


//--------------------------------------------------------------------------
/**
 * @brief Verifica si el arco existe en el grafo
 * @param g Grafo del cual se verificará la existencia del arco
 * @param x Vértice origen
 * @param y Vértice destino
 * @return int - 1 si el arco existe, 0 en caso contrario
*/
int grafo_existe_arco (Grafo g, int x, int y)
{
    ListaArco k=g.a;

    while ((k!=NULL) && ((k->origen != x) || (k->destino != y)))
       k=k->sig;
    if (k==NULL)
       return 0;
    else
       return 1;
}


//--------------------------------------------------------------------------
/**
 * @brief Desenlaza y libera el primer vertice coincidente; conserva los arcos.
 * @param[in,out] g Grafo por valor con lista propia de vertices.
 * @param[in] x Identificador int a buscar.
 * @return Grafo con cabeza actualizada; vacio o ausencia no cambian nodos.
 * @pre Lista propia viva y aciclica; nodos liberables sin ownership compartido.
 * @note No elimina arcos incidentes: sus identificadores pueden quedar sin vertice asociado. No reserva ni imprime.
 * @note Caller asigna retorno para cambiar cabeza; aliases al nodo liberado quedan indeterminados y no deben leerse ni usarse. Los demas nodos se comparten, no se copian.
 */
Grafo grafo_eliminar_vertice (Grafo g, int x)
{
    ListaVertice k=g.v, p;

    if (g.v!=NULL)
        {
           if (g.v->dato == x)
             {
              g.v = g.v->sig;
              free(k);
              }
           else
             {
               while ((k->sig != NULL) && (k->sig->dato != x))
                  k=k->sig;
               if (k->sig!=NULL)
                  {
                     p=k->sig;
                     k->sig=p->sig;
                     free(p);
                  }
             }
        }
     return g;
 }


//----------------------------------------------------------------------
/**
 * @brief Desenlaza y libera el primer arco con origen y destino coincidentes.
 * @param[in,out] g Grafo por valor con lista propia de arcos.
 * @param[in] x Identificador origen.
 * @param[in] y Identificador destino.
 * @return Grafo con cabeza de arcos actualizada; ausencia conserva el grafo.
 * @pre Lista propia viva y aciclica; reservas liberables sin ownership compartido.
 * @note No borra vertices ni arco de sentido inverso. No reserva; imprime diagnostico solo si elimina un nodo posterior a la cabeza.
 * @note Caller asigna retorno para nueva cabeza; aliases al nodo liberado quedan indeterminados y no se deben leer ni usar.
 */
Grafo grafo_eliminar_arco (Grafo g, int x, int y)
{
    ListaArco k=g.a, p;

    if (g.a!=NULL)
        {
           if ((g.a->origen == x) && (g.a->destino == y))
             {
              g.a = g.a->sig;
              free(k);
              }
           else
             {
               while ((k->sig != NULL) && !((k->sig->origen == x) && (k->sig->destino == y)))
                  k=k->sig;
               if (k->sig!=NULL)
                  {
                     p=k->sig;
                     printf("\n el arco a borrar es %d   %d",p->origen,p->destino);
                     k->sig=p->sig;
                     free(p);
                  }
             }
        }
     return g;
 }
 
 
//-------------------------------------------------------------------------------- 
/**
 * @brief Retorna el costo del arco que parte del vértice x al vértice y del grafo
 * @param g Grafo del cual se retornará el costo del arco
 * @param x Vértice origen
 * @param y Vértice destino
 * @return Costo del arco, o -1 si no existe; un arco válido también puede tener costo -1.
 * @note Para distinguir ausencia de costo -1, consultar grafo_existe_arco.
*/
  int grafo_costo_arco (Grafo g, int x, int y)
  {
    ListaArco k=g.a;

    while (k != NULL)
      {
       if ((k->origen == x) && (k->destino == y))
          return k->costo;
       k=k->sig;
      }
    return -1;       // no encontró el arco
  }


//---------------------------------------------------------------------------
/**
 * @brief Cuenta nodos almacenados de vertices.
 * @param[in] g Grafo inicializado por valor con lista prestada.
 * @return Numero de nodos de g.v; 0 si la cabeza es NULL.
 * @pre Lista viva, aciclica y con numero de nodos <= INT_MAX.
 * @note No valida identificadores, consistencia de extremos ni unicidad; no reserva/libera/imprime ni modifica. No certifica contadores fuera del rango int.
 */
int grafo_orden(Grafo g)
  {
    int orden=0;
    ListaVertice k=g.v;

    while (k != NULL)
      {
        orden++;
        k=k->sig;
      }
    return orden;
  }


//-------------------------------------------------------------------------------
/**
 * @brief Cuenta nodos almacenados de arcos.
 * @param[in] g Grafo inicializado por valor con lista prestada.
 * @return Numero de nodos de g.a; 0 si la cabeza es NULL.
 * @pre Lista viva, aciclica y con numero de nodos <= INT_MAX.
 * @note No valida identificadores, consistencia de extremos ni unicidad; no reserva/libera/imprime ni modifica. No certifica contadores fuera del rango int.
 */
int grafo_tamano(Grafo g)
  {
    int tamano=0;
    ListaArco k=g.a;

    while (k != NULL)
      {
        tamano++;
        k=k->sig;
      }
    return tamano;
  }


//--------------------------------------------------------------------
/**
 * @brief Cuenta arcos almacenados cuyo origen es x (grado de salida).
 * @param[in] g Grafo inicializado por valor con lista de arcos prestada.
 * @param[in] x Identificador origen a contar.
 * @return Numero de coincidencias de origen, 0 si no hay; no exige que exista vertice x.
 * @pre Lista de arcos viva y aciclica; contador resultante <= INT_MAX.
 * @note No cuenta entradas; un bucle con origen x aporta uno. No valida simetria/direccion ni reserva/libera/imprime/modifica.
 */
int grafo_grado_vertice(Grafo g, int x)
   {
      int grado=0;
      ListaArco k=g.a;
   
      while (k != NULL)
         {
         if (k->origen == x)
            grado++;
         k=k->sig;
         }
      return grado;
   }


//----------------------------------------------------------------------
/**
 * @brief Escribe cero en la marca del primer vertice cuyo dato coincide.
 * @param[in,out] g Copia por valor con nodos de vertices compartidos modificables.
 * @param[in] x Identificador int buscado, incluidos negativos.
 * @return La misma pareja de cabezas; ausencia conserva todas las marcas.
 * @pre Lista de vertices viva y aciclica o NULL.
 * @note No reserva/libera ni imprime. La escritura es visible por aliases a nodos aunque el caller no asigne el retorno; no cambia arcos.
 */
Grafo grafo_desmarcar_vertice (Grafo g, int x)
{
    ListaVertice k=g.v;
    while (k!=NULL)
        {
           if (k->dato == x)
             {
              k->marcado = 0;
              k=NULL;
             }
           else
             k=k->sig;
        }
     return g;
 }


//----------------------------------------------------------------------------------
/**
 * @brief Pone a cero las marcas de todos los nodos de vertices compartidos.
 * @param[in,out] g Copia por valor del grafo; listas validas o NULL.
 * @return La misma pareja de cabezas; no reserva ni libera nodos.
 * @note Copiar Grafo no copia sus nodos: las escrituras se observan en los aliases.
 */
Grafo grafo_desmarcar(Grafo g) {
    ListaVertice k = g.v;
    while (k != NULL) {
              k->marcado = 0;
        k = k->sig;
        }
     return g;
 }

//----------------------------------------------------------------------------------
/**
 * @brief Escribe 1 en la marca del primer vertice cuyo dato es x.
 * @param[in,out] g Grafo por valor con nodos prestados validos.
 * @param x Identificador entero, incluidos negativos y -1.
 * @return La misma pareja de cabezas; si x no existe no cambia nodos.
 * @note No reserva ni libera memoria; el grafo vacio es valido.
 */
Grafo grafo_marcar_vertice(Grafo g, int x) {
    ListaVertice k = g.v;
    while (k != NULL) {
        if (k->dato == x) {
            k->marcado = 1;
            break;
        }
        k = k->sig;
        }
     return g;
 }

//----------------------------------------------------------------------------------
/**
 * @brief Consulta la marca almacenada del primer vertice coincidente.
 * @param g Grafo prestado por valor; listas validas o NULL.
 * @param x Identificador entero buscado.
 * @return Valor int de marcado, o 0 si x no existe; no normaliza otro valor a 1.
 * @note No modifica nodos ni transfiere propiedad.
 */
int grafo_marcado_vertice(Grafo g, int x) {
    ListaVertice k = g.v;
    while (k != NULL) {
        if (k->dato == x) {
            return k->marcado;
        }
        k = k->sig;
        }
     return 0;
 }    

/**
 * @brief Libera todos los nodos de una lista de arcos.
 * @param lista Cabeza de la lista; NULL es válido.
 */
static void liberarListaArcos(ListaArco lista) {
    while (lista != NULL) {
        ListaArco tmp = lista;
        lista = lista->sig;
        free(tmp);
    }
}

/**
 * @brief Busca un valor en un arreglo de identificadores.
 * @param vertices Arreglo con al menos n posiciones.
 * @param n Número de posiciones a consultar.
 * @param valor Identificador buscado.
 * @return Primer índice coincidente, o -1 si no existe.
 */
static int indiceVertice(const int *vertices, int n, int valor) {
    int i;
    for (i = 0; i < n; i++) {
        if (vertices[i] == valor) {
            return i;
        }
    }
    return -1;
}

/**
 * @brief Copia los identificadores del grafo al arreglo.
 * @param g Grafo fuente.
 * @param vertices Salida con capacidad n.
 * @param n Número de identificadores esperado.
 * @return 1 si se copiaron n identificadores; 0 en otro caso.
 */
static int inicializarVectorVertices(Grafo g, int *vertices, int n) {
    int i = 0;
    ListaVertice v = grafo_vertices(g);
    while (v != NULL && i < n) {
        vertices[i++] = v->dato;
        v = v->sig;
    }
    return i == n;
}

//------------------------------------------------------------------------------    
/**
 * @brief Reserva una lista independiente de destinos de arcos cuyo origen es x.
 * @param g Grafo prestado por valor; lista de arcos valida o NULL.
 * @param x Identificador entero de origen; no exige que exista un vertice x.
 * @return Lista nueva, o NULL sin coincidencias/reservas; el caller libera cada nodo.
 * @note Ante fallo malloc omite ese destino y sigue; puede retornar lista parcial.
 * @note Prepend invierte el orden de recorrido de la lista de arcos; marcado es 0.
 * @note No modifica marcas ni enlaces del grafo original y no imprime salida.
 */
ListaVertice grafo_sucesores(Grafo g, int x) {
    ListaArco k = g.a;
    ListaVertice ver = NULL, nuevo;

    while (k != NULL) {
        if (k->origen == x) {
            nuevo = (ListaVertice)malloc(sizeof(struct NodoV));
            if (nuevo != NULL) {
                nuevo->sig = ver;
                nuevo->dato = k->destino;
                nuevo->marcado = 0;
                ver = nuevo;
            }
        }
        k = k->sig;
      }
   return ver;
}

//------------------------------------------------------------------------------
/**
 * @brief Reserva una lista independiente de origenes de arcos cuyo destino es x.
 * @param[in] g Grafo inicializado por valor con arcos prestados.
 * @param[in] x Identificador destino; no exige vertice x presente.
 * @return Lista nueva propia, o NULL sin coincidencias/reservas; caller libera cada nodo.
 * @pre Lista de arcos viva y aciclica o NULL.
 * @note Cada nodo nuevo tiene marcado=0. Prepend invierte el orden del barrido de arcos; puede repetir origenes. No modifica grafo ni libera sus nodos.
 * @note Fallo malloc omite ese origen y continua: puede devolver lista parcial sin flag de error. Imprime predecesor solo para cada nodo cuya reserva tuvo exito.
 */
ListaVertice grafo_predecesores(Grafo g, int x)
{
   ListaArco k=g.a;
   ListaVertice ver=NULL, nuevo;

    while (k != NULL)
      {
       if (k->destino == x)
          {  // se agrega a la lista el origen del arco como predecesor de x
            nuevo=(ListaVertice) malloc(sizeof (struct NodoV));
            if (nuevo != NULL) {
                nuevo->sig=ver;
                nuevo->dato=k->origen;
                nuevo->marcado=0;   // el vertice no esta marcado
                ver=nuevo;
                printf("\npredecesor %d  ",nuevo->dato);
            }
          }
       k=k->sig;
      }
   return ver;
}

//------------------------------------------------------------------------------
/**
 * @brief Recorre desde inicio con FIFO y publica una lista nueva en orden BFS.
 * @param[in,out] g Grafo por valor con nodos prestados validos; comparte sus marcas.
 * @param inicio Identificador entero inicial, incluidos negativos y -1.
 * @return Lista nueva de vertices procesados; NULL si inicio no existe o no obtiene nodos.
 * @note Desmarca primero, incluso si inicio falta; luego marca al intentar encolar.
 * @note El caller libera todos los nodos del resultado; sus marcas propias son 0.
 * @note Cola y listas de sucesores son temporales y se liberan durante la ruta normal.
 * @note Fallos de reserva pueden omitir vertices o dar resultado parcial/NULL. Si
 *       cola_encolar falla, BFS puede marcar un vertice que no sera procesado.
 * @note La guarda de cola no vacia permite extraer -1 como dato valido, no como error.
 * @note Ignora costos: minimiza cantidad de arcos, no peso. Este TAD barre listas de
 *       vertices/arcos repetidamente: cota O(V*(V+E)), no O(V+E) de una implementacion
 *       con adyacencia directa y consulta de marcas constante.
 */
ListaVertice grafo_bfs(Grafo g, int inicio) {
    g = grafo_desmarcar(g);
    struct Cola cola = {NULL, NULL};
    ListaVertice recorrido = NULL;
    ListaVertice ultimo = NULL;

    // Verifica si el vértice de inicio existe
    ListaVertice v = g.v;
    int existe = 0;
    while (v != NULL) {
        if (v->dato == inicio) {
            existe = 1;
            break;
        }
        v = v->sig;
    }

    if (!existe) return NULL;

    cola_encolar(&cola, inicio);
    g = grafo_marcar_vertice(g, inicio);

    while (cola.delante != NULL) {
        int actual = cola_desencolar(&cola);
        // La cola no vacía garantiza extracción; -1 es un identificador válido.

        // Agregar al recorrido
        ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));
        if (tmp == NULL) continue;

        tmp->dato = actual;
        tmp->marcado = 0;
        tmp->sig = NULL;
        if (recorrido == NULL) recorrido = tmp;
        else ultimo->sig = tmp;
        ultimo = tmp;

        // Explorar grafo_sucesores
        ListaVertice suces = grafo_sucesores(g, actual);
        while (suces != NULL) {
            if (!grafo_marcado_vertice(g, suces->dato)) {
                cola_encolar(&cola, suces->dato);
                g = grafo_marcar_vertice(g, suces->dato);
            }
            ListaVertice temp = suces;
            suces = suces->sig;
            free(temp);
        }
    }

    return recorrido;
}


//----------------------------------------------------------------------------
/**
 * @brief Agrega al final un nodo ya reservado del recorrido.
 * @param recorrido Dirección válida de la cabeza del recorrido.
 * @param nuevo Nodo no NULL cuya propiedad se transfiere a la lista.
 * @note Requiere recorrido no NULL y lista aciclica valida. Inicializa nuevo->sig
 * antes de publicar la cabeza/enlace; recorre hasta la cola en cada insercion.
 * No reserva ni libera memoria; los nodos publicados quedan a cargo del caller.
 */
static void grafo_agregar_recorrido(ListaVertice *recorrido, ListaVertice nuevo) {
    ListaVertice ultimo;
    nuevo->sig = NULL;
    if (*recorrido == NULL) { *recorrido = nuevo; return; }
    ultimo = *recorrido;
    while (ultimo->sig != NULL) ultimo = ultimo->sig;
    ultimo->sig = nuevo;
}

/**
 * @brief Marca un vértice y agrega su recorrido en profundidad.
 * @param g Grafo cuyos nodos de vértice se marcan.
 * @param actual Vértice actual, que debe pertenecer al grafo.
 * @param recorrido Dirección de una lista de recorrido; NULL se ignora.
 * @note Comparte los nodos y marcas de g y la cabeza referenciada por recorrido.
 * No desmarca ni comprueba que actual estuviera sin visitar: el wrapper y la
 * prueba de marcas de cada sucesor establecen ese contrato. Marca antes de
 * reservar el nodo de resultado, cuyo marcado es 0. Cada frame libera su lista
 * temporal de sucesores, no los nodos del grafo ni el resultado del caller.
 * Un fallo de reserva puede dejar marcas y resultado parciales. Recorrido NULL
 * retorna antes de marcar. Profundidad de recursion acotada por vertices alcanzables.
 */
void grafo_dfs_recursivo(Grafo g, int actual, ListaVertice *recorrido) {
    if (recorrido == NULL) {
        return;
    }

    g = grafo_marcar_vertice(g, actual);

    ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));
    if (tmp == NULL) return;

    tmp->dato = actual;
    tmp->marcado = 0;
    grafo_agregar_recorrido(recorrido, tmp);

    ListaVertice suces = grafo_sucesores(g, actual);
    while (suces) {
        if (!grafo_marcado_vertice(g, suces->dato)) {
            grafo_dfs_recursivo(g, suces->dato, recorrido);
        }
        ListaVertice temp = suces;
        suces = suces->sig;
        free(temp);
    }
}

/**
 * @brief Desmarca el grafo y recorre desde inicio en profundidad.
 * @param g Grafo cuyos nodos se marcan durante el recorrido.
 * @param inicio Identificador del vértice inicial.
 * @return Lista nueva de vértices visitados, o NULL si inicio no existe o no se reservan nodos.
 * @note Comprueba inicio antes de desmarcar: si falta, conserva las marcas previas.
 * Identificadores negativos, incluido -1, son datos validos. Con inicio valido,
 * desmarca todos los vertices y marca los alcanzables al entrar en recursion.
 * El resultado usa nodos nuevos con marcado=0; el caller libera cada nodo.
 * No libera vertices prestados del grafo ni modifica arcos. El orden depende
 * de la lista de arcos, no de ordenar identificadores. Una reserva fallida
 * puede dejar marcas y resultado parciales; NULL no identifica por si solo la causa.
 * El TAD real barre listas: cota O(V*(V+E)), frente al modelo ideal O(V+E).
 */
ListaVertice grafo_dfs(Grafo g, int inicio) {
    if (!grafo_existe_vertice(g, inicio)) {
        return NULL;
    }

    g = grafo_desmarcar(g);
    ListaVertice recorrido = NULL;
    grafo_dfs_recursivo(g, inicio, &recorrido);
    return recorrido;
}
//--------------------------------------------------
/**
 * @brief Consulta si algún arco tiene peso negativo.
 * @param g Grafo fuente.
 * @return 1 si existe un costo negativo; 0 en otro caso.
 */
static int grafo_tiene_peso_negativo(Grafo g) {
    ListaArco actual = g.a;
    while (actual != NULL) {
        if (actual->costo < 0) return 1;
        actual = actual->sig;
    }
    return 0;
}

/**
 * @brief Construye todos los sucesores o libera el parcial y reporta fallo.
 * @param g Grafo prestado; no se modifican nodos, arcos ni marcas.
 * @param x Vertice cuya lista de sucesores se consulta.
 * @param correcto Puntero prestado a un int valido del caller privado: 1 si
 * la lista esta completa (tambien vacia), 0 si una reserva falla.
 * @return Lista propia completa; NULL si vacia o fallo distinguido por correcto.
 * @note Helper privado exclusivo de Prim/Dijkstra. Conserva el orden de
 * grafo_sucesores; ante malloc fallido nunca entrega una lista parcial.
 */
static ListaVertice grafo_sucesores_atomicos(Grafo g, int x, int *correcto) {
    ListaArco k = g.a;
    ListaVertice ver = NULL, nuevo;
    *correcto = 1;
    while (k != NULL) {
        if (k->origen == x) {
            nuevo = (ListaVertice)malloc(sizeof(struct NodoV));
            if (nuevo == NULL) {
                while (ver != NULL) {
                    ListaVertice temp = ver;
                    ver = ver->sig;
                    free(temp);
                }
                *correcto = 0;
                return NULL;
            }
            nuevo->sig = ver;
            nuevo->dato = k->destino;
            nuevo->marcado = 0;
            ver = nuevo;
        }
        k = k->sig;
    }
    return ver;
}

/**
 * @brief Calcula un camino mínimo con pesos no negativos.
 * @param g Grafo dirigido ponderado.
 * @param inicio Vértice inicial.
 * @param llegada Vértice destino.
 * @return Lista nueva de arcos del camino; NULL si no hay arcos de resultado, hay pesos negativos, vértices inválidos o error de memoria.
 * @note NULL también representa el camino sin arcos de un vértice a sí mismo. El llamador libera el resultado.
 * @note INT_MAX es infinito: no se publica un camino con costo total mayor o igual a INT_MAX. Las sumas que excederían INT_MAX se descartan antes de sumar.
 * @note Los empates eligen el primer índice con distancia mínima en el orden de la lista de vértices; una distancia igual no reemplaza el predecesor.
 * @note Se rechaza cualquier peso negativo del grafo, incluso en componentes no alcanzables. No se modifican sus marcas.
 */
ListaArco grafo_dijkstra(Grafo g, int inicio, int llegada) {
    int n = grafo_orden(g);
    int *dist;
    int *prev;
    int *visitado;
    int *vertices;
    int i;
    int idx_inicio;
    int idx_llegada;
    ListaArco camino = NULL;
    if (grafo_tiene_peso_negativo(g)) {
        return NULL;
    }

    if (n <= 0) {
        return NULL;
    }

    dist = malloc(sizeof(int) * n);
    prev = malloc(sizeof(int) * n);
    visitado = calloc(n, sizeof(int));
    vertices = malloc(sizeof(int) * n);
    if (dist == NULL || prev == NULL || visitado == NULL || vertices == NULL) {
        free(dist);
        free(prev);
        free(visitado);
        free(vertices);
        return NULL;
    }
    if (!inicializarVectorVertices(g, vertices, n)) {
        free(dist);
        free(prev);
        free(visitado);
        free(vertices);
        return NULL;
    }

    for (i = 0; i < n; i++) {
        dist[i] = INT_MAX;
        prev[i] = -1;
    }

    idx_inicio = indiceVertice(vertices, n, inicio);
    idx_llegada = indiceVertice(vertices, n, llegada);
    if (idx_inicio == -1 || idx_llegada == -1) {
        free(dist);
        free(prev);
        free(visitado);
        free(vertices);
        return NULL;
    }

    dist[idx_inicio] = 0;

    for (i = 0; i < n; i++) {
        int j;
        int u = -1;
        int min = INT_MAX;
        ListaVertice suces;
        int suces_ok;

        for (j = 0; j < n; j++) {
            if (!visitado[j] && dist[j] < min) {
                min = dist[j];
                u = j;
            }
        }
        if (u == -1) break;
        visitado[u] = 1;

        suces = grafo_sucesores_atomicos(g, vertices[u], &suces_ok);
        if (!suces_ok) {
            free(dist);
            free(prev);
            free(visitado);
            free(vertices);
            return NULL;
        }
        while (suces != NULL) {
            int v = indiceVertice(vertices, n, suces->dato);
            if (v != -1 && !visitado[v]) {
                int costo = grafo_costo_arco(g, vertices[u], vertices[v]);
                if (costo >= 0 && dist[u] != INT_MAX && dist[u] <= INT_MAX - costo) {
                    int nueva_dist = dist[u] + costo;
                    if (nueva_dist < dist[v]) {
                        dist[v] = nueva_dist;
                        prev[v] = u;
                    }
                }
            }
            ListaVertice temp = suces;
            suces = suces->sig;
            free(temp);
        }
    }

    if (dist[idx_llegada] == INT_MAX) {
        free(dist);
        free(prev);
        free(visitado);
        free(vertices);
        return NULL;
    }

    {
        int destino = idx_llegada;
        while (prev[destino] != -1) {
            ListaArco nuevo = malloc(sizeof(struct NodoA));
            if (nuevo == NULL) {
                liberarListaArcos(camino);
                camino = NULL;
                break;
            }
            nuevo->origen = vertices[prev[destino]];
            nuevo->destino = vertices[destino];
            nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);
            nuevo->sig = camino;
            camino = nuevo;
            destino = prev[destino];
        }
    }

    free(dist);
    free(prev);
    free(visitado);
    free(vertices);
    return camino;
}
//-------------------------------------------------------------------------
/**
 * @brief Calcula un camino mínimo admitiendo pesos negativos.
 * @param g Grafo dirigido ponderado.
 * @param inicio Vértice inicial.
 * @param llegada Vértice destino.
 * @return Lista nueva de arcos del camino; NULL si no hay arcos de resultado, vértices inválidos, ciclo negativo alcanzable o error de memoria.
 * @note El llamador libera el resultado. La detección de ciclo negativo escribe una advertencia en stdout.
 * @note Las distancias internas son long long con alcanzabilidad separada: INT_MAX es un costo válido.
 * @note La suma se comprueba antes de ejecutarse. Una caminata inferior a (n-1)*INT_MIN demuestra un ciclo negativo y evita descenso ilimitado.
 * @note Un límite interno no representable produce diagnóstico explícito y NULL; no se descartan ni saturan candidatas.
 * @note Un inicio igual a llegada sin arcos de resultado también retorna NULL. Se validan ambos índices antes de relajar.
 */
ListaArco grafo_bellman_ford(Grafo g, int inicio, int llegada) {
    int n = grafo_orden(g);
    long long *dist;
    int *alcanzable;
    long long minimo_simple;
    int *prev;
    int *vertices;
    int i;
    int idx_inicio;
    int idx_llegada;
    ListaArco camino = NULL;

    if (n <= 0 || (size_t)n > (size_t)-1 / sizeof(long long) ||
        (n > 1 && (long long)INT_MIN < LLONG_MIN / (n - 1))) {
        return NULL;
    }

    minimo_simple = (long long)(n - 1) * INT_MIN;
    dist = malloc(sizeof(long long) * (size_t)n);
    alcanzable = calloc((size_t)n, sizeof(int));
    prev = malloc(sizeof(int) * n);
    vertices = malloc(sizeof(int) * n);
    if (dist == NULL || alcanzable == NULL || prev == NULL || vertices == NULL) {
        free(dist);
        free(alcanzable);
        free(prev);
        free(vertices);
        return NULL;
    }
    if (!inicializarVectorVertices(g, vertices, n)) {
        free(dist);
        free(alcanzable);
        free(prev);
        free(vertices);
        return NULL;
    }

    for (i = 0; i < n; i++) {
        dist[i] = 0;
        prev[i] = -1;
    }

    idx_inicio = indiceVertice(vertices, n, inicio);
    idx_llegada = indiceVertice(vertices, n, llegada);
    if (idx_inicio == -1 || idx_llegada == -1) {
        free(dist);
        free(alcanzable);
        free(prev);
        free(vertices);
        return NULL;
    }
    dist[idx_inicio] = 0;
    alcanzable[idx_inicio] = 1;

    for (i = 0; i < n - 1; i++) {
        ListaArco a = grafo_arcos(g);
        while (a != NULL) {
            int u = indiceVertice(vertices, n, a->origen);
            int v = indiceVertice(vertices, n, a->destino);
            if (u != -1 && v != -1 && alcanzable[u]) {
                long long cand;
                if ((a->costo > 0 && dist[u] > LLONG_MAX - a->costo) ||
                    (a->costo < 0 && dist[u] < LLONG_MIN - a->costo)) {
                    printf("Distancia fuera del rango interno.\n");
                    goto liberar_bellman;
                }
                cand = dist[u] + a->costo;
                /* Toda ruta simple tiene a lo sumo n-1 arcos. Una
                   caminata menor que este limite prueba un ciclo negativo. */
                if (cand < minimo_simple) {
                    printf("Se detecto un ciclo negativo.\n");
                    goto liberar_bellman;
                }
                if (!alcanzable[v] || cand < dist[v]) {
                    dist[v] = cand;
                    alcanzable[v] = 1;
                    prev[v] = u;
                } 
            }
            a = a->sig;
        }
    }

    {
        ListaArco a = grafo_arcos(g);
        while (a != NULL) {
            int u = indiceVertice(vertices, n, a->origen);
            int v = indiceVertice(vertices, n, a->destino);
            if (u != -1 && v != -1 && alcanzable[u]) {
                long long cand;
                if ((a->costo > 0 && dist[u] > LLONG_MAX - a->costo) ||
                    (a->costo < 0 && dist[u] < LLONG_MIN - a->costo)) {
                    printf("Distancia fuera del rango interno.\n");
                    goto liberar_bellman;
                }
                cand = dist[u] + a->costo;
                /* Toda ruta simple tiene a lo sumo n-1 arcos. Una
                   caminata menor que este limite prueba un ciclo negativo. */
                if (cand < minimo_simple) {
                    printf("Se detecto un ciclo negativo.\n");
                    goto liberar_bellman;
                }
                if (!alcanzable[v] || cand < dist[v]) {
                    printf("Se detecto un ciclo negativo.\n");
                    free(dist);
        free(alcanzable);
                    free(prev);
                    free(vertices);
                    return NULL;
                }
            }
            a = a->sig;
        }
    }

    if (!alcanzable[idx_llegada]) {
        free(dist);
        free(alcanzable);
        free(prev);
        free(vertices);
        return NULL;
    }

    {
        int destino = idx_llegada;
        while (prev[destino] != -1) {
            ListaArco nuevo = malloc(sizeof(struct NodoA));
            if (nuevo == NULL) {
                liberarListaArcos(camino);
                camino = NULL;
                break;
            }
            nuevo->origen = vertices[prev[destino]];
            nuevo->destino = vertices[destino];
            nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);
            nuevo->sig = camino;
            camino = nuevo;
            destino = prev[destino];
        }
    }

liberar_bellman:
    free(dist);
    free(alcanzable);
    free(prev);
    free(vertices);
    return camino;
}

//--------------------------------------------------------------

/**
 * @brief Construye el bosque con la selección de Prim sobre los arcos disponibles.
 * @param g Grafo; para la interpretación no dirigida se requieren arcos simétricos.
 * @param inicio Vértice desde el que comienza la selección.
 * @return Lista nueva de arcos seleccionados o NULL si el bosque no tiene arcos, inicio no existe o falla memoria.
 * @note Admite todos los costos int, incluidos INT_MIN e INT_MAX, con presencia de candidato separada.
 * @note Reinicia la selección en componentes desconectadas. El llamador libera el resultado.
 * @note Los empates de extracción conservan el primer índice mínimo de la lista de vértices y la mejora de padre es estricta.
 * @note El grafo y sus marcas se conservan. La API rechaza dirigidos, pero este C no tiene bandera de dirección ni comprueba simetría.
 */
ListaArco grafo_prim(Grafo g, int inicio) {
    int n = grafo_orden(g);
    int *costo;
    int *candidato;
    int *padre;
    int *visitado;
    int *vertices;
    int i;
    int idx_inicio;
    ListaArco arbol = NULL;

    if (n <= 0 || (size_t)n > (size_t)-1 / sizeof(int)) {
        return NULL;
    }

    costo = malloc(sizeof(int) * (size_t)n);
    candidato = calloc((size_t)n, sizeof(int));
    padre = malloc(sizeof(int) * n);
    visitado = calloc(n, sizeof(int));
    vertices = malloc(sizeof(int) * n);
    if (costo == NULL || candidato == NULL || padre == NULL || visitado == NULL || vertices == NULL) {
        free(costo);
        free(candidato);
        free(padre);
        free(visitado);
        free(vertices);
        return NULL;
    }
    if (!inicializarVectorVertices(g, vertices, n)) {
        free(costo);
        free(candidato);
        free(padre);
        free(visitado);
        free(vertices);
        return NULL;
    }

    for (i = 0; i < n; i++) {
        costo[i] = 0;
        padre[i] = -1;
    }

    idx_inicio = indiceVertice(vertices, n, inicio);
    if (idx_inicio == -1) {
        free(costo);
        free(candidato);
        free(padre);
        free(visitado);
        free(vertices);
        return NULL;
    }
    costo[idx_inicio] = 0;
    candidato[idx_inicio] = 1;

    for (i = 0; i < n; i++) {
        int j;
        int u = -1;
        int min = INT_MAX;
        ListaVertice suces;
        int suces_ok;

        for (j = 0; j < n; j++) {
            if (!visitado[j] && candidato[j] && (u == -1 || costo[j] < min)) {
                min = costo[j];
                u = j;
            }
        }
        if (u == -1) {
            for (j = 0; j < n; j++) if (!visitado[j]) { u = j; costo[u] = 0; break; }
            if (u == -1) break;
        }
        visitado[u] = 1;

        suces = grafo_sucesores_atomicos(g, vertices[u], &suces_ok);
        if (!suces_ok) {
            free(costo);
            free(candidato);
            free(padre);
            free(visitado);
            free(vertices);
            return NULL;
        }
        while (suces != NULL) {
            int v = indiceVertice(vertices, n, suces->dato);
            if (v != -1 && !visitado[v]) {
                int peso = grafo_costo_arco(g, vertices[u], vertices[v]);
                if (!candidato[v] || peso < costo[v]) {
                    costo[v] = peso;
                    candidato[v] = 1;
                    padre[v] = u;
                }
            }
            {
                ListaVertice temp = suces;
                suces = suces->sig;
                free(temp);
            }
        }
    }

    for (i = 0; i < n; i++) {
        if (padre[i] != -1) {
            ListaArco nuevo = malloc(sizeof(struct NodoA));
            if (nuevo == NULL) {
                liberarListaArcos(arbol);
                arbol = NULL;
                break;
            }
            nuevo->origen = vertices[padre[i]];
            nuevo->destino = vertices[i];
            nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);
            nuevo->sig = arbol;
            arbol = nuevo;
        }
    }

    free(costo);
    free(candidato);
    free(padre);
    free(visitado);
    free(vertices);
    return arbol;
}

//-------------------------------------------------------------------
/**
 * @brief Union-Find sobre indices 0..n-1, no sobre identificadores de vertices.
 * @note Con n positivo, padre dispone de n ints vivos y escribibles; cada
 * padre[i] pertenece a 0..n-1 y las cadenas terminan en una raiz padre[r]==r.
 * encontrar comprime caminos; unir modifica el arreglo. La estructura no
 * reserva ni libera por si sola: el caller administra el arreglo y sus aliases.
 */
typedef struct Conjunto {
    int *padre; /**< Arreglo propio o prestado de n indices padre; no punteros a nodos. */
    int n; /**< Número de elementos del arreglo padre. */
} Conjunto; /**< Alias del conjunto Union-Find. */
/**
 * @brief Busca la raíz de Union-Find y comprime el camino.
 * @param c Conjunto con arreglo padre válido y sin ciclos.
 * @param x Índice del elemento.
 * @return Índice de raíz o -1 ante puntero NULL o índice fuera de rango.
 */

int grafo_encontrar_conjunto(Conjunto *c, int x) {
    if (c == NULL || c->padre == NULL || x < 0 || x >= c->n) {
        return -1;
    }
    if (c->padre[x] != x)
        c->padre[x] = grafo_encontrar_conjunto(c, c->padre[x]);
    return c->padre[x];
}

/**
 * @brief Enlaza la raíz de y a la raíz de x si ambas son válidas.
 * @param c Conjunto Union-Find que se modifica.
 * @param x Índice del primer elemento.
 * @param y Índice del segundo elemento.
 */
void grafo_unir_conjuntos(Conjunto *c, int x, int y) {
    int rx = grafo_encontrar_conjunto(c, x);
    int ry = grafo_encontrar_conjunto(c, y);
    if (rx != -1 && ry != -1 && rx != ry) c->padre[ry] = rx;
}

/**
 * @brief Selecciona arcos por costo evitando ciclos mediante Union-Find.
 * @param g Grafo cuyos arcos se consideran como conexiones para la selección.
 * @return Lista nueva del bosque seleccionado; NULL si no hay arcos de resultado o falla memoria.
 * @note El llamador libera los nodos del resultado; no se modifica la lista de arcos del grafo.
 * @note Admite costos negativos y extremos int; ordena punteros a arcos por burbuja estable, no por O(E log E).
 * @note Arcos simétricos se consideran por separado; Union-Find descarta el segundo sentido y los bucles.
 * @note En empates conserva el orden de la lista de arcos; ante desconexión devuelve un bosque. No modifica marcas.
 * @note El C no tiene bandera dirigida: considera arcos como conexiones; la API rechaza grafos dirigidos.
 */
ListaArco grafo_kruskal(Grafo g) {
    int n = grafo_orden(g);
    int m = grafo_tamano(g);
    Conjunto conjuntos;
    int *vertices;
    ListaArco *aristas;
    ListaArco a;
    int i;
    ListaArco mst = NULL;

    if (n <= 0 || m <= 0) {
        return NULL;
    }

    conjuntos.padre = malloc(n * sizeof(int));
    conjuntos.n = n;
    vertices = malloc(sizeof(int) * n);
    aristas = malloc(sizeof(ListaArco) * m);
    if (conjuntos.padre == NULL || vertices == NULL || aristas == NULL) {
        free(conjuntos.padre);
        free(vertices);
        free(aristas);
        return NULL;
    }

    if (!inicializarVectorVertices(g, vertices, n)) {
        free(conjuntos.padre);
        free(vertices);
        free(aristas);
        return NULL;
    }
    for (i = 0; i < n; i++) conjuntos.padre[i] = i;

    i = 0;
    a = grafo_arcos(g);
    while (a != NULL && i < m) {
        aristas[i++] = a;
        a = a->sig;
    }

    for (int x = 0; x < i - 1; x++) {
        for (int y = 0; y < i - x - 1; y++) {
            if (aristas[y]->costo > aristas[y+1]->costo) {
                ListaArco tmp = aristas[y];
                aristas[y] = aristas[y+1];
                aristas[y+1] = tmp;
            }
        }
    }

    for (int j = 0; j < i; j++) {
        int u = indiceVertice(vertices, n, aristas[j]->origen);
        int v = indiceVertice(vertices, n, aristas[j]->destino);
        if (u != -1 && v != -1 && grafo_encontrar_conjunto(&conjuntos, u) != grafo_encontrar_conjunto(&conjuntos, v)) {
            grafo_unir_conjuntos(&conjuntos, u, v);
            ListaArco nuevo = malloc(sizeof(struct NodoA));
            if (nuevo == NULL) {
                liberarListaArcos(mst);
                mst = NULL;
                break;
            }
            nuevo->origen = aristas[j]->origen;
            nuevo->destino = aristas[j]->destino;
            nuevo->costo = aristas[j]->costo;
            nuevo->sig = mst;
            mst = nuevo;
        }
    }

    free(aristas);
    free(conjuntos.padre);
    free(vertices);
    return mst;
}


