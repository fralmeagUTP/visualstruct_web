/* Test-only observer contract; never part of the downloadable public API. */
#ifndef GRAPH_PRIVATE_DIAGNOSTIC_QA_H
#define GRAPH_PRIVATE_DIAGNOSTIC_QA_H
extern int qa_status;
enum { GRAFO_OK, GRAFO_MEMORIA, GRAFO_NO_EXISTE,
       GRAFO_PESO_NEGATIVO, GRAFO_CICLO_NEGATIVO,
       GRAFO_DESCONECTADO, GRAFO_ARGUMENTO, GRAFO_RANGO };
#endif
