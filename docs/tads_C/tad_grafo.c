//---------------------------------------------------------------------------
/**
 * @file TADGrafo.h
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
    int dato;                     
    struct NodoV* sig;           
    int marcado;                 
} *ListaVertice;

//----------------------------------------------------------------------------
/**
 * @brief Nodo de arco en el grafo.
 */
typedef struct NodoA {
    int origen;                  
    int destino;                 
    int costo;                   
    struct NodoA* sig;           
} *ListaArco;

//----------------------------------------------------------------------------
/**
 * @brief Estructura principal del grafo.
 */
typedef struct nodoGrafo {
    ListaVertice v;              
    ListaArco a;                 
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
 * @brief Inserta un vértice en el grafo
 * @param g Grafo en el cual se insertará el vértice
 * @param x Vértice a insertar
 * @return Grafo con el nuevo vértice
*/
Grafo grafo_insertar_vertice(Grafo g, int x) {
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
 * @brief Inserta un arco en el grafo
 * @param g Grafo en el cual se insertará el arco
 * @param x Vértice origen
 * @param y Vértice destino
 * @param z Costo del arco
 * @return Grafo con el nuevo arco
 */
Grafo grafo_insertar_arco(Grafo g, int x, int y, int z) {
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
 * @brief Devuelve la lista de vértices del grafo
 * @param g Grafo del cual se devolverá la lista de vértices
 * @return ListaVertice - La lista de vértices del grafo
 */         
ListaVertice grafo_vertices (Grafo g)
 {
     return g.v;
 }


//---------------------------------------------------------------
/**
 * @brief Devuelve la lista de arcos del grafo
 * @param g Grafo del cual se devolverá la lista de arcos
 * @return ListaArco - La lista de arcos del grafo
*/         
ListaArco grafo_arcos (Grafo g)
 {
     return g.a;
 }


//------------------------------------------------------------------
/**
 * @brief Cambia la lista de vértices del grafo
 * @param g Grafo del cual se cambiará la lista de vértices
 * @param k Nueva lista de vértices
 * @return Grafo con la nueva lista de vértices
*/
Grafo grafo_cambiar_vertices (Grafo g, ListaVertice k)
{
   g.v = k;
   return g;
}


//----------------------------------------------------------------------
/**
 * @brief Cambia la lista de arcos del grafo
 * @param g Grafo del cual se cambiará la lista de arcos
 * @param k Nueva lista de arcos
 * @return Grafo con la nueva lista de arcos
*/
Grafo grafo_cambiar_arcos (Grafo g, ListaArco k)
{
   g.a = k;
   return g;
}


//--------------------------------------------------------------------------------
/**
 * @brief Verifica si el grafo es vacio
 * @param g Grafo del cual se verificará si es vacio
 * @return int - 1 si el grafo es vacio, 0 en caso contrario
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
 * @brief Elimina un vértice del grafo
 * @param g Grafo del cual se eliminará el vértice
 * @param x Vértice a eliminar
 * @return Grafo con el vértice eliminado
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
 * @brief Elimina un arco del grafo
 * @param g Grafo del cual se eliminará el arco
 * @param x Vértice origen
 * @param y Vértice destino
 * @return Grafo con el arco eliminado
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
 * @return int - El costo del arco
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
 * @brief Retorna el número de vértices asociados al grafo
 * @param g Grafo del cual se retornará el número de vértices
 * @return int - El número de vértices asociados al grafo
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
 * @brief Retorna el número de arcos asociados al grafo
 * @param g Grafo del cual se retornará el número de arcos
 * @return int - El número de arcos asociados al grafo
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
 * @brief Retorna el grado del vértice x del grafo
 * @param g Grafo del cual se retornará el grado del vértice
 * @param x Vértice
 * @return int - El grado del vértice
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
 * @brief Desmarca un vértice de grafo
 * @param g Grafo del cual se desmarcará el vértice
 * @param x Vértice
 * @return Grafo con el vértice desmarcado  
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
 * @brief Desmarca todos los vértices del grafo
 * @param g Grafo del cual se desmarcarán todos los vértices
 * @return Grafo con los vértices desmarcados
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
 * @brief Marca un vértice del grafo
 * @param g Grafo del cual se marcará el vértice
 * @param x Vértice a marcar
 * @return Grafo con el vértice marcado
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
 * @brief Verifica si un vértice está marcado
 * @param g Grafo del cual se verificará el vértice
 * @param x Vértice a verificar
 * @return 1 si el vértice está marcado, 0 en caso contrario
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

static void liberarListaArcos(ListaArco lista) {
    while (lista != NULL) {
        ListaArco tmp = lista;
        lista = lista->sig;
        free(tmp);
    }
}

static int indiceVertice(const int *vertices, int n, int valor) {
    int i;
    for (i = 0; i < n; i++) {
        if (vertices[i] == valor) {
            return i;
        }
    }
    return -1;
}

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
 * @brief Retorna una lista con los grafo_sucesores de un vértice
 * @param g Grafo del cual se retornará la lista de grafo_sucesores
 * @param x Vértice
 * @return ListaVertice - Una lista con los grafo_sucesores de un vértice
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
 * @brief Retorna una lista con los grafo_predecesores de un vértice
 * @param g Grafo del cual se retornará la lista de grafo_predecesores
 * @param x Vértice
 * @return ListaVertice - Una lista con los grafo_predecesores de un vértice
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
 * @brief Implementa el algoritmo de recorrido en amplitud (grafo_bfs).
 * @param g Grafo sobre el cual se realizará el recorrido.
 * @param inicio Vértice inicial para el recorrido.
 * @return Lista enlazada de vértices en orden de recorrido grafo_bfs.
 */
ListaVertice grafo_bfs(Grafo g, int inicio) {
    g = grafo_desmarcar(g);
    struct Cola cola = {NULL, NULL};
    ListaVertice recorrido = NULL;

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
        if (actual == -1) {
            break;
        }

        // Agregar al recorrido
        ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));
        if (tmp == NULL) continue;

        tmp->dato = actual;
        tmp->marcado = 0;
        tmp->sig = recorrido;
        recorrido = tmp;

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
void grafo_dfs_recursivo(Grafo g, int actual, ListaVertice *recorrido) {
    if (recorrido == NULL) {
        return;
    }

    g = grafo_marcar_vertice(g, actual);

    ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));
    if (tmp == NULL) return;

    tmp->dato = actual;
    tmp->marcado = 0;
    tmp->sig = *recorrido;
    *recorrido = tmp;

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

        for (j = 0; j < n; j++) {
            if (!visitado[j] && dist[j] < min) {
                min = dist[j];
                u = j;
            }
        }
        if (u == -1) {
            break;
        }
        visitado[u] = 1;

        suces = grafo_sucesores(g, vertices[u]);
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
ListaArco grafo_bellman_ford(Grafo g, int inicio, int llegada) {
    int n = grafo_orden(g);
    int *dist;
    int *prev;
    int *vertices;
    int i;
    int idx_inicio;
    int idx_llegada;
    ListaArco camino = NULL;

    if (n <= 0) {
        return NULL;
    }

    dist = malloc(sizeof(int) * n);
    prev = malloc(sizeof(int) * n);
    vertices = malloc(sizeof(int) * n);
    if (dist == NULL || prev == NULL || vertices == NULL) {
        free(dist);
        free(prev);
        free(vertices);
        return NULL;
    }
    if (!inicializarVectorVertices(g, vertices, n)) {
        free(dist);
        free(prev);
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
        free(vertices);
        return NULL;
    }
    dist[idx_inicio] = 0;

    for (i = 0; i < n - 1; i++) {
        ListaArco a = grafo_arcos(g);
        while (a != NULL) {
            int u = indiceVertice(vertices, n, a->origen);
            int v = indiceVertice(vertices, n, a->destino);
            if (u != -1 && v != -1 && dist[u] != INT_MAX) {
                long long cand = (long long)dist[u] + (long long)a->costo;
                if (cand >= INT_MIN && cand <= INT_MAX && (int)cand < dist[v]) {
                    dist[v] = (int)cand;
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
            if (u != -1 && v != -1 && dist[u] != INT_MAX) {
                long long cand = (long long)dist[u] + (long long)a->costo;
                if (cand >= INT_MIN && cand <= INT_MAX && (int)cand < dist[v]) {
                    printf("Se detecto un ciclo negativo.\n");
                    free(dist);
                    free(prev);
                    free(vertices);
                    return NULL;
                }
            }
            a = a->sig;
        }
    }

    if (dist[idx_llegada] == INT_MAX) {
        free(dist);
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

    free(dist);
    free(prev);
    free(vertices);
    return camino;
}

//--------------------------------------------------------------

ListaArco grafo_prim(Grafo g, int inicio) {
    int n = grafo_orden(g);
    int *costo;
    int *padre;
    int *visitado;
    int *vertices;
    int i;
    int idx_inicio;
    ListaArco arbol = NULL;

    if (n <= 0) {
        return NULL;
    }

    costo = malloc(sizeof(int) * n);
    padre = malloc(sizeof(int) * n);
    visitado = calloc(n, sizeof(int));
    vertices = malloc(sizeof(int) * n);
    if (costo == NULL || padre == NULL || visitado == NULL || vertices == NULL) {
        free(costo);
        free(padre);
        free(visitado);
        free(vertices);
        return NULL;
    }
    if (!inicializarVectorVertices(g, vertices, n)) {
        free(costo);
        free(padre);
        free(visitado);
        free(vertices);
        return NULL;
    }

    for (i = 0; i < n; i++) {
        costo[i] = INT_MAX;
        padre[i] = -1;
    }

    idx_inicio = indiceVertice(vertices, n, inicio);
    if (idx_inicio == -1) {
        free(costo);
        free(padre);
        free(visitado);
        free(vertices);
        return NULL;
    }
    costo[idx_inicio] = 0;

    for (i = 0; i < n; i++) {
        int j;
        int u = -1;
        int min = INT_MAX;
        ListaVertice suces;

        for (j = 0; j < n; j++) {
            if (!visitado[j] && costo[j] < min) {
                min = costo[j];
                u = j;
            }
        }
        if (u == -1) {
            break;
        }
        visitado[u] = 1;

        suces = grafo_sucesores(g, vertices[u]);
        while (suces != NULL) {
            int v = indiceVertice(vertices, n, suces->dato);
            if (v != -1 && !visitado[v]) {
                int peso = grafo_costo_arco(g, vertices[u], vertices[v]);
                if (peso >= 0 && peso < costo[v]) {
                    costo[v] = peso;
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
    free(padre);
    free(visitado);
    free(vertices);
    return arbol;
}

//-------------------------------------------------------------------
typedef struct Conjunto {
    int *padre;
    int n;
} Conjunto;

int grafo_encontrar_conjunto(Conjunto *c, int x) {
    if (c == NULL || c->padre == NULL || x < 0 || x >= c->n) {
        return -1;
    }
    if (c->padre[x] != x)
        c->padre[x] = grafo_encontrar_conjunto(c, c->padre[x]);
    return c->padre[x];
}

void grafo_unir_conjuntos(Conjunto *c, int x, int y) {
    int rx = grafo_encontrar_conjunto(c, x);
    int ry = grafo_encontrar_conjunto(c, y);
    if (rx != -1 && ry != -1 && rx != ry) c->padre[ry] = rx;
}

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


