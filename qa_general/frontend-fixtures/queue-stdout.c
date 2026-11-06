#include "tad_cola.h"
int main(void) { struct Cola q={0}; cola_encolar(&q,7); cola_encolar(&q,3); cola_encolar(&q,7); cola_mostrar(q); cola_vaciar(&q); return 0; }
