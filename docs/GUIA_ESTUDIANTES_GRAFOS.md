# VisualStruct: grafos y lectura de resultados

Guía de aula · actualización del 11 de noviembre de 2026

Esta guía acompaña la revisión de VisualStruct con firmas mínimas del TAD grafo, capacidad visual de 30 vértices y resultados completos. Debe usarse con el código C y el encabezado de esa misma revisión. La fecha del documento no certifica por sí sola que una instalación web ya esté actualizada.

## 1. Qué aprenderás

- Construir un grafo con llamadas C que reciben únicamente los datos de la operación.
- Distinguir un recorrido, un camino mínimo y un árbol de expansión mínima.
- Leer el resultado sin confundirlo con la salida de `printf` o los diagnósticos del visualizador.
- Liberar correctamente las listas que produce cada consulta.

## 2. Las funciones que usarás

No debes declarar ni pasar `GrafoEstado` para utilizar la interfaz pública. El visualizador sigue comprobando errores internamente. Esto no elimina las condiciones que debe cumplir un algoritmo.

| Operación | Llamada | Resultado |
| --- | --- | --- |
| Crear | `grafo_crear()` | Grafo vacío |
| Insertar vértice | `grafo_insertar_vertice(g, dato)` | Grafo actualizado |
| Insertar arco | `grafo_insertar_arco(g, origen, destino, peso)` | Grafo actualizado |
| Sucesores | `grafo_sucesores(g, vertice)` | Lista de vértices propia |
| Predecesores | `grafo_predecesores(g, vertice)` | Lista de vértices propia |
| BFS | `grafo_bfs(g, inicio)` | Lista del recorrido |
| DFS | `grafo_dfs(g, inicio)` | Lista del recorrido |
| Dijkstra | `grafo_dijkstra(g, inicio, llegada)` | Lista de arcos del camino |
| Bellman-Ford | `grafo_bellman_ford(g, inicio, llegada)` | Lista de arcos del camino |
| Prim | `grafo_prim(g, inicio)` | Lista de arcos del árbol |
| Kruskal | `grafo_kruskal(g)` | Lista de arcos del árbol |

El encabezado [tad_grafo.h](tads_C/tad_grafo.h) contiene todas las declaraciones. Los identificadores y pesos usados aquí son enteros. En las inserciones, asigna siempre el resultado:

```c
Grafo g = grafo_crear();
g = grafo_insertar_vertice(g, 1);
g = grafo_insertar_vertice(g, 2);
g = grafo_insertar_arco(g, 1, 2, 4);
```

Crea los vértices antes de insertar sus arcos. El TAD C representa cada arco con dirección: `1→2` no implica `2→1`. Para un grafo no dirigido en C, agrega ambos sentidos con el mismo peso. La opción no dirigida del visualizador se encarga de esas dos llamadas.

**Migrar ejercicios anteriores:** retira el argumento `&estado` de las diez funciones simplificadas y las instrucciones que crean o imprimen ese estado. No combines un `main.c` antiguo con el encabezado nuevo. Otras funciones conservan parámetros útiles para su resultado: por ejemplo, `grafo_costo_arco(g, origen, destino, &costo)` entrega el costo consultado y retorna si lo encontró; `&costo` no es un diagnóstico.

## 3. Práctica guiada: tres vértices

Construye un grafo no dirigido:

- Vértices: 1, 2 y 3.
- Aristas: 1–2 con peso 4; 2–3 con peso 2; 1–3 con peso 9.

Antes de ejecutar, responde: ¿es mejor ir directamente de 1 a 3 o pasar por 2?

### Recorridos

Ejecuta BFS desde 1 y después DFS desde 1. BFS visita por niveles; DFS profundiza antes de retroceder. **No optimizan la suma de pesos.** El orden entre vecinos depende de cómo se almacenan y recorren; no hay que imponer un orden numérico que el algoritmo no promete. En el ejemplo C adjunto ambos recorridos son `1, 2, 3`.

### Caminos mínimos

Ejecuta Dijkstra entre 1 y 3: el camino esperado es `1→2→3`, con costo `4+2=6`, menor que 9. Bellman-Ford produce el mismo costo en este ejemplo.

- Dijkstra exige pesos no negativos; esta implementación rechaza pesos negativos incluso en otra parte del grafo.
- Bellman-Ford permite pesos negativos, pero detecta ciclos negativos alcanzables desde el inicio.
- Un destino no alcanzable no tiene camino. Un camino de un vértice a sí mismo puede ser válido y tener cero arcos.

### Árbol de expansión mínima

Ejecuta Prim desde 1 y Kruskal. El árbol utiliza las conexiones 1–2 y 2–3 y tiene peso total 6. En esta revisión, **los arcos del árbol aparecen amarillos y los demás azules**, con una leyenda.

El árbol conecta todos los vértices con costo total mínimo; no es necesariamente un camino entre dos vértices. Prim y Kruskal pueden elegir árboles distintos cuando hay empates. Requieren conexiones simétricas y conectividad para este contrato: no presentan un bosque desconectado como árbol completo exitoso. En C, una arista del resultado puede aparecer en cualquiera de sus dos orientaciones; en el ejemplo, Kruskal devuelve `2→1` y `3→2`, equivalentes a 1–2 y 2–3.

## 4. Ejemplo completo que puedes compilar

El archivo [grafos_aula.c](examples/grafos_aula.c) incluye creación, inserciones, listas prestadas, sucesores, predecesores, BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal y liberación de memoria. Usa exactamente los tres vértices de la práctica.

Desde la raíz del repositorio, con GCC disponible:

```sh
gcc -std=c17 -Wall -Wextra -Werror -pedantic -I docs/tads_C docs/examples/grafos_aula.c docs/tads_C/tad_grafo.c -o grafos_aula
```

Ejecuta `./grafos_aula` en Linux/macOS o `./grafos_aula.exe` en PowerShell si GCC generó ese archivo. Si copias los archivos a otra carpeta, conserva juntos el encabezado, la implementación y tu programa, o ajusta la ruta `-I`.

Salida verificada:

```text
Vertices del grafo: 3 2 1
Sucesores de 1: 2 3
Predecesores de 1: 2 3
BFS desde 1: 1 2 3
DFS desde 1: 1 2 3
Dijkstra 1 a 3: 1->2(4) 2->3(2); peso total = 6
Bellman-Ford 1 a 3: 1->2(4) 2->3(2); peso total = 6
Prim: 1->2(4) 2->3(2); peso total = 6
Kruskal: 2->1(4) 3->2(2); peso total = 6
```

Las comprobaciones `assert` del ejemplo verifican datos conocidos de esta práctica; no sustituyen un tratamiento general de errores o falta de memoria.

## 5. Quién libera cada lista

| Origen de la lista | Propiedad | Qué hacer |
| --- | --- | --- |
| `grafo_vertices(g)` y `grafo_arcos(g)` | Prestada: pertenece al grafo | Leerla sin liberar ni modificar sus nodos por separado. No conservarla después de borrar sus nodos o destruir el grafo. |
| Sucesores, predecesores, BFS y DFS | Propia del resultado | Llamar a `grafo_liberar_vertices(&lista)` al terminar. |
| Dijkstra, Bellman-Ford, Prim y Kruskal | Propia del resultado | Llamar a `grafo_liberar_arcos(&lista)` al terminar. |
| Grafo completo | Del programa | Llamar a `grafo_destruir(&g)` al terminar todas las operaciones. |

No interpretes `NULL` automáticamente como «error»: puede ser un resultado válido sin elementos o una operación sin resultado. Consulta el diagnóstico que muestra VisualStruct y las condiciones del ejercicio. La interfaz C mínima no ofrece un parámetro público con el detalle del error.

## 6. Cómo leer el área de resultados

Primero mira el resultado del algoritmo: recorrido, camino, árbol o respuesta de la operación. Las salidas se ajustan al ancho disponible y crecen en altura para evitar el pequeño scroll interno que tapaba líneas.

- En grafos, recorridos de árboles y salidas secuenciales, los resultados están integrados en la tarjeta de visualización, fuera del viewport desplazable del dibujo.
- En hash y ordenamiento se conserva su sección de resultados/consola, con texto ajustado y sin scroll propio pequeño. No se cambia el orden de las pestañas para mover artificialmente el contenido.
- El dibujo puede mantener zoom y desplazamiento cuando no cabe. El editor C también conserva desplazamiento para leer código. Esto es distinto del resultado recortado.
- La **consola C** muestra lo que imprimió el programa. Una consola vacía no implica necesariamente que la operación haya fallado.
- Los **diagnósticos** explican condiciones de ejecución del visualizador. No debes añadir un argumento a la llamada C para obtenerlos en la aplicación.
- En modo práctica, predice primero y revela la decisión con los controles correspondientes: el cambio de presentación no debe anticiparte las respuestas.

### Retorno del TAD y función auxiliar

Si consultas `grafo_vertices(g)`, el TAD devuelve una referencia a su lista. Después el programa puede llamar a una función auxiliar `void` que la imprime. Que esa función auxiliar no devuelva valor **no significa que la lista se haya perdido**. Distingue el retorno recibido del TAD del último retorno auxiliar al revisar la traza; una impresión no reemplaza el contenido del grafo. Avanza y retrocede para localizar el instante de recepción de cada resultado, sin atribuir a un paso información que todavía no existe.

## 7. Trabajar con hasta 30 vértices

El límite de esta revisión del visualizador es **30 vértices**. La inserción del vértice 31 se rechaza sin borrar los existentes. El TAD C usa memoria dinámica: este tope corresponde a la experiencia educativa de la aplicación, no al lenguaje C.

Empieza con 3 a 6 vértices para estudiar el código. Después prueba 20 o 30. Un grafo denso tiene muchas conexiones cruzadas y puede ser difícil de leer, aunque conserve todos los datos. Usa zoom y ejemplos menos densos cuando la pregunta sea comprender un algoritmo.

El número de vértices y el tamaño de la traza son límites distintos. El modo paso a paso conserva un presupuesto de **4.000 eventos**: si una operación lo supera, no se prepara una traza recortada. Reduce el caso o utiliza el modo normal para consultar el resultado cuando la operación sea válida. No esperes una animación completa de cualquier grafo denso solo porque admite 30 vértices.

## 8. Retos para comprobar lo aprendido

1. Cambia el peso de 1–3 a 5 en ambos sentidos. Predice qué camino elegirán Dijkstra y Bellman-Ford antes de ejecutar.
2. Quita las dos aristas incidentes al vértice 3. Explica por qué no existe un árbol de expansión que conecte los tres vértices.
3. Construye una cadena de 10 vértices y ejecútala en modo normal y paso a paso. Distingue resultado final y traza.
4. Modifica el ejemplo C para ejecutar BFS desde 2. Libera su resultado y comprueba que el grafo conserva sus vértices.
5. Descarga el `main.c` de tu práctica y comprueba que las llamadas públicas no necesitan `GrafoEstado`.

Consulta también el [manual general](USER_GUIDE.md) y la [referencia de la API pública](graph_public_api.md).
