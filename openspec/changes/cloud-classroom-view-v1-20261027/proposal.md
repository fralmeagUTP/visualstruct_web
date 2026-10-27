# Vista de clase transversal v1
## Por qué
El usuario observó ABB9 con árbol de unos150px, memoria ocupando más que la
visualización y nodos miniatura. La solución v0 estabiliza el viewport pero el
reparto fijo y SVGforzado a100% reducen legibilidad en contenido mayor.
## Qué
Dar prioridad a estructura grande a la izquierda y código estable a la derecha;
memoria opcional cerrada inicialmente, controles compactos y zoom/pan explícitos
persistentes sin autoencoger al avanzar. Resultados con consola/main/TAD claramente
separados, ampliar/copiar sin recarga y sin alterar texto C ni stdout.
